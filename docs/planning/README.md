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
- STEP 11 — Windows Portable Build, Release, Rollback, Final Handoff — PASS

## Current State
STEP 00–11 planning is COMPLETE.

Coding remains BLOCKED until the canonical MASTER + STEP00–11 DOCX files are physically present in this V2 repository and match `PLANNING_ARTIFACTS_MANIFEST.md`.

## Architecture Summary
- Layered/ports-and-adapters with AppKernel/CompositionRoot.
- Existing behavior wrapped before replacement; migration M0..M9.
- ProjectDocument + EditorController remain authoritative.
- Task/Process lifecycle becomes explicit and bounded.
- ffprobe/FFmpeg remain canonical media/render infrastructure.
- ProjectDocument UUID media IDs remain canonical; relink preserves identity.
- TIMEBASE=240000 and Packed/Free semantics remain frozen.
- Accurate Preview is parity oracle.
- Render uses immutable snapshot/plan + critical preflight + verification + transactional publish.
- Layer.animation v1 + BeatResponse adds scalable animation without project schema bump.
- Existing FFmpeg Spectrum remains canonical.
- All baseline user-facing features are MUST KEEP.
- AI provider remains planner-only; local registry/dry-run/EditorController own mutation.
- Existing UI/workflow and all 9 routes are preserved.
- Existing 115-file test/workflow baseline is the minimum quality floor.

## STEP 11 Release Summary
- First mature V2 stable target is v2.0.0 after implementation/Q5.
- Stable publication is explicit from exact approved candidate SHA.
- Exact tested ZIP is the published ZIP and is identified by SHA-256.
- Windows portable remains primary distribution.
- Exact extracted-ZIP smoke must prove no global Python/FFmpeg/API-key dependency and verified A/V output.
- Release facts should converge on one canonical release manifest.
- THIRD_PARTY_NOTICES currently contains stale FFmpeg provenance and must be corrected before future V2 RC.
- Current auto-release-on-main behavior and old hardcoded handoff ancestry must be redesigned before V2 stable.
- Side-by-side portable update/rollback is the initial safe distribution model.
- Stable release artifacts/tags/checksums remain immutable recovery points.

## Pre-Coding Gate
Before any source implementation:
- upload canonical final MASTER + STEP00–11 DOCX files to the V2 repo;
- verify SHA-256 values against `PLANNING_ARTIFACTS_MANIFEST.md`;
- keep exactly one canonical DOCX per STEP;
- update status/handoff to mark the gate PASS.

Then implementation starts at M0/T1 FeatureParityRegistry/characterization, followed by additive M1 AppKernel/CompositionRoot.

Detailed DOCX planning artifacts are the canonical detailed references. Markdown summaries are fast navigation/handoff aids and do not replace the DOCX files.
