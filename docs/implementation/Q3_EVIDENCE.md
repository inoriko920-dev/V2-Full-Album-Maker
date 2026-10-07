# Q3 Infrastructure Evidence

Status: **PASS**

## Branch / candidate

- Branch: `quality-q3-infrastructure`
- Q2 base:
  `e673bbcd2812a93c6bb59c36448d58b1215037b5`
- Initial Q3 workflow:
  `b1aabab1638e010ae662c5109129f9d692777750`
- Validated scope correction:
  `af98388eeb2c0eecb84bfe1cdbd44fdcad6d1385`
- Successful Actions run:
  `37602494015`

## Real FFmpeg

Job: `real-ffmpeg-q3`

Result:
- 10 passed
- 0 failed

Coverage includes real probe, BeatAnalysis, final render + ffprobe verification,
Accurate Preview parity, release Spectrum styles, and Spectrum silence parity.

Initial run `37602128417` produced 10 passed / 1 failed because Ubuntu FFmpeg
6.1.1 does not support `-/filter_complex`.

The failing test explicitly targets the pinned Windows FFmpeg capability and
remains unchanged for Q4. It was removed only from the Linux Q3 matrix, not from
the repository.

## UI capture matrix

Job: `ui-capture-matrix-q3`

Result:
- nine fresh captures generated;
- 9/9 route reports validated;
- all images exactly 1672 x 941;
- evidence artifact uploaded;
- functional UI capture status: PASS;
- pixel-match status: NOT CLAIMED.

Golden identities remain frozen in
`docs/ui-reference/manifest.json`. Exact golden binary payloads are not
present in this branch, so Q3 does not fabricate pixel-match evidence.

## Structural / performance

Job: `structural-performance-q3`

Structural tests:
- 2 passed

Candidate duration:
- 200 songs x 54 seconds = 10,800 seconds.

Same-runner comparator against Q2 final head:

- Packed resolve: -1.19%
- Free resolve: -0.61%
- Packed compile: -1.73%
- Free compile: -0.87%

Regressions >10%:
- none

Result:
- PASS

Benchmark JSON evidence is uploaded by the workflow.

## Python 3.11

Job: `python311-compat-q3`

Full pytest:
- 557 passed
- 93 skipped
- 0 failed

Result:
- declared Python >=3.11 compatibility has direct Q3 evidence.

## Scope

Q3 diff contains only:
- infrastructure workflow;
- benchmark runner.

No production runtime source changes were required.

## Q4 blocker carried forward

The Windows-only
`test_real_ffmpeg_accepts_external_filter_script` must run against the exact
pinned Windows FFmpeg in Q4.

Q3 does not waive this requirement.

## Final-head rule

A documentation-only Q3 final commit follows this evidence. The same Q3
workflow must remain green on that final branch head before handoff is complete.
