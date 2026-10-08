# Full Album Maker v2.0.1 — Patch Release Candidate

Status: **Release candidate — not published**

**Q4 and Q5 pending.** This document is a proposed patch changelog, not a stable release announcement or authorization to publish. The Windows candidate and its exact SHA-256 must be generated and frozen under the new v2.0.1 gate.

Planned artifact: `Full-Album-Maker-v2.0.1-Windows-Portable.zip`.

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

## Release candidate contracts

- Application version, pyproject metadata and canonical release manifest: `2.0.1`.
- Windows x86_64 portable onedir, Python `3.12.10`, pinned dependencies, existing pinned FFmpeg and Noto Sans.
- Real Windows regression suite, FFmpeg render/parity checks, executable build and extracted Unicode/apostrophe-path portable smoke.
- The exact candidate commit, portable ZIP byte count and SHA-256 must be recorded after the Q4 gate passes.
- Q5 must retrieve **that exact frozen ZIP** and verify it without rebuilding, re-run isolated smoke, verify rollback availability, and verify released assets after publication.
- No existing tag or asset may be moved, replaced or overwritten.

## Rollback

Last published stable: `v2.0.0`, tag target `d2ce2ccac62cdcd8994a38251a5b547c8460421e`.

Its published Windows portable ZIP SHA-256 is `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`.

Rollback is side-by-side. Project-data rollback remains a separate action; do not silently modify project data.

## Hold points

1. Patch candidate review and Windows PR validation must PASS.
2. Merge to `main` and validate `main`; choose a frozen exact candidate commit.
3. Execute the version-specific Q4 quality gate, save artifact ID / digest / byte count and record evidence.
4. Execute the separate Q5 no-rebuild publication gate with the frozen Q4 tuple.
5. Re-download published ZIP and checksum; verify hash, bytes, tag target, then mark stable.

**No release has been published by preparing this document.**
