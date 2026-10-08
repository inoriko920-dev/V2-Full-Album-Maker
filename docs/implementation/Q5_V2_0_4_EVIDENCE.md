# Q5 v2.0.4 — Stable Release Publication Evidence

Status: **PASS — Stable v2.0.4 PUBLISHED**

## Immutable published release identity

| Field | Verified |
| --- | --- |
| Stable version and tag | `v2.0.4` |
| Release ID | `406580160` |
| Exact Q4 candidate source and tag commit | `af5af1ce24aba17ff68d469390a0c3d21f80f44d` |
| Q4 Actions run / artifact ID | `37745568166` / `11536240883` |
| Q5 Actions run / control SHA | `37747917087` / `1e41dcf974d3302ae835b8efd3195d420de0c552` |
| Q5 Windows job | `113213739103` |
| Published at UTC | `2026-10-08T08:09:44Z` |
| Published at WIB | `2026-10-08 15:09:44 WIB` |
| Published portable ZIP | `Full-Album-Maker-v2.0.4-Windows-Portable.zip` |
| Exact ZIP bytes | `189599237` |
| Exact portable ZIP SHA-256 | `888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b` |
| Q5 evidence Actions artifact ID | `11536193084` |
| Published flags | `draft=false`; `prerelease=false` |

Stable release: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.4

Direct ZIP: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.4/Full-Album-Maker-v2.0.4-Windows-Portable.zip

Checksum file: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.4/SHA256SUMS.txt

## Quality gates — Q4 PASS, Q5 PASS

1. Q4 Windows workflow run `37745568166` PASS at exact source SHA `af5af1ce24aba17ff68d469390a0c3d21f80f44d`: **782 regression tests PASS**, **1** pinned real FFmpeg external-filter test PASS, Windows onedir packaging, extracted Unicode/apostrophe-path offline audio/video smoke PASS.
2. Q4 artifact `11536240883`, name `q4-v2.0.4-windows-artifact-candidate`, existed, was not expired, and was tied to that exact successful Q4 run. The Actions wrapper's hash/size differ from the **inner portable ZIP**.
3. Q4 PR #54 exact-head validation run `37745591187` PASS. Protected-main post-merge run `37746119351` PASS. Q4 evidence PR #55 exact-head run `37746382025` PASS; post-merge protected-main run `37746897742` PASS.
4. Q5 control branch was created directly from the **exact frozen Q4 commit**. Its only content diff from Q4 is the new `.github/workflows/v2-q5-v2.0.4-release.yml` workflow, which contains no executable/packager rebuild step.
5. Q5 workflow run `37747917087` PASS. Its log verified `Q5_PROVENANCE_NO_REBUILD_PASS`, `Q5_UNUSED_TAG_RELEASE_PASS`, `Q5_ROLLBACK_PASS v2.0.3`, `Q5_FROZEN_ARTIFACT_IDENTITY_PASS`, `Q5_EMBEDDED_PROVENANCE_PASS`, `Q5_EXACT_ZIP_SMOKE_PASS`, `Q5_SECRET_METADATA_PASS`, and `Q5_RELEASE_PUBLICATION_PASS`.
6. Q5 downloaded the actual Q4 artifact and extracted the inner ZIP; it verified **189599237 bytes**, SHA-256 `888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b` and SHA256SUMS.txt.
7. Verified embedded CAPABILITIES.json and release manifest, pinned FFmpeg/font/notices, frozen source build commit, and absence of secret leaks.
8. Re-ran extracted **unchanged** Windows ZIP offline A/V smoke with no global Python, global FFmpeg or provider API keys.
9. Published the **exact Q4 ZIP and SHA256SUMS.txt** without rebuilding, repacking or recompressing. Tag `v2.0.4` points directly to the frozen Q4 candidate commit, *not* the Q4 squash-merge, evidence merge or Q5 control commit.
10. Re-downloaded the published ZIP/checksum and confirmed exact bytes, SHA-256, tag commit, release flags and asset names. Workflow log Q5 summary recorded `publication_performed=true` and `published_asset_redownload_verified=true`. Overall run ended `completed/success`.

**exact_zip_rebuilt = false**

**published_asset_redownload_verified = true**

**publication_performed = true**

Q5 evidence artifact `11536193084`, name `q5-release-evidence`, was uploaded successfully during run `37747917087`.

## Previous stable and rollback

Published stable v2.0.3 remains unchanged:
- tag/source commit `ee61ca0af5d15cdc51af91ad48e05bc2b641f49d`;
- `Full-Album-Maker-v2.0.3-Windows-Portable.zip`, exactly `189599847` bytes;
- SHA-256 `b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0`.

Older v2.0.2, v2.0.1 and v2.0.0 releases remain untouched; original `inoriko920-dev/Full-Album-Maker` repository remains untouched.

All published tags, exact ZIPs and checksums are immutable. A later executable change requires a new version with independent Q4/Q5 validation.

**v2.0.4 Q4 PASS. v2.0.4 Q5 PASS. STABLE v2.0.4 PUBLISHED.**
