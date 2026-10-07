# Planning Source-of-Truth — V2 Full-Album-Maker

## Planning Sequence
- MASTER — overall development plan
- STEP 00 — Baseline Copy, Governance, Source-of-Truth — PASS
- STEP 01 — Audit Repo Lama dan Kontrak Perilaku — PASS
- STEP 02 — Riset Pondasi Matang, Lisensi, Keputusan Adopsi — PASS
- STEP 03 — Target Architecture V2 dan Strategi Migrasi Bertahap — PASS
- STEP 04 — Hardening Stabilitas, Lifecycle, Error Handling, Recovery — PASS
- STEP 05 — Media, Preview, Cache, Timeline, Project Data — PASS
- STEP 06 — Render Engine, Processing Pipeline, Long-Album Reliability — NEXT
- STEP 07 — Animation, Transition, Spectrum, Preview Parity
- STEP 08 — Feature Parity, Enhancement, AI Agent Reliability
- STEP 09 — UI Preservation, Responsiveness, Integration Contract
- STEP 10 — Testing, Regression, Stress, Benchmark, Quality Gate
- STEP 11 — Windows Portable Build, Release, Rollback, Final Handoff

## Current State
STEP 05 is PASS. STEP 06 is next. Coding remains blocked.

## STEP 03 Architecture Summary
Target architecture is layered/ports-and-adapters with one AppKernel/CompositionRoot. Existing behavior is wrapped before replacement. Migration order is M0..M9 and every slice must be rollback-capable.

## STEP 04 Hardening Summary
V2 centralizes async/process ownership through TaskSupervisor/TaskScope and ProcessSupervisor, uses stable project token+generation for stale-result protection, orchestrates app close/project switching through ApplicationLifecycleService, retains verification-first atomic/transactional publication, classifies recovery explicitly, treats cache corruption as regenerable, and requires bounded shutdown plus fault-injection evidence.

## STEP 05 Media / Preview / Timeline / Data Summary
- Canonical media identity is ProjectDocument UUID asset_id; source path and fingerprint are independent.
- ffprobe supplies normalized media facts through MediaProbeService.
- Relink preserves identity/references and never silently changes timeline duration semantics.
- Accurate Preview is the parity oracle; preview requests are generation-aware and off the UI thread.
- Cache is disposable/versioned/namespaced/quota-bounded.
- Timeline remains integer-tick (240000 ticks/sec), time-based, and preserves Packed/Free/gap/crossfade rules.
- Project schema v2 remains frozen; extensions are versioned JSON-only domain data.
- Project migration is deterministic; Save/Reopen uses normalized semantic equality.
- Missing media keeps the project openable and relinkable.

Detailed DOCX planning artifacts remain the canonical detailed references. Markdown files provide fast status/handoff summaries and do not replace the DOCX files.
