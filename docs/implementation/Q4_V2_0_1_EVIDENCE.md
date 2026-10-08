# Q4 v2.0.1 — Exact Windows Artifact Evidence

Status: **PASS — artifact validated and frozen; NOT PUBLISHED**

## Exact frozen Q4 tuple

| Field | Frozen value |
| --- | --- |
| Version | `2.0.1` |
| Source candidate SHA | `35a8c195469d49d7f7938b31761ceb17c4c720e0` |
| Q4 Actions run ID | `37724287381` |
| Q4 Actions job ID | `113138794504` |
| Actions artifact ID | `11527152731` |
| Actions artifact name | `q4-v2.0.1-windows-artifact-candidate` |
| Exact inner ZIP | `Full-Album-Maker-v2.0.1-Windows-Portable.zip` |
| Inner ZIP bytes | `189598786` |
| Inner ZIP SHA-256 | `6c97461ee3472973fc9b7950952287ae5aab9ffe2dffbe6a1fb0c236353d4a5d` |

**Frozen identity:**

`2.0.1 | 35a8c195469d49d7f7938b31761ceb17c4c720e0 | Full-Album-Maker-v2.0.1-Windows-Portable.zip | 189598786 | 6c97461ee3472973fc9b7950952287ae5aab9ffe2dffbe6a1fb0c236353d4a5d`

Source: https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37724287381

The GitHub Actions artifact is a wrapper ZIP. Its metadata are **not** the inner portable ZIP's hash or size:
- wrapper artifact bytes: `189252043`;
- wrapper artifact GitHub digest: `sha256:b4e1cd6d789f9efa371c7b211a9ec66f575a3ff833885ad630855c8ea90854a9`;
- GitHub artifact `expired=false` at verification on 2026-10-08; recheck availability before Q5.

## Windows validation — Q4 PASS

The exact candidate run completed with `conclusion=success`. All critical steps PASS:

- exact candidate checkout;
- canonical release manifest / `2.0.1` package-version / license and third-party provenance consistency;
- Windows full regression: **760 passed, 0 failed**;
- PyInstaller Windows x86_64 portable onedir build;
- portable ZIP creation and SHA-256 checksum generation;
- extracted Unicode/apostrophe path smoke without global Python, global FFmpeg, Google/Gemini API keys;
- bundled executable launched and produced audio + video, verified by ffprobe;
- separate pinned Windows FFmpeg external-filter-script regression: **1 passed**;
- secret scan;
- embedded `CAPABILITIES.json`, `RELEASE_MANIFEST.json`, notices and bundled FFmpeg/font verification;
- exact artifact and evidence upload.

Q4 result explicitly records `publication_performed=false` and `q5_required=true`.

Shipping pinned FFmpeg source digest remains:
`a885f564dee2b60f69ab866c6c89b96ae531fc2ee1f24ff8b5b1a6d29960a96b`.

## Workflow PR and source-control provenance

- Q4 workflow PR: https://github.com/inoriko920-dev/V2-Full-Album-Maker/pull/33
- PR #33 HEAD `35a8c195469d49d7f7938b31761ceb17c4c720e0` passed generic Windows CI run `37724339639`.
- Workflow merged into `main` at `40fb095964416fb2400c6c52b4cddaa4b895b092`.
- The squash merge SHA differs from the **frozen artifact build SHA**. Do not replace the frozen build SHA with the merge SHA.
- Post-merge `main` validation run: `37724739883` (must be checked independently before declaring main PASS).
- Historical `v2.0.0` tag, assets, digest and old Q4/Q5 control workflows were not modified.

## Q5 handoff — NOT STARTED

Q5 must:
1. Run independently on a version-specific `v2.0.1` publication control; never reuse `step12-release-validation.yml` hardcoded for v2.0.0.
2. Verify the frozen candidate is an ancestor of its control branch and no forbidden non-document edits occurred after freeze.
3. Verify tag `v2.0.1` and release are unused.
4. Verify rollback `v2.0.0` stable publication exists and remains intact.
5. Download **artifact ID `11527152731` from run `37724287381`**, extract the Actions wrapper, and verify the exact **inner ZIP** name, bytes and SHA-256 listed above. Require checksum file contents to match.
6. Inspect embedded capabilities, version, pinned FFmpeg/font and notices.
7. Re-run isolated smoke against this **unchanged ZIP** with global Python/FFmpeg and provider keys absent.
8. Scan secrets and verify release metadata.
9. Publish exact ZIP and checksum only after all gates PASS; **do not build, repack or recompress the inner portable ZIP**.
10. Re-download the published ZIP and checksum, independently verify byte count, SHA-256, tag target, release status, and record immutable Q5 evidence.

**Never** claim `v2.0.1` has been published merely because Q4 is PASS.

## Prior stable immutable identity

- v2.0.0 release target `d2ce2ccac62cdcd8994a38251a5b547c8460421e`.
- v2.0.0 portable ZIP SHA-256 `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`.

Rollback of the app remains side-by-side, separate from project-data rollback.
