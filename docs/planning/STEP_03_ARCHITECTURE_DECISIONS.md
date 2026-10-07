# STEP 03 — Target Architecture V2 & Strategi Migrasi Bertahap

## Gate
PASS

## Coding Status
BLOCKED — planning only.

## Target Architecture
Layered architecture with ports/adapters and one explicit CompositionRoot/AppKernel.

Dependency direction:
Presentation (PySide6) -> Application Services -> Domain -> Ports <- Infrastructure Adapters.

ProjectDocument + EditorController remain the authoritative project/history state.

## Core Runtime Boundaries
- AppKernel / CompositionRoot
- ProjectSession
- WorkspaceRegistry
- TaskSupervisor / TaskScope
- CapabilityRegistry
- MediaProbeService
- CacheManager
- PreviewEngine
- RenderEngine
- ProjectPersistence
- BeatAnalysisService
- AIPlanningService

## Migration Strategy
Strangler/adaptor-first migration. Existing proven implementation is wrapped first; implementation replacement happens only after parity evidence.

Phases:
- M0 Characterization
- M1 Composition Root
- M2 Task Lifecycle
- M3 Persistence
- M4 Render Facade
- M5 Probe / Preview / Cache
- M6 Beat Analysis
- M7 Workspace Registry
- M8 Legacy Bridge Retirement
- M9 Consolidation

No phase may combine architecture migration with user-facing redesign.

## Official Decisions
- D03-01: TaskSupervisor/TaskScope is the central async lifecycle boundary.
- D03-02: MediaProbeService uses ffprobe/current logic as initial adapter.
- D03-03: CacheManager unifies cache policy/namespace/invalidation, not payload format.
- D03-04: PreviewEngine facade comes before decode optimization; current FFmpeg accurate preview remains canonical.
- D03-05: RenderEngine wraps current STEP10 -> Step08 -> V13 -> S11 -> FFmpegV2 chain before compiler consolidation.
- D03-06: BeatAnalysisService is additive; FFmpeg PCM + optional NumPy candidate; non-reactive fallback is mandatory.
- D03-07: ProjectPersistence isolates legacy compatibility; no new V2 service may add a fresh dependency on Project v1.
- D03-08: AI provider is separated from validation/execution through AIPlanningService.
- D03-09: WorkspaceRegistry replaces runtime patch ownership one route at a time.
- D03-10: Dual-path is allowed for rollback/testing only; dual-write project state is forbidden.
- D03-11: AppKernel/CompositionRoot becomes the single dependency-wiring location.
- D03-12: Domain remains technology-neutral and free of PySide6/subprocess/network dependencies.
- D03-13: ProjectSession owns project runtime context without replacing ProjectDocument.
- D03-14: Python >=3.11, FFmpeg, PySide6, project schema v2, and Windows portable remain frozen.
- D03-15: Migration order is M0 through M9; cleanup cannot precede proven ownership/parity.

## Legacy Retirement Rule
Legacy code may be removed only after it is no longer a production owner and behavior contracts have replacement evidence.

## Next STEP
STEP 04 — Hardening Stabilitas, Lifecycle, Error Handling, dan Recovery.
