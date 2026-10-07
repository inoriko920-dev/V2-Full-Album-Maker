from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from full_album_maker import media_feature
from full_album_maker.media_library_model import MediaType, stable_asset_id
from full_album_maker.media_library_services import MediaSidecarStore, SidecarRecord


class _Log:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def appendPlainText(self, value: str) -> None:
        self.lines.append(str(value))


def _video(path: Path, duration: float = 5.0):
    return SimpleNamespace(
        path=str(path),
        duration=duration,
        width=1920,
        height=1080,
        fps=30.0,
        container="mp4",
        codec="h264",
    )


def _payload(project, old_path: Path, new_path: Path, item, asset_id: str):
    return {
        "project": project,
        "asset_id": asset_id,
        "old": str(old_path),
        "new": str(new_path),
        "kind": MediaType.VIDEO.value,
        "item": item,
        "error": "",
        "generation": 1,
    }


def _fake(project, store, asset_id: str):
    return SimpleNamespace(
        project=project,
        _s03_relink_generation={asset_id: 1},
        _s03_store=store,
        _foundation_project_path=str(store.project_path or ""),
        timeline_plan=None,
        log=_Log(),
        refresh=lambda: None,
        _s03_refresh=lambda _reset=False: None,
    )


def test_relink_to_source_already_used_by_other_asset_is_blocked(
    tmp_path: Path,
    monkeypatch,
) -> None:
    old_path = tmp_path / "missing-old.mp4"
    used_path = tmp_path / "already-used.mp4"
    used_path.write_bytes(b"used")
    old = _video(old_path)
    existing = _video(used_path)
    project = SimpleNamespace(videos=[old, existing], audios=[], _visual_order=[])
    project_path = tmp_path / "Project.json"
    project_path.write_text("{}", encoding="utf-8")
    store = MediaSidecarStore(project_path)
    old_id = stable_asset_id(str(old_path), MediaType.VIDEO)
    store.set(old_id, SidecarRecord(tags=("keep",)))

    warnings: list[str] = []
    monkeypatch.setattr(
        media_feature.async_mod,
        "_item_source_still_current",
        lambda _item: True,
    )
    monkeypatch.setattr(
        media_feature.QMessageBox,
        "warning",
        lambda _parent, _title, message: warnings.append(str(message)),
    )

    fake = _fake(project, store, old_id)
    media_feature._relinked(
        fake,
        _payload(project, old_path, used_path, _video(used_path), old_id),
    )

    assert old.path == str(old_path)
    assert existing.path == str(used_path)
    assert warnings and "sudah dipakai media lain" in warnings[0]
    assert store.get(old_id).tags == ("keep",)


def test_relink_sidecar_conflict_leaves_project_and_metadata_unchanged(
    tmp_path: Path,
    monkeypatch,
) -> None:
    old_path = tmp_path / "old.mp4"
    new_path = tmp_path / "replacement.mp4"
    new_path.write_bytes(b"replacement")
    old = _video(old_path)
    project = SimpleNamespace(videos=[old], audios=[], _visual_order=[str(old_path)])
    project_path = tmp_path / "Project.json"
    project_path.write_text("{}", encoding="utf-8")
    store = MediaSidecarStore(project_path)
    old_id = stable_asset_id(str(old_path), MediaType.VIDEO)
    new_id = stable_asset_id(str(new_path), MediaType.VIDEO)
    old_record = SidecarRecord(tags=("old",), description="keep old")
    new_record = SidecarRecord(tags=("new",), description="destination")
    store.set(old_id, old_record)
    store.set(new_id, new_record)

    warnings: list[str] = []
    monkeypatch.setattr(
        media_feature.async_mod,
        "_item_source_still_current",
        lambda _item: True,
    )
    monkeypatch.setattr(
        media_feature.QMessageBox,
        "warning",
        lambda _parent, _title, message: warnings.append(str(message)),
    )

    fake = _fake(project, store, old_id)
    media_feature._relinked(
        fake,
        _payload(project, old_path, new_path, _video(new_path), old_id),
    )

    assert old.path == str(old_path)
    assert project._visual_order == [str(old_path)]
    latest = MediaSidecarStore(project_path)
    assert latest.get(old_id) == old_record
    assert latest.get(new_id) == new_record
    assert warnings and "tidak dapat dimigrasikan dengan aman" in warnings[0]


def test_successful_relink_moves_sidecar_before_project_path_commit(
    tmp_path: Path,
    monkeypatch,
) -> None:
    old_path = tmp_path / "old-success.mp4"
    new_path = tmp_path / "new-success.mp4"
    new_path.write_bytes(b"replacement")
    old = _video(old_path)
    project = SimpleNamespace(videos=[old], audios=[], _visual_order=[str(old_path)])
    project_path = tmp_path / "Project.json"
    project_path.write_text("{}", encoding="utf-8")
    store = MediaSidecarStore(project_path)
    old_id = stable_asset_id(str(old_path), MediaType.VIDEO)
    new_id = stable_asset_id(str(new_path), MediaType.VIDEO)
    record = SidecarRecord(favorite=True, tags=("follow",), description="logical asset")
    store.set(old_id, record)

    monkeypatch.setattr(
        media_feature.async_mod,
        "_item_source_still_current",
        lambda _item: True,
    )

    fake = _fake(project, store, old_id)
    media_feature._relinked(
        fake,
        _payload(project, old_path, new_path, _video(new_path, 9.0), old_id),
    )

    assert old.path == str(new_path)
    assert old.duration == 9.0
    assert project._visual_order == [str(new_path)]
    latest = MediaSidecarStore(project_path)
    assert "old-id" not in latest.records()
    assert latest.get(new_id) == record
