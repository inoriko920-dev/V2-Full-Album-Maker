# M6 — Beat Analysis Evidence

Status: **PASS**

## Candidate

- Branch: `impl-m6-beat-analysis`
- M5 rollback/base: `33991c640681ac57bd6cfd812f27187a100fe493`
- Runtime implementation commit:
  `3f3eae92b7bd4de643e28ca2e36e8dc12e2f3681`
- Validated candidate head:
  `a0d5a88a372f373c852c40242cea82511c1fd3dc`
- GitHub Actions run: `37595757999`

The two commits after the runtime implementation corrected false-positive
architecture guard assertions in tests; runtime source was unchanged.

## Runtime Scope Evidence

Runtime additions/changes:
- new `src/full_album_maker/beat_analysis.py`;
- AppKernel/CompositionRoot ownership and bounded context binding.

No Spectrum renderer/compiler source was changed.
No ProjectDocument model/schema source was changed.
No UI/workspace source was changed.
No dependency/build/release source was changed.
No M7 WorkspaceRegistry work was started.

## M2 Lifecycle Evidence

BeatAnalysisService:
- receives the AppKernel-owned TaskSupervisor;
- uses `get_or_create_scope("beat-analysis")`;
- submits async work through `TaskSupervisor.submit()`;
- exposes generation invalidation;
- contains no private ThreadPoolExecutor or direct worker-thread construction.

Focused async test proves invalidated analysis raises cancellation rather than
being accepted as current.

## M5 Cache Evidence

BeatAnalysisService receives the AppKernel-owned CacheManager and uses only the
`beat-analysis` namespace.

Cache key includes:
- SourceFingerprint token;
- namespace version;
- analyzer version;
- sample rate;
- detector timing parameters.

Focused tests prove:
- second identical analysis is a cache hit;
- source mutation changes fingerprint/cache identity;
- corrupt JSON is a disposable miss and gets recomputed;
- decoder failure does not create a fake cached result.

## D07 Fallback / Separation Evidence

BeatAnalysis is derived data only. No BeatResponse authored data is created or
stored.

Focused tests prove:
- deterministic event output for the same envelope;
- silence returns zero beat events;
- decoder failure returns `available=False`, empty envelope, empty beat list;
- no ProjectDocument/schema dependency was introduced.

## Real FFmpeg Evidence

Targeted real-FFmpeg job: **SUCCESS — 4 passed**.

It proves:
1. synthetic pulse WAV produces three real detected events near expected pulse
   times;
2. SHA-256 of source audio is identical before/after analysis;
3. real silence produces no reactive events;
4. existing Accurate Preview/final render and Spectrum Accurate Preview compiler
   parity tests continue to pass.

## Regression Results

Main M6 job: **SUCCESS**
- M0–M6 contracts: 58 passed, 4 skipped
- Beat/Spectrum parity: 19 passed, 1 skipped
- Accurate Preview/render parity: 7 passed, 1 skipped
- persistence + production shell: 12 passed
- 200-song/~3-hour structural stress: 2 passed

## Final-Head Rule

This evidence records the validated candidate. The following documentation-only
commit changes governance/evidence only. The same
`v2-m6-beat-analysis.yml` workflow must be green on the final branch head
before M6 handoff is complete.
