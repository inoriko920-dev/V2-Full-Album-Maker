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
- Current production compiler semantics remain Step08 -> V13 -> S11 -> FFmpegV2 until facade parity is proven.
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

Implementation is now allowed, but has **not started yet**.

## First Work After Unlock
- M0 / T1: FeatureParityRegistry + characterization map.
- Then M1: additive AppKernel/CompositionRoot using current proven behavior through legacy adapters.
- Do not start with animation catalog, compiler rewrite, route patch deletion, or release work.

## Current Handoff
- Phase: IMPLEMENTATION READY
- Completed planning: STEP 00–11 PASS
- Pre-coding documentation gate: PASS
- Coding: UNLOCKED, NOT STARTED
- Next operational action: M0/T1 FeatureParityRegistry + characterization map only; then report gate before M1.
