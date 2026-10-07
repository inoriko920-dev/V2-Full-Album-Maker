from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from full_album_maker import media_feature
from full_album_maker.async_import import _probe_one
from full_album_maker.media_library_model import MediaType
from full_album_maker.media_probe_service import MediaProbeService
from full_album_maker.project import Project


class _Log:
    def __init__(self) -> None:
        self.lines: list[str] = []

    def appendPlainText(self, value: str) -> None:
        self.lines.append(str(value))


def _service() -> MediaProbeService:
    return MediaProbeService(
        duration_probe=lambda path, kind=None: 7.0,
        image_probe=lambda path: {"width": 100, "height": 100},
        audio_tag_probe=lambda path: ("", ""),
    )


def test_step03_import_drops_probe_result_if_source_changed_before_ui_adopt(
    tmp_path: Path,
) -> None:
    source = tmp_path / "step03-import.mp4"
    source.write_bytes(b"before")
    item = _probe_one("video", str(source), _service())
    source.write_bytes(b"changed-before-adopt-longer")

    fake = SimpleNamespace()
    fake._s03_jobs = 1
    fake.project = Project()
    fake.log = _Log()
    fake.media_workspace = SimpleNamespace(
        set_import_progress=lambda *args, **kwargs: None,
    )
    fake._sync_foundation_state = lambda: None
    fake.invalidate_timeline = lambda: None
    fake.refresh = lambda: None
    fake._s03_refresh = lambda reset=False: None

    media_feature._imported(
        fake,
        {
            "project": fake.project,
            "accepted": [("video", item)],
            "errors": [],
            "canceled": False,
        },
    )

    assert fake.project.videos == []
    assert fake._s03_jobs == 0
    assert any("source berubah" in line.casefold() for line in fake.log.lines)


def test_step03_older_relink_generation_cannot_overwrite_newer_request() -> None:
    fake = SimpleNamespace(
        project=object(),
        _s03_relink_generation={"asset-1": 2},
        log=_Log(),
    )

    media_feature._relinked(
        fake,
        {
            "project": fake.project,
            "asset_id": "asset-1",
            "generation": 1,
            "error": "",
        },
    )

    assert any("relink lama diabaikan" in line.casefold() for line in fake.log.lines)


def test_step03_relink_rejects_source_changed_after_probe_before_adopt(
    tmp_path: Path,
    monkeypatch,
) -> None:
    replacement = tmp_path / "replacement.mp4"
    replacement.write_bytes(b"replacement-before")
    item = _probe_one("video", str(replacement), _service())
    replacement.write_bytes(b"replacement-changed-after-probe-longer")

    warnings: list[str] = []
    monkeypatch.setattr(
        media_feature.QMessageBox,
        "warning",
        lambda _parent, _title, message: warnings.append(str(message)),
    )

    fake = SimpleNamespace(
        project=object(),
        _s03_relink_generation={"asset-1": 3},
        log=_Log(),
    )
    media_feature._relinked(
        fake,
        {
            "project": fake.project,
            "asset_id": "asset-1",
            "generation": 3,
            "old": "old.mp4",
            "new": str(replacement),
            "kind": MediaType.VIDEO.value,
            "item": item,
            "error": "",
        },
    )

    assert warnings
    assert "berubah setelah probe" in warnings[0]
