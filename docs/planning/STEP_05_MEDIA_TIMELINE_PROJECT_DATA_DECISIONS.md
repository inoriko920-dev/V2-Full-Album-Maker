# STEP 05 — Media, Preview, Cache, Timeline, dan Project Data

Status: **PASS**  
Phase: **PLANNING**  
Coding: **BLOCKED**

## Final Decisions

- **D05-01** — ProjectDocument UUID `asset_id` is the sole canonical media identity. Path-derived Media Library IDs are compatibility/projection keys only.
- **D05-02** — SourceFingerprint uses tiered facts; fingerprint strength depends on operation cost and risk.
- **D05-03** — MediaProbeService with ffprobe as initial adapter is the shared normalized metadata source.
- **D05-04** — Import workers prepare proposals; project commits occur only through controlled application/domain transactions.
- **D05-05** — Relink preserves asset UUID and all references. Incompatible media kind or source duration requires explicit resolution.
- **D05-06** — Media sidecar has independent versioning; do not bump ProjectDocument schema for library-convenience metadata.
- **D05-07** — Path resolution is deterministic: explicit locator -> relative path -> explicit relink/search assistance. No hidden full-drive search.
- **D05-08** — Accurate Preview remains the parity oracle for final composition semantics.
- **D05-09** — Preview scheduling is generation-aware, cancellable/coalesced, and off the UI thread.
- **D05-10** — CacheManager centralizes namespace/version/quota/invalidation; all caches are disposable.
- **D05-11** — TIMEBASE=240000 integer ticks/sec remains authoritative.
- **D05-12** — Packed / Free / gap / crossfade semantics remain frozen.
- **D05-13** — Project timeline is time-based, not source-frame-number-based; VFR remains a source metadata/timestamp concern.
- **D05-14** — ProjectDocument schema_version=2 remains frozen during initial V2 consolidation.
- **D05-15** — Extensions require namespace/version discipline, JSON-only payloads, validation, and technology-neutral data.
- **D05-16** — Project migration is deterministic and yields one current-schema document or a typed failure.
- **D05-17** — Save/Reopen correctness is normalized semantic equality, not JSON byte equality.
- **D05-18** — Missing media does not corrupt the project; references remain available for relink and dependent operations block only when required.

## Media Identity

Canonical domain identity:
- `asset_id`: stable UUID
- `locator`: current source location
- `relative_path`: optional project-relative hint
- `fingerprint`: source-version facts
- `metadata`: normalized technical/source metadata

Relink must not be implemented as remove+add. It updates source resolution data while preserving `asset_id`, song references, visual references, layer refs, AI stable IDs, and undo semantics.

## Source Fingerprint Tiers

- **F0** — locator/path hint
- **F1** — size + mtime
- **F2** — semantic probe facts
- **F3** — optional full SHA-256

Do not hash multi-gigabyte media repeatedly for low-risk UI/cache tasks.

## Preview / Cache

Preview classes:
1. Library thumbnail
2. Approximate interactive editor preview
3. Accurate frame preview
4. Render preview/check

Accurate Preview is the parity oracle and uses the same project/timeline composition semantics as Render.

Cache namespaces planned:
- media-preview
- probe
- accurate-preview
- spectrum-preview
- template-thumbnail
- beat-analysis

Cache corruption/version mismatch/zero-byte entries are cache misses, not project corruption.

## Timeline

- TIMEBASE: 240000 ticks/sec.
- Domain timing is integer-tick based.
- Packed: songs contiguous.
- Free: explicit `free_start_tick`; gap means silence.
- Free overlap requires one valid crossfade pair and exact overlap/crossfade agreement.
- Triple overlap remains invalid.
- VFR video does not change the project timeline clock.
- TimelineResolver remains a pure document -> resolved timeline/errors operation.

## Project Data

Project schema v2 remains frozen. Do not serialize Qt objects, NumPy arrays, Path objects, threads, subprocesses, provider instances, or raw binary into ProjectDocument/extensions.

Future extension keys should use explicit feature/version naming and validators.

Project loading:
- current v2 -> strict validation
- legacy v1 -> deterministic migration
- future schema -> fail closed
- timeline-only legacy -> explicit not-a-project error
- corrupt/unknown -> typed schema error

## Planned Implementation Slices (Future SOL Only)

- **P1** — Canonical SourceFingerprint + MediaProbeResult contracts.
- **P2** — ffprobe MediaProbe adapter around current behavior.
- **P3** — MediaIdentityResolver mapping ProjectDocument UUIDs to legacy Media Library projection keys.
- **P4** — MediaService import/relink commands.
- **P5** — CacheManager namespaces around current caches.
- **P6** — PreviewEngine wrapper around AccuratePreviewService.
- **P7** — Formal TimelinePort/Resolver contract without behavior changes.
- **P8** — Sidecar v1->v2 read/migration implementation if approved.
- **P9** — ProjectPersistence normalized roundtrip + deterministic path resolution.
- **P10** — Fault/performance/portable regression before retiring legacy direct paths.

## No-Go

- No path-derived ProjectDocument identity.
- No relink remove+add behavior.
- No hidden duration clamp.
- No automatic full-drive media search.
- No authoritative float-second timeline.
- No cache artifact as project truth.
- No project schema bump merely for refactor.
- No approximate preview presented as accurate.
- No independent Preview and Render timeline semantics.
- No silent future-schema acceptance.
- No source-file mutation during import/relink/probe.
- No sidecar failure blocking project open/render.

## Next
STEP 06 — Render Engine, Processing Pipeline, dan Long-Album Reliability.
