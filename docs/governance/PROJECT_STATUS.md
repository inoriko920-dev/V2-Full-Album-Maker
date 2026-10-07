# V2 Full-Album-Maker — Project Status

## Current Phase
RELEASE — Q5 STABLE

## Current STEP
Q5 — Release Quality Gate — PASS

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
- The exact Q4 Windows candidate is version v2.0.0, but stable publication remains blocked until Q5 PASS.
- Stable publication must be explicit from the Q4-approved candidate SHA; main/build validation must not auto-publish an unapproved stable release.
- Exact tested ZIP must be the published ZIP and is identified by semantic version + candidate commit + SHA-256.
- Windows portable remains the primary distribution model: Python 3.12.10 release runtime, pinned dependencies, pinned FFmpeg digest, pinned font, PyInstaller onedir.
- Extracted-ZIP smoke must run in Unicode/apostrophe path without global Python, global FFmpeg, or API keys and must verify audio+video output.
- One canonical release manifest should prevent drift between workflow/build script/CAPABILITIES/notices.
- Q4 resolved the stale THIRD_PARTY_NOTICES FFmpeg provenance and aligned it with the canonical release manifest/shipping pin.
- Q4 removed stable-release-on-main behavior from the build workflow; the old STEP12 hardcoded ancestry remains a Q5 publication-workflow blocker and must not be used to rebuild or bless another artifact.
- Application rollback and project-data rollback are separate contracts.
- Initial updates use side-by-side portable folders; auto-updater/installer remain deferred.
- Old Full-Album-Maker repository remains permanently read-only.

## Planning Status
STEP 00–11 planning is COMPLETE.

## Coding Status
M0/T1 through M9 are implemented and validated. Q2, Q3, Q4, and Q5 Quality Gates are PASS. Full Album Maker v2.0.0 stable is published.

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

M9 result:
- added one explicit `ProductionRuntimeInstaller` and exact 27-installer manifest as the single owner of the surviving compatibility/presentation bootstrap order;
- `main.py` no longer imports/calls individual production installers and now invokes one `install_production_runtime()` boundary before the lazy v14 GUI import;
- exact installer order remains unchanged from the M8 production chain;
- installer completion is tracked per entry so repeated successful calls are idempotent and same-process retry after a partial failure resumes from the first incomplete installer;
- M8-retained production bridges remain present because they still own real behavior;
- ProjectDocument schema v2, TIMEBASE=240000, all nine routes, M2–M8 service ownership, render compiler semantics, UI design, dependencies, and release behavior remain unchanged;
- STEP 03 architecture migration sequence M0–M9 is now fully implemented and gate-protected;
- Q2/Q3/Q4/Q5 quality/release promotion was not started.

Validated candidate `4a9a4b2f91b0dd81b749d02fd356c00d6b14b817` on Actions run `37600034073`: Q0 compile PASS; 73 M0–M9 contract tests passed (4 skipped); 13 bootstrap/retirement parity tests passed; 42 nine-route UI tests passed; 25 production navigation/persistence/render/preview tests passed (2 skipped); 29 responsive/lifecycle/entrypoint tests passed; 2 long-album structural stress tests passed; real-FFmpeg M9 job PASS with 3 tests.

Q2 result:
- current regression inventory contains 123 Python test files, above the STEP10 minimum floor of 115;
- full repository pytest is green: 557 passed, 93 skipped, 0 failed;
- explicit cross-workspace/session/lifecycle integration evidence is green: 60 passed;
- M0–M9 ownership smoke remains green: 72 passed, 4 skipped;
- initial Q2 full-suite run exposed four async-import compatibility regressions caused by disappearance of the legacy direct-window `async_import.probe_duration` patch surface;
- the regression was fixed in source with a bounded legacy/direct-window MediaProbeService compatibility adapter while AppKernel production windows still use the exact M5-owned MediaProbeService;
- no tests were deleted or weakened to bless the regression;
- Q3 infrastructure, Q4 Windows artifact, and Q5 release work were not started.

Validated Q2 candidate `98a8f096990f1135989997f4047340c3b5bbb270` on Actions run `37601017717`: 123-file inventory PASS; full pytest 557 passed / 93 skipped; cross-workspace/session/lifecycle 60 passed; M0–M9 ownership smoke 72 passed / 4 skipped.

Q3 result:
- real Linux FFmpeg/ffprobe infrastructure matrix is green: 10 passed;
- the first Q3 run correctly exposed that Ubuntu FFmpeg 6.1.1 does not support `-/filter_complex`; that test explicitly targets the pinned Windows FFmpeg and remains required for Q4 rather than being weakened or deleted;
- deterministic functional UI capture matrix is green for all nine production workspaces at 1672x941 with per-route JSON reports and uploaded evidence;
- pixel-match is explicitly NOT CLAIMED because exact golden binaries are not checked into this branch and STEP10 separates functional UI PASS from pixel-match PASS;
- 200-song/~3-hour Packed and Free structural tests pass;
- same-runner performance comparison against Q2 final head shows no >10% regression: Packed resolve -1.19%, Free resolve -0.61%, Packed compile -1.73%, Free compile -0.87%;
- Python 3.11 full pytest is green: 557 passed, 93 skipped;
- Q3 changes no production runtime source; only the Q3 workflow and benchmark runner were added;
- Q4 Windows Artifact and Q5 Release were not started.

Validated Q3 candidate `af98388eeb2c0eecb84bfe1cdbd44fdcad6d1385` on Actions run `37602494015`: real FFmpeg 10 passed; UI capture matrix 9/9 PASS; structural stress 2 passed; performance comparator PASS with no >10% regression; Python 3.11 full suite 557 passed / 93 skipped.

Q4 result:
- v2.0.0 candidate version is aligned across package metadata, release manifest, capabilities, and release notes;
- `build/release_manifest.json` is the canonical source for Windows Python, pip/packages, FFmpeg asset/digest, Noto Sans commit, and artifact naming;
- stale THIRD_PARTY_NOTICES FFmpeg provenance was corrected to the exact shipping pin;
- build-windows-portable is validation-only with `contents: read` and no automatic GitHub Release publication;
- full Windows regression during exact candidate build: 651 passed, 0 failed;
- PyInstaller onedir portable build PASS;
- exact extracted ZIP smoke PASS from Unicode/apostrophe path without global Python, global FFmpeg, Gemini API key, or Google API key;
- smoke verified bundled real render + ffprobe audio/video output and GUI v2.0.0 identity;
- exact pinned Windows FFmpeg `N-127142-g12b7b9891b-20261003` passed the Q3-carried `-/filter_complex` capability test;
- secret scan, package-lock/manifest alignment, notice/provenance alignment, embedded release manifest/capabilities, and ZIP checksum gates PASS;
- no stable GitHub Release was published.

Exact Q4 artifact identity:
- version: `2.0.0`
- candidate SHA: `d2ce2ccac62cdcd8994a38251a5b547c8460421e`
- Actions run: `37615631835`
- Actions artifact ID: `11480755092`
- artifact name: `q4-windows-artifact-candidate`
- inner ZIP: `Full-Album-Maker-v2.0.0-Windows-Portable.zip`
- inner ZIP bytes: `189554128`
- inner ZIP SHA-256: `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`
- shipping FFmpeg ZIP SHA-256: `a885f564dee2b60f69ab866c6c89b96ae531fc2ee1f24ff8b5b1a6d29960a96b`

The Q4 workflow ignores documentation-only pushes after candidate freeze so governance/evidence commits cannot generate a replacement artifact. Q5 must publish the exact tested inner ZIP above without rebuilding it.

Q5 result:
- successful workflow run: `37617534800`;
- stable GitHub Release: `v2.0.0`;
- release ID: `405709866`;
- published at: `2026-10-07T11:57:27Z`;
- tag target is the exact Q4 candidate `d2ce2ccac62cdcd8994a38251a5b547c8460421e`;
- published ZIP is `Full-Album-Maker-v2.0.0-Windows-Portable.zip`, 189554128 bytes;
- published ZIP SHA-256 is exactly `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`;
- GitHub release asset digest independently reports the same SHA-256;
- Q5 re-downloaded the published asset and re-hashed it successfully;
- `SHA256SUMS.txt` was also published and verified;
- release is stable (not draft, not prerelease);
- rollback stable tag `v1.5.0` was verified before publication;
- no rebuild occurred in Q5;
- Q5 evidence artifact ID `11481041761` was uploaded.


## Next Operational Step
Q5 is PASS. The approved STEP 00–11 workflow and Q2–Q5 quality sequence are complete.

No additional release/build gate is pending. Further work must begin only from a new explicit user instruction, such as post-release bug fixing, v2.0.x maintenance, main-branch integration, or a new feature cycle.

Stable release:
- `v2.0.0`
- exact candidate: `d2ce2ccac62cdcd8994a38251a5b547c8460421e`
- exact ZIP SHA-256: `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`
- rollback stable: `v1.5.0`

## Canonical References
- MASTER planning DOCX.
- STEP 00–11 final planning DOCX files.
- `docs/planning/STEP_11_WINDOWS_PORTABLE_BUILD_RELEASE_ROLLBACK_DAN_HANDOFF_FINAL.md`
- `docs/planning/STEP_11_ARTIFACT_INTEGRITY.txt`
- `docs/planning/PLANNING_ARTIFACTS_MANIFEST.md`
- prior STEP planning summaries/integrity files.
- `docs/governance/PROJECT_GOVERNANCE.md`
- `docs/governance/AI_HANDOFF.md`
