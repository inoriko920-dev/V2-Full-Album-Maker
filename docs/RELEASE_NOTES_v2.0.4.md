# Full Album Maker v2.0.4 — Patch Release Candidate

Status: **Release candidate — not published**

**Q4 and Q5 pending.** This is an internal Windows patch candidate, **not** a public stable download. The latest published stable remains **v2.0.3**.

Planned artifact: `Full-Album-Maker-v2.0.4-Windows-Portable.zip` (**not frozen or published**).

## Changes since published v2.0.3

- **PR #52 — Template thumbnail close lifecycle:** a closed TemplateThumbnailCache no longer accepts new requests or emits cached-image results after closure, and in-progress completion callbacks are suppressed after close. A new Qt event-drain regression verifies late signal behavior, and another verifies closed cache-hit/new-request behavior.
- **PR #51 — Released ZIP identity regression:** tests verify the specifically labeled published v2.0.3 ZIP SHA-256, byte size and frozen source commit against Q5 evidence; unrelated matching hashes can no longer hide errors.
- **PR #50 — README stable download instructions:** the homepage now links the correct verified v2.0.3 ZIP and checksum instead of treating V2 source as an incomplete recovery archive.
- No redesign of the UI, no project/schema migration, no new Python packages, and no changes to the pinned Python 3.12.10, FFmpeg or font.

## Candidate source and evidence

- Runtime bug fix PR: [#52](https://github.com/inoriko920-dev/V2-Full-Album-Maker/pull/52).
- PR #52 exact-head Windows check: [37743420847](https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37743420847), **780 tests passed** and extracted portable audio/video smoke PASS.
- PR #52 squash-merge source SHA: `224be664195065a83120bc7b6a917b76e850961a`.
- Required post-merge protected-main run: [37743973995](https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37743973995), must independently be **SUCCESS** before P01 can merge.
- This release candidate prepares `__version__`, `pyproject.toml`, and the canonical release manifest for `2.0.4`. A P01 branch build is *not* a frozen Q4 artifact.

## P01, Q4 and Q5 release gates

1. **P01:** exact final v2.0.4 preparation PR HEAD must PASS full Windows regression, portable build and extracted offline audio/video smoke; independently verify the post-PR #52 protected-main run before merging. Then verify P01 protected-main CI.
2. **Q4:** create a **new** v2.0.4-specific Windows Quality Gate workflow rather than modifying historical controls. Verify versions and pinned dependencies, full regression, FFmpeg external-filter capability, provenance/licenses/secret scan, and offline extracted portable A/V smoke; freeze the exact candidate SHA, artifact ID, inner ZIP bytes and SHA-256.
3. **Q5:** only after Q4 PASS, create a **separate** v2.0.4 no-rebuild publisher that downloads the exact frozen Q4 ZIP, re-verifies all identities and offline smoke, points the new tag to exact Q4 candidate SHA, publishes only the same ZIP plus SHA256SUMS, then re-downloads and verifies the published assets.
4. **Evidence:** record Q4 and Q5 PASS, exact SHA/byte count, workflow and GitHub release IDs, and update the README/handoff only after actual publication verification.

**No v2.0.4 ZIP, artifact checksum, Q4 candidate SHA, tag or release should be assumed to exist until the corresponding gate proves it.**

## Previous stable and rollback (immutable)

Published stable: [v2.0.3](https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.3).

- Source/tag SHA: `ee61ca0af5d15cdc51af91ad48e05bc2b641f49d`.
- Published portable ZIP bytes: `189599847`.
- Published portable ZIP SHA-256: `b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0`.
- Q4 Windows Actions run: `37736530557`; Q5 publication run: `37737839379`.
- Q5 evidence: `docs/implementation/Q5_V2_0_3_EVIDENCE.md`.

All published v2.0.3, v2.0.2, v2.0.1, v2.0.0 tags/assets remain immutable. The original repository `inoriko920-dev/Full-Album-Maker` is read-only and must not be changed.

**v2.0.4 IS NOT YET PUBLISHED. Do not present the CI validation ZIP as a stable release.**
