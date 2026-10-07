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
13. Preserve STEP 10 quality decisions D10-01..D10-20.
14. Do not skip planning gates or redesign UI/workflow merely because another architecture looks cleaner.
15. Every future implementation must remain reversible and test-protected.
16. If a required architecture decision is not covered by approved planning, stop and document it first.

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
- Existing FFmpeg Spectrum styles remain canonical.
- Use versioned `Layer.animation` for generic keyframes; project schema remains v2.
- Animation property targets come only from a validated registry.
- Keyframe timing uses integer project ticks.
- Evaluation order is base/legacy -> manual track -> BeatResponse -> clamp.
- BeatAnalysis is derived data; BeatResponse is authored behavior.
- Visual transitions remain separate from audio crossfade.
- Existing overlay effects remain deterministic/seeded/bounded.
- Generic authored animation wins only for the property explicitly authored.
- Missing beat analysis uses neutral/non-reactive fallback; never fake reactivity.
- New effect families require Accurate Preview vs Final Render golden evidence.
- Animation complexity cannot expand per-frame Python data for long albums.
- Presets are declarative/versioned/non-executable.

## STEP 08 Feature / AI Rules
- All user-facing baseline features default to MUST KEEP.
- No user-facing removal is authorized.
- Manual editor remains feature authority.
- AI provider plans only; local ActionRegistry + dry-run + EditorController own mutation.
- Agent context is bounded/stable-ID based and excludes paths/API keys.
- Ambiguity means clarification + zero mutation.
- Project/revision/context/permission mismatch invalidates plan; no auto-rebase.
- Preview Diff and Execute use the same resolver/commands.
- One plan commits as one revision and one Undo transaction.
- AI direct render and filesystem path selection remain deferred.

## STEP 09 UI Rules
- Preserve existing production UI/workflow and all 9 route/order.
- WorkspaceRegistry/WorkspaceBundle becomes explicit route owner.
- UI patches retire route-by-route after visual/state parity.
- Heavy process/network/media/analysis work is forbidden on UI thread.
- Required visual/responsive evidence: 1672/100%, 1366/100%, 125%, 150%.
- Current production UI is migration no-regression baseline.
- Frozen canonical goldens remain immutable references.
- AI and Render UI reflect true underlying state/evidence.

## STEP 10 Quality Rules
- Existing 115-file test/workflow baseline is the minimum regression floor.
- Test layers run from L0 Static/Supply through L7 Release Candidate.
- FeatureParityRegistry maps MUST KEEP behavior to test evidence.
- New facade/adapter ownership requires legacy-vs-new contract evidence.
- Concurrency tests prove terminal state, stale-result rejection, and bounded resource behavior.
- Save/render/recovery/process boundaries require fault-injection tests.
- Real FFmpeg remains mandatory for affected critical paths.
- 200-song/~3-hour structural stress remains mandatory.
- Performance >10% regression versus same-environment baseline requires investigation.
- Functional UI PASS and pixel-match PASS are separate claims.
- Declared Python >=3.11 compatibility must be tested or revised explicitly.
- No rerun-until-green release policy.
- Exact extracted Windows portable ZIP is the final artifact under smoke.
- Release requires supply-chain/license/secret/checksum/evidence-manifest PASS.
- Promotion ladder: Q0 Developer -> Q1 Slice -> Q2 Integration -> Q3 Infrastructure -> Q4 Windows Artifact -> Q5 Release.

## Migration Rule
Wrap current proven behavior first. Route one path through the facade. Prove parity. Only then retire the old direct path. Never dual-write project state.

## Current Handoff
- Phase: PLANNING
- Completed through: STEP 10
- STEP 00–10: PASS
- Next: STEP 11 — Windows Portable Build, Release, Rollback, dan Final Handoff
- Coding: BLOCKED
- Pre-coding requirement after STEP 11: place all STEP 00–11 planning/source-of-truth artifacts in the V2 repository before implementation begins.
