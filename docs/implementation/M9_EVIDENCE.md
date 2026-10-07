# M9 — Consolidation Evidence

Status: **PASS**

## Candidate

- Branch: `impl-m9-consolidation`
- M8 rollback/base:
  `9513edf833d4649225e2b66fcaf27d4f909948fb`
- Runtime consolidation:
  `8d8c9088bc8974b6c2de90a4791117f2dcc9fdd8`
- Validated candidate:
  `4a9a4b2f91b0dd81b749d02fd356c00d6b14b817`
- GitHub Actions run: `37600034073`

## Diff scope

M8 -> validated M9 changes:
- add `production_runtime.py`;
- simplify `main.py`;
- add M9 consolidation tests/workflow;
- update entrypoint/AppKernel characterization tests.

No ProjectDocument, timeline model, renderer/compiler, workspace UI, dependency,
build, version, or release publication file is changed.

## Bootstrap ownership evidence

Before M9, `main.py` individually imported and called the full installer
chain.

After M9:
- `main.py` calls only `install_production_runtime()`;
- `production_runtime.py` is the single ordered bootstrap manifest owner;
- the exact 27-installer order is test-frozen;
- names are unique;
- installer plan refuses empty/duplicate/uncallable definitions.

## Idempotence evidence

Focused unit tests prove:
- first install executes A -> B -> C once;
- second install performs no repeated calls;
- if B fails after A succeeds, retry executes B -> C but not A again.

This prevents duplicate replay of already-applied global runtime patches during
same-process diagnostic retries.

## Entrypoint evidence

Static tests prove:
- consolidated runtime installation happens before lazy
  `from full_album_maker.v14_window import run`;
- no direct `install_async_import()`, `install_step03_media()`,
  `install_step10_render()`, or STEP11 installer wiring remains in main;
- production still routes through AppKernel;
- portable smoke path remains present.

## Frozen-contract evidence

M9 tests explicitly verify:
- `SCHEMA_VERSION = 2`;
- `TIMEBASE = 240_000`;
- canonical nine route identifiers remain present.

Existing M0–M8 tests additionally protect ProjectDocument authority,
WorkspaceRegistry, service ownership, persistence, preview/render parity, and
legacy bridge retirement.

## Regression results

Main M9 job: **SUCCESS**
- M0–M9 contracts: 73 passed, 4 skipped
- bootstrap/retirement parity: 13 passed
- nine-route UI: 42 passed
- production navigation/persistence/render/preview: 25 passed, 2 skipped
- responsive/lifecycle/entrypoint: 29 passed
- long-album stress: 2 passed

Real FFmpeg M9 job: **SUCCESS**
- 3 passed

The real job keeps green:
- final render vs Accurate Preview;
- Spectrum Accurate Preview compiler parity;
- BeatAnalysis derived pulse detection/master-audio immutability.

## Architecture migration status

STEP 03 M0–M9 sequence is now fully implemented and gate-protected.

This is not Q5 release approval.

The next quality promotion gate is Q2 Integration from STEP 10.

## Final-head rule

This evidence records the validated runtime candidate. The following
documentation-only commit changes governance/evidence only. The same
`v2-m9-consolidation.yml` workflow must be green on the final branch head
before M9 handoff is complete.
