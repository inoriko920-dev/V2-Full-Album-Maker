from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from full_album_maker import media_feature
from full_album_maker.media_library_model import MediaLibraryIndex
from full_album_maker.media_library_services import MediaSidecarStore, SidecarRecord
from full_album_maker.project import Project


class _Button:
    def setEnabled(self, _value):
        pass


class _Workspace:
    def __init__(self):
        self.import_file = _Button()
        self.import_folder = _Button()
        self.selection = SimpleNamespace(selected_ids=())
        self.index = None

    def set_index(self, value):
        self.index = value


class _Context:
    def set_counts(self, _value):
        pass

    def set_collection_counts(self, _value):
        pass


class _Timeline:
    def set_project(self, _project):
        pass


def _fake(project: Project, project_path: str = ""):
    fake = SimpleNamespace()
    fake.project = project
    fake._foundation_project_path = project_path
    fake._foundation_project_open = True
    fake._s03_jobs = 0
    fake._s03_project = project
    fake._s03_store = MediaSidecarStore(project_path or None)
    fake._s03_store.load()
    fake._s03_index = MediaLibraryIndex()
    fake.media_workspace = _Workspace()
    fake.media_context = _Context()
    fake.media_timeline_canvas = _Timeline()
    fake._s03_select = lambda _ids: None
    fake.log = SimpleNamespace(lines=[], appendPlainText=lambda text: fake.log.lines.append(str(text)))
    return fake


def test_refresh_same_project_first_save_carries_pending_sidecar(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(media_feature.visual_mod, "images", lambda _project: [])

    project = Project()
    fake = _fake(project)
    original_store = fake._s03_store
    original_store.update(
        "asset-pending",
        favorite=True,
        tags=("first-save",),
        persist=False,
    )

    saved = tmp_path / "Saved.json"
    saved.write_text("{}", encoding="utf-8")
    fake._foundation_project_path = str(saved)

    media_feature._refresh_media(fake, reset=False)

    assert fake._s03_store is original_store
    assert fake._s03_store.project_path == saved
    restored = MediaSidecarStore(saved).get("asset-pending")
    assert restored.favorite is True
    assert restored.tags == ("first-save",)


def test_refresh_project_switch_does_not_carry_old_sidecar(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(media_feature.visual_mod, "images", lambda _project: [])

    first_path = tmp_path / "First.json"
    second_path = tmp_path / "Second.json"
    first_path.write_text("{}", encoding="utf-8")
    second_path.write_text("{}", encoding="utf-8")

    first_project = Project()
    fake = _fake(first_project, str(first_path))
    fake._s03_store.update("first-only", favorite=True)

    second_seed = MediaSidecarStore(second_path)
    second_seed.update("second-only", tags=("second",))

    fake.project = Project()
    fake._foundation_project_path = str(second_path)

    media_feature._refresh_media(fake, reset=True)

    assert fake._s03_project is fake.project
    assert fake._s03_store.project_path == second_path
    assert fake._s03_store.get("second-only").tags == ("second",)
    assert "first-only" not in fake._s03_store.records()


def test_failed_first_save_sidecar_retries_on_next_refresh_without_losing_data(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from full_album_maker import media_library_services

    monkeypatch.setattr(media_feature.visual_mod, "images", lambda _project: [])
    project = Project()
    fake = _fake(project)
    store = fake._s03_store
    store.update(
        "asset-local",
        tags=("unsaved",),
        description="must survive",
        persist=False,
    )
    saved = tmp_path / "FirstSaveRetry.json"
    saved.write_text("{}", encoding="utf-8")
    fake._foundation_project_path = str(saved)

    original_write = media_library_services._write_sidecar_records
    attempts = 0

    def fail_once(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise OSError("temporary disk failure")
        return original_write(*args, **kwargs)

    monkeypatch.setattr(media_library_services, "_write_sidecar_records", fail_once)
    media_feature._refresh_media(fake, reset=False)

    assert fake._s03_store is store
    assert store.project_path == saved
    assert store.has_pending_changes is True
    assert store.get("asset-local").description == "must survive"
    assert any("belum dapat disimpan" in value for value in fake.log.lines)

    # A different instance may add independent metadata before our retry.
    external = MediaSidecarStore(saved)
    external.update("asset-external", favorite=True)

    media_feature._refresh_media(fake, reset=False)
    assert fake._s03_store is store
    assert store.has_pending_changes is False
    latest = MediaSidecarStore(saved)
    assert latest.get("asset-local").tags == ("unsaved",)
    assert latest.get("asset-local").description == "must survive"
    assert latest.get("asset-external").favorite is True


def test_failed_save_as_metadata_survives_explicit_refresh_until_retry(
    tmp_path: Path,
    monkeypatch,
) -> None:
    from full_album_maker import media_library_services

    monkeypatch.setattr(media_feature.visual_mod, "images", lambda _project: [])
    source = tmp_path / "Source.json"
    source.write_text("{}", encoding="utf-8")
    destination = tmp_path / "SaveAs.json"
    destination.write_text("{}", encoding="utf-8")

    fake = _fake(Project(), str(source))
    store = fake._s03_store
    store.update("asset-source", favorite=True, tags=("original",))
    fake._foundation_project_path = str(destination)

    original_write = media_library_services._write_sidecar_records
    attempts = 0

    def fail_twice(target, version, records):
        nonlocal attempts
        if target == store.path:
            attempts += 1
            if attempts <= 2:
                raise OSError("disk temporarily read-only")
        return original_write(target, version, records)

    monkeypatch.setattr(media_library_services, "_write_sidecar_records", fail_twice)
    media_feature._refresh_media(fake, reset=False)
    assert store.has_pending_changes
    assert store.get("asset-source").tags == ("original",)

    # Reset must not instantiate a fresh empty store while unsaved data exists.
    media_feature._refresh_media(fake, reset=True)
    assert fake._s03_store is store
    assert store.has_pending_changes
    assert store.get("asset-source").favorite is True
    assert not store.path.exists()

    media_feature._refresh_media(fake, reset=True)
    assert fake._s03_store is store
    assert not store.has_pending_changes
    assert MediaSidecarStore(destination).get("asset-source").tags == ("original",)
    assert MediaSidecarStore(source).get("asset-source").tags == ("original",)


def test_explicit_refresh_still_reloads_remote_metadata_without_pending_edits(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(media_feature.visual_mod, "images", lambda _project: [])
    project_path = tmp_path / "Shared.json"
    project_path.write_text("{}", encoding="utf-8")
    fake = _fake(Project(), str(project_path))
    old = fake._s03_store
    assert not old.has_pending_changes

    external = MediaSidecarStore(project_path)
    external.update("asset", description="newer on disk")

    media_feature._refresh_media(fake, reset=True)
    assert fake._s03_store is not old
    assert fake._s03_store.get("asset").description == "newer on disk"


def test_save_as_sidecar_migration_collision_keeps_local_and_disk_records(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(media_feature.visual_mod, "images", lambda _project: [])
    fake = _fake(Project())
    store = fake._s03_store
    store.set("old-id", SidecarRecord(tags=("source",)), persist=False)
    store.migrate_asset_id("old-id", "new-id", persist=False)

    dest = tmp_path / "Collision.json"
    dest.write_text("{}", encoding="utf-8")
    external = MediaSidecarStore(dest)
    external.set("old-id", SidecarRecord(tags=("target-old",)))
    external.set("new-id", SidecarRecord(tags=("target-new",)))
    disk_before = external.path.read_bytes()

    fake._foundation_project_path = str(dest)
    media_feature._refresh_media(fake, reset=False)

    assert fake._s03_store is store
    assert store.project_path == dest
    assert store.has_pending_changes
    assert store.get("new-id").tags == ("source",)
    assert external.path.read_bytes() == disk_before
    assert any("belum dapat disimpan" in text for text in fake.log.lines)

    # A second explicit refresh must not drop either side of this collision.
    media_feature._refresh_media(fake, reset=True)
    assert fake._s03_store is store
    assert store.has_pending_changes
    assert store.get("new-id").tags == ("source",)
    assert external.path.read_bytes() == disk_before



def test_save_as_conflicting_new_id_only_never_overwrites_destination(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(media_feature.visual_mod, "images", lambda _project: [])
    fake = _fake(Project())
    store = fake._s03_store
    store.set("old-id", SidecarRecord(tags=("local-source",)), persist=False)
    store.migrate_asset_id("old-id", "new-id", persist=False)

    project_path = tmp_path / "DestinationNewOnly.json"
    project_path.write_text("{}", encoding="utf-8")
    external = MediaSidecarStore(project_path)
    # Unlike the existing collision test, there is NO old-id on disk.
    external.set("new-id", SidecarRecord(tags=("external-destination",)))
    before = external.path.read_bytes()

    fake._foundation_project_path = str(project_path)
    media_feature._refresh_media(fake, reset=False)

    assert fake._s03_store is store
    assert store.has_pending_changes
    assert store.get("new-id").tags == ("local-source",)
    assert external.path.read_bytes() == before
    assert MediaSidecarStore(project_path).get("new-id").tags == ("external-destination",)
    assert any("belum dapat disimpan" in message for message in fake.log.lines)

    media_feature._refresh_media(fake, reset=True)
    assert store.has_pending_changes
    assert external.path.read_bytes() == before
