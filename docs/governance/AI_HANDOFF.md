# AI Handoff — V2 Full-Album-Maker

Before doing any work:

1. Confirm target repository is `inoriko920-dev/V2-Full-Album-Maker`.
2. Never write to `inoriko920-dev/Full-Album-Maker`.
3. Read governance/status/planning index and verify `PLANNING_ARTIFACTS_MANIFEST.md`.
4. Read MASTER + STEP 00–11 canonical final DOCX files in order before architecture decisions.
5. Preserve STEP 01 behavior contracts C-01..C-20.
6. Preserve STEP 02 adoption decisions.
7. Preserve STEP 03 architecture and M0..M9 migration order.
8. Preserve STEP 04 lifecycle/failure/recovery decisions D04-01..D04-15.
9. Preserve STEP 05 media/timeline/project decisions D05-01..D05-18.
10. Preserve STEP 06 render decisions D06-01..D06-20.
11. Preserve STEP 07 animation/Spectrum/parity decisions D07-01..D07-18.
12. Preserve STEP 08 feature/AI decisions D08-01..D08-20.
13. Preserve STEP 09 UI decisions D09-01..D09-20.
14. Preserve STEP 10 quality decisions D10-01..D10-20.
15. Preserve STEP 11 build/release/handoff decisions D11-01..D11-24.
16. Do not skip planning gates or redesign UI/workflow merely because another architecture looks cleaner.
17. Every implementation must remain reversible and test-protected.
18. If a required architecture decision conflicts with approved planning, STOP implementation and update the decision record first.

## Frozen Architecture Facts
- ProjectDocument + EditorController/EditorSession remain authoritative.
- Legacy Project is compatibility only and must not regain ownership.
- FFmpeg/ffprobe remain canonical render/probe infrastructure.
- Current production compiler semantics remain Step08 -> V13 -> S11 -> FFmpegV2; M4 facade parity is proven, but compiler consolidation remains deferred until a later approved cleanup gate.
- Manual/offline editing and rendering remain first-class.
- AI remains optional, sanitized, fail-closed, and locally executed through validated commands.
- Save/output publication remains atomic/transactional and recovery remains separate.
- Existing production UI/workflow and all 9 routes are preserved.
- Project schema v2 and TIMEBASE=240000 remain frozen during initial consolidation.

## Migration Rule
Wrap current proven behavior first. Route one path through the facade. Prove parity. Only then retire the old direct path. Never dual-write project state.

## Quality Rule
- Existing 115-file test/workflow baseline is the minimum regression floor.
- Q0 Developer -> Q1 Slice -> Q2 Integration -> Q3 Infrastructure -> Q4 Windows Artifact -> Q5 Release.
- Real FFmpeg remains mandatory for affected render/Spectrum paths.
- 200-song/~3-hour structural stress remains mandatory.
- Destructive boundaries require fault-injection evidence.
- Functional UI PASS and pixel-match PASS are separate claims.
- Declared Python >=3.11 support must be tested or revised explicitly.

## STEP 11 Release Rules
- First mature V2 stable target: v2.0.0 after implementation + Q5, not during planning.
- Separate build validation from stable publication.
- Stable release must target the exact Q5-approved candidate SHA.
- Publish the exact tested ZIP + SHA256SUMS; do not rebuild something merely similar.
- Release artifact identity = version + candidate commit + SHA-256.
- Q4/Q5 smoke uses the extracted final ZIP with no global Python/FFmpeg/API key.
- One release manifest should drive/verify repeated version/FFmpeg/font/dependency facts.
- THIRD_PARTY_NOTICES must match exact shipping pins; Q4 resolved the stale FFmpeg provenance and Q5 must preserve that exact manifest/notices alignment.
- Main/build validation must not automatically create an unapproved stable release; Q4 removed that behavior from the build workflow.
- Application binary rollback and project-data rollback are separate.
- Initial updates use side-by-side portable folders; auto-updater/installer are deferred.
- Old repo remains read-only permanently.

## PRE-CODING DOCUMENTATION GATE — PASS
The documentation hard block has been cleared.

Verified evidence:
1. MASTER + STEP00–11 canonical final DOCX files are present at `docs/planning/source-of-truth/`.
2. Canonical binary commit: `19de01219fbfd6aa1662785b298649c67a682da2`.
3. 13/13 Git blob identities match the exact local canonical bytes.
4. The local canonical bytes match all SHA-256 values in `docs/planning/PLANNING_ARTIFACTS_MANIFEST.md`.
5. Obsolete duplicate `STEP_07_ANIMATION_TRANSITION_SPECTRUM_DAN_PREVIEW_PARITY.docx` is absent.
6. Detailed evidence is recorded in `docs/planning/PRE_CODING_GATE_VERIFICATION.md`.

Implementation is active. M0/T1 through M9 are completed and gate-protected. The STEP 03 architecture migration sequence is complete.

## M0/T1 Implementation Result — PASS
- Branch: `impl-m0-t1-feature-parity`
- FeatureParityRegistry: 51 MUST KEEP behavior families / 11 areas.
- Registry evidence points to actual existing baseline test functions and workflows.
- Characterization map: `docs/implementation/M0_T1_FEATURE_PARITY_CHARACTERIZATION_MAP.md`.
- GitHub Actions run `37583231121`: Q0 compile PASS, 6 registry tests PASS, Q1 nine-workspace navigation smoke PASS.
- Existing runtime application files were not edited.

## M1 Implementation Result — PASS
- Branch: `impl-m1-app-kernel`
- AppKernel/CompositionRoot is now the explicit launch wiring boundary.
- Existing GUI and portable smoke are wrapped through `LegacyRuntimeAdapter`.
- The existing production installer chain remains in the same order.
- ProjectDocument + EditorController/EditorSession remain authoritative.
- No current service implementation or ownership was replaced.
- GitHub Actions run `37583919255`: Q0 compile PASS, 14 contract tests PASS, Q1 nine-workspace navigation PASS, Q1 authoritative-state/canonical-save shell PASS.

## M2 Implementation Result — PASS
- Branch: `impl-m2-task-lifecycle`
- Added typed lifecycle AppError/AppResult primitives.
- Added TaskToken/TaskScope/TaskSupervisor/TaskHandle.
- AppKernel owns one central TaskSupervisor and closes it boundedly on normal return or exception.
- Generation invalidation/cancellation/stale-result contracts are explicit.
- Seven legacy async owners are characterized in `task_owner_inventory.py`.
- Existing legacy async owner modules were not migrated or edited.
- GitHub Actions run `37585385248`: 27 M0/M1/M2 contracts PASS, 7 legacy async stale/cancel tests PASS, 3 render/close lifecycle tests PASS, 9-workspace characterization PASS, authoritative-state/canonical-save shell PASS.
- H3 ProcessSupervisor and H4 ApplicationLifecycleService remain future hardening work; they were not silently implemented here.

## M3 Implementation Result — PASS
- Branch: `impl-m3-persistence`
- Added ProjectPersistence and wired it through CompositionRoot/AppKernel.
- EditorWorkspace v2 open/save now routes through ProjectPersistence.
- STEP11 canonical compatibility Save and recovery write/clear/classification route through ProjectPersistence.
- Native v2 Save is stage -> semantic verify -> atomic publish.
- Recovery classifications: CORRUPT / STALE / SAME / NEWER / FOREIGN.
- Corrupt/foreign/stale recovery evidence is retained.
- Legacy v1 migration IDs are deterministic from canonical payload.
- GitHub Actions run `37588571955`: 37 M0–M3 contracts PASS, 8 baseline persistence tests PASS, 14 STEP11 persistence lifecycle/core tests PASS, production canonical Save PASS, nine-workspace characterization PASS.

## M4 Implementation Result — PASS
- Branch: `impl-m4-render-facade`
- Added AppKernel-owned `RenderEngine` as the canonical preflight/final-render facade.
- Production `RenderAsyncBridge` routes preflight and execution through RenderEngine and no longer directly constructs RenderExecutor.
- The existing STEP10 RenderExecutor remains the proven adapter; Step08 -> V13 -> S11 -> FFmpegV2 remains unchanged.
- Critical preflight, immutable snapshot, AUTO hardware runtime verification/software fallback, progress/cancel, ffprobe verification, and transactional publication are preserved.
- H3 ProcessSupervisor was not silently introduced; existing STEP10 process ownership remains in place.
- GitHub Actions run `37591981581`: 43 M0–M4/entrypoint tests passed (1 skipped), 38 STEP10 render parity tests passed, 21 render safety/lifecycle tests passed (9 skipped), 2 long-album structural stress tests passed, production canonical Save PASS, nine-workspace characterization PASS, and real-FFmpeg M4 job PASS with 2 tests.

## M5 Implementation Result — PASS
- Branch: `impl-m5-probe-preview-cache`
- Added AppKernel-owned `MediaProbeService`, `CacheManager`, and `PreviewEngine`.
- Media import/relink probe paths route through MediaProbeService while current FFprobe/FFmpeg/image/tag behavior remains the adapter.
- SourceFingerprint exposes F0/F1/F2/F3 tiers and never performs F3 full hashing automatically.
- Accurate Preview routes through PreviewEngine and still uses the current Step08 compiler semantics.
- Existing MediaPreviewCache generation/de-dup/stale guards remain in place behind PreviewEngine.
- Spectrum Accurate Preview and existing Spectrum/template-thumbnail cache roots route through the M5 facades without payload-format changes.
- Media-preview corrupt/missing/zero-byte/version-mismatch entries are disposable cache misses.
- No M6 Beat Analysis, M7 WorkspaceRegistry, UI redesign, schema bump, dependency, compiler, or release work was performed.
- GitHub Actions run `37594113013`: 50 M0–M5 contracts passed (2 skipped), 9 focused probe/preview/cache parity tests passed, 12 persistence/production-shell tests passed, 2 long-album structural stress tests passed, and real-FFmpeg M5 job PASS with 3 tests.
- Detailed records: `docs/implementation/M5_PROBE_PREVIEW_CACHE.md` and `docs/implementation/M5_EVIDENCE.md`.

## M6 Implementation Result — PASS
- Branch: `impl-m6-beat-analysis`
- Added AppKernel-owned `BeatAnalysisService` sharing the exact M2 TaskSupervisor and M5 CacheManager.
- BeatAnalysis is derived/cacheable data only and remains separate from authored BeatResponse.
- FFmpeg derives a compact low-rate amplitude envelope; deterministic detection operates on that derived data.
- No fake reactivity: silence/tool/decode failure yields no beat events and an honest non-reactive fallback.
- Source fingerprint + analyzer/config version protects cache identity; corrupt/stale cache is disposable.
- Async analysis uses TaskSupervisor/TaskScope generation invalidation and adds no private worker pool.
- Real-FFmpeg evidence proves pulse detection, silence fallback, and byte-identical source/master audio before/after analysis.
- Existing FFmpeg Spectrum/circular Spectrum and Accurate Preview/final render semantics remain unchanged and parity-tested.
- No M7 WorkspaceRegistry, UI redesign, schema bump, dependency, compiler, or release work was performed.
- GitHub Actions run `37595757999`: 58 M0–M6 contracts passed (4 skipped), 19 Beat/Spectrum parity tests passed (1 skipped), 7 Accurate Preview/render parity tests passed (1 skipped), 12 persistence/production-shell tests passed, 2 long-album structural stress tests passed, and real-FFmpeg M6 job PASS with 4 tests.
- Detailed records: `docs/implementation/M6_BEAT_ANALYSIS.md` and `docs/implementation/M6_EVIDENCE.md`.

## M7 Implementation Result — PASS
- Branch: `impl-m7-workspace-registry`
- Added AppKernel-owned, Qt-agnostic `WorkspaceRegistry` and `WorkspaceBundle` route composition boundary.
- FoundationShell is now the single direct `workspace_changed` subscriber and routes activation through WorkspaceRegistry.
- Home, Media, Album, Timeline, Visual, Template, Spectrum, AI Agent, and Render register their existing production surfaces through the registry in canonical order.
- Feature modules no longer access private `workspace_stack._index`; capture tooling also uses the public registry boundary.
- Existing route methods remain transitional adapters for M7 parity and are dispatched by the registry instead of owning signal subscriptions.
- Render remains the final migrated workspace route; the later STEP11 integration observer is not a workspace route owner.
- Full production route navigation remains read-only against authoritative ProjectDocument.
- No M8 bridge retirement, UI redesign, schema bump, dependency, compiler, or release work was performed.
- GitHub Actions run `37597489445`: 63 M0–M7 contracts passed (4 skipped), 42 nine-route functional UI tests passed, 13 production navigation/persistence tests passed, 23 responsive/shell regressions passed, 2 long-album structural stress tests passed, and real-FFmpeg M7 job PASS with 2 tests.
- Detailed records: `docs/implementation/M7_WORKSPACE_REGISTRY.md` and `docs/implementation/M7_EVIDENCE.md`.

## M8 Implementation Result — PASS
- Branch: `impl-m8-legacy-bridge-retirement`
- Physically removed three obsolete bridge modules: `media_feature_activation.py`, `album_restore_fix.py`, and `timeline_route_fix.py`.
- Removed their imports/installer calls from the production main chain.
- Media persisted-route coherence is now owned by M7 WorkspaceRegistry/WorkspaceStack; no replacement timer was introduced.
- Album's valid legacy active-audio compatibility invariant now lives directly in `album_feature.py`; a hidden dependency on the old bridge-injected helper was eliminated.
- Timeline's proven Ripple/Snap label and route-exit control behavior now lives directly in `timeline_feature_step05.py`; no global route wrapper remains.
- Explicit M8 tests prove persisted Media/Album/Timeline startup, Album legacy compatibility, Timeline route-fix behavior, and physical absence of retired modules.
- Bridges that still own unreplaced production behavior remain intentionally present.
- No M9 consolidation, UI redesign, schema bump, dependency, compiler, build, or release work was performed.
- GitHub Actions run `37598817830`: 68 M0–M8 contracts passed (4 skipped), 8 retirement-parity tests passed, 42 nine-route UI tests passed, 25 production navigation/persistence/render/preview tests passed (2 skipped), 28 responsive/lifecycle tests passed, 2 long-album structural stress tests passed, and real-FFmpeg M8 job PASS with 3 tests.
- Detailed records: `docs/implementation/M8_LEGACY_BRIDGE_RETIREMENT.md` and `docs/implementation/M8_EVIDENCE.md`.

## M9 Implementation Result — PASS
- Branch: `impl-m9-consolidation`
- Added `ProductionRuntimeInstaller` as the single ordered owner of the surviving production compatibility/presentation bootstrap.
- The exact 27-installer order from M8 is preserved and test-frozen.
- `main.py` now calls one `install_production_runtime()` boundary before the lazy v14 GUI import instead of wiring every installer independently.
- Repeated successful installation is idempotent; partial-failure retry resumes at the first incomplete installer without replaying completed global patches.
- M8-retained bridges remain because their production behavior is still unreplaced.
- No compiler rewrite, UI redesign, schema bump, dependency, Windows build, version bump, or release publication was performed.
- STEP 03 M0–M9 architecture migration is now complete.
- GitHub Actions run `37600034073`: 73 M0–M9 contracts passed (4 skipped), 13 bootstrap/retirement parity tests passed, 42 nine-route UI tests passed, 25 production navigation/persistence/render/preview tests passed (2 skipped), 29 responsive/lifecycle/entrypoint tests passed, 2 long-album structural stress tests passed, and real-FFmpeg M9 job PASS with 3 tests.
- Detailed records: `docs/implementation/M9_CONSOLIDATION.md` and `docs/implementation/M9_EVIDENCE.md`.

## Q2 Integration Quality Gate — PASS
- Branch: `quality-q2-integration`
- Current test inventory: 123 Python test files; STEP10 floor 115.
- Full pytest: 557 passed, 93 skipped, 0 failed.
- Cross-workspace/session/lifecycle evidence: 60 passed.
- M0–M9 ownership smoke: 72 passed, 4 skipped.
- Initial Q2 run exposed four real async-import compatibility regressions; tests were not weakened.
- Source fix restores the direct-window monkeypatchable probe surface through a compatibility MediaProbeService while production AppKernel windows retain the exact M5 MediaProbeService owner.
- Successful Actions run: `37601017717`.
- Detailed records: `docs/implementation/Q2_INTEGRATION_QUALITY_GATE.md` and `docs/implementation/Q2_EVIDENCE.md`.

## Q3 Infrastructure Quality Gate — PASS
- Branch: `quality-q3-infrastructure`
- Real Linux FFmpeg/ffprobe infrastructure matrix: 10 passed.
- Initial Linux matrix exposed unsupported `-/filter_complex` on Ubuntu FFmpeg 6.1.1; the unchanged test explicitly targets the pinned Windows FFmpeg and is carried forward to Q4.
- Fresh functional UI capture matrix: 9/9 workspaces PASS at 1672x941 with uploaded screenshots/reports.
- Pixel-match is NOT CLAIMED; exact golden binaries are not present in this branch and STEP10 treats functional UI and pixel-match as separate claims.
- 200-song/~3-hour structural gate: 2 passed.
- Same-runner performance vs Q2 final baseline: no regression >10%; all four measured deltas are between -0.61% and -1.73%.
- Python 3.11 full regression: 557 passed, 93 skipped.
- Q3 changes no production runtime source.
- Successful Actions run: `37602494015`.
- Detailed records: `docs/implementation/Q3_INFRASTRUCTURE_QUALITY_GATE.md` and `docs/implementation/Q3_EVIDENCE.md`.

## Q4 Windows Artifact Quality Gate — PASS
- Branch: `quality-q4-windows-artifact`
- Exact candidate SHA: `d2ce2ccac62cdcd8994a38251a5b547c8460421e`.
- Exact Actions run: `37615631835`.
- Exact Actions artifact ID/name: `11480755092` / `q4-windows-artifact-candidate`.
- Exact inner ZIP: `Full-Album-Maker-v2.0.0-Windows-Portable.zip`.
- Exact inner ZIP SHA-256: `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`.
- Exact inner ZIP bytes: `189554128`.
- Full Windows regression in artifact build: 651 passed, 0 failed.
- Pinned shipping Windows FFmpeg: `N-127142-g12b7b9891b-20261003`; Q3-carried `-/filter_complex` test PASS.
- Extracted ZIP smoke from Unicode/apostrophe path PASS with global Python/FFmpeg unavailable and API keys absent; bundled output verified audio+video.
- Secret scan, package pins, manifest/notices provenance, checksum, embedded capabilities/release manifest, licenses/fonts/FFmpeg assets all PASS.
- `build/release_manifest.json` is now the canonical release metadata source.
- `build-windows-portable.yml` is validation-only and cannot auto-publish stable releases.
- Q4 publication flag: false; no stable GitHub Release was created.
- Q4 workflow ignores docs-only pushes after artifact freeze; later documentation commits are not release candidates and must not replace the tested artifact.
- Detailed records: `docs/implementation/Q4_WINDOWS_ARTIFACT_QUALITY_GATE.md` and `docs/implementation/Q4_EVIDENCE.md`.

## Q5 Release Quality Gate — PASS
- Stable release: `v2.0.0`.
- Successful Q5 Actions run: `37617534800`.
- Stable release ID: `405709866`.
- Exact tag target / Q4 candidate: `d2ce2ccac62cdcd8994a38251a5b547c8460421e`.
- Published portable ZIP: `Full-Album-Maker-v2.0.0-Windows-Portable.zip`.
- Published ZIP SHA-256: `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`.
- Published ZIP bytes: `189554128`.
- GitHub release asset digest matches the frozen Q4 SHA-256.
- Q5 did not rebuild the ZIP; it downloaded Q4 artifact ID `11480755092`, verified it, smoke-tested the exact ZIP, published it, then downloaded it again and re-verified the same digest.
- `SHA256SUMS.txt` is published and verified.
- Release is stable: draft=false, prerelease=false.
- Rollback stable `v1.5.0` was verified.
- Q5 evidence artifact ID: `11481041761`.
- Detailed records: `docs/implementation/Q5_RELEASE_QUALITY_GATE.md` and `docs/implementation/Q5_EVIDENCE.md`.

## Next Work
- No STEP 00–11 or Q2–Q5 gate remains pending.
- Stable v2.0.0 is published from the frozen Q4 candidate.
- Do not rebuild or replace v2.0.0 assets in later maintenance work.
- Use v1.5.0 as the verified previous stable rollback tag.
- Any future change starts a new explicit maintenance/feature cycle and requires its own version/release evidence.

## Current Handoff
- Phase: IMPLEMENTATION
- Completed planning: STEP 00–11 PASS
- Pre-coding documentation gate: PASS
- M0/T1 FeatureParityRegistry + characterization: PASS
- M1 AppKernel/CompositionRoot: PASS
- M2 Task Lifecycle/TaskSupervisor/TaskScope: PASS
- M3 ProjectPersistence: PASS
- M4 RenderEngine Facade: PASS
- M5 MediaProbeService / PreviewEngine / CacheManager: PASS
- M6 BeatAnalysisService: PASS
- M7 WorkspaceRegistry: PASS
- M8 Legacy Bridge Retirement: PASS
- M9 Consolidation: PASS
- STEP 03 M0–M9 architecture migration: COMPLETE
- Q2 Integration Quality Gate: PASS
- Q3 Infrastructure Quality Gate: PASS
- Q4 Windows Artifact Quality Gate: PASS
- Q5 Release Quality Gate: PASS
- Stable v2.0.0: PUBLISHED
- Stable tag target: d2ce2ccac62cdcd8994a38251a5b547c8460421e
- Stable portable ZIP SHA-256: 4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad
- Previous stable rollback tag: v1.5.0
- Approved STEP 00–11 + Q2–Q5 workflow: COMPLETE
- Next action: none until a new explicit user instruction starts maintenance or a new development cycle.


## October 8, 2026 — v2.0.1 patch maintenance (newer than historic v2.0.0 Q5)

The historic references above to Q5 being complete apply to the **published v2.0.0 release only**. The current maintenance patch is separate:

- v2.0.1 candidate preparation PR #32: merged, main Windows validation PASS (run `37724111066`).
- v2.0.1 Q4 Windows artifact workflow PR #33: merged, exact Q4 run `37724287381` PASS (760 regressions plus separate pinned FFmpeg capability test).
- Exact frozen candidate commit: `35a8c195469d49d7f7938b31761ceb17c4c720e0` (not the later squash-merge SHA).
- Q4 Actions artifact ID: `11527152731` (name `q4-v2.0.1-windows-artifact-candidate`).
- Exact portable ZIP: `Full-Album-Maker-v2.0.1-Windows-Portable.zip`; 189598786 bytes; SHA-256 `6c97461ee3472973fc9b7950952287ae5aab9ffe2dffbe6a1fb0c236353d4a5d`.
- **v2.0.1 Q4: PASS / FROZEN. v2.0.1 Q5: NOT STARTED. v2.0.1 stable: NOT PUBLISHED.**
- Authoritative patch Q4 evidence: `docs/implementation/Q4_V2_0_1_EVIDENCE.md`; gate plan: `docs/release/V2_0_1_GATE_PLAN.md`.
- Next gate: explicit v2.0.1 Q5 **without rebuild**. Download and verify the exact Q4 artifact; never substitute a new build, change the old v2.0.0 release, or use its hardcoded publication workflow.


## October 8, 2026 — v2.0.1 maintenance release COMPLETED

This supersedes the earlier v2.0.1 "Q5 NOT STARTED" handoff entries **for v2.0.1**. Historical v2.0.0 Q4/Q5 evidence remains unchanged.

- **Q4 v2.0.1:** PASS / frozen on source SHA `35a8c195469d49d7f7938b31761ceb17c4c720e0`; run `37724287381`; artifact ID `11527152731`; exact ZIP SHA-256 `6c97461ee3472973fc9b7950952287ae5aab9ffe2dffbe6a1fb0c236353d4a5d` (189598786 bytes).
- **Q5 v2.0.1:** PASS / PUBLISHED; run `37725395630`; control SHA `aea9fbfc8f1c4b184145e118836a61aac3b3beb0`; evidence artifact ID `11527089380`.
- **Stable v2.0.1:** release ID `406399261`, published 2026-10-08 11:01:03 WIB; tag `v2.0.1` points to exact Q4 candidate `35a8c195469d49d7f7938b31761ceb17c4c720e0`.
- Exact published `Full-Album-Maker-v2.0.1-Windows-Portable.zip` is byte-identical to Q4 and was re-downloaded; no rebuild in Q5.
- Latest stable: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.1
- Detailed authoritative publication proof: `docs/implementation/Q5_V2_0_1_EVIDENCE.md`.
- Previous stable v2.0.0 was preserved, available for side-by-side rollback; old source `inoriko920-dev/Full-Album-Maker` remains unmodified.
- **Next work:** only a new user-directed post-release maintenance or feature wave, with its own branch, CI and new semantic version if a changed binary is published.


## October 8, 2026 — v2.0.2 patch candidate Q4 frozen (Q5 pending)

This supersedes older "v2.0.2 Q4 not started" statements. `v2.0.1` remains the last **published stable**; its historical Q4/Q5 evidence is immutable.

- PR #37: retry transient sidecar read/lock failures without quarantining healthy metadata, merged.
- PR #39: skip NTFS directory junctions during recursive media scan, merged.
- PR #40: v2.0.2 candidate identity merged; `main` Windows run `37731780154` PASS.
- PR #41: v2.0.2 Q4 workflow merged; exact Windows Q4 run `37732261424` PASS (769 pytest + 1 FFmpeg filter test).
- **Frozen exact Q4 candidate SHA:** `2678b9f93364334c7eaf9ebad9ef7e079533716f` (never substitute squash commit).
- **Q4 Actions artifact ID:** `11530243260`, name `q4-v2.0.2-windows-artifact-candidate`.
- **Frozen inner ZIP:** `Full-Album-Maker-v2.0.2-Windows-Portable.zip`, 189599767 bytes, SHA-256 `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64`.
- Authoritative Q4 proof: `docs/implementation/Q4_V2_0_2_EVIDENCE.md`.
- CI after PR #41 merge: `37732736075`, must be checked before Q5 execution.
- **Q4: PASS/FROZEN. Q5: NOT STARTED. Stable v2.0.2: NOT PUBLISHED.** Current published stable is v2.0.1.
- Next: verify post-merge `main` CI, build v2.0.2 Q5-specific no-rebuild control, download/verify **this exact** frozen Q4 artifact, run offline smoke, publish only after Q5 gate PASS, re-download published ZIP and validate checksum/tag.


## October 8, 2026 — v2.0.2 stable release COMPLETED (latest)

This section supersedes the earlier v2.0.2 "Q5 NOT STARTED" notices. Historical v2.0.0/v2.0.1 evidence must remain unchanged.

- PR #37 and #39: metadata read/lock retry safety and Windows junction-scan loop fixes merged, tested.
- PR #40: v2.0.2 candidate prepared and merged; `main` CI `37731780154` PASS.
- PR #41: Q4 workflow merged; Q4 source SHA `2678b9f93364334c7eaf9ebad9ef7e079533716f`; Windows artifact run `37732261424` PASS (769 tests plus 1 pinned FFmpeg test).
- Q4 frozen artifact ID `11530243260`; portable ZIP `Full-Album-Maker-v2.0.2-Windows-Portable.zip`; exactly `189599767` bytes; SHA-256 `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64`.
- **Q5 v2.0.2 PASS/PUBLISHED** on run `37733519371`, control SHA `46b4970bc342a267bab36231aafcd323c0a073bc`.
- GitHub Release ID `406458763`, published 2026-10-08 **12:40:50 WIB**. Tag `v2.0.2` directly targets exact Q4 SHA `2678b9f93364334c7eaf9ebad9ef7e079533716f`.
- Published ZIP was independently re-downloaded and verified; no Q5 rebuild.
- Latest release: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.2
- Authoritative Q4 evidence: `docs/implementation/Q4_V2_0_2_EVIDENCE.md`; Q5 evidence: `docs/implementation/Q5_V2_0_2_EVIDENCE.md`.
- v2.0.1 and v2.0.0 remain immutable historical stable rollback choices; original `inoriko920-dev/Full-Album-Maker` remains untouched.
- **Current phase:** post-release maintenance. Future changed binaries require a new patch/minor version and their own Windows Q4/Q5 gates.
