from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import textwrap

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from full_album_maker.app_kernel import build_app_kernel
from full_album_maker.foundation_shell import FoundationShellWidget
from full_album_maker.foundation_tokens import WORKSPACE_ORDER
from full_album_maker.workspace_registry import (
    WorkspaceRegistry,
    current_workspace_registry,
)


ROOT = Path(__file__).resolve().parents[1]
ROUTES = tuple(route for route, _label, _icon in WORKSPACE_ORDER)


def _app() -> QApplication:
    return QApplication.instance() or QApplication([])


def test_registry_preserves_canonical_order_and_deterministic_listener_dispatch() -> None:
    replaced: list[tuple[str, object]] = []
    calls: list[tuple[str, str]] = []
    registry = WorkspaceRegistry(
        WORKSPACE_ORDER,
        replace_workspace=lambda route, widget: replaced.append((route, widget)) or None,
    )

    home = object()
    media = object()
    registry.register_bundle(
        "home",
        workspace=home,
        listener=lambda route: calls.append(("home", route)),
        listener_name="home-route",
    )
    registry.register_bundle(
        "media",
        workspace=media,
        listener=lambda route: calls.append(("media", route)),
        listener_name="media-route",
    )
    registry.register_listener(
        "media",
        lambda route: calls.append(("media-extra", route)),
        name="media-extra",
    )

    assert registry.routes == ROUTES
    assert registry.registered_routes == ("home", "media")
    assert replaced == [("home", home), ("media", media)]

    assert registry.activate("media") == "media"
    assert registry.current_route == "media"
    assert calls == [
        ("home", "media"),
        ("media", "media"),
        ("media-extra", "media"),
    ]

    assert registry.activate("unknown") == "home"
    assert registry.current_route == "home"


def test_registry_complete_gate_requires_all_nine_workspaces() -> None:
    registry = WorkspaceRegistry(
        WORKSPACE_ORDER,
        replace_workspace=lambda _route, _widget: None,
    )
    for route in ROUTES[:-1]:
        registry.register_bundle(route, workspace=object())

    try:
        registry.assert_complete()
    except RuntimeError as exc:
        assert "render" in str(exc)
    else:
        raise AssertionError("Incomplete registry harus gagal.")

    registry.register_bundle("render", workspace=object())
    registry.assert_complete()
    assert registry.registered_routes == ROUTES


def test_app_kernel_binds_exact_workspace_registry_into_shell() -> None:
    _app()
    registry = WorkspaceRegistry(WORKSPACE_ORDER)
    seen: dict[str, object] = {}

    def gui_runner() -> int:
        shell = FoundationShellWidget()
        seen["registry"] = shell.workspace_registry
        seen["bound"] = current_workspace_registry()
        seen["routes"] = shell.workspace_registry.routes
        shell.deleteLater()
        return 0

    kernel = build_app_kernel(
        gui_runner=gui_runner,
        portable_smoke_runner=lambda: 0,
        workspace_registry=registry,
    )
    assert kernel.workspace_registry is registry
    assert kernel.run([]) == 0
    assert seen["registry"] is registry
    assert seen["bound"] is registry
    assert seen["routes"] == ROUTES
    assert current_workspace_registry() is None


def test_route_modules_no_longer_own_signal_subscription_or_stack_indices() -> None:
    src = ROOT / "src" / "full_album_maker"
    offenders: list[str] = []
    for path in sorted(src.glob("*.py")):
        source = path.read_text(encoding="utf-8")
        if path.name != "foundation_shell.py" and "workspace_changed.connect(" in source:
            offenders.append(f"{path.name}: direct workspace_changed.connect")
        if path.name != "foundation_shell.py" and "workspace_stack._index" in source:
            offenders.append(f"{path.name}: direct workspace_stack._index")

    assert offenders == []
    shell = (src / "foundation_shell.py").read_text(encoding="utf-8")
    assert "workspace_changed.connect(self.workspace_registry.activate)" in shell


def test_full_production_window_registers_all_nine_routes_and_render_last() -> None:
    script = textwrap.dedent(
        r"""
        import os
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        os.environ.setdefault("FAM_DISABLE_TEMPLATE_THUMBNAIL_RENDER", "1")
        os.environ.setdefault("FAM_STEP09_PROVIDER", "mock")
        os.environ.setdefault("FAM_STEP11_NO_RECOVERY_PROMPT", "1")

        from PySide6.QtWidgets import QApplication
        import full_album_maker.main
        from full_album_maker.foundation_window import FoundationMainWindow

        app = QApplication.instance() or QApplication([])
        window = FoundationMainWindow()
        app.processEvents()
        app.processEvents()

        registry = window.foundation_shell.workspace_registry
        expected = ("home", "media", "album", "timeline", "visual", "template", "spectrum", "ai_agent", "render")
        assert registry.routes == expected
        assert registry.registered_routes == expected
        registry.assert_complete()

        names = registry.listener_names
        assert names[0] == "foundation-shell"
        assert "home-route" in names
        assert "media-route" in names
        assert "media-completion-route" in names
        assert "album-route" in names
        assert "timeline-route" in names
        assert "visual-route" in names
        assert "template-route" in names
        assert "spectrum-route" in names
        assert "ai-agent-route" in names
        assert names[-1] == "render-route"

        for route in expected:
            window.foundation_shell.set_workspace(route)
            app.processEvents()
            app.processEvents()
            assert registry.current_route == route
            assert window.foundation_state.workspace == route
            bundle = registry.bundle(route)
            assert bundle.workspace is not None
            assert window.foundation_shell.workspace_stack.currentWidget() is bundle.workspace

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
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + "\n" + result.stderr
