# M8 — Legacy Bridge Retirement Evidence

Status: **PASS**

## Candidate

- Branch: `impl-m8-legacy-bridge-retirement`
- M7 rollback/base: `398183204a6bef776f363472ac7834c797365c75`
- Retirement commit:
  `4ab91eaf9928f60c91a518f7bd9fd99a382eb8af`
- Validated candidate head:
  `006d64eff4a0793162cb759a8cd77476a1a9c704`
- GitHub Actions run: `37598817830`

## Removed production bridge modules

Physically removed:
- `src/full_album_maker/media_feature_activation.py` — 51 lines
- `src/full_album_maker/album_restore_fix.py` — 118 lines
- `src/full_album_maker/timeline_route_fix.py` — 46 lines

`main.py` also removed their three imports and three installer calls.

## Replacement ownership evidence

### Media activation

No replacement timer was created.

M7 WorkspaceRegistry/WorkspaceStack now owns the relevant route/widget
coherence. A production subprocess boots with persisted Media, Album, and
Timeline routes and proves route state, registry state, and current widget stay
identical after queued event processing.

### Album compatibility

The valid portion of `album_restore_fix.py` moved into `album_feature.py`.

The focused M8 test proves legacy active-audio compatibility only mirrors
locators that already exist in legacy `Project.audios`, while a V2-only audio
asset remains solely in ProjectDocument.

The candidate gate also exposed and removed one hidden dependency on the old
bridge-injected `_capture_document` name. The canonical owner now calls
`_s04_capture_document` directly.

### Timeline presentation

The valid portion of `timeline_route_fix.py` moved into
`timeline_feature_step05.py`.

Production evidence proves:
- the precision panel keeps `↔ Ripple` and `⌁ Snap`;
- leaving Timeline restores the same Foundation generic timeline controls.

No global wrapper remains around `Window._s05_route`.

## Intentionally retained production bridges

Static M8 evidence requires these files to remain present because their
production behavior is not yet replaced:
- `media_layout_fix.py`
- `timeline_completion_step05.py`
- `visual_timeline_completion_step06.py`
- `integration_completion_step11.py`
- `render_queue_presentation_step10.py`

This prevents M8 from turning into unproven cleanup.

## Diff scope

M7 -> validated M8 candidate contains only:
- M8 workflow/test additions;
- Album owner absorption;
- Timeline owner absorption;
- main installer retirement;
- deletion of the three proven obsolete bridges.

No service/compiler/schema/UI redesign/dependency/release scope is included.

## Regression results

Main M8 job: **SUCCESS**
- M0–M8 contracts: 68 passed, 4 skipped
- retired bridge parity: 8 passed
- nine-route UI: 42 passed
- production navigation/persistence/render/preview: 25 passed, 2 skipped
- responsive/lifecycle: 28 passed
- long-album stress: 2 passed

Real FFmpeg M8 job: **SUCCESS**
- 3 passed

## Final-head rule

This evidence records the validated runtime candidate. The following
documentation-only commit changes governance/evidence only. The same
`v2-m8-legacy-bridge-retirement.yml` workflow must be green on the final
branch head before M8 handoff is complete.
