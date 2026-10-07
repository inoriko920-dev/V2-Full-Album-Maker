"""Central task lifecycle primitives for V2 migration M2.

This module intentionally owns only Python task identity/cancellation/scope
lifecycle. It does NOT own subprocesses (ProcessSupervisor is later), Qt, project
state, persistence, rendering, previews, workspaces, or AI provider behavior.
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor, wait
from dataclasses import dataclass
from threading import Event, Lock
from time import monotonic
from typing import Callable, Generic, TypeVar
from uuid import uuid4

from .app_errors import (
    LifecycleClosedError,
    StaleResultError,
    TaskCancelledError,
)


T = TypeVar("T")
TaskWorker = Callable[["TaskToken"], T]


class _CancellationState:
    def __init__(self) -> None:
        self._event = Event()
        self._lock = Lock()
        self._reason = ""

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    @property
    def reason(self) -> str:
        with self._lock:
            return self._reason

    def cancel(self, reason: str) -> None:
        with self._lock:
            if not self._event.is_set():
                self._reason = str(reason or "Task dibatalkan.")
                self._event.set()


@dataclass(frozen=True, slots=True)
class TaskToken:
    """Immutable identity plus cooperative cancellation state."""

    scope_id: str
    scope_name: str
    generation: int
    task_id: str
    task_name: str
    _state: _CancellationState

    @property
    def cancelled(self) -> bool:
        return self._state.cancelled

    @property
    def cancel_reason(self) -> str:
        return self._state.reason

    def wait_cancelled(self, timeout: float | None = None) -> bool:
        return self._state._event.wait(timeout)

    def raise_if_cancelled(self) -> None:
        if self.cancelled:
            raise TaskCancelledError(self.cancel_reason or "Task dibatalkan.")


@dataclass(frozen=True, slots=True)
class TaskScopeSnapshot:
    scope_id: str
    name: str
    generation: int
    closed: bool
    active_tokens: int


class TaskScope:
    """Generation-scoped task identity used to reject stale completions."""

    def __init__(self, name: str) -> None:
        normalized = str(name).strip()
        if not normalized:
            raise ValueError("Nama TaskScope tidak boleh kosong.")
        self._name = normalized
        self._scope_id = uuid4().hex
        self._generation = 0
        self._closed = False
        self._tokens: dict[str, TaskToken] = {}
        self._lock = Lock()

    @property
    def name(self) -> str:
        return self._name

    @property
    def scope_id(self) -> str:
        return self._scope_id

    @property
    def generation(self) -> int:
        with self._lock:
            return self._generation

    @property
    def closed(self) -> bool:
        with self._lock:
            return self._closed

    def snapshot(self) -> TaskScopeSnapshot:
        with self._lock:
            return TaskScopeSnapshot(
                scope_id=self._scope_id,
                name=self._name,
                generation=self._generation,
                closed=self._closed,
                active_tokens=len(self._tokens),
            )

    def issue_token(self, task_name: str = "") -> TaskToken:
        with self._lock:
            if self._closed:
                raise LifecycleClosedError(f"TaskScope '{self._name}' sudah ditutup.")
            token = TaskToken(
                scope_id=self._scope_id,
                scope_name=self._name,
                generation=self._generation,
                task_id=uuid4().hex,
                task_name=str(task_name or ""),
                _state=_CancellationState(),
            )
            self._tokens[token.task_id] = token
            return token

    def is_current(self, token: TaskToken) -> bool:
        with self._lock:
            return (
                not self._closed
                and token.scope_id == self._scope_id
                and token.generation == self._generation
                and not token.cancelled
            )

    def invalidate(self, reason: str = "TaskScope diinvalidasi.") -> int:
        with self._lock:
            if self._closed:
                return self._generation
            self._generation += 1
            tokens = tuple(self._tokens.values())
        for token in tokens:
            token._state.cancel(reason)
        return self.generation

    def cancel_all(self, reason: str = "TaskScope dibatalkan.") -> int:
        with self._lock:
            tokens = tuple(self._tokens.values())
        for token in tokens:
            token._state.cancel(reason)
        return len(tokens)

    def close(self, reason: str = "TaskScope ditutup.") -> None:
        with self._lock:
            if self._closed:
                return
            self._closed = True
            self._generation += 1
            tokens = tuple(self._tokens.values())
        for token in tokens:
            token._state.cancel(reason)

    def _release(self, token: TaskToken) -> None:
        with self._lock:
            self._tokens.pop(token.task_id, None)


@dataclass(frozen=True, slots=True)
class ShutdownReport:
    submitted: int
    completed: int
    unfinished: int
    timed_out: bool
    elapsed_seconds: float


@dataclass(frozen=True, slots=True)
class TaskHandle(Generic[T]):
    """Future wrapper that forces consumers to distinguish stale/current result."""

    token: TaskToken
    scope: TaskScope
    future: Future[T]

    @property
    def done(self) -> bool:
        return self.future.done()

    def cancel(self, reason: str = "Task dibatalkan.") -> bool:
        self.token._state.cancel(reason)
        return self.future.cancel()

    def result(self, timeout: float | None = None) -> T:
        return self.future.result(timeout=timeout)

    def result_if_current(self, timeout: float | None = None) -> T:
        value = self.future.result(timeout=timeout)
        if not self.scope.is_current(self.token):
            raise StaleResultError(
                f"Hasil task '{self.token.task_name or self.token.task_id}' sudah stale."
            )
        return value


class TaskSupervisor:
    """Owns bounded Python worker execution and lifecycle scopes.

    Workers must cooperate by checking TaskToken. This supervisor cannot kill a
    running Python thread. Close is therefore bounded and reports unfinished
    workers instead of blocking forever. Process termination is deliberately left
    to the later ProcessSupervisor boundary.
    """

    def __init__(self, *, max_workers: int = 4, thread_name_prefix: str = "fam-task") -> None:
        workers = int(max_workers)
        if workers < 1:
            raise ValueError("max_workers harus >= 1.")
        self._executor = ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix=str(thread_name_prefix or "fam-task"),
        )
        self._lock = Lock()
        self._scopes: dict[str, TaskScope] = {}
        self._futures: set[Future] = set()
        self._submitted = 0
        self._closed = False

    @property
    def closed(self) -> bool:
        with self._lock:
            return self._closed

    @property
    def pending_count(self) -> int:
        with self._lock:
            return sum(1 for future in self._futures if not future.done())

    def create_scope(self, name: str) -> TaskScope:
        normalized = str(name).strip()
        if not normalized:
            raise ValueError("Nama TaskScope tidak boleh kosong.")
        with self._lock:
            if self._closed:
                raise LifecycleClosedError("TaskSupervisor sudah ditutup.")
            existing = self._scopes.get(normalized)
            if existing is not None and not existing.closed:
                raise ValueError(f"TaskScope '{normalized}' sudah ada.")
            scope = TaskScope(normalized)
            self._scopes[normalized] = scope
            return scope

    def get_or_create_scope(self, name: str) -> TaskScope:
        normalized = str(name).strip()
        if not normalized:
            raise ValueError("Nama TaskScope tidak boleh kosong.")
        with self._lock:
            if self._closed:
                raise LifecycleClosedError("TaskSupervisor sudah ditutup.")
            scope = self._scopes.get(normalized)
            if scope is not None and not scope.closed:
                return scope
            scope = TaskScope(normalized)
            self._scopes[normalized] = scope
            return scope

    def scope(self, name: str) -> TaskScope:
        with self._lock:
            scope = self._scopes.get(str(name))
        if scope is None:
            raise KeyError(name)
        return scope

    def submit(
        self,
        scope: TaskScope,
        worker: TaskWorker[T],
        *,
        task_name: str = "",
    ) -> TaskHandle[T]:
        if not callable(worker):
            raise TypeError("worker harus callable.")
        with self._lock:
            if self._closed:
                raise LifecycleClosedError("TaskSupervisor sudah ditutup.")
            owned = self._scopes.get(scope.name)
            if owned is not scope:
                raise ValueError("TaskScope bukan milik TaskSupervisor ini.")
            token = scope.issue_token(task_name)

            def run() -> T:
                token.raise_if_cancelled()
                value = worker(token)
                token.raise_if_cancelled()
                return value

            future: Future[T] = self._executor.submit(run)
            self._futures.add(future)
            self._submitted += 1

        def finished(done: Future[T]) -> None:
            scope._release(token)
            with self._lock:
                self._futures.discard(done)

        future.add_done_callback(finished)
        return TaskHandle(token=token, scope=scope, future=future)

    def invalidate_scope(self, name: str, reason: str = "Project/context berganti.") -> int:
        return self.scope(name).invalidate(reason)

    def close_scope(self, name: str, reason: str = "TaskScope ditutup.") -> None:
        scope = self.scope(name)
        scope.close(reason)

    def wait_for_idle(self, timeout: float = 0.0) -> bool:
        with self._lock:
            futures = tuple(self._futures)
        if not futures:
            return True
        _done, not_done = wait(futures, timeout=max(0.0, float(timeout)))
        return not not_done

    def close(self, *, timeout: float = 1.0) -> ShutdownReport:
        started = monotonic()
        with self._lock:
            if self._closed:
                futures = tuple(self._futures)
                submitted = self._submitted
            else:
                self._closed = True
                futures = tuple(self._futures)
                submitted = self._submitted
                scopes = tuple(self._scopes.values())
                for scope in scopes:
                    scope.close("Application/task supervisor ditutup.")

        if futures:
            done, not_done = wait(futures, timeout=max(0.0, float(timeout)))
        else:
            done, not_done = set(), set()

        self._executor.shutdown(wait=False, cancel_futures=True)
        elapsed = monotonic() - started
        return ShutdownReport(
            submitted=submitted,
            completed=len(done),
            unfinished=len(not_done),
            timed_out=bool(not_done),
            elapsed_seconds=elapsed,
        )


__all__ = [
    "ShutdownReport",
    "TaskHandle",
    "TaskScope",
    "TaskScopeSnapshot",
    "TaskSupervisor",
    "TaskToken",
    "TaskWorker",
]
