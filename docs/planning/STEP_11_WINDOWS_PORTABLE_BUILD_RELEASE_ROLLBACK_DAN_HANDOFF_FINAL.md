# STEP 11 — Windows Portable Build, Release, Rollback, dan Final Handoff

## Status
PASS — final planning STEP complete. No source/build/release mutation was performed.

## Core Decisions
- First mature V2 stable target: v2.0.0 after implementation and Q0–Q5 PASS.
- No stable release is authorized merely because main builds green.
- Stable publication is explicit from an approved candidate SHA.
- Exact tested ZIP must be the exact published ZIP.
- Artifact identity is semantic version + commit SHA + ZIP SHA-256.
- Windows x86_64 portable PyInstaller onedir remains primary distribution.
- Q4/Q5 validates the extracted final ZIP in an isolated Unicode/apostrophe path with global Python/FFmpeg/API keys unavailable.
- A canonical release manifest should prevent drift across build workflow, build script, capability report, notices, and evidence.
- Current THIRD_PARTY_NOTICES FFmpeg data is stale versus the build/capability pin and is a future release blocker.
- Existing automatic release-on-main behavior must be separated from validation before V2 stable.
- Existing release-QA hardcoded old STEP11 ancestry must be replaced by current V2 approved release provenance.
- Rollback preserves last-known-good tag, ZIP, checksum, release notes, capabilities/evidence.
- Application rollback never silently rewrites project data.
- Initial updates are side-by-side portable; auto-updater/installer are deferred.
- Old Full-Album-Maker repository remains read-only.

## Pre-Coding Gate
STEP00–11 planning completion does not unlock coding by itself.

Implementation begins only after canonical final MASTER + STEP00–11 DOCX files are physically present in V2 and their SHA-256 values match `PLANNING_ARTIFACTS_MANIFEST.md`.

First implementation after unlock:
1. M0/T1 FeatureParityRegistry + characterization map.
2. M1 additive AppKernel/CompositionRoot with legacy adapters.
3. Then Task/Process lifecycle migration and the remaining M phases.

## Release Blockers Observed in Baseline
1. THIRD_PARTY_NOTICES contains older FFmpeg asset/digest while build/capabilities use the newer pinned N-127142 asset.
2. Main push workflow can create a stable GitHub Release automatically.
3. Release QA contains an old hardcoded STEP11 handoff ancestry SHA.
4. Repeated release metadata is duplicated across files and can drift.
5. Python >=3.11 support claim needs a Python 3.11 test lane or an explicit support-floor change.
