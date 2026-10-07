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
- STEP 08 — Feature Parity, Enhancement, AI Agent Reliability — NEXT
- STEP 09 — UI Preservation, Responsiveness, Integration Contract
- STEP 10 — Testing, Regression, Stress, Benchmark, Quality Gate
- STEP 11 — Windows Portable Build, Release, Rollback, Final Handoff

## Current State
STEP 07 is PASS. STEP 08 is next. Coding remains blocked.

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
- Existing FFmpeg Spectrum (bars/line/waveform/stereo/circular) remains canonical.
- Visual transition never silently alters audio timing/crossfade.
- Existing seeded/bounded overlay effects remain the foundation.
- Accurate Preview vs Final Render golden parity is mandatory for new effect families.
- Non-reactive fallback is required when beat analysis is unavailable.
- Preset catalog expands only after a small animation core is proven.

Detailed DOCX planning artifacts remain the canonical detailed references. Markdown files provide fast status/handoff summaries and do not replace the DOCX files.
