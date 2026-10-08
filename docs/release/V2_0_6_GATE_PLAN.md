# MASTER P01 / Q4 / Q5 — Full Album Maker v2.0.6

**ASTRA planning → SOL implementation | 8 October 2026 WIB**

**CURRENT GATE: PLANNING ONLY. P01 NOT STARTED. Q4 NOT STARTED. Q5 NOT STARTED. v2.0.6 NOT PUBLISHED.**

## 00. Otoritas, repository, dan batas perubahan

- Repository target **hanya** `inoriko920-dev/V2-Full-Album-Maker`; repository asli `inoriko920-dev/Full-Album-Maker` read-only.
- Protected-main baseline: `d804e7dfc98c625a83b55066bbf4b48627c6fc73`.
- Bugfix source-only PR **#63**: https://github.com/inoriko920-dev/V2-Full-Album-Maker/pull/63. Merge commit sama dengan baseline di atas.
- PR #63 exact final-head CI **37759297097**: **792 tests passed**, portable build/smoke audio+video **PASS**. CI protected-main **37759784954**: **792 tests passed**, Windows portable build/smoke **PASS**. No open PR/issue at planning kickoff.
- Latest **official published stable** is **v2.0.5**, release ID `406656131`, at https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.5. The published version must remain v2.0.5 until future Q5 **fully succeeds**.
- Frozen v2.0.5 source/tag `645fa166aa7a4cdc372b80c82db09026a7ab9b95`; **original inner portable ZIP** `Full-Album-Maker-v2.0.5-Windows-Portable.zip`; **189598540 bytes**; SHA-256 `8a3cdc694b003cb8d1aff3e9a3e7d68591b0fd3b4106a29cea94dd9f45b82f74`. All historical v2.0.4–v2.0.0 assets/tags/checksums remain unchanged.
- No new UI design, no window rearrangement, no project-schema change, no new feature wave, no provider/API key changes, no FFmpeg/font or Python pin changes.

## 01. Exact defect addressed by this patch

`MediaPreviewCache.request()` in `src/full_album_maker/media_preview_cache.py` previously increased `_jobs` and emitted `jobs_changed(1)` **before** calling `_queue.put(...)`. If a connected UI listener synchronously closed the cache on that signal, `close()` could drain an empty queue, mark the cache closed and terminate workers; then `request()` could enqueue a job **after** close. A stranded pending job would leave `job_count` nonzero with no workers to process it.

PR #63 moves the queue insertion into the protected critical section with `_pending` and `_jobs` updates, **before** broadcasting `jobs_changed`. New deterministic regression `test_preview_jobs_changed_reentrant_close_cannot_strand_a_queued_job` closes on `jobs_changed(1)` and verifies `job_count == 0`, stopped workers, rejection of new work, and unchanged original source media. It passed with the complete 792-test suite.

The **v2.0.5 published ZIP does not contain PR #63**, because its immutable frozen source precedes PR #63. v2.0.6 is needed to deliver the source fix.

## 02. Acceptance and exclusions

| Allowed and required | Prohibited |
| --- | --- |
| P01 bumps three canonical version values from `2.0.5` to `2.0.6` | Replacing/modifying v2.0.5 or older GitHub tag/ZIP/checksum |
| `src/full_album_maker/__init__.py`, `pyproject.toml`, `build/release_manifest.json` only for version identity | Editing runtime preview code beyond already-merged PR #63 |
| New `docs/RELEASE_NOTES_v2.0.6.md` marked **Release candidate — not published** | Presenting a development Actions artifact as stable ZIP |
| Version-aware tests confirm public README and Q5 evidence remain at v2.0.5 pending Q5 | Switching public download to v2.0.6 before publication |
| Version-specific isolated Q4 and Q5 workflows | Editing old Q4/Q5 workflows or releasing via regular CI |
| Actual artifact and quality-gate evidence with run IDs, source SHA, bytes and SHA-256 | Invented checksums, invented success, bypassing CI |
| Keep existing Windows 11 portable functionality and pinned toolchain | Dependency pins, Python, FFmpeg, font/license/provenance, UI, schema changes |

## 03. P01 — exact executable version metadata candidate

1. Reconfirm protected-main SHA, PR #63 merge status, **both exact CI PASS**, and **absence of v2.0.6 tag/release**. Verify official v2.0.5 ZIP bytes/hash unchanged. A mismatch means **STOP**.
2. Merge this planning Markdown and companion DOCX into the repository **before** coding metadata; planning PR latest-head Windows regression+smoke **PASS** and post-merge protected-main Windows regression+smoke **PASS** are mandatory.
3. From current verified main, create **new** `release/prepare-v2.0.6-20261008` branch.
4. Change exact markers: `__version__ = "2.0.6"`, `pyproject.toml [project].version = "2.0.6"`, `build/release_manifest.json target_stable_version = "2.0.6"`. No other manifest/dependency fields may change.
5. Add `docs/RELEASE_NOTES_v2.0.6.md`: candidate-only, clear PR #63 fix and regression proof, **Q4/Q5 pending**; do **not** claim ZIP size, digest, run IDs or release publication.
6. Update `tests/test_stable_release_v1.py` for candidate version/notes, preserve **every historical published Q5 identity**. Update `tests/test_readme_stable_identity.py`: `CURRENT_VERSION == "2.0.6"`, `PUBLISHED_STABLE == "2.0.5"`; ensure public README stays v2.0.5 and never links to non-existent v2.0.6. Keep old rescue checksums and explicit v2.0.5 Q5 identity checks.
7. Review exact PR diff (strict allowlist), ensure no user-authored data, dependency, UI or build controls have changed.
8. Require exact final-head Windows CI **all regression tests PASS**, Windows PyInstaller portable build PASS, extracted audio/video smoke PASS and uploaded validation artifact. If any fails: **STOP**, fix branch and rerun final SHA.
9. Only then squash-merge protected-main; independently verify post-merge main CI **SUCCESS** at resulting merge SHA.
10. P01 PASS means **source candidate only**. It does not create tag, release or official ZIP.

## 04. Q4 — Windows artifact freeze

1. Q4 blocked until P01 PR and independent protected-main Windows CI **PASS**. Check v2.0.6 tag/release absent and previous v2.0.5 still immutable.
2. Branch `release/q4-v2.0.6` from verified P01 protected main. Add a **new** `.github/workflows/v2-q4-v2.0.6-windows-artifact.yml` copied/adapted from the proven v2.0.5 workflow with version-specific gates. Do not alter any older release workflow.
3. Verify Python `3.12.10`, pip `26.2.1`, PySide6/Windows dependency lock, pinned FFmpeg asset URL/SHA-256 `a885f564dee2b60f69ab866c6c89b96ae531fc2ee1f24ff8b5b1a6d29960a96b`, Noto Sans source commit, licenses and `THIRD_PARTY_NOTICES.md`.
4. Validate 2.0.6 package/pyproject/manifest/candidate notes and forbid premature public release or tag.
5. Full Windows regression (baseline **792 tests**, plus any new gate-specific tests), real pinned FFmpeg external-filter script test, secret scan, portable onedir PyInstaller packaging, extracted **Unicode and apostrophe-path offline audio/video smoke** with no global Python/FFmpeg or provider keys.
6. Build the future **inner ZIP** `Full-Album-Maker-v2.0.6-Windows-Portable.zip` once; checksum `SHA256SUMS.txt`. Record actual inner ZIP **bytes and SHA-256**, exact frozen **Q4 source SHA**, Q4 run/job ID, Actions **artifact ID** and name. **Never confuse wrapper artifact size/digest with inner ZIP.**
7. Verify embedded CAPABILITIES/RELEASE_MANIFEST, source SHA, bundled FFmpeg/fonts/licenses and absence of secrets. Upload Q4 candidate wrapper/evidence. **Do not publish** stable release, tag, or GitHub release.
8. Exact-head Q4 PR CI **PASS**, merge, protected-main post-merge CI **PASS**. Document all actual evidence in `docs/implementation/Q4_V2_0_6_EVIDENCE.md` in a separate documentation PR; that PR and its postmerge Windows CI also must PASS.
9. Never fabricate frozen candidate metadata; if Q4 artifact expires/is missing, or any executable source/build changes, repeat **fresh Q4** and record new identity.

## 05. Q5 — no-rebuild independent stable release publication

1. Q5 blocked until frozen Q4, protected-main CI after Q4 merge and after evidence merge **ALL PASS**, no v2.0.6 release/tag exists, and prior stable v2.0.5 remains intact.
2. Create `release/q5-v2.0.6` **directly from frozen Q4 source SHA** (not main squash SHA), adding **only** `.github/workflows/v2-q5-v2.0.6-release.yml`.
3. Permission scope and source-diff fence: prohibit new runtime files, package build, `PyInstaller`, `build_portable.ps1`, rezip/repack/recompression of the frozen inner ZIP.
4. Download the precise successful Q4 Actions **artifact ID and run ID**. Verify wrapper association/expiry/source commit, extract its **inner ZIP** and `SHA256SUMS.txt`, compare **inner ZIP** bytes/hash to Q4 evidence. Verify embedded version, source provenance, CAPABILITIES, manifest, bundled pins/notices and secret scan.
5. Re-extract **unchanged** ZIP and perform independent offline audio/video smoke (no global Python/FFmpeg/provider API keys).
6. Publish **the same frozen inner ZIP and checksum**, no rebuild or repack. GitHub tag `v2.0.6` must point **directly** to frozen Q4 source SHA, not Q5 control or any merge SHA. No touching any prior stable release.
7. Re-download published ZIP and SHA256SUMS independently, compare file names, exact byte sizes and SHA-256, tag source SHA, flags `draft=false`, `prerelease=false`, and release asset identity. If verification fails, do not claim PASS.
8. Archive Q5 run/job/release ID, output ZIP hash/size, publication time WIB and `published_asset_redownload_verified=true` in `docs/implementation/Q5_V2_0_6_EVIDENCE.md`.
9. Only after actual Q5 SUCCESS, update README stable download, release notes, tests, project status/handoff/maintenance and archive Q5 workflow, via documentation PR with full exact-head and postmerge-main Windows CI PASS.

## 06. Risk register and STOP conditions

| Risk | Detector | Mitigation |
| --- | --- | --- |
| Preview queue regression / reentrant close | Existing new deterministic PR #63 test; Windows suite | Fail CI and block merge |
| Version drift across metadata | Exact equality tests and release manifest | Correct candidate only and rerun |
| Wrong public download prematurely | Published-stable identity tests | Keep README v2.0.5 until Q5 |
| Unpinned Python/FFmpeg/fonts | Canonical manifest, lockfile, Q4 hard gate | STOP, preserve original pins |
| Q4 artifact wrapper hash confused with inner ZIP | Explicit inner ZIP size/hash in Q4 evidence | Q5 compares inner ZIP only |
| Wrong frozen source/tag SHA | Q4 commit and Q5 source-diff gate | Tag exact Q4 source only |
| Non-identical public ZIP | Q5 published-asset redownload and SHA256SUMS | Do not report release PASS |
| Old release overwritten | Existing v2.0.5 release/tag/asset preflight | STOP and audit, never replace |
| Secrets or broken offline package | Q4/Q5 secret scan & isolated A/V smoke | Fail closed |
| Windows CI pending/failure | Exact final PR/main run IDs | No merge or next gate |

## 07. Evidence, ownership, and handoff

ASTRA = planning, gate decisions and evidence. SOL = implementation only after planning gate PASS. Each meaningful planning STEP receives DOCX. The UI is frozen: **no new UI prompt or redesign** is necessary for this narrow patch. Do not initiate code changes before the planning DOCX and Markdown land in the repository.

Final acceptance of a **downloadable stable v2.0.6** requires: planning PR and main CI PASS; P01 PR and main CI PASS; Q4 exact source and Windows artifact PASS; Q4 evidence PR and main CI PASS; independent Q5 no-rebuild publication/re-download PASS; final README/identity/handoff PR and main CI PASS. No future results may be claimed in advance.

**Next after this planning document is merged and verified: P01 metadata candidate only.** Previous official stable remains v2.0.5.
