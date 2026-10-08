# Q5 v2.0.2 — Stable Release Publication Evidence

Status: **PASS — Stable v2.0.2 PUBLISHED**

## Immutable stable release identity

| Field | Verified result |
| --- | --- |
| Semantic version and release tag | `v2.0.2` |
| Published GitHub Release ID | `406458763` |
| Exact frozen Q4 commit and published tag target | `2678b9f93364334c7eaf9ebad9ef7e079533716f` |
| Q4 Actions run | `37732261424` |
| Q4 frozen artifact ID | `11530243260` |
| Q5 Actions run | `37733519371` |
| Q5 control commit | `46b4970bc342a267bab36231aafcd323c0a073bc` |
| Published at (UTC) | `2026-10-08T05:40:50Z` |
| Published at (WIB) | `2026-10-08 12:40:50 WIB` |
| Exact published portable ZIP | `Full-Album-Maker-v2.0.2-Windows-Portable.zip` |
| Portable ZIP size | `189599767` bytes |
| Portable ZIP SHA-256 | `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64` |
| Portable ZIP GitHub asset ID | `620855299` |
| SHA256SUMS.txt GitHub asset ID | `620855301` |
| GitHub asset flags | draft=false, prerelease=false |

Stable release: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.2

Exact ZIP download: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.2/Full-Album-Maker-v2.0.2-Windows-Portable.zip

Checksum: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.2/SHA256SUMS.txt

## Q4 and Q5 gates — ALL PASS

1. Q4 Windows run `37732261424`: full **769 tests passed**; separate pinned FFmpeg external-filter-script test **1 passed**; Windows portable build and extracted Unicode/apostrophe-path smoke PASS; source provenance, SHA256SUMS, embedded capabilities/license, secrets and FFmpeg/font pins verified.
2. Frozen Actions artifact `11530243260` was verified as not expired; exact Q4 commit, run, name and identity matched.
3. Q5 `37733519371` provenance/no-rebuild gate PASS: candidate is ancestor of control branch and only new Q5 control differs.
4. Before publication, GitHub `v2.0.2` tag and release were unused; previously published `v2.0.1` existed as rollback.
5. Q5 downloaded exact frozen Actions artifact, extracted its wrapper and verified **inner ZIP** byte count `189599767`, SHA-256 `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64`, and checksum file.
6. Q5 verified the embedded release manifest, `CAPABILITIES.json` version and exact build commit, FFmpeg/font provenance and notices.
7. Q5 performed a second isolated offline portable audio+video smoke from the **unchanged Q4 ZIP** without global Python, global FFmpeg, or provider API keys.
8. Q5 secret and metadata gate PASS.
9. Q5 published **that exact ZIP and checksum**, no rebuild or repack.
10. Q5 downloaded published ZIP and checksum again and verified published bytes, digest, stable flags and tag ref pointed at exact frozen Q4 commit.
11. Q5 uploaded immutable release evidence with run conclusion `success`.

**exact_zip_rebuilt = false**

**published_asset_redownload_verified = true**

**publication_performed = true**

## Saved Q5 audit evidence

- Q5 GitHub Actions job ID: `113167810887`
- Evidence artifact ID: `11530643844`
- Artifact name: `q5-release-evidence`
- Wrapper digest: `sha256:ed175ad02246189745a73506b5abac0d4da7eb96c5bd36df0c93240135fa80c5`
- Run URL: https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37733519371

## Rollback and governance

Published v2.0.1 is unchanged, tag `v2.0.1` targets `35a8c195469d49d7f7938b31761ceb17c4c720e0`, ZIP SHA-256 `6c97461ee3472973fc9b7950952287ae5aab9ffe2dffbe6a1fb0c236353d4a5d`. Older v2.0.0 is also immutable. Original `inoriko920-dev/Full-Album-Maker` repository was not modified.

App rollback is side-by-side; project-data rollback must be handled independently.

This is a historical release record. **Do not** change published stable tags, ZIPs or checksums, and do not confuse the later squash-merge SHA with the exact Q4 build/tag SHA.

**Q4 v2.0.2 PASS. Q5 v2.0.2 PASS. Stable v2.0.2 PUBLISHED.**
