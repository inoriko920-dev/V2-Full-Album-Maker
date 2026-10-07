# M7 — Workspace Registry

Status: **PASS — implemented and validated**

## Scope

M7 introduces the approved AppKernel-owned `WorkspaceRegistry` and routes the
existing nine production workspaces through that boundary without redesigning
the UI or changing ProjectDocument ownership.

The migration follows D03-09 and STEP 09 U2–U9:
- wrap current proven route behavior first;
- move route dispatch and workspace replacement behind WorkspaceRegistry;
- preserve the current route callbacks as adapters;
- keep the exact route order and user mental model;
- migrate Render last.

M8 legacy bridge retirement is explicitly not part of M7.

## Canonical Route Order

The registry preserves exactly:

1. home — Beranda
2. media — Media
3. album — Album
4. timeline — Timeline
5. visual — Visual
6. template — Template
7. spectrum — Spectrum
8. ai_agent — AI Agent
9. render — Render

No route was renamed, reordered, added, or removed.

## New Boundary

`src/full_album_maker/workspace_registry.py` adds:

- `WorkspaceDescriptor`
  - immutable route/label/icon/order metadata.

- `WorkspaceBundle`
  - one route's workspace plus optional context, inspector, and timeline surfaces;
  - surfaces remain opaque objects so the registry itself imports no PySide6.

- `WorkspaceListenerRecord`
  - deterministic registration/dispatch metadata.

- `WorkspaceRegistry`
  - owns canonical route order;
  - owns workspace bundle registration;
  - owns public route workspace replacement through an injected adapter;
  - owns deterministic listener ordering;
  - owns current route projection;
  - provides `assert_complete()` for the nine-route production gate;
  - falls back to Home for an unknown route rather than producing an invalid route.

- bounded ContextVar binding
  - lets the legacy Qt shell capture the exact AppKernel-owned registry while it
    is constructed;
  - context is reset after legacy runtime execution.

## AppKernel Ownership

CompositionRoot now creates or accepts exactly one `WorkspaceRegistry`.

AppKernel validates that the registry's routes match the canonical
`WORKSPACE_ORDER`.

During GUI launch the registry is bound beside the M4–M6 service facades.

`FoundationShellWidget`:
- captures the exact bound registry when launched through AppKernel;
- attaches its Qt `WorkspaceStack.replace_route` adapter;
- otherwise creates a local registry only for standalone fixtures/captures.

This keeps CompositionRoot as the dependency-wiring owner while the registry
itself remains Qt-agnostic.

## Single Route Signal Owner

Before M7, route modules subscribed directly to
`FoundationUiState.workspace_changed`.

After M7:
- `FoundationShellWidget` is the only source module that subscribes directly;
- the signal calls `WorkspaceRegistry.activate`;
- the registry dispatches the existing route adapters in deterministic
  registration order.

The existing adapter order remains equivalent to the previous signal order:
- shell projection first;
- Home;
- Media;
- Media completion observer;
- Album;
- Timeline;
- Visual;
- Template;
- Spectrum;
- AI Agent;
- Render;
- STEP11 integration observer.

Render remains the final migrated workspace route. The STEP11 observer is not a
workspace route owner.

## Workspace Replacement Ownership

Feature modules no longer access `workspace_stack._index`.

Production route widgets are installed with
`WorkspaceRegistry.register_bundle()`; the registry delegates replacement to
the shell's public `WorkspaceStack.replace_route()` adapter.

The adapter:
- preserves the canonical route slot;
- removes the old placeholder;
- restores the same current route if the replaced widget was active;
- reparents the retired placeholder exactly as before.

Capture utilities for Home and Media also use the public registry boundary
instead of private stack indices.

## Route Bundles

M7 registers the existing production surfaces, not redesigned replacements:

- Home: HomeWorkspace + HomeInspector + existing timeline surface.
- Media: MediaWorkspace + MediaContextWidget + MediaInspectorWidget +
  MediaTimelinePreviewCanvas.
- Album: AlbumWorkspace + AlbumContextWidget + AlbumMassToolsWidget +
  AlbumTimelineOverviewCanvas.
- Timeline: TimelinePreviewWorkspace + TimelineContextWidget +
  TimelineClipInspector + TimelinePrecisionPanel.
- Visual: VisualPreviewWorkspace + VisualSongContext + VisualInspector +
  VisualAlignmentCanvas.
- Template: TemplateGalleryWorkspace + TemplateFilterContext +
  TemplateInspector + VisualAlignmentCanvas.
- Spectrum: SpectrumWorkspace + SpectrumLayerContext + SpectrumInspector +
  SpectrumTimelineCanvas.
- AI Agent: AITaskCanvas + AIConversationPanel + AIContextDock +
  TimelinePrecisionPanel.
- Render: RenderCenterWorkspace + RenderHistoryContext +
  RenderSettingsInspector + existing collapsed timeline host.

## Preserved Transitional Adapters

M7 intentionally does **not** remove the existing route callback methods or
their transitional hide/show logic.

Examples remain:
- `_s03_route`
- `_s04_route`
- `_s05_route`
- `_s06_route`
- `_s07_route`
- `_s08_route`
- `_s09_route`
- `_s10_route`

They are now listeners owned/dispatched by WorkspaceRegistry rather than direct
signal owners.

Retiring obsolete route hide/show/install patch lists belongs to M8 after M7
ownership/parity evidence, matching D03-15 and STEP 09 U10.

## UI Preservation

M7 does not change:
- professional white/blue shell;
- navigation labels/order;
- Global Command Bar;
- Context panel;
- center Workspace;
- right Inspector/AI dock;
- Timeline dock;
- Status bar;
- shortcuts;
- ProjectDocument/application-service truth;
- existing busy/progress/cancel behavior.

No new UI prompt/reference images are required because this is an architecture
migration under the existing UI baseline.

## Rollback

M7 is additive and branch-isolated.

Rollback target:
- M6 PASS head: `0947940cb8a447e28fb7a361807d2c98cb4e6857`.

No schema/data migration is introduced.

## Gate

M7 is PASS only after:
1. M0–M7 contracts pass;
2. all nine production routes are registered and complete;
3. no non-shell source module subscribes directly to
   `workspace_changed.connect`;
4. no non-shell source module accesses `workspace_stack._index`;
5. all nine route functional UI tests remain PASS;
6. navigation remains read-only against authoritative ProjectDocument;
7. canonical persistence/production shell remains PASS;
8. responsive/shell regression tests remain PASS;
9. 200-song/~3-hour structural stress remains PASS;
10. real Spectrum/Accurate Preview parity remains PASS after route migration;
11. no M8 cleanup, UI redesign, schema bump, dependency change, or release work
    is mixed into M7.

## Validation Evidence

Validated candidate head:
- branch: `impl-m7-workspace-registry`
- initial runtime commit:
  `62da009ab3abd79e4c16baafad7890b53f7d4232`
- ownership cleanup candidate:
  `3e0af4f8b5c7a344a481b02f8805286209182b6f`
- GitHub Actions run: `37597489445`

Main `m7-workspace-registry` job: **SUCCESS**
- Q0 compile: PASS
- M0–M7 contracts: **63 passed, 4 skipped**
- nine-route functional UI: **42 passed**
- production navigation + persistence: **13 passed**
- responsive + shell regressions: **23 passed**
- 200-song/~3-hour structural stress: **2 passed**

Targeted `real-ffmpeg-m7`: **SUCCESS**
- **2 passed**
- existing Accurate Preview/final-render parity remains green;
- existing Spectrum Accurate Preview compiler parity remains green.

The documentation-only final commit must keep the same M7 workflow green before
handoff is complete.

## Next

M7 is PASS. The next allowed migration phase is
**M8 — Legacy Bridge Retirement**.

M8 is not started in this turn.
