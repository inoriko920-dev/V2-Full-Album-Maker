# V2 Full-Album-Maker — Project Status

## Current Phase
PLANNING

## Current STEP
STEP 05 — Media, Preview, Cache, Timeline, dan Project Data

## Gate Status
- STEP 00: PASS
- STEP 01: PASS
- STEP 02: PASS
- STEP 03: PASS
- STEP 04: PASS
- STEP 05: PASS

## STEP 05 Final Data/Media Direction
- ProjectDocument MediaAsset `asset_id` UUID is the sole canonical media identity.
- File location (`locator` / `relative_path`) and source fingerprint are separate from domain identity.
- Relink preserves asset UUID and all song/layer/project references.
- ffprobe remains the initial canonical adapter behind MediaProbeService.
- Import workers prepare proposals; project mutations commit through controlled EditorController/application transactions.
- Accurate Preview remains the parity oracle for project composition.
- Preview work is generation-aware, coalesced/cancellable, and off the UI thread.
- Cache is disposable, versioned, namespaced, fingerprint-aware, quota-bounded, and never project truth.
- Timeline remains time-based with TIMEBASE=240000 integer ticks per second.
- Packed / Free / gap / crossfade semantics remain frozen.
- Source VFR is media metadata/timestamp behavior, not a new project timeline clock.
- ProjectDocument schema_version=2 remains frozen during initial V2 consolidation.
- Extensions must be namespaced/versioned, JSON-only, validated, and technology-neutral.
- Project migration is deterministic and yields one current-schema ProjectDocument or a typed failure.
- Save/reopen correctness is normalized semantic equality, not byte-for-byte JSON formatting.
- Missing media does not make the project corrupt; references remain available for relink and dependent render operations block only when required.

## Coding Status
BLOCKED — planning phase.

No STEP 05 source-code, dependency, UI, schema, renderer, workflow, or project-format implementation change was made.

## Next STEP
STEP 06 — Render Engine, Processing Pipeline, dan Long-Album Reliability.

STEP 06 must design canonical render request/snapshot/compiler/process/preflight/verification/publication boundaries, long-album resource behavior, retry/resume policy, Windows command/filter-graph limits, and parity with Accurate Preview while preserving STEP 01–05 contracts.

## Canonical References
- Master planning DOCX.
- STEP 00 DOCX.
- STEP 01 DOCX.
- STEP 02 DOCX.
- STEP 03 DOCX.
- STEP 04 DOCX.
- STEP 05 DOCX.
- `docs/planning/STEP_01_AUDIT_SUMMARY.md`
- `docs/planning/STEP_02_DECISIONS.md`
- `docs/planning/STEP_03_ARCHITECTURE_DECISIONS.md`
- `docs/planning/STEP_04_HARDENING_DECISIONS.md`
- `docs/planning/STEP_05_MEDIA_TIMELINE_PROJECT_DATA_DECISIONS.md`
- `docs/planning/STEP_05_ARTIFACT_INTEGRITY.txt`
- `docs/governance/PROJECT_GOVERNANCE.md`
- `docs/governance/AI_HANDOFF.md`
