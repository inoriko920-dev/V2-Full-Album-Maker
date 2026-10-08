from dataclasses import dataclass
import errno
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

from full_album_maker.media_library_model import MediaStatus, MediaType, stable_asset_id
import full_album_maker.media_library_services as media_services
from full_album_maker.media_library_services import (
    MediaSidecarStore,
    SidecarCorruptionError,
    SidecarMigrationConflict,
    SidecarRecord,
    SidecarWriteConflict,
    SidecarStoreError,
    asset_from_item,
    collect_folder_paths,
    media_type_for_path,
)


@dataclass
class Item:
    path: str
    duration: float = 0.0


def test_sidecar_roundtrip_does_not_modify_source_media(tmp_path: Path):
    project = tmp_path / 'Album.json'
    project.write_text('{}', encoding='utf-8')
    media = tmp_path / 'Lagu Ω.mp3'
    media.write_bytes(b'original')
    before = media.read_bytes()
    store = MediaSidecarStore(project)
    asset_id = stable_asset_id(str(media), MediaType.AUDIO)
    store.set(asset_id, SidecarRecord(True, ('senja',), 'deskripsi', ('Musik',), 123.0))
    assert media.read_bytes() == before
    loaded = MediaSidecarStore(project).get(asset_id)
    assert loaded.favorite is True
    assert loaded.tags == ('senja',)
    assert loaded.collections == ('Musik',)


def test_asset_adapter_marks_missing_without_dropping_record(tmp_path: Path):
    missing = tmp_path / 'hilang.mp4'
    asset = asset_from_item(Item(str(missing), 42), MediaType.VIDEO)
    assert asset.status == MediaStatus.MISSING
    assert asset.metadata.duration == 42
    assert asset.path.endswith('hilang.mp4')


def test_folder_scan_supported_unicode_hidden_and_cancel(tmp_path: Path):
    (tmp_path / 'sub').mkdir()
    (tmp_path / '.cache').mkdir()
    (tmp_path / 'sub' / 'Video Ω.mp4').write_bytes(b'x')
    (tmp_path / 'foto.jpg').write_bytes(b'x')
    (tmp_path / 'ignore.txt').write_text('x')
    (tmp_path / '.cache' / 'hidden.mp3').write_bytes(b'x')
    result = collect_folder_paths(tmp_path)
    names = {Path(p).name for p in result.paths}
    assert names == {'Video Ω.mp4', 'foto.jpg'}
    assert result.canceled is False
    cancel = threading.Event(); cancel.set()
    assert collect_folder_paths(tmp_path, cancel).canceled is True


def test_media_type_resolver_supported_minimum():
    assert media_type_for_path('a.mp3') == MediaType.AUDIO
    assert media_type_for_path('a.jpg') == MediaType.PHOTO
    assert media_type_for_path('a.mp4') == MediaType.VIDEO
    assert media_type_for_path('a.exe') is None



def test_two_stale_sidecar_instances_preserve_changes_on_different_assets(
    tmp_path: Path,
) -> None:
    project = tmp_path / "Shared.json"
    project.write_text("{}", encoding="utf-8")
    first = MediaSidecarStore(project)
    second = MediaSidecarStore(project)
    first.load()
    second.load()

    first.update("asset-a", favorite=True)
    second.update("asset-b", tags=("tag-b",))

    latest = MediaSidecarStore(project)
    assert latest.get("asset-a").favorite is True
    assert latest.get("asset-b").tags == ("tag-b",)


def test_two_stale_sidecar_instances_merge_independent_fields_same_asset(
    tmp_path: Path,
) -> None:
    project = tmp_path / "SharedFields.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.set(
        "asset-shared",
        SidecarRecord(
            favorite=False,
            tags=("awal",),
            description="awal",
            collections=("Aset Utama",),
            imported_at=10.0,
        ),
    )

    first = MediaSidecarStore(project)
    second = MediaSidecarStore(project)
    first.load()
    second.load()

    first.update("asset-shared", favorite=True)
    second.update("asset-shared", tags=("baru",), description="instance-b")

    merged = MediaSidecarStore(project).get("asset-shared")
    assert merged.favorite is True
    assert merged.tags == ("baru",)
    assert merged.description == "instance-b"
    assert merged.collections == ("Aset Utama",)
    assert merged.imported_at == 10.0


def test_deferred_local_sidecar_save_merges_latest_disk_state(
    tmp_path: Path,
) -> None:
    project = tmp_path / "Deferred.json"
    project.write_text("{}", encoding="utf-8")
    external = MediaSidecarStore(project)
    external.update("external", favorite=True)

    local = MediaSidecarStore(project)
    local.load()
    local.update("local", tags=("pending",), persist=False)

    external.update("external", description="changed-after-local-load")
    local.save()

    latest = MediaSidecarStore(project)
    assert latest.get("local").tags == ("pending",)
    assert latest.get("external").favorite is True
    assert latest.get("external").description == "changed-after-local-load"


def test_sidecar_migration_preserves_other_instance_changes(tmp_path: Path) -> None:
    project = tmp_path / "Migration.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.set("old-id", SidecarRecord(tags=("keep-me",)))

    migrator = MediaSidecarStore(project)
    writer = MediaSidecarStore(project)
    migrator.load()
    writer.load()

    writer.update("other-id", favorite=True)
    migrator.migrate_asset_id("old-id", "new-id")

    latest = MediaSidecarStore(project)
    assert latest.get("new-id").tags == ("keep-me",)
    assert latest.get("other-id").favorite is True
    assert "old-id" not in latest.records()


def test_sidecar_lock_serializes_real_second_process(tmp_path: Path) -> None:
    project = tmp_path / "ProcessShared.json"
    project.write_text("{}", encoding="utf-8")
    store = MediaSidecarStore(project)
    target = store.path
    assert target is not None

    repo_root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(repo_root / "src") + (
        os.pathsep + existing if existing else ""
    )
    script = r"""
import sys
import time
from pathlib import Path
from full_album_maker.media_library_services import _sidecar_file_lock

target = Path(sys.argv[1])
with _sidecar_file_lock(target):
    print("LOCKED", flush=True)
    time.sleep(0.45)
"""
    process = subprocess.Popen(
        [sys.executable, "-c", script, str(target)],
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        assert process.stdout is not None
        assert process.stdout.readline().strip() == "LOCKED"
        started = time.monotonic()
        store.update("asset-process", favorite=True)
        elapsed = time.monotonic() - started
        assert elapsed >= 0.25
        assert store.get("asset-process").favorite is True
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)



def test_unsaved_sidecar_metadata_survives_first_project_save(tmp_path: Path) -> None:
    store = MediaSidecarStore(None)
    store.update(
        "asset-unsaved",
        favorite=True,
        tags=("pending",),
        description="before first save",
        persist=False,
    )

    project = tmp_path / "FirstSave.json"
    project.write_text("{}", encoding="utf-8")

    assert store.rebind_project_path(project, carry_current=True, persist=True) is True
    assert store.project_path == project

    restored = MediaSidecarStore(project).get("asset-unsaved")
    assert restored.favorite is True
    assert restored.tags == ("pending",)
    assert restored.description == "before first save"


def test_save_as_carries_current_sidecar_and_preserves_destination_only_records(
    tmp_path: Path,
) -> None:
    source_project = tmp_path / "Source.json"
    source_project.write_text("{}", encoding="utf-8")
    source = MediaSidecarStore(source_project)
    source.update(
        "asset-current",
        tags=("from-source",),
        description="authoritative current project",
    )

    destination_project = tmp_path / "Destination.json"
    destination_project.write_text("{}", encoding="utf-8")
    destination = MediaSidecarStore(destination_project)
    destination.update("asset-destination-only", favorite=True)

    assert source.rebind_project_path(
        destination_project,
        carry_current=True,
        persist=True,
    ) is True

    latest = MediaSidecarStore(destination_project)
    assert latest.get("asset-current").tags == ("from-source",)
    assert latest.get("asset-current").description == "authoritative current project"
    assert latest.get("asset-destination-only").favorite is True


def test_pending_relink_migration_survives_first_save_rebind(tmp_path: Path) -> None:
    store = MediaSidecarStore(None)
    store.set(
        "old-id",
        SidecarRecord(tags=("keep",), description="pending relink"),
        persist=False,
    )
    store.migrate_asset_id("old-id", "new-id", persist=False)

    project = tmp_path / "RelinkFirstSave.json"
    project.write_text("{}", encoding="utf-8")
    store.rebind_project_path(project, carry_current=True, persist=True)

    latest = MediaSidecarStore(project)
    assert latest.get("new-id").tags == ("keep",)
    assert latest.get("new-id").description == "pending relink"
    assert "old-id" not in latest.records()


def test_rebind_without_carry_loads_destination_fresh(tmp_path: Path) -> None:
    first_project = tmp_path / "First.json"
    second_project = tmp_path / "Second.json"
    first_project.write_text("{}", encoding="utf-8")
    second_project.write_text("{}", encoding="utf-8")

    first = MediaSidecarStore(first_project)
    first.update("first-only", favorite=True)

    second_seed = MediaSidecarStore(second_project)
    second_seed.update("second-only", tags=("fresh",))

    first.rebind_project_path(
        second_project,
        carry_current=False,
        persist=False,
    )

    assert first.get("second-only").tags == ("fresh",)
    assert "first-only" not in first.records()



def test_sidecar_migration_refuses_conflicting_destination_metadata(
    tmp_path: Path,
) -> None:
    project = tmp_path / "MigrationConflict.json"
    project.write_text("{}", encoding="utf-8")
    store = MediaSidecarStore(project)
    old = SidecarRecord(
        favorite=True,
        tags=("old",),
        description="metadata lama",
    )
    destination = SidecarRecord(
        favorite=False,
        tags=("destination",),
        description="metadata tujuan",
    )
    store.set("old-id", old)
    store.set("new-id", destination)

    try:
        store.migrate_asset_id("old-id", "new-id")
    except SidecarMigrationConflict:
        pass
    else:
        raise AssertionError("Konflik metadata relink harus diblokir")

    latest = MediaSidecarStore(project)
    assert latest.get("old-id") == old
    assert latest.get("new-id") == destination


def test_deferred_migration_conflict_with_other_instance_fails_without_data_loss(
    tmp_path: Path,
) -> None:
    project = tmp_path / "DeferredMigrationConflict.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    old = SidecarRecord(tags=("old",), description="follow logical asset")
    seed.set("old-id", old)

    migrator = MediaSidecarStore(project)
    migrator.load()
    migrator.migrate_asset_id("old-id", "new-id", persist=False)

    external = MediaSidecarStore(project)
    destination = SidecarRecord(tags=("external",), description="new destination")
    external.set("new-id", destination)

    try:
        migrator.save()
    except SidecarMigrationConflict:
        pass
    else:
        raise AssertionError("Deferred migration conflict harus gagal aman")

    latest = MediaSidecarStore(project)
    assert latest.get("old-id") == old
    assert latest.get("new-id") == destination


def test_sidecar_migration_deduplicates_identical_destination_record(
    tmp_path: Path,
) -> None:
    project = tmp_path / "IdenticalMigration.json"
    project.write_text("{}", encoding="utf-8")
    record = SidecarRecord(
        favorite=True,
        tags=("same",),
        description="identical",
    )
    store = MediaSidecarStore(project)
    store.set("old-id", record)
    store.set("new-id", record)

    store.migrate_asset_id("old-id", "new-id")

    latest = MediaSidecarStore(project)
    assert "old-id" not in latest.records()
    assert latest.get("new-id") == record



def test_corrupt_sidecar_is_quarantined_without_losing_original_bytes(
    tmp_path: Path,
) -> None:
    project = tmp_path / "Corrupt.json"
    project.write_text("{}", encoding="utf-8")
    store = MediaSidecarStore(project)
    target = store.path
    assert target is not None
    corrupt = b'{"version": 1, "records": '
    target.write_bytes(corrupt)

    assert store.load() == {}
    assert "dikarantina" in store.last_recovery_warning
    assert store.quarantined_path is not None
    assert store.quarantined_path.read_bytes() == corrupt
    assert not target.exists()
    assert store.persistence_blocked is False

    store.update("fresh", favorite=True)
    assert target.is_file()
    assert MediaSidecarStore(project).get("fresh").favorite is True
    assert store.quarantined_path.read_bytes() == corrupt


def test_unsupported_sidecar_version_is_preserved_and_blocks_writes(
    tmp_path: Path,
) -> None:
    project = tmp_path / "Future.json"
    project.write_text("{}", encoding="utf-8")
    store = MediaSidecarStore(project)
    target = store.path
    assert target is not None
    payload = {
        "version": 999,
        "records": {
            "future": {
                "favorite": True,
                "tags": ["future"],
                "description": "new schema",
                "collections": [],
                "imported_at": 1.0,
            }
        },
    }
    original = json.dumps(payload).encode("utf-8")
    target.write_bytes(original)

    assert store.load() == {}
    assert store.persistence_blocked is True
    assert "tidak didukung" in store.last_recovery_warning
    assert target.read_bytes() == original
    assert store.quarantined_path is None

    try:
        store.update("local", tags=("must-not-write",))
    except SidecarStoreError:
        pass
    else:
        raise AssertionError("Unsupported sidecar version harus memblok write")

    assert target.read_bytes() == original


def test_runtime_corruption_is_quarantined_and_retry_restores_last_good_memory(
    tmp_path: Path,
) -> None:
    project = tmp_path / "RuntimeCorrupt.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update(
        "asset-a",
        favorite=True,
        tags=("keep",),
        description="last-known-good",
    )

    store = MediaSidecarStore(project)
    assert store.get("asset-a").description == "last-known-good"
    target = store.path
    assert target is not None

    corrupt = b'{"version": 1, "records": {"asset-a": '
    target.write_bytes(corrupt)

    try:
        store.update("asset-a", description="new-value")
    except SidecarCorruptionError:
        pass
    else:
        raise AssertionError("Corruption saat runtime harus gagal sebelum write")

    assert store.quarantined_path is not None
    assert store.quarantined_path.read_bytes() == corrupt
    assert not target.exists()
    assert store.get("asset-a").description == "last-known-good"

    # Explicit retry after quarantine rebuilds a clean sidecar from the last
    # known-good in-memory snapshot plus the new requested change.
    store.update("asset-a", description="new-value")
    latest = MediaSidecarStore(project).get("asset-a")
    assert latest.favorite is True
    assert latest.tags == ("keep",)
    assert latest.description == "new-value"


def test_sidecar_load_cleans_only_orphan_transaction_temp_files(
    tmp_path: Path,
) -> None:
    project = tmp_path / "Temps.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset-a", favorite=True)
    target = seed.path
    assert target is not None

    orphan = target.parent / f"{target.name}.deadbeef.tmp"
    unrelated = target.parent / "unrelated.tmp"
    orphan.write_bytes(b"partial-sidecar")
    unrelated.write_bytes(b"keep")

    loaded = MediaSidecarStore(project)
    assert loaded.get("asset-a").favorite is True
    assert not orphan.exists()
    assert unrelated.read_bytes() == b"keep"


def test_sidecar_replace_enospc_preserves_previous_file_and_cleans_temp(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project = tmp_path / "NoSpace.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset-a", tags=("old",))
    target = seed.path
    assert target is not None
    original = target.read_bytes()

    store = MediaSidecarStore(project)
    assert store.get("asset-a").tags == ("old",)

    def no_space(*args, **kwargs):
        raise OSError(errno.ENOSPC, "No space left on device")

    monkeypatch.setattr(media_services.os, "replace", no_space)

    try:
        store.update("asset-a", tags=("new",))
    except OSError as exc:
        assert exc.errno == errno.ENOSPC
    else:
        raise AssertionError("ENOSPC harus menggagalkan sidecar publish")

    assert target.read_bytes() == original
    assert not list(target.parent.glob(f"{target.name}.*.tmp"))


def test_failed_corrupt_sidecar_quarantine_blocks_persistence(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project = tmp_path / "CannotQuarantine.json"
    project.write_text("{}", encoding="utf-8")
    store = MediaSidecarStore(project)
    target = store.path
    assert target is not None
    corrupt = b'{"version":'
    target.write_bytes(corrupt)

    monkeypatch.setattr(
        media_services.os,
        "replace",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            PermissionError("replace blocked")
        ),
    )
    monkeypatch.setattr(
        media_services.shutil,
        "copy2",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            PermissionError("copy blocked")
        ),
    )

    assert store.load() == {}
    assert store.persistence_blocked is True
    assert "dinonaktifkan" in store.last_recovery_warning
    assert target.read_bytes() == corrupt

    try:
        store.update("asset-a", favorite=True)
    except SidecarStoreError:
        pass
    else:
        raise AssertionError("Write harus diblok jika corruption tidak bisa diamankan")

    assert target.read_bytes() == corrupt



def test_two_stale_instances_cannot_overwrite_same_metadata_field(
    tmp_path: Path,
) -> None:
    project = tmp_path / "SameFieldConflict.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update(
        "asset-shared",
        description="baseline",
        tags=("keep",),
    )

    first = MediaSidecarStore(project)
    second = MediaSidecarStore(project)
    assert first.get("asset-shared").description == "baseline"
    assert second.get("asset-shared").description == "baseline"

    first.update("asset-shared", description="instance-a")

    try:
        second.update("asset-shared", description="instance-b")
    except SidecarWriteConflict as exc:
        assert "description" in str(exc)
    else:
        raise AssertionError("Stale same-field write harus diblokir")

    latest = MediaSidecarStore(project).get("asset-shared")
    assert latest.description == "instance-a"
    assert latest.tags == ("keep",)


def test_stale_instances_still_merge_different_fields_on_same_asset(
    tmp_path: Path,
) -> None:
    project = tmp_path / "DifferentFields.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update(
        "asset-shared",
        favorite=False,
        tags=("baseline",),
        description="baseline",
    )

    first = MediaSidecarStore(project)
    second = MediaSidecarStore(project)
    first.load()
    second.load()

    first.update("asset-shared", favorite=True)
    second.update(
        "asset-shared",
        tags=("instance-b",),
        description="description-b",
    )

    latest = MediaSidecarStore(project).get("asset-shared")
    assert latest.favorite is True
    assert latest.tags == ("instance-b",)
    assert latest.description == "description-b"


def test_stale_same_field_write_is_allowed_when_intended_value_matches_disk(
    tmp_path: Path,
) -> None:
    project = tmp_path / "IdempotentSameField.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset-shared", description="baseline")

    first = MediaSidecarStore(project)
    second = MediaSidecarStore(project)
    first.load()
    second.load()

    first.update("asset-shared", description="same-final-value")
    second.update("asset-shared", description="same-final-value")

    assert (
        MediaSidecarStore(project).get("asset-shared").description
        == "same-final-value"
    )


def test_refresh_after_same_field_conflict_allows_new_edit(
    tmp_path: Path,
) -> None:
    project = tmp_path / "RefreshAfterConflict.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset-shared", description="baseline")

    first = MediaSidecarStore(project)
    stale = MediaSidecarStore(project)
    first.load()
    stale.load()
    first.update("asset-shared", description="instance-a")

    try:
        stale.update("asset-shared", description="stale-write")
    except SidecarWriteConflict:
        pass
    else:
        raise AssertionError("Conflict fixture tidak terpicu")

    refreshed = MediaSidecarStore(project)
    assert refreshed.get("asset-shared").description == "instance-a"
    refreshed.update("asset-shared", description="after-refresh")

    assert (
        MediaSidecarStore(project).get("asset-shared").description
        == "after-refresh"
    )


def test_deferred_same_asset_independent_fields_merge_on_save(tmp_path: Path) -> None:
    project = tmp_path / "DeferredSameAsset.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset", description="baseline", tags=("initial",))

    local = MediaSidecarStore(project)
    remote = MediaSidecarStore(project)
    assert local.get("asset").description == "baseline"
    assert remote.get("asset").description == "baseline"

    local.update("asset", tags=("pending",), persist=False)
    remote.update("asset", description="remote newer")
    assert local.save() is True

    actual = MediaSidecarStore(project).get("asset")
    assert actual.tags == ("pending",)
    assert actual.description == "remote newer"


def test_deferred_same_field_conflict_blocks_save_without_data_loss(
    tmp_path: Path,
) -> None:
    project = tmp_path / "DeferredSameField.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset", description="baseline", favorite=False)

    local = MediaSidecarStore(project)
    remote = MediaSidecarStore(project)
    local.load()
    remote.load()
    local.update("asset", description="pending-local", persist=False)
    remote.update("asset", description="remote-new", favorite=True)
    target = local.path
    assert target is not None
    untouched_bytes = target.read_bytes()

    try:
        local.save()
    except SidecarWriteConflict as exc:
        assert "description" in str(exc)
    else:
        raise AssertionError("Deferred stale same-field save must fail closed")

    assert target.read_bytes() == untouched_bytes
    assert local.get("asset").description == "pending-local"
    actual = MediaSidecarStore(project).get("asset")
    assert actual.description == "remote-new"
    assert actual.favorite is True


def test_deferred_field_edits_accumulate_without_overwriting_remote_fields(
    tmp_path: Path,
) -> None:
    project = tmp_path / "DeferredAccumulated.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset", tags=("initial",), description="baseline")

    local = MediaSidecarStore(project)
    remote = MediaSidecarStore(project)
    local.load()
    remote.load()
    local.update("asset", tags=("new",), persist=False)
    local.update("asset", favorite=True, persist=False)
    remote.update("asset", description="remote")
    local.save()

    actual = MediaSidecarStore(project).get("asset")
    assert actual.tags == ("new",)
    assert actual.favorite is True
    assert actual.description == "remote"


def test_deferred_same_value_concurrent_edit_is_idempotent(tmp_path: Path) -> None:
    project = tmp_path / "DeferredIdempotent.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset", description="baseline")
    local = MediaSidecarStore(project)
    remote = MediaSidecarStore(project)
    local.load()
    remote.load()

    local.update("asset", description="same", persist=False)
    remote.update("asset", description="same")
    assert local.save() is True
    assert MediaSidecarStore(project).get("asset").description == "same"


def test_deferred_pending_conflict_blocks_unrelated_immediate_update(
    tmp_path: Path,
) -> None:
    project = tmp_path / "DeferredThenImmediate.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset", description="baseline")

    local = MediaSidecarStore(project)
    remote = MediaSidecarStore(project)
    local.load()
    remote.load()
    local.update("asset", description="deferred", persist=False)
    remote.update("asset", description="remote")

    try:
        local.update("asset", favorite=True)
    except SidecarWriteConflict:
        pass
    else:
        raise AssertionError("Immediate write must not flush conflicting pending edit")

    assert MediaSidecarStore(project).get("asset").favorite is False
    assert MediaSidecarStore(project).get("asset").description == "remote"


def test_deferred_then_immediate_same_field_is_not_a_false_conflict(
    tmp_path: Path,
) -> None:
    project = tmp_path / "DeferredThenImmediateSameField.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset", tags=("baseline",), description="keep")

    local = MediaSidecarStore(project)
    remote = MediaSidecarStore(project)
    local.load()
    remote.load()
    local.update("asset", tags=("pending",), persist=False)
    remote.update("asset", favorite=True)
    local.update("asset", tags=("final",))

    actual = MediaSidecarStore(project).get("asset")
    assert actual.tags == ("final",)
    assert actual.favorite is True
    assert actual.description == "keep"


def test_deferred_fields_survive_quarantine_and_explicit_retry(
    tmp_path: Path,
) -> None:
    project = tmp_path / "DeferredQuarantine.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset", tags=("baseline",), description="last good")

    local = MediaSidecarStore(project)
    local.load()
    local.update("asset", tags=("deferred",), persist=False)
    target = local.path
    assert target is not None
    target.write_bytes(b'{"version": 1, "records":')

    try:
        local.save()
    except SidecarCorruptionError:
        pass
    else:
        raise AssertionError("Corrupt sidecar must be quarantined first")

    assert local.quarantined_path is not None
    assert local.quarantined_path.read_bytes() == b'{"version": 1, "records":'
    assert local.save() is True

    actual = MediaSidecarStore(project).get("asset")
    assert actual.description == "last good"
    assert actual.tags == ("deferred",)



def test_sidecar_load_retries_after_initial_lock_timeout(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from contextlib import contextmanager

    project = tmp_path / "IntermittentLock.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset", favorite=True, tags=("preserve",))

    original_lock = media_services._sidecar_file_lock
    attempts = 0

    @contextmanager
    def intermittent_lock(target: Path):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise OSError("Metadata Media lock busy")
        with original_lock(target):
            yield

    monkeypatch.setattr(media_services, "_sidecar_file_lock", intermittent_lock)
    store = MediaSidecarStore(project)
    try:
        store.get("asset")
    except OSError as exc:
        assert "lock busy" in str(exc)
    else:
        raise AssertionError("Initial lock timeout must propagate")

    assert store._loaded is False
    assert store.records()["asset"].tags == ("preserve",)
    assert store.get("asset").favorite is True
    assert attempts == 2


def test_sidecar_load_retries_after_orphan_cleanup_failure(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project = tmp_path / "IntermittentCleanup.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset", description="on disk")
    target = seed.path
    assert target is not None
    original = target.read_bytes()

    cleanup = media_services._cleanup_sidecar_temps
    attempts = 0

    def intermittent_cleanup(path: Path) -> int:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise PermissionError("temporary cleanup error")
        return cleanup(path)

    monkeypatch.setattr(
        media_services, "_cleanup_sidecar_temps", intermittent_cleanup
    )
    store = MediaSidecarStore(project)
    try:
        store.load()
    except PermissionError:
        pass
    else:
        raise AssertionError("Cleanup failure must propagate to caller")

    assert store._loaded is False
    assert store.get("asset").description == "on disk"
    assert attempts == 2
    assert target.read_bytes() == original


def test_deferred_relink_blocks_foreign_old_id_only_on_save_as(
    tmp_path: Path,
) -> None:
    source = MediaSidecarStore(None)
    source.set("old-id", SidecarRecord(tags=("original-source",)), persist=False)
    source.migrate_asset_id("old-id", "new-id", persist=False)

    destination = tmp_path / "ForeignOldOnly.json"
    destination.write_text("{}", encoding="utf-8")
    foreign = MediaSidecarStore(destination)
    foreign.set("old-id", SidecarRecord(tags=("foreign-old",)))
    before = foreign.path.read_bytes()

    try:
        source.rebind_project_path(destination, carry_current=True, persist=True)
    except SidecarMigrationConflict:
        pass
    else:
        raise AssertionError("Foreign old-ID metadata must block Save As relink")

    assert foreign.path.read_bytes() == before
    assert MediaSidecarStore(destination).get("old-id").tags == ("foreign-old",)
    assert source.get("new-id").tags == ("original-source",)
    assert source.has_pending_changes is True

    # A retry cannot silently overwrite the destination either.
    try:
        source.save()
    except SidecarMigrationConflict:
        pass
    else:
        raise AssertionError("Retry must remain fail-closed")
    assert foreign.path.read_bytes() == before


def test_deferred_relink_accepts_same_value_old_id_and_preserves_other_assets(
    tmp_path: Path,
) -> None:
    record = SidecarRecord(favorite=True, tags=("same-source",))
    source = MediaSidecarStore(None)
    source.set("old-id", record, persist=False)
    source.migrate_asset_id("old-id", "new-id", persist=False)

    destination = tmp_path / "SameOldSafe.json"
    destination.write_text("{}", encoding="utf-8")
    existing = MediaSidecarStore(destination)
    existing.set("old-id", record)
    existing.set("other-id", SidecarRecord(description="unrelated"))

    assert source.rebind_project_path(destination, persist=True)
    latest = MediaSidecarStore(destination)
    assert "old-id" not in latest.records()
    assert latest.get("new-id") == record
    assert latest.get("other-id").description == "unrelated"
    assert source.has_pending_changes is False


def test_deferred_relink_chain_blocks_foreign_original_id(
    tmp_path: Path,
) -> None:
    source = MediaSidecarStore(None)
    source.set("asset-a", SidecarRecord(description="source-a"), persist=False)
    source.migrate_asset_id("asset-a", "asset-b", persist=False)
    source.migrate_asset_id("asset-b", "asset-c", persist=False)
    assert source.get("asset-c").description == "source-a"

    destination = tmp_path / "ForeignChain.json"
    destination.write_text("{}", encoding="utf-8")
    disk = MediaSidecarStore(destination)
    disk.set("asset-a", SidecarRecord(description="foreign-a"))
    original = disk.path.read_bytes()
    try:
        source.rebind_project_path(destination, persist=True)
    except SidecarMigrationConflict:
        pass
    else:
        raise AssertionError("Chained relink must validate original foreign ID")

    assert disk.path.read_bytes() == original
    assert source.get("asset-c").description == "source-a"
    assert source.has_pending_changes is True


def test_deferred_relink_without_local_source_does_not_move_foreign_record(
    tmp_path: Path,
) -> None:
    source = MediaSidecarStore(None)
    source.migrate_asset_id("absent-local", "new-id", persist=False)
    destination = tmp_path / "UnknownOld.json"
    destination.write_text("{}", encoding="utf-8")
    foreign = MediaSidecarStore(destination)
    foreign.set("absent-local", SidecarRecord(description="foreign-only"))
    before = foreign.path.read_bytes()

    try:
        source.rebind_project_path(destination, persist=True)
    except SidecarMigrationConflict:
        pass
    else:
        raise AssertionError("Absent local source must not migrate foreign data")

    assert foreign.path.read_bytes() == before
    assert source.has_pending_changes is True


def test_sidecar_transient_read_permission_error_retries_without_quarantine(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project = tmp_path / "ReadRetry.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("asset", description="healthy media metadata", favorite=True)
    target = seed.path
    assert target is not None
    original_bytes = target.read_bytes()

    original_read_text = Path.read_text
    attempts = 0

    def fail_once(self: Path, *args, **kwargs):
        nonlocal attempts
        if self == target:
            attempts += 1
            if attempts == 1:
                raise PermissionError("sharing violation from another app")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_once)
    store = MediaSidecarStore(project)
    try:
        store.load()
    except SidecarStoreError as exc:
        assert not isinstance(exc, SidecarCorruptionError)
        assert "sharing violation" in str(exc)
    else:
        raise AssertionError("Transient read error must propagate as retryable")

    assert store._loaded is False
    assert store.persistence_blocked is False
    assert store.quarantined_path is None
    assert not store.last_recovery_warning
    assert target.read_bytes() == original_bytes
    assert list(tmp_path.glob("*.corrupt-*")) == []

    assert store.get("asset").description == "healthy media metadata"
    assert store.get("asset").favorite is True
    assert store._loaded is True
    assert attempts == 2
    assert target.read_bytes() == original_bytes


def test_sidecar_save_keeps_pending_edits_when_disk_read_temporarily_fails(
    tmp_path: Path,
    monkeypatch,
) -> None:
    project = tmp_path / "WriteReadRetry.json"
    project.write_text("{}", encoding="utf-8")
    seed = MediaSidecarStore(project)
    seed.update("local", description="preserve disk description")
    seed.update("other", favorite=True)
    target = seed.path
    assert target is not None

    store = MediaSidecarStore(project)
    store.update("local", tags=("pending-tag",), persist=False)
    assert store.has_pending_changes
    before = target.read_bytes()

    original_read_text = Path.read_text
    attempts = 0

    def fail_once(self: Path, *args, **kwargs):
        nonlocal attempts
        if self == target:
            attempts += 1
            if attempts == 1:
                raise PermissionError("antivirus temporarily locked file")
        return original_read_text(self, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", fail_once)
    try:
        store.save()
    except SidecarStoreError as exc:
        assert not isinstance(exc, SidecarCorruptionError)
    else:
        raise AssertionError("Save must fail closed on unreadable healthy disk file")

    assert store.has_pending_changes
    assert store.get("local").tags == ("pending-tag",)
    assert target.read_bytes() == before
    assert store.quarantined_path is None
    assert list(tmp_path.glob("*.corrupt-*")) == []

    assert store.save() is True
    assert not store.has_pending_changes
    disk = MediaSidecarStore(project)
    assert disk.get("local").description == "preserve disk description"
    assert disk.get("local").tags == ("pending-tag",)
    assert disk.get("other").favorite is True


def test_sidecar_invalid_utf8_still_quarantines_genuinely_corrupt_bytes(
    tmp_path: Path,
) -> None:
    project = tmp_path / "UnreadableEncoding.json"
    project.write_text("{}", encoding="utf-8")
    store = MediaSidecarStore(project)
    target = store.path
    assert target is not None
    bad_data = b"\xff\xfe\x80invalid utf-8"
    target.write_bytes(bad_data)

    assert store.load() == {}
    assert store.quarantined_path is not None
    assert store.quarantined_path.read_bytes() == bad_data
    assert not target.exists()
    assert "karantina" in store.last_recovery_warning


def test_scan_folder_skips_windows_directory_junctions_without_skipping_siblings(
    tmp_path: Path,
    monkeypatch,
) -> None:
    # On Windows a junction can point back to an ancestor while is_symlink()
    # remains False. Simulate its is_junction() result deterministically on
    # every OS so an infinite recursive scan can be detected by this test.
    junction = tmp_path / "linked-back-to-parent"
    junction.mkdir()
    (junction / "should-not-import.mp3").write_bytes(b"hidden through junction")

    nested = tmp_path / "normal-nested"
    nested.mkdir()
    (nested / "regular Ω.wav").write_bytes(b"valid media")
    (tmp_path / "top-level.mp4").write_bytes(b"valid media")
    (tmp_path / "ignore.md").write_text("ignored", encoding="utf-8")

    real_is_junction = Path.is_junction
    visited_junction = []

    def simulated_windows_junction(self: Path) -> bool:
        if self == junction:
            visited_junction.append(str(self))
            return True
        return real_is_junction(self)

    monkeypatch.setattr(Path, "is_junction", simulated_windows_junction)
    assert junction.is_symlink() is False
    discovered = list(media_services.scan_folder(tmp_path))
    assert visited_junction == [str(junction)]
    assert {entry.name for entry in discovered} == {
        "regular Ω.wav", "top-level.mp4",
    }
    assert "should-not-import.mp3" not in {entry.name for entry in discovered}


def test_scan_folder_keeps_deterministic_order_with_junction_skipped(
    tmp_path: Path,
    monkeypatch,
) -> None:
    junction = tmp_path / "B-junction"
    junction.mkdir()
    (junction / "must-skip.flac").write_bytes(b"skip")
    nested = tmp_path / "A-normal"
    nested.mkdir()
    (nested / "01.wav").write_bytes(b"ok")
    (tmp_path / "02.mp3").write_bytes(b"ok")

    real_is_junction = Path.is_junction
    monkeypatch.setattr(
        Path, "is_junction",
        lambda self: self == junction or real_is_junction(self),
    )

    first = media_services.collect_folder_paths(tmp_path)
    second = media_services.collect_folder_paths(tmp_path)
    assert first.paths == second.paths
    assert {Path(p).name for p in first.paths} == {"01.wav", "02.mp3"}
    assert first.canceled is False
