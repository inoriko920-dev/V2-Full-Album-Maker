# M3 Implementation Evidence — ProjectPersistence

Status: **PASS**

## Branch / Baseline

- Repository: `inoriko920-dev/V2-Full-Album-Maker`
- Branch: `impl-m3-persistence`
- M2 parent: `8bfe513fad117b625204f1a45fa4fbda2828e45c`
- Validated M3 candidate: `4a7ac31a196365b5b639bd2e3ff3670cd28b5fad`

## Implemented

- `src/full_album_maker/project_persistence.py`
  - native v2 load/save;
  - STEP11 compatibility-envelope save;
  - semantic verification;
  - recovery write/clear/classification;
  - current v2, embedded v2, legacy v1 migration, future/timeline fail-closed.

- `src/full_album_maker/app_kernel.py`
  - CompositionRoot/AppKernel owns the ProjectPersistence dependency.

- `src/full_album_maker/editor_workspace.py`
  - editor-v2 open/save routes through ProjectPersistence.

- `src/full_album_maker/integration_feature_step11.py`
  - canonical compatibility Save and recovery paths route through ProjectPersistence.

- `src/full_album_maker/project_migrations.py`
  - v1 migration IDs changed from random UUID4 defaults to deterministic UUID5 values derived from canonical legacy payload + semantic key.

- `tests/test_v2_project_persistence.py`
  - native semantic roundtrip;
  - failed verification preserves old canonical bytes;
  - compatibility roundtrip/mismatch preservation;
  - future schema and timeline fail-closed;
  - deterministic v1 migration;
  - all five recovery classifications;
  - corrupt recovery retained;
  - AppKernel dependency ownership and production routing assertions.

## Verified GitHub Actions Evidence

Run: `37588571955`
Job: `m3-persistence`
Commit: `4a7ac31a196365b5b639bd2e3ff3670cd28b5fad`

Results:
- Q0 compile: PASS;
- M0/M1/M2/M3 contract suite: **37 passed in 0.58s**;
- baseline atomic/project persistence: **8 passed in 0.17s**;
- STEP11 persistence lifecycle + integration core: **14 passed in 0.17s**;
- production authoritative-state/canonical Save: **1 passed in 1.66s**;
- nine-workspace read-only navigation: **1 passed in 1.13s**;
- job conclusion: **success**.

## Safety / Isolation

Diff from M2 contains only M3 persistence/migration/wiring/tests/docs/workflow files.
No renderer, FFmpeg compiler, Preview/Cache, workspace ownership, project schema,
dependency, version, or UI redesign is included.

## Gate

**M3: PASS**

This evidence/status commit must pass the same M3 workflow on its own final head
before M4 starts.
