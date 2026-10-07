from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import textwrap

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from full_album_maker.editor_models import MediaAsset, ProjectDocument, SongInstance, TIMEBASE
from full_album_maker.playlist_feature import get_active_audio_paths
from full_album_maker.project import AudioItem, Project


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "full_album_maker"


def test_retired_bridge_modules_are_absent_from_runtime_tree_and_main() -> None:
    retired = (
        "media_feature_activation.py",
        "album_restore_fix.py",
        "timeline_route_fix.py",
    )
    for name in retired:
        assert not (SRC / name).exists(), name

    main = (SRC / "main.py").read_text(encoding="utf-8")
    assert "media_feature_activation" not in main
    assert "install_step03_media_activation_guard" not in main
    assert "album_restore_fix" not in main
    assert "install_step04_album_restore_fix" not in main
    assert "timeline_route_fix" not in main
    assert "install_step05_timeline_route_fix" not in main


def test_album_owner_keeps_legacy_active_audio_invariant_without_restore_bridge() -> None:
    from full_album_maker.album_feature import _mirror_legacy_active_audio

    project = Project()
    legacy_path = "/tmp/legacy-song.mp3"
    v2_only_path = "/tmp/v2-only-song.mp3"
    project.audios.append(AudioItem(path=legacy_path, duration=120.0))

    document = ProjectDocument.new_empty("M8 album bridge retirement")
    for path in (legacy_path, v2_only_path):
        asset = MediaAsset(
            kind="audio",
            locator=path,
            original_name=Path(path).name,
            source_duration_tick=120 * TIMEBASE,
        )
        document.media.append(asset)
        document.playlist.entries.append(
            SongInstance(
                asset_id=asset.asset_id,
                display_title=Path(path).stem,
                source_out_tick=120 * TIMEBASE,
            )
        )
    document.validate()

    class Owner:
        pass

    owner = Owner()
    owner.project = project
    _mirror_legacy_active_audio(owner, document)

    assert get_active_audio_paths(project) == [legacy_path]


def test_production_persisted_routes_survive_without_reactivation_bridges() -> None:
    script = textwrap.dedent(
        r"""
        import os
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        os.environ.setdefault("FAM_DISABLE_TEMPLATE_THUMBNAIL_RENDER", "1")
        os.environ.setdefault("FAM_STEP09_PROVIDER", "mock")
        os.environ.setdefault("FAM_STEP11_NO_RECOVERY_PROMPT", "1")

        from PySide6.QtWidgets import QApplication
        import full_album_maker.main
        from full_album_maker.foundation_preferences import FoundationPreferences, FoundationPreferenceStore
        from full_album_maker.foundation_window import FoundationMainWindow

        app = QApplication.instance() or QApplication([])
        original_load = FoundationPreferenceStore.load
        try:
            for requested in ("media", "album", "timeline"):
                FoundationPreferenceStore.load = lambda self, route=requested: FoundationPreferences(
                    workspace=route,
                    width=1600,
                    height=900,
                )
                window = FoundationMainWindow()
                app.processEvents()
                app.processEvents()
                app.processEvents()

                registry = window.foundation_shell.workspace_registry
                assert window.foundation_state.workspace == requested, (
                    requested,
                    window.foundation_state.workspace,
                )
                assert registry.current_route == requested
                assert window.foundation_shell.workspace_stack.currentWidget() is registry.bundle(requested).workspace

                shutdown = getattr(window, "_s11_shutdown", None)
                if callable(shutdown):
                    shutdown()
                window.hide()
                window.deleteLater()
                app.processEvents()
        finally:
            FoundationPreferenceStore.load = original_load
        """
    )
    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["FAM_DISABLE_TEMPLATE_THUMBNAIL_RENDER"] = "1"
    env["FAM_STEP09_PROVIDER"] = "mock"
    env["FAM_STEP11_NO_RECOVERY_PROMPT"] = "1"
    completed = subprocess.run(
        [sys.executable, "-c", script],
        env=env,
        text=True,
        capture_output=True,
        timeout=75,
    )
    assert completed.returncode == 0, completed.stdout + "\n" + completed.stderr


def test_production_timeline_keeps_route_fix_behavior_without_wrapper_module() -> None:
    script = textwrap.dedent(
        r"""
        import os
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        os.environ.setdefault("FAM_DISABLE_TEMPLATE_THUMBNAIL_RENDER", "1")
        os.environ.setdefault("FAM_STEP09_PROVIDER", "mock")
        os.environ.setdefault("FAM_STEP11_NO_RECOVERY_PROMPT", "1")

        from PySide6.QtWidgets import QApplication, QPushButton
        import full_album_maker.main
        from full_album_maker.foundation_window import FoundationMainWindow

        app = QApplication.instance() or QApplication([])
        window = FoundationMainWindow()
        app.processEvents()
        app.processEvents()

        window.foundation_shell.set_workspace("timeline")
        app.processEvents()
        assert window.timeline_precision_s05.ripple.text() == "↔ Ripple"
        assert window.timeline_precision_s05.snap.text() == "⌁ Snap"

        window.foundation_shell.set_workspace("home")
        app.processEvents()
        mode = window.foundation_shell.timeline.mode
        assert mode.isHidden() is False
        parent = window.foundation_shell.timeline.canvas.parentWidget()
        generic = {
            button.text(): button
            for button in parent.findChildren(QPushButton)
            if button.text() in {"Split", "Ripple", "Snap", "Marker"}
        }
        assert set(generic) == {"Split", "Ripple", "Snap", "Marker"}
        assert all(button.isHidden() is False for button in generic.values())

        shutdown = getattr(window, "_s11_shutdown", None)
        if callable(shutdown):
            shutdown()
        window.hide()
        window.deleteLater()
        app.processEvents()
        """
    )
    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["FAM_DISABLE_TEMPLATE_THUMBNAIL_RENDER"] = "1"
    env["FAM_STEP09_PROVIDER"] = "mock"
    env["FAM_STEP11_NO_RECOVERY_PROMPT"] = "1"
    completed = subprocess.run(
        [sys.executable, "-c", script],
        env=env,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stdout + "\n" + completed.stderr


def test_remaining_bridge_modules_are_not_falsely_retired() -> None:
    # M8 is evidence-driven. These modules still own proven behavior and must not
    # be deleted merely to reduce installer count.
    still_required = (
        "media_layout_fix.py",
        "timeline_completion_step05.py",
        "visual_timeline_completion_step06.py",
        "integration_completion_step11.py",
        "render_queue_presentation_step10.py",
    )
    for name in still_required:
        assert (SRC / name).is_file(), name
