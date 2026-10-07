from __future__ import annotations

import ast
from pathlib import Path

import pytest

from full_album_maker.app_kernel import (
    AppKernel,
    CompositionRoot,
    LegacyRuntimeAdapter,
    build_app_kernel,
)
from full_album_maker.feature_parity_registry import (
    DEFAULT_FEATURE_PARITY_REGISTRY,
    FeatureParityRegistry,
    RegistryValidationError,
)


ROOT = Path(__file__).resolve().parents[1]


def test_composition_root_builds_kernel_with_m0_registry() -> None:
    kernel = build_app_kernel(gui_runner=lambda: 0, portable_smoke_runner=lambda: 0)

    assert isinstance(kernel, AppKernel)
    assert isinstance(kernel.runtime, LegacyRuntimeAdapter)
    assert kernel.feature_parity is DEFAULT_FEATURE_PARITY_REGISTRY
    assert kernel.feature_parity.validate() == ()


def test_kernel_default_path_runs_gui_exactly_once() -> None:
    calls: list[str] = []

    kernel = build_app_kernel(
        gui_runner=lambda: calls.append("gui") or 17,
        portable_smoke_runner=lambda: calls.append("smoke") or 23,
    )

    assert kernel.run([]) == 17
    assert calls == ["gui"]


def test_kernel_portable_smoke_flag_runs_smoke_exactly_once() -> None:
    calls: list[str] = []

    kernel = build_app_kernel(
        gui_runner=lambda: calls.append("gui") or 17,
        portable_smoke_runner=lambda: calls.append("smoke") or 23,
    )

    assert kernel.run(["--portable-smoke"]) == 23
    assert calls == ["smoke"]


def test_kernel_preserves_legacy_cli_behavior_for_unrelated_args() -> None:
    calls: list[str] = []
    kernel = build_app_kernel(
        gui_runner=lambda: calls.append("gui") or 0,
        portable_smoke_runner=lambda: calls.append("smoke") or 0,
    )

    assert kernel.run(["--anything-else", "value"]) == 0
    assert calls == ["gui"]


def test_composition_root_fails_closed_if_m0_registry_is_invalid() -> None:
    invalid = FeatureParityRegistry(())

    with pytest.raises(RegistryValidationError, match="registry is empty"):
        CompositionRoot(
            gui_runner=lambda: 0,
            portable_smoke_runner=lambda: 0,
            feature_parity=invalid,
        ).build()


def test_app_kernel_has_no_qt_subprocess_or_project_state_dependency() -> None:
    path = ROOT / "src" / "full_album_maker" / "app_kernel.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)

    assert not any(name.startswith("PySide6") for name in imported)
    assert "subprocess" not in imported
    assert not any(
        name.endswith(suffix)
        for name in imported
        for suffix in (
            "editor_models",
            "editor_controller",
            "editor_session",
            "project",
            "project_repository",
        )
    )


def test_main_keeps_legacy_installers_before_gui_import_and_routes_through_kernel() -> None:
    source = (ROOT / "src" / "full_album_maker" / "main.py").read_text(encoding="utf-8")

    gui_import = "from full_album_maker.v14_window import run"
    assert source.count("install_") >= 30
    assert source.index("install_async_import()") < source.index(gui_import)
    assert "build_app_kernel(" in source
    assert "gui_runner=_run_legacy_gui" in source
    assert "portable_smoke_runner=_run_legacy_portable_smoke" in source
    assert "return kernel.run(args)" in source
