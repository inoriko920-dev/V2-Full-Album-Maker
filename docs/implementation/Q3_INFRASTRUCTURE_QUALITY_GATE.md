# Q3 — Infrastructure Quality Gate

Status: **PASS — infrastructure evidence validated**

## Scope

Q3 is the STEP 10 Infrastructure Quality Gate.

It validates:
- real FFmpeg / ffprobe behavior on Linux infrastructure;
- deterministic UI capture evidence for all nine workspaces;
- 200-song / ~3-hour structural behavior;
- same-runner performance comparison against the final Q2 baseline;
- the declared Python >=3.11 compatibility lane.

Q3 does **not** build the Windows portable artifact and does not publish a
release. Q4/Q5 remain blocked until their own gates.

## Candidate

- Branch: `quality-q3-infrastructure`
- Q2 base:
  `e673bbcd2812a93c6bb59c36448d58b1215037b5`
- Initial Q3 infrastructure commit:
  `b1aabab1638e010ae662c5109129f9d692777750`
- Scope correction:
  `af98388eeb2c0eecb84bfe1cdbd44fdcad6d1385`
- Successful Actions run:
  `37602494015`

Q3 changes no production runtime source. The diff from Q2 contains only:
- `.github/workflows/v2-q3-infrastructure.yml`;
- `tests/q3_benchmark_runner.py`.

## Real FFmpeg infrastructure matrix

Linux runtime:
- FFmpeg 6.1.1-3ubuntu5
- Python 3.12
- Qt offscreen runtime

Validated real-infrastructure coverage:
- MediaProbeService real audio duration probing;
- BeatAnalysis real pulse detection;
- BeatAnalysis silence/non-reactive fallback;
- STEP10 real render + ffprobe verified publication;
- real final-render vs Accurate Preview parity;
- all release Spectrum styles;
- real Spectrum silence / Accurate Preview compiler parity.

Result:
- **10 passed**
- **0 failed**

## First-run FFmpeg scope finding

The first Q3 run failed only on:

`tests/test_editor_v2_s12_performance.py::test_real_ffmpeg_accepts_external_filter_script`

Ubuntu FFmpeg reported:

`Unrecognized option '/filter_complex'.`

This is not treated as an application regression because that test explicitly
documents its purpose as proving the **pinned Windows FFmpeg build** supports
the `-/filter_complex` indirection syntax.

Q3 does not delete or weaken that test.

The test remains required evidence for **Q4 Windows Artifact**, where the exact
shipping Windows FFmpeg pin is available.

The corrected Q3 Linux matrix records this scope explicitly and keeps the
structural command-indirection tests green without making a false claim about
the Ubuntu package.

## UI capture matrix

Fresh deterministic screenshots were generated for all nine production
workspaces at the canonical functional capture viewport:

- 1672 x 941
- 100% scale
- Beranda
- Media
- Album
- Timeline
- Visual
- Template
- Spectrum
- AI Agent
- Render

Each screenshot:
- exists and is non-empty;
- is exactly 1672 x 941;
- has a JSON geometry report;
- reports the expected canonical route;
- is included in the uploaded Q3 UI evidence artifact.

Result:
- **9/9 functional UI captures PASS**

### Pixel-match claim

Q3 explicitly does **not** claim pixel-match PASS.

`docs/ui-reference/manifest.json` preserves the nine canonical reference
identities, but the exact multi-megabyte golden PNG payloads are intentionally
not checked into this branch.

STEP10 D10-13 states that functional UI PASS and pixel-match PASS are separate
claims.

Therefore Q3 records:
- functional UI capture matrix: **PASS**;
- pixel-match status: **NOT CLAIMED**.

The existing post-release golden audit remains the source describing previously
measured visual gaps. Q3 neither modifies golden references nor falsely closes
that separate visual-remediation concern.

## Structural 200-song / ~3-hour evidence

Existing structural gates were rerun:
- Packed mode, 200 songs x 54 seconds;
- Free mode, 200 songs x 54 seconds.

Both resolve to exactly 10,800 seconds (~3 hours), keep empty error lists, and
retain bounded command construction.

Result:
- **2 passed**
- **0 failed**

## Same-runner performance comparison

Baseline:
`e673bbcd2812a93c6bb59c36448d58b1215037b5`

Candidate:
`af98388eeb2c0eecb84bfe1cdbd44fdcad6d1385`

Both were benchmarked on the same GitHub runner with the same Python process
environment.

Median timings:

| Metric | Q2 baseline | Q3 candidate | Delta |
| --- | ---: | ---: | ---: |
| Packed resolve | 1.5557 ms | 1.5371 ms | -1.19% |
| Free resolve | 1.7457 ms | 1.7350 ms | -0.61% |
| Packed compile | 10.4497 ms | 10.2687 ms | -1.73% |
| Free compile | 10.9820 ms | 10.8860 ms | -0.87% |

STEP10 requires investigation for a >10% same-environment regression.

Q3 result:
- regressions over 10%: **none**;
- performance comparator: **PASS**.

## Python 3.11 compatibility lane

STEP10 D10-02 requires the declared Python >=3.11 support claim to be tested or
explicitly revised.

Q3 ran the complete repository pytest suite on Python 3.11.

Result:
- **557 passed**
- **93 skipped**
- **0 failed**

The >=3.11 support claim therefore has direct CI evidence.

## Frozen contracts preserved

Q3 does not change:
- ProjectDocument schema v2;
- TIMEBASE=240000;
- ProjectDocument/EditorSession authority;
- all nine route identifiers/order;
- M2–M9 service ownership;
- Q2 compatibility fix;
- Step08 -> V13 -> S11 -> FFmpegV2 semantics;
- UI production implementation;
- dependencies or release version;
- Windows packaging;
- stable release automation.

## Gate conclusion

Q3: **PASS**

Required evidence:
1. real FFmpeg infrastructure matrix — PASS, 10 tests;
2. UI capture matrix — PASS, 9/9 functional captures;
3. 200-song/~3-hour structural tests — PASS, 2 tests;
4. same-runner performance comparison — PASS, no >10% regression;
5. Python 3.11 compatibility — PASS, 557 passed / 93 skipped;
6. Windows-only external filter-script test remains deferred to Q4, not waived;
7. pixel-match is not falsely claimed.

## Next

The next allowed quality gate is **Q4 — Windows Artifact**.

Q4 must validate the exact Windows portable build, exact pinned Windows FFmpeg,
extracted-ZIP smoke/isolation, checksums, and supply-chain/release blockers.

Q4 is not started in this turn.
