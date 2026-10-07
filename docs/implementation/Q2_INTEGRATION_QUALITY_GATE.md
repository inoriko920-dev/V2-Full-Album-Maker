# Q2 — Integration Quality Gate

Status: **PASS — full integration regression validated**

## Scope

Q2 is the STEP 10 Integration Quality Gate.

It validates:
- the complete current pytest regression floor;
- cross-workspace navigation/integration;
- session lifecycle;
- close/shutdown lifecycle;
- persistence/save/recovery integration;
- M0–M9 ownership boundaries.

Q2 does not perform Q3 infrastructure work, Q4 Windows artifact build, or Q5
release publication.

## Regression floor

The planning baseline documented 115 Python test files.

The Q2 candidate contains **123** `tests/test_*.py` files.

The Q2 workflow asserts that the test-file inventory may not fall below 115
before full pytest is allowed to run.

## Full pytest result

Candidate:
- branch: `quality-q2-integration`
- validated runtime/fix head:
  `98a8f096990f1135989997f4047340c3b5bbb270`
- GitHub Actions run: `37601017717`

Full repository pytest:
- **557 passed**
- **93 skipped**
- **0 failed**
- runtime: 59.26 seconds

This is the first post-M0–M9 quality gate in this sequence that executes the
entire current Python test suite in one job.

## Regression discovered by Q2

The first Q2 run exposed four failures in `tests/test_async_import.py`.

Failure:
- `full_album_maker.async_import.probe_duration` no longer existed after M5
  probe-facade migration.

The focused M5 tests had correctly proved production routing through
`MediaProbeService`, but the complete regression floor revealed a legacy
direct-window/test extension compatibility surface that was still contractual.

The failure was not hidden by editing/removing those tests.

## Q2 fix

`async_import.py` now restores a bounded direct-window compatibility adapter:

- module-level `probe_duration` remains patchable for legacy direct-window
  tests/extensions;
- image/audio metadata compatibility continues through the existing
  `visual_feature_module` probe functions;
- a `LEGACY_ASYNC_IMPORT_PROBE_SERVICE` wraps those call surfaces through
  `MediaProbeService`;
- production windows launched through AppKernel still capture and use the exact
  AppKernel-owned M5 `MediaProbeService`.

Therefore:
- production service ownership does not regress;
- direct legacy-window compatibility is restored;
- there is no second production authoritative probe owner.

Fix commit:
`98a8f096990f1135989997f4047340c3b5bbb270`

## Explicit cross-workspace/session/lifecycle evidence

After the full suite passes, Q2 reruns a focused integration set covering:
- STEP09 session flow;
- WorkspaceRegistry;
- STEP11 E2E navigation;
- STEP11 integration core;
- production integration;
- STEP11 lifecycle;
- close lifecycle;
- TaskSupervisor lifecycle;
- ProjectPersistence;
- dirty/save state;
- render lifecycle.

Result:
- **60 passed**
- **0 failed**

## M0–M9 ownership smoke

Q2 then reruns the architecture ownership contracts:
- FeatureParityRegistry;
- AppKernel;
- Task lifecycle;
- ProjectPersistence;
- RenderEngine;
- M5 media services;
- BeatAnalysis;
- WorkspaceRegistry;
- legacy bridge retirement;
- M9 consolidation.

Result:
- **72 passed**
- **4 skipped**
- **0 failed**

## Frozen contracts preserved

Q2 does not change:
- ProjectDocument schema v2;
- TIMEBASE=240000;
- all nine workspace routes/order;
- ProjectDocument/EditorSession authority;
- M2 TaskSupervisor ownership;
- M3 ProjectPersistence;
- M4 RenderEngine;
- M5 probe/preview/cache ownership;
- M6 BeatAnalysis;
- M7 WorkspaceRegistry;
- M8 retirement decisions;
- M9 consolidated production bootstrap;
- Step08 -> V13 -> S11 -> FFmpegV2 render semantics;
- UI design/workflow;
- build/release policy.

## Gate conclusion

Q2: **PASS**

Required evidence:
1. current test inventory >= baseline floor — PASS, 123 >= 115;
2. full pytest — PASS, 557 passed / 93 skipped;
3. cross-workspace/session/lifecycle — PASS, 60 passed;
4. M0–M9 ownership contracts — PASS, 72 passed / 4 skipped;
5. no unexplained flaky retry used to waive a failure — PASS;
6. discovered regression fixed in source rather than blessed by test deletion —
   PASS.

## Next

The next allowed quality gate is **Q3 — Infrastructure**:
- real FFmpeg tier evidence;
- UI capture matrix;
- structural/performance benchmarks.

Q3 is not started in this turn.
