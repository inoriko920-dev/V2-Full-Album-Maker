# V2-Full-Album-Maker — v2.0.4 patch quality-gate plan

Status: **P01 PASS; Q4 PASS/FROZEN; Q5 NOT STARTED; v2.0.4 NOT PUBLISHED**

## Repository and source fence

- Target only: `inoriko920-dev/V2-Full-Album-Maker`.
- Preparation branch: `release/prepare-v2.0.4-20261008`, based on `main` commit `224be664195065a83120bc7b6a917b76e850961a` (PR #52 merge).
- Original `inoriko920-dev/Full-Album-Maker` remains **read-only**.
- Latest published stable remains **v2.0.3**, frozen on Q4 SHA `ee61ca0af5d15cdc51af91ad48e05bc2b641f49d`.
- Its ZIP remains `189599847` bytes / SHA-256 `b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0`.
- No previous version's tag, asset, release notes, checksums or historical Q4/Q5 control should be modified.

## Scope since v2.0.3

| PR | Scope | Executable effect |
| --- | --- | --- |
| #50 | Correct stable README download and historic provenance | None |
| #51 | Harden release identity regression (exact Q5 ZIP checksum, size, commit) | None |
| #52 | Suppress thumbnail delivery/request after TemplateThumbnailCache.close; Qt lifecycle regressions | **Patch runtime** |

No UI redesign, project/schema migration, new dependency, FFmpeg/font pin change or architecture refactor.

## P01 — Candidate metadata and Windows validation

1. Change `2.0.3 → 2.0.4` only in package `__version__`, `pyproject.toml` and `build/release_manifest.json`.
2. Add `docs/RELEASE_NOTES_v2.0.4.md` with explicit `Release candidate — not published` and Q4/Q5 pending.
3. Keep public README pointing to the **published** v2.0.3 ZIP until Q5 really completes.
4. Protect immutable v2.0.3 Q5 evidence with dedicated tests; distinguish candidate assertions from stable assertions instead of weakening them.
5. Independently verify protected-main CI of PR #52 merge: [run 37743973995](https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37743973995) at exact `224be664195065a83120bc7b6a917b76e850961a` is **SUCCESS**.
6. Demand P01 exact final PR head Windows `build` SUCCESS, including full pytest, portable ZIP build, offline extracted audio+video smoke.
7. Only then squash-merge P01 and independently verify **new** protected-main Windows CI PASS at the merge commit.
8. Record the PR and exact run IDs/commit SHA in this gate plan/handoff when known; do not label any unverified gate PASS.

**Hard stop:** P01 merge is forbidden if either prerequisite CI or its own final-head Windows CI is pending or failed.

## Q4 — Freeze immutable Windows artifact (blocked until P01 protected-main PASS)

1. Create a new `.github/workflows/v2-q4-v2.0.4-windows-artifact.yml`, adapted from v2.0.3 without editing any historical workflow.
2. Restrict Q4 to a dedicated `release/q4-v2.0.4` branch, with `contents: read` and no release publication.
3. Verify manifest + `__version__` + pyproject + candidate notes all equal `2.0.4`.
4. Verify exact dependency lock, pinned Python 3.12.10, SHA-pinned FFmpeg, Noto Sans, third-party notices and license alignment.
5. Execute full regression, pinned real FFmpeg external filter-script test, secrets scan, Windows onedir packaging and extracted Unicode/apostrophe-path **offline audio+video smoke** without global Python/FFmpeg or API keys.
6. Freeze Q4 **candidate commit SHA, run/job IDs, Actions artifact ID/name, inner ZIP exact byte size and SHA-256** in `docs/implementation/Q4_V2_0_4_EVIDENCE.md`.
7. No Q5 workflow may use a merge SHA or a freshly rebuilt ZIP instead of the exact frozen Q4 artifact.

**Hard stop:** any post-freeze executable or build change invalidates the Q4 candidate and requires new Q4 evidence.

## Q5 — No-rebuild stable publication (blocked until Q4 PASS)

1. Independently verify Q4 full status and protected-main state; v2.0.4 tag/release must not already exist.
2. Create a separate `.github/workflows/v2-q5-v2.0.4-release.yml` anchored to actual Q4 SHA/run/artifact/hash/bytes, on a dedicated `release/q5-v2.0.4` branch.
3. Download **that** Actions artifact, extract the wrapper, verify inner `Full-Album-Maker-v2.0.4-Windows-Portable.zip`, SHA256SUMS, exact bytes/hash, build commit and bundled pinned manifest/notices.
4. Re-run isolated offline extracted ZIP audio+video smoke; any mismatch fails closed **before publication**.
5. Publish the untouched Q4 ZIP and SHA256SUMS; new tag must target the exact frozen Q4 **candidate SHA**.
6. Re-download the newly published assets; independently re-check stable flags, tag ref, ZIP byte size, SHA-256 and checksum file.
7. Archive `docs/implementation/Q5_V2_0_4_EVIDENCE.md`, stable release notes, project status and handoff, then update README to v2.0.4 with exact verified facts.
8. Preserve v2.0.3/v2.0.2/v2.0.1/v2.0.0 rollback assets.

**Hard stop:** do not call any Q5/stable step complete until the actual published release passes independent verification.

## Current gates

| Gate | State | Evidence |
| --- | --- | --- |
| Source PR #52 exact head | PASS | 37743420847: 780 tests + Windows portable smoke |
| PR #52 protected-main | **PASS** | 37743973995, SHA `224be664195065a83120bc7b6a917b76e850961a` |
| v2.0.4 P01 branch | **PASS/MERGED** | PR #53, 782 tests run 37744463640, post-merge main 37745055766 PASS |
| v2.0.4 Q4 artifact | **PASS/FROZEN** | SHA `af5af1ce24aba17ff68d469390a0c3d21f80f44d`, run 37745568166, artifact 11536240883, 189599237 bytes, SHA-256 `888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b` |
| v2.0.4 Q5 published | NOT STARTED | No tag/release is authorized yet |

## Handoff

Read `docs/governance/AI_HANDOFF.md`, `docs/governance/PROJECT_STATUS.md`, `docs/governance/POST_RELEASE_MAINTENANCE.md` and the immutable Q4/Q5 v2.0.3 evidence. Do not invent artifact identities, merge without exact-head CI or publish from routine `main` validation.


## Verified Q4 freeze — October 8, 2026

This supersedes the earlier Q4-NOT-STARTED planning language while retaining the original gate decisions and audit trail.

- P01 PR #53 exact-head Windows run `37744463640`: **782 tests and portable smoke PASS**. Squash merged to protected main `b7824e68c7fc26de07555ebee2866080c948ab1b`; post-merge run `37745055766`: **PASS**.
- Q4 PR #54 exact candidate and workflow commit: `af5af1ce24aba17ff68d469390a0c3d21f80f44d`. Isolated Q4 run `37745568166`: **782 tests, additional pinned FFmpeg test, metadata, secrets, artifact identity, extracted offline audio/video smoke PASS**.
- Exact **inner portable ZIP**: `Full-Album-Maker-v2.0.4-Windows-Portable.zip`; **189599237 bytes**; SHA-256 `888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b`.
- GitHub Actions wrapper artifact **ID `11536240883`**, name `q4-v2.0.4-windows-artifact-candidate`. Wrapper digest is **not** the inner ZIP digest.
- Generic PR #54 Windows run `37745591187`: **782 tests and portable smoke PASS**.
- PR #54 merged to `main` at `1ebbb49d0ecfc2da1b450d5f7142af879728a9d9`. This merge SHA is **not** the frozen Q4 build SHA.
- Verify Q4 post-merge protected-main run **`37746119351`** PASS before starting Q5. It was pending when Q4 evidence was first authored.
- Exact source-of-truth: `docs/implementation/Q4_V2_0_4_EVIDENCE.md`.
- Q5 is **NOT STARTED**; do not publish/rebuild/retag v2.0.4, or modify v2.0.3 and earlier stable assets.
