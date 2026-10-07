# AI Handoff — V2 Full-Album-Maker

Before doing any work:

1. Confirm target repository is `inoriko920-dev/V2-Full-Album-Maker`.
2. Never write to `inoriko920-dev/Full-Album-Maker`.
3. Read:
   - `docs/governance/PROJECT_GOVERNANCE.md`
   - `docs/governance/PROJECT_STATUS.md`
   - `docs/planning/README.md`
   - `docs/planning/STEP_01_AUDIT_SUMMARY.md`
   - `docs/planning/STEP_02_DECISIONS.md`
   - `docs/planning/STEP_03_ARCHITECTURE_DECISIONS.md`
   - `docs/planning/STEP_04_HARDENING_DECISIONS.md`
   - Master Plan DOCX and every completed STEP DOCX in order.
4. Preserve STEP 01 behavior contracts C-01..C-20.
5. Preserve STEP 02 adoption decisions.
6. Preserve STEP 03 dependency direction and M0..M9 migration order.
7. Preserve STEP 04 lifecycle/failure/recovery decisions D04-01..D04-15.
8. Do not skip planning gates.
9. Do not redesign UI/workflow merely because another architecture looks cleaner.
10. Every future implementation must remain reversible and test-protected.
11. If a required architecture decision is not covered by approved planning, stop and document it first.

## Frozen Architecture Facts
- ProjectDocument + EditorController/EditorSession remain authoritative.
- Legacy Project is compatibility only and must not regain ownership.
- FFmpeg/ffprobe remain canonical render/probe infrastructure.
- Production render semantics remain the current Step10 -> Step08 -> V13 -> S11 -> FFmpegV2 chain until facade parity is proven.
- Manual/offline editing and rendering remain first-class.
- AI remains optional, sanitized, fail-closed, and locally executed through validated commands.
- Save/output publication remains atomic/transactional and recovery remains separate.

## STEP 03 Target Boundaries
- AppKernel / CompositionRoot
- ProjectSession
- WorkspaceRegistry
- TaskSupervisor / TaskScope
- CapabilityRegistry
- MediaProbeService
- CacheManager
- PreviewEngine
- RenderEngine
- ProjectPersistence
- BeatAnalysisService
- AIPlanningService

## STEP 04 Hardening Rules
- Task/process cancellation is idempotent and terminal states are explicit.
- All new project-bound async work carries stable project token + generation.
- ProcessSupervisor owns subprocess lifetime and terminate -> grace -> kill -> reap.
- App close and project switch use deterministic orchestration, not implicit closeEvent patch ordering.
- No canonical Save/render output is replaced before verification.
- Invalid recovery/journal/cache is never silently trusted.
- Cache corruption is non-critical and regenerable.
- Cancellation is not reported as successful completion or generic crash.
- Retry is bounded and only allowed when operation semantics are idempotent.
- No unbounded shutdown wait; no post-close project mutation.
- Existing safety code is retired only after stronger replacement behavior has evidence.

## Migration Rule
Wrap current proven behavior first. Route one path through the facade. Prove parity. Only then retire the old direct path. Never dual-write project state.

## Current Handoff
- Phase: PLANNING
- Completed through: STEP 04
- STEP 00: PASS
- STEP 01: PASS
- STEP 02: PASS
- STEP 03: PASS
- STEP 04: PASS
- Next: STEP 05 — Media, Preview, Cache, Timeline, dan Project Data
- Coding: BLOCKED
