from __future__ import annotations

import os
import threading
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from full_album_maker.editor_workspace import EditorWorkspace


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_accurate_preview_completion_is_suppressed_after_workspace_close(
    tmp_path: Path,
    monkeypatch,
) -> None:
    app = _app()
    entered = threading.Event()
    release = threading.Event()

    class SlowPreviewEngine:
        def render_frame(self, document, tick, target):
            entered.set()
            assert release.wait(timeout=5)
            target = Path(target)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b"not-a-real-png")
            return str(target)

    engine = SlowPreviewEngine()
    monkeypatch.setattr(
        "full_album_maker.editor_workspace.current_preview_engine",
        lambda: engine,
    )

    workspace = EditorWorkspace()
    workspace.show()
    app.processEvents()

    workspace.render_accurate_preview()
    assert entered.wait(timeout=2)
    assert workspace._preview_busy is True

    status_after_start = workspace.status.text()
    assert workspace.close() is True
    app.processEvents()
    assert workspace.isVisible() is False

    release.set()
    deadline = time.time() + 2.0
    while time.time() < deadline:
        app.processEvents()
        time.sleep(0.01)

    assert workspace.status.text() == status_after_start
    assert workspace._preview_busy is False
