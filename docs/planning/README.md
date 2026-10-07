# Planning Source-of-Truth — V2 Full-Album-Maker

## Planning Sequence
- MASTER — overall development plan
- STEP 00 — Baseline Copy, Governance, Source-of-Truth — PASS
- STEP 01 — Audit Repo Lama dan Kontrak Perilaku — PASS
- STEP 02 — Riset Pondasi Matang, Lisensi, Keputusan Adopsi — PASS
- STEP 03 — Target Architecture V2 dan Strategi Migrasi Bertahap — PASS
- STEP 04 — Hardening Stabilitas, Lifecycle, Error Handling, Recovery — PASS
- STEP 05 — Media, Preview, Cache, Timeline, Project Data — NEXT
- STEP 06 — Render Engine, Processing Pipeline, Long-Album Reliability
- STEP 07 — Animation, Transition, Spectrum, Preview Parity
- STEP 08 — Feature Parity, Enhancement, AI Agent Reliability
- STEP 09 — UI Preservation, Responsiveness, Integration Contract
- STEP 10 — Testing, Regression, Stress, Benchmark, Quality Gate
- STEP 11 — Windows Portable Build, Release, Rollback, Final Handoff

## Current State
STEP 04 is PASS. STEP 05 is next. Coding remains blocked.

## STEP 03 Architecture Summary
Target architecture is layered/ports-and-adapters with one AppKernel/CompositionRoot. Existing behavior is wrapped before replacement. Migration order is M0..M9 and every slice must be rollback-capable.

## STEP 04 Hardening Summary
V2 will centralize async/process ownership through TaskSupervisor/TaskScope and ProcessSupervisor, use stable project token+generation for stale-result protection, orchestrate app close/project switching through ApplicationLifecycleService, retain verification-first atomic/transactional publication, classify recovery explicitly, treat cache corruption as regenerable, and require bounded shutdown plus fault-injection evidence.

Detailed DOCX planning artifacts remain the canonical detailed references. Markdown files provide fast status/handoff summaries and do not replace the DOCX files.
