# M1 Implementation Evidence — AppKernel / CompositionRoot

Status: **PASS**

## Scope

M1 establishes one explicit launch-time composition boundary and routes the current
production entrypoints through it without replacing existing service ownership.

## Branch / Baseline

- Repository: `inoriko920-dev/V2-Full-Album-Maker`
- Branch: `impl-m1-app-kernel`
- M0 parent: `cbd803aa1effa8c36f0f0f6a1ac0304aae1974be`
- First validated M1 candidate: `10387ede457cd66873321cbe23dee5125bf6b33b`

## Deliverables

1. `src/full_album_maker/app_kernel.py`
   - `CompositionRoot`;
   - `AppKernel`;
   - `LegacyRuntimeAdapter`;
   - M0 FeatureParityRegistry validation at composition time;
   - no Qt/subprocess/project-state ownership.

2. `src/full_album_maker/main.py`
   - keeps the existing installer order;
   - keeps the deferred `v14_window.run` import after installers;
   - delegates GUI/portable-smoke launch selection to AppKernel.

3. `tests/test_v2_app_kernel.py`
   - validates CompositionRoot construction;
   - validates GUI vs portable-smoke dispatch exactly once;
   - validates unrelated CLI behavior;
   - validates fail-closed invalid M0 registry;
   - statically proves AppKernel does not import Qt/subprocess/project state;
   - validates main keeps installer-before-GUI-import behavior.

4. `docs/implementation/M1_APP_KERNEL_COMPOSITION_ROOT.md`
   - records ownership boundaries, touched parity IDs, gate, and rollback.

5. `.github/workflows/v2-m1-app-kernel.yml`
   - Q0 compile;
   - M0 + M1 contract tests;
   - Q1 nine-workspace launch characterization;
   - Q1 one-authoritative-state/canonical-save production shell.

## Verified GitHub Actions Evidence

Run: `37583919255`
Job: `m1-app-kernel`
Commit: `10387ede457cd66873321cbe23dee5125bf6b33b`

Results:
- Q0 compile: PASS;
- `pytest tests/test_v2_feature_parity_registry.py tests/test_v2_app_kernel.py tests/test_editor_v2_main_entrypoint.py`: **14 passed in 0.27s**;
- nine-workspace navigation read-only smoke: **1 passed in 1.69s**;
- authoritative project state + canonical save production shell: **1 passed in 0.84s**;
- job conclusion: **success**.

## Change Isolation

Comparison from M0 head to the first validated M1 candidate contains exactly five
M1 files: workflow, M1 documentation, AppKernel, main-entrypoint wiring, and M1 tests.

No renderer, UI workspace, persistence, AI, project schema, dependency, version,
or task-lifecycle implementation was changed.

## Ownership Invariant

After M1:
- ProjectDocument + EditorController/EditorSession remain authoritative;
- legacy Project remains compatibility only;
- current distributed async/process owners remain unchanged until M2;
- current render/persistence/preview/workspace/AI implementations remain production owners;
- AppKernel owns only launch-time routing/wiring.

## Gate

**M1: PASS**

This evidence/status commit must pass the same M1 GitHub Actions workflow on its
own final head before M2 begins.
