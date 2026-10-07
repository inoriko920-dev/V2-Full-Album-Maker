# M9 — Consolidation

Status: **PASS — implemented and validated**

## Scope

M9 completes the M0–M9 architecture migration sequence by consolidating the
surviving production bootstrap ownership without changing feature behavior,
ProjectDocument authority, UI design, compiler semantics, dependencies, or
release mechanics.

This slice deliberately does not perform a compiler rewrite. The current proven
render semantics remain:

Step08 -> V13 -> S11 -> FFmpegV2

M9 consolidates already-proven runtime preparation ownership only.

## Problem before M9

After M8, `main.py` still:
- imported every surviving compatibility/presentation installer directly;
- called 27 installers one by one;
- implicitly owned the exact ordering contract for the whole recovered runtime.

That made the entrypoint a second wiring map next to AppKernel/CompositionRoot
and made future ownership auditing difficult.

## Consolidated production bootstrap

New module:

`src/full_album_maker/production_runtime.py`

It introduces:
- `RuntimeInstaller` — immutable installer name/callable pair;
- `ProductionRuntimeInstaller` — explicit ordered installer owner;
- `PRODUCTION_INSTALLERS` — exact canonical 27-installer manifest;
- `PRODUCTION_INSTALLER_NAMES` — stable order evidence;
- `DEFAULT_PRODUCTION_RUNTIME_INSTALLER`;
- `install_production_runtime()` — one production preparation entrypoint.

## Exact preserved installer order

The manifest preserves the proven runtime order exactly:

1. playlist-feature
2. gemini-schema-compat
3. playlist-hardening
4. visual-feature
5. engine-hardening
6. source-integrity
7. ui-hardening
8. atomic-bundle
9. render-lifecycle
10. project-dirty-state
11. async-import
12. step03-media
13. step03-media-completion
14. step03-media-layout-fix
15. step04-album
16. step05-timeline
17. step05-timeline-completion
18. step06-visual
19. step06-visual-preview-decode
20. step06-visual-timeline-completion
21. step07-template
22. step08-spectrum
23. step09-ai-agent
24. step10-queue-presentation
25. step10-render
26. step11-integration
27. step11-integration-completion

No installer was reordered, added, or removed during M9.

## Idempotent / partial-failure behavior

`ProductionRuntimeInstaller` tracks completed installer names.

A second successful `install()` call:
- does not rerun already-completed global monkey-patches;
- returns the same completed order.

If installer B fails after installer A completed:
- A stays marked completed;
- a same-process diagnostic retry resumes at B;
- A is not executed twice.

This is safer than a raw list of repeated module-level calls.

## Production entrypoint simplification

`main.py` now imports only:
- `build_app_kernel`;
- `install_production_runtime`.

It performs one:

`install_production_runtime()`

before the lazy `v14_window` import.

This preserves the established import-time preparation contract relied on by the
existing production tests while removing individual installer ownership from
the entrypoint.

The GUI still launches through AppKernel:

`build_app_kernel(...).run(args)`

Portable smoke routing remains unchanged.

## Boundaries intentionally not consolidated

M9 does not:
- remove still-required M8-retained compatibility/completion modules;
- merge ProjectDocument with legacy Project;
- replace EditorController/EditorSession;
- change TaskSupervisor lifecycle;
- change ProjectPersistence;
- change RenderEngine/PreviewEngine/MediaProbeService/CacheManager;
- change BeatAnalysisService;
- change WorkspaceRegistry;
- change current render compiler semantics;
- change AI provider behavior;
- redesign UI/workspaces;
- change schema v2 or TIMEBASE=240000;
- change Python/FFmpeg/PySide6 support policy;
- change Windows packaging/release automation.

Those require their own quality/release gates and are not silently bundled into
M9.

## Migration sequence completion

With M9 PASS, the architecture migration sequence defined by STEP 03 is
complete:

M0 Characterization
-> M1 Composition Root
-> M2 Task Lifecycle
-> M3 Persistence
-> M4 Render Facade
-> M5 Probe / Preview / Cache
-> M6 Beat Analysis
-> M7 Workspace Registry
-> M8 Legacy Bridge Retirement
-> M9 Consolidation

This does **not** mean v2.0.0 is release-ready yet.

STEP 10 still requires promotion through Q2–Q5, and STEP 11 release blockers
must be closed before stable publication.

## Rollback

M9 is branch-isolated.

Rollback target:
- M8 PASS head: `9513edf833d4649225e2b66fcaf27d4f909948fb`.

No project-data migration is introduced.

## Gate

M9 is PASS only after:
1. production installer manifest preserves exact proven order;
2. bootstrap installer is idempotent;
3. partial-failure retry does not rerun completed installers;
4. main has one bootstrap owner rather than individual installer wiring;
5. legacy GUI import remains after runtime installation;
6. schema/timebase/routes remain frozen;
7. M0–M9 contracts pass;
8. M8 retirement parity remains green;
9. all nine UI route tests pass;
10. production navigation/persistence/render/preview pass;
11. lifecycle/entrypoint regressions pass;
12. 200-song/~3-hour structural stress passes;
13. real FFmpeg render/Spectrum/BeatAnalysis evidence remains green;
14. no Q4/Q5 build/release mutation is mixed into M9.

## Validation evidence

Validated candidate:
- branch: `impl-m9-consolidation`
- runtime consolidation commit:
  `8d8c9088bc8974b6c2de90a4791117f2dcc9fdd8`
- candidate head after test correction:
  `4a9a4b2f91b0dd81b749d02fd356c00d6b14b817`
- GitHub Actions run: `37600034073`

Main `m9-consolidation` job: **SUCCESS**
- Q0 compile: PASS
- M0–M9 contracts: **73 passed, 4 skipped**
- consolidated bootstrap + retirement parity: **13 passed**
- nine-route functional UI: **42 passed**
- production navigation/persistence/render/preview: **25 passed, 2 skipped**
- responsive/lifecycle/entrypoint regressions: **29 passed**
- 200-song/~3-hour structural stress: **2 passed**

Targeted `real-ffmpeg-m9`: **SUCCESS**
- **3 passed**

## Next quality gate

M9 completes the architecture migration sequence.

The next allowed work is **Q2 — Integration Quality Gate** from STEP 10:
- full pytest regression floor;
- cross-workspace/session/lifecycle integration;
- no Windows stable publication yet.

Q3/Q4/Q5 remain later gates.

M9 does not start Q2 in this turn.
