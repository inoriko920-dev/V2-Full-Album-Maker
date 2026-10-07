# Planning Source-of-Truth — V2 Full-Album-Maker

This directory is the planning index for V2 development.

## Planning Sequence
- MASTER — overall development plan
- STEP 00 — Baseline Copy, Governance, Source-of-Truth — **PASS**
- STEP 01 — Audit Repo Lama dan Kontrak Perilaku — **PASS**
- STEP 02 — Riset Pondasi Matang, Lisensi, Keputusan Adopsi — **NEXT**
- STEP 03 — Target Architecture V2 dan Strategi Migrasi
- STEP 04 — Hardening Stabilitas, Lifecycle, Error Handling, Recovery
- STEP 05 — Media, Preview, Cache, Timeline, Project Data
- STEP 06 — Render Engine, Processing Pipeline, Long-Album Reliability
- STEP 07 — Animation, Transition, Spectrum, Preview Parity
- STEP 08 — Feature Parity, Enhancement, AI Agent Reliability
- STEP 09 — UI Preservation, Responsiveness, Integration Contract
- STEP 10 — Testing, Regression, Stress, Benchmark, Quality Gate
- STEP 11 — Windows Portable Build, Release, Rollback, Final Handoff

## Current State
STEP 00 and STEP 01 are PASS. STEP 02 is next. Coding remains blocked.

## STEP 01 Frozen Behavior Areas
- UI/workflow concept and nine workspace model.
- ProjectDocument schema v2 and one authoritative editor state.
- Packed/Free timeline timing semantics.
- Preview/final composition parity.
- AI privacy, stable-ID, revision and fail-closed semantics.
- Immutable render snapshot, preflight, output verification and transactional publication.
- Canonical Save versus separate autosave/recovery semantics.
- Windows portable multi-file distribution target.

## Important
The DOCX files are the detailed planning artifacts. Markdown files in `docs/governance` and this directory provide fast handoff/status, but do not replace the detailed DOCX source-of-truth. Coding must remain blocked until all planning prerequisites and required DOCX references are present and accepted.
