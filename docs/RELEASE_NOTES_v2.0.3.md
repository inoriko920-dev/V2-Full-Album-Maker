# Full Album Maker v2.0.3 — Patch Release Candidate

Status: **Release candidate — not published**

**Q4 and Q5 pending.** This is an internal Windows patch candidate and must not be confused with a published stable release.

Planned artifact: `Full-Album-Maker-v2.0.3-Windows-Portable.zip` (not yet built by Q4).

## Fixes since stable v2.0.2

- **PR #45 / issue #44 — Preview cache recovery:** valid JSON with an invalid root type (array, null, number or string) in disposable preview metadata no longer causes an `AttributeError`. The thumbnail cache is regenerated; invalidation skips malformed records and continues to valid ones. User media files and project data are not modified.
- **Regression coverage:** five new cases added (four cache-regeneration root types and one mixed invalidation case).
- No new UI elements, editor features, media/project schema migration, new Python dependency, FFmpeg change or bundled font change.

The source fix is merged into `main` at `242e2350903d88d1ec220fc669edcd06646fc6b4` with PR-head Windows validation PASS. Post-merge Windows CI run `37735096131` **must be independently verified** before the release candidate proceeds.

## Frozen dependencies and build target

- Windows x86_64 portable onedir.
- Python 3.12.10 and all pinned dependencies as in `v2.0.2`.
- Pinned BtbN FFmpeg and Noto Sans unchanged.
- Application `__version__`, project TOML and canonical release manifest target: `2.0.3`.

## Publication requirements (not yet satisfied)

1. Version-preparation PR exact Windows test, build and extracted portable A/V smoke PASS.
2. Verify post-merge `main` PASS.
3. New **v2.0.3-specific Q4** run with pinned FFmpeg validation, full pytest, extracted offline Windows smoke, embedded provenance, secrets check and immutable ZIP/checksum freeze.
4. Record **actual** Q4 candidate commit, Actions artifact ID, exact ZIP byte count and SHA-256 (currently **not available**).
5. New independent **v2.0.3 Q5** using only that frozen Q4 ZIP; never rebuild, recompress, or replace the tested portable ZIP.
6. Re-download published ZIP and SHA256SUMS, check byte count, hash and tag ref against frozen Q4 commit before claiming Stable.

## Previous stable and rollback

Published `v2.0.2` remains immutable:
- tag commit `2678b9f93364334c7eaf9ebad9ef7e079533716f`;
- ZIP SHA-256 `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64`;
- https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.2.

Older v2.0.1/v2.0.0 and the original `inoriko920-dev/Full-Album-Maker` repo must not be changed.

**v2.0.3 is not yet downloadable. Published latest stable remains v2.0.2.**
