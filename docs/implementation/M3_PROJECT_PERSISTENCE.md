# M3 — ProjectPersistence

Status: **IMPLEMENTED — validation pending**

## Scope

M3 introduces one persistence facade around the proven project/recovery behavior
without changing ProjectDocument schema v2, editor ownership, UI, render pipeline,
preview/cache ownership, or release packaging.

Implemented:
- ProjectPersistence facade;
- native ProjectDocument verified save;
- compatibility-envelope verified save through existing STEP11 writer;
- ProjectDocument load from native v2, STEP11 embedded v2, and deterministic v1 migration;
- recovery classification: CORRUPT / STALE / SAME / NEWER / FOREIGN;
- editor-v2 open/save routed through ProjectPersistence;
- STEP11 canonical save + recovery write/clear/classification routed through ProjectPersistence;
- ProjectPersistence wired into CompositionRoot/AppKernel;
- legacy v1 migration IDs made deterministic from canonical payload.

Not implemented:
- project schema bump;
- hidden media path search;
- ProcessSupervisor;
- RenderEngine M4;
- Preview/Cache M5;
- workspace migration;
- UI redesign.

## Frozen Decisions Preserved

- ProjectDocument + EditorController/EditorSession remain authoritative.
- Legacy Project remains compatibility-only.
- Schema version remains v2.
- TIMEBASE remains 240000.
- Save correctness is semantic equality, not JSON byte equality.
- Save publication is snapshot -> same-directory stage -> semantic read-back verification -> atomic publish.
- Recovery remains separate from canonical Save.
- Corrupt/foreign recovery evidence is never silently trusted or deleted.
- Future schema fails closed.
- Legacy v1 migration yields a current-schema ProjectDocument or typed failure.

## ProjectPersistence Boundary

`src/full_album_maker/project_persistence.py`

### load_document(path)

Supported inputs:
1. native ProjectDocument v2;
2. STEP11 compatibility envelope with `album_document_v2`;
3. legacy Project v1 when migration is enabled.

Rejected:
- timeline-only v1;
- future project schema;
- corrupt/unknown payload.

### save_document(path, document)

Native v2 publication:
1. clone authoritative ProjectDocument;
2. validate snapshot;
3. serialize to a same-directory stage;
4. read stage back through ProjectPersistence;
5. compare normalized semantic hashes;
6. only then `os.replace(stage, canonical)`.

A failed stage/verification cannot replace the previous canonical file.

### save_compatibility(path, legacy_project, document)

Wraps the existing proven STEP11 `save_verified_legacy_project` implementation.
The legacy compatibility envelope stays in use for production Foundation save
while the embedded ProjectDocument remains authoritative.

### Recovery classification

`assess_recovery()` classifies without deleting evidence:
- CORRUPT — unreadable/tampered recovery;
- FOREIGN — project token mismatch;
- SAME — same normalized ProjectDocument;
- STALE — valid but older revision;
- NEWER — valid non-identical recovery at current/newer revision.

Production STEP11 behavior:
- SAME may be explicitly cleared as redundant;
- CORRUPT/FOREIGN/STALE are ignored for current restore UX but retained;
- NEWER remains eligible for the existing recovery prompt/restore flow.

## Deterministic Legacy Migration

Before M3, `migrate_project_v1()` used default UUID4 values for new v2 IDs.
The same v1 payload could therefore produce different canonical IDs on repeated
migration.

M3 derives migration IDs with UUID5 from a SHA-256 of canonical legacy JSON plus
stable semantic keys:
- project;
- visual/audio tracks;
- assets by kind + normalized path;
- songs by deterministic order + asset ID;
- migration layers by semantic role.

No schema field is added. This implements D05-16 without changing v2 serialization.

## Production Routing

M3 routes these existing paths through the facade:
- `EditorWorkspace.open_project()`;
- `EditorWorkspace.save_project()`;
- STEP11 Foundation verified save;
- STEP11 recovery write;
- STEP11 recovery clear;
- STEP11 recovery assessment.

The existing HomeProjectService legacy-envelope open remains available for the
Foundation compatibility shell. STEP04 already restores the embedded
`album_document_v2` into EditorWorkspace after legacy Project adoption, so M3
does not invent a second open owner.

## Fault / Regression Gate

M3 PASS requires:
1. Q0 compile;
2. M0/M1/M2/M3 contract tests;
3. native v2 semantic save/load roundtrip;
4. compatibility-envelope semantic roundtrip;
5. save verification failure preserves the previous canonical file;
6. future schema/timeline-only payload fail closed;
7. repeated v1 migration yields identical v2 IDs/document for the same payload;
8. recovery classifications cover SAME/NEWER/STALE/FOREIGN/CORRUPT;
9. corrupt recovery evidence remains on disk;
10. baseline atomic persistence tests PASS;
11. STEP11 lifecycle/recovery tests PASS;
12. production authoritative-state + canonical-save integration PASS;
13. editor-v2 dirty checkpoint behavior PASS;
14. nine-workspace navigation remains read-only;
15. no M4 RenderEngine work in the branch.

## Rollback

Rollback target is M2:
`8bfe513fad117b625204f1a45fa4fbda2828e45c`.

No project schema migration is written to disk merely by running M3. A user only
publishes new bytes through explicit Save, and the format remains schema v2 /
current compatibility envelope.

## Next

After M3 PASS, the next allowed migration phase is **M4 — Render Facade**.
Do not proceed to M4 in the same turn.
