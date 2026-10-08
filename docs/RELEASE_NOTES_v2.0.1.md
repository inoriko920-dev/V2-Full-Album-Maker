# Full Album Maker v2.0.1 — Stable Patch Release

Status: **Stable — Q5 Release Quality Gate PASS**

**Q4 and Q5 PASS.** The exact frozen Q4 Windows candidate was published by Q5 without rebuilding, and release assets were re-downloaded and verified.

Published artifact: `Full-Album-Maker-v2.0.1-Windows-Portable.zip`.

## Scope relative to stable v2.0.0

This patch candidate consolidates post-release Media Library metadata safety fixes merged on `main`:

- PR #23 — preserve sidecar metadata on First Save and Save As.
- PR #24 — prevent relink collisions of media/source IDs.
- PR #25 — quarantine corrupt metadata and preserve recovery evidence.
- PR #26 — prevent stale concurrent writes to the same metadata field.
- PR #27 — merge non-conflicting deferred edits while rejecting same-field lost updates.
- PR #28 — retry loading after transient file-lock / cleanup failures.
- PR #29 — retry failed First Save / Save As metadata writes without dropping unsaved changes; block target-ID collisions.
- PR #31 — reject foreign old-ID metadata collisions, including chained or source-less deferred relinks.

All changes are bug fixes and regressions. No user-facing UI redesign, project-document schema change, FFmpeg change, or new dependency is intended.

## Release identity and validation contracts

- Application version, pyproject metadata and canonical release manifest: `2.0.1`.
- Windows x86_64 portable onedir, Python `3.12.10`, pinned dependencies, existing pinned FFmpeg and Noto Sans.
- Real Windows regression suite, FFmpeg render/parity checks, executable build and extracted Unicode/apostrophe-path portable smoke.
- Q4 froze commit `35a8c195469d49d7f7938b31761ceb17c4c720e0`, portable ZIP size `189598786` bytes, and SHA-256 `6c97461ee3472973fc9b7950952287ae5aab9ffe2dffbe6a1fb0c236353d4a5d`.
- Q5 retrieved **that exact frozen ZIP** without rebuilding, re-ran isolated smoke, verified rollback availability, and verified the published assets by re-download.
- No existing tag or asset may be moved, replaced or overwritten.

## Rollback

Last published stable: `v2.0.0`, tag target `d2ce2ccac62cdcd8994a38251a5b547c8460421e`.

Its published Windows portable ZIP SHA-256 is `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`.

Rollback is side-by-side. Project-data rollback remains a separate action; do not silently modify project data.

## Completed quality gates

1. Candidate review and Windows PR validation: PASS (PR #32).
2. Q4 Windows artifact gate: PASS (run `37724287381`, artifact `11527152731`).
3. Frozen candidate checksum, embedded provenance and offline portable smoke: PASS.
4. Q5 no-rebuild publication: PASS (run `37725395630`).
5. Published ZIP, checksum and tag ref re-download and identity check: PASS.

**Published:** 2026-10-08 11:01:03 WIB — https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.1

**Q5 audit:** `docs/implementation/Q5_V2_0_1_EVIDENCE.md`. Previous stable v2.0.0 remains immutable.
