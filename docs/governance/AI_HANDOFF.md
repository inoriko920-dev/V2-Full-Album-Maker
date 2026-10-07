# AI Handoff — V2 Full-Album-Maker

Before doing any work:

1. Confirm target repository is `inoriko920-dev/V2-Full-Album-Maker`.
2. Never write to `inoriko920-dev/Full-Album-Maker`.
3. Read governance/status/planning index, then every completed STEP planning artifact in order.
4. Preserve STEP 01 behavior contracts C-01..C-20.
5. Preserve STEP 02 adoption decisions.
6. Preserve STEP 03 architecture and M0..M9 migration order.
7. Preserve STEP 04 lifecycle/failure/recovery decisions D04-01..D04-15.
8. Preserve STEP 05 media/timeline/project decisions D05-01..D05-18.
9. Preserve STEP 06 render decisions D06-01..D06-20.
10. Do not skip planning gates or redesign UI/workflow merely because another architecture looks cleaner.
11. Every future implementation must remain reversible and test-protected.
12. If a required architecture decision is not covered by approved planning, stop and document it first.

## Frozen Architecture Facts
- ProjectDocument + EditorController/EditorSession remain authoritative.
- Legacy Project is compatibility only and must not regain ownership.
- FFmpeg/ffprobe remain canonical render/probe infrastructure.
- Current production compiler semantics remain Step08 -> V13 -> S11 -> FFmpegV2 until facade parity is proven.
- Manual/offline editing and rendering remain first-class.
- AI remains optional, sanitized, fail-closed, and locally executed through validated commands.
- Save/output publication remains atomic/transactional and recovery remains separate.

## STEP 03 Target Boundaries
AppKernel / CompositionRoot; ProjectSession; WorkspaceRegistry; TaskSupervisor / TaskScope; CapabilityRegistry; MediaProbeService; CacheManager; PreviewEngine; RenderEngine; ProjectPersistence; BeatAnalysisService; AIPlanningService.

## STEP 04 Hardening Rules
- Task/process cancellation is idempotent and terminal states are explicit.
- Project-bound async work carries stable project token + generation.
- ProcessSupervisor owns subprocess lifetime and terminate -> grace -> kill -> reap.
- App close/project switch use deterministic orchestration.
- No canonical Save/render output is replaced before verification.
- Invalid recovery/journal/cache is never silently trusted.
- Cache corruption is regenerable.
- No unbounded shutdown wait or post-close project mutation.

## STEP 05 Media / Timeline / Project Rules
- ProjectDocument UUID asset IDs are canonical.
- Relink preserves asset identity/references.
- ffprobe initially supplies normalized media facts.
- Accurate Preview is the parity oracle.
- Cache is disposable.
- TIMEBASE=240000 integer ticks/sec remains authoritative.
- Packed/Free/gap/crossfade semantics are frozen.
- Project schema v2 remains frozen during consolidation.
- Missing media keeps references intact for relink.

## STEP 06 Render Rules
- All final renders go through one RenderEngine orchestration path.
- RenderSnapshot and RenderPlan are immutable evidence/execution inputs.
- No renderer may re-read live ProjectSession state.
- Critical preflight runs immediately before execution even for READY/QUEUED jobs.
- AUTO hardware encoding requires runtime verification and can fall back to software.
- Existing compiler hierarchy is wrapped before any consolidation.
- Long graphs are externalized; unsafe command length blocks before launch.
- Every attempt owns its work/staging files.
- COMPLETED means FFmpeg success + ffprobe verification + transaction publish success.
- MP4 and standard sidecars publish as one transaction.
- Crash active attempts become INTERRUPTED; retry is a fresh attempt/preflight.
- Pause/resume and crash-resume are not claimed.
- One-pass rendering is default; segmentation is evidence-gated and currently deferred.
- 200-song/~3-hour structural stress remains an upper planning regression baseline.
- Accurate Preview/final Render share composition semantics.
- Beat-derived input never retimes master audio.

## Migration Rule
Wrap current proven behavior first. Route one path through the facade. Prove parity. Only then retire the old direct path. Never dual-write project state.

## Current Handoff
- Phase: PLANNING
- Completed through: STEP 06
- STEP 00–06: PASS
- Next: STEP 07 — Animation, Transition, Spectrum, Beat-Reactive Behavior, dan Preview/Render Parity
- Coding: BLOCKED
