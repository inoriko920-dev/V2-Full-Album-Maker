# P01 v2.0.5 — patch candidate release quality plan (ASTRA → SOL)

Status: **PLANNING ONLY; P01 NOT STARTED; Q4 NOT STARTED; Q5 NOT STARTED; v2.0.5 NOT PUBLISHED**

Documentation authored **8 October 2026 WIB**. The associated DOCX is the planning handoff; this Markdown is the machine-auditable source of truth.

## 0. Scope and repository boundaries

- Work **only** on `inoriko920-dev/V2-Full-Album-Maker`. Never edit `inoriko920-dev/Full-Album-Maker`.
- Base protected `main` commit: `e5bd1a68b8cd3dd14edd41f51676c7d9f84bd5f1`, merging Beat Analysis cache correctness PR [#57](https://github.com/inoriko920-dev/V2-Full-Album-Maker/pull/57).
- Exact PR #57 Windows CI **37750219397 PASS**, `790 passed` + Windows portable audio/video smoke PASS.
- Independent protected-main CI after merge **37750771995 PASS** at `e5bd1a68b8cd3dd14edd41f51676c7d9f84bd5f1`: `790 passed`, Windows packaging and portable audio/video smoke PASS.
- Official/latest **published** stable stays v2.0.4 until v2.0.5 independently passes Q5.
- Rollback v2.0.4 tag/Q4 source: `af5af1ce24aba17ff68d469390a0c3d21f80f44d`; exact ZIP `Full-Album-Maker-v2.0.4-Windows-Portable.zip` **189599237 bytes**, SHA-256 `888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b`. v2.0.3 and all earlier versions remain immutable.

## 1. Bug fixed in source, waiting for patch release

The v2.0.4 binary does **not** include PR #57. The corrected BeatAnalysisService._load_cache() no longer falsely treats parseable but malformed cache as valid when it contains non-object beat elements, invalid normalized envelope fields, oversized JSON numbers, type-wrong beat strength or timestamps beyond audio duration. It discards/recreates **only disposable cache**; it never changes an original audio file or authored project data. Eight new parametrized regressions verify recalculation, subsequent cache hit, and byte-for-byte unchanged source audio.

## 2. P01 exact change allowlist

| REQUIRED | EXPLICITLY FORBIDDEN |
| --- | --- |
| Bump only package `__version__`, `pyproject.toml` `version` and `build/release_manifest.json` target to `2.0.5` | Modify already-published v2.0.4 tag, ZIP, SHA256SUMS or historical Q4/Q5 workflows |
| Create `docs/RELEASE_NOTES_v2.0.5.md` stating **Release candidate — not published** and Q4/Q5 pending | Mark candidate as stable or fabricate candidate Q4 SHA/artifact ID/checksum |
| Update tests to preserve README download `v2.0.4` until v2.0.5 Q5 success | Prematurely change README download to v2.0.5 |
| Add candidate-vs-published-stable tests, retain historical v2.0.4/3/2/1/0 evidence | Modify runtime code PR #57, UI, schema, project persistence, FFmpeg/font, dependency pins |
| Full exact-head Windows regression and portable build/smoke before merge | Merge pending/failed checks or publish from routine main validation |

No application code or UI should be changed by P01; this is version/release metadata and release validation only.

## 3. P01 implementation order and hard gates

1. **Prerequisite gate:** independently confirm PR #57 protected-main CI `37750771995` SUCCESS on exact source commit; v2.0.5 tag/release **absent**; v2.0.4 rollback intact. FAIL → STOP.
2. Ensure the **planning DOCX** and this full plan are available as an immutable checked-in handoff before any metadata/runtime changes. FAIL → STOP.
3. Create branch `release/prepare-v2.0.5-20261008` from verified protected main.
4. Bump only **three** version fields `2.0.4 → 2.0.5`; preserve pinned Python 3.12.10, pip 26.2.1, Qt, FFmpeg SHA, fonts and lock files.
5. Add candidate notes with exact #57 regression scope and no claimed Q4/Q5 outputs.
6. Adjust version-aware tests: package metadata and manifest must be 2.0.5; candidate notes must be unpublished/Q4/Q5 pending; **published stable identity tests remain v2.0.4** including 189599237 bytes, SHA-256 and frozen source SHA. Protect older Q5 evidence.
7. Audit PR exact diff: no unintended source/UI/project/pin/workflow/release changes.
8. Run full GitHub Windows CI at **exact final PR head**; prove full pytest, packaged Windows executable and extracted portable audio/video smoke PASS.
9. If failure, fix on PR branch and rerun on its latest commit; never substitute an older successful workflow.
10. Squash-merge only after exact-head CI completed SUCCESS and no merge conflicts. Verify protected-main post-merge CI SUCCESS at resulting merge SHA.
11. Record all actual PR/run/commit IDs without inventing PASS. **Q4 blocked** until final main gate PASS.

## 4. Q4 v2.0.5 — immutable candidate ZIP

1. After P01 protected-main PASS only: create a new isolated `.github/workflows/v2-q4-v2.0.5-windows-artifact.yml` on `release/q4-v2.0.5`. Do not edit old release workflows.
2. Verify app version, pyproject, canonical release manifest and candidate notes exactly `2.0.5`.
3. Audit pins/licenses/provenance: Python 3.12.10, pinned Qt/wheels/pip, FFmpeg exact GitHub asset SHA-256, Noto Sans commit, THIRD_PARTY_NOTICES, secret scan.
4. Run full Windows regression (>=790 existing tests), **real FFmpeg external-filter script**, package PyInstaller onedir, then extracted Unicode/apostrophe-path **offline A/V smoke** with no global Python, FFmpeg or API keys.
5. Freeze **exact Q4 source SHA**, run ID/job ID, Actions artifact name/ID, actual **inner ZIP** name/bytes/SHA-256, check `SHA256SUMS.txt`, artifact expiry, embedded manifest/provenance. Distinguish GitHub artifact **wrapper** hash/size from inner ZIP.
6. Archive `docs/implementation/Q4_V2_0_5_EVIDENCE.md`; validate PR and protected-main after merge. Q4 never creates a stable release or tag.
7. Any executable/source/build change after freeze requires a **new** Q4 candidate and full retest. No placeholder artifact IDs.

## 5. Q5 v2.0.5 — publish exact Q4 artifact **without rebuilding**

1. Require Q4 PASS, Q4 postmerge main CI PASS, Q4 evidence recorded and its PR/main CI PASS; confirm `v2.0.5` tag and release still absent and v2.0.4 rollback immutable.
2. Create new `.github/workflows/v2-q5-v2.0.5-release.yml` on `release/q5-v2.0.5` branching **directly from exact frozen Q4 source commit**, with only the new release workflow added (no runtime changes).
3. Fetch the Q4 Actions wrapper by exact artifact ID and run ID; extract exact inner `Full-Album-Maker-v2.0.5-Windows-Portable.zip`, verify inner bytes/SHA-256, SHA256SUMS, Q4 source SHA and packaged manifest/pins/notices.
4. Repeat extracted **unchanged** ZIP offline A/V smoke with no global tools or provider keys; secret and permission/provenance safety checks.
5. Only if all gates PASS, publish **that same** ZIP/SHA256SUMS. New `v2.0.5` tag must point at frozen Q4 source SHA, not PR/squash merge or Q5 control SHA. **No rebuild, repack or recompression.**
6. Download the actual published assets again; verify tag commit, release flags `draft=false` and `prerelease=false`, byte size, SHA-256, checksum file and asset name. FAIL → do not claim PASS.
7. Archive `docs/implementation/Q5_V2_0_5_EVIDENCE.md`, update stable notes/README download/checksum/AI handoff only **after** successful publication. Previous v2.0.4, v2.0.3 etc. never overwritten.

## 6. Failure, recovery and rollback rules

| Failure | Required behavior |
| --- | --- |
| PR P01 CI pending/failed | STOP merge. Fix/retest exact head. |
| P01 protected-main CI pending/failed | STOP Q4. |
| Q4 pinned dependency/regression/real FFmpeg/smoke fail | STOP freeze; no stable publication. |
| Q4 artifact, SHA, bytes or source not identical | STOP Q5. Do not rebuild/repack the pinned Q4 ZIP. |
| Existing v2.0.5 tag/release detected | STOP publishing; audit existing record rather than overwrite. |
| Q5 post-publication independent verification failed | Do not declare release PASS; preserve evidence and v2.0.4 rollback, investigate actual GitHub state. |
| Runtime/UI/schema change discovered | Reject out-of-scope PR and obtain a new plan/release gate. |

## 7. Handoff and final acceptance

A user-downloadable **v2.0.5 stable** is accepted only after source P01 gate, Q4 frozen artifact proof and independent no-rebuild Q5 publication/re-download PASS. All PASS claims must include exact GitHub run IDs, artifact IDs and SHA-256 in committed evidence. In the meantime, latest published stable is **v2.0.4** (see its Q4/Q5 evidence). The original `Full-Album-Maker` repo and prior stable ZIPs/tags stay immutable. Read `docs/governance/AI_HANDOFF.md`, `docs/governance/PROJECT_STATUS.md`, `docs/governance/POST_RELEASE_MAINTENANCE.md` and older Q4/Q5 workflows as **references**, not a publishing shortcut.
