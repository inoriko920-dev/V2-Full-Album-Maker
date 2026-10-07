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
- STEP 07 — Animation, Transition, Spectrum, Preview/Render Parity — NEXT
- STEP 08 — Feature Parity, Enhancement, AI Agent Reliability
- STEP 09 — UI Preservation, Responsiveness, Integration Contract
- STEP 10 — Testing, Regression, Stress, Benchmark, Quality Gate
- STEP 11 — Windows Portable Build, Release, Rollback, Final Handoff

## Current State
STEP 06 is PASS. STEP 07 is next. Coding remains blocked.

## STEP 03 Architecture Summary
Target architecture is layered/ports-and-adapters with one AppKernel/CompositionRoot. Existing behavior is wrapped before replacement. Migration order is M0..M9 and every slice must be rollback-capable.

## STEP 04 Hardening Summary
V2 centralizes async/process ownership, stable project-token/generation guards, deterministic close/project switching, verification-first publication, explicit recovery classification, bounded shutdown, and fault-injection evidence.

## STEP 05 Media / Preview / Timeline / Data Summary
Canonical media identity is ProjectDocument UUID asset_id. ffprobe is the initial normalized probe adapter. Relink preserves identity. Accurate Preview is the parity oracle. Cache is disposable. Timeline stays at 240000 integer ticks/sec with frozen Packed/Free semantics. Project schema v2 remains frozen.

## STEP 06 Render Summary
- One RenderEngine path owns final rendering.
- Immutable RenderSnapshot + RenderPlan bind each job to a frozen revision.
- Critical preflight is mandatory immediately before launch.
- AUTO hardware requires runtime verification and software fallback remains available.
- Current Step08→V13→S11→FFmpegV2 semantics are wrapped, not rewritten.
- Large filter graphs are externalized for Windows command safety.
- Process completion alone is not success: ffprobe verification and transactional bundle publish are mandatory.
- Queue crash attempts become INTERRUPTED; Retry creates a fresh attempt.
- One-pass is default; segment/resume is deferred pending evidence.
- S/M/L/XL stress reaches 200 songs / ~3 hours structurally.
- Accurate Preview/final Render share compilation semantics.

Detailed DOCX planning artifacts remain the canonical detailed references. Markdown files provide fast status/handoff summaries and do not replace the DOCX files.
