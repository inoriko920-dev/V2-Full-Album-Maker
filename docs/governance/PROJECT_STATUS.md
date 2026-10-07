# V2 Full-Album-Maker — Project Status

## Current Phase
IMPLEMENTATION — M1 COMPOSITION ROOT

## Current STEP
M1 — AppKernel / CompositionRoot — PASS

## Gate Status
- STEP 00: PASS
- STEP 01: PASS
- STEP 02: PASS
- STEP 03: PASS
- STEP 04: PASS
- STEP 05: PASS
- STEP 06: PASS
- STEP 07: PASS
- STEP 08: PASS
- STEP 09: PASS
- STEP 10: PASS
- STEP 11: PASS

## STEP 11 Final Release / Handoff Direction
- First mature V2 stable target is v2.0.0 after implementation and Q0–Q5 PASS; no version bump was performed during planning.
- Stable publication must be explicit from a Q5-approved candidate SHA; main push must not auto-publish an unapproved stable release.
- Exact tested ZIP must be the published ZIP and is identified by semantic version + candidate commit + SHA-256.
- Windows portable remains the primary distribution model: Python 3.12.10 release runtime, pinned dependencies, pinned FFmpeg digest, pinned font, PyInstaller onedir.
- Extracted-ZIP smoke must run in Unicode/apostrophe path without global Python, global FFmpeg, or API keys and must verify audio+video output.
- One canonical release manifest should prevent drift between workflow/build script/CAPABILITIES/notices.
- Current THIRD_PARTY_NOTICES.md contains stale FFmpeg provenance and is a release blocker before V2 RC.
- Current stable-release-on-main behavior and old hardcoded STEP11 ancestry in release QA must be redesigned before V2 stable.
- Application rollback and project-data rollback are separate contracts.
- Initial updates use side-by-side portable folders; auto-updater/installer remain deferred.
- Old Full-Album-Maker repository remains permanently read-only.

## Planning Status
STEP 00–11 planning is COMPLETE.

## Coding Status
M0/T1 and M1 are implemented and validated.

M1 result:
- one explicit `AppKernel / CompositionRoot` launch boundary exists;
- current GUI and portable-smoke implementations are wrapped by `LegacyRuntimeAdapter`;
- `main.py` routes launch through the kernel after the existing installer chain;
- FeatureParityRegistry is validated when the composition root builds;
- ProjectDocument + EditorController/EditorSession remain authoritative;
- no service ownership was migrated and no legacy installer was removed/reordered.

Validated on Actions run `37583919255`: Q0 compile PASS, 14 contract tests PASS, Q1 nine-workspace navigation PASS, Q1 authoritative-state/canonical-save production shell PASS.

No UI redesign, dependency, project schema, renderer, persistence, AI, workspace ownership, or M2 lifecycle migration was performed.

## Next Operational Step
M1 is PASS. On the next explicit implementation turn:
1. Start **M2 — Task Lifecycle** only.
2. Introduce the central TaskSupervisor/TaskScope boundary additively.
3. Characterize current async/process owners before routing any owner through M2.
4. Do not migrate persistence, render orchestration, preview/cache, workspace ownership, or AI provider ownership yet.
5. Preserve M0 FeatureParityRegistry and M1 AppKernel boundaries.
6. Run focused Q0/Q1 lifecycle/cancel/close/stale-result evidence before reporting M2 PASS.
7. Do not proceed to M3 in the same turn unless explicitly instructed otherwise.

## Canonical References
- MASTER planning DOCX.
- STEP 00–11 final planning DOCX files.
- `docs/planning/STEP_11_WINDOWS_PORTABLE_BUILD_RELEASE_ROLLBACK_DAN_HANDOFF_FINAL.md`
- `docs/planning/STEP_11_ARTIFACT_INTEGRITY.txt`
- `docs/planning/PLANNING_ARTIFACTS_MANIFEST.md`
- prior STEP planning summaries/integrity files.
- `docs/governance/PROJECT_GOVERNANCE.md`
- `docs/governance/AI_HANDOFF.md`
