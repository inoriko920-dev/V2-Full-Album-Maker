# AI Handoff — V2 Full-Album-Maker

Before doing any work:

1. Confirm the target repository is `inoriko920-dev/V2-Full-Album-Maker`.
2. Do not write to `inoriko920-dev/Full-Album-Maker`.
3. Read:
   - `docs/governance/PROJECT_GOVERNANCE.md`
   - `docs/governance/PROJECT_STATUS.md`
   - `docs/planning/README.md`
   - `docs/planning/STEP_01_AUDIT_SUMMARY.md`
   - the Master Plan DOCX
   - every completed STEP DOCX in order
4. Check the current STEP and gate status before acting.
5. Do not skip planning gates.
6. Do not redesign the UI or application concept merely because another repository has a stronger engine.
7. Treat external repositories as references/candidates until license, maintenance, packaging, parity, and integration risks are reviewed.
8. Preserve STEP 01 behavior contracts C-01..C-20 unless an explicit later planning decision replaces one with migration/UX/regression evidence.
9. Keep all changes reversible and protected by tests.
10. If an implementation requires a major architecture decision not covered by planning, stop implementation and document the decision first.

### STEP 01 Architecture Facts
- Production startup installs 30 runtime compatibility/feature patches before constructing the final window.
- ProjectDocument plus EditorController/EditorSession is the authoritative editor state and history owner.
- Legacy Project is a compatibility/persistence bridge, not a second authoritative editor.
- Production render path is Step10 RenderExecutor -> Step08FFmpegCompiler -> V13FFmpegCompiler -> S11FFmpegCompiler -> FFmpegV2Compiler.
- Render jobs use immutable snapshots, critical preflight, ffprobe verification, and transactional publication.
- AI is optional and must remain a sanitized intent planner whose mutations execute locally through validated commands.
- Manual/offline editing and rendering must remain available.

### Current Handoff
- Phase: PLANNING
- Current completed STEP: STEP 01
- STEP 00 Gate: PASS
- STEP 01 Gate: PASS
- Next STEP: STEP 02 — Riset Pondasi Matang, Lisensi, dan Keputusan Adopsi
- Coding: BLOCKED
