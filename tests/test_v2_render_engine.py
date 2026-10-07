from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import threading
import wave

import pytest

from full_album_maker.app_kernel import build_app_kernel
from full_album_maker.editor_models import MediaAsset, ProjectDocument, SongInstance, TIMEBASE
from full_album_maker.paths import ffmpeg_path, ffprobe_path
from full_album_maker.render_async_step10 import RenderAsyncBridge
from full_album_maker.render_center_model_step10 import (
    RenderJob,
    RenderSettings,
    build_render_snapshot,
)
from full_album_maker.render_engine import (
    RenderEngine,
    bind_render_engine,
    current_render_engine,
)
from full_album_maker.render_executor_step10 import Step10RenderError
from full_album_maker.render_preflight_step10 import FFmpegCapability


def _capability() -> FFmpegCapability:
    return FFmpegCapability(
        ffmpeg="ffmpeg",
        ffprobe="ffprobe",
        version="ffmpeg m4 fixture",
        encoders=frozenset({"libx264", "libx265"}),
        source="bundled",
    )


def _settings(tmp_path: Path, *, filename: str = "m4") -> RenderSettings:
    return RenderSettings(
        filename=filename,
        output_folder=str(tmp_path),
        width=320,
        height=240,
        fps=24,
        video_codec="h264",
        video_bitrate_bps=500_000,
        audio_codec="aac",
        audio_bitrate_bps=128_000,
        sample_rate=48_000,
        hardware_mode="software",
        container="mp4",
        overwrite=False,
        preset_id="custom",
    )


def _document(tmp_path: Path, *, seconds: int = 2) -> ProjectDocument:
    source = tmp_path / "source.wav"
    source.write_bytes(b"m4-audio-fixture")
    doc = ProjectDocument.new_empty("M4 Render Facade")
    asset = MediaAsset(
        kind="audio",
        locator=str(source),
        original_name=source.name,
        source_duration_tick=seconds * TIMEBASE,
    )
    doc.media.append(asset)
    doc.playlist.entries.append(
        SongInstance(
            asset_id=asset.asset_id,
            display_title="M4 Song",
            source_out_tick=seconds * TIMEBASE,
        )
    )
    doc.validate()
    return doc


def test_preflight_uses_clone_and_one_capability_policy(tmp_path: Path) -> None:
    doc = _document(tmp_path)
    settings = _settings(tmp_path)
    seen: dict[str, object] = {}

    def capability_factory(value: RenderSettings) -> FFmpegCapability:
        seen["settings"] = value
        return _capability()

    def preflight_runner(document, render_settings, *, capability):
        seen["document"] = document
        seen["capability"] = capability
        document.name = "mutated-inside-preflight"
        return SimpleNamespace(blocked=False, snapshot=object())

    engine = RenderEngine(
        capability_factory=capability_factory,
        preflight_runner=preflight_runner,
    )
    result = engine.preflight(doc, settings)

    assert result.capability is seen["capability"]
    assert seen["settings"] is settings
    assert seen["document"] is not doc
    assert doc.name == "M4 Render Facade"


def test_execute_delegates_to_proven_executor_adapter_and_preserves_callbacks(tmp_path: Path) -> None:
    doc = _document(tmp_path)
    job = RenderJob(build_render_snapshot(doc), _settings(tmp_path))
    calls: dict[str, object] = {}
    metrics_cb = lambda value: None
    log_cb = lambda line: None

    class FakeExecutor:
        def __init__(self, capability):
            calls["capability"] = capability

        def execute(self, received, *, cancel_event=None, on_metrics=None, on_log=None):
            calls["job"] = received
            calls["cancel_event"] = cancel_event
            calls["metrics"] = on_metrics
            calls["log"] = on_log
            return "legacy-executor-result"

    event = threading.Event()
    engine = RenderEngine(
        capability_factory=lambda settings: _capability(),
        executor_factory=FakeExecutor,
    )
    result = engine.execute(
        job,
        cancel_event=event,
        on_metrics=metrics_cb,
        on_log=log_cb,
    )

    assert result == "legacy-executor-result"
    assert calls["job"] is job
    assert calls["cancel_event"] is event
    assert calls["metrics"] is metrics_cb
    assert calls["log"] is log_cb
    assert calls["capability"] == _capability()
    assert engine.busy is False


def test_render_engine_rejects_overlapping_attempts(tmp_path: Path) -> None:
    doc = _document(tmp_path)
    first = RenderJob(build_render_snapshot(doc), _settings(tmp_path, filename="first"))
    second = RenderJob(build_render_snapshot(doc), _settings(tmp_path, filename="second"))
    engine: RenderEngine

    class ReentrantExecutor:
        def __init__(self, capability):
            pass

        def execute(self, job, **kwargs):
            with pytest.raises(Step10RenderError, match="double-start"):
                engine.execute(second)
            return "first-ok"

    engine = RenderEngine(
        capability_factory=lambda settings: _capability(),
        executor_factory=ReentrantExecutor,
    )
    assert engine.execute(first) == "first-ok"
    assert engine.busy is False


def test_app_kernel_binds_exact_render_engine_for_legacy_gui_then_resets_context() -> None:
    engine = RenderEngine(capability_factory=lambda settings: _capability())
    seen: list[object] = []

    kernel = build_app_kernel(
        gui_runner=lambda: seen.append(current_render_engine()) or 0,
        portable_smoke_runner=lambda: 0,
        render_engine=engine,
    )
    assert kernel.render_engine is engine
    assert current_render_engine() is None
    assert kernel.run([]) == 0
    assert seen == [engine]
    assert current_render_engine() is None


def test_render_async_bridge_captures_app_kernel_bound_engine() -> None:
    engine = RenderEngine(capability_factory=lambda settings: _capability())
    with bind_render_engine(engine):
        bridge = RenderAsyncBridge()
    try:
        assert bridge.render_engine is engine
        assert current_render_engine() is None
    finally:
        bridge.close()


def test_render_async_bridge_no_longer_owns_direct_render_executor_import() -> None:
    import full_album_maker.render_async_step10 as module

    source = Path(module.__file__).read_text(encoding="utf-8")
    assert "RenderExecutor(" not in source
    assert "from .render_executor_step10 import RenderExecutor" not in source
    assert "self._render_engine.execute(" in source
    assert "self._render_engine.preflight(" in source


def _write_silence_wav(path: Path, seconds: int = 1, sample_rate: int = 48_000) -> None:
    frames = b"\x00\x00" * sample_rate * seconds
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(frames)


def test_real_ffmpeg_render_engine_preserves_verified_publish_contract(tmp_path: Path) -> None:
    if not ffmpeg_path() or not ffprobe_path():
        pytest.skip("Real FFmpeg/ffprobe smoke only runs in targeted M4 infrastructure job.")

    source = tmp_path / "real-source.wav"
    _write_silence_wav(source)
    stat = source.stat()
    doc = ProjectDocument.new_empty("M4 Real FFmpeg")
    audio = MediaAsset(
        kind="audio",
        locator=str(source),
        original_name=source.name,
        fingerprint={"size": stat.st_size, "mtime_ns": stat.st_mtime_ns},
        source_duration_tick=TIMEBASE,
    )
    doc.media.append(audio)
    doc.playlist.entries.append(
        SongInstance(
            asset_id=audio.asset_id,
            display_title="M4 Real",
            source_out_tick=TIMEBASE,
        )
    )
    doc.validate()

    settings = _settings(tmp_path, filename="m4-real")
    job = RenderJob(build_render_snapshot(doc), settings)
    result = RenderEngine().execute(job)

    final = settings.final_output
    assert final.is_file() and final.stat().st_size > 0
    assert result.verification.verified is True
    assert result.verification.has_video is True
    assert result.verification.has_audio is True
    assert job.verified_output == str(final)
