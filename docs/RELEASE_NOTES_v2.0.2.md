# Full Album Maker v2.0.2 — Patch Release Candidate

Status: **Release candidate — not published**

**Q4 and Q5 pending.** This changelog describes the proposed patch and does not authorize release publication.

Planned artifact: `Full-Album-Maker-v2.0.2-Windows-Portable.zip`.

## Changes since stable v2.0.1

- **PR #37:** Distinguish transient filesystem/permission read errors from actual JSON or encoding corruption in per-project media metadata. Do not quarantine healthy files because of temporary sharing violations. Keep Media workspace accessible during read/lock failures; retry metadata loading on subsequent refresh.
- **PR #39:** Skip NTFS directory junctions during recursive folder media import, preventing loops when a junction points back to an ancestor while preserving normal directory traversal.

Both fixes were merged to `main` after Windows PR CI PASS. Final merged-source Windows CI gate must also PASS before the v2.0.2 candidate can be frozen.

## Patch scope

- No new UI design, media schema migration, editor feature, or dependency upgrade.
- Canonical app version, `pyproject.toml`, and release manifest target are `2.0.2`.
- Windows x86_64 portable onedir; pinned Python 3.12.10, PySide6 and PyInstaller, bundled FFmpeg and Noto Sans remain unchanged.
- Require complete regression tests and extracted/offline Windows portable smoke.
- Exact candidate source commit + Actions artifact ID + portable ZIP bytes + SHA-256 to be frozen at Q4; **none is known yet**.
- At Q5 publish **only** the exact frozen Q4 ZIP without rebuilding; re-download published assets for independent verification.

## Rollback and preservation

Previous stable `v2.0.1`:
- tag `v2.0.1` -> commit `35a8c195469d49d7f7938b31761ceb17c4c720e0`;
- ZIP SHA-256 `6c97461ee3472973fc9b7950952287ae5aab9ffe2dffbe6a1fb0c236353d4a5d`;
- release https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.1.

Older v2.0.0 also remains immutable. Never change the original `inoriko920-dev/Full-Album-Maker` repository.

## Gate state

1. P01 version identity, notes and release-plan review — **IN PROGRESS**.
2. P01 exact Windows PR-head test/build/smoke — **PENDING**.
3. Post-merge main Windows CI — **PENDING**.
4. Q4 new v2.0.2-specific candidate/artifact validation and freeze — **NOT STARTED**.
5. Q5 independent v2.0.2 no-rebuild publication and verification — **NOT STARTED**.

**v2.0.2 is not yet downloadable.** Published latest stable remains v2.0.1.
