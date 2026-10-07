# M7 — Workspace Registry Evidence

Status: **PASS**

## Candidate

- Branch: `impl-m7-workspace-registry`
- M6 rollback/base: `0947940cb8a447e28fb7a361807d2c98cb4e6857`
- Initial M7 runtime commit:
  `62da009ab3abd79e4c16baafad7890b53f7d4232`
- Validated ownership-clean candidate:
  `3e0af4f8b5c7a344a481b02f8805286209182b6f`
- GitHub Actions run: `37597489445`

## Ownership Evidence

`WorkspaceRegistry` is AppKernel-owned and Qt-agnostic.

The shell captures the exact bound instance and injects one public
WorkspaceStack replacement adapter.

Static M7 contract scans every `src/full_album_maker/*.py` file and proves:
- only `foundation_shell.py` directly subscribes to
  `workspace_changed.connect`;
- no non-shell source module uses `workspace_stack._index`.

The first candidate correctly exposed three remaining legacy leaks:
- `home_capture.py` private stack index;
- `media_capture.py` private stack index;
- `integration_completion_step11.py` direct route signal subscription.

All three were migrated to the registry boundary in
`3e0af4f8b5c7a344a481b02f8805286209182b6f`.

## Nine-Route Production Evidence

A full production subprocess imports the complete installer chain through
STEP11, constructs FoundationMainWindow, and requires:

`home, media, album, timeline, visual, template, spectrum, ai_agent, render`

for both:
- `registry.routes`;
- `registry.registered_routes`.

`registry.assert_complete()` passes.

Every route activation requires:
- FoundationUiState route equals requested route;
- WorkspaceRegistry current route equals requested route;
- WorkspaceStack current widget is the bundle workspace.

Render-route registration occurs after AI Agent, preserving STEP 09's
Render-last workspace migration rule.

## Read-Only Navigation Evidence

The existing production subprocess navigation characterization remains green:
all nine route changes preserve the authoritative ProjectDocument normalized
hash.

Route activation remains UI projection only and cannot become a second project
truth store.

## UI / Responsive Evidence

Focused nine-route UI suite: **42 passed**.

Responsive/shell regression suite: **23 passed**.

This covers the existing foundation and route UIs, toolbar responsiveness,
layout, media UI regressions, and engine/UI hardening without introducing a
pixel-match remediation workstream.

## Persistence / Stress Evidence

Production navigation + persistence suite: **13 passed**.

200-song/~3-hour structural stress: **2 passed**.

ProjectDocument schema v2, TIMEBASE=240000, ProjectPersistence, and the current
M2–M6 service ownership remain unchanged.

## Real FFmpeg Evidence

Targeted real-FFmpeg job: **SUCCESS — 2 passed**.

It proves route-composition migration did not change:
- Accurate Preview vs final render parity;
- Spectrum Accurate Preview compiler parity.

## Regression Summary

Main M7 job: **SUCCESS**
- M0–M7 contracts: 63 passed, 4 skipped
- nine-route functional UI: 42 passed
- production navigation + persistence: 13 passed
- responsive + shell regressions: 23 passed
- long-album structural stress: 2 passed

Targeted real-FFmpeg job:
- 2 passed

## Final-Head Rule

This evidence records the validated runtime candidate. The following
documentation-only commit changes governance/evidence only. The same
`v2-m7-workspace-registry.yml` workflow must be green on the final branch
head before M7 handoff is complete.
