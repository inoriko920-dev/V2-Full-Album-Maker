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
- THIRD_PARTY_NOTICES must match exact shipping pins; current stale FFmpeg notice is a future RC blocker.
- Main push must not automatically create an unapproved stable release.
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

Implementation is active. M0/T1 through M6 are completed and gate-protected.

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

## Next Work
- M7: Workspace Registry only.
- Re-read STEP 03 and STEP 09 canonical decisions before implementation.
- Replace runtime workspace/patch ownership one route at a time; preserve all 9 production routes and current UI/workflow.
- Keep ProjectDocument/EditorSession and the M2–M6 service boundaries authoritative.
- Do not proceed to M8 Legacy Bridge Retirement until M7 gate PASS.

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
- Next operational action: M7 Workspace Registry only; then report gate before M8.
