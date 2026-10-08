from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import threading
import wave

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from full_album_maker.app_errors import TaskCancelledError
from full_album_maker.app_kernel import build_app_kernel
from full_album_maker.beat_analysis import (
    BeatAnalysisService,
    current_beat_analysis_service,
    detect_beats,
)
from full_album_maker.cache_manager import CacheManager, CacheNamespacePolicy
from full_album_maker.preview_engine import PreviewEngine
from full_album_maker.task_lifecycle import TaskSupervisor


ROOT = Path(__file__).resolve().parents[1]


def _cache_manager(root: Path) -> CacheManager:
    return CacheManager(
        {
            "beat-analysis": CacheNamespacePolicy(
                "beat-analysis",
                1,
                lambda: root,
            )
        }
    )


def _fake_envelope() -> tuple[float, ...]:
    values = [0.02] * 100
    for index in (25, 50, 75):
        values[index - 1] = 0.15
        values[index] = 1.0
        values[index + 1] = 0.18
    return tuple(values)


def _service(
    tmp_path: Path,
    decoder,
) -> tuple[BeatAnalysisService, TaskSupervisor]:
    tasks = TaskSupervisor(max_workers=2, thread_name_prefix="test-beat")
    service = BeatAnalysisService(
        cache_manager=_cache_manager(tmp_path / "beat-cache"),
        task_supervisor=tasks,
        decoder=decoder,
        sample_hz=50,
    )
    return service, tasks


def test_detect_beats_is_deterministic_and_bounded() -> None:
    first = detect_beats(_fake_envelope(), 50)
    second = detect_beats(_fake_envelope(), 50)

    assert first == second
    assert [event.time_seconds for event in first] == pytest.approx([0.5, 1.0, 1.5])
    assert all(0.0 <= event.strength <= 1.0 for event in first)


def test_silence_is_honest_non_reactive_state() -> None:
    assert detect_beats((0.0,) * 200, 50) == ()


def test_service_caches_derived_result_and_source_change_invalidates_identity(tmp_path: Path) -> None:
    source = tmp_path / "song.wav"
    source.write_bytes(b"source-audio")
    calls = 0

    def decoder(_source, _hz, _token):
        nonlocal calls
        calls += 1
        return _fake_envelope()

    service, tasks = _service(tmp_path, decoder)
    try:
        first = service.analyze(source)
        second = service.analyze(source)
        assert first.available is True
        assert first.cache_hit is False
        assert second.available is True
        assert second.cache_hit is True
        assert second.beats == first.beats
        assert calls == 1

        source.write_bytes(source.read_bytes() + b"-changed")
        third = service.analyze(source)
        assert third.available is True
        assert third.cache_hit is False
        assert calls == 2
        assert third.fingerprint_token != first.fingerprint_token
    finally:
        tasks.close(timeout=1.0)


def test_corrupt_beat_cache_is_disposable_miss(tmp_path: Path) -> None:
    source = tmp_path / "song.wav"
    source.write_bytes(b"source-audio")
    calls = 0

    def decoder(_source, _hz, _token):
        nonlocal calls
        calls += 1
        return _fake_envelope()

    service, tasks = _service(tmp_path, decoder)
    try:
        first = service.analyze(source)
        cache = service.cache_path(source)
        assert first.available and cache.is_file()
        cache.write_text("{broken", encoding="utf-8")

        second = service.analyze(source)
        assert second.available is True
        assert second.cache_hit is False
        assert calls == 2
    finally:
        tasks.close(timeout=1.0)



@pytest.mark.parametrize(
    "malformation",
    [
        "non_object_beat",
        "invalid_envelope_text",
        "invalid_envelope_bool",
        "huge_envelope_number",
        "beat_beyond_audio_duration",
    ],
)
def test_parseable_but_corrupt_beat_cache_triggers_fresh_analysis(
    tmp_path: Path, malformation: str
) -> None:
    source = tmp_path / "song.wav"
    original_audio = b"source-audio-not-to-be-modified"
    source.write_bytes(original_audio)
    calls = 0

    def decoder(_source, _hz, _token):
        nonlocal calls
        calls += 1
        return _fake_envelope()

    service, tasks = _service(tmp_path, decoder)
    try:
        first = service.analyze(source)
        assert first.available and first.beats and first.cache_hit is False
        path = service.cache_path(source)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if malformation == "non_object_beat":
            # The old cache loader silently filtered this instead of retrying.
            payload["beats"].append("not-a-beat")
        elif malformation == "invalid_envelope_text":
            payload["envelope"][0] = "not-a-number"
        elif malformation == "invalid_envelope_bool":
            payload["envelope"][0] = True
        elif malformation == "huge_envelope_number":
            payload["envelope"][0] = 10**400
        elif malformation == "beat_beyond_audio_duration":
            payload["beats"][0]["time_seconds"] = first.duration_seconds + 100
        else:
            pytest.fail(f"Unknown malformation: {malformation}")
        path.write_text(json.dumps(payload), encoding="utf-8")

        recovered = service.analyze(source)
        assert recovered.available is True
        assert recovered.cache_hit is False
        assert recovered.beats == first.beats
        assert recovered.envelope == first.envelope
        assert calls == 2
        assert source.read_bytes() == original_audio
        # The disposable corrupted JSON was replaced, not reused forever.
        valid_again = service.analyze(source)
        assert valid_again.cache_hit is True
        assert valid_again.beats == first.beats
        assert calls == 2
    finally:
        tasks.close(timeout=1.0)


def test_decoder_failure_returns_non_reactive_fallback_without_fake_beats(tmp_path: Path) -> None:
    source = tmp_path / "broken.wav"
    source.write_bytes(b"not-audio")

    def decoder(_source, _hz, _token):
        raise RuntimeError("decoder unavailable")

    service, tasks = _service(tmp_path, decoder)
    try:
        result = service.analyze(source)
        assert result.available is False
        assert result.is_reactive is False
        assert result.envelope == ()
        assert result.beats == ()
        assert "decoder unavailable" in result.reason
        assert not service.cache_path(source).exists()
    finally:
        tasks.close(timeout=1.0)


def test_async_analysis_uses_m2_scope_and_invalidation_rejects_stale_result(tmp_path: Path) -> None:
    source = tmp_path / "song.wav"
    source.write_bytes(b"source-audio")
    started = threading.Event()
    release = threading.Event()

    def decoder(_source, _hz, token):
        started.set()
        assert release.wait(2.0)
        if token is not None:
            token.raise_if_cancelled()
        return _fake_envelope()

    service, tasks = _service(tmp_path, decoder)
    try:
        handle = service.submit(source)
        assert started.wait(1.0)
        previous_generation = service.generation
        assert service.invalidate("project changed") > previous_generation
        release.set()
        with pytest.raises(TaskCancelledError):
            handle.result(timeout=2.0)
    finally:
        release.set()
        tasks.close(timeout=1.0)


def test_app_kernel_owns_exact_beat_service_and_shared_lifecycle(tmp_path: Path) -> None:
    manager = _cache_manager(tmp_path / "cache")
    tasks = TaskSupervisor(max_workers=1)
    beat = BeatAnalysisService(
        cache_manager=manager,
        task_supervisor=tasks,
        decoder=lambda _source, _hz, _token: (),
    )
    preview = PreviewEngine(
        cache_manager=manager,
        accurate_factory=lambda: pytest.fail("accurate preview should not execute"),
    )
    seen: dict[str, object] = {}

    def gui_runner() -> int:
        seen["beat"] = current_beat_analysis_service()
        return 0

    kernel = build_app_kernel(
        gui_runner=gui_runner,
        portable_smoke_runner=lambda: 0,
        task_supervisor=tasks,
        cache_manager=manager,
        preview_engine=preview,
        beat_analysis_service=beat,
    )
    assert kernel.beat_analysis_service is beat
    assert kernel.beat_analysis_service.cache_manager is kernel.cache_manager
    assert kernel.beat_analysis_service.task_supervisor is kernel.tasks
    assert kernel.run([]) == 0
    assert seen["beat"] is beat
    assert current_beat_analysis_service() is None


def test_m6_service_does_not_create_private_worker_pool_or_touch_project_schema() -> None:
    source = (ROOT / "src" / "full_album_maker" / "beat_analysis.py").read_text(encoding="utf-8")
    models = (ROOT / "src" / "full_album_maker" / "editor_models.py").read_text(encoding="utf-8")

    assert "from concurrent.futures import ThreadPoolExecutor" not in source
    assert "ThreadPoolExecutor(" not in source
    assert "threading.Thread(" not in source
    assert "from .editor_models import ProjectDocument" not in source
    assert "schema_version =" not in source
    assert "task_supervisor.submit(" in source


def _write_pulse_wav(path: Path, *, duration: float = 2.0, sample_rate: int = 8000) -> None:
    frames = int(duration * sample_rate)
    centers = (0.5, 1.0, 1.5)
    payload = bytearray()
    for index in range(frames):
        time_s = index / sample_rate
        amplitude = 0.0
        for center in centers:
            if center <= time_s < center + 0.05:
                amplitude = max(
                    amplitude,
                    0.82 * math.sin(2.0 * math.pi * 440.0 * time_s),
                )
        sample = int(max(-1.0, min(1.0, amplitude)) * 32767)
        payload += int(sample).to_bytes(2, "little", signed=True)

    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(bytes(payload))


def _write_silence_wav(path: Path, *, duration: float = 1.0, sample_rate: int = 8000) -> None:
    frames = int(duration * sample_rate)
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(b"\x00\x00" * frames)


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="FFmpeg tidak tersedia")
def test_real_ffmpeg_detects_pulses_without_mutating_master_audio(tmp_path: Path) -> None:
    source = tmp_path / "pulse.wav"
    _write_pulse_wav(source)
    before = hashlib.sha256(source.read_bytes()).hexdigest()

    tasks = TaskSupervisor(max_workers=1)
    service = BeatAnalysisService(
        cache_manager=_cache_manager(tmp_path / "beat-cache"),
        task_supervisor=tasks,
    )
    try:
        result = service.analyze(source)
    finally:
        tasks.close(timeout=1.0)

    after = hashlib.sha256(source.read_bytes()).hexdigest()
    assert before == after
    assert result.available is True
    assert result.is_reactive is True
    times = [event.time_seconds for event in result.beats]
    assert len(times) == 3
    assert times == pytest.approx([0.52, 1.02, 1.52], abs=0.08)


@pytest.mark.skipif(not shutil.which("ffmpeg"), reason="FFmpeg tidak tersedia")
def test_real_ffmpeg_silence_stays_non_reactive(tmp_path: Path) -> None:
    source = tmp_path / "silence.wav"
    _write_silence_wav(source)

    tasks = TaskSupervisor(max_workers=1)
    service = BeatAnalysisService(
        cache_manager=_cache_manager(tmp_path / "beat-cache"),
        task_supervisor=tasks,
    )
    try:
        result = service.analyze(source)
    finally:
        tasks.close(timeout=1.0)

    assert result.available is True
    assert result.is_reactive is False
    assert result.beats == ()
    assert result.envelope
    assert max(result.envelope) == 0.0
