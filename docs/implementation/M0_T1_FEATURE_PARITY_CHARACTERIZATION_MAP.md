# M0/T1 — Feature Parity Characterization Map

Status: **PASS — M0/T1 characterization implemented and validated**

This map is the human-readable companion to
`src/full_album_maker/feature_parity_registry.py`.

## Purpose

M0 freezes externally meaningful behavior before architecture ownership moves.
T1 makes that behavior machine-readable through `FeatureParityRegistry`.

Rules:
- Every entry below is **MUST KEEP**.
- Registry entries are behavior families, not promises to preserve historical module names.
- Legacy code may be retired only after equivalent or stronger evidence protects the same feature IDs.
- New V2 features may be additive, but cannot satisfy a missing baseline parity row by replacing it with something different.
- Tests listed here are characterization/regression evidence that already exists in the baseline.
- The registry itself is not imported by production startup and causes no runtime behavior change.

## Governance Boundary

**C-01 — old repository read-only** is not represented as an application feature.
It is a repository-governance boundary verified by branch/repository process.
The runtime parity registry covers the relevant behavioral contracts C-02..C-20.

## Coverage Summary

- Total MUST KEEP behavior families: **51**
- Areas: **11**
- Home: 4
- Media: 6
- Album: 6
- Timeline: 7
- Visual: 5
- Template: 4
- Spectrum: 5
- AI Agent: 5
- Render: 6
- Windows portable: 2
- Manual/offline: 1

## Home

| ID | MUST KEEP behavior | Contracts | Representative evidence |
|---|---|---|---|
| FP-HOME-01 | New/Open Project | C-02, C-04 | `test_step02_home_ui.py::test_home_workspace_create_and_open_signals_are_real_controls` |
| FP-HOME-02 | Recent Projects / quick start | C-02 | `test_step02_home_ui.py::test_home_workspace_renders_recovery_four_recent_and_quick_start` |
| FP-HOME-03 | Recovery discovery and candidate preservation | C-16, C-17, C-18 | `test_step02_home_ui.py::test_home_error_state_is_visible_and_recovery_candidate_is_preserved` |
| FP-HOME-04 | Capability/status surface | C-02, C-19 | `test_step02_home_ui.py::test_capability_warning_does_not_destroy_recovery_or_error_primary_state` |

## Media

| ID | MUST KEEP behavior | Contracts | Representative evidence |
|---|---|---|---|
| FP-MEDIA-01 | Batch audio/video/image import | C-04, C-06 | `test_async_import.py` probe/import tests |
| FP-MEDIA-02 | Folder scan / cancel / Unicode | C-03, C-06 | `test_step03_media_services.py::test_folder_scan_supported_unicode_hidden_and_cancel` |
| FP-MEDIA-03 | Metadata probe + preview cache invalidation | C-06, C-09 | `test_async_import.py`; `test_step03_preview_cache_final.py` |
| FP-MEDIA-04 | Missing media stays visible; relink preserves identity | C-06, C-18 | `test_step03_media_ui.py`; `test_step06_visual_assignment.py` |
| FP-MEDIA-05 | Library metadata sidecar non-destructive | C-18 | `test_step03_media_services.py::test_sidecar_roundtrip_does_not_modify_source_media` |
| FP-MEDIA-06 | Duplicate/pending import protection | C-06 | `test_async_import.py::test_pending_duplicate_is_not_started_twice` |

## Album

| ID | MUST KEEP behavior | Contracts | Representative evidence |
|---|---|---|---|
| FP-ALBUM-01 | Playlist add/remove with stable song identity | C-04, C-05, C-06 | `test_editor_v2_playlist.py` |
| FP-ALBUM-02 | Playlist reorder is ID-based and undoable | C-05, C-06 | `test_editor_v2_playlist.py::test_move_song_is_id_based_and_undo_restores_order` |
| FP-ALBUM-03 | Cover assignment / safe auto-match | C-06 | `test_step04_album_model.py::test_safe_cover_match_never_guesses_ambiguous_candidates` |
| FP-ALBUM-04 | Bulk cover/visual/transition = one Undo transaction | C-05 | `test_step04_album_model.py::test_bulk_cover_visual_and_transition_are_one_undoable_transaction` |
| FP-ALBUM-05 | Auto arrange idempotent / no duplicate owned layers | C-05 | `test_step04_album_acceptance.py`; `test_editor_v2_playlist.py` |
| FP-ALBUM-06 | Album visuals remain renderable/previewable | C-09 | `test_editor_v2_s06_album_visuals.py::test_real_ffmpeg_s06_visual_album_and_accurate_preview` |

## Timeline

| ID | MUST KEEP behavior | Contracts | Representative evidence |
|---|---|---|---|
| FP-TIMELINE-01 | Packed timeline contiguous | C-07 | `test_editor_v2_s11_free_timeline.py`; `test_step05_timeline_audio.py` |
| FP-TIMELINE-02 | Free gaps are explicit silence | C-08, C-09 | `test_editor_v2_s11_free_timeline.py::test_real_ffmpeg_free_gap_contains_actual_silence` |
| FP-TIMELINE-03 | Overlap requires exact valid crossfade | C-08 | overlap/crossfade tests in `test_editor_v2_s11_free_timeline.py` |
| FP-TIMELINE-04 | Ripple/snap/edit operations transactional | C-05, C-08 | `test_step05_timeline_precision.py`; `test_editor_v2_interaction.py` |
| FP-TIMELINE-05 | Markers + song gain/fade mix persist and undo | C-05, C-07, C-08 | `test_step05_timeline_precision.py` |
| FP-TIMELINE-06 | Global Undo/Redo remains cross-workspace | C-05 | `test_step11_e2e.py::test_full_cross_workspace_edit_undo_redo_save_reopen_and_render_snapshot` |
| FP-TIMELINE-07 | Auto Susun preserves manual absolute layers | C-05, C-07 | `test_editor_v2_playlist.py::test_auto_arrange_is_idempotent_and_preserves_manual_absolute_layer` |

## Visual

| ID | MUST KEEP behavior | Contracts | Representative evidence |
|---|---|---|---|
| FP-VISUAL-01 | Per-song image/video visual assignment | C-05, C-06 | `test_editor_v2_v13_song_visuals.py`; `test_visual_feature.py` |
| FP-VISUAL-02 | Crop/fit/position/scale/motion semantics | C-09 | `test_step06_visual_precision.py::test_renderer_consumes_per_song_crop_scale_motion_freeze_and_transition` |
| FP-VISUAL-03 | Loop/freeze/video-speed remain visual-only | C-07, C-08, C-09 | `test_editor_v2_v13_song_visuals.py`; `test_step09_slowmo_contract.py` |
| FP-VISUAL-04 | Existing song transitions remain compiler-backed | C-09 | `test_editor_v2_v13_song_visuals.py::test_v13_compiler_keeps_existing_graph_and_adds_transition_filters` |
| FP-VISUAL-05 | Accurate Preview matches final song visual | C-09 | `test_editor_v2_v13_song_visuals.py::test_real_ffmpeg_song_images_switch_and_accurate_preview_matches` |

## Template

| ID | MUST KEEP behavior | Contracts | Representative evidence |
|---|---|---|---|
| FP-TEMPLATE-01 | Built-in/legacy template catalog | C-02, C-18 | `test_step07_template_model.py`; `test_editor_v2_s10_presets_templates.py` |
| FP-TEMPLATE-02 | Custom capture/export/import roundtrip | C-18 | `test_editor_v2_s08_custom_templates.py::test_store_roundtrip_export_import_collision_and_corrupt_scan` |
| FP-TEMPLATE-03 | Apply scopes atomic and undoable | C-05 | selected/all scope tests in `test_step07_template_model.py` |
| FP-TEMPLATE-04 | Thumbnail/cache remains real and non-destructive | C-02, C-09 | `test_step07_template_thumbnail_cache.py`; `test_editor_v2_s10_presets_templates.py` |

## Spectrum

| ID | MUST KEEP behavior | Contracts | Representative evidence |
|---|---|---|---|
| FP-SPECTRUM-01 | Bars/line/waveform/stereo/circular styles remain real | C-09 | `test_step08_spectrum_ui.py`; `test_editor_v2_v12_circular_spectrum.py` |
| FP-SPECTRUM-02 | Presets/properties bounded + undoable | C-05, C-09 | `test_step08_spectrum_model.py` |
| FP-SPECTRUM-03 | Accurate circular preview/final parity | C-09 | `test_editor_v2_v12_circular_spectrum.py::test_real_ffmpeg_circular_render_and_accurate_preview_parity` |
| FP-SPECTRUM-04 | Spectrum render remains audio-reactive | C-09 | `test_step08_spectrum_render.py` |
| FP-SPECTRUM-05 | Complex state persists without schema migration | C-18 | `test_step08_spectrum_persistence.py::test_complex_spectrum_state_round_trips_without_schema_migration` |

## AI Agent

| ID | MUST KEEP behavior | Contracts | Representative evidence |
|---|---|---|---|
| FP-AI-01 | Send -> Preview Diff -> Execute -> Undo AI | C-05, C-10 | `test_step09_session_flow.py::test_complete_flow_preview_then_execute_is_one_revision_and_undo_ai` |
| FP-AI-02 | Ambiguity/stale/mismatch fail closed | C-10 | `test_step09_session_flow.py`; `test_step09_agent_core.py` |
| FP-AI-03 | One revision/Undo + idempotent execution | C-05, C-10 | `test_step09_agent_core.py::test_execute_multi_action_is_one_revision_one_undo_and_idempotent` |
| FP-AI-04 | Context bounded/path-free/key-free | C-11 | `test_step09_agent_core.py`; `test_step09_provider.py` |
| FP-AI-05 | 100-key pool + safe failover/quarantine | C-20 | `test_key_pool.py`; `test_key_pool_hardening.py` |

## Render

| ID | MUST KEEP behavior | Contracts | Representative evidence |
|---|---|---|---|
| FP-RENDER-01 | Immutable snapshot + critical preflight | C-12, C-13 | `test_step10_render_model.py`; `test_step10_render_executor.py` |
| FP-RENDER-02 | Persistent queue/retry/interrupted attempts | C-12, C-13 | `test_step10_render_queue.py` |
| FP-RENDER-03 | Cancel never publishes partial final | C-14, C-15 | `test_step10_render_executor.py`; `test_render_lifecycle.py` |
| FP-RENDER-04 | Hardware runtime probe + software fallback | C-13 | `test_step10_render_preflight.py::test_auto_uses_verified_hardware_else_explicit_software_fallback` |
| FP-RENDER-05 | ffprobe verification precedes publish | C-14, C-15 | `test_step10_render_executor.py`; `test_step10_render_real_ffmpeg.py` |
| FP-RENDER-06 | Video + sidecars transactional publish/recovery | C-14, C-15 | `test_atomic_render_bundle.py` |

## Windows Portable

| ID | MUST KEEP behavior | Contracts | Representative evidence |
|---|---|---|---|
| FP-PORTABLE-01 | Windows portable ZIP remains distribution target | C-19 | `test_release_candidate_audit.py` + Windows build/release workflows |
| FP-PORTABLE-02 | Release identity/checksum/pins explicit | C-19 | `test_stable_release_v1.py` + Windows build workflow |

## Manual / Offline

| ID | MUST KEEP behavior | Contracts | Representative evidence |
|---|---|---|---|
| FP-OFFLINE-01 | Manual editing/rendering remains first-class without AI | C-03, C-04, C-12, C-15 | `test_step11_e2e.py` + `test_step10_render_real_ffmpeg.py` |

## Migration Use

For every later migration slice:
1. list touched FeatureParityRegistry IDs;
2. run the tests referenced by those IDs;
3. add facade/adapter contract evidence where ownership changes;
4. do not retire the legacy owner while any touched ID lacks equivalent evidence;
5. keep this map and the machine-readable registry synchronized;
6. run the higher Q-gate required by the affected boundary.

## M0/T1 Exit Criteria

M0/T1 passes only when:
- the registry validates structurally;
- all 51 IDs are present;
- every referenced test file exists;
- every referenced test function exists in the actual baseline suite;
- every referenced workflow exists;
- C-02..C-20 relevant behavioral coverage is represented;
- C-01 remains explicitly governed outside runtime code;
- this characterization map contains every registry ID;
- no runtime startup/module wiring changes are introduced.


## Validation Evidence

Final gate basis:
- Branch: `impl-m0-t1-feature-parity`
- Candidate commit initially validated: `6e7a1749f587a494f09eab39ff5da489b5df3ac2`
- GitHub Actions run: `37583231121`
- Job: `m0-characterization`
- Q0 compile: PASS
- Registry contract tests: **6 passed**
- Q1 baseline navigation characterization smoke: **1 passed**
- Diff from pre-implementation head contained only:
  - `src/full_album_maker/feature_parity_registry.py`
  - `tests/test_v2_feature_parity_registry.py`
  - this characterization map
  - `.github/workflows/v2-m0-feature-parity.yml`
- No existing application runtime file was edited.

The status/evidence commit that records this result must rerun the same workflow on its own final head before M1 starts.
