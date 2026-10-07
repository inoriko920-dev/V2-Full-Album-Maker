from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from full_album_maker import media_feature
from full_album_maker.media_library_model import MediaLibraryIndex
from full_album_maker.media_library_services import MediaSidecarStore
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
