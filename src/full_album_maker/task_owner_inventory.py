"""Characterization inventory of pre-M2 async/task owners.

The inventory is evidence only. M2 does not reroute these owners yet.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LegacyTaskOwner:
    owner_id: str
    path: str
    primitive: str
    stale_guard: str
    shutdown: str
    migration_note: str


LEGACY_TASK_OWNERS: tuple[LegacyTaskOwner, ...] = (
    LegacyTaskOwner(
        "async-import",
        "src/full_album_maker/async_import.py",
        "daemon threading.Thread per import batch",
        "captures project_ref and ignores completion after project switch or accepted window close",
        "accepted window close suppresses delivery; daemon worker winds down independently without retaining the window",
        "TaskScope migration remains optional after the v2.0.1 close-safety guard",
    ),
    LegacyTaskOwner(
        "editor-preview-render",
        "src/full_album_maker/editor_workspace.py",
        "daemon threading.Thread for accurate preview/render helpers",
        "workspace busy flags / current document behavior",
        "no central ownership",
        "do not migrate until preview/render facades are ready",
    ),
    LegacyTaskOwner(
        "media-preview-cache",
        "src/full_album_maker/media_preview_cache.py",
        "bounded daemon thread queue",
        "generation token suppresses stale preview result",
        "no explicit close method in baseline owner",
        "migrate with M5 preview/cache boundary",
    ),
    LegacyTaskOwner(
        "spectrum-preview",
        "src/full_album_maker/spectrum_preview_step08.py",
        "ThreadPoolExecutor",
        "generation token",
        "executor shutdown(wait=False, cancel_futures=True)",
        "migrate only with Spectrum/preview parity evidence",
    ),
    LegacyTaskOwner(
        "template-thumbnail",
        "src/full_album_maker/template_thumbnail_cache_step07.py",
        "ThreadPoolExecutor",
        "cache-key pending map; immutable document snapshot",
        "wait_for_idle + executor shutdown(wait=False, cancel_futures=True)",
        "migrate with cache/preview lifecycle work",
    ),
    LegacyTaskOwner(
        "ai-provider",
        "src/full_album_maker/ai_async_step09.py",
        "ThreadPoolExecutor",
        "generation token + owner-thread queued delivery",
        "cancel_current + wait_for_idle + close",
        "preserve STEP09 stale guard until AI task routing is separately proven",
    ),
    LegacyTaskOwner(
        "render-center",
        "src/full_album_maker/render_async_step10.py",
        "ThreadPoolExecutor + threading.Event",
        "preflight generation + active attempt identity",
        "cancel + invalidate_preflight + executor close",
        "do not migrate process ownership before ProcessSupervisor/RenderEngine gates",
    ),
)


OWNER_IDS = frozenset(owner.owner_id for owner in LEGACY_TASK_OWNERS)


__all__ = ["LEGACY_TASK_OWNERS", "OWNER_IDS", "LegacyTaskOwner"]
