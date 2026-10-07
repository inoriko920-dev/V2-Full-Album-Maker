# V2 Full-Album-Maker — Project Status

## Current Phase
IMPLEMENTATION — M8 LEGACY BRIDGE RETIREMENT

## Current STEP
M8 — Legacy Bridge Retirement — PASS

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
M0/T1, M1, M2, M3, M4, M5, M6, M7, and M8 are implemented and validated.

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

M5 result:
- AppKernel/CompositionRoot now owns one `MediaProbeService`, one `CacheManager`, and one `PreviewEngine`;
- media import/relink probing routes through MediaProbeService while current ffprobe/FFmpeg/image/tag behavior remains the adapter;
- `SourceFingerprint` formalizes F0/F1/F2/F3 tiers without automatic full-file hashing;
- Accurate Preview routes through PreviewEngine and still delegates to the existing Step08 compiler path;
- Media and decoded-video preview queues are created through PreviewEngine while existing generation/stale-result guards remain intact;
- CacheManager centralizes namespace/version/root/eviction policy while existing payload formats and existing media-preview/Spectrum/template-thumbnail roots remain unchanged;
- corrupt, missing, zero-byte, or version-mismatched media-preview cache entries are disposable misses and are regenerated;
- Spectrum Accurate Preview/default cache root and template-thumbnail default cache root now route through the M5 facades;
- ProjectDocument schema v2, TIMEBASE=240000, timeline semantics, UI, render compiler chain, dependencies, and release behavior remain unchanged;
- M6 Beat Analysis and M7 WorkspaceRegistry were not started.

Validated runtime candidate `6aa2a14a3bb52d0b598cba19526c3b99191adedd` on Actions run `37594113013`: Q0 compile PASS; 50 M0–M5 contract tests passed (2 skipped); 9 focused probe/preview/cache parity tests passed; 12 persistence/production-shell tests passed; 2 long-album structural stress tests passed; real-FFmpeg M5 job PASS with 3 tests.

M6 result:
- AppKernel/CompositionRoot now owns one `BeatAnalysisService` sharing the exact M2 TaskSupervisor and M5 CacheManager;
- derived BeatAnalysis remains separate from authored BeatResponse and is never ProjectDocument truth;
- default FFmpeg adapter derives a low-rate mono amplitude envelope and does not alter source/master audio;
- deterministic transient detection produces bounded beat events from real envelope evidence only;
- silence and decoder/tool failures remain honest non-reactive states with no fake beat events;
- beat-analysis cache identity includes source fingerprint, namespace version, analyzer version, sample rate, and detector timing parameters;
- corrupt/stale beat cache is a disposable miss; valid analysis remains usable even if cache publication fails;
- async analysis routes through TaskSupervisor/TaskScope with generation invalidation and no private worker pool;
- existing FFmpeg Spectrum, circular Spectrum, Accurate Preview, final render compiler chain, ProjectDocument schema v2, TIMEBASE=240000, UI, dependencies, and release behavior remain unchanged;
- M7 WorkspaceRegistry was not started.

Validated candidate `a0d5a88a372f373c852c40242cea82511c1fd3dc` on Actions run `37595757999`: Q0 compile PASS; 58 M0–M6 contract tests passed (4 skipped); 19 Beat/Spectrum parity tests passed (1 skipped); 7 Accurate Preview/render parity tests passed (1 skipped); 12 persistence/production-shell tests passed; 2 long-album structural stress tests passed; real-FFmpeg M6 job PASS with 4 tests.

M7 result:
- AppKernel/CompositionRoot now owns one Qt-agnostic `WorkspaceRegistry`;
- FoundationShell captures the exact bound registry and provides the single Qt WorkspaceStack replacement adapter;
- all nine production routes are registered in canonical order: home, media, album, timeline, visual, template, spectrum, ai_agent, render;
- route modules no longer subscribe directly to `workspace_changed`; the registry is the single route dispatch owner;
- non-shell modules no longer access the private `workspace_stack._index`;
- current route callbacks remain transitional adapters and keep existing context/inspector/timeline hide/show behavior for parity;
- Render remains the last migrated workspace route;
- full production navigation remains read-only against authoritative ProjectDocument;
- UI/workflow, ProjectDocument schema v2, TIMEBASE=240000, M2–M6 service ownership, compiler chain, dependencies, and release behavior remain unchanged;
- M8 Legacy Bridge Retirement was not started.

Validated candidate `3e0af4f8b5c7a344a481b02f8805286209182b6f` on Actions run `37597489445`: Q0 compile PASS; 63 M0–M7 contract tests passed (4 skipped); 42 nine-route functional UI tests passed; 13 production navigation/persistence tests passed; 23 responsive/shell regression tests passed; 2 long-album structural stress tests passed; real-FFmpeg M7 job PASS with 2 tests.

M8 result:
- three proven obsolete bridge modules were physically removed: `media_feature_activation.py`, `album_restore_fix.py`, and `timeline_route_fix.py`;
- their imports and installer calls were removed from the production `main.py` chain;
- Media no longer needs a queued route-reactivation guard because M7 WorkspaceRegistry/WorkspaceStack now preserves active route/widget coherence;
- Album legacy active-audio sanitization moved into the canonical `album_feature.py` owner, and a hidden dependency on the old bridge-injected helper name was removed;
- Timeline's proven Ripple/Snap labels and route-exit placeholder-control behavior moved into `timeline_feature_step05.py` instead of wrapping the route method globally;
- production tests prove persisted Media/Album/Timeline startup routes remain coherent without the reactivation wrappers;
- bridges that still own unreplaced behavior were intentionally retained: media layout, timeline completion, visual timeline completion, STEP11 integration completion, and render queue presentation;
- ProjectDocument schema v2, TIMEBASE=240000, all nine routes, M2–M7 service ownership, compiler chain, UI design, dependencies, and release behavior remain unchanged;
- M9 Consolidation was not started.

Validated candidate `006d64eff4a0793162cb759a8cd77476a1a9c704` on Actions run `37598817830`: Q0 compile PASS; 68 M0–M8 contract tests passed (4 skipped); 8 retired-bridge parity tests passed; 42 nine-route UI tests passed; 25 production navigation/persistence/render/preview tests passed (2 skipped); 28 responsive/lifecycle tests passed; 2 long-album structural stress tests passed; real-FFmpeg M8 job PASS with 3 tests.

## Next Operational Step
M8 is PASS. On the next explicit implementation turn:
1. Start **M9 — Consolidation** only.
2. Re-read STEP 03 consolidation order plus M8 retirement evidence before combining or simplifying surviving runtime paths.
3. Consolidate only already-proven ownership boundaries; do not redesign the UI, project schema, or release model.
4. Preserve ProjectDocument/EditorSession authority, all nine routes, and M2–M8 gate evidence.
5. Run focused ownership, production navigation, persistence, render/preview, UI, lifecycle, and stress evidence before reporting M9 PASS.
6. Do not begin Windows Q4/Q5 release work in the same turn unless the documented implementation sequence explicitly reaches that gate and the user separately continues.

## Canonical References
- MASTER planning DOCX.
- STEP 00–11 final planning DOCX files.
- `docs/planning/STEP_11_WINDOWS_PORTABLE_BUILD_RELEASE_ROLLBACK_DAN_HANDOFF_FINAL.md`
- `docs/planning/STEP_11_ARTIFACT_INTEGRITY.txt`
- `docs/planning/PLANNING_ARTIFACTS_MANIFEST.md`
- prior STEP planning summaries/integrity files.
- `docs/governance/PROJECT_GOVERNANCE.md`
- `docs/governance/AI_HANDOFF.md`
