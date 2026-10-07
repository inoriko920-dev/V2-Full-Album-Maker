# M1 — AppKernel / CompositionRoot Additive Migration

Status: **IMPLEMENTED — validation pending**

## Scope

M1 introduces one explicit launch-time composition boundary without replacing
any existing production implementation.

M1 is intentionally additive:
- no ProjectDocument replacement;
- no EditorController/EditorSession replacement;
- no TaskSupervisor implementation yet;
- no persistence migration;
- no render/preview/media/AI/workspace ownership migration;
- no removal/reordering of the production `install_*()` chain;
- no UI redesign;
- no project schema/version/dependency change.

## New Boundary

`src/full_album_maker/app_kernel.py` introduces:

- `CompositionRoot`
  - validates the M0/T1 FeatureParityRegistry;
  - wires the currently proven GUI and portable-smoke entrypoints;
  - builds exactly one `AppKernel`.

- `AppKernel`
  - owns only application launch dispatch in M1;
  - chooses the portable smoke path only when `--portable-smoke` is present;
  - otherwise delegates to the existing production GUI runner.

- `LegacyRuntimeAdapter`
  - wraps current production entrypoints;
  - does not claim project/service ownership;
  - is the rollback-safe adapter boundary for later migration slices.

## Production Entry Point

`src/full_album_maker/main.py` keeps the existing installer sequence unchanged.
After all compatibility/presentation installers are applied, the legacy GUI
runner still imports `full_album_maker.v14_window.run`.

The only production routing change is:

```
main(argv)
  -> build_app_kernel(...)
  -> AppKernel.run(argv)
       -> current portable smoke OR current GUI runner
```

This makes startup wiring explicit without creating a second app.

## Ownership After M1

| Boundary | Production owner after M1 | Migration phase |
|---|---|---|
| Project state | ProjectDocument + EditorController/EditorSession | unchanged |
| Legacy envelope | existing compatibility/persistence bridge | unchanged |
| Async/process lifecycle | existing distributed owners | M2 |
| Persistence/recovery | existing implementation | M3 |
| Final render | existing STEP10 -> Step08 -> V13 -> S11 -> FFmpegV2 chain | M4 |
| Probe/preview/cache | existing implementations | M5 |
| Beat analysis | not yet production-owned by V2 | M6 |
| Workspace composition | existing runtime installers/patches | M7 |
| AI planning/runtime | existing STEP09/V14 behavior | later approved slice |
| Launch wiring | **AppKernel / CompositionRoot** | **M1** |

## M0/T1 Integration

CompositionRoot calls `FeatureParityRegistry.assert_valid()` while building.
A later slice therefore cannot start the application through the V2 root with
an invalid/empty characterization registry.

The registry remains read-only evidence; it does not become project state.

## Feature-Parity IDs Touched

Because M1 changes only the production launch boundary, the focused parity
surface is:

- `FP-OFFLINE-01` — manual editing/rendering remains first-class;
- `FP-PORTABLE-01` — portable smoke remains explicitly routable;
- all 9 workspace navigation is exercised as a broad startup/read-only
  characterization smoke because a launch regression could affect every route.

No feature implementation is replaced in M1.

## Q0 / Q1 Gate

M1 PASS requires:
1. source + M1 tests compile;
2. AppKernel/CompositionRoot focused tests pass;
3. existing main-entrypoint ordering test passes;
4. nine-workspace production navigation remains read-only;
5. production shell still uses one authoritative project state and canonical save;
6. branch diff contains only M1 kernel/wiring/tests/docs/workflow/status evidence;
7. no M2 lifecycle implementation appears.

## Rollback

Rollback is trivial: the M1 branch can be abandoned and M0 head
`cbd803aa1effa8c36f0f0f6a1ac0304aae1974be` remains unchanged.

No project/data migration exists in M1, so rollback requires no data conversion.

## Next Slice

After M1 gate PASS, the next allowed slice is **M2 — Task Lifecycle**.
M2 must not begin in the same implementation turn.
