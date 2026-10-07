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
10. Preserve STEP 07 animation/Spectrum/parity decisions D07-01..D07-18.
11. Preserve STEP 08 feature/AI decisions D08-01..D08-20.
12. Preserve STEP 09 UI decisions D09-01..D09-20.
13. Do not skip planning gates or redesign UI/workflow merely because another architecture looks cleaner.
14. Every future implementation must remain reversible and test-protected.
15. If a required architecture decision is not covered by approved planning, stop and document it first.

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

## STEP 07 Animation / Spectrum Rules
- Existing FFmpeg Spectrum styles remain canonical; do not replace them with fake beat animation.
- Use versioned `Layer.animation` for generic keyframes; project schema remains v2.
- Animation property targets come only from a validated registry.
- Keyframe timing uses integer project ticks.
- Evaluation order is base/legacy -> manual track -> BeatResponse -> clamp.
- BeatAnalysis is derived data; BeatResponse is authored behavior.
- Visual transitions remain separate from audio crossfade.
- Existing overlay effects remain deterministic/seeded/bounded.
- Generic authored animation wins only for the property explicitly authored; otherwise legacy behavior remains.
- If beat analysis is unavailable, use a neutral/non-reactive fallback; never fake reactivity.
- Every new effect family requires Accurate Preview vs Final Render golden evidence.
- Animation complexity must not expand per-frame Python data for long albums.
- Presets are declarative/versioned/non-executable.
- Initial implementation proves a small core before expanding the catalog.

## STEP 08 Feature / AI Rules
- All user-facing baseline features default to MUST KEEP.
- No user-facing removal is authorized by this planning set.
- Manual editor remains the feature authority; AI coverage may safely lag behind.
- AI provider plans only; local ActionRegistry + dry-run + EditorController own mutation.
- Agent context is bounded, stable-ID based, and excludes paths/API keys/locator/vault data.
- Ambiguity or insufficient context means clarification + zero mutation.
- Any project/revision/context/permission incompatibility invalidates the plan; no auto-rebase.
- Preview Diff and Execute use exactly the same resolvers/commands.
- One plan commits as one revision and one Undo transaction.
- AI direct render and AI filesystem path selection remain deferred.

## STEP 09 UI Rules
- Preserve the existing production UI/workflow; no redesign is authorized.
- Keep all 9 routes in the current order: Beranda, Media, Album, Timeline, Visual, Template, Spectrum, AI Agent, Render.
- Preserve the command bar, navigation, context panel, center workspace, inspector/AI dock, timeline dock, and status bar mental model.
- WorkspaceRegistry/WorkspaceBundle becomes the explicit route owner.
- Retire UI patches route-by-route only after visual/state parity.
- No FFmpeg/ffprobe, media scan/probe, Accurate Preview, BeatAnalysis, Gemini/network, heavy cache generation, or render verification/publish on the UI thread.
- UI busy/progress/cancel states mirror underlying task state machines.
- Global command/status state derives from ProjectSession/application services.
- Required visual/responsive evidence: 1672/100%, 1366/100%, 125%, 150%.
- Current production UI is the migration no-regression baseline.
- Frozen canonical 1672x941 goldens remain immutable references; historical pixel-match remediation is a separate workstream.
- No new UI-image prompt/reference set is required for this preservation scope.
- AI Agent preserves Send/Preview/Execute confirmation/Cancel/Undo truth.
- Render Center can show COMPLETED only after RenderEngine verified publication.
- Render is the last route to migrate.

## Migration Rule
Wrap current proven behavior first. Route one path through the facade. Prove parity. Only then retire the old direct path. Never dual-write project state.

## Current Handoff
- Phase: PLANNING
- Completed through: STEP 09
- STEP 00–09: PASS
- Next: STEP 10 — Testing, Regression, Stress, Benchmark, dan Release Quality Gate
- Coding: BLOCKED
