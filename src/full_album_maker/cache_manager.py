"""M5 cache policy facade.

CacheManager centralizes namespace/version/root/invalidation policy while legacy
payload formats remain owned by their proven adapters.  Cache contents are
always disposable and never authoritative project data.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path
import shutil
from typing import Callable, Iterator, Mapping

from .paths import data_dir, temp_dir


RootFactory = Callable[[], Path]


@dataclass(frozen=True, slots=True)
class CacheNamespacePolicy:
    name: str
    version: int
    root_factory: RootFactory
    quota_bytes: int | None = None

    def root(self) -> Path:
        value = Path(self.root_factory())
        value.mkdir(parents=True, exist_ok=True)
        return value


def _default_policies() -> dict[str, CacheNamespacePolicy]:
    # Existing roots are intentionally preserved for namespaces that already
    # have production payloads. M5 changes ownership, not cache identity.
    return {
        "media-preview": CacheNamespacePolicy(
            "media-preview", 1, lambda: data_dir() / "cache" / "media-previews"
        ),
        "probe": CacheNamespacePolicy(
            "probe", 1, lambda: data_dir() / "cache" / "probe-v1"
        ),
        "accurate-preview": CacheNamespacePolicy(
            "accurate-preview", 1, lambda: temp_dir() / "accurate-preview-v1"
        ),
        "spectrum-preview": CacheNamespacePolicy(
            "spectrum-preview", 1, lambda: temp_dir() / "spectrum-preview-step08-v1"
        ),
        "template-thumbnail": CacheNamespacePolicy(
            "template-thumbnail", 1, lambda: data_dir() / "cache" / "template_thumbnails_v1"
        ),
        "beat-analysis": CacheNamespacePolicy(
            "beat-analysis", 1, lambda: data_dir() / "cache" / "beat-analysis-v1"
        ),
    }


class CacheManager:
    """Canonical M5 namespace/policy owner for disposable caches."""

    def __init__(
        self,
        policies: Mapping[str, CacheNamespacePolicy] | None = None,
    ) -> None:
        values = dict(policies or _default_policies())
        if not values:
            raise ValueError("CacheManager membutuhkan minimal satu namespace.")
        for name, policy in values.items():
            if name != policy.name:
                raise ValueError("Nama policy cache harus sama dengan key namespace.")
            if int(policy.version) <= 0:
                raise ValueError(f"Versi namespace cache tidak valid: {name}")
        self._policies = values

    @property
    def namespaces(self) -> tuple[str, ...]:
        return tuple(sorted(self._policies))

    def policy(self, namespace: str) -> CacheNamespacePolicy:
        key = str(namespace).strip()
        try:
            return self._policies[key]
        except KeyError as exc:
            raise KeyError(f"Namespace cache tidak dikenal: {key}") from exc

    def root(self, namespace: str) -> Path:
        return self.policy(namespace).root()

    def version(self, namespace: str) -> int:
        return int(self.policy(namespace).version)

    def quota_bytes(self, namespace: str) -> int | None:
        value = self.policy(namespace).quota_bytes
        return None if value is None else max(0, int(value))

    @staticmethod
    def entry_usable(path: str | Path) -> bool:
        """Corrupt/missing/zero-byte cache artifacts are cache misses."""

        candidate = Path(path)
        try:
            return candidate.is_file() and candidate.stat().st_size > 0
        except OSError:
            return False

    def evict(self, namespace: str, *paths: str | Path) -> int:
        """Delete cache artifacts only when they live under the namespace root."""

        root = self.root(namespace).resolve(strict=False)
        removed = 0
        for raw in paths:
            candidate = Path(raw)
            try:
                resolved = candidate.resolve(strict=False)
                if not resolved.is_relative_to(root):
                    continue
                candidate.unlink()
                removed += 1
            except FileNotFoundError:
                pass
            except OSError:
                pass
        return removed

    def clear(self, namespace: str) -> int:
        """Clear one disposable namespace without touching project/source data."""

        root = self.root(namespace)
        removed = 0
        for child in tuple(root.iterdir()):
            try:
                if child.is_dir():
                    shutil.rmtree(child)
                else:
                    child.unlink()
                removed += 1
            except OSError:
                pass
        return removed


DEFAULT_CACHE_MANAGER = CacheManager()

_CURRENT_CACHE_MANAGER: ContextVar[CacheManager | None] = ContextVar(
    "full_album_maker_current_cache_manager",
    default=None,
)


def current_cache_manager() -> CacheManager | None:
    return _CURRENT_CACHE_MANAGER.get()


@contextmanager
def bind_cache_manager(manager: CacheManager) -> Iterator[CacheManager]:
    if not isinstance(manager, CacheManager):
        raise TypeError("manager harus CacheManager.")
    token = _CURRENT_CACHE_MANAGER.set(manager)
    try:
        yield manager
    finally:
        _CURRENT_CACHE_MANAGER.reset(token)


__all__ = [
    "CacheManager",
    "CacheNamespacePolicy",
    "DEFAULT_CACHE_MANAGER",
    "bind_cache_manager",
    "current_cache_manager",
]
