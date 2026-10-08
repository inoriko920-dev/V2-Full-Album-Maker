# V2-Full-Album-Maker — v2.0.3 patch candidate release gate plan

Status: **P01 PASS; Q4 PASS / FROZEN; Q5 NOT STARTED — NOT PUBLISHED**

## Fixed source scope

Repository: `inoriko920-dev/V2-Full-Album-Maker`.
P01 branch: `release/prepare-v2.0.3-20261008`, from post-PR #45 `main` commit `242e2350903d88d1ec220fc669edcd06646fc6b4`.

The only executable change relative to v2.0.2 is the post-release **PR #45** preview-cache non-object JSON fix, supported by five regression cases. Source was merged into `main` after exact-head Windows validation PASS. Current `main` postmerge CI: `37735096131`, conclusion to be independently checked.

**Immutability:** no writes to original `Full-Album-Maker` repo or any previously published stable tag, ZIP, checksum or historical Q4/Q5 workflow.

## P01 — Identity and source of truth (current)

- Bump version from 2.0.2 to 2.0.3 in `src/full_album_maker/__init__.py`, `pyproject.toml` and `build/release_manifest.json`.
- No changes to pinned dependencies, Python, FFmpeg binary hash or font.
- Add `docs/RELEASE_NOTES_v2.0.3.md` marked **Release candidate — not published**.
- Update tests to assert the v2.0.3 candidate contract while preserving immutable Q5 publication evidence for v2.0.2, v2.0.1 and v2.0.0.
- Require full Windows regression, pinned FFT/FFmpeg validation, portable build and extracted offline audio/video smoke PASS on the *exact PR head*.
- Merge to protected `main` only after PASS; independently verify postmerge Windows CI success.

## Q4 — Windows artifact freeze (COMPLETE / PASS)

- Add a **separate v2.0.3 Q4 workflow**, based on the verified v2.0.2 Q4 workflow without altering historical controls.
- Verify `2.0.3` across app/package/manifest/release notes and bundled capabilities.
- Run all Windows regression tests, pinned FFmpeg external-filter check, provenance/license/secret checks, Windows x86_64 PyInstaller onedir build.
- Extract ZIP into a Unicode and apostrophe path, without global Python/FFmpeg or provider API keys; confirm real audio+video output.
- Record Q4 exact candidate SHA, run/job IDs, Actions artifact ID/name, **inner portable ZIP** exact byte count and SHA-256 in a dedicated immutable evidence document.
- Freeze the full tuple. A later squash-merge SHA is *not* the candidate SHA. Any code/build change after freeze requires a fresh Q4 run.

## Q5 — No-rebuild publication (NEXT — NOT STARTED)

- Add an isolated v2.0.3 release workflow from the frozen Q4 commit; **never edit or re-run** historical publication controls to create a new release.
- Verify v2.0.3 tag/release unused, v2.0.2 stable exists for rollback, and frozen Q4 run/commit/artifact provenance matches.
- Download the exact Q4 Actions artifact; verify wrapped and **inner ZIP**, SHA256SUMS, byte count and hash.
- Recheck embedded capabilities/manifest/FFmpeg/font/notices and offline extracted A/V smoke on the **unchanged ZIP**.
- Only after every verification PASS, create v2.0.3 tag pointing to exact Q4 commit and publish frozen ZIP plus checksum.
- Re-download assets, verify tag commit, byte count, SHA-256 and stable flags; document exact Q5 evidence and handoff.

## Gates

| Gate | PASS condition | Failure action |
| --- | --- | --- |
| Previous main CI | PR #45 postmerge SHA `242e235...` SUCCESS | Hold P01 merge and Q4 |
| P01 PR CI | Exact head full Windows regression and portable smoke SUCCESS | Fix and rerun |
| P01 main CI | Post-merge head Windows CI SUCCESS | Hold Q4 |
| Q4 candidate | Full real Windows smoke + immutable SHA/bytes/ID recorded | Hold Q5 |
| Q5 no-rebuild | Exact frozen Q4 ZIP downloaded and independently validated | Do not publish |
| Published assets | Re-download ZIP and checksum, verify tag/hash/size | Do not declare Stable |

## Handoff to another AI

Read Software Factory governance in `docs/governance/AI_HANDOFF.md`, `docs/governance/PROJECT_STATUS.md`, `docs/governance/POST_RELEASE_MAINTENANCE.md`, and previous version evidence `docs/implementation/Q4_V2_0_2_EVIDENCE.md`, `docs/implementation/Q5_V2_0_2_EVIDENCE.md`.
Check current PR head SHA and all CI outcomes; **do not trust earlier "PASS" claims without the exact successful run**.

**P01 result:** PR #46 merged; independent protected-main Windows CI `37736088109` PASS on `03e55e009d8c38bbc554162d3a77945f7b2b3b29`.

**Q4 result:** PR #47 merged. Exact Q4 candidate/source SHA `ee61ca0af5d15cdc51af91ad48e05bc2b641f49d`; Windows Q4 run `37736530557` PASS (775 regression tests and separate FFmpeg test), artifact ID `11531549824`. Frozen inner ZIP `Full-Album-Maker-v2.0.3-Windows-Portable.zip`, `189599847` bytes, SHA-256 `b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0`. Evidence: `docs/implementation/Q4_V2_0_3_EVIDENCE.md`. Protected-main Windows CI after PR #47: run `37737069774`, must independently PASS before Q5.

**Next step:** independent Q5 v2.0.3 no-rebuild gate, only after above CI prerequisites PASS. No publication until Q5 and release asset re-download pass.
