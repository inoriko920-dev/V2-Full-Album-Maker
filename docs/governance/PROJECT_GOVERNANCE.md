# V2 Full-Album-Maker — Project Governance

## Repository Boundary
- Original repository: `inoriko920-dev/Full-Album-Maker`
- V2 repository: `inoriko920-dev/V2-Full-Album-Maker`
- Original repository is READ-ONLY for this V2 project.
- All planning, experiments, fixes, refactors, tests, builds, and releases must target the V2 repository only.

## Frozen Baseline
- Source baseline commit (old repo): `584c94774e6197ecf60ecedb3bffd5a8797e7737`
- Verified copied baseline commit (V2): `e3bc35b024654271cd594703f1402f9b003b1b08`
- Recovery branch: `baseline-copy-from-v1-2026-10-07`
- Verification: 372 blobs vs 372 blobs; 0 missing; 0 extra; 0 SHA/mode mismatches.

## Mandatory Rules
1. No write operations to the original repository.
2. No big-bang rewrite.
3. Preserve UI concept, primary workflow, and core feature behavior unless a later approved planning decision explicitly changes them.
4. External repositories/components are references or candidates only until license, packaging, maintenance, regression, and benchmark gates pass.
5. Every implementation change must remain rollback-capable.
6. Project-format compatibility must be preserved unless a documented migration plan is approved.
7. Planning and implementation must remain separated. No source-code implementation before planning gates are complete.
8. Architecture-changing decisions require a written decision record before implementation.

## Branch Policy
- `baseline-copy-from-v1-2026-10-07`: immutable recovery snapshot.
- `main`: protected integration/release line.
- `planning-v2`: planning documentation and handoff source-of-truth before implementation.
- Future implementation should use focused branches and merge only after required tests pass.

## Rollback Policy
If a new engine, adapter, cache, renderer, animation path, or persistence change fails parity or reliability gates, revert to the last passing adapter/path without changing the user's project format.

## Coding Gate
Coding remains BLOCKED until the required planning documents are complete and the project status explicitly changes from PLANNING to IMPLEMENTATION-READY.
