from __future__ import annotations

import os
import threading
import time
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QImage

from full_album_maker.media_library_model import MediaAsset, MediaMetadata, MediaStatus, MediaType, stable_asset_id
from full_album_maker.cache_manager import CacheManager, CacheNamespacePolicy
import full_album_maker.media_preview_cache as preview_module
from full_album_maker.media_preview_cache import (
    MediaPreviewCache,
    generate_preview,
    invalidate_source,
    preview_cache_path,
)
from full_album_maker.media_probe_service import SourceFingerprint


def _photo(path: Path) -> MediaAsset:
    return MediaAsset(
        asset_id=stable_asset_id(str(path), MediaType.PHOTO),
        path=str(path),
        display_name=path.name,
        media_type=MediaType.PHOTO,
        metadata=MediaMetadata(width=64, height=48),
    )


def test_photo_preview_cache_hit_and_source_change_invalidate_identity(tmp_path):
    source = tmp_path / "foto.png"
    image = QImage(64, 48, QImage.Format.Format_RGB32)
    image.fill(0xFF4477AA)
    assert image.save(str(source), "PNG")
    asset = _photo(source)
    first_target = preview_cache_path(asset)
    first = generate_preview(asset)
    assert Path(first).is_file()
    first_mtime = Path(first).stat().st_mtime_ns
    second = generate_preview(asset)
    assert second == first
    assert Path(second).stat().st_mtime_ns == first_mtime

    time.sleep(0.01)
    source.write_bytes(source.read_bytes() + b"\n")
    assert preview_cache_path(asset) != first_target
    assert invalidate_source(source) >= 1
    assert not first_target.exists()


def test_missing_media_has_no_usable_preview(tmp_path):
    path = tmp_path / "missing.jpg"
    asset = MediaAsset(
        asset_id=stable_asset_id(str(path), MediaType.PHOTO),
        path=str(path),
        display_name=path.name,
        media_type=MediaType.PHOTO,
        status=MediaStatus.MISSING,
    )
    try:
        generate_preview(asset)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("Missing media tidak boleh menghasilkan preview cache")



def test_source_change_during_preview_generation_never_publishes_cache(
    tmp_path,
    monkeypatch,
):
    source = tmp_path / "mutating.png"
    source.write_bytes(b"original-source")
    asset = _photo(source)
    cache_root = tmp_path / "cache"
    manager = CacheManager(
        {
            "media-preview": CacheNamespacePolicy(
                "media-preview",
                1,
                lambda: cache_root,
            )
        }
    )
    expected_target = preview_cache_path(asset, cache_manager=manager)

    def mutate_while_generating(_source, target):
        Path(target).write_bytes(b"valid-preview-bytes")
        source.write_bytes(b"changed-source-bytes-longer")

    monkeypatch.setattr(preview_module, "_generate_photo", mutate_while_generating)

    try:
        generate_preview(asset, cache_manager=manager)
    except RuntimeError as exc:
        assert "berubah" in str(exc)
    else:
        raise AssertionError("Mutasi source harus membatalkan publikasi preview cache")

    assert not expected_target.exists()
    assert not expected_target.with_suffix(".json").exists()
    assert not list(cache_root.glob("*.png"))



def test_same_size_same_mtime_replacement_gets_new_preview_identity(tmp_path):
    source = tmp_path / "replace-in-place.png"
    source.write_bytes(b"AAAA")
    asset = _photo(source)
    before = SourceFingerprint.capture(source)
    first = preview_cache_path(asset)

    replacement = tmp_path / "replacement.tmp"
    replacement.write_bytes(b"BBBB")
    old_stat = source.stat()
    os.utime(
        replacement,
        ns=(old_stat.st_atime_ns, old_stat.st_mtime_ns),
    )
    os.replace(replacement, source)
    os.utime(
        source,
        ns=(old_stat.st_atime_ns, old_stat.st_mtime_ns),
    )

    after = SourceFingerprint.capture(source)
    assert source.stat().st_size == old_stat.st_size
    assert source.stat().st_mtime_ns == old_stat.st_mtime_ns
    if before.same_source_version(after):
        pytest.skip("Filesystem tidak mengekspos ctime/inode replacement identity")

    assert preview_cache_path(asset) != first


def test_preview_worker_reset_mid_generation_never_republishes_stale_cache(
    tmp_path,
    monkeypatch,
    qapp,
):
    source = tmp_path / "slow.png"
    source.write_bytes(b"source-v1")
    asset = _photo(source)
    cache_root = tmp_path / "cache-reset"
    manager = CacheManager(
        {
            "media-preview": CacheNamespacePolicy(
                "media-preview",
                1,
                lambda: cache_root,
            )
        }
    )

    entered = threading.Event()
    release = threading.Event()

    def blocking_generate(_source, target):
        entered.set()
        assert release.wait(timeout=5)
        Path(target).write_bytes(b"preview-old-generation")

    monkeypatch.setattr(preview_module, "_generate_photo", blocking_generate)

    cache = MediaPreviewCache(workers=1, cache_manager=manager)
    results = []
    cache.preview_ready.connect(results.append)
    try:
        assert cache.request(asset) is True
        assert entered.wait(timeout=2)

        cache.reset()
        release.set()

        deadline = time.time() + 3.0
        while time.time() < deadline and cache.job_count:
            qapp.processEvents()
            time.sleep(0.01)
        qapp.processEvents()

        assert cache.job_count == 0
        assert results == []
        assert not list(cache_root.glob("*.png"))
        assert not list(cache_root.glob("*.json"))
    finally:
        release.set()
        cache.close(timeout=2.0)


def test_reset_discards_queued_old_generation_work(
    tmp_path,
    monkeypatch,
    qapp,
):
    first_source = tmp_path / "first.png"
    second_source = tmp_path / "second.png"
    first_source.write_bytes(b"first")
    second_source.write_bytes(b"second")
    first = _photo(first_source)
    second = _photo(second_source)
    cache_root = tmp_path / "cache-drain"
    manager = CacheManager(
        {
            "media-preview": CacheNamespacePolicy(
                "media-preview",
                1,
                lambda: cache_root,
            )
        }
    )

    entered = threading.Event()
    release = threading.Event()
    generated: list[str] = []

    def blocking_generate(source, target):
        generated.append(Path(source).name)
        if Path(source).name == first_source.name:
            entered.set()
            assert release.wait(timeout=5)
        Path(target).write_bytes(b"preview")

    monkeypatch.setattr(preview_module, "_generate_photo", blocking_generate)

    cache = MediaPreviewCache(workers=1, cache_manager=manager)
    try:
        assert cache.request(first) is True
        assert entered.wait(timeout=2)
        assert cache.request(second) is True
        assert cache.job_count == 2

        cache.reset()
        assert cache.job_count == 1

        release.set()
        deadline = time.time() + 3.0
        while time.time() < deadline and cache.job_count:
            qapp.processEvents()
            time.sleep(0.01)

        assert cache.job_count == 0
        assert generated == [first_source.name]
        assert not list(cache_root.glob("*.png"))
    finally:
        release.set()
        cache.close(timeout=2.0)
