from __future__ import annotations

import os
import subprocess
import sys
import textwrap


def _run(script: str, *, timeout: int = 60) -> str:
    env = dict(os.environ)
    env["QT_QPA_PLATFORM"] = "offscreen"
    env["FAM_STEP11_NO_RECOVERY_PROMPT"] = "1"
    env["FAM_DISABLE_TEMPLATE_THUMBNAIL_RENDER"] = "1"
    env["FAM_STEP09_PROVIDER"] = "mock"
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(script)],
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
    return result.stdout


def test_discard_waits_for_inflight_autosave_then_clears_recovery() -> None:
    output = _run(
        r"""
        import os
        import tempfile
        import time
        from pathlib import Path

        from PySide6.QtWidgets import QApplication, QMessageBox
        import full_album_maker.main
        import full_album_maker.integration_feature_step11 as feature
        from full_album_maker.v14_window import create_main_window

        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory(prefix="s11-discard-race-") as folder:
            root = Path(folder)
            feature.data_dir = lambda: root

            persistence = feature.DEFAULT_PROJECT_PERSISTENCE
            original_write = persistence.write_recovery

            def delayed_write(path, request):
                time.sleep(0.25)
                return original_write(path, request)

            persistence.write_recovery = delayed_write
            window = create_main_window()
            window._foundation_project_open = True
            canonical = root / "discard-project.json"
            window._foundation_project_path = str(canonical)

            window.editor_workspace.session.add_text_layer("discard-race")
            window.editor_workspace._after_edit()
            app.processEvents()
            assert window.editor_workspace.session.is_dirty is True

            token = window._s11_project_token
            session_id = window._s11_recovery_session.session_id
            recovery_path = feature._recovery_path(token, session_id)

            window._s11_autosave_timer.stop()
            window._s11_schedule_autosave_flush()
            QMessageBox.question = lambda *a, **k: QMessageBox.StandardButton.Discard

            started = time.monotonic()
            assert window.close() is True
            elapsed = time.monotonic() - started
            app.processEvents()

            assert elapsed >= 0.18
            assert not recovery_path.exists()
            assert window._s11_autosave_runtime["closed"] is True
            assert window._s11_autosave_runtime["executor"] is None
            assert not window._s11_recovery_session.path.exists()
            print("DISCARD_RACE_OK", flush=True)
        """
    )
    assert "DISCARD_RACE_OK" in output


def test_project_switch_flushes_old_pending_recovery_and_ignores_old_callback() -> None:
    output = _run(
        r"""
        import tempfile
        from pathlib import Path

        from PySide6.QtWidgets import QApplication
        import full_album_maker.main
        import full_album_maker.integration_feature_step11 as feature
        from full_album_maker.editor_models import ProjectDocument
        from full_album_maker.v14_window import create_main_window

        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory(prefix="s11-switch-race-") as folder:
            root = Path(folder)
            feature.data_dir = lambda: root

            window = create_main_window()
            window._foundation_project_open = True
            first_path = root / "first.json"
            window._foundation_project_path = str(first_path)

            window.editor_workspace.session.add_text_layer("pending-first")
            window.editor_workspace._after_edit()
            app.processEvents()
            assert window._s11_autosave.status.pending is True

            first_token = window._s11_project_token
            session_id = window._s11_recovery_session.session_id
            first_recovery = feature._recovery_path(first_token, session_id)

            second_path = root / "second.json"
            second = ProjectDocument.new_empty("Second Project")
            window._foundation_project_path = str(second_path)
            window.editor_workspace.set_document(second, current_path=str(second_path))
            app.processEvents()

            assert window._s11_project_token != first_token
            assert first_recovery.is_file()
            assert window._s11_autosave.status.last_success_revision == 0
            assert window._s11_autosave.status.latest_revision == 0
            assert window.editor_workspace.session.is_dirty is False

            window._s11_quiesce_autosave(restart=False)
            window._s11_recovery_session.close()
            window.hide()
            window.deleteLater()
            app.processEvents()
            print("SWITCH_RACE_OK", flush=True)
        """
    )
    assert "SWITCH_RACE_OK" in output


def test_destroy_waits_worker_suppresses_callback_and_releases_session_lease() -> None:
    output = _run(
        r"""
        import tempfile
        import time
        from pathlib import Path

        from PySide6.QtCore import QCoreApplication, QEvent
        from PySide6.QtWidgets import QApplication
        import full_album_maker.main
        import full_album_maker.integration_feature_step11 as feature
        from full_album_maker.v14_window import create_main_window

        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory(prefix="s11-destroy-race-") as folder:
            root = Path(folder)
            feature.data_dir = lambda: root

            persistence = feature.DEFAULT_PROJECT_PERSISTENCE
            original_write = persistence.write_recovery

            def delayed_write(path, request):
                time.sleep(0.20)
                return original_write(path, request)

            persistence.write_recovery = delayed_write
            window = create_main_window()
            window._foundation_project_open = True
            window._foundation_project_path = str(root / "destroy.json")
            window.editor_workspace.session.add_text_layer("destroy-race")
            window.editor_workspace._after_edit()
            app.processEvents()

            token = window._s11_project_token
            session_id = window._s11_recovery_session.session_id
            recovery_path = feature._recovery_path(token, session_id)
            lease_path = window._s11_recovery_session.path

            window._s11_autosave_timer.stop()
            window._s11_schedule_autosave_flush()

            started = time.monotonic()
            window.hide()
            window.deleteLater()
            QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
            app.processEvents()
            elapsed = time.monotonic() - started

            assert elapsed >= 0.13
            assert recovery_path.is_file()
            assert not lease_path.exists()
            assert window._s11_autosave_runtime["closed"] is True
            assert window._s11_autosave_runtime["executor"] is None
            print("DESTROY_RACE_OK", flush=True)
        """
    )
    assert "DESTROY_RACE_OK" in output


def test_quiesced_autosave_rejects_late_timer_submission() -> None:
    output = _run(
        r"""
        import tempfile
        from pathlib import Path

        from PySide6.QtWidgets import QApplication
        import full_album_maker.main
        import full_album_maker.integration_feature_step11 as feature
        from full_album_maker.v14_window import create_main_window

        app = QApplication.instance() or QApplication([])
        with tempfile.TemporaryDirectory(prefix="s11-late-timeout-") as folder:
            root = Path(folder)
            feature.data_dir = lambda: root

            window = create_main_window()
            window.editor_workspace.session.add_text_layer("late-timeout")
            window.editor_workspace._after_edit()
            app.processEvents()
            assert window._s11_autosave.status.pending is True

            window._s11_quiesce_autosave(restart=False)
            window._s11_schedule_autosave_flush()
            assert window._s11_autosave_runtime["closed"] is True
            assert window._s11_autosave_runtime["executor"] is None

            window._s11_recovery_session.close()
            window.hide()
            window.deleteLater()
            app.processEvents()
            print("LATE_TIMEOUT_OK", flush=True)
        """
    )
    assert "LATE_TIMEOUT_OK" in output
