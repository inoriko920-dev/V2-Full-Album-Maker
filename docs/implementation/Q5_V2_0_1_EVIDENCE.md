# Q5 v2.0.1 — Release Quality Gate and Publication Evidence

Status: **PASS — Stable v2.0.1 PUBLISHED**

## Published release identity

| Field | Verified |
| --- | --- |
| Stable version | `2.0.1` |
| Stable tag | `v2.0.1` |
| Exact frozen Q4 candidate and tag target | `35a8c195469d49d7f7938b31761ceb17c4c720e0` |
| Q4 Actions run | `37724287381` |
| Q4 frozen artifact ID | `11527152731` |
| Q5 control workflow run | `37725395630` |
| Q5 control commit | `aea9fbfc8f1c4b184145e118836a61aac3b3beb0` |
| GitHub Release ID | `406399261` |
| Published timestamp (UTC) | `2026-10-08T04:01:03Z` |
| Published timestamp (WIB) | `2026-10-08 11:01:03 WIB` |
| Exact published portable ZIP | `Full-Album-Maker-v2.0.1-Windows-Portable.zip` |
| Exact ZIP size | `189598786` bytes |
| Exact ZIP SHA-256 | `6c97461ee3472973fc9b7950952287ae5aab9ffe2dffbe6a1fb0c236353d4a5d` |
| ZIP release asset ID | `620661866` |
| Checksum release asset ID | `620661867` |

Release URL: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.1

Portable ZIP: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.1/Full-Album-Maker-v2.0.1-Windows-Portable.zip

Checksum: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.1/SHA256SUMS.txt

## Q5 proven checks

GitHub Actions run `37725395630` and every required step concluded SUCCESS:

1. Q5 provenance and **no-rebuild** ancestry/diff guard PASS: only the dedicated Q5 control workflow differed from frozen Q4 candidate.
2. Verified release/tag `v2.0.1` did not pre-exist before publication.
3. Verified rollback `v2.0.0` is already published stable.
4. Rechecked frozen Q4 workflow success, candidate SHA, artifact ID, name and non-expiration.
5. Downloaded Q4 Actions artifact `11527152731` and verified the inner ZIP's exact name, byte size, SHA-256 and checksum line.
6. Independently verified embedded `CAPABILITIES.json` v2.0.1, release manifest, FFmpeg/font pins, third-party notices and provenance.
7. Extracted and smoke-tested **that exact ZIP** without global Python, global FFmpeg or Google/Gemini API keys; A/V streams verified.
8. Secret and release metadata recheck PASS.
9. Published exact Q4-tested ZIP plus `SHA256SUMS.txt` as **stable** (draft=false, prerelease=false), without rebuilding.
10. Downloaded published release assets again and verified ZIP byte count and SHA-256, checksum content, and tag ref pointing directly to exact Q4 commit.
11. Uploaded Q5 evidence.

**exact_zip_rebuilt = false**

**published_asset_redownload_verified = true**

**publication_performed = true**

The published ZIP's GitHub asset digest matches the frozen Q4 inner ZIP SHA-256 exactly.

## Evidence artifact

- Q5 Actions artifact ID: `11527089380`
- Artifact name: `q5-release-evidence`
- Artifact digest: `sha256:e33f62545f104bc7b5c41cec1d8e3039cb4b9131107b62e03fc411fead9c2f50`
- Actions run: https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37725395630

## Old stable preservation / rollback

Published `v2.0.0` remained unchanged:
- tag target: `d2ce2ccac62cdcd8994a38251a5b547c8460421e`
- ZIP SHA-256: `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`.

The original `inoriko920-dev/Full-Album-Maker` repository is read-only and unchanged.

Application rollback uses side-by-side portable directories. Project-data rollback is a separate action.

## Post-publication governance

This document is recorded in a separate maintenance documentation branch after release. Updating evidence, notes and handoff must not change the published tag, ZIP, checksum or candidate commit.

For future maintenance begin from protected `main`, use dedicated branches, require Windows CI; any changed binary requires a new semantic version and its own Q4/Q5 evidence.

**Q4 v2.0.1 PASS. Q5 v2.0.1 PASS. Stable v2.0.1 PUBLISHED.**
