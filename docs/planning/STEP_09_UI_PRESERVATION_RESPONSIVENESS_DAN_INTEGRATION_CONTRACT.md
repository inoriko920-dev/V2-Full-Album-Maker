# STEP 09 — UI Preservation, Responsiveness, dan Integration Contract

## Status
PASS — planning complete. Coding remains BLOCKED.

## Scope
STEP 09 preserves the existing production UI/workflow while defining explicit route composition, responsive behavior, UI-thread safety, and visual-regression gates. No source/UI implementation change was made.

## Baseline Contracts
- Keep all 9 routes in current order: Beranda, Media, Album, Timeline, Visual, Template, Spectrum, AI Agent, Render.
- Keep the existing professional white/blue shell and user mental model.
- Preserve Global Command Bar, Navigation, Context panel, center Workspace, right Inspector/AI dock, Timeline dock, and Status bar.
- Current production UI is the migration no-regression baseline.
- Frozen canonical 1672x941 golden references remain immutable design/reference evidence.
- Historical pixel-match remediation is a separate workstream and must not be mixed silently into architecture migration.
- No new UI-image prompt/reference set is required because this V2 scope explicitly preserves the existing UI.

## Decisions D09-01..D09-20
1. Existing shell geometry/tokens are migration contracts.
2. All 9 workspace routes/order and mental model stay stable.
3. WorkspaceBundle/WorkspaceRegistry owns explicit route composition and lifecycle.
4. Runtime UI patches retire route-by-route only after visual/state parity.
5. Heavy I/O/process/network/analysis never runs on the UI thread.
6. Busy/progress/cancel UI mirrors underlying task state machines and remains non-blocking.
7. Typed errors map to concise user messages plus separate technical evidence.
8. Global status is a projection of application state, not a second truth store.
9. Global commands stay shell/application-owned with stable shortcuts.
10. Inspector/context/timeline routing moves to WorkspaceBundle; manual hide lists are transitional.
11. Required responsive evidence: 1672/100%, 1366/100%, 125%, and 150%.
12. DPI/Unicode/path fixes may harden technical behavior without redesign.
13. Current production baseline is the migration no-regression authority; frozen goldens remain immutable references.
14. MUST KEEP features must remain discoverable after migration.
15. AI Agent UI preserves Send → Preview → Execute confirmation → Cancel → Undo truth.
16. Render Center completes only from RenderEngine verified/published evidence.
17. UI is an intent/projection surface; ProjectDocument/application services remain authoritative.
18. No new UI image prompt is needed for this preservation scope.
19. Architecture migration and pixel-match remediation remain separate unless explicitly combined by the user.
20. Render route migrates last after lower-risk routes prove the WorkspaceRegistry/lifecycle pattern.

## Planned UI Migration U1..U10
- U1: freeze current 9-route screenshots, geometry, and functional baseline.
- U2: introduce WorkspaceRegistry returning legacy bundles first.
- U3: bind shell/global commands/status to ProjectSession and application services.
- U4: migrate Home.
- U5: migrate Media and async probe/cache UI binding.
- U6: migrate Album and Timeline routing.
- U7: migrate Visual, Template, and Spectrum with preview task ownership.
- U8: migrate AI Agent via AIPlanningService/TaskSupervisor.
- U9: migrate Render last via RenderEngine/ProcessSupervisor.
- U10: retire obsolete route hide/show/install patch lists after full UI regression.

## Responsive / UI-Thread Gates
- No FFmpeg/ffprobe, folder scan/probe, Accurate Preview, BeatAnalysis, Gemini/network, heavy cache generation, or render verification/publish on the UI thread.
- 1366 width remains the minimum supported design evidence point.
- 1672x941 remains the deterministic canonical capture viewport.
- DPI 125% and 150% are mandatory smoke/evidence points.
- Compact navigation must retain tooltips/accessibility names.
- Progress 100% never means success until the owning operation has verified completion.

## Next STEP
STEP 10 — Testing, Regression, Stress, Benchmark, dan Release Quality Gate.

Coding remains BLOCKED.
