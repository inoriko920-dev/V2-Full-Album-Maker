from __future__ import annotations

import ast
from concurrent.futures import TimeoutError as FutureTimeoutError
from pathlib import Path
from threading import Event
from time import monotonic

import pytest

from full_album_maker.app_errors import (
    AppError,
    AppErrorCode,
    AppResult,
    LifecycleClosedError,
    StaleResultError,
    TaskCancelledError,
)
from full_album_maker.app_kernel import build_app_kernel
from full_album_maker.task_lifecycle import TaskScope, TaskSupervisor
from full_album_maker.task_owner_inventory import LEGACY_TASK_OWNERS, OWNER_IDS


ROOT = Path(__file__).resolve().parents[1]


def test_typed_app_error_and_result_are_technology_neutral() -> None:
    error = AppError(AppErrorCode.VALIDATION, "invalid", retryable=False)
    failed = AppResult[str](error=error)
    success = AppResult[str](value="ok")

    assert failed.ok is False
    with pytest.raises(AppError) as caught:
        failed.unwrap()
    assert caught.value.code is AppErrorCode.VALIDATION

    assert success.ok is True
    assert success.unwrap() == "ok"


def test_scope_generation_invalidation_cancels_old_token_and_accepts_new_token() -> None:
    scope = TaskScope("project")
    old = scope.issue_token("old")
    assert scope.is_current(old)

    generation = scope.invalidate("project switched")
    assert generation == 1
    assert old.cancelled is True
    assert scope.is_current(old) is False
    with pytest.raises(TaskCancelledError, match="project switched"):
        old.raise_if_cancelled()

    new = scope.issue_token("new")
    assert new.generation == 1
    assert scope.is_current(new)


def test_supervisor_returns_current_completed_result_and_releases_bookkeeping() -> None:
    supervisor = TaskSupervisor(max_workers=1)
    scope = supervisor.create_scope("preview")

    handle = supervisor.submit(scope, lambda token: (token.raise_if_cancelled(), 42)[1], task_name="frame")

    assert handle.result_if_current(timeout=2) == 42
    assert supervisor.wait_for_idle(timeout=2) is True
    assert supervisor.pending_count == 0
    assert scope.snapshot().active_tokens == 0

    report = supervisor.close(timeout=0.2)
    assert report.timed_out is False
    assert report.submitted == 1
    assert report.completed == 1
    assert report.unfinished == 0


def test_stale_result_is_rejected_after_scope_invalidation() -> None:
    supervisor = TaskSupervisor(max_workers=1)
    scope = supervisor.create_scope("project")
    release = Event()
    started = Event()

    def work(token):
        started.set()
        release.wait(2)
        return "old-result"

    handle = supervisor.submit(scope, work, task_name="old-project")
    assert started.wait(1)
    supervisor.invalidate_scope("project", "project switched")
    release.set()

    with pytest.raises(TaskCancelledError):
        handle.result(timeout=2)
    with pytest.raises((TaskCancelledError, StaleResultError)):
        handle.result_if_current(timeout=2)

    supervisor.close(timeout=0.2)


def test_cooperative_worker_observes_cancel_without_project_callback() -> None:
    supervisor = TaskSupervisor(max_workers=1)
    scope = supervisor.create_scope("ai")
    started = Event()

    def work(token):
        started.set()
        assert token.cancelled is False
        while not token.cancelled:
            token.wait_cancelled(0.01)
        token.raise_if_cancelled()
        return "unreachable"

    handle = supervisor.submit(scope, work, task_name="interpret")
    assert started.wait(1)
    scope.cancel_all("user cancelled")

    with pytest.raises(TaskCancelledError, match="user cancelled"):
        handle.result(timeout=2)
    assert supervisor.wait_for_idle(timeout=2)
    supervisor.close(timeout=0.2)


def test_close_is_bounded_and_reports_noncooperative_worker() -> None:
    supervisor = TaskSupervisor(max_workers=1)
    scope = supervisor.create_scope("legacy")
    release = Event()
    started = Event()

    def work(_token):
        started.set()
        release.wait(2)
        return "late"

    handle = supervisor.submit(scope, work, task_name="non-cooperative")
    assert started.wait(1)

    before = monotonic()
    report = supervisor.close(timeout=0.03)
    elapsed = monotonic() - before

    assert report.timed_out is True
    assert report.submitted == 1
    assert report.completed == 0
    assert report.unfinished == 1
    assert elapsed < 0.5
    assert supervisor.closed is True
    assert scope.closed is True
    assert handle.token.cancelled is True

    release.set()
    with pytest.raises(TaskCancelledError):
        handle.result(timeout=2)


def test_closed_supervisor_rejects_new_scope_and_submit() -> None:
    supervisor = TaskSupervisor(max_workers=1)
    scope = supervisor.create_scope("media")
    supervisor.close(timeout=0)

    with pytest.raises(LifecycleClosedError):
        supervisor.create_scope("other")
    with pytest.raises(LifecycleClosedError):
        supervisor.submit(scope, lambda token: 1)


def test_foreign_scope_cannot_be_submitted() -> None:
    supervisor = TaskSupervisor(max_workers=1)
    foreign = TaskScope("foreign")

    with pytest.raises(ValueError, match="bukan milik"):
        supervisor.submit(foreign, lambda token: 1)

    supervisor.close(timeout=0)


def test_app_kernel_owns_one_supervisor_and_closes_it_after_runner_returns() -> None:
    supervisor = TaskSupervisor(max_workers=1)
    calls: list[str] = []
    kernel = build_app_kernel(
        gui_runner=lambda: calls.append("gui") or 9,
        portable_smoke_runner=lambda: 0,
        task_supervisor=supervisor,
        shutdown_timeout_seconds=0.1,
    )

    assert kernel.tasks is supervisor
    assert kernel.run([]) == 9
    assert calls == ["gui"]
    assert supervisor.closed is True


def test_app_kernel_closes_supervisor_when_runner_raises() -> None:
    supervisor = TaskSupervisor(max_workers=1)

    def fail() -> int:
        raise RuntimeError("boom")

    kernel = build_app_kernel(
        gui_runner=fail,
        portable_smoke_runner=lambda: 0,
        task_supervisor=supervisor,
        shutdown_timeout_seconds=0.1,
    )

    with pytest.raises(RuntimeError, match="boom"):
        kernel.run([])
    assert supervisor.closed is True


def test_task_lifecycle_has_no_qt_subprocess_or_project_state_import() -> None:
    path = ROOT / "src" / "full_album_maker" / "task_lifecycle.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)

    assert not any(name.startswith("PySide6") for name in imported)
    assert "subprocess" not in imported
    assert not any(
        name.endswith(suffix)
        for name in imported
        for suffix in (
            "editor_models",
            "editor_controller",
            "editor_session",
            "project",
            "project_repository",
            "render_executor_step10",
        )
    )


def test_legacy_task_owner_inventory_is_complete_and_points_to_real_files() -> None:
    expected = {
        "async-import",
        "editor-preview-render",
        "media-preview-cache",
        "spectrum-preview",
        "template-thumbnail",
        "ai-provider",
        "render-center",
    }
    assert OWNER_IDS == expected
    assert len(LEGACY_TASK_OWNERS) == len(expected)
    for owner in LEGACY_TASK_OWNERS:
        path = ROOT / owner.path
        assert path.is_file(), owner.owner_id
        source = path.read_text(encoding="utf-8")
        assert any(marker in source for marker in (
            "threading.Thread",
            "ThreadPoolExecutor",
        )), owner.owner_id
        assert owner.stale_guard.strip()
        assert owner.shutdown.strip()
        assert owner.migration_note.strip()


def test_m2_does_not_modify_legacy_owner_modules_by_importing_inventory() -> None:
    # Inventory is intentionally passive data: importing it cannot import any
    # owner implementation, Qt, subprocess, or project state.
    path = ROOT / "src" / "full_album_maker" / "task_owner_inventory.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
    assert not any(name.startswith("PySide6") for name in imported)
    assert "subprocess" not in imported
    assert not any("async_import" in name or "render_async" in name for name in imported)
