# M4 — RenderEngine Facade

Status: **IMPLEMENTED — validation pending**

## Scope

M4 introduces the approved `RenderEngine` application-service boundary around
the current proven STEP10 render implementation.

This slice is intentionally a strangler/facade migration:
- the current STEP10 `RenderExecutor` remains the execution adapter;
- `Step08FFmpegCompiler -> V13 -> S11 -> FFmpegV2` remains untouched;
- FFmpeg/ffprobe remain canonical;
- critical preflight remains immediately before every execution;
- progress, cooperative cancel, staged output, ffprobe verification, and
  transactional publication remain owned by the proven implementation;
- no ProcessSupervisor/H3 replacement is introduced;
- no Preview/Cache M5, Beat Analysis M6, WorkspaceRegistry M7, UI redesign,
  schema bump, dependency change, or release work is included.

## New Boundary

`src/full_album_maker/render_engine.py` adds:

- `RenderEngine`
  - one canonical facade for UI preflight and final execution;
  - one capability policy for preflight and execution;
  - one active-attempt guard at the application-service boundary;
  - delegates execution to the existing `RenderExecutor`;
  - passes progress/log/cancel callbacks through unchanged.

- `RenderPreflightResult`
  - pairs the immutable preflight report with the exact capability evidence used
    to produce it.

- `bind_render_engine()` / `current_render_engine()`
  - a bounded `ContextVar` migration bridge used only while the legacy runtime
    constructs the production window;
  - allows `RenderAsyncBridge` to capture the exact AppKernel-owned engine;
  - resets after the legacy runner returns, so it is not a permanent service
    locator or second owner.

## Production Ownership After M4

`CompositionRoot` creates or accepts exactly one `RenderEngine` and stores it on
`AppKernel`.

During normal GUI launch:

    AppKernel.run()
      -> bind_render_engine(kernel.render_engine)
      -> existing legacy GUI runner
      -> RenderAsyncBridge captures current_render_engine()
      -> RenderEngine.preflight()/execute()
      -> existing RenderExecutor
      -> Step08 -> V13 -> S11 -> FFmpegV2
      -> FFmpeg process
      -> ffprobe verification
      -> transactional publish

The Qt bridge no longer imports or constructs `RenderExecutor` directly.

## Preserved STEP 06 Contracts

- D06-01: one canonical RenderEngine orchestration boundary.
- D06-02/D06-03: immutable `RenderSnapshot` / canonical `RenderPlan` remain
  unchanged.
- D06-04: `RenderExecutor` still performs critical preflight immediately before
  launch.
- D06-05: AUTO hardware runtime verification + software fallback policy moved
  behind `RenderEngine.capability_for_settings()` without semantic change.
- D06-06: compiler chain is wrapped, not rewritten.
- D06-07: existing large-filter-graph externalization remains untouched.
- D06-08: unique staging/work artifacts remain in `RenderExecutor`.
- D06-09/D06-10: COMPLETED still requires successful process + ffprobe
  verification + publish.
- D06-11/D06-12: publication/recovery infrastructure is not weakened.
- D06-13: pause/resume and crash-resume remain deferred.
- D06-14: 200-song/~3-hour structural stress remains a regression floor.
- D06-15/D06-16: disk budget and one-pass default remain unchanged.
- D06-17: composition semantics remain shared with the existing compiler path.
- D06-18: no audio-retiming/beat-analysis change.
- D06-19: existing safe render evidence/log sanitization remains.
- D06-20: no compiler consolidation is attempted.

## Lifecycle Boundary

M4 does **not** claim H3 ProcessSupervisor. The existing STEP10 process runner
continues to own FFmpeg process termination and the current cancel contract.
That avoids mixing facade migration with subprocess-lifecycle replacement.

`RenderEngine` adds only a facade-level active-attempt lock. The existing
`RenderAsyncBridge` still owns its UI busy/cancel event and its worker executor.

## Rollback

M4 is additive and branch-isolated. Rollback target is the M3 PASS head:

`b8ff524b94f85d6b090a846e2b78c18c51983757`

No project/schema/data migration is introduced.

## Gate

M4 may be marked PASS only after:
1. M0–M4 contract tests pass;
2. baseline STEP10 preflight/executor/queue/UI tests pass;
3. baseline render lifecycle/atomic publication tests pass;
4. AppKernel production launch characterization remains PASS;
5. real FFmpeg executes through `RenderEngine`, then ffprobe-verifies before
   final publication;
6. the production Qt bridge is proven to route through RenderEngine rather than
   directly constructing RenderExecutor;
7. no M5/M6/M7/UI redesign scope appears in the branch diff.

## Next

After M4 PASS, the next allowed migration phase is **M5 — Probe / Preview /
Cache**. M5 must not start in the same turn.
