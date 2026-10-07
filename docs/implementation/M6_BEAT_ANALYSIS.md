# M6 — Beat Analysis

Status: **PASS — implemented and validated**

## Scope

M6 introduces the approved `BeatAnalysisService` as derived/cacheable audio
analysis only. It does **not** implement authored BeatResponse behavior, does
not change ProjectDocument schema, does not redesign UI, and does not replace
the existing FFmpeg Spectrum renderer.

The existing production Spectrum remains canonical. M6 only establishes the
derived analysis boundary that later authored visual responses may consume
under the STEP 07 rules.

## New Boundary

`src/full_album_maker/beat_analysis.py` adds:

- `BeatAnalysisService`
  - AppKernel-owned application service;
  - shares the exact M5 `CacheManager`;
  - shares the exact M2 `TaskSupervisor`;
  - creates no private `ThreadPoolExecutor` or independent worker thread pool;
  - exposes synchronous `analyze()` and TaskSupervisor-backed `submit()`;
  - owns one generation-aware `beat-analysis` TaskScope.

- `BeatAnalysisResult`
  - derived envelope + detected beat/transient events;
  - never serialized into ProjectDocument;
  - explicitly reports `available=False` for unavailable analysis;
  - `is_reactive` is false when no real beat evidence exists.

- `BeatEvent`
  - deterministic event time + bounded strength only.

- `detect_beats()`
  - pure deterministic detector over the derived low-rate envelope;
  - no random state and no dependency on render FPS.

## FFmpeg Derived Envelope

The default adapter reads source audio without modifying it.

FFmpeg performs:
1. mono conversion;
2. 8 kHz intermediate resampling;
3. absolute-value rectification;
4. bounded low-pass smoothing;
5. downsampling to 50 Hz by default;
6. float32 derived output to Python.

At 50 Hz the derived stream is approximately 200 bytes/second, so Python-side
memory scales with low-rate analysis samples rather than original PCM size or
video duration × FPS.

M6 introduces no NumPy dependency.

## Deterministic Beat Detection

The detector:
- normalizes the derived envelope;
- calculates a rolling local baseline;
- derives positive onset strength;
- uses a deterministic adaptive threshold;
- applies bounded local-maximum selection;
- enforces a minimum event interval;
- normalizes event strength to 0..1.

This is the initial small analysis core required by D07-18. It is not presented
as a full DJ/BPM/tempo engine.

## Non-Reactive Fallback

D07-13 is preserved explicitly.

If:
- source media is missing;
- FFmpeg is unavailable;
- audio decoding fails;
- the source changes during analysis;

the service returns an unavailable derived result with:
- no envelope;
- no beat events;
- `is_reactive=False`;
- a diagnostic reason.

Silence is a valid available analysis result with a zero envelope and no beat
events. M6 never generates fake reactivity.

## Cache Policy

M6 uses the M5 `beat-analysis` cache namespace.

Cache identity includes:
- M5 SourceFingerprint token;
- cache namespace version;
- M6 analyzer version;
- analysis sample rate;
- detector timing parameters.

A source size/mtime change therefore gets a different cache identity.

Cache payload publication is atomic. Corrupt, incompatible, stale, or malformed
cache JSON is treated as a disposable miss and evicted. Cache write failure does
not corrupt or invalidate a valid in-memory analysis result.

Derived beat cache remains non-authoritative project data.

## Lifecycle / Cancellation

Async analysis uses the existing M2 `TaskSupervisor` and `TaskScope`.

- no second Python executor is introduced;
- generation invalidation cancels stale tokens;
- stale/cancelled work cannot be accepted as current;
- the worker checks cancellation before and after decoding.

M6 does not claim H3 ProcessSupervisor. A currently running FFmpeg subprocess
still cannot be force-killed through TaskSupervisor; cancellation is
cooperatively observed before/after the current adapter call. Process ownership
hardening remains a later approved concern.

## AppKernel Ownership

CompositionRoot now creates or accepts exactly one `BeatAnalysisService`.

The service must use:
- the exact AppKernel-owned `CacheManager`;
- the exact AppKernel-owned `TaskSupervisor`.

During legacy runtime execution the exact service instance is exposed through a
bounded ContextVar migration bridge alongside the M4/M5 services.

## STEP 07 Decisions Preserved

- D07-01: analysis is deterministic.
- D07-04: no BeatResponse evaluation/order is implemented or changed.
- D07-07: derived BeatAnalysis remains separate from authored BeatResponse.
- D07-08/D07-09: no new authored response/topology behavior is introduced.
- D07-10/D07-11: current FFmpeg Spectrum/circular Spectrum remain canonical.
- D07-13: fallback never fakes audio reactivity.
- D07-14: existing Accurate Preview vs Final Render/Spectrum parity remains
  gate-protected.
- D07-15: analysis scales with low-rate derived samples, not duration × FPS
  Python frame data.
- D07-17: master audio is not retimed or modified.
- D07-18: M6 proves a small analysis core before any larger response catalog.

## Master Audio Safety

The real-FFmpeg M6 test hashes the source WAV before and after analysis and
requires byte identity. BeatAnalysisService only reads the source.

No master-audio gain, timing, crossfade, source range, or project timeline field
is modified.

## Rollback

M6 is additive and branch-isolated.

Rollback target:
- M5 PASS head: `33991c640681ac57bd6cfd812f27187a100fe493`.

No schema/data migration is introduced.

## Gate

M6 is PASS only after:
1. M0–M6 contracts pass;
2. deterministic/cache/fallback/lifecycle BeatAnalysis tests pass;
3. existing Spectrum model/render/failure/async behavior remains PASS;
4. Accurate Preview/render parity remains PASS;
5. production persistence/nine-workspace characterization remains PASS;
6. 200-song/~3-hour structural stress remains PASS;
7. real FFmpeg detects real synthetic pulses;
8. real silence remains non-reactive;
9. master audio bytes remain unchanged;
10. existing real Accurate Preview/Spectrum parity remains PASS;
11. no M7/UI/schema/release scope appears in the runtime change.

## Validation Evidence

Validated candidate head:
- branch: `impl-m6-beat-analysis`
- candidate: `a0d5a88a372f373c852c40242cea82511c1fd3dc`
- runtime implementation introduced at:
  `3f3eae92b7bd4de643e28ca2e36e8dc12e2f3681`
- subsequent candidate commits only corrected architecture-guard tests;
- GitHub Actions run: `37595757999`

Main job `m6-beat-analysis`: **SUCCESS**
- Q0 compile: PASS
- M0–M6 contracts: **58 passed, 4 skipped**
- Beat/Spectrum parity: **19 passed, 1 skipped**
- Accurate Preview/render parity: **7 passed, 1 skipped**
- persistence + production shell: **12 passed**
- 200-song/~3-hour structural stress: **2 passed**

Targeted `real-ffmpeg-m6`: **SUCCESS**
- **4 passed**
- real pulse audio creates real derived events;
- real silence stays non-reactive;
- source/master-audio bytes remain unchanged;
- existing Accurate Preview/final-render and Spectrum compiler parity remain
  protected.

The documentation-only final commit must keep the same M6 workflow green before
handoff is complete.

## Next

M6 is PASS. The next allowed migration phase is **M7 — Workspace Registry**.
M7 is not started in this turn.
