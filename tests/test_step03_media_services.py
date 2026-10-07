from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

from full_album_maker.media_library_model import MediaStatus, MediaType, stable_asset_id
from full_album_maker.media_library_services import (
    MediaSidecarStore, SidecarMigrationConflict, SidecarRecord, asset_from_item, collect_folder_paths,
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
