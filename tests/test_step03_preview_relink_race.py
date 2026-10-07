from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from full_album_maker import media_completion
from full_album_maker.media_library_model import (
    MediaAsset,
    MediaMetadata,
    MediaType,
    stable_asset_id,
)
from full_album_maker.media_preview_cache import PreviewResult


def _asset(path: Path) -> MediaAsset:
    return MediaAsset(
        asset_id=stable_asset_id(str(path), MediaType.PHOTO),
        path=str(path),
        display_name=path.name,
        media_type=MediaType.PHOTO,
        metadata=MediaMetadata(width=100, height=100),
    )


def test_preview_result_with_stale_source_identity_is_ignored(tmp_path: Path) -> None:
    source = tmp_path / "same-path.png"
    source.write_bytes(b"current-source")
    asset = _asset(source)

    calls: list[PreviewResult] = []
    inspector_calls: list[tuple[str, str]] = []
    expected = tmp_path / "current-token.png"

    fake = SimpleNamespace(
        _s03_preview_cache=SimpleNamespace(generation=4),
        _s03_index=SimpleNamespace(get=lambda asset_id: asset if asset_id == asset.asset_id else None),
        _m5_preview_engine=SimpleNamespace(media_preview_path=lambda current: expected),
        media_workspace=SimpleNamespace(
            _step03_preview_result=lambda result: calls.append(result)
        ),
        media_inspector=SimpleNamespace(
            set_preview_path=lambda asset_id, path: inspector_calls.append((asset_id, path))
        ),
    )

    media_completion._preview_ready(
        fake,
        PreviewResult(
            asset_id=asset.asset_id,
            path=str(tmp_path / "old-token.png"),
            generation=4,
            source_key=str(source.resolve()),
            source_fingerprint="old-token",
        ),
    )

    assert calls == []
    assert inspector_calls == []


def test_relink_invalidates_generation_before_old_cache_and_project_refresh(
    tmp_path: Path,
    qapp,
) -> None:
    events: list[str] = []

    class Cache:
        def reset(self):
            events.append("reset")

    class Engine:
        def invalidate_media_source(self, path):
            events.append("invalidate")
            return 0

    class Preview:
        def clear(self):
            events.append("inspector-clear")

    workspace = SimpleNamespace(
        _step03_preview_paths={"old": "preview.png"},
        _step03_preview_failed={"old"},
        _step03_request_nearby=lambda: events.append("request"),
    )
    fake = SimpleNamespace(
        _s03_preview_cache=Cache(),
        _m5_preview_engine=Engine(),
        media_workspace=workspace,
        media_inspector=SimpleNamespace(preview=Preview()),
    )

    previous = media_completion._originals.get("relinked")
    media_completion._originals["relinked"] = (
        lambda self, payload: events.append("original")
    )
    try:
        media_completion._relinked(
            fake,
            {"old": str(tmp_path / "old-source.mp4")},
        )
        qapp.processEvents()
    finally:
        if previous is None:
            media_completion._originals.pop("relinked", None)
        else:
            media_completion._originals["relinked"] = previous

    assert events[:4] == [
        "reset",
        "inspector-clear",
        "invalidate",
        "original",
    ]
    assert workspace._step03_preview_paths == {}
    assert workspace._step03_preview_failed == set()
