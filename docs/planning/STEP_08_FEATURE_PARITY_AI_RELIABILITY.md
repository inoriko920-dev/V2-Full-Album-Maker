# STEP 08 — Feature Parity, Enhancement, dan AI Agent Reliability

Status: **PASS**

Coding remains **BLOCKED**. No source-code, dependency, UI, schema, renderer, or AI implementation change is authorized by STEP 08.

## Feature Governance
- Every user-facing baseline capability defaults to **MUST KEEP**.
- **IMPROVE** is additive/backward-compatible.
- **DEFER** means valid idea but not required for first stable V2.
- **REMOVE** is not authorized for user-facing features in this planning set.
- Internal legacy implementations may be retired only after replacement + parity evidence.

## User-Facing Parity Decisions
MUST KEEP includes:
- Home/New/Open/Recent/Recovery.
- Media import/folder scan/preview/metadata/relink/library metadata.
- Album playlist/reorder/cover/visual assignment/auto-match/album visuals.
- Packed + Free Timeline, gap/crossfade/ripple/snap/markers/gain/fade/Undo/Redo/Auto Susun.
- Per-song image/video visual, crop/fit/position/scale, loop/freeze, video speed, existing transitions.
- Built-in/legacy/custom templates and thumbnails.
- FFmpeg Spectrum bars/line/waveform/stereo/circular and accurate preview.
- Render preflight/queue/retry/progress/cancel/hardware fallback/ffprobe verification/sidecars/transactional publish.
- Windows portable ZIP.
- Manual/offline workflows.

IMPROVE includes:
- Generic keyframes/AnimationTrack.
- BeatAnalysis + BeatResponse and beat-reactive presets.
- More declarative animation/Spectrum presets.
- Stronger recovery/cache/lifecycle behavior from prior STEPs.
- AI actions for animation, beat response, richer Spectrum properties, and local deterministic auto-match.

DEFER includes:
- AI direct render request until RenderEngine facade is production-proven.
- AI relink/import filesystem path handling.
- Pause/resume and segment/checkpoint render.
- projectM/GPU/3D/page-turn visual systems.

## Current STEP09 AI Baseline
- 9 whitelisted actions.
- 5 write permission domains.
- AgentPlan max actions: 100.
- Prompt max: 4000 chars.
- Context is bounded and path/API-key/locator free.
- Revision + project_id + context fingerprint guards.
- Dry-run / Preview Diff before Execute.
- One AI plan commits as one EditorController transaction and one Undo.
- Duplicate plan_id causes no second mutation.
- Saved commands replay intent text, not stale plans.
- Up to 100 Gemini keys with Windows DPAPI, cooldown/failover, corrupt-vault quarantine.

## Target AI Reliability
Provider is an **intent planner only**:
```
User text
  -> sanitized ContextBuilder
  -> AIProviderPort
  -> AgentPlan
  -> local ActionRegistry validation
  -> DryRun / PreviewDiff on cloned ProjectDocument
  -> explicit user confirmation
  -> EditorController.dispatch(... expected_revision)
  -> local execution evidence
  -> factual natural-language response
```

## ActionSpec V2
Every AI action must declare:
- schema,
- permission,
- scope,
- required capabilities,
- side-effect class,
- local resolver to normal domain commands,
- preview policy,
- idempotency policy.

## Planned Permission Expansion
- KEEP: visual.write, timeline.write, playlist.write, template.write, spectrum.write.
- ADD later: animation.write, only after STEP 07 animation commands exist.
- DEFER: media.write and render.request.
- project.save is not an initial AI permission.

## Safety Rules
- Ambiguous targets -> clarification, zero mutation.
- Unknown IDs/presets/properties -> reject.
- Revision/project/context/permission change -> stale plan, replan.
- Provider text never overrides local execution facts.
- Preview Diff and Execute use exactly the same resolver/domain commands.
- No arbitrary code/shell/FFmpeg command/filesystem path/network side effects.
- No provider-initiated Save/Save As.
- No AI direct render in initial V2.
- Manual editor remains authoritative and complete.

## Implementation Slices for SOL Later
F1 FeatureParityRegistry/test mapping.
F2 ActionSpec metadata expansion.
F3 central ActionRegistry under AIPlanningService.
F4 preserve all current STEP09 actions through contract tests.
F5 add animation.write after STEP07 command contracts.
F6 animation/BeatResponse AI actions with dry-run parity.
F7 safe auto-match cover/visual actions.
F8 factual post-execution natural-language summaries.
F9 TaskSupervisor provider lifecycle integration.
F10 full feature parity + AI stress/regression before legacy AI removal.

## Next STEP
**STEP 09 — UI Preservation, Responsiveness, dan Integration Contract.**
