"""Machine-readable feature parity registry for the V2 migration.

M0/T1 is intentionally additive.  This module does not wire itself into the
application runtime and does not replace any existing implementation.  It
records the user-facing behavior families that must remain protected while
the V2 architecture is introduced behind facades/adapters.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Iterable


class FeatureStatus(str, Enum):
    MUST_KEEP = "MUST_KEEP"


@dataclass(frozen=True, slots=True)
class TestEvidence:
    file: str
    tests: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FeatureParityEntry:
    feature_id: str
    area: str
    feature: str
    status: FeatureStatus
    contracts: tuple[str, ...]
    evidence: tuple[TestEvidence, ...]
    workflow_evidence: tuple[str, ...] = ()
    note: str = ""


class RegistryValidationError(ValueError):
    """Raised when a parity registry violates its structural contract."""


CONTRACT_IDS = frozenset(f"C-{index:02d}" for index in range(1, 21))

REQUIRED_AREAS = (
    "home",
    "media",
    "album",
    "timeline",
    "visual",
    "template",
    "spectrum",
    "ai",
    "render",
    "portable",
    "offline",
)


def _ev(file: str, *tests: str) -> TestEvidence:
    return TestEvidence(file=file, tests=tuple(tests))


FEATURE_PARITY_ENTRIES: tuple[FeatureParityEntry, ...] = (
    # Home
    FeatureParityEntry(
        "FP-HOME-01", "home", "New/Open Project", FeatureStatus.MUST_KEEP,
        ("C-02", "C-04"),
        (_ev("tests/test_step02_home_ui.py",
             "test_home_workspace_create_and_open_signals_are_real_controls"),),
    ),
    FeatureParityEntry(
        "FP-HOME-02", "home", "Recent Projects / quick start", FeatureStatus.MUST_KEEP,
        ("C-02",),
        (_ev("tests/test_step02_home_ui.py",
             "test_home_workspace_renders_recovery_four_recent_and_quick_start"),),
    ),
    FeatureParityEntry(
        "FP-HOME-03", "home", "Recovery discovery and preserved recovery candidate",
        FeatureStatus.MUST_KEEP, ("C-16", "C-17", "C-18"),
        (_ev("tests/test_step02_home_ui.py",
             "test_home_error_state_is_visible_and_recovery_candidate_is_preserved"),),
    ),
    FeatureParityEntry(
        "FP-HOME-04", "home", "Capability/status surface", FeatureStatus.MUST_KEEP,
        ("C-02", "C-19"),
        (_ev("tests/test_step02_home_ui.py",
             "test_capability_warning_does_not_destroy_recovery_or_error_primary_state"),),
    ),

    # Media
    FeatureParityEntry(
        "FP-MEDIA-01", "media", "Batch audio/video/image import", FeatureStatus.MUST_KEEP,
        ("C-04", "C-06"),
        (_ev("tests/test_async_import.py",
             "test_video_probe_runs_off_ui_thread_and_commits_after_completion",
             "test_audio_import_probes_metadata_in_worker",
             "test_image_import_keeps_dimensions_and_visual_order"),),
    ),
    FeatureParityEntry(
        "FP-MEDIA-02", "media", "Folder scan / cancel / Unicode handling",
        FeatureStatus.MUST_KEEP, ("C-03", "C-06"),
        (_ev("tests/test_step03_media_services.py",
             "test_folder_scan_supported_unicode_hidden_and_cancel"),),
    ),
    FeatureParityEntry(
        "FP-MEDIA-03", "media", "Metadata probe and preview cache invalidation",
        FeatureStatus.MUST_KEEP, ("C-06", "C-09"),
        (
            _ev("tests/test_async_import.py",
                "test_video_probe_runs_off_ui_thread_and_commits_after_completion"),
            _ev("tests/test_step03_preview_cache_final.py",
                "test_photo_preview_cache_hit_and_source_change_invalidate_identity"),
        ),
    ),
    FeatureParityEntry(
        "FP-MEDIA-04", "media", "Missing-media visibility and relink identity",
        FeatureStatus.MUST_KEEP, ("C-06", "C-18"),
        (
            _ev("tests/test_step03_media_ui.py",
                "test_missing_asset_stays_visible_and_relink_enabled"),
            _ev("tests/test_step06_visual_assignment.py",
                "test_relink_preserves_asset_identity_and_is_undoable"),
        ),
    ),
    FeatureParityEntry(
        "FP-MEDIA-05", "media", "Library metadata sidecar remains non-destructive",
        FeatureStatus.MUST_KEEP, ("C-18",),
        (_ev("tests/test_step03_media_services.py",
             "test_sidecar_roundtrip_does_not_modify_source_media"),),
    ),
    FeatureParityEntry(
        "FP-MEDIA-06", "media", "Duplicate/pending import protection",
        FeatureStatus.MUST_KEEP, ("C-06",),
        (_ev("tests/test_async_import.py",
             "test_pending_duplicate_is_not_started_twice"),),
    ),

    # Album
    FeatureParityEntry(
        "FP-ALBUM-01", "album", "Playlist add/remove with stable song identity",
        FeatureStatus.MUST_KEEP, ("C-04", "C-05", "C-06"),
        (_ev("tests/test_editor_v2_playlist.py",
             "test_same_audio_asset_can_appear_twice_with_unique_song_ids",
             "test_remove_song_does_not_remove_media_and_undo_restores_instance"),),
    ),
    FeatureParityEntry(
        "FP-ALBUM-02", "album", "Playlist reorder is ID-based and undoable",
        FeatureStatus.MUST_KEEP, ("C-05", "C-06"),
        (_ev("tests/test_editor_v2_playlist.py",
             "test_move_song_is_id_based_and_undo_restores_order"),),
    ),
    FeatureParityEntry(
        "FP-ALBUM-03", "album", "Cover assignment / safe auto-match",
        FeatureStatus.MUST_KEEP, ("C-06",),
        (_ev("tests/test_step04_album_model.py",
             "test_safe_cover_match_never_guesses_ambiguous_candidates"),),
    ),
    FeatureParityEntry(
        "FP-ALBUM-04", "album", "Bulk cover/visual/transition is one Undo transaction",
        FeatureStatus.MUST_KEEP, ("C-05",),
        (_ev("tests/test_step04_album_model.py",
             "test_bulk_cover_visual_and_transition_are_one_undoable_transaction"),),
    ),
    FeatureParityEntry(
        "FP-ALBUM-05", "album", "Auto arrange is idempotent / does not duplicate owned layers",
        FeatureStatus.MUST_KEEP, ("C-05",),
        (
            _ev("tests/test_step04_album_acceptance.py",
                "test_auto_arrange_twice_reuses_owned_layers_without_duplicates"),
            _ev("tests/test_editor_v2_playlist.py",
                "test_auto_arrange_is_idempotent_and_preserves_manual_absolute_layer"),
        ),
    ),
    FeatureParityEntry(
        "FP-ALBUM-06", "album", "Album visuals remain renderable and previewable",
        FeatureStatus.MUST_KEEP, ("C-09",),
        (_ev("tests/test_editor_v2_s06_album_visuals.py",
             "test_real_ffmpeg_s06_visual_album_and_accurate_preview"),),
    ),

    # Timeline
    FeatureParityEntry(
        "FP-TIMELINE-01", "timeline", "Packed timeline remains contiguous",
        FeatureStatus.MUST_KEEP, ("C-07",),
        (
            _ev("tests/test_editor_v2_s11_free_timeline.py",
                "test_packed_resolver_remains_contiguous"),
            _ev("tests/test_step05_timeline_audio.py",
                "test_split_song_packed_stays_contiguous"),
        ),
    ),
    FeatureParityEntry(
        "FP-TIMELINE-02", "timeline", "Free timeline gaps are explicit silence",
        FeatureStatus.MUST_KEEP, ("C-08", "C-09"),
        (_ev("tests/test_editor_v2_s11_free_timeline.py",
             "test_free_gap_is_valid_and_extends_album_duration",
             "test_real_ffmpeg_free_gap_contains_actual_silence"),),
    ),
    FeatureParityEntry(
        "FP-TIMELINE-03", "timeline", "Overlap requires exact valid crossfade",
        FeatureStatus.MUST_KEEP, ("C-08",),
        (_ev("tests/test_editor_v2_s11_free_timeline.py",
             "test_overlap_without_crossfade_is_rejected",
             "test_crossfade_must_exactly_match_overlap",
             "test_valid_crossfade_resolves_and_is_persisted"),),
    ),
    FeatureParityEntry(
        "FP-TIMELINE-04", "timeline", "Ripple/snap/edit operations stay transactional",
        FeatureStatus.MUST_KEEP, ("C-05", "C-08"),
        (
            _ev("tests/test_step05_timeline_precision.py",
                "test_ripple_move_moves_selected_and_downstream_as_one_transaction"),
            _ev("tests/test_editor_v2_interaction.py",
                "test_snap_uses_playlist_and_layer_boundaries"),
        ),
    ),
    FeatureParityEntry(
        "FP-TIMELINE-05", "timeline", "Markers and song gain/fade mix persist and undo",
        FeatureStatus.MUST_KEEP, ("C-05", "C-07", "C-08"),
        (_ev("tests/test_step05_timeline_precision.py",
             "test_marker_persists_and_undoes",
             "test_song_mix_is_persisted_and_atomic_undo"),),
    ),
    FeatureParityEntry(
        "FP-TIMELINE-06", "timeline", "Global Undo/Redo remains cross-workspace",
        FeatureStatus.MUST_KEEP, ("C-05",),
        (_ev("tests/test_step11_e2e.py",
             "test_full_cross_workspace_edit_undo_redo_save_reopen_and_render_snapshot"),),
    ),
    FeatureParityEntry(
        "FP-TIMELINE-07", "timeline", "Auto Susun keeps manual absolute layers",
        FeatureStatus.MUST_KEEP, ("C-05", "C-07"),
        (_ev("tests/test_editor_v2_playlist.py",
             "test_auto_arrange_is_idempotent_and_preserves_manual_absolute_layer"),),
    ),

    # Visual
    FeatureParityEntry(
        "FP-VISUAL-01", "visual", "Per-song image/video visual assignment",
        FeatureStatus.MUST_KEEP, ("C-05", "C-06"),
        (
            _ev("tests/test_editor_v2_v13_song_visuals.py",
                "test_bulk_song_visual_assignment_is_one_revision_and_one_undo"),
            _ev("tests/test_visual_feature.py",
                "test_photo_only_per_song_builds_exact_audio_length"),
        ),
    ),
    FeatureParityEntry(
        "FP-VISUAL-02", "visual", "Crop/fit/position/scale/motion render semantics",
        FeatureStatus.MUST_KEEP, ("C-09",),
        (_ev("tests/test_step06_visual_precision.py",
             "test_renderer_consumes_per_song_crop_scale_motion_freeze_and_transition"),),
    ),
    FeatureParityEntry(
        "FP-VISUAL-03", "visual", "Video loop/freeze/speed remain visual-only",
        FeatureStatus.MUST_KEEP, ("C-07", "C-08", "C-09"),
        (
            _ev("tests/test_editor_v2_v13_song_visuals.py",
                "test_real_ffmpeg_video_visual_loop_and_freeze_compile"),
            _ev("tests/test_step09_slowmo_contract.py",
                "test_slowmo_is_visual_only_persisted_and_one_undo",
                "test_renderer_applies_video_setpts_but_keeps_audio_plan_timing"),
        ),
    ),
    FeatureParityEntry(
        "FP-VISUAL-04", "visual", "Existing song transitions remain compiler-backed",
        FeatureStatus.MUST_KEEP, ("C-09",),
        (_ev("tests/test_editor_v2_v13_song_visuals.py",
             "test_v13_compiler_keeps_existing_graph_and_adds_transition_filters"),),
    ),
    FeatureParityEntry(
        "FP-VISUAL-05", "visual", "Accurate Preview matches final song-visual composition",
        FeatureStatus.MUST_KEEP, ("C-09",),
        (_ev("tests/test_editor_v2_v13_song_visuals.py",
             "test_real_ffmpeg_song_images_switch_and_accurate_preview_matches"),),
    ),

    # Template
    FeatureParityEntry(
        "FP-TEMPLATE-01", "template", "Built-in/legacy template catalog remains available",
        FeatureStatus.MUST_KEEP, ("C-02", "C-18"),
        (
            _ev("tests/test_step07_template_model.py",
                "test_builtin_presentation_wraps_without_renaming_recovered_engine_ids"),
            _ev("tests/test_editor_v2_s10_presets_templates.py",
                "test_s10_has_exactly_ten_public_templates_and_required_spectrum_presets"),
        ),
    ),
    FeatureParityEntry(
        "FP-TEMPLATE-02", "template", "Custom template capture/export/import roundtrip",
        FeatureStatus.MUST_KEEP, ("C-18",),
        (_ev("tests/test_editor_v2_s08_custom_templates.py",
             "test_store_roundtrip_export_import_collision_and_corrupt_scan"),),
    ),
    FeatureParityEntry(
        "FP-TEMPLATE-03", "template", "Template apply scopes are atomic and undoable",
        FeatureStatus.MUST_KEEP, ("C-05",),
        (_ev("tests/test_step07_template_model.py",
             "test_selected_scope_preserves_order_and_supports_one_undo_redo_transaction",
             "test_all_scope_targets_every_song_without_reorder_or_partial_apply"),),
    ),
    FeatureParityEntry(
        "FP-TEMPLATE-04", "template", "Template thumbnails/cache stay real and non-destructive",
        FeatureStatus.MUST_KEEP, ("C-02", "C-09"),
        (
            _ev("tests/test_step07_template_thumbnail_cache.py",
                "test_fast_renderer_does_not_deadlock_and_cache_hit_is_reused"),
            _ev("tests/test_editor_v2_s10_presets_templates.py",
                "test_every_template_thumbnail_is_real_compiler_render_and_source_is_unchanged"),
        ),
    ),

    # Spectrum
    FeatureParityEntry(
        "FP-SPECTRUM-01", "spectrum", "Bars/line/waveform/stereo/circular styles remain real",
        FeatureStatus.MUST_KEEP, ("C-09",),
        (
            _ev("tests/test_step08_spectrum_ui.py",
                "test_context_exposes_layer_stack_and_all_nine_golden_presets"),
            _ev("tests/test_editor_v2_v12_circular_spectrum.py",
                "test_circular_registry_preset_and_property_validation"),
        ),
    ),
    FeatureParityEntry(
        "FP-SPECTRUM-02", "spectrum", "Spectrum presets/properties remain undoable and bounded",
        FeatureStatus.MUST_KEEP, ("C-05", "C-09"),
        (_ev("tests/test_step08_spectrum_model.py",
             "test_type_switch_is_one_undo_and_preserves_center_and_common_fields",
             "test_classic_preset_is_real_bundle_and_unsupported_mockup_presets_fail_closed"),),
    ),
    FeatureParityEntry(
        "FP-SPECTRUM-03", "spectrum", "Accurate circular preview/final parity",
        FeatureStatus.MUST_KEEP, ("C-09",),
        (_ev("tests/test_editor_v2_v12_circular_spectrum.py",
             "test_real_ffmpeg_circular_render_and_accurate_preview_parity"),),
    ),
    FeatureParityEntry(
        "FP-SPECTRUM-04", "spectrum", "Spectrum render remains audio-reactive",
        FeatureStatus.MUST_KEEP, ("C-09",),
        (_ev("tests/test_step08_spectrum_render.py",
             "test_circular_renderer_consumes_band_count_smoothing_thickness_reactive_and_color",
             "test_band_count_and_thickness_change_real_filter_geometry"),),
    ),
    FeatureParityEntry(
        "FP-SPECTRUM-05", "spectrum", "Complex Spectrum state persists without schema migration",
        FeatureStatus.MUST_KEEP, ("C-18",),
        (_ev("tests/test_step08_spectrum_persistence.py",
             "test_complex_spectrum_state_round_trips_without_schema_migration"),),
    ),

    # AI Agent
    FeatureParityEntry(
        "FP-AI-01", "ai", "Send -> Preview Diff -> Execute -> Undo AI flow",
        FeatureStatus.MUST_KEEP, ("C-05", "C-10"),
        (_ev("tests/test_step09_session_flow.py",
             "test_complete_flow_preview_then_execute_is_one_revision_and_undo_ai"),),
    ),
    FeatureParityEntry(
        "FP-AI-02", "ai", "Ambiguity/stale/mismatch fail closed with zero mutation",
        FeatureStatus.MUST_KEEP, ("C-10",),
        (
            _ev("tests/test_step09_session_flow.py",
                "test_manual_edit_after_preview_makes_execute_fail_stale_without_ai_mutation",
                "test_provider_plan_metadata_mismatch_fails_before_preview"),
            _ev("tests/test_step09_agent_core.py",
                "test_stale_revision_and_context_fingerprint_fail_closed"),
        ),
    ),
    FeatureParityEntry(
        "FP-AI-03", "ai", "AI execution is one revision/Undo and idempotent",
        FeatureStatus.MUST_KEEP, ("C-05", "C-10"),
        (_ev("tests/test_step09_agent_core.py",
             "test_execute_multi_action_is_one_revision_one_undo_and_idempotent"),),
    ),
    FeatureParityEntry(
        "FP-AI-04", "ai", "AI context stays bounded/path-free/key-free",
        FeatureStatus.MUST_KEEP, ("C-11",),
        (
            _ev("tests/test_step09_agent_core.py",
                "test_context_is_bounded_path_free_and_permission_scoped"),
            _ev("tests/test_step09_provider.py",
                "test_gemini_adapter_builds_plan_without_sending_paths_or_keys"),
        ),
    ),
    FeatureParityEntry(
        "FP-AI-05", "ai", "Gemini key pool supports 100 keys with safe failover/quarantine",
        FeatureStatus.MUST_KEEP, ("C-20",),
        (
            _ev("tests/test_key_pool.py", "test_pool_caps_at_100"),
            _ev("tests/test_key_pool_hardening.py",
                "test_invalid_key_400_disables_and_rotates_to_next_key",
                "test_corrupt_vault_is_quarantined_instead_of_silently_erased",
                "test_parallel_requests_reserve_different_ready_keys"),
        ),
    ),

    # Render
    FeatureParityEntry(
        "FP-RENDER-01", "render", "Immutable render snapshot + critical preflight",
        FeatureStatus.MUST_KEEP, ("C-12", "C-13"),
        (
            _ev("tests/test_step10_render_model.py",
                "test_render_snapshot_is_canonical_immutable_and_separate_from_live_edit"),
            _ev("tests/test_step10_render_executor.py",
                "test_ready_job_reenters_critical_preflight_before_start"),
        ),
    ),
    FeatureParityEntry(
        "FP-RENDER-02", "render", "Persistent queue / retry / interrupted-attempt semantics",
        FeatureStatus.MUST_KEEP, ("C-12", "C-13"),
        (_ev("tests/test_step10_render_queue.py",
             "test_restart_marks_active_attempt_interrupted_and_cleans_bound_stage",
             "test_retry_creates_new_attempt_in_draft_and_cannot_queue_without_new_preflight"),),
    ),
    FeatureParityEntry(
        "FP-RENDER-03", "render", "Progress/cancel never publishes partial final output",
        FeatureStatus.MUST_KEEP, ("C-14", "C-15"),
        (
            _ev("tests/test_step10_render_executor.py",
                "test_cancel_never_publishes_final_and_sets_cancelled"),
            _ev("tests/test_render_lifecycle.py",
                "test_cancel_terminates_running_subprocess"),
        ),
    ),
    FeatureParityEntry(
        "FP-RENDER-04", "render", "Hardware encoder runtime probe + software fallback",
        FeatureStatus.MUST_KEEP, ("C-13",),
        (_ev("tests/test_step10_render_preflight.py",
             "test_auto_uses_verified_hardware_else_explicit_software_fallback"),),
    ),
    FeatureParityEntry(
        "FP-RENDER-05", "render", "ffprobe verification precedes final publication",
        FeatureStatus.MUST_KEEP, ("C-14", "C-15"),
        (
            _ev("tests/test_step10_render_executor.py",
                "test_verified_executor_publishes_only_after_verifier",
                "test_ffprobe_verifier_rejects_corrupt_and_accepts_expected_streams"),
            _ev("tests/test_step10_render_real_ffmpeg.py",
                "test_real_ffmpeg_renders_then_ffprobe_verifies_before_final_publish"),
        ),
    ),
    FeatureParityEntry(
        "FP-RENDER-06", "render", "Video + sidecars publish transactionally and recover",
        FeatureStatus.MUST_KEEP, ("C-14", "C-15"),
        (_ev("tests/test_atomic_render_bundle.py",
             "test_transactional_publish_replaces_complete_bundle",
             "test_publish_failure_restores_every_previous_file",
             "test_sidecar_staging_failure_does_not_publish_new_video"),),
    ),

    # Windows portable / manual offline
    FeatureParityEntry(
        "FP-PORTABLE-01", "portable", "Windows portable ZIP remains the distribution target",
        FeatureStatus.MUST_KEEP, ("C-19",),
        (_ev("tests/test_release_candidate_audit.py",
             "test_local_portable_build_uses_canonical_release_manifest_contract"),),
        workflow_evidence=(
            ".github/workflows/build-windows-portable.yml",
            ".github/workflows/step12-release-validation.yml",
        ),
    ),
    FeatureParityEntry(
        "FP-PORTABLE-02", "portable", "Release identity/checksum/pins remain explicit",
        FeatureStatus.MUST_KEEP, ("C-19",),
        (_ev("tests/test_stable_release_v1.py",
             "test_stable_version_is_consistent_across_package_metadata",
             "test_capability_report_records_release_identity_and_manifest_pins",
             "test_build_workflow_validates_only_and_cannot_auto_publish_stable"),),
        workflow_evidence=(".github/workflows/build-windows-portable.yml",),
    ),
    FeatureParityEntry(
        "FP-OFFLINE-01", "offline", "Manual editing/rendering remains first-class without AI",
        FeatureStatus.MUST_KEEP, ("C-03", "C-04", "C-12", "C-15"),
        (
            _ev("tests/test_step11_e2e.py",
                "test_full_cross_workspace_edit_undo_redo_save_reopen_and_render_snapshot"),
            _ev("tests/test_step10_render_real_ffmpeg.py",
                "test_real_ffmpeg_renders_then_ffprobe_verifies_before_final_publish"),
        ),
    ),
)


_FEATURE_ID_RE = re.compile(r"^FP-[A-Z]+-[0-9]{2}$")


class FeatureParityRegistry:
    """Read-only registry with structural validation helpers."""

    def __init__(self, entries: Iterable[FeatureParityEntry] = FEATURE_PARITY_ENTRIES):
        self._entries = tuple(entries)
        self._by_id = {entry.feature_id: entry for entry in self._entries}

    def all(self) -> tuple[FeatureParityEntry, ...]:
        return self._entries

    def get(self, feature_id: str) -> FeatureParityEntry:
        return self._by_id[feature_id]

    def by_area(self, area: str) -> tuple[FeatureParityEntry, ...]:
        return tuple(entry for entry in self._entries if entry.area == area)

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []
        ids = [entry.feature_id for entry in self._entries]

        if not self._entries:
            errors.append("registry is empty")
        if len(ids) != len(set(ids)):
            errors.append("feature_id values must be unique")

        seen_areas = {entry.area for entry in self._entries}
        missing_areas = set(REQUIRED_AREAS) - seen_areas
        if missing_areas:
            errors.append(
                "required areas missing: " + ", ".join(sorted(missing_areas))
            )

        for entry in self._entries:
            prefix = f"{entry.feature_id}: "
            if not _FEATURE_ID_RE.fullmatch(entry.feature_id):
                errors.append(prefix + "invalid feature_id format")
            if entry.status is not FeatureStatus.MUST_KEEP:
                errors.append(prefix + "M0/T1 registry only accepts MUST_KEEP")
            if not entry.feature.strip():
                errors.append(prefix + "feature name is blank")
            if not entry.contracts:
                errors.append(prefix + "at least one behavior contract is required")
            invalid_contracts = set(entry.contracts) - CONTRACT_IDS
            if invalid_contracts:
                errors.append(
                    prefix + "unknown contracts: " + ", ".join(sorted(invalid_contracts))
                )
            if not entry.evidence:
                errors.append(prefix + "at least one test evidence reference is required")
            for evidence in entry.evidence:
                if not evidence.file.startswith("tests/") or not evidence.file.endswith(".py"):
                    errors.append(prefix + f"invalid test file: {evidence.file}")
                if not evidence.tests:
                    errors.append(prefix + f"no test functions listed for {evidence.file}")
                for test_name in evidence.tests:
                    if not test_name.startswith("test_"):
                        errors.append(prefix + f"invalid test function: {test_name}")
            for workflow in entry.workflow_evidence:
                if not workflow.startswith(".github/workflows/"):
                    errors.append(prefix + f"invalid workflow evidence: {workflow}")

        return tuple(errors)

    def assert_valid(self) -> None:
        errors = self.validate()
        if errors:
            raise RegistryValidationError("\n".join(errors))


DEFAULT_FEATURE_PARITY_REGISTRY = FeatureParityRegistry()
DEFAULT_FEATURE_PARITY_REGISTRY.assert_valid()


__all__ = [
    "CONTRACT_IDS",
    "DEFAULT_FEATURE_PARITY_REGISTRY",
    "FEATURE_PARITY_ENTRIES",
    "FeatureParityEntry",
    "FeatureParityRegistry",
    "FeatureStatus",
    "REQUIRED_AREAS",
    "RegistryValidationError",
    "TestEvidence",
]
