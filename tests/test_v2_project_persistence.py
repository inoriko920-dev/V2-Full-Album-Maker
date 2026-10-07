from __future__ import annotations

import json
from pathlib import Path

import pytest

from full_album_maker.app_kernel import build_app_kernel
from full_album_maker.editor_models import ProjectDocument, ProjectSchemaError
from full_album_maker.integration_core_step11 import normalized_project_hash
from full_album_maker.integration_lifecycle_step11 import request_from_document
from full_album_maker.project import MediaItem, Project
from full_album_maker.project_migrations import migrate_project_v1
from full_album_maker.project_persistence import (
    ProjectPersistence,
    ProjectPersistenceConflict,
    RecoveryClassification,
)


ROOT = Path(__file__).resolve().parents[1]


def _document(name: str = "Persistence", *, revision: int = 0) -> ProjectDocument:
    doc = ProjectDocument.new_empty(name)
    doc.revision = revision
    doc.album_title = f"{name} Album"
    doc.validate()
    return doc


class _CompatibilityEnvelope:
    def __init__(self, document: ProjectDocument) -> None:
        self.document = document.clone()

    def to_dict(self) -> dict:
        return {
            "version": 1,
            "videos": [],
            "audios": [],
            "settings": {
                "auto_speed": True,
                "manual_speed": 1.0,
                "min_speed": 0.5,
                "loop_mode": "auto",
                "width": 1920,
                "height": 1080,
                "fps": 30,
                "codec": "h264",
                "video_bitrate": "12M",
                "audio_bitrate": "320k",
            },
            "album_document_v2": self.document.to_dict(),
        }


def test_native_save_roundtrip_uses_semantic_equality(tmp_path: Path) -> None:
    persistence = ProjectPersistence()
    original = _document("Native", revision=3)

    saved = persistence.save_document(tmp_path / "native-project", original)
    restored = persistence.load_document(saved)

    assert saved.endswith(".json")
    assert normalized_project_hash(restored) == normalized_project_hash(original)
    assert restored.to_dict() == original.to_dict()


def test_native_save_verification_failure_preserves_previous_file(tmp_path: Path) -> None:
    class RejectingPersistence(ProjectPersistence):
        def verify_document(self, path, expected):
            return False

    target = tmp_path / "canonical.json"
    target.write_text('{"old":"good"}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="staged tidak sama"):
        RejectingPersistence().save_document(target, _document("Rejected"))

    assert target.read_text(encoding="utf-8") == '{"old":"good"}\n'
    assert not list(tmp_path.glob(".canonical.json.*.stage.json"))


def test_compatibility_save_roundtrip_and_mismatch_preserves_old_file(tmp_path: Path) -> None:
    persistence = ProjectPersistence()
    expected = _document("Compatibility", revision=4)
    target = tmp_path / "compat.json"

    saved = persistence.save_compatibility(
        target,
        _CompatibilityEnvelope(expected),
        expected,
    )
    restored = persistence.load_document(saved)

    assert normalized_project_hash(restored) == normalized_project_hash(expected)

    old_bytes = target.read_bytes()
    wrong = _document("Wrong", revision=5)
    with pytest.raises(ValueError, match="staged tidak sama"):
        persistence.save_compatibility(
            target,
            _CompatibilityEnvelope(wrong),
            expected,
        )

    assert target.read_bytes() == old_bytes
    assert not list(tmp_path.glob(".compat.json.*.stage.json"))


def test_future_schema_and_timeline_payload_fail_closed(tmp_path: Path) -> None:
    persistence = ProjectPersistence()

    future = tmp_path / "future.json"
    future.write_text(
        json.dumps({"format": "full-album-maker-project", "schema_version": 999}),
        encoding="utf-8",
    )
    with pytest.raises(ProjectSchemaError, match="lebih baru"):
        persistence.load_document(future)

    timeline = tmp_path / "timeline.json"
    timeline.write_text(
        json.dumps({"version": 1, "audio_clips": [], "video_clips": []}),
        encoding="utf-8",
    )
    with pytest.raises(ProjectSchemaError, match="TimelinePlan"):
        persistence.load_document(timeline)


def test_legacy_v1_migration_is_deterministic_for_same_payload(tmp_path: Path) -> None:
    raw = Project(
        videos=[MediaItem("video.mp4", 30.0)],
        audios=[MediaItem("song.mp3", 20.0)],
    ).to_dict()

    first = migrate_project_v1(raw, name="Legacy")
    second = migrate_project_v1(raw, name="Legacy")

    assert first.to_dict() == second.to_dict()
    assert first.project_id == second.project_id
    assert [x.asset_id for x in first.media] == [x.asset_id for x in second.media]
    assert [x.song_id for x in first.playlist.entries] == [
        x.song_id for x in second.playlist.entries
    ]


def test_load_document_migrates_legacy_v1_deterministically(tmp_path: Path) -> None:
    raw = Project(audios=[MediaItem("song.mp3", 12.0)]).to_dict()
    path = tmp_path / "legacy.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    persistence = ProjectPersistence()

    first = persistence.load_document(path)
    second = persistence.load_document(path)

    assert first.to_dict() == second.to_dict()
    assert first.schema_version == 2


def test_recovery_classification_same_newer_stale_foreign_and_corrupt(tmp_path: Path) -> None:
    persistence = ProjectPersistence()
    canonical_path = tmp_path / "project.json"
    canonical = _document("Canonical", revision=5)

    same_path = tmp_path / "same.recovery.json"
    persistence.write_recovery(
        same_path,
        request_from_document(canonical, project_path=str(canonical_path)),
    )
    same = persistence.assess_recovery(
        same_path,
        canonical,
        canonical_path=canonical_path,
    )
    assert same is not None
    assert same.classification is RecoveryClassification.SAME

    newer_doc = canonical.clone()
    newer_doc.revision = 6
    newer_doc.album_title = "newer"
    newer_doc.validate()
    newer_path = tmp_path / "newer.recovery.json"
    persistence.write_recovery(
        newer_path,
        request_from_document(newer_doc, project_path=str(canonical_path)),
    )
    newer = persistence.assess_recovery(
        newer_path,
        canonical,
        canonical_path=canonical_path,
    )
    assert newer is not None
    assert newer.classification is RecoveryClassification.NEWER
    assert newer.document is not None
    assert newer.document.revision == 6

    stale_doc = canonical.clone()
    stale_doc.revision = 4
    stale_doc.album_title = "stale"
    stale_doc.validate()
    stale_path = tmp_path / "stale.recovery.json"
    persistence.write_recovery(
        stale_path,
        request_from_document(stale_doc, project_path=str(canonical_path)),
    )
    stale = persistence.assess_recovery(
        stale_path,
        canonical,
        canonical_path=canonical_path,
    )
    assert stale is not None
    assert stale.classification is RecoveryClassification.STALE

    foreign_path = tmp_path / "foreign.recovery.json"
    persistence.write_recovery(
        foreign_path,
        request_from_document(
            newer_doc,
            project_path=str(tmp_path / "different-project.json"),
        ),
    )
    foreign = persistence.assess_recovery(
        foreign_path,
        canonical,
        canonical_path=canonical_path,
    )
    assert foreign is not None
    assert foreign.classification is RecoveryClassification.FOREIGN

    corrupt_path = tmp_path / "corrupt.recovery.json"
    corrupt_path.write_text("{broken-json", encoding="utf-8")
    corrupt = persistence.assess_recovery(
        corrupt_path,
        canonical,
        canonical_path=canonical_path,
    )
    assert corrupt is not None
    assert corrupt.classification is RecoveryClassification.CORRUPT
    assert corrupt_path.is_file()
    assert corrupt_path.read_text(encoding="utf-8") == "{broken-json"


def test_recovery_clear_is_explicit_and_missing_candidate_is_none(tmp_path: Path) -> None:
    persistence = ProjectPersistence()
    path = tmp_path / "recovery.json"
    canonical = _document()

    assert persistence.assess_recovery(path, canonical) is None

    persistence.write_recovery(path, request_from_document(canonical))
    assert path.is_file()
    persistence.clear_recovery(path)
    assert not path.exists()


def test_app_kernel_owns_injected_project_persistence() -> None:
    persistence = ProjectPersistence()
    kernel = build_app_kernel(
        gui_runner=lambda: 0,
        portable_smoke_runner=lambda: 0,
        project_persistence=persistence,
    )

    assert kernel.persistence is persistence
    assert kernel.run([]) == 0


def test_editor_workspace_and_step11_save_route_through_m3_facade() -> None:
    editor_source = (
        ROOT / "src" / "full_album_maker" / "editor_workspace.py"
    ).read_text(encoding="utf-8")
    integration_source = (
        ROOT / "src" / "full_album_maker" / "integration_feature_step11.py"
    ).read_text(encoding="utf-8")

    assert "DEFAULT_PROJECT_PERSISTENCE.load_document" in editor_source
    assert "DEFAULT_PROJECT_PERSISTENCE.save_document" in editor_source
    assert "from .project_repository import load_project_document" not in editor_source

    assert "DEFAULT_PROJECT_PERSISTENCE.save_compatibility" in integration_source
    assert "DEFAULT_PROJECT_PERSISTENCE.write_recovery" in integration_source
    assert "DEFAULT_PROJECT_PERSISTENCE.assess_recovery" in integration_source
    assert "save_verified_legacy_project(path" not in integration_source



def test_stale_native_save_cannot_overwrite_newer_external_project(tmp_path: Path) -> None:
    persistence = ProjectPersistence()
    target = tmp_path / "shared.json"
    base = _document("Shared", revision=1)
    persistence.save_document(target, base)
    baseline = persistence.document_hash_on_disk(target)

    first = base.clone()
    first.revision = 2
    first.album_title = "Saved by instance A"
    first.validate()

    stale = base.clone()
    stale.revision = 2
    stale.album_title = "Stale instance B"
    stale.validate()

    persistence.save_document(
        target,
        first,
        expected_disk_hash=baseline,
    )

    with pytest.raises(ProjectPersistenceConflict, match="berubah sejak dibuka"):
        persistence.save_document(
            target,
            stale,
            expected_disk_hash=baseline,
        )

    restored = persistence.load_document(target)
    assert restored.album_title == "Saved by instance A"
    assert normalized_project_hash(restored) == normalized_project_hash(first)


def test_stale_compatibility_save_cannot_overwrite_other_instance(tmp_path: Path) -> None:
    persistence = ProjectPersistence()
    target = tmp_path / "shared-compat.json"
    base = _document("Shared Compatibility", revision=3)
    persistence.save_compatibility(
        target,
        _CompatibilityEnvelope(base),
        base,
    )
    baseline = persistence.document_hash_on_disk(target)

    first = base.clone()
    first.revision = 4
    first.album_title = "Instance A wins"
    first.validate()
    persistence.save_compatibility(
        target,
        _CompatibilityEnvelope(first),
        first,
        expected_disk_hash=baseline,
    )

    stale = base.clone()
    stale.revision = 4
    stale.album_title = "Instance B stale"
    stale.validate()
    with pytest.raises(ProjectPersistenceConflict, match="Save As"):
        persistence.save_compatibility(
            target,
            _CompatibilityEnvelope(stale),
            stale,
            expected_disk_hash=baseline,
        )

    assert persistence.load_document(target).album_title == "Instance A wins"


def test_expected_empty_hash_refuses_unexpected_existing_target(tmp_path: Path) -> None:
    persistence = ProjectPersistence()
    target = tmp_path / "appeared.json"
    existing = _document("Existing", revision=2)
    persistence.save_document(target, existing)

    with pytest.raises(ProjectPersistenceConflict):
        persistence.save_document(
            target,
            _document("New Attempt", revision=1),
            expected_disk_hash="",
        )
