# M2 — Task Lifecycle / TaskSupervisor / TaskScope

Status: **PASS — central task lifecycle implemented and validated**

## Scope

M2 introduces the central task-lifecycle boundary approved by STEP 04 without
migrating service/process ownership prematurely.

Implemented in this slice:
- H1 prerequisite: small typed `AppError/AppResult` lifecycle primitives;
- H2: `TaskToken`, `TaskScope`, `TaskSupervisor`, `TaskHandle`;
- one central `TaskSupervisor` owned by `AppKernel`;
- generation-based stale-result protection;
- cooperative cancellation;
- bounded supervisor close with explicit unfinished-task report;
- machine-readable characterization inventory of current legacy async owners.

Not implemented in this slice:
- H3 ProcessSupervisor;
- H4 ApplicationLifecycleService;
- persistence/recovery migration;
- RenderEngine orchestration migration;
- PreviewEngine/CacheManager migration;
- WorkspaceRegistry migration;
- AI provider ownership migration;
- replacement/removal of existing worker implementations.

## STEP 04 Decisions Preserved

- D04-01: TaskToken mandatory for new async task identity.
- D04-03 remains future work: ApplicationLifecycleService not introduced here.
- D04-04/D04-11: generation invalidation is the stale-result target model.
- D04-13: shutdown waits are bounded.
- D04-15: existing safety code is not retired before replacement parity.
- Hard no-go preserved: daemon thread is not treated as sufficient lifecycle ownership.
- H3 ProcessSupervisor remains separate because Python thread cancellation cannot kill subprocesses.

## New Task Lifecycle Contract

```
AppKernel
  └─ TaskSupervisor
       ├─ TaskScope("...")
       │    ├─ generation
       │    ├─ TaskToken
       │    └─ cancel / invalidate / close
       └─ ThreadPoolExecutor (bounded)
```

### TaskToken

A token carries:
- stable scope identity;
- scope generation;
- unique task identity;
- task name;
- cooperative cancellation state/reason.

A worker may call:
- `token.cancelled`;
- `token.wait_cancelled(timeout)`;
- `token.raise_if_cancelled()`.

### TaskScope

A scope:
- issues tokens for one logical lifecycle boundary;
- increments generation on invalidate;
- cancels all older tokens when invalidated;
- rejects new tokens after close;
- determines whether a completed token is still current.

### TaskSupervisor

The supervisor:
- owns a bounded ThreadPoolExecutor;
- owns named TaskScopes;
- rejects foreign scopes;
- rejects new work after close;
- tracks pending futures;
- invalidates scopes explicitly;
- closes all scopes;
- waits only up to a bounded timeout;
- returns a `ShutdownReport` when workers do not cooperate.

Important limitation:
**TaskSupervisor cannot forcibly kill a running Python thread.**
That is why non-cooperative work is reported rather than waited forever.
Subprocess ownership/termination remains H3 ProcessSupervisor.

### TaskHandle

`TaskHandle.result_if_current()` requires a result to belong to the current,
non-cancelled scope generation. A stale generation cannot be treated as a valid
completion.

## AppKernel Integration

M1 already made AppKernel the composition boundary.

M2 adds:
- exactly one central `TaskSupervisor` field on AppKernel;
- CompositionRoot creates it unless a tested/injected supervisor is supplied;
- AppKernel closes the supervisor in `finally` after GUI or portable-smoke
  runner exits;
- bounded shutdown occurs even if the runner raises.

No current GUI/service receives the supervisor yet. This is deliberate: owner
migration requires owner-specific characterization and happens only in approved
later slices.

## Legacy Async Owner Inventory

M2 records seven current owners without changing them.

| Owner | Current primitive | Current stale/cancel protection | Current shutdown | Migration rule |
|---|---|---|---|---|
| async-import | daemon `threading.Thread` | captured `project_ref` identity | no explicit join | migrate only after import characterization |
| editor-preview-render | daemon `threading.Thread` | busy/current workspace behavior | no central owner | wait for preview/render facade boundaries |
| media-preview-cache | bounded daemon queue | generation token | no explicit close baseline | M5 preview/cache |
| spectrum-preview | `ThreadPoolExecutor` | generation token | executor shutdown | preserve parity during preview migration |
| template-thumbnail | `ThreadPoolExecutor` | cache-key pending + immutable snapshot | wait_for_idle + close | cache/preview lifecycle slice |
| ai-provider | `ThreadPoolExecutor` | generation + owner-thread queued delivery | cancel/wait/close | migrate only with AI-specific parity |
| render-center | executor + cancel Event | preflight generation + attempt identity | cancel/invalidate/close | after ProcessSupervisor / RenderEngine gates |

The machine-readable source is:
`src/full_album_maker/task_owner_inventory.py`.

## Why M2 Does Not Route Legacy Owners Yet

Routing all current workers through TaskSupervisor in one change would violate the
strangler migration plan. Each owner currently has different semantics:
- some use Qt queued delivery;
- some use project-reference guards;
- some run FFmpeg/subprocess work;
- some own cache-specific de-duplication;
- render has attempt identity and process cancellation;
- AI has provider/network-specific stale behavior.

M2 therefore creates the common boundary first and proves it independently.
Later migrations wrap one owner at a time and retain the old guard until parity
tests pass.

## Feature-Parity Surface

M2 does not change feature behavior. Risk is lifecycle-level and therefore broad.

Focused parity/evidence:
- FP-OFFLINE-01: application still launches/works without AI;
- FP-AI-02 / FP-AI-03: existing AI stale/idempotency behavior must stay intact;
- FP-RENDER-03: existing cancel/no-partial-publish behavior must stay intact;
- Media import stale-project behavior remains characterized;
- nine-workspace navigation remains read-only;
- authoritative ProjectDocument/canonical-save production shell remains intact.

## Q0 / Q1 Gate

M2 PASS requires:
1. compile of source + new M2 tests;
2. M0 FeatureParityRegistry tests remain PASS;
3. M1 AppKernel tests remain PASS;
4. typed lifecycle error/result tests PASS;
5. TaskScope generation/cancel/stale tests PASS;
6. cooperative cancellation test PASS;
7. bounded close with a deliberately non-cooperative worker PASS;
8. closed supervisor and foreign-scope rejection PASS;
9. AppKernel closes central TaskSupervisor on normal return and exception;
10. owner inventory points to real baseline async modules;
11. existing async import stale-project tests PASS;
12. existing AI async stale/cancel tests PASS;
13. existing render cancel/lifecycle tests PASS;
14. nine-workspace navigation remains read-only;
15. authoritative production shell/canonical save remains one-state;
16. branch diff proves no existing async owner implementation was edited;
17. no ProcessSupervisor/H3 or M3 persistence implementation appears.

## Rollback

Rollback target is M1 head:
`d1c8296e970d8e915fc874db8e6d0439ca6f9f69`.

M2 makes no project/schema/data migration, so branch rollback requires no data
conversion.

## Next Allowed Work

After M2 gate PASS, the next migration phase is **M3 — Persistence** according to
the approved M0→M9 architecture order.

However, STEP 04 H3/H4 lifecycle hardening may need to be completed as a bounded
precondition before a later boundary uses subprocess/application-close ownership.
Do not silently combine those with M3 in this M2 slice.


## Validation Evidence

Validated M2 candidate:
- commit: `e69f426ec53ca1f2e0e2164758ddf63a8db36bb3`
- GitHub Actions run: `37585385248`
- job: `m2-task-lifecycle`
- Q0 compile: PASS
- M0 + M1 + M2 contracts: **27 passed**
- legacy async-import + AI stale/cancel characterization: **7 passed**
- render/close lifecycle characterization: **3 passed**
- nine-workspace read-only launch characterization: **1 passed**
- authoritative-state/canonical-save production shell: **1 passed**
- job conclusion: **success**

Two earlier workflow attempts failed before product assertions because a later
`test_async_import.py` test was selected in isolation even though that baseline
file initializes `QApplication` in its first test. The workflow was corrected to
run the baseline file as designed. No legacy async-import source/test was modified
to obtain PASS.

The evidence/status commit that records this PASS must rerun the same workflow on
its own final head before M3 begins.
