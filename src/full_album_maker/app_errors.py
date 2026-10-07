"""Small typed application error/result primitives for V2 hardening.

M2 only needs a stable, technology-neutral way to distinguish cancellation,
closed lifecycle boundaries, stale results, validation failures, and internal
failures. Cross-service diagnostics/redaction remains a later hardening slice.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Generic, TypeVar


T = TypeVar("T")


class AppErrorCode(str, Enum):
    CANCELLED = "CANCELLED"
    CLOSED = "CLOSED"
    STALE = "STALE"
    VALIDATION = "VALIDATION"
    INTERNAL = "INTERNAL"


class AppError(RuntimeError):
    """Typed application-level failure without UI/Qt/process dependencies."""

    def __init__(
        self,
        code: AppErrorCode,
        message: str,
        *,
        retryable: bool = False,
    ) -> None:
        super().__init__(str(message))
        self.code = AppErrorCode(code)
        self.retryable = bool(retryable)


class TaskCancelledError(AppError):
    def __init__(self, message: str = "Task dibatalkan.") -> None:
        super().__init__(AppErrorCode.CANCELLED, message, retryable=False)


class LifecycleClosedError(AppError):
    def __init__(self, message: str = "Lifecycle sudah ditutup.") -> None:
        super().__init__(AppErrorCode.CLOSED, message, retryable=False)


class StaleResultError(AppError):
    def __init__(self, message: str = "Hasil task sudah stale.") -> None:
        super().__init__(AppErrorCode.STALE, message, retryable=False)


@dataclass(frozen=True, slots=True)
class AppResult(Generic[T]):
    """Simple explicit result for boundaries that do not want to throw."""

    value: T | None = None
    error: AppError | None = None

    def __post_init__(self) -> None:
        if (self.value is None) == (self.error is None):
            raise ValueError("AppResult harus memiliki tepat satu dari value atau error.")

    @property
    def ok(self) -> bool:
        return self.error is None

    def unwrap(self) -> T:
        if self.error is not None:
            raise self.error
        return self.value  # type: ignore[return-value]


__all__ = [
    "AppError",
    "AppErrorCode",
    "AppResult",
    "LifecycleClosedError",
    "StaleResultError",
    "TaskCancelledError",
]
