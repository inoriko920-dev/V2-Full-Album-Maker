# AI Handoff — V2 Full-Album-Maker

Before doing any work:

1. Confirm the target repository is `inoriko920-dev/V2-Full-Album-Maker`.
2. Do not write to `inoriko920-dev/Full-Album-Maker`.
3. Read:
   - `docs/governance/PROJECT_GOVERNANCE.md`
   - `docs/governance/PROJECT_STATUS.md`
   - `docs/planning/README.md`
   - `docs/planning/STEP_01_AUDIT_SUMMARY.md`
   - `docs/planning/STEP_02_DECISIONS.md`
   - the Master Plan DOCX
   - every completed STEP DOCX in order
4. Check current STEP and gate status before acting.
5. Do not skip planning gates.
6. Preserve STEP 01 behavior contracts C-01..C-20.
7. Do not redesign UI/workflow merely because an external project has a stronger engine.
8. External projects/components remain references/candidates until license, packaging, parity, benchmark, and rollback gates pass.
9. Keep every future implementation reversible and test-protected.
10. If an implementation needs an architecture decision not covered by approved planning, stop and document it first.

## Frozen Architecture Facts from STEP 01
- Production startup installs 30 runtime compatibility/feature patches before constructing the final window.
- ProjectDocument plus EditorController/EditorSession is the authoritative editor state/history owner.
- Legacy Project is a compatibility/persistence bridge, not a second authoritative editor.
- Production render path is Step10 RenderExecutor -> Step08FFmpegCompiler -> V13FFmpegCompiler -> S11FFmpegCompiler -> FFmpegV2Compiler.
- Render jobs use immutable snapshots, critical preflight, ffprobe verification, and transactional publication.
- AI remains optional, sanitized, fail-closed, and executes mutations locally through validated actions.
- Manual/offline editing and rendering must remain available.

## STEP 02 Adoption Decisions
- KEEP: FFmpeg/ffprobe, PySide6/Qt, current V2 repo as foundation.
- CANDIDATE: NumPy 2.3.x for future BeatAnalysisService after benchmarks.
- DEFER: SciPy, PyAV.
- REFERENCE-ONLY: MLT, libopenshot, imageio-ffmpeg, MoviePy, librosa.
- POST-V2 OPTIONAL: projectM as isolated visualizer/plugin only.
- REJECT CORE: aubio, Essentia.
- Python >=3.11 remains the initial baseline.
- Do not bundle a second FFmpeg without an explicit approved reason.

## Current Handoff
- Phase: PLANNING
- Current completed STEP: STEP 02
- STEP 00 Gate: PASS
- STEP 01 Gate: PASS
- STEP 02 Gate: PASS
- Next STEP: STEP 03 — Target Architecture V2 dan Strategi Migrasi Bertahap
- Coding: BLOCKED
