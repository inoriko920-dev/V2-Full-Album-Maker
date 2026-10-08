# Full Album Maker v2.0.5 — Stable Patch Release

Status: **Stable — Q5 Release Quality Gate PASS**

**Q4 and Q5 PASS.** The exact Windows portable ZIP frozen by Q4 is published without rebuilding, repacking or recompressing. Q5 re-downloaded the published assets to verify byte-for-byte identity.

## Improvements since stable v2.0.4

- **PR #57 — Beat Analysis cache corruption recovery:** malformed but parseable JSON cache entries no longer silently drop beat events, convert invalid envelope entries into usable values, or fail on huge numeric inputs. The disposable cache is regenerated safely from the existing source audio.
- Eight parametrized regression cases cover malformed beat entries, invalid strength/timestamp/duration/envelope, and ensure original audio is unchanged and repaired cache is reused.
- No UI redesign, authored project/schema migration, new package dependency, FFmpeg/font pin change or render-engine replacement.

## Verified stable release

- Published: **October 8, 2026 at 16:29:52 WIB**.
- Tag: `v2.0.5`, targets exact Q4 source commit `645fa166aa7a4cdc372b80c82db09026a7ab9b95`.
- Windows portable: `Full-Album-Maker-v2.0.5-Windows-Portable.zip`.
- ZIP size: **189598540 bytes**
- ZIP SHA-256: `8a3cdc694b003cb8d1aff3e9a3e7d68591b0fd3b4106a29cea94dd9f45b82f74`
- Q4 Windows workflow `37754857699`: **791 regression tests PASS**, separate real pinned Windows FFmpeg external-filter test **1 PASS**, extracted isolated audio/video portable smoke PASS, secret and provenance checks PASS.
- Exact Q4 Actions artifact `11540026862`, name `q4-v2.0.5-windows-artifact-candidate`.
- Q5 no-rebuild publication workflow `37756942493`: **SUCCESS**, exact Q4 ZIP verified, embedded manifest and capabilities checked, portable smoke repeated offline, final ZIP and checksum re-downloaded and verified after publication.
- GitHub Release ID: `406656131`; Q5 evidence Actions artifact ID: `11540114007`.
- Python 3.12.10, bundled FFmpeg, font and third-party license pins remain unchanged.

Release page: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.5

Direct Windows ZIP: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.5/Full-Album-Maker-v2.0.5-Windows-Portable.zip

SHA256SUMS.txt: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.5/SHA256SUMS.txt

## Run on Windows

Download the ZIP and SHA256SUMS.txt. Verify the ZIP SHA-256, extract to a separate writable folder on Windows 11, then start `Full Album Maker.exe` from that extracted folder. Do not run directly from inside the ZIP. Python and FFmpeg are bundled. Optional external AI features require appropriate provider configuration.

## Previous stable / rollback

Published **v2.0.4** release remains unchanged:
- Source/tag SHA `af5af1ce24aba17ff68d469390a0c3d21f80f44d`.
- Published `Full-Album-Maker-v2.0.4-Windows-Portable.zip` size: `189599237` bytes.
- SHA-256: `888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b`.

Earlier v2.0.3, v2.0.2, v2.0.1, v2.0.0 and original `inoriko920-dev/Full-Album-Maker` repository remain untouched.

## Audit evidence

- `docs/implementation/Q4_V2_0_5_EVIDENCE.md` — exact frozen Windows artifact, source, Q4 tests and ZIP SHA-256.
- `docs/implementation/Q5_V2_0_5_EVIDENCE.md` — no-rebuild publication, independent Windows ZIP smoke, GitHub published ZIP re-download.

**v2.0.5 stable is published. Do not replace its tag, ZIP or SHA256SUMS.**
