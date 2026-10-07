# Planning Source-of-Truth — V2 Full-Album-Maker

This directory is the planning index for V2 development.

## Planning Sequence
- MASTER — overall development plan
- STEP 00 — Baseline Copy, Governance, Source-of-Truth — **PASS**
- STEP 01 — Audit Repo Lama dan Kontrak Perilaku — **PASS**
- STEP 02 — Riset Pondasi Matang, Lisensi, Keputusan Adopsi — **PASS**
- STEP 03 — Target Architecture V2 dan Strategi Migrasi — **NEXT**
- STEP 04 — Hardening Stabilitas, Lifecycle, Error Handling, Recovery
- STEP 05 — Media, Preview, Cache, Timeline, Project Data
- STEP 06 — Render Engine, Processing Pipeline, Long-Album Reliability
- STEP 07 — Animation, Transition, Spectrum, Preview Parity
- STEP 08 — Feature Parity, Enhancement, AI Agent Reliability
- STEP 09 — UI Preservation, Responsiveness, Integration Contract
- STEP 10 — Testing, Regression, Stress, Benchmark, Quality Gate
- STEP 11 — Windows Portable Build, Release, Rollback, Final Handoff

## Current State
STEP 00, STEP 01, and STEP 02 are PASS. STEP 03 is next. Coding remains blocked.

## STEP 01 Frozen Behavior Areas
- UI/workflow concept and nine workspace model.
- ProjectDocument schema v2 and one authoritative editor state.
- Packed/Free timeline timing semantics.
- Preview/final composition parity.
- AI privacy, stable-ID, revision, permission, and fail-closed semantics.
- Immutable render snapshot, critical preflight, output verification, and transactional publication.
- Canonical Save versus separate autosave/recovery semantics.
- Windows portable multi-file distribution target.

## STEP 02 Technology Direction
- Do not replace the application with an external repository.
- Keep direct FFmpeg/ffprobe final rendering and PySide6 UI.
- Learn from MLT/libopenshot architecture without adopting them as core runtime.
- Plan beat-reactive animation as a separate deterministic analysis service.
- NumPy is the first runtime candidate for that analysis; adoption still requires benchmark/portable gates.
- Treat third-party license compliance as release evidence, not an afterthought.

## Important
Detailed DOCX files are the planning source-of-truth. Markdown files provide fast status/handoff. Before coding starts, all final planning DOCX/reference artifacts must be consolidated into the V2 repository as required by project governance.
