"""V2 application composition boundary introduced in migration M1.

M1 is deliberately additive: existing production implementations remain the
owners of project state, UI, lifecycle, persistence, render, preview, AI, and
workspace behavior.  The kernel only centralizes launch-time dependency wiring
so later migration slices can replace one adapter at a time without creating a
second application or a second authoritative project state.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Sequence

from .feature_parity_registry import (
    DEFAULT_FEATURE_PARITY_REGISTRY,
    FeatureParityRegistry,
)
from .task_lifecycle import ShutdownReport, TaskSupervisor
from .project_persistence import DEFAULT_PROJECT_PERSISTENCE, ProjectPersistence
from .cache_manager import CacheManager, bind_cache_manager
from .media_probe_service import MediaProbeService, bind_media_probe_service
from .preview_engine import PreviewEngine, bind_preview_engine
from .beat_analysis import BeatAnalysisService, bind_beat_analysis_service
from .render_engine import RenderEngine, bind_render_engine


Runner = Callable[[], int]


def _lazy_portable_smoke_runner() -> int:
    # Deliberately lazy: normal application startup must not import release-only
    # smoke dependencies unless the explicit portable smoke flag is requested.
    from .release_smoke import run_portable_smoke

    return int(run_portable_smoke())


@dataclass(frozen=True, slots=True)
class LegacyRuntimeAdapter:
    """Adapter around the currently proven production entrypoints.

    M1 does not replace either entrypoint.  The adapter only gives the kernel a
    stable boundary that later slices may wrap or replace after parity evidence.
    """

    gui_runner: Runner
    portable_smoke_runner: Runner

    def run_gui(self) -> int:
        return int(self.gui_runner())

    def run_portable_smoke(self) -> int:
        return int(self.portable_smoke_runner())


@dataclass(frozen=True, slots=True)
class AppKernel:
    """Application kernel with one central task-lifecycle owner.

    M2 wires TaskSupervisor ownership, M3 ProjectPersistence, M4 RenderEngine,
    M5 the probe/preview/cache service facades, and M6 BeatAnalysisService.
    Legacy implementations remain adapters until their individual parity gates
    permit retirement.
    """

    runtime: LegacyRuntimeAdapter
    feature_parity: FeatureParityRegistry
    tasks: TaskSupervisor
    persistence: ProjectPersistence
    media_probe_service: MediaProbeService
    cache_manager: CacheManager
    preview_engine: PreviewEngine
    beat_analysis_service: BeatAnalysisService
    render_engine: RenderEngine
    shutdown_timeout_seconds: float = 1.0

    def close(self) -> ShutdownReport:
        return self.tasks.close(timeout=self.shutdown_timeout_seconds)

    def run(self, argv: Sequence[str] = ()) -> int:
        args = tuple(str(arg) for arg in argv)
        try:
            if "--portable-smoke" in args:
                return self.runtime.run_portable_smoke()
            # M4–M6 expose kernel-owned services only while the legacy runtime
            # is active. Legacy constructors capture these exact instances
            # before their worker threads start, avoiding a second owner.
            with (
                bind_render_engine(self.render_engine),
                bind_media_probe_service(self.media_probe_service),
                bind_cache_manager(self.cache_manager),
                bind_preview_engine(self.preview_engine),
                bind_beat_analysis_service(self.beat_analysis_service),
            ):
                return self.runtime.run_gui()
        finally:
            # The kernel owns its central task boundary. Existing legacy workers
            # are still closed by their current owners until migrated in later
            # M2 follow-up slices / approved service migrations.
            self.close()


class CompositionRoot:
    """Single M1 launch-time wiring location for V2.

    M1 bound the proven runtime entrypoints. M2 added TaskSupervisor, M3 added
    ProjectPersistence, M4 added RenderEngine, M5 added MediaProbeService,
    CacheManager, and PreviewEngine, and M6 adds BeatAnalysisService while
    preserving the proven Spectrum/render paths. WorkspaceRegistry and later
    migration boundaries remain deferred.
    """

    def __init__(
        self,
        *,
        gui_runner: Runner,
        portable_smoke_runner: Runner | None = None,
        feature_parity: FeatureParityRegistry = DEFAULT_FEATURE_PARITY_REGISTRY,
        task_supervisor: TaskSupervisor | None = None,
        project_persistence: ProjectPersistence = DEFAULT_PROJECT_PERSISTENCE,
        media_probe_service: MediaProbeService | None = None,
        cache_manager: CacheManager | None = None,
        preview_engine: PreviewEngine | None = None,
        beat_analysis_service: BeatAnalysisService | None = None,
        render_engine: RenderEngine | None = None,
        task_workers: int = 4,
        shutdown_timeout_seconds: float = 1.0,
    ) -> None:
        if not callable(gui_runner):
            raise TypeError("gui_runner harus callable.")
        if portable_smoke_runner is not None and not callable(portable_smoke_runner):
            raise TypeError("portable_smoke_runner harus callable.")
        self._gui_runner = gui_runner
        self._portable_smoke_runner = portable_smoke_runner or _lazy_portable_smoke_runner
        if float(shutdown_timeout_seconds) < 0:
            raise ValueError("shutdown_timeout_seconds harus >= 0.")
        self._feature_parity = feature_parity
        self._task_supervisor = task_supervisor
        self._project_persistence = project_persistence
        self._media_probe_service = media_probe_service
        self._cache_manager = cache_manager
        self._preview_engine = preview_engine
        self._beat_analysis_service = beat_analysis_service
        self._render_engine = render_engine
        self._task_workers = int(task_workers)
        self._shutdown_timeout_seconds = float(shutdown_timeout_seconds)

    def build(self) -> AppKernel:
        # M0/T1 is a hard invariant for every later migration slice.
        self._feature_parity.assert_valid()
        runtime = LegacyRuntimeAdapter(
            gui_runner=self._gui_runner,
            portable_smoke_runner=self._portable_smoke_runner,
        )
        tasks = self._task_supervisor or TaskSupervisor(max_workers=self._task_workers)
        if self._cache_manager is not None:
            cache_manager = self._cache_manager
        elif self._preview_engine is not None:
            cache_manager = self._preview_engine.cache_manager
        else:
            cache_manager = CacheManager()
        preview_engine = self._preview_engine or PreviewEngine(cache_manager=cache_manager)
        if preview_engine.cache_manager is not cache_manager:
            raise ValueError("PreviewEngine harus memakai CacheManager milik AppKernel.")
        beat_analysis_service = self._beat_analysis_service or BeatAnalysisService(
            cache_manager=cache_manager,
            task_supervisor=tasks,
        )
        if beat_analysis_service.cache_manager is not cache_manager:
            raise ValueError("BeatAnalysisService harus memakai CacheManager milik AppKernel.")
        if beat_analysis_service.task_supervisor is not tasks:
            raise ValueError("BeatAnalysisService harus memakai TaskSupervisor milik AppKernel.")
        return AppKernel(
            runtime=runtime,
            feature_parity=self._feature_parity,
            tasks=tasks,
            persistence=self._project_persistence,
            media_probe_service=self._media_probe_service or MediaProbeService(),
            cache_manager=cache_manager,
            preview_engine=preview_engine,
            beat_analysis_service=beat_analysis_service,
            render_engine=self._render_engine or RenderEngine(),
            shutdown_timeout_seconds=self._shutdown_timeout_seconds,
        )


def build_app_kernel(
    *,
    gui_runner: Runner,
    portable_smoke_runner: Runner | None = None,
    feature_parity: FeatureParityRegistry = DEFAULT_FEATURE_PARITY_REGISTRY,
    task_supervisor: TaskSupervisor | None = None,
    project_persistence: ProjectPersistence = DEFAULT_PROJECT_PERSISTENCE,
    media_probe_service: MediaProbeService | None = None,
    cache_manager: CacheManager | None = None,
    preview_engine: PreviewEngine | None = None,
    beat_analysis_service: BeatAnalysisService | None = None,
    render_engine: RenderEngine | None = None,
    task_workers: int = 4,
    shutdown_timeout_seconds: float = 1.0,
) -> AppKernel:
    """Convenience factory used by the production entrypoint and tests."""

    return CompositionRoot(
        gui_runner=gui_runner,
        portable_smoke_runner=portable_smoke_runner,
        feature_parity=feature_parity,
        task_supervisor=task_supervisor,
        project_persistence=project_persistence,
        media_probe_service=media_probe_service,
        cache_manager=cache_manager,
        preview_engine=preview_engine,
        beat_analysis_service=beat_analysis_service,
        render_engine=render_engine,
        task_workers=task_workers,
        shutdown_timeout_seconds=shutdown_timeout_seconds,
    ).build()


__all__ = [
    "AppKernel",
    "BeatAnalysisService",
    "CacheManager",
    "CompositionRoot",
    "LegacyRuntimeAdapter",
    "MediaProbeService",
    "PreviewEngine",
    "ProjectPersistence",
    "RenderEngine",
    "Runner",
    "ShutdownReport",
    "TaskSupervisor",
    "build_app_kernel",
]
