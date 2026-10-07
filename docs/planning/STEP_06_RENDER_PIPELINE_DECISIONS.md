# STEP 06 — Render Pipeline Decisions

Status: **PASS**  
Implementation status: **BLOCKED — planning only**

## Baseline Evidence
- Current final chain: Render Center -> RenderExecutor -> Step08FFmpegCompiler -> V13FFmpegCompiler -> S11FFmpegCompiler -> FFmpegV2Compiler -> process -> ffprobe verification -> transactional publish.
- Existing structural stress fixture covers 200 songs × 54 seconds = 3 hours for both Packed and Free Timeline.
- The stress resolver has a generous <2 second CI ceiling.
- Large graphs are externalized at 8,192 characters or when approximate Windows command line approaches the 30,000-character safety limit.
- Real FFmpeg test covers external filter-script execution.
- Queue persistence marks active attempts INTERRUPTED after restart instead of claiming resume.
- Real FFmpeg smoke proves staged render is ffprobe-verified before final publication.

## Decisions D06-01 .. D06-20
1. D06-01 — One canonical RenderEngine orchestration path.
2. D06-02 — RenderSnapshot/RenderPlan are immutable execution and audit evidence.
3. D06-03 — RenderPlan is the canonical resolved timing view.
4. D06-04 — Mandatory critical preflight immediately before start.
5. D06-05 — AUTO hardware requires runtime verification and may fall back to software.
6. D06-06 — Wrap Step08→V13→S11→FFmpegV2 first; do not rewrite the compiler chain.
7. D06-07 — Externalize large filter graphs; unsafe command length blocks pre-launch.
8. D06-08 — Every attempt owns unique work/staging artifacts.
9. D06-09 — COMPLETED only after process success, verification, and publication.
10. D06-10 — ffprobe output verification is mandatory.
11. D06-11 — MP4 and standard sidecars publish as one bundle transaction.
12. D06-12 — Transaction-journal recovery remains mandatory.
13. D06-13 — Pause/resume and crash-resume remain deferred.
14. D06-14 — 200-song/~3-hour structural stress remains the upper planning regression baseline.
15. D06-15 — Disk budget includes staging/work overhead, not only final bitrate estimate.
16. D06-16 — One-pass render remains default; segmentation is evidence-gated.
17. D06-17 — Accurate Preview and final Render share composition semantics.
18. D06-18 — Beat response is deterministic derived compiler input and never retimes master audio.
19. D06-19 — Persist safe evidence about snapshot/settings/capability/compiler/verification.
20. D06-20 — Compiler consolidation is optional cleanup after parity gates, not a goal itself.

## Long-Album Tiers
- S: 10 songs, ~10–30 minutes
- M: 50 songs, ~30–60 minutes
- L: 100 songs, ~60–120 minutes
- XL: 200 songs, ~180 minutes

## Next
STEP 07 — Animation, Transition, Spectrum, Beat-Reactive Behavior, and Preview/Render Parity.
