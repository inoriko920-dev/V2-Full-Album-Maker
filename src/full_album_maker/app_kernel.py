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

    M2 wires TaskSupervisor ownership, M3 ProjectPersistence, and M4 the
    RenderEngine facade. Legacy implementations remain adapters until their
    individual parity gates permit retirement.
    """

    runtime: LegacyRuntimeAdapter
    feature_parity: FeatureParityRegistry
    tasks: TaskSupervisor
    persistence: ProjectPersistence
    render_engine: RenderEngine
    shutdown_timeout_seconds: float = 1.0

    def close(self) -> ShutdownReport:
        return self.tasks.close(timeout=self.shutdown_timeout_seconds)

    def run(self, argv: Sequence[str] = ()) -> int:
        args = tuple(str(arg) for arg in argv)
        try:
            if "--portable-smoke" in args:
                return self.runtime.run_portable_smoke()
            # M4 exposes the AppKernel-owned RenderEngine only while the legacy
            # production window is constructed/run. RenderAsyncBridge captures
            # this exact instance, avoiding a second render orchestration owner.
            with bind_render_engine(self.render_engine):
                return self.runtime.run_gui()
        finally:
            # The kernel owns its central task boundary. Existing legacy workers
            # are still closed by their current owners until migrated in later
            # M2 follow-up slices / approved service migrations.
            self.close()


class CompositionRoot:
    """Single M1 launch-time wiring location for V2.

    M1 bound the proven runtime entrypoints. M2 added TaskSupervisor, M3 added
    ProjectPersistence, and M4 adds the RenderEngine facade while preserving the
    proven STEP10 executor/compiler implementation. Later boundaries such as
    PreviewEngine/CacheManager and WorkspaceRegistry remain deferred.
    """

    def __init__(
        self,
        *,
        gui_runner: Runner,
        portable_smoke_runner: Runner | None = None,
        feature_parity: FeatureParityRegistry = DEFAULT_FEATURE_PARITY_REGISTRY,
        task_supervisor: TaskSupervisor | None = None,
        project_persistence: ProjectPersistence = DEFAULT_PROJECT_PERSISTENCE,
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
        return AppKernel(
            runtime=runtime,
            feature_parity=self._feature_parity,
            tasks=tasks,
            persistence=self._project_persistence,
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
        render_engine=render_engine,
        task_workers=task_workers,
        shutdown_timeout_seconds=shutdown_timeout_seconds,
    ).build()


__all__ = [
    "AppKernel",
    "CompositionRoot",
    "LegacyRuntimeAdapter",
    "ProjectPersistence",
    "RenderEngine",
    "Runner",
    "ShutdownReport",
    "TaskSupervisor",
    "build_app_kernel",
]
