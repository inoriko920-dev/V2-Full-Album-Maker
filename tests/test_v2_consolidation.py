from __future__ import annotations

from pathlib import Path

import pytest

from full_album_maker.production_runtime import (
    PRODUCTION_INSTALLER_NAMES,
    ProductionRuntimeInstaller,
    RuntimeInstaller,
)


ROOT = Path(__file__).resolve().parents[1]


EXPECTED_INSTALLER_ORDER = (
    "playlist-feature",
    "gemini-schema-compat",
    "playlist-hardening",
    "visual-feature",
    "engine-hardening",
    "source-integrity",
    "ui-hardening",
    "atomic-bundle",
    "render-lifecycle",
    "project-dirty-state",
    "async-import",
    "step03-media",
    "step03-media-completion",
    "step03-media-layout-fix",
    "step04-album",
    "step05-timeline",
    "step05-timeline-completion",
    "step06-visual",
    "step06-visual-preview-decode",
    "step06-visual-timeline-completion",
    "step07-template",
    "step08-spectrum",
    "step09-ai-agent",
    "step10-queue-presentation",
    "step10-render",
    "step11-integration",
    "step11-integration-completion",
)


def test_production_runtime_manifest_preserves_exact_proven_order() -> None:
    assert PRODUCTION_INSTALLER_NAMES == EXPECTED_INSTALLER_ORDER
    assert len(PRODUCTION_INSTALLER_NAMES) == 27
    assert len(set(PRODUCTION_INSTALLER_NAMES)) == 27


def test_runtime_installer_runs_once_in_order() -> None:
    calls: list[str] = []
    plan = ProductionRuntimeInstaller(
        RuntimeInstaller(name, lambda name=name: calls.append(name))
        for name in ("a", "b", "c")
    )

    assert plan.install() == ("a", "b", "c")
    assert plan.install() == ("a", "b", "c")
    assert calls == ["a", "b", "c"]
    assert plan.is_installed


def test_runtime_installer_retry_continues_after_first_incomplete_installer() -> None:
    calls: list[str] = []
    failures = {"b": 1}

    def run(name: str) -> None:
        calls.append(name)
        if failures.get(name, 0):
            failures[name] -= 1
            raise RuntimeError(name)

    plan = ProductionRuntimeInstaller(
        RuntimeInstaller(name, lambda name=name: run(name))
        for name in ("a", "b", "c")
    )

    with pytest.raises(RuntimeError, match="b"):
        plan.install()

    assert plan.completed_names == ("a",)
    assert calls == ["a", "b"]

    assert plan.install() == ("a", "b", "c")
    assert calls == ["a", "b", "b", "c"]
    assert plan.is_installed


def test_main_has_one_runtime_bootstrap_owner_not_individual_installer_wiring() -> None:
    main = (ROOT / "src" / "full_album_maker" / "main.py").read_text(encoding="utf-8")
    assert main.count("install_production_runtime()") == 1
    assert "PRODUCTION_INSTALLERS" not in main
    assert "install_async_import()" not in main
    assert "install_step03_media()" not in main
    assert "install_step10_render()" not in main
    assert "install_step11_integration_completion()" not in main


def test_consolidation_does_not_change_frozen_schema_or_route_contracts() -> None:
    models = (ROOT / "src" / "full_album_maker" / "editor_models.py").read_text(encoding="utf-8")
    tokens = (ROOT / "src" / "full_album_maker" / "foundation_tokens.py").read_text(encoding="utf-8")
    assert "TIMEBASE = 240_000" in models
    assert "SCHEMA_VERSION = 2" in models
    assert "schema_version: int = SCHEMA_VERSION" in models
    for route in (
        "home",
        "media",
        "album",
        "timeline",
        "visual",
        "template",
        "spectrum",
        "ai_agent",
        "render",
    ):
        assert f'"{route}"' in tokens
