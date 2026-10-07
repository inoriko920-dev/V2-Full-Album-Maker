# M2 Implementation Evidence — Task Lifecycle

Status: **PASS**

## Scope

M2 introduces the central Python task-lifecycle boundary approved by STEP04 while
leaving existing async/service ownership intact.

## Branch / Baseline

- Repository: `inoriko920-dev/V2-Full-Album-Maker`
- Branch: `impl-m2-task-lifecycle`
- M1 parent: `d1c8296e970d8e915fc874db8e6d0439ca6f9f69`
- Validated M2 candidate: `e69f426ec53ca1f2e0e2164758ddf63a8db36bb3`

## Deliverables

1. `src/full_album_maker/app_errors.py`
   - typed lifecycle error codes;
   - AppError / AppResult;
   - cancellation / closed / stale errors.

2. `src/full_album_maker/task_lifecycle.py`
   - TaskToken;
   - TaskScope with generation invalidation;
   - TaskSupervisor with bounded ThreadPoolExecutor ownership;
   - TaskHandle with current-result check;
   - ShutdownReport;
   - cooperative cancellation and bounded shutdown.

3. `src/full_album_maker/app_kernel.py`
   - AppKernel owns one TaskSupervisor;
   - CompositionRoot constructs/injects it;
   - supervisor is closed in finally after GUI/portable runner exit.

4. `src/full_album_maker/task_owner_inventory.py`
   - machine-readable characterization of seven legacy async owners;
   - no owner module import or mutation.

5. `tests/test_v2_task_lifecycle.py`
   - typed error/result tests;
   - generation invalidation;
   - stale/current result behavior;
   - cooperative cancel;
   - bounded close with non-cooperative worker;
   - closed/foreign-scope rejection;
   - AppKernel normal/exception shutdown;
   - technology-neutral import boundary;
   - legacy owner inventory validation.

6. `.github/workflows/v2-m2-task-lifecycle.yml`
   - Q0 compile/contracts;
   - existing async import + AI stale guards;
   - render/close lifecycle characterization;
   - nine-workspace launch characterization;
   - authoritative-state/canonical-save shell.

## Verified GitHub Actions Evidence

Run: `37585385248`
Job: `m2-task-lifecycle`
Commit: `e69f426ec53ca1f2e0e2164758ddf63a8db36bb3`

Results:
- Q0 compile: PASS;
- M0/M1/M2 contract suite: **27 passed in 0.46s**;
- legacy async-import + AI stale/cancel characterization: **7 passed in 0.91s**;
- render + close lifecycle characterization: **3 passed in 1.70s**;
- nine-workspace navigation read-only smoke: **1 passed in 1.13s**;
- authoritative project state + canonical save production shell: **1 passed in 0.94s**;
- job conclusion: **success**.

## Gate Harness Correction

Runs `37584948856` and `37585082430` failed because the workflow selected
`test_finished_import_is_discarded_if_project_changed` alone. That baseline test
constructs a QWidget but relies on the first test in `test_async_import.py` to
create QApplication. Qt therefore aborted before a product assertion.

Correction:
- run the complete baseline `tests/test_async_import.py` file;
- do not modify the existing baseline test or async-import implementation.

The corrected workflow then passed.

## Change Isolation

M2 changes only:
- new app error/task lifecycle/inventory modules;
- AppKernel task-supervisor wiring;
- M2 tests/docs/workflow/status evidence.

No existing legacy async owner module was edited:
- async_import.py unchanged;
- editor_workspace.py unchanged;
- media_preview_cache.py unchanged;
- spectrum_preview_step08.py unchanged;
- template_thumbnail_cache_step07.py unchanged;
- ai_async_step09.py unchanged;
- render_async_step10.py unchanged.

No ProcessSupervisor, ApplicationLifecycleService, persistence migration, renderer,
preview/cache migration, workspace migration, project schema change, dependency
change, or UI redesign is included.

## Ownership After M2

- ProjectDocument + EditorController/EditorSession remain authoritative.
- AppKernel owns the central TaskSupervisor boundary.
- Existing async owners still own their current workers until individually migrated.
- TaskSupervisor owns Python task lifecycle only, not subprocess lifecycle.
- ProcessSupervisor (H3) remains required before central subprocess ownership.
- ApplicationLifecycleService (H4) remains a separate later hardening boundary.

## Gate

**M2: PASS**

This evidence/status commit must pass the same M2 workflow on its own final head
before M3 starts.
