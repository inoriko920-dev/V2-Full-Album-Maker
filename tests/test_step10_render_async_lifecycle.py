from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
import threading
import time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from full_album_maker.editor_models import MediaAsset, ProjectDocument, SongInstance, TIMEBASE
from full_album_maker.render_async_step10 import RenderAsyncBridge
from full_album_maker.render_center_model_step10 import (
    RenderJob,
    RenderMetrics,
    build_render_snapshot,
    settings_from_preset,
)


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def _job(tmp_path: Path) -> RenderJob:
    source = tmp_path / "song.wav"
    source.write_bytes(b"fixture-audio")
    document = ProjectDocument.new_empty("Render lifecycle")
    asset = MediaAsset(
        kind="audio",
        locator=str(source),
        original_name=source.name,
        source_duration_tick=2 * TIMEBASE,
    )
    document.media.append(asset)
    document.playlist.entries.append(
        SongInstance(
            asset_id=asset.asset_id,
            display_title="Lifecycle Fixture",
            source_out_tick=2 * TIMEBASE,
        )
    )
    document.validate()
    settings = settings_from_preset(
        "youtube_1080p",
        filename="render-lifecycle",
        output_folder=str(tmp_path),
    )
    return RenderJob(build_render_snapshot(document), settings)


def _pump(seconds: float = 0.2) -> None:
    app = _app()
    deadline = time.time() + max(0.0, float(seconds))
    while time.time() < deadline:
        app.processEvents()
        time.sleep(0.01)


class _BlockingRenderEngine:
    def __init__(self) -> None:
        self.started = threading.Event()
        self.release = threading.Event()
        self.finished = threading.Event()
        self.preflight_calls = 0

    def execute(self, job, *, cancel_event=None, on_metrics=None, on_log=None):
        self.started.set()
        self.release.wait(timeout=2.0)
        if on_metrics is not None:
            on_metrics(
                RenderMetrics(
                    percent=50.0,
                    rendered_seconds=1.0,
                    fps=30.0,
                    average_fps=30.0,
                    speed=1.0,
                    eta_seconds=1.0,
                )
            )
        if on_log is not None:
            on_log("late worker callback")
        self.finished.set()
        return SimpleNamespace(job_id=job.job_id, attempt_id=job.attempt_id)

    def preflight(self, document, settings):
        self.preflight_calls += 1
        return SimpleNamespace(report=object(), capability=object())

    def capability_for_settings(self, settings):
        return object()


def test_close_suppresses_late_render_callbacks_and_busy_reset(tmp_path: Path) -> None:
    _app()
    engine = _BlockingRenderEngine()
    bridge = RenderAsyncBridge(render_engine=engine)
    job = _job(tmp_path)
    events: list[str] = []

    bridge.render_started.connect(lambda *_args: events.append("started"))
    bridge.metrics_ready.connect(lambda *_args: events.append("metrics"))
    bridge.log_ready.connect(lambda *_args: events.append("log"))
    bridge.render_finished.connect(lambda *_args: events.append("finished"))
    bridge.render_failed.connect(lambda *_args: events.append("failed"))
    bridge.busy_changed.connect(lambda value: events.append(f"busy:{bool(value)}"))

    assert bridge.start(job) is True
    assert engine.started.wait(timeout=1.0)
    _pump(0.05)
    assert "started" in events
    assert "busy:True" in events

    bridge.close()
    assert bridge.closed is True
    assert bridge.busy is False
    baseline = tuple(events)

    engine.release.set()
    assert engine.finished.wait(timeout=1.0)
    _pump(0.25)

    assert tuple(events) == baseline
    bridge.close()  # idempotent


def test_start_after_close_is_rejected_without_reactivating_busy(tmp_path: Path) -> None:
    _app()
    engine = _BlockingRenderEngine()
    bridge = RenderAsyncBridge(render_engine=engine)
    job = _job(tmp_path)
    events: list[str] = []
    bridge.render_started.connect(lambda *_args: events.append("started"))
    bridge.busy_changed.connect(lambda value: events.append(f"busy:{bool(value)}"))

    bridge.close()

    assert bridge.start(job) is False
    assert bridge.busy is False
    assert bridge.closed is True
    assert events == []
    assert engine.started.is_set() is False


def test_preflight_after_close_is_invalidated_without_executor_error(tmp_path: Path) -> None:
    _app()
    engine = _BlockingRenderEngine()
    bridge = RenderAsyncBridge(render_engine=engine)
    job = _job(tmp_path)
    emitted: list[str] = []
    bridge.preflight_ready.connect(lambda *_args: emitted.append("ready"))
    bridge.preflight_failed.connect(lambda *_args: emitted.append("failed"))

    bridge.close()
    token = bridge.request_preflight(job.snapshot.document(), job.settings)
    _pump(0.05)

    assert token >= 1
    assert emitted == []
    assert engine.preflight_calls == 0
