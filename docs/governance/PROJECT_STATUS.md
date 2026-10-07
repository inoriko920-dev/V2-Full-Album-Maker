# V2 Full-Album-Maker — Project Status

## Current Phase
IMPLEMENTATION — M2 TASK LIFECYCLE

## Current STEP
M2 — Task Lifecycle / TaskSupervisor / TaskScope — PASS

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
M0/T1, M1, and M2 are implemented and validated.

M2 result:
- typed lifecycle `AppError/AppResult` primitives added as STEP04 H1 prerequisite;
- central `TaskToken / TaskScope / TaskSupervisor / TaskHandle` boundary added;
- AppKernel now owns exactly one central TaskSupervisor and closes it in `finally`;
- scope generation invalidation cancels old tokens and rejects stale result use;
- cooperative cancellation and bounded close are explicit;
- non-cooperative Python threads are reported as unfinished instead of blocking forever;
- seven existing async/task owners are recorded in a machine-readable inventory;
- no legacy async owner implementation was migrated or edited.

Validated on Actions run `37585385248`: Q0 compile PASS, 27 M0/M1/M2 contract tests PASS, 7 legacy async stale/cancel tests PASS, 3 render/close lifecycle tests PASS, 1 nine-workspace navigation test PASS, and 1 authoritative-state/canonical-save production shell test PASS.

H3 ProcessSupervisor and H4 ApplicationLifecycleService are **not implemented in this slice**. No persistence, RenderEngine, preview/cache, workspace, AI ownership, schema, dependency, UI, or release migration was performed.

## Next Operational Step
M2 is PASS. On the next explicit implementation turn:
1. Start **M3 — Persistence** only, following the approved M0→M9 order.
2. Keep ProjectDocument authoritative and legacy Project compatibility-only.
3. Introduce/wrap ProjectPersistence behind existing proven save/load behavior before replacing any direct path.
4. Preserve atomic committed snapshot → stage → semantic verification → atomic publish.
5. Preserve recovery as separate from canonical Save.
6. Do not introduce ProcessSupervisor/render migration, PreviewEngine migration, WorkspaceRegistry migration, or UI redesign in M3.
7. Run focused roundtrip/save-failure/recovery Q0/Q1 evidence before reporting M3 PASS.
8. Do not proceed to M4 in the same turn unless explicitly instructed otherwise.

## Canonical References
- MASTER planning DOCX.
- STEP 00–11 final planning DOCX files.
- `docs/planning/STEP_11_WINDOWS_PORTABLE_BUILD_RELEASE_ROLLBACK_DAN_HANDOFF_FINAL.md`
- `docs/planning/STEP_11_ARTIFACT_INTEGRITY.txt`
- `docs/planning/PLANNING_ARTIFACTS_MANIFEST.md`
- prior STEP planning summaries/integrity files.
- `docs/governance/PROJECT_GOVERNANCE.md`
- `docs/governance/AI_HANDOFF.md`
