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
from full_album_maker.media_preview_cache import MediaPreviewCache, generate_preview, invalidate_source
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


def test_preview_jobs_changed_reentrant_close_cannot_strand_a_queued_job(
    tmp_path: Path,
) -> None:
    """Close from the synchronous jobs signal must drain the accepted job.

    A previous request() notified jobs_changed *before* enqueueing work.
    Closing in a listener then stopped the worker and request() enqueued a
    permanently stranded job (job_count == 1) after close had finished.
    """
    source = tmp_path / "close-at-notification.png"
    image = QImage(64, 48, QImage.Format.Format_RGB32)
    image.fill(0xFF5588AA)
    assert image.save(str(source), "PNG")
    original = source.read_bytes()

    manager = _media_cache_manager(tmp_path / "preview-close-queue", version=13)
    cache = MediaPreviewCache(workers=1, cache_manager=manager)
    asset = MediaAsset(
        asset_id="close-while-notifying",
        path=str(source),
        display_name=source.name,
        media_type=MediaType.PHOTO,
        metadata=MediaMetadata(width=64, height=48),
    )
    notifications: list[int] = []

    def close_on_first_job(job_count: int) -> None:
        notifications.append(job_count)
        if job_count == 1:
            cache.close(timeout=2.0)

    cache.jobs_changed.connect(close_on_first_job)
    try:
        assert cache.request(asset) is True
        assert 1 in notifications
        assert cache.closed is True
        assert cache.close(timeout=2.0) is True
        assert cache.job_count == 0
        assert cache.request(asset) is False
        assert all(not worker.is_alive() for worker in cache._threads)
        assert source.read_bytes() == original
    finally:
        cache.close(timeout=2.0)


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

    def slow_generate(_asset, *, cache_manager=None, publish_guard=None):
        assert callable(publish_guard)
        entered.set()
        assert release.wait(timeout=5)
        assert publish_guard() is False
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


@pytest.mark.parametrize("wrong_root", [[], None, 42, "not a cache record"])
def test_preview_cache_nonobject_json_is_cache_miss_not_preview_failure(
    tmp_path: Path,
    wrong_root,
) -> None:
    source = tmp_path / "original-source.png"
    image = QImage(64, 48, QImage.Format.Format_RGB32)
    image.fill(0xFF4477AA)
    assert image.save(str(source), "PNG")
    original_source_bytes = source.read_bytes()

    manager = _media_cache_manager(tmp_path / "preview-cache-nonobject", version=11)
    asset = MediaAsset(
        asset_id="bad-root-photo",
        path=str(source),
        display_name=source.name,
        media_type=MediaType.PHOTO,
        metadata=MediaMetadata(width=64, height=48),
    )

    preview = Path(generate_preview(asset, cache_manager=manager))
    metadata = preview.with_suffix(".json")
    assert preview.is_file()
    metadata.write_text(json.dumps(wrong_root), encoding="utf-8")

    # The cache has a parseable JSON document, but not a metadata object.
    # The app must regenerate this disposable preview, not raise AttributeError.
    regenerated = Path(generate_preview(asset, cache_manager=manager))
    assert regenerated == preview
    assert regenerated.is_file()
    assert regenerated.stat().st_size > 0
    record = json.loads(metadata.read_text(encoding="utf-8"))
    assert isinstance(record, dict)
    assert record["asset_id"] == asset.asset_id
    assert record["version"] == 11
    assert source.read_bytes() == original_source_bytes


def test_invalidate_preview_skips_nonobject_json_and_continues_to_valid_record(
    tmp_path: Path,
) -> None:
    image = QImage(64, 48, QImage.Format.Format_RGB32)
    image.fill(0xFF4477AA)
    broken_source = tmp_path / "broken-cache-but-healthy-source.png"
    valid_source = tmp_path / "updated-source.png"
    assert image.save(str(broken_source), "PNG")
    assert image.save(str(valid_source), "PNG")
    original_broken = broken_source.read_bytes()
    original_valid = valid_source.read_bytes()

    manager = _media_cache_manager(tmp_path / "preview-cache-invalidation", version=12)
    bad_asset = MediaAsset(
        asset_id="bad-preview-metadata",
        path=str(broken_source),
        display_name=broken_source.name,
        media_type=MediaType.PHOTO,
    )
    valid_asset = MediaAsset(
        asset_id="valid-preview-metadata",
        path=str(valid_source),
        display_name=valid_source.name,
        media_type=MediaType.PHOTO,
    )
    bad_preview = Path(generate_preview(bad_asset, cache_manager=manager))
    valid_preview = Path(generate_preview(valid_asset, cache_manager=manager))
    bad_meta = bad_preview.with_suffix(".json")
    valid_meta = valid_preview.with_suffix(".json")
    bad_meta.write_text("[]", encoding="utf-8")

    # Invalidation must process every candidate even when an unrelated record
    # has a malformed JSON root. Neither source file may be affected.
    count = invalidate_source(valid_source, cache_manager=manager)
    assert count == 2
    assert not valid_preview.exists()
    assert not valid_meta.exists()
    assert bad_preview.exists()
    assert bad_meta.read_text(encoding="utf-8") == "[]"
    assert broken_source.read_bytes() == original_broken
    assert valid_source.read_bytes() == original_valid
