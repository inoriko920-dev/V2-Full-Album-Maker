# Full Album Maker v2.0.4 — Stable Patch Release

Status: **Stable — Q5 Release Quality Gate PASS**

**Q4 and Q5 PASS.** The exact Windows portable ZIP tested by Q4 has now been published, without rebuilding. Q5 also re-downloaded the published ZIP and SHA256SUMS.txt and verified the source tag, bytes and SHA-256.

Published artifact: `Full-Album-Maker-v2.0.4-Windows-Portable.zip`.

## Improvements since v2.0.3

- **PR #52 — Template thumbnail close lifecycle:** prevent new requests or cache-hit signals after the template gallery thumbnail cache closes. In-flight worker completion cannot emit stale thumbnail results after close. Includes regression tests that process queued Qt signals.
- **PR #51 — Exact stable ZIP identity checks:** require the published README checksum, byte size and source commit to match the specifically named Q5 evidence fields, not just an unrelated coincident hash.
- **PR #50 — Published download instructions:** README accurately describes available V2 source code, portable build and historical recovery provenance.
- No new UI design, project/schema migration, Python dependency, pinned FFmpeg or bundled font changes.

## Verified stable release

- Published: **October 8, 2026 at 15:09:44 WIB**.
- Tag: `v2.0.4`, targets exact Q4 source commit `af5af1ce24aba17ff68d469390a0c3d21f80f44d`.
- Windows portable: `Full-Album-Maker-v2.0.4-Windows-Portable.zip`.
- ZIP size: **189599237 bytes**.
- ZIP SHA-256: `888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b`.
- Q4 Windows run `37745568166`: **782 regression tests PASS**, separate pinned FFmpeg external-filter-script test **1 PASS**, portable build and isolated offline audio/video smoke PASS.
- Q4 Actions artifact ID `11536240883`: frozen exact ZIP, name `q4-v2.0.4-windows-artifact-candidate`.
- Q5 run `37747917087`: **PASS**, exact Q4 artifact retrieved without rebuild, its embedded version/dependencies and extracted offline smoke reverified, published ZIP/checksum re-downloaded and verified.
- GitHub Release ID `406580160`; Q5 evidence Actions artifact `11536193084`.
- Python 3.12.10, FFmpeg and font provenance, pinned Windows dependencies and notices unchanged.

Download: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.4

Direct ZIP: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.4/Full-Album-Maker-v2.0.4-Windows-Portable.zip

Checksum: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/download/v2.0.4/SHA256SUMS.txt

## Run the Windows portable app

Extract the downloaded ZIP into a separate folder on Windows 11 and start `Full Album Maker.exe`. Do not run the EXE directly from inside the ZIP. Python and FFmpeg are bundled; external Gemini/AI features still require the appropriate provider configuration.

## Previous stable / rollback

The previously published **v2.0.3** release remains unchanged:
- Tag/source commit `ee61ca0af5d15cdc51af91ad48e05bc2b641f49d`.
- Windows portable ZIP size `189599847` bytes.
- ZIP SHA-256 `b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0`.

v2.0.2, v2.0.1 and v2.0.0 remain immutable. Keep portable releases in separate application directories when rolling back; restoring project data is a separate operation.

## Audit references

- `docs/implementation/Q4_V2_0_4_EVIDENCE.md` — immutable exact Windows artifact and Q4 quality proof.
- `docs/implementation/Q5_V2_0_4_EVIDENCE.md` — no-rebuild publication, independent Q5 smoke, re-downloaded asset verification.

**Stable v2.0.4 is published. Never replace its ZIP, checksum or tag.**
