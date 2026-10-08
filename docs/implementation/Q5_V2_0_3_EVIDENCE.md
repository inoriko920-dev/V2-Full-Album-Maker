# Q5 v2.0.3 — Stable Release Publication Evidence

Status: **PASS — Stable v2.0.3 PUBLISHED**

## Immutable published release identity

| Field | Verified |
| --- | --- |
| Stable version and tag | `v2.0.3` |
| Release ID | `406491420` |
| Exact Q4 candidate source and tag commit | `ee61ca0af5d15cdc51af91ad48e05bc2b641f49d` |
| Q4 Actions run / artifact ID | `37736530557` / `11531549824` |
| Q5 Actions run / control SHA | `37737839379` / `28fcc614630bac1ca6ffbb88ee527869bf5a775e` |
| Q5 Windows job | `113181363714` |
| Published at UTC | `2026-10-08T06:29:47Z` |
| Published at WIB | `2026-10-08 13:29:47 WIB` |
| Published portable ZIP | `Full-Album-Maker-v2.0.3-Windows-Portable.zip` |
| Exact ZIP bytes | `189599847` |
| Exact portable ZIP SHA-256 | `b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0` |
| Published ZIP GitHub asset ID | `620959320` |
| Published SHA256SUMS.txt asset ID | `620959315` |
| Published status | `draft=false`; `prerelease=false` |

Stable release: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.3

Direct ZIP: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.3/Full-Album-Maker-v2.0.3-Windows-Portable.zip

Checksum file: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.3/SHA256SUMS.txt

## Quality gates — Q4 PASS, Q5 PASS

1. Q4 Windows run `37736530557` PASS on `ee61ca0af5d15cdc51af91ad48e05bc2b641f49d` (**775 regressions passed**, separate FFmpeg external filter-script **1 passed**, portable onedir build and extracted Unicode/apostrophe-path offline audio/video smoke PASS).
2. Frozen Q4 Actions artifact ID `11531549824`, name `q4-v2.0.3-windows-artifact-candidate`, verified not expired and sourced from successful Q4 run.
3. Q5 run `37737839379` PASS; provenance and no-rebuild ancestry/diff guard PASS.
4. Q5 verified tag/release `v2.0.3` had not existed before publication and stable `v2.0.2` existed for rollback.
5. Q5 downloaded that **exact Q4 artifact**, extracted its Actions wrapper, verified the **inner ZIP** exact filename, `189599847` bytes, SHA-256 `b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0` and `SHA256SUMS.txt`.
6. Verified embedded `CAPABILITIES.json`, release manifest, pinned Python/FFmpeg/fonts, third-party notices/licenses and secret scan.
7. Re-ran offline extracted portable audio/video smoke on the **same unchanged ZIP** without global Python, global FFmpeg or provider API keys.
8. Published exact tested Q4 ZIP and checksum, **no rebuilding or repacking**.
9. Re-downloaded the published ZIP and checksum, verified byte size, SHA-256 and stable flags; tag points to the **frozen Q4 candidate** (not Q5 control SHA or Q4 workflow squash-merge SHA).
10. Q5 uploaded evidence, and overall workflow result is `completed/success`.

**exact_zip_rebuilt = false**

**published_asset_redownload_verified = true**

**publication_performed = true**

## Q5 evidence artifact

- GitHub Actions artifact ID: `11532163113`
- Artifact name: `q5-release-evidence`
- Evidence wrapper digest: `sha256:c92177e268f553ef6c2f0ccf364e1d8ca43fd691d9509093e09a2fd5419f3fcd`
- Workflow: https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37737839379

## Immutable past releases and rollback

- v2.0.2 remains stable with tag commit `2678b9f93364334c7eaf9ebad9ef7e079533716f` and ZIP SHA-256 `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64`.
- v2.0.1 and v2.0.0 remain unchanged.
- Original `inoriko920-dev/Full-Album-Maker` repository remains unmodified.
- Application rollback uses separate portable directories; project-data rollback is a separate action.

Published tags, ZIPs, checksums and history are immutable. Any future changes to the executable require a new release/version with fresh Q4/Q5 validation.

**Q4 v2.0.3 PASS. Q5 v2.0.3 PASS. STABLE v2.0.3 PUBLISHED.**
