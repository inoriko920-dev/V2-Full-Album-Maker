# Q5 v2.0.5 — Stable Release Publication Evidence

Status: **PASS — Stable v2.0.5 PUBLISHED**

## Immutable published release identity

| Field | Verified |
| --- | --- |
| Stable version and tag | `v2.0.5` |
| Release ID | `406656131` |
| Exact Q4 candidate source and tag commit | `645fa166aa7a4cdc372b80c82db09026a7ab9b95` |
| Q4 Actions run / artifact ID | `37754857699` / `11540026862` |
| Q5 Actions run / control SHA | `37756942493` / `d7ed9f2191484fbd8a2e66f726b53634c5a9a482` |
| Q5 Windows job | `113243707978` |
| Published at UTC | `2026-10-08T09:29:52Z` |
| Published at WIB | `2026-10-08 16:29:52 WIB` |
| Published portable ZIP | `Full-Album-Maker-v2.0.5-Windows-Portable.zip` |
| Exact ZIP bytes | `189598540` |
| Exact portable ZIP SHA-256 | `8a3cdc694b003cb8d1aff3e9a3e7d68591b0fd3b4106a29cea94dd9f45b82f74` |
| Q5 evidence Actions artifact ID | `11540114007` |
| Published flags | `draft=false`; `prerelease=false` |

Stable release: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.5

Exact ZIP: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.5/Full-Album-Maker-v2.0.5-Windows-Portable.zip

Checksum file: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.5/SHA256SUMS.txt

## Independent Q4 and Q5 quality gates

1. Q4 exact Windows workflow `37754857699` finished **completed/success** on exact build source `645fa166aa7a4cdc372b80c82db09026a7ab9b95`. Full Windows regression: **791 tests PASS**. Additional real pinned FFmpeg external-filter-script test: **1 PASS**. Extracted Unicode/apostrophe-path offline audio/video smoke PASS; no global Python, global FFmpeg or API key required.
2. Q4 artifact `11540026862` (`q4-v2.0.5-windows-artifact-candidate`) was present, unexpired and linked to Q4 run and exact frozen source SHA. Its **Actions wrapper** size `189251417` and SHA-256 `c2e76c52e48a23773e342fc9e2528a218ad66c2aa3a52a1eae6249be0ee7c078` are **not** the inner ZIP's size and checksum.
3. Q4 PR #60 exact-head Windows run `37754885928` PASS. Q4 merge protected-main run `37755534261` PASS. Q4 evidence PR #61 exact-head Windows run `37755797199` PASS; evidence merge protected-main run `37756315130` PASS (**791 tests** and portable smoke).
4. Q5 control branch `release/q5-v2.0.5` was created directly from frozen Q4 SHA `645fa166aa7a4cdc372b80c82db09026a7ab9b95`. The entire diff from that SHA was **only** `.github/workflows/v2-q5-v2.0.5-release.yml`. Q5 did not change source, packages or build inputs after Q4.
5. Q5 release workflow `37756942493` on control commit `d7ed9f2191484fbd8a2e66f726b53634c5a9a482` finished **completed/success**. Its job `113243707978` passed every gate.
6. Logs proved `Q5_PROVENANCE_NO_REBUILD_PASS`, `Q5_UNUSED_TAG_RELEASE_PASS`, `Q5_ROLLBACK_PASS v2.0.4`, `Q5_FROZEN_ARTIFACT_IDENTITY_PASS`, `Q5_EMBEDDED_PROVENANCE_PASS`, `Q5_EXACT_ZIP_SMOKE_PASS`, `Q5_SECRET_METADATA_PASS`, and `Q5_RELEASE_PUBLICATION_PASS`.
7. Q5 downloaded **exact Q4 artifact ID `11540026862`**, extracted `Full-Album-Maker-v2.0.5-Windows-Portable.zip`, verified **189598540 bytes**, SHA-256 `8a3cdc694b003cb8d1aff3e9a3e7d68591b0fd3b4106a29cea94dd9f45b82f74`, and the companion SHA256SUMS.txt. Embedded `CAPABILITIES.json`, `RELEASE_MANIFEST.json`, pinned FFmpeg/font and third-party notices were rechecked.
8. Q5 re-extracted **that same unchanged ZIP** in a Unicode/apostrophe-path directory and ran portable audio/video smoke with no global Python, FFmpeg or provider API keys, then passed secret and metadata validation.
9. Q5 published the **exact** Q4 ZIP and SHA256SUMS.txt **without rebuilding/repacking/recompressing** as GitHub release `406656131`, dated `2026-10-08T09:29:52Z` / **16:29:52 WIB**, with `draft=false` and `prerelease=false`. The new lightweight tag `v2.0.5` directly points to **frozen Q4 commit**, *not* workflow control, merge or documentation SHA.
10. The publication workflow **re-downloaded the published ZIP and SHA256SUMS.txt**, verified ZIP bytes, SHA-256, checksum file, tag SHA, release flags and asset presence. Its actual summary reported `status: PASS_PUBLISHED`, `exact_zip_rebuilt: false`, `publication_performed: true`, `published_asset_redownload_verified: true`. Overall workflow finished **SUCCESS**. Evidence artifact `11540114007`, name `q5-release-evidence`, uploaded successfully.

**exact_zip_rebuilt = false**

**published_asset_redownload_verified = true**

**publication_performed = true**

## Previous stable and rollback — immutable

Latest previous stable `v2.0.4` remains unchanged:
- Tag/source SHA `af5af1ce24aba17ff68d469390a0c3d21f80f44d`.
- `Full-Album-Maker-v2.0.4-Windows-Portable.zip`, exactly `189599237` bytes.
- Published SHA-256 `888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b`.
- Historical evidence: `docs/implementation/Q5_V2_0_4_EVIDENCE.md`.

Earlier v2.0.3, v2.0.2, v2.0.1, v2.0.0 and the original repository `inoriko920-dev/Full-Album-Maker` remain untouched. Do not move or overwrite ANY published stable release/tag/asset. New executable work requires a later semantic version and new Q4/Q5 quality gates.

**v2.0.5: Q4 PASS, Q5 PASS, STABLE PUBLISHED AND VERIFIED.**
