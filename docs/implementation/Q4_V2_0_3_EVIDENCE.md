# Q4 v2.0.3 — Frozen Windows Portable Artifact Evidence

Status: **PASS / FROZEN — NOT PUBLISHED**

## Exact frozen Q4 identity

| Field | Frozen value |
| --- | --- |
| Version | `2.0.3` |
| Exact Q4 candidate source and build commit | `ee61ca0af5d15cdc51af91ad48e05bc2b641f49d` |
| Q4 Actions run | `37736530557` |
| Q4 Windows job | `113177219212` |
| GitHub Actions artifact ID | `11531549824` |
| GitHub Actions artifact name | `q4-v2.0.3-windows-artifact-candidate` |
| **Inner portable ZIP** | `Full-Album-Maker-v2.0.3-Windows-Portable.zip` |
| **Inner portable ZIP bytes** | `189599847` |
| **Inner portable ZIP SHA-256** | `b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0` |
| Full Windows regression | `775 passed` |
| Pinned FFmpeg external-filter-script test | `1 passed` |
| Publication | `false` |

**Frozen tuple:** `2.0.3 | ee61ca0af5d15cdc51af91ad48e05bc2b641f49d | 11531549824 | Full-Album-Maker-v2.0.3-Windows-Portable.zip | 189599847 | b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0`

Source: https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37736530557

The Actions **wrapper** artifact (not the inner ZIP) has size `189252622` bytes and SHA-256 `908fbb2f54afcb663e1ede37b8c7068f07bfb25018d8b6a94b9705dd323a0f93`. Never substitute its digest/size for the inner ZIP.

## Verified Q4 quality gates

- Q4 run `37736530557` completed with `conclusion=success`.
- Complete Windows regression suite: **775 passed**, 0 failed. Separate pinned FFmpeg external filter-script test: **1 passed**.
- Windows x86_64 PyInstaller onedir portable ZIP and `SHA256SUMS.txt` were produced, checksum matched real inner ZIP bytes.
- Extracted isolated portable smoke in Unicode/apostrophe folder with no global Python, FFmpeg or provider API keys: PASS; audio/video streams confirmed.
- Exact Python 3.12.10, dependencies, version `2.0.3`, pinned FFmpeg SHA-256 `a885f564dee2b60f69ab866c6c89b96ae531fc2ee1f24ff8b5b1a6d29960a96b`, bundled font/notices, capabilities and embedded manifest checked.
- External pinned Windows FFmpeg filter-script check PASS; secret scan PASS.
- Artifact successfully uploaded as Actions artifact `11531549824` and was not expired when recorded.
- Generic Windows PR #47 CI run `37736567702` PASS on the same exact candidate source SHA.
- PR #47 merged into protected `main` as SHA `14545877cade0e0f7629411cc8a67f862b8211be`. **This is not the frozen build SHA.**
- Post-merge protected-main CI run `37737069774` must be checked for independent PASS before starting Q5.

## Previous published stable releases

Published v2.0.2 tag targets exact Q4 SHA `2678b9f93364334c7eaf9ebad9ef7e079533716f`, ZIP SHA-256 `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64`. v2.0.1 and v2.0.0 also remain preserved and unmodified. Original `inoriko920-dev/Full-Album-Maker` repository must never be modified.

## Q5 mandatory no-rebuild handoff — NOT STARTED

1. Create a new **version-specific v2.0.3** Q5 workflow. Do not reuse any historical stable publication controls.
2. Verify exact Q4 source SHA `ee61ca0af5d15cdc51af91ad48e05bc2b641f49d` is an ancestor of the Q5 control branch and only a new Q5 workflow / documentation differs.
3. Confirm Q4 run `37736530557` completed SUCCESS with that SHA.
4. Download GitHub Actions artifact ID `11531549824`, name `q4-v2.0.3-windows-artifact-candidate`; verify not expired and associated with that run.
5. Extract wrapper, verify inner ZIP `Full-Album-Maker-v2.0.3-Windows-Portable.zip`, `189599847` bytes and SHA-256 `b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0` and `SHA256SUMS.txt`.
6. Recheck exact embedded version, manifest, capabilities, FFmpeg/font, third-party notices and secrets.
7. Run isolated extracted portable A/V smoke from **this exact unchanged ZIP**, no rebuild, repack or recompression.
8. Confirm `v2.0.3` tag and release unused; `v2.0.2` published for rollback.
9. Only after all checks PASS, publish the exact ZIP and checksum; tag must target frozen source SHA, not merge/control SHA.
10. Re-download published release ZIP and checksum to verify bytes, SHA-256, stable flags and tag reference. Record separate Q5 evidence.

**Q4 PASS does not mean v2.0.3 stable is published.**
