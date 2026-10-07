# M5 — Probe / Preview / Cache Evidence

Status: **PASS**

## Candidate

- Branch: `impl-m5-probe-preview-cache`
- M4 rollback/base: `d23f91f331942f2abbbfb9b4133439ebcc163fab`
- Validated runtime candidate: `6aa2a14a3bb52d0b598cba19526c3b99191adedd`
- GitHub Actions run: `37594113013`

## Scope Evidence

Runtime additions:
- `src/full_album_maker/media_probe_service.py`
- `src/full_album_maker/cache_manager.py`
- `src/full_album_maker/preview_engine.py`

Production wiring/routing changes are limited to:
- AppKernel/CompositionRoot M5 ownership;
- legacy async media import/relink probe routing;
- editor Accurate Preview routing;
- media/decoded preview queue construction;
- Spectrum Accurate Preview/default cache root;
- template-thumbnail default cache root;
- media-preview cache namespace/version/corruption validation.

No M6 Beat Analysis, M7 WorkspaceRegistry, UI redesign, ProjectDocument schema,
timeline semantics, compiler chain, dependency, build, or release behavior was
implemented.

## Q0 / Q1 Results

Main job `m5-probe-preview-cache`: **SUCCESS**
- M0–M5 contracts: 50 passed, 2 skipped
- focused probe/preview/cache parity: 9 passed
- persistence + production shell: 12 passed
- 200-song/~3-hour packed/free structural stress: 2 passed

Targeted job `real-ffmpeg-m5`: **SUCCESS**
- 3 passed
- real MediaProbeService audio duration uses the current FFmpeg/ffprobe adapter;
- current real Accurate Preview remains frame-parity checked against final
  rendering;
- current real Spectrum Accurate Preview remains on the same compiler semantics.

## Safety / Parity Evidence

- SourceFingerprint defaults to cheap F0/F1 and only becomes F2 after semantic
  probe facts; F3 full hashing is never automatic.
- Media-preview cache version participates in cache identity.
- corrupt/missing/zero-byte/version-mismatched media-preview entries are treated
  as disposable misses and regenerated.
- generation-based stale-result rejection remains in the existing
  MediaPreviewCache and decoded visual preview path.
- Spectrum request generation/invalidation behavior remains covered by existing
  asynchronous tests.
- Accurate Preview still delegates to the current Step08 compiler adapter.

## Final-Head Rule

This evidence records the validated runtime candidate. The subsequent
status/evidence/handoff commit changes documentation only. The same
`v2-m5-probe-preview-cache.yml` workflow must be green on the final branch head
before M5 handoff is complete.
