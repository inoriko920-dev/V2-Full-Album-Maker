"""M5 PreviewEngine facade around proven AccuratePreview/media-preview behavior."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from pathlib import Path
from typing import Callable, Iterator, Protocol

from .cache_manager import CacheManager, DEFAULT_CACHE_MANAGER
from .editor_models import ProjectDocument


class AccuratePreviewAdapter(Protocol):
    def render_frame(
        self,
        document: ProjectDocument,
        time_tick: int,
        destination: str | Path,
    ) -> str: ...


AccuratePreviewFactory = Callable[[], AccuratePreviewAdapter]


def _default_accurate_factory() -> AccuratePreviewAdapter:
    from .preview_service import AccuratePreviewService

    return AccuratePreviewService()


class PreviewEngine:
    """Canonical M5 preview facade.

    Accurate Preview still delegates to the existing Step08 compiler path.
    Library-preview generation still delegates to the existing cache adapter.
    M5 changes service ownership without changing composition semantics.
    """

    def __init__(
        self,
        *,
        cache_manager: CacheManager = DEFAULT_CACHE_MANAGER,
        accurate_factory: AccuratePreviewFactory = _default_accurate_factory,
    ) -> None:
        if not isinstance(cache_manager, CacheManager):
            raise TypeError("cache_manager harus CacheManager.")
        if not callable(accurate_factory):
            raise TypeError("accurate_factory harus callable.")
        self.cache_manager = cache_manager
        self._accurate_factory = accurate_factory

    def render_frame(
        self,
        document: ProjectDocument,
        time_tick: int,
        destination: str | Path,
    ) -> str:
        snapshot = document.clone()
        snapshot.validate()
        service = self._accurate_factory()
        return str(service.render_frame(snapshot, max(0, int(time_tick)), destination))

    def media_preview_path(self, asset) -> Path:
        from .media_preview_cache import preview_cache_path

        return preview_cache_path(asset, cache_manager=self.cache_manager)

    def generate_media_preview(self, asset) -> str:
        from .media_preview_cache import generate_preview

        return str(generate_preview(asset, cache_manager=self.cache_manager))

    def invalidate_media_source(self, path: str | Path) -> int:
        from .media_preview_cache import invalidate_source

        return int(invalidate_source(path, cache_manager=self.cache_manager))

    def new_media_preview_cache(self, parent=None, *, workers: int = 2):
        from .media_preview_cache import MediaPreviewCache

        return MediaPreviewCache(
            parent,
            workers=workers,
            cache_manager=self.cache_manager,
        )

    def cache_root(self, namespace: str) -> Path:
        return self.cache_manager.root(namespace)


DEFAULT_PREVIEW_ENGINE = PreviewEngine()

_CURRENT_PREVIEW_ENGINE: ContextVar[PreviewEngine | None] = ContextVar(
    "full_album_maker_current_preview_engine",
    default=None,
)


def current_preview_engine() -> PreviewEngine | None:
    return _CURRENT_PREVIEW_ENGINE.get()


@contextmanager
def bind_preview_engine(engine: PreviewEngine) -> Iterator[PreviewEngine]:
    if not isinstance(engine, PreviewEngine):
        raise TypeError("engine harus PreviewEngine.")
    token = _CURRENT_PREVIEW_ENGINE.set(engine)
    try:
        yield engine
    finally:
        _CURRENT_PREVIEW_ENGINE.reset(token)


__all__ = [
    "AccuratePreviewAdapter",
    "AccuratePreviewFactory",
    "DEFAULT_PREVIEW_ENGINE",
    "PreviewEngine",
    "bind_preview_engine",
    "current_preview_engine",
]
