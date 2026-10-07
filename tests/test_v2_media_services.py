from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import threading
import time
import wave

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage

from full_album_maker.app_kernel import build_app_kernel
from full_album_maker.cache_manager import (
    CacheManager,
    CacheNamespacePolicy,
    current_cache_manager,
)
from full_album_maker.editor_models import ProjectDocument
from full_album_maker.media_library_model import MediaAsset, MediaMetadata, MediaType
from full_album_maker.media_preview_cache import MediaPreviewCache, generate_preview
from full_album_maker.media_probe_service import (
    MediaProbeResult,
    MediaProbeService,
    SourceFingerprint,
    current_media_probe_service,
)
from full_album_maker.preview_engine import PreviewEngine, current_preview_engine


ROOT = Path(__file__).resolve().parents[1]


def _media_cache_manager(root: Path, *, version: int = 1) -> CacheManager:
    return CacheManager(
        {
            "media-preview": CacheNamespacePolicy(
                "media-preview",
                version,
                lambda: root,
            )
        }
    )


def test_source_fingerprint_is_tiered_without_automatic_full_hash(tmp_path: Path) -> None:
    source = tmp_path / "media.bin"
    source.write_bytes(b"abc")

    fingerprint = SourceFingerprint.capture(source)

    assert fingerprint.tier == "F1"
    assert fingerprint.size_bytes == 3
    assert fingerprint.mtime_ns is not None
    assert fingerprint.full_sha256 == ""

    semantic = fingerprint.with_semantic({"kind": "audio", "duration": "1.25"})
    assert semantic.tier == "F2"
    assert semantic.cache_token() != fingerprint.cache_token()


def test_media_probe_service_normalizes_current_adapter_results(tmp_path: Path) -> None:
    source = tmp_path / "song.wav"
    source.write_bytes(b"fixture")
    service = MediaProbeService(
        duration_probe=lambda path, kind: 12.5,
        image_probe=lambda path: {"width": 1920, "height": 1080},
        audio_tag_probe=lambda path: ("Judul", "Artis"),
    )

    audio = service.probe(source, "audio")
    assert audio.media_kind == "audio"
    assert audio.duration_seconds == pytest.approx(12.5)
    assert audio.title == "Judul"
    assert audio.artist == "Artis"
    assert audio.fingerprint is not None
    assert audio.fingerprint.tier == "F2"

    photo = service.probe(source, "image")
    assert photo.media_kind == "photo"
    assert photo.duration_seconds == 0.0
    assert (photo.width, photo.height) == (1920, 1080)


def test_cache_manager_treats_zero_byte_as_miss_and_bounds_eviction(tmp_path: Path) -> None:
    root = tmp_path / "cache"
    manager = _media_cache_manager(root, version=3)
    zero = manager.root("media-preview") / "zero.bin"
    zero.write_bytes(b"")

    assert manager.version("media-preview") == 3
    assert manager.entry_usable(zero) is False

    outside = tmp_path / "outside.bin"
    outside.write_bytes(b"x")
    assert manager.evict("media-preview", outside) == 0
    assert outside.exists()

    assert manager.evict("media-preview", zero) == 1
    assert not zero.exists()


def test_media_preview_corrupt_metadata_is_disposable_cache_miss(tmp_path: Path) -> None:
    source = tmp_path / "foto.png"
    image = QImage(64, 48, QImage.Format.Format_RGB32)
    image.fill(0xFF4477AA)
    assert image.save(str(source), "PNG")

    manager = _media_cache_manager(tmp_path / "preview-cache", version=7)
    asset = MediaAsset(
        asset_id="asset-photo",
        path=str(source),
        display_name=source.name,
        media_type=MediaType.PHOTO,
        metadata=MediaMetadata(width=64, height=48),
    )

    first = Path(generate_preview(asset, cache_manager=manager))
    metadata = first.with_suffix(".json")
    assert first.is_file()
    assert json.loads(metadata.read_text(encoding="utf-8"))["version"] == 7

    metadata.write_text("{broken", encoding="utf-8")
    second = Path(generate_preview(asset, cache_manager=manager))

    assert second == first
    assert second.stat().st_size > 0
    repaired = json.loads(metadata.read_text(encoding="utf-8"))
    assert repaired["version"] == 7
    assert repaired["asset_id"] == asset.asset_id


def test_preview_engine_delegates_accurate_preview_with_snapshot_clone(tmp_path: Path) -> None:
    calls: dict[str, object] = {}

    class FakeAccurate:
        def render_frame(self, document, time_tick, destination):
            calls["document"] = document
            calls["tick"] = time_tick
            target = Path(destination)
            target.write_bytes(b"png")
            return str(target)

    manager = _media_cache_manager(tmp_path / "cache")
    engine = PreviewEngine(
        cache_manager=manager,
        accurate_factory=lambda: FakeAccurate(),
    )
    document = ProjectDocument.new_empty("M5 Preview")
    target = tmp_path / "accurate.png"

    assert engine.render_frame(document, -50, target) == str(target)
    assert calls["document"] is not document
    assert calls["tick"] == 0
    assert target.read_bytes() == b"png"


def test_app_kernel_binds_exact_m5_service_instances(tmp_path: Path) -> None:
    manager = _media_cache_manager(tmp_path / "cache")
    probe = MediaProbeService(
        duration_probe=lambda path, kind: 1.0,
        image_probe=lambda path: {"width": 1, "height": 1},
        audio_tag_probe=lambda path: ("", ""),
    )
    preview = PreviewEngine(
        cache_manager=manager,
        accurate_factory=lambda: pytest.fail("accurate preview should not execute"),
    )
    seen: dict[str, object] = {}

    def gui_runner() -> int:
        seen["probe"] = current_media_probe_service()
        seen["cache"] = current_cache_manager()
        seen["preview"] = current_preview_engine()
        return 0

    kernel = build_app_kernel(
        gui_runner=gui_runner,
        portable_smoke_runner=lambda: 0,
        media_probe_service=probe,
        cache_manager=manager,
        preview_engine=preview,
    )

    assert kernel.media_probe_service is probe
    assert kernel.cache_manager is manager
    assert kernel.preview_engine is preview
    assert kernel.run([]) == 0
    assert seen == {"probe": probe, "cache": manager, "preview": preview}
    assert current_media_probe_service() is None
    assert current_cache_manager() is None
    assert current_preview_engine() is None


def test_production_preview_and_probe_owners_route_through_m5_facades() -> None:
    editor = (ROOT / "src" / "full_album_maker" / "editor_workspace.py").read_text(encoding="utf-8")
    completion = (ROOT / "src" / "full_album_maker" / "media_completion.py").read_text(encoding="utf-8")
    decoded = (ROOT / "src" / "full_album_maker" / "visual_preview_decode_step06.py").read_text(encoding="utf-8")
    importer = (ROOT / "src" / "full_album_maker" / "async_import.py").read_text(encoding="utf-8")
    spectrum = (ROOT / "src" / "full_album_maker" / "spectrum_preview_step08.py").read_text(encoding="utf-8")

    assert "AccuratePreviewService().render_frame" not in editor
    assert "MediaPreviewCache(self, workers=" not in completion
    assert "MediaPreviewCache(self, workers=" not in decoded
    assert "probe_duration(path" not in importer
    assert "service_factory or AccuratePreviewService" not in spectrum

    assert "current_preview_engine()" in editor
    assert "new_media_preview_cache" in completion
    assert "new_media_preview_cache" in decoded
    assert "current_media_probe_service()" in importer
    assert "current_preview_engine()" in spectrum


@pytest.mark.skipif(
    not shutil.which("ffmpeg") or not shutil.which("ffprobe"),
    reason="FFmpeg/ffprobe tidak tersedia",
)
def test_real_ffmpeg_media_probe_service_audio_duration(tmp_path: Path) -> None:
    source = tmp_path / "tone.wav"
    sample_rate = 8000
    frames = int(sample_rate * 0.25)
    with wave.open(str(source), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(sample_rate)
        handle.writeframes(b"\x00\x00" * frames)

    service = MediaProbeService(audio_tag_probe=lambda path: ("", ""))
    result = service.probe(source, "audio")

    assert result.duration_seconds is not None
    assert result.duration_seconds == pytest.approx(0.25, abs=0.03)
    assert result.fingerprint is not None
    assert result.fingerprint.tier == "F2"


def test_media_preview_cache_close_stops_workers_and_rejects_new_requests(tmp_path: Path) -> None:
    manager = _media_cache_manager(tmp_path / "cache", version=9)
    cache = MediaPreviewCache(workers=2, cache_manager=manager)

    assert cache.closed is False
    assert cache.close(timeout=1.0) is True
    assert cache.closed is True
    assert all(not worker.is_alive() for worker in cache._threads)

    source = tmp_path / "after-close.png"
    source.write_bytes(b"not-a-real-image")
    asset = MediaAsset(
        asset_id="asset-after-close",
        path=str(source),
        display_name=source.name,
        media_type=MediaType.PHOTO,
    )
    assert cache.request(asset) is False
    assert cache.job_count == 0


# v2.0.1 regression guard: no preview completion is allowed after cache close.
def test_media_preview_cache_close_suppresses_inflight_completion(tmp_path: Path, monkeypatch) -> None:
    manager = _media_cache_manager(tmp_path / "cache-running", version=10)
    cache = MediaPreviewCache(workers=1, cache_manager=manager)

    source = tmp_path / "running-photo.png"
    source.write_bytes(b"fixture")
    asset = MediaAsset(
        asset_id="asset-running",
        path=str(source),
        display_name=source.name,
        media_type=MediaType.PHOTO,
    )

    entered = threading.Event()
    release = threading.Event()
    delivered: list[object] = []
    job_updates: list[int] = []

    def slow_generate(_asset, *, cache_manager=None):
        entered.set()
        assert release.wait(timeout=5)
        target = tmp_path / "generated.png"
        target.write_bytes(b"png")
        return str(target)

    monkeypatch.setattr("full_album_maker.media_preview_cache.generate_preview", slow_generate)
    cache.preview_ready.connect(delivered.append)
    cache.jobs_changed.connect(job_updates.append)

    assert cache.request(asset) is True
    assert entered.wait(timeout=2)
    assert cache.job_count == 1

    assert cache.close(timeout=0.01) is False
    assert cache.closed is True
    updates_at_close = list(job_updates)

    release.set()
    assert cache.close(timeout=1.0) is True

    deadline = time.time() + 0.5
    while time.time() < deadline:
        time.sleep(0.01)

    assert delivered == []
    assert job_updates == updates_at_close
    assert cache.job_count == 0
    assert all(not worker.is_alive() for worker in cache._threads)
