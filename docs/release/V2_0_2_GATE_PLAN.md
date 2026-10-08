# v2.0.2 patch release — governed release plan and handoff

Status: **P01 PASS; Q4 PASS; Q5 PASS — STABLE v2.0.2 PUBLISHED**

## Source of truth

Repository `inoriko920-dev/V2-Full-Album-Maker`; base `main` commit `89758d236f25bc90fbd5a2b8929fb69c9d15c878` after PR #37 and #39 were merged.

Immutability: do not modify historical v2.0.0/v2.0.1 tags, release assets, checksums, or their version-scoped Q4/Q5 publication workflows. Original `inoriko920-dev/Full-Album-Maker` untouched.

### P01 — Candidate identity and regression gate
- In dedicated `release/prepare-v2.0.2-20261008` branch, change only canonical app/version manifest and candidate tests, add these notes and planning document.
- Require all pinned Windows dependencies and release manifest fields other than target version to match latest stable v2.0.1.
- Keep historical v2.0.1 Q5 evidence verified by tests; new v2.0.2 candidate must say NOT PUBLISHED.
- Require final SHA Windows PR CI PASS, with regression pytest + PyInstaller portable ZIP extracted smoke. Merge only then and validate new `main` independently.

### Q4 — Frozen exact Windows candidate (blocked until P01 PASS)
- Create separate v2.0.2-specific Q4 workflow by adapting proven v2.0.1 Q4 **without editing it**.
- Verify version, provenance, secret scan, Python 3.12.10, pinned dependencies, FFmpeg SHA, Noto font commit and licenses, external filter-script test.
- Run full regression and actual Windows portable onedir build; extract ZIP into path containing Unicode and apostrophe; check offline render audio/video with no global Python/FFmpeg or provider API keys.
- Save exact source SHA, Q4 run/job IDs, GitHub Actions artifact ID/name, inner portable ZIP bytes and SHA-256; record Q4 evidence in repo handoff.
- After freeze only documentation-only adjustments permitted, and new code/build/dependency changes must start a fresh Q4 run.

### Q5 — Publish exact frozen Q4 ZIP (blocked until Q4 PASS)
- Create separate v2.0.2 Q5 no-rebuild workflow (old v2.0.1 Q5 must not be re-run or changed).
- Ensure `v2.0.2` tag and release do not exist, verify previous stable v2.0.1 published for rollback.
- Confirm Q4 run SUCCESS and target SHA exact; download its Actions artifact, inspect wrapper/inner ZIP identities, bytes, digest and SHA256SUMS.
- Inspect embedded manifests, FFmpeg/font license pins, scan for secrets, smoke-test the exact downloaded ZIP offline with no global tools or provider keys.
- Verify code ancestry and Q5 control-only differences from frozen Q4 source; reject rebuilds or repacks.
- Publish exact ZIP and checksum; re-download release assets, independently verify tag target, size/hash, stable release flags; store immutable Q5 evidence and update release notes/handoff.

## Gate matrix

| Gate | Required PASS | On failure |
|---|---|---|
| Package identity | 2.0.2 across app, project TOML, release manifest, candidate notes | Hold PR |
| Frozen dependencies | Identical pins to v2.0.1 (except version) | Review/hold |
| Windows PR CI | Full pytest and portable build/smoke on exact commit | Fix and rerun |
| Windows main CI | PASS on post-merge SHA | Hold Q4 |
| Q4 artifact | Exact SHA, ZIP bytes, SHA-256, artifact ID and smoke PASS | Hold Q5 |
| Q5 no-rebuild | Downloaded frozen Q4 ZIP checks match and smoke PASS | No publication |
| Stable publication | Published assets re-downloaded with identical bytes/digests | No stable claim |

## Handoff requirements

Read `docs/governance/AI_HANDOFF.md`, `docs/governance/PROJECT_STATUS.md`, `docs/implementation/Q4_V2_0_1_EVIDENCE.md`, `docs/implementation/Q5_V2_0_1_EVIDENCE.md`, and `docs/release/V2_0_1_GATE_PLAN.md` before Q4 or Q5.

**P01 evidence:** PR #40 merged; Windows CI on `main` run `37731780154` PASS on SHA `dc2f585c45036e24b8d844a522cdc03e3f8c1eb5`.

**Q4 evidence:** PR #41 merged; Windows Q4 run `37732261424` PASS on frozen candidate source SHA `2678b9f93364334c7eaf9ebad9ef7e079533716f`. Artifact ID `11530243260`, exact portable ZIP `Full-Album-Maker-v2.0.2-Windows-Portable.zip`, `189599767` bytes, SHA-256 `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64`. Complete evidence `docs/implementation/Q4_V2_0_2_EVIDENCE.md`.

**Main after PR #41:** Windows run `37732736075` PASS on merge commit `6cb54bc2e640113791d8e39da9d727a30f343926`.

**Q5 result:** PASS on Actions run `37733519371` with control commit `46b4970bc342a267bab36231aafcd323c0a073bc`. Exact frozen Q4 ZIP `Full-Album-Maker-v2.0.2-Windows-Portable.zip`, `189599767` bytes, SHA-256 `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64`, was published **without rebuilding**. Published assets were re-downloaded and verified. Stable tag `v2.0.2` targets exact Q4 SHA `2678b9f93364334c7eaf9ebad9ef7e079533716f`. Release ID `406458763`, published October 8, 2026 12:40:50 WIB.

**Source of truth:** `docs/implementation/Q5_V2_0_2_EVIDENCE.md`.

**Next work:** protected stable v2.0.2 post-release maintenance; do not move tags, replace published ZIPs/checksums, or change historical Q4/Q5 controls. Future changed binaries need a new version and new Q4/Q5 gates.
