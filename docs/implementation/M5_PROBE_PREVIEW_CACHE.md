# M5 — Probe / Preview / Cache

Status: **PASS — implemented and validated**

## Scope

M5 introduces the approved application-service boundaries for media probing,
preview orchestration, and disposable cache policy while preserving the current
proven implementations as adapters.

This slice follows the strangler/adaptor-first rule:
- current FFprobe/FFmpeg duration behavior remains the initial probe adapter;
- current `AccuratePreviewService` remains the accurate-frame implementation;
- current `MediaPreviewCache` keeps its bounded workers, de-duplication, and
  generation stale-result guard;
- current Spectrum and template-thumbnail cache payload formats remain unchanged;
- cache roots that already existed before M5 keep the same paths;
- no ProjectDocument schema change, UI redesign, Beat Analysis M6,
  WorkspaceRegistry M7, compiler rewrite, dependency change, or release work is
  included.

## New Boundaries

### MediaProbeService

`src/full_album_maker/media_probe_service.py` adds:
- `SourceFingerprint` with D05 tier semantics:
  - F0 locator;
  - F1 size + mtime;
  - F2 normalized semantic probe facts;
  - F3 optional full SHA-256, never calculated automatically.
- `MediaProbeResult` as the normalized result contract.
- `MediaProbeService` as the shared probe facade.
- a bounded ContextVar migration bridge so legacy constructors can capture the
  exact AppKernel-owned service before worker threads start.

The default adapter preserves current behavior:
- video duration -> current FFprobe stream-duration logic;
- audio duration -> current decoded/gapless FFmpeg progress logic with FFprobe
  fallback;
- photo dimensions -> current proven image probe;
- audio title/artist -> current proven tag probe.

### CacheManager

`src/full_album_maker/cache_manager.py` adds one namespace/policy owner for
disposable cache data.

Declared namespaces:
- `media-preview`
- `probe`
- `accurate-preview`
- `spectrum-preview`
- `template-thumbnail`
- `beat-analysis`

Existing production roots are preserved:
- `media-preview` -> existing `data/cache/media-previews`;
- `spectrum-preview` -> existing `temp/spectrum-preview-step08-v1`;
- `template-thumbnail` -> existing `data/cache/template_thumbnails_v1`.

The manager owns namespace version/root/quota policy and bounded eviction.
Zero-byte, missing, corrupt, or version-mismatched entries are cache misses, not
project failures.

### PreviewEngine

`src/full_album_maker/preview_engine.py` adds the canonical M5 facade for:
- Accurate Preview frame rendering;
- library media-preview path/generation/invalidation;
- creation of the existing generation-aware `MediaPreviewCache` adapter;
- cache-root lookup through the AppKernel-owned CacheManager.

Accurate Preview still delegates to the existing Step08 compiler path and does
not create a second composition model.

## Production Ownership After M5

`CompositionRoot` creates/accepts exactly one:
- `MediaProbeService`;
- `CacheManager`;
- `PreviewEngine`.

The PreviewEngine must use the exact CacheManager owned by the same AppKernel.

During normal GUI launch the kernel temporarily binds these services alongside
RenderEngine. Legacy runtime constructors capture the exact instances before
their background workers start.

Production routes changed in M5:
- legacy async import/relink probe -> MediaProbeService;
- editor Accurate Preview -> PreviewEngine;
- Media workspace preview queue -> PreviewEngine -> existing MediaPreviewCache;
- decoded visual preview queue -> PreviewEngine -> existing MediaPreviewCache;
- Spectrum Accurate Preview -> PreviewEngine;
- Spectrum cache root -> CacheManager;
- template-thumbnail default cache root -> CacheManager.

No dual project-state write path was introduced.

## Preserved STEP 05 / STEP 06 Contracts

- D05-02: source fingerprints are tiered; expensive full hash is not automatic.
- D05-03: FFprobe/current logic remains the initial MediaProbeService adapter.
- D05-08: Accurate Preview remains the parity oracle.
- D05-09: existing generation-aware asynchronous preview stale guards remain.
- D05-10: cache namespace/version/invalidation policy is centralized while
  payload format remains in proven adapters.
- D05-11: TIMEBASE=240000 is unchanged.
- D05-12/D05-13: timeline semantics are unchanged.
- D05-14: ProjectDocument schema_version=2 is unchanged.
- D05-18: cache/media failure is not promoted to project corruption.
- D06-17: Accurate Preview continues to use the same composition/compiler
  semantics as final Render.

## Cache Hardening

The media-preview adapter now validates the sidecar metadata before accepting a
cache hit:
- namespace version;
- asset ID;
- canonical source key;
- media type;
- preview filename.

A corrupt/missing metadata file, zero-byte PNG, or version mismatch is evicted
as disposable cache state and regenerated. Source media remains read-only.

## Lifecycle Note

M5 does not silently replace the existing worker/process lifecycle architecture.
The existing MediaPreviewCache worker queue and Spectrum executor remain in
place behind the new facade. H3 ProcessSupervisor and unrelated legacy worker
retirement are outside M5.

## Rollback

M5 is additive and branch-isolated.

Rollback target:
- M4 PASS head: `d23f91f331942f2abbbfb9b4133439ebcc163fab`.

No data/schema migration is introduced.

## Gate

M5 is PASS only after:
1. M0–M5 contract tests pass;
2. existing library-preview cache tests pass;
3. decoded visual preview generation/stale-result tests pass;
4. Accurate Preview/Spectrum preview parity tests pass;
5. template-thumbnail cache parity remains PASS;
6. production Save and nine-workspace characterization remain PASS;
7. 200-song/~3-hour structural stress remains PASS;
8. real FFmpeg proves the probe adapter and existing Accurate Preview parity;
9. branch diff contains no M6/M7/UI/schema/release scope.

## Validation Evidence

Validated runtime candidate:
- commit: `6aa2a14a3bb52d0b598cba19526c3b99191adedd`
- GitHub Actions run: `37594113013`
- `m5-probe-preview-cache`: SUCCESS
  - Q0 compile: PASS
  - M0–M5 contracts: **50 passed, 2 skipped**
  - focused probe/preview/cache parity: **9 passed**
  - persistence + production shell: **12 passed**
  - 200-song/~3-hour structural stress: **2 passed**
- `real-ffmpeg-m5`: SUCCESS
  - **3 passed**
  - includes real FFmpeg/ffprobe audio probing;
  - existing Accurate Preview vs final-render frame parity;
  - existing Spectrum Accurate Preview compiler parity.

The following documentation-only commit must keep the same M5 workflow green on
the final branch head before handoff is considered complete.

## Next

M5 is PASS. The next allowed migration phase is **M6 — Beat Analysis**.
M6 is not started in this turn.
