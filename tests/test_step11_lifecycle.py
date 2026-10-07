from __future__ import annotations

import json
from pathlib import Path

import pytest

from full_album_maker.editor_commands import SetPlaylistEntries
from full_album_maker.editor_controller import EditorController
from full_album_maker.editor_models import MediaAsset, ProjectDocument, SongInstance, TIMEBASE
from full_album_maker.integration_lifecycle_step11 import (
    DebouncedAutosaveCoordinator,
    IntegrationRecoveryStore,
    RecoveryEnvelope,
    RecoverySessionLease,
    recovery_path_for_session,
    extract_project_document_from_saved_json,
    request_from_document,
    verify_persisted_document,
)
from full_album_maker.project_repository import save_project_document
import full_album_maker.integration_feature_step11 as integration_feature
from full_album_maker.integration_core_step11 import project_token
from full_album_maker.project_persistence import ProjectPersistence


def _document(tmp_path: Path) -> ProjectDocument:
    doc = ProjectDocument.new_empty("Lifecycle")
    for index in range(2):
        path = tmp_path / f"song-{index}.mp3"
        path.write_bytes(b"audio")
        asset = MediaAsset(
            kind="audio",
            locator=str(path),
            original_name=path.name,
            source_duration_tick=20 * TIMEBASE,
        )
        doc.media.append(asset)
        doc.playlist.entries.append(
            SongInstance(asset_id=asset.asset_id, display_title=f"Song {index}", source_out_tick=20 * TIMEBASE)
        )
    doc.validate()
    return doc


def _next_revision(doc: ProjectDocument) -> ProjectDocument:
    controller = EditorController(doc)
    controller.dispatch(SetPlaylistEntries(list(reversed(doc.playlist.entries))))
    return controller.snapshot()


def test_autosave_requests_coalesce_to_last_committed_revision(tmp_path: Path) -> None:
    doc = _document(tmp_path)
    coordinator = DebouncedAutosaveCoordinator()
    first = coordinator.request(doc, project_path=str(tmp_path / "project.json"))
    second_doc = _next_revision(doc)
    second = coordinator.request(second_doc, project_path=str(tmp_path / "project.json"))
    pending = coordinator.take_pending()
    assert pending is not None
    assert pending.generation == second.generation
    assert pending.revision == second_doc.revision
    assert pending.signature == second.signature
    assert pending.signature != first.signature
    assert coordinator.take_pending() is None


def test_stale_autosave_completion_cannot_claim_newer_revision_saved(tmp_path: Path) -> None:
    doc = _document(tmp_path)
    coordinator = DebouncedAutosaveCoordinator()
    older = coordinator.request(doc)
    newer_doc = _next_revision(doc)
    newer = coordinator.request(newer_doc)
    coordinator.complete(older, success=True)
    assert coordinator.status.last_success_generation == 0
    assert coordinator.status.pending is True
    coordinator.complete(newer, success=True)
    assert coordinator.status.last_success_generation == newer.generation
    assert coordinator.status.last_success_revision == newer.revision
    assert coordinator.status.pending is False


def test_failed_latest_autosave_records_error_without_marking_success(tmp_path: Path) -> None:
    coordinator = DebouncedAutosaveCoordinator()
    request = coordinator.request(_document(tmp_path))
    coordinator.complete(request, success=False, error="disk penuh")
    assert coordinator.status.pending is True
    assert coordinator.status.last_success_generation == 0
    assert coordinator.status.last_error == "disk penuh"


def test_recovery_store_roundtrip_is_atomic_domain_snapshot(tmp_path: Path) -> None:
    doc = _next_revision(_document(tmp_path))
    request = request_from_document(doc, project_path=str(tmp_path / "canonical.json"), generation=4)
    store = IntegrationRecoveryStore(tmp_path / "recovery.json")
    envelope = store.write(request)
    discovered = store.discover()
    assert discovered is not None
    assert discovered.project_token == envelope.project_token
    assert discovered.revision == doc.revision
    assert discovered.document().content_signature() == doc.content_signature()
    raw = json.loads((tmp_path / "recovery.json").read_text(encoding="utf-8"))
    assert raw["format"] == "full-album-maker-step11-recovery"
    assert raw["document"]["format"] == "full-album-maker-project"
    assert raw["source_project_path"].endswith("canonical.json")


def test_corrupt_or_tampered_recovery_fails_closed(tmp_path: Path) -> None:
    path = tmp_path / "recovery.json"
    path.write_text("{broken", encoding="utf-8")
    store = IntegrationRecoveryStore(path)
    assert store.discover() is None

    doc = _document(tmp_path)
    envelope = RecoveryEnvelope(
        project_token="p",
        revision=doc.revision,
        signature="0" * 64,
        source_project_path="",
        saved_at_utc="2026-01-01T00:00:00+00:00",
        document_payload=doc.to_dict(),
    )
    path.write_text(json.dumps(envelope.to_dict()), encoding="utf-8")
    assert store.discover() is None
    with pytest.raises(ValueError, match="Signature"):
        store.load_strict()


def test_native_project_save_verifies_normalized_authoritative_state(tmp_path: Path) -> None:
    doc = _next_revision(_document(tmp_path))
    path = tmp_path / "native.json"
    save_project_document(str(path), doc)
    restored = extract_project_document_from_saved_json(path)
    assert restored.content_signature() == doc.content_signature()
    assert verify_persisted_document(path, doc) is True


def test_legacy_envelope_verification_uses_embedded_project_document(tmp_path: Path) -> None:
    doc = _next_revision(_document(tmp_path))
    path = tmp_path / "legacy.json"
    path.write_text(
        json.dumps({"legacy": True, "album_document_v2": doc.to_dict()}),
        encoding="utf-8",
    )
    restored = extract_project_document_from_saved_json(path)
    assert restored.project_id == doc.project_id
    assert verify_persisted_document(path, doc) is True

    changed = _next_revision(doc)
    assert verify_persisted_document(path, changed) is False



def test_live_sessions_keep_independent_recovery_files(tmp_path: Path) -> None:
    root = tmp_path / "recovery"
    first = RecoverySessionLease(root)
    second = RecoverySessionLease(root)
    first.start()
    second.start()
    try:
        canonical_path = tmp_path / "project.json"
        base = _document(tmp_path)
        token = project_token(base, str(canonical_path))

        first_doc = _next_revision(base)
        second_doc = first_doc.clone()
        second_doc.revision += 1
        second_doc.album_title = "second-session"
        second_doc.validate()

        first_path = recovery_path_for_session(root, token, first.session_id)
        second_path = recovery_path_for_session(root, token, second.session_id)
        store_first = IntegrationRecoveryStore(first_path)
        store_second = IntegrationRecoveryStore(second_path)

        store_first.write(
            request_from_document(
                first_doc,
                project_path=str(canonical_path),
                owner_session_id=first.session_id,
            )
        )
        store_second.write(
            request_from_document(
                second_doc,
                project_path=str(canonical_path),
                owner_session_id=second.session_id,
            )
        )

        assert first_path != second_path
        assert first_path.is_file() and second_path.is_file()
        assert store_first.load_strict().owner_session_id == first.session_id
        assert store_second.load_strict().owner_session_id == second.session_id
        assert first.session_alive(second.session_id) is True
        assert second.session_alive(first.session_id) is True
    finally:
        first.close()
        second.close()


def test_live_instance_recovery_is_not_offered_or_deleted(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(integration_feature, "data_dir", lambda: tmp_path)
    monkeypatch.setenv("FAM_STEP11_NO_RECOVERY_PROMPT", "1")
    root = tmp_path / "recovery" / "step11"

    owner = RecoverySessionLease(root)
    observer = RecoverySessionLease(root)
    owner.start()
    observer.start()
    try:
        canonical_path = tmp_path / "canonical.json"
        canonical = _document(tmp_path)
        canonical.revision = 5
        canonical.validate()
        token = project_token(canonical, str(canonical_path))

        newer = canonical.clone()
        newer.revision = 6
        newer.album_title = "live-owner-unsaved"
        newer.validate()
        recovery_path = recovery_path_for_session(root, token, owner.session_id)
        ProjectPersistence().write_recovery(
            recovery_path,
            request_from_document(
                newer,
                project_path=str(canonical_path),
                owner_session_id=owner.session_id,
            ),
        )

        class _Status:
            def __init__(self):
                self.calls = []

            def set_status(self, **kwargs):
                self.calls.append(kwargs)

        class _Fake:
            pass

        fake = _Fake()
        fake._s11_project_token = token
        fake._s11_recovery_session = observer
        observer.session_alive = lambda session_id: session_id == owner.session_id
        fake._s11_project_path = lambda: str(canonical_path)
        fake.foundation_state = _Status()

        assert integration_feature._maybe_offer_recovery(fake, canonical) is False
        assert recovery_path.is_file()
        assert fake.foundation_state.calls == []

        owner.close()

        assert integration_feature._maybe_offer_recovery(fake, canonical) is True
        assert recovery_path.is_file()
        assert fake.foundation_state.calls[-1]["save"][0] == "Recovery tersedia"
    finally:
        owner.close()
        observer.close()


def test_closed_recovery_session_is_detected_as_dead(tmp_path: Path) -> None:
    root = tmp_path / "recovery"
    owner = RecoverySessionLease(root)
    observer = RecoverySessionLease(root)
    owner.start()
    observer.start()
    owner_id = owner.session_id
    try:
        assert observer.session_alive(owner_id) is True
        owner.close()
        assert observer.session_alive(owner_id) is False
    finally:
        owner.close()
        observer.close()



def test_recovery_session_lease_tracks_real_second_process(tmp_path: Path) -> None:
    import os
    import subprocess
    import sys
    import textwrap

    root = tmp_path / "recovery"
    repo_root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(repo_root / "src") + (
        os.pathsep + existing if existing else ""
    )
    script = textwrap.dedent(
        r"""
        import sys
        import time
        from pathlib import Path
        from full_album_maker.integration_lifecycle_step11 import RecoverySessionLease

        lease = RecoverySessionLease(Path(sys.argv[1]), "external-owner")
        lease.start()
        print("LOCKED", flush=True)
        time.sleep(30)
        """
    )
    process = subprocess.Popen(
        [sys.executable, "-c", script, str(root)],
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    observer = RecoverySessionLease(root, "observer")
    observer.start()
    try:
        assert process.stdout is not None
        assert process.stdout.readline().strip() == "LOCKED"
        assert observer.session_alive("external-owner") is True

        process.terminate()
        process.wait(timeout=5)
        assert observer.session_alive("external-owner") is False
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        observer.close()
