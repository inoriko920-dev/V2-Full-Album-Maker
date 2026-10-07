# M8 — Legacy Bridge Retirement

Status: **PASS — implemented and validated**

## Scope

M8 retires only legacy bridge modules that are no longer production owners and
whose replacement behavior already has M2–M7 ownership/parity evidence.

The retirement rule is the STEP 03 rule:
- a bridge may be removed only after its production ownership has moved;
- replacement behavior must be characterized and test-protected;
- ProjectDocument/EditorSession authority must not change;
- UI/workflow redesign is forbidden in the retirement slice.

M8 does not perform M9 consolidation.

## Retired Bridge 1 — Media activation guard

Removed:
- `src/full_album_maker/media_feature_activation.py`
- `install_step03_media_activation_guard` import/call from `main.py`.

The old bridge wrapped `FoundationMainWindow.__init__` and scheduled another
zero-delay route activation after Media replaced its placeholder.

M7 made that workaround obsolete:
- WorkspaceRegistry is the route activation owner;
- WorkspaceStack replacement preserves the active canonical route slot;
- route state and current widget are verified together.

M8 adds a production subprocess test that boots with persisted
`media`, `album`, and `timeline` preferences and proves, after queued Qt
events settle, that:
- FoundationUiState keeps the requested route;
- WorkspaceRegistry keeps the same current route;
- WorkspaceStack current widget is the registry bundle workspace.

No extra reactivation timer is required.

## Retired Bridge 2 — Album restore fix wrapper

Removed:
- `src/full_album_maker/album_restore_fix.py`
- `install_step04_album_restore_fix` import/call from `main.py`.

The bridge previously had two responsibilities.

### A. Legacy active-audio compatibility invariant

This real behavior is now owned directly by
`src/full_album_maker/album_feature.py`.

The owner now provides `_mirror_legacy_active_audio()`, which mirrors into
legacy `Project._active_audio_paths` only audio locators that already exist in
legacy `project.audios`.

This preserves the legacy invariant without inventing legacy media records for
V2-only ProjectDocument assets.

Focused evidence proves a V2-only playlist audio entry is not written into the
legacy active-audio compatibility list.

### B. Route reactivation wrapper

The old bridge also wrapped `FoundationMainWindow.__init__` and queued another
route reactivation after Album setup.

That ownership is obsolete after M7 WorkspaceRegistry and is removed rather
than re-created.

During retirement testing, a hidden dependency was found:
`_restore_document()` still called the old injected method name
`self._capture_document()`.

M8 corrected the real owner to call the canonical installed owner method
`self._s04_capture_document()` directly. This is exactly the kind of hidden
bridge dependency M8 is intended to expose and remove.

## Retired Bridge 3 — Timeline route fix wrapper

Removed:
- `src/full_album_maker/timeline_route_fix.py`
- `install_step05_timeline_route_fix` import/call from `main.py`.

The old module globally monkey-patched:
- `TimelinePrecisionPanel.__init__`;
- `Window._s05_route`.

Its proven presentation behavior is now local to the Timeline owner:
- production Timeline setup assigns the same `↔ Ripple` and `⌁ Snap`
  labels;
- when leaving Timeline, the owner restores the same Foundation placeholder
  mode and Split/Ripple/Snap/Marker visibility behavior.

This removes a second global wrapper around the route callback while preserving
the tested UI behavior.

## Production Installer Reduction

`main.py` no longer imports or calls the three retired installers.

Removed production installer calls:
- `install_step03_media_activation_guard()`
- `install_step04_album_restore_fix()`
- `install_step05_timeline_route_fix()`

The underlying modules are physically removed from the repository tree.

## Bridges intentionally retained

M8 is evidence-driven and does not delete every file with a historical
"fix/completion" name.

The following are explicitly retained because they still own real, unreplaced
production behavior:
- `media_layout_fix.py`
  - Media geometry, responsive columns, and early bootstrap safety.
- `timeline_completion_step05.py`
  - marker edit/delete UI, keyboard navigation, preview aspect behavior.
- `visual_timeline_completion_step06.py`
  - transition badges on the Visual alignment canvas.
- `integration_completion_step11.py`
  - selection/playhead integration, autosave quiesce, close-time worker cleanup.
- `render_queue_presentation_step10.py`
  - approved Render Center presentation behavior.

Deleting those would violate D03-15 because their ownership has not yet been
replaced and independently proven.

## Frozen contracts preserved

M8 does not change:
- ProjectDocument schema v2;
- TIMEBASE=240000;
- EditorController/EditorSession authority;
- all nine workspace routes/order;
- WorkspaceRegistry ownership;
- M2 TaskSupervisor ownership;
- M3 ProjectPersistence;
- M4 RenderEngine;
- M5 MediaProbeService / PreviewEngine / CacheManager;
- M6 BeatAnalysisService;
- current Step08 -> V13 -> S11 -> FFmpegV2 compiler semantics;
- FFmpeg/ffprobe infrastructure;
- UI design/tokens/mental model;
- dependencies, packaging, version, or release publication.

## Rollback

M8 is branch-isolated.

Rollback target:
- M7 PASS head: `398183204a6bef776f363472ac7834c797365c75`.

No schema/data migration is introduced.

## Gate

M8 is PASS only after:
1. retired modules are absent from the source tree and `main.py`;
2. their required behavior exists in the current production owner;
3. persisted non-Home startup routes stay coherent without activation wrappers;
4. Album legacy active-audio compatibility remains valid;
5. Timeline route-fix presentation behavior remains valid;
6. M0–M8 contracts pass;
7. all nine route functional UI tests pass;
8. production navigation/persistence/render/preview regressions pass;
9. responsive/lifecycle regressions pass;
10. 200-song/~3-hour structural stress passes;
11. real FFmpeg render/Spectrum/BeatAnalysis parity remains green;
12. bridges still owning unreplaced behavior remain present;
13. no M9 consolidation/UI/schema/release work is mixed in.

## Validation Evidence

Validated candidate head:
- branch: `impl-m8-legacy-bridge-retirement`
- retirement commit:
  `4ab91eaf9928f60c91a518f7bd9fd99a382eb8af`
- test-fixture correction:
  `6e2d625c35ef79bba2aa08a7c695eb6e852a8042`
- hidden Album dependency correction:
  `006d64eff4a0793162cb759a8cd77476a1a9c704`
- GitHub Actions run: `37598817830`

Main `m8-legacy-bridge-retirement` job: **SUCCESS**
- Q0 compile: PASS
- M0–M8 contracts: **68 passed, 4 skipped**
- retired bridge behavior parity: **8 passed**
- nine-route functional UI: **42 passed**
- production navigation/persistence/render/preview: **25 passed, 2 skipped**
- responsive/lifecycle regressions: **28 passed**
- 200-song/~3-hour structural stress: **2 passed**

Targeted `real-ffmpeg-m8`: **SUCCESS**
- **3 passed**
- real final-render / Accurate Preview parity remains green;
- real Spectrum Accurate Preview compiler parity remains green;
- real BeatAnalysis still detects derived pulse evidence without mutating master
  audio.

The following documentation-only final commit must keep the same M8 workflow
green before handoff is complete.

## Next

M8 is PASS. The next allowed migration phase is **M9 — Consolidation**.

M9 is not started in this turn.
