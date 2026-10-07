from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
import threading
from typing import Callable

from PySide6.QtCore import QObject, Signal

from .editor_models import ProjectDocument
from .render_center_model_step10 import RenderJob, RenderSettings
from .render_engine import RenderEngine, current_render_engine
from .render_executor_step10 import Step10RenderCancelled
from .render_preflight_step10 import FFmpegCapability


class RenderAsyncBridge(QObject):
    preflight_ready = Signal(int, object, object)  # token, report, capability
    preflight_failed = Signal(int, str)
    render_started = Signal(str, str)
    metrics_ready = Signal(str, str, object)
    log_ready = Signal(str, str, str)
    render_finished = Signal(str, str, object)
    render_failed = Signal(str, str, str, str)  # job, attempt, code, message
    busy_changed = Signal(bool)

    def __init__(self, *, workers: int = 2, render_engine: RenderEngine | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._executor = ThreadPoolExecutor(max_workers=max(2, int(workers)), thread_name_prefix="fam-render-center")
        self._lock = threading.Lock()
        self._preflight_generation = 0
        self._active_attempt = ""
        self._cancel_event: threading.Event | None = None
        self._closed = False
        # During normal production startup AppKernel binds its single M4 engine
        # in a context while the legacy window is constructed. Tests/legacy
        # callers may still inject an engine explicitly.
        self._render_engine = render_engine or current_render_engine() or RenderEngine()

    @property
    def render_engine(self) -> RenderEngine:
        return self._render_engine

    @property
    def closed(self) -> bool:
        with self._lock:
            return bool(self._closed)

    def _emit_if_open(self, signal: Signal, *args) -> bool:
        with self._lock:
            if self._closed:
                return False
        signal.emit(*args)
        return True

    def _capability_for_settings(self, settings: RenderSettings) -> FFmpegCapability:
        # Compatibility helper retained for existing callers/tests. Policy now
        # belongs to RenderEngine rather than the Qt bridge.
        return self._render_engine.capability_for_settings(settings)

    def request_preflight(self, document: ProjectDocument, settings: RenderSettings) -> int:
        with self._lock:
            self._preflight_generation += 1
            token = self._preflight_generation
            if self._closed:
                return token
        snapshot = document.clone()
        try:
            self._executor.submit(self._run_preflight, token, snapshot, settings)
        except RuntimeError:
            # close() may win a race between the closed check and submit().
            # Treat it as an invalidated request rather than surfacing an
            # executor-shutdown exception into the Qt event loop.
            return token
        return token

    def invalidate_preflight(self) -> int:
        with self._lock:
            self._preflight_generation += 1
            return self._preflight_generation

    def _run_preflight(self, token: int, document: ProjectDocument, settings: RenderSettings) -> None:
        try:
            result = self._render_engine.preflight(document, settings)
            report = result.report
            capability = result.capability
        except Exception as exc:
            with self._lock:
                current = self._preflight_generation
            if token == current:
                self._emit_if_open(self.preflight_failed, token, str(exc))
            return
        with self._lock:
            current = self._preflight_generation
        if token == current:
            self._emit_if_open(self.preflight_ready, token, report, capability)

    def start(self, job: RenderJob) -> bool:
        with self._lock:
            if self._closed or self._active_attempt:
                return False
            self._active_attempt = job.attempt_id
            self._cancel_event = threading.Event()
            cancel_event = self._cancel_event
        self._emit_if_open(self.busy_changed, True)
        self._emit_if_open(self.render_started, job.job_id, job.attempt_id)
        try:
            self._executor.submit(self._run_job, job, cancel_event)
        except RuntimeError:
            # close() may have shut the executor down after the state claim.
            with self._lock:
                if self._active_attempt == job.attempt_id:
                    self._active_attempt = ""
                    self._cancel_event = None
            self._emit_if_open(self.busy_changed, False)
            return False
        return True

    def _run_job(self, job: RenderJob, cancel_event: threading.Event) -> None:
        try:
            # Capability is re-probed here even when the UI preflight already
            # passed. RenderExecutor then performs the critical snapshot/media/
            # disk/output preflight again immediately before start.
            result = self._render_engine.execute(
                job,
                cancel_event=cancel_event,
                on_metrics=lambda value: self._emit_if_open(
                    self.metrics_ready, job.job_id, job.attempt_id, value
                ),
                on_log=lambda line: self._emit_if_open(
                    self.log_ready, job.job_id, job.attempt_id, line
                ),
            )
        except Step10RenderCancelled as exc:
            self._emit_if_open(
                self.render_failed,
                job.job_id,
                job.attempt_id,
                "CANCELLED",
                str(exc),
            )
        except Exception as exc:
            self._emit_if_open(
                self.render_failed,
                job.job_id,
                job.attempt_id,
                job.error_code or "RENDER_FAILED",
                job.error_message or str(exc),
            )
        else:
            self._emit_if_open(
                self.render_finished, job.job_id, job.attempt_id, result
            )
        finally:
            with self._lock:
                if self._active_attempt == job.attempt_id:
                    self._active_attempt = ""
                    self._cancel_event = None
            self._emit_if_open(self.busy_changed, False)

    def cancel(self) -> bool:
        with self._lock:
            if self._closed:
                return False
            event = self._cancel_event
        if event is None:
            return False
        event.set()
        return True

    @property
    def busy(self) -> bool:
        with self._lock:
            return bool(self._active_attempt) and not self._closed

    def close(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._preflight_generation += 1
            event = self._cancel_event
            self._active_attempt = ""
            self._cancel_event = None
        if event is not None:
            event.set()
        self._executor.shutdown(wait=False, cancel_futures=True)
