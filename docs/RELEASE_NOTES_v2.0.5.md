# Full Album Maker v2.0.5 — Patch Release Candidate

Status: **Release candidate — not published**

**Q4 and Q5 pending.** This document describes a planned patch, **not** a published stable GitHub Release or downloadable v2.0.5 ZIP. The latest **published** stable remains v2.0.4.

Planned portable artifact: `Full-Album-Maker-v2.0.5-Windows-Portable.zip` (**not frozen, not published, no SHA-256 assigned**).

## Changes since stable v2.0.4

- **PR #57 — Beat Analysis corrupted cache recovery.** A parseable but malformed JSON Beat Analysis cache must not silently drop beat events or turn bad envelope elements into zeros. Invalid beat shapes/types, oversized numeric values, invalid envelope, and beats beyond source duration are discarded **as disposable cache**, followed by recomputation from the unchanged original source audio.
- Eight new parametrized regression cases confirm fresh computation, reuse of the repaired cache, and byte-for-byte unchanged audio.
- PR #57 final-head Windows CI: [37750219397](https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37750219397), **790 tests PASS**, Windows portable build and extracted audio/video smoke PASS.
- PR #57 protected-main post-merge CI: [37750771995](https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37750771995), **790 tests PASS**, Windows portable build and A/V smoke PASS, source commit `e5bd1a68b8cd3dd14edd41f51676c7d9f84bd5f1`.
- P01 planning documents: [PR #58](https://github.com/inoriko920-dev/V2-Full-Album-Maker/pull/58), planning DOCX and detailed quality plan; its protected-main CI [37752580397](https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37752580397) **790 PASS** at `a9143d0cfc62724bd3127a4cdbb6d6fe4a2e240d`.
- No redesign of UI, no project/schema migration, no new dependencies, no Python/FFmpeg/font pin change, no change to export/render engine.

## P01 candidate identity (not a Q4 artifact)

- Candidate version fields: package `__version__`, `pyproject.toml` and canonical `build/release_manifest.json` each `2.0.5`.
- Public README must continue to link the **verified published v2.0.4 ZIP**, size and SHA256SUMS until **v2.0.5 Q5 publication actually passes**.
- Full Windows regression and extracted portable A/V smoke must PASS on the **exact P01 PR head** before merging metadata.
- After P01 protected-main CI PASS, a **new** Q4 v2.0.5-specific workflow may generate and freeze the portable ZIP. That future Q4 must record the actual source commit, workflow run/job, Actions artifact ID, **inner ZIP bytes and SHA-256**.
- Q5 must fetch that precise Q4 artifact by ID, verify the **inner ZIP** and embedded manifest/pins, smoke-test unchanged bytes offline, publish tag pointing directly to **Q4 source SHA**, and independently re-download the published release/checksum. **No rebuild, repack or retag**.

**P01 NOT PUBLISHED. Q4 NOT STARTED. Q5 NOT STARTED.** Do not invent v2.0.5 ZIP metadata.

## Rollback / historical releases

Latest verified published stable remains [Full Album Maker v2.0.4](https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.4).

- Tag/source SHA: `af5af1ce24aba17ff68d469390a0c3d21f80f44d`.
- Published `Full-Album-Maker-v2.0.4-Windows-Portable.zip`: **189599237 bytes**.
- Published SHA-256: `888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b`.
- Official proof: `docs/implementation/Q4_V2_0_4_EVIDENCE.md` and `docs/implementation/Q5_V2_0_4_EVIDENCE.md`.
- v2.0.3, v2.0.2, v2.0.1 and v2.0.0 remain available and immutable. The original `inoriko920-dev/Full-Album-Maker` repository must remain unchanged.

## Release handoff

Read `docs/release/V2_0_5_GATE_PLAN.md`, `docs/release/V2_FULL_ALBUM_MAKER_P01_V2_0_5_PLAN_2026-10-08.docx` and `docs/governance/AI_HANDOFF.md`. Each gate requires **actual** GitHub PASS evidence. Do not conflate routine build artifact with frozen Q4 ZIP or stable Q5 release.

**Full Album Maker v2.0.5 is only a candidate.**
