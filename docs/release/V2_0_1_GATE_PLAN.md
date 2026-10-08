# v2.0.1 Maintenance Release — Gate Plan

Status: **PREPARATION IN PROGRESS; NOT APPROVED FOR PUBLICATION**

## Authority

- Repository: `inoriko920-dev/V2-Full-Album-Maker`. The original `Full-Album-Maker` is read-only.
- Base: post-merge `main` commit `cc95de6a1fb8e61a34aba8d8d3f6ba0ffe98f79c` (#31).
- Previous stable `v2.0.0` is immutable. Do not change the historical v2.0.0 Q4/Q5 control files, tag, or assets.
- This is a patch release (metadata persistence and concurrency bug fixes), not a feature wave.

## Work packages

### P01 — Candidate identity and source-of-truth
- Bump `__version__`, `pyproject.toml`, and `build/release_manifest.json` to 2.0.1, with no upgrades to pinned runtime dependencies or shipping FFmpeg/font.
- Add candidate notes `docs/RELEASE_NOTES_v2.0.1.md` without claiming it is stable.
- Preserve the historical Q5 v2.0.0 evidence and adjust tests that hardcoded 2.0.0 to distinguish frozen stable from new candidate.
- Require an exact Windows portable validation PASS on the final head before merge.

### P02 — Frozen Windows candidate Q4 (BLOCKED until P01 PASS)
- Run a version-aware Windows artifact gate from a separate candidate ref. Include exact output ZIP, extracted smoke, full regression, notices and supply-chain checks, secret scan and third-party pin parity.
- Record exact commit, build run ID, artifact ID, ZIP bytes and SHA-256. Freeze the triple `version | SHA | digest`.
- Documentation-only commits after freeze may not trigger or mutate the artifact.
- Reject any changed code, dependencies, version or build semantics after freeze without a new Q4 run.

### P03 — No-rebuild release Q5 (BLOCKED until P02 PASS)
- Use a new `v2.0.1`-specific publication control, not the historical hardcoded v2.0.0 Q5 workflow.
- Download the frozen Q4 Actions artifact (never build again).
- Verify version, exact ZIP checksum and bytes, candidate ancestry, provenance, bundled FFmpeg/font, isolation smoke and release notes.
- Verify `v2.0.1` tag/release unused and `v2.0.0` rollback published.
- Only then create stable tag and release; re-download assets, verify checksums/bytes and record evidence.

### P04 — After publication
- Record immutable release identity in project handoff and release docs.
- Retain the prior `v2.0.0` ZIP unchanged for side-by-side rollback.
- Do not claim completion until the exact published assets are re-downloaded and verified.

## Gate matrix

| Gate | PASS condition | On failure |
| --- | --- | --- |
| Source identity | 2.0.1 agrees across app, manifest, project metadata, candidate notes | Block build |
| Full Windows regression | All tests pass against the final commit | Fix branch and rerun |
| Portable smoke | Fresh extracted ZIP opens and renders A/V offline without global dependencies/API keys | Block freeze |
| Q4 artifact freeze | Exact candidate SHA + ZIP size + SHA-256 + artifact ID captured | Do not publish |
| Q5 no-rebuild | Frozen artifact verified, no rebuild, prepublication smoke PASS | Do not publish |
| Postrelease | Tag SHA, published ZIP digest/size, checksum re-download match | Mark release incomplete |

## Handoff to subsequent AI

Read `docs/governance/AI_HANDOFF.md`, `docs/governance/PROJECT_STATUS.md`, `docs/governance/POST_RELEASE_MAINTENANCE.md`, `docs/implementation/Q4_WINDOWS_ARTIFACT_QUALITY_GATE.md` and `docs/implementation/Q5_RELEASE_QUALITY_GATE.md`; preserve original frozen v2.0.0.
Review the latest `release/prepare-v2.0.1-20261008` PR and its exact CI head. Never re-use v2.0.0 workflow hardcoded candidate tuple to publish v2.0.1.

**Next authorized action:** complete P01 candidate PR and Windows gate. Do not publish in this preparation stage.
