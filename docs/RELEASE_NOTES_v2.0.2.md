# Full Album Maker v2.0.2 — Stable Patch Release

Status: **Stable — Q5 Release Quality Gate PASS**

**Q4 and Q5 PASS.** The exact Q4-tested portable ZIP was published without rebuilding, and the released assets were independently re-downloaded and verified.

Published artifact: `Full-Album-Maker-v2.0.2-Windows-Portable.zip`.

## Improvements since v2.0.1

- **PR #37 — Metadata safety:** temporary sidecar permission, file I/O or lock failures no longer automatically quarantine valid metadata. Media workspace remains accessible and retries the read during subsequent refresh. Genuine invalid JSON/UTF-8 data still follows protected recovery.
- **PR #39 — Windows folder import stability:** skip NTFS directory junctions, preventing recursive folder scans from repeatedly following ancestor links. Normal media folder traversal remains deterministic.

This patch does not introduce new UI design, dependencies, schema migration, or features.

## Verified stable release identity

- Tag `v2.0.2` targets exact frozen Q4 candidate commit `2678b9f93364334c7eaf9ebad9ef7e079533716f`.
- Portable ZIP: `Full-Album-Maker-v2.0.2-Windows-Portable.zip`.
- ZIP size: **189599767 bytes**.
- ZIP SHA-256: `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64`.
- Q4 Windows build and smoke: run `37732261424` PASS (**769 regression tests + 1 pinned FFmpeg external-filter test**).
- Q4 artifact ID: `11530243260`; the ZIP was frozen.
- Q5 publication: run `37733519371` PASS, no rebuild; exact published ZIP and checksum re-downloaded and verified.
- Original pinned Python 3.12.10, third-party packages, FFmpeg and Noto Sans retained.

Published on **October 8, 2026 at 12:40:50 WIB**.

Download: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.2

## Installation

Download the Windows portable ZIP and extract it into its own folder, then run `Full Album Maker.exe`. Do not run the executable directly from inside the archive.

## Previous stable / rollback

`v2.0.1` is preserved with tag commit `35a8c195469d49d7f7938b31761ceb17c4c720e0`, ZIP SHA-256 `6c97461ee3472973fc9b7950952287ae5aab9ffe2dffbe6a1fb0c236353d4a5d`.

Older `v2.0.0` is also unchanged. Use side-by-side portable folders for application rollback; project-file data rollback is a separate responsibility.

## Quality audit

- Q4 frozen evidence: `docs/implementation/Q4_V2_0_2_EVIDENCE.md`.
- Q5 publication evidence: `docs/implementation/Q5_V2_0_2_EVIDENCE.md`.

**Stable release publication is complete. Published tags, ZIP bytes and checksums must not be changed.**
