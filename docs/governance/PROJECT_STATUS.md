# V2 Full-Album-Maker — Project Status

## Current Phase
IMPLEMENTATION — M4 RENDER FACADE

## Current STEP
M4 — RenderEngine Facade — PASS

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
M0/T1, M1, M2, M3, and M4 are implemented and validated.

M3 result:
- one `ProjectPersistence` facade now owns ProjectDocument save/load/recovery contracts;
- native v2 Save uses clone -> validate -> same-directory stage -> semantic read-back verify -> atomic publish;
- STEP11 compatibility-envelope Save is routed through ProjectPersistence while preserving the proven writer;
- editor-v2 open/save is routed through ProjectPersistence;
- recovery is classified as CORRUPT / STALE / SAME / NEWER / FOREIGN;
- corrupt/foreign/stale recovery evidence is not silently deleted;
- v1 migration IDs are deterministic for the same canonical legacy payload;
- ProjectPersistence is wired through CompositionRoot/AppKernel;
- ProjectDocument schema v2 and TIMEBASE=240000 remain unchanged.

Validated on Actions run `37588571955`: Q0 compile PASS, 37 M0–M3 contract tests PASS, 8 baseline atomic/project persistence tests PASS, 14 STEP11 persistence lifecycle/integration tests PASS, production canonical Save PASS, and nine-workspace read-only navigation PASS.

No ProcessSupervisor/H3 replacement, Preview/Cache M5, Beat Analysis M6, WorkspaceRegistry M7, UI redesign, schema bump, dependency change, or release work was performed.

M4 result:
- one AppKernel-owned `RenderEngine` is now the canonical facade for production render preflight and final execution;
- `RenderAsyncBridge` no longer imports or constructs `RenderExecutor` directly;
- the facade delegates to the existing STEP10 `RenderExecutor` and preserves the Step08 -> V13 -> S11 -> FFmpegV2 compiler chain;
- immutable snapshot, critical preflight, AUTO hardware runtime verification/software fallback, progress/cancel, ffprobe verification, and transactional publish behavior remain intact;
- a facade-level active-attempt guard rejects overlapping starts;
- the AppKernel-to-legacy-window handoff uses a bounded ContextVar migration bridge so the production Qt bridge captures the exact kernel-owned engine;
- H3 ProcessSupervisor remains explicitly deferred.

Validated implementation candidate `5f7a428945102f08197bdbe91d7036fbff91c750` on Actions run `37591981581`: Q0 compile PASS; 43 M0–M4/entrypoint tests passed (1 skipped); 38 STEP10 render parity tests passed; 21 render safety/lifecycle tests passed (9 skipped); 2 long-album structural stress tests passed; production canonical Save PASS; nine-workspace read-only navigation PASS; real-FFmpeg M4 job PASS with 2 tests.

## Next Operational Step
M4 is PASS. On the next explicit implementation turn:
1. Start **M5 — Probe / Preview / Cache** only.
2. Introduce the approved MediaProbeService / PreviewEngine / CacheManager facades around current proven implementations before replacing ownership.
3. Preserve Accurate Preview composition semantics and current cache-generation/stale-result protections.
4. Do not start M6 Beat Analysis, M7 Workspace Registry, UI redesign, schema bump, dependency/release work in M5.
5. Run focused preview/probe/cache parity and affected real-FFmpeg evidence before reporting M5 PASS.
6. Do not proceed to M6 in the same turn unless explicitly instructed otherwise.

## Canonical References
- MASTER planning DOCX.
- STEP 00–11 final planning DOCX files.
- `docs/planning/STEP_11_WINDOWS_PORTABLE_BUILD_RELEASE_ROLLBACK_DAN_HANDOFF_FINAL.md`
- `docs/planning/STEP_11_ARTIFACT_INTEGRITY.txt`
- `docs/planning/PLANNING_ARTIFACTS_MANIFEST.md`
- prior STEP planning summaries/integrity files.
- `docs/governance/PROJECT_GOVERNANCE.md`
- `docs/governance/AI_HANDOFF.md`
