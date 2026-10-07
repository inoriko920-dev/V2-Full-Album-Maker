"""M4 RenderEngine facade around the proven STEP10 render pipeline.

The facade is deliberately additive.  It owns orchestration policy and delegates
actual compilation/process/verification/publication to the already-proven
STEP10 implementation.  M4 does not replace the Step08 -> V13 -> S11 ->
FFmpegV2 compiler chain and does not introduce a new process owner.
"""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
import threading
from typing import Callable, Iterator

from .editor_models import ProjectDocument
from .render_center_model_step10 import RenderJob, RenderSettings
from .render_executor_step10 import (
    ExecutionResult,
    LogCallback,
    MetricCallback,
    RenderExecutor,
    Step10RenderError,
)
from .render_preflight_step10 import (
    FFmpegCapability,
    PreflightReport,
    hardware_encoder,
    probe_ffmpeg,
    run_preflight,
    verify_encoder_runtime,
)


@dataclass(frozen=True, slots=True)
class RenderPreflightResult:
    """UI-preflight evidence produced through the canonical render facade."""

    report: PreflightReport
    capability: FFmpegCapability


CapabilityFactory = Callable[[RenderSettings], FFmpegCapability]
ExecutorFactory = Callable[[FFmpegCapability], RenderExecutor]
PreflightRunner = Callable[..., PreflightReport]


def _default_capability_for_settings(settings: RenderSettings) -> FFmpegCapability:
    """Preserve STEP10 capability and AUTO hardware-fallback semantics."""

    capability = probe_ffmpeg()
    if settings.hardware_mode == "software":
        return capability
    try:
        candidate = hardware_encoder(settings.video_codec)
    except Exception:
        return capability
    if candidate in capability.encoders:
        capability = verify_encoder_runtime(capability, candidate)
    return capability


def _default_executor_factory(capability: FFmpegCapability) -> RenderExecutor:
    return RenderExecutor(capability)


class RenderEngine:
    """Canonical M4 facade for preflight and final render execution.

    The current STEP10 executor remains the implementation adapter.  The facade
    adds one stable application-service boundary and one active-attempt guard;
    it intentionally does not replace FFmpeg process lifecycle ownership.
    """

    def __init__(
        self,
        *,
        capability_factory: CapabilityFactory = _default_capability_for_settings,
        executor_factory: ExecutorFactory = _default_executor_factory,
        preflight_runner: PreflightRunner = run_preflight,
    ) -> None:
        if not callable(capability_factory):
            raise TypeError("capability_factory harus callable.")
        if not callable(executor_factory):
            raise TypeError("executor_factory harus callable.")
        if not callable(preflight_runner):
            raise TypeError("preflight_runner harus callable.")
        self._capability_factory = capability_factory
        self._executor_factory = executor_factory
        self._preflight_runner = preflight_runner
        self._lock = threading.Lock()
        self._active_attempt = ""

    def capability_for_settings(self, settings: RenderSettings) -> FFmpegCapability:
        settings.validate()
        capability = self._capability_factory(settings)
        if not isinstance(capability, FFmpegCapability):
            raise TypeError("capability_factory harus menghasilkan FFmpegCapability.")
        return capability

    def preflight(
        self,
        document: ProjectDocument,
        settings: RenderSettings,
    ) -> RenderPreflightResult:
        """Run the existing STEP10 preflight against an immutable caller clone."""

        snapshot = document.clone()
        snapshot.validate()
        capability = self.capability_for_settings(settings)
        report = self._preflight_runner(
            snapshot,
            settings,
            capability=capability,
        )
        return RenderPreflightResult(report=report, capability=capability)

    def _claim(self, attempt_id: str) -> None:
        with self._lock:
            if self._active_attempt:
                raise Step10RenderError(
                    "RenderEngine sedang menjalankan attempt lain; double-start ditolak."
                )
            self._active_attempt = str(attempt_id)

    def _release(self, attempt_id: str) -> None:
        with self._lock:
            if self._active_attempt == str(attempt_id):
                self._active_attempt = ""

    @property
    def busy(self) -> bool:
        with self._lock:
            return bool(self._active_attempt)

    def execute(
        self,
        job: RenderJob,
        *,
        cancel_event: threading.Event | None = None,
        on_metrics: MetricCallback | None = None,
        on_log: LogCallback | None = None,
    ) -> ExecutionResult:
        """Delegate one attempt to the proven STEP10 executor.

        RenderExecutor still owns critical re-preflight, the current compiler
        chain, FFmpeg progress/cancel behavior, ffprobe verification, and
        transactional publication.  M4 only makes that path explicit.
        """

        self._claim(job.attempt_id)
        try:
            capability = self.capability_for_settings(job.settings)
            executor = self._executor_factory(capability)
            return executor.execute(
                job,
                cancel_event=cancel_event,
                on_metrics=on_metrics,
                on_log=on_log,
            )
        finally:
            self._release(job.attempt_id)


_CURRENT_RENDER_ENGINE: ContextVar[RenderEngine | None] = ContextVar(
    "full_album_maker_current_render_engine",
    default=None,
)


def current_render_engine() -> RenderEngine | None:
    """Return the AppKernel-bound engine during legacy window construction."""

    return _CURRENT_RENDER_ENGINE.get()


@contextmanager
def bind_render_engine(engine: RenderEngine) -> Iterator[RenderEngine]:
    """Temporarily expose the AppKernel engine to legacy construction.

    This is a migration bridge, not a second owner.  RenderAsyncBridge captures
    the engine while the production window is constructed; the context is reset
    immediately after the runner returns.
    """

    if not isinstance(engine, RenderEngine):
        raise TypeError("engine harus RenderEngine.")
    token = _CURRENT_RENDER_ENGINE.set(engine)
    try:
        yield engine
    finally:
        _CURRENT_RENDER_ENGINE.reset(token)


__all__ = [
    "CapabilityFactory",
    "ExecutorFactory",
    "PreflightRunner",
    "RenderEngine",
    "RenderPreflightResult",
    "bind_render_engine",
    "current_render_engine",
]
