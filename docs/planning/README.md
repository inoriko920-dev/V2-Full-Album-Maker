# Planning Source-of-Truth — V2 Full-Album-Maker

## Planning Sequence
- MASTER — overall development plan
- STEP 00 — Baseline Copy, Governance, Source-of-Truth — PASS
- STEP 01 — Audit Repo Lama dan Kontrak Perilaku — PASS
- STEP 02 — Riset Pondasi Matang, Lisensi, Keputusan Adopsi — PASS
- STEP 03 — Target Architecture V2 dan Strategi Migrasi Bertahap — PASS
- STEP 04 — Hardening Stabilitas, Lifecycle, Error Handling, Recovery — PASS
- STEP 05 — Media, Preview, Cache, Timeline, Project Data — PASS
- STEP 06 — Render Engine, Processing Pipeline, Long-Album Reliability — PASS
- STEP 07 — Animation, Transition, Spectrum, Beat-Reactive, Preview/Render Parity — PASS
- STEP 08 — Feature Parity, Enhancement, AI Agent Reliability — PASS
- STEP 09 — UI Preservation, Responsiveness, Integration Contract — PASS
- STEP 10 — Testing, Regression, Stress, Benchmark, Quality Gate — PASS
- STEP 11 — Windows Portable Build, Release, Rollback, Final Handoff — NEXT

## Current State
STEP 10 is PASS. STEP 11 is next. Coding remains blocked.

## STEP 03 Architecture Summary
Target architecture is layered/ports-and-adapters with one AppKernel/CompositionRoot. Existing behavior is wrapped before replacement. Migration order is M0..M9 and every slice must be rollback-capable.

## STEP 04 Hardening Summary
V2 centralizes async/process ownership, stable project-token/generation guards, deterministic close/project switching, verification-first publication, explicit recovery classification, bounded shutdown, and fault-injection evidence.

## STEP 05 Media / Preview / Timeline / Data Summary
Canonical media identity is ProjectDocument UUID asset_id. ffprobe is the initial normalized probe adapter. Relink preserves identity. Accurate Preview is the parity oracle. Cache is disposable. Timeline stays at 240000 integer ticks/sec with frozen Packed/Free semantics. Project schema v2 remains frozen.

## STEP 06 Render Summary
One RenderEngine path owns final rendering; immutable RenderSnapshot + RenderPlan bind each job to a frozen revision. Critical preflight, runtime encoder verification, graph externalization, ffprobe verification, transactional publication, crash-interrupted retry semantics, and long-album one-pass reliability are mandatory.

## STEP 07 Animation Summary
- Generic animation lives in versioned Layer.animation v1.
- Typed property registry + deterministic keyframe evaluator.
- BeatAnalysis derived data is separate from authored BeatResponse.
- Existing FFmpeg Spectrum remains canonical.
- Visual transition never silently alters audio timing/crossfade.
- Accurate Preview vs Final Render golden parity is mandatory for new effect families.
- Non-reactive fallback is required when beat analysis is unavailable.
- Preset catalog expands only after a small animation core is proven.

## STEP 08 Feature / AI Summary
- No user-facing baseline feature removal is authorized.
- Manual editor remains complete and authoritative.
- AI provider is planner-only; local registry + dry-run + EditorController own mutations.
- Current STEP09 safe actions/permissions remain parity-protected.
- Animation AI actions are added only after animation command contracts exist.
- AI filesystem path operations and direct render remain deferred.
- Ambiguity/stale revision/context/permission failure produces zero mutation.
- One plan = one revision + one Undo.
- Gemini 100-key pool reliability remains protected.

## STEP 09 UI Summary
- Existing production UI/workflow is preserved; V2 is not a redesign.
- All 9 workspace routes and shell mental model remain stable.
- WorkspaceRegistry/WorkspaceBundle replaces patch ownership route-by-route.
- Heavy process/network/media/analysis work is forbidden on the UI thread.
- Required responsive evidence: 1672/100%, 1366/100%, 125%, 150%.
- Current production UI is the migration no-regression baseline.
- Frozen canonical goldens remain immutable references.
- No new UI-image prompt is required for this preservation scope.

## STEP 10 Quality Summary
- Existing 115-file suite/workflows are the minimum regression floor.
- Test/evidence layers span L0 Static/Supply through L7 Release Candidate.
- FeatureParityRegistry maps MUST KEEP behavior to regression evidence.
- Facades/adapters require legacy-vs-new contract proof before cleanup.
- Concurrency, destructive boundaries, and recovery paths require fault/race evidence.
- Real FFmpeg remains mandatory for affected render/Spectrum paths.
- 200-song/~3-hour structural stress remains mandatory.
- Performance >10% regression triggers investigation.
- Functional UI and pixel-match status are separate.
- Python >=3.11 support must be tested on 3.11 or changed explicitly.
- Exact extracted Windows portable ZIP is the final artifact under smoke.
- Release promotion follows Q0→Q5 and requires an evidence manifest.

Detailed DOCX planning artifacts remain the canonical detailed references. Markdown files provide fast status/handoff summaries and do not replace the DOCX files.

After STEP 11 planning completes, all STEP 00–11 source-of-truth planning artifacts must be placed in the V2 repository before coding begins.
