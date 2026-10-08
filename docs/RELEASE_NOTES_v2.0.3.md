# Full Album Maker v2.0.3 — Stable Patch Release

Status: **Stable — Q5 Release Quality Gate PASS**

**Q4 and Q5 PASS.** The exact Q4-tested portable ZIP was published without rebuilding. Q5 successfully downloaded the published release assets again and checked their hashes, bytes, and tag commit.

Published artifact: `Full-Album-Maker-v2.0.3-Windows-Portable.zip`.

## Improvement since v2.0.2

**Preview-cache recovery — PR #45 / issue #44.** Disposable preview metadata containing parseable JSON with the wrong root type (array, null, number or string) no longer disrupts thumbnail regeneration with an `AttributeError`. Invalid disposable cache data can be recreated. Source invalidation ignores malformed cache records and still processes valid entries, without changing original user images, audio, video or project files.

Five additional regression cases cover invalid JSON root types and mixed cached metadata. There are no new UI designs, editor features, project/schema migrations, Python dependencies, FFmpeg changes or font changes.

## Verified stable release

- Published: **October 8, 2026 at 13:29:47 WIB**.
- Tag: `v2.0.3`, targets exact Q4 source commit `ee61ca0af5d15cdc51af91ad48e05bc2b641f49d`.
- Windows portable: `Full-Album-Maker-v2.0.3-Windows-Portable.zip`.
- ZIP size: **189599847 bytes**.
- ZIP SHA-256: `b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0`.
- Q4 Windows run `37736530557`: **775 regression tests PASS**, external pinned FFmpeg filter-script test **1 PASS**, portable build and isolated offline audio/video smoke PASS.
- Q4 artifact ID `11531549824`: frozen exact ZIP.
- Q5 run `37737839379`: **PASS**, exact Q4 ZIP re-used without rebuilding; published ZIP/checksum re-downloaded and verified.
- Pinned Python 3.12.10, FFmpeg, fonts, dependencies and third-party notices remain unchanged.

Download: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.3

## Run the portable app

Extract the ZIP into its own Windows folder, then run `Full Album Maker.exe`. Do not launch the executable from inside the ZIP archive.

## Previous stable / rollback

v2.0.2 remains unchanged as prior stable:
- tag target `2678b9f93364334c7eaf9ebad9ef7e079533716f`
- ZIP SHA-256 `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64`.

v2.0.1 and v2.0.0 are also immutable. Keep portable versions in separate folders for application rollback; project-data rollback must be managed separately.

## Audit references

- `docs/implementation/Q4_V2_0_3_EVIDENCE.md`: frozen Windows artifact identity.
- `docs/implementation/Q5_V2_0_3_EVIDENCE.md`: no-rebuild publication and independent post-publication verification.

**Stable v2.0.3 is published. Do not replace its ZIP, checksum, or tag.**
