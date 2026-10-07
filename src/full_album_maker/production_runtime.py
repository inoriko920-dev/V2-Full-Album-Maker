"""M9 consolidated production bootstrap for the proven installer chain.

This module does not replace feature implementations. It gives the surviving
legacy compatibility/presentation installers one explicit ordered owner so the
production entrypoint no longer wires dozens of patch functions independently.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .gemini_schema_compat import install_gemini_schema_compat
from .playlist_feature import install_feature
from .playlist_hardening import install_playlist_hardening
from .visual_feature import install_visual_feature
from .engine_hardening import install_engine_hardening
from .source_integrity import install_source_integrity
from .ui_hardening import install_ui_hardening
from .atomic_bundle import install_atomic_bundle
from .render_lifecycle import install_render_lifecycle
from .project_dirty import install_project_dirty_state
from .async_import import install_async_import
from .media_feature import install_step03_media
from .media_completion import install_step03_media_completion
from .media_layout_fix import install_step03_media_layout_fix
from .album_feature import install_step04_album
from .timeline_feature_step05 import install_step05_timeline
from .timeline_completion_step05 import install_step05_timeline_completion
from .visual_feature_step06 import install_step06_visual
from .visual_preview_decode_step06 import install_step06_visual_preview_decode
from .visual_timeline_completion_step06 import install_step06_visual_timeline_completion
from .template_feature_step07 import install_step07_template
from .spectrum_feature_step08 import install_step08_spectrum
from .ai_feature_step09 import install_step09_ai_agent
from .render_queue_presentation_step10 import install_step10_queue_presentation
from .render_feature_step10 import install_step10_render
from .integration_feature_step11 import install_step11_integration
from .integration_completion_step11 import install_step11_integration_completion


Installer = Callable[[], None]


@dataclass(frozen=True, slots=True)
class RuntimeInstaller:
    name: str
    install: Installer


class ProductionRuntimeInstaller:
    """Own the exact proven runtime installer order.

    Completion is tracked per installer. If one installer fails, a diagnostic
    retry in the same process continues from the first incomplete installer
    instead of re-running already completed global monkey-patches.
    """

    def __init__(self, installers: Iterable[RuntimeInstaller]) -> None:
        values = tuple(installers)
        if not values:
            raise ValueError("ProductionRuntimeInstaller membutuhkan installer.")
        names = tuple(item.name for item in values)
        if any(not name.strip() for name in names):
            raise ValueError("Nama installer tidak boleh kosong.")
        if len(set(names)) != len(names):
            raise ValueError("Nama installer production harus unik.")
        if any(not callable(item.install) for item in values):
            raise TypeError("Semua production installer harus callable.")
        self._installers = values
        self._completed: list[str] = []

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(item.name for item in self._installers)

    @property
    def completed_names(self) -> tuple[str, ...]:
        return tuple(self._completed)

    @property
    def is_installed(self) -> bool:
        return len(self._completed) == len(self._installers)

    def install(self) -> tuple[str, ...]:
        completed = set(self._completed)
        for item in self._installers:
            if item.name in completed:
                continue
            item.install()
            self._completed.append(item.name)
            completed.add(item.name)
        return self.completed_names


PRODUCTION_INSTALLERS: tuple[RuntimeInstaller, ...] = (
    RuntimeInstaller("playlist-feature", install_feature),
    RuntimeInstaller("gemini-schema-compat", install_gemini_schema_compat),
    RuntimeInstaller("playlist-hardening", install_playlist_hardening),
    RuntimeInstaller("visual-feature", install_visual_feature),
    RuntimeInstaller("engine-hardening", install_engine_hardening),
    RuntimeInstaller("source-integrity", install_source_integrity),
    RuntimeInstaller("ui-hardening", install_ui_hardening),
    RuntimeInstaller("atomic-bundle", install_atomic_bundle),
    RuntimeInstaller("render-lifecycle", install_render_lifecycle),
    RuntimeInstaller("project-dirty-state", install_project_dirty_state),
    RuntimeInstaller("async-import", install_async_import),
    RuntimeInstaller("step03-media", install_step03_media),
    RuntimeInstaller("step03-media-completion", install_step03_media_completion),
    RuntimeInstaller("step03-media-layout-fix", install_step03_media_layout_fix),
    RuntimeInstaller("step04-album", install_step04_album),
    RuntimeInstaller("step05-timeline", install_step05_timeline),
    RuntimeInstaller("step05-timeline-completion", install_step05_timeline_completion),
    RuntimeInstaller("step06-visual", install_step06_visual),
    RuntimeInstaller("step06-visual-preview-decode", install_step06_visual_preview_decode),
    RuntimeInstaller("step06-visual-timeline-completion", install_step06_visual_timeline_completion),
    RuntimeInstaller("step07-template", install_step07_template),
    RuntimeInstaller("step08-spectrum", install_step08_spectrum),
    RuntimeInstaller("step09-ai-agent", install_step09_ai_agent),
    RuntimeInstaller("step10-queue-presentation", install_step10_queue_presentation),
    RuntimeInstaller("step10-render", install_step10_render),
    RuntimeInstaller("step11-integration", install_step11_integration),
    RuntimeInstaller("step11-integration-completion", install_step11_integration_completion),
)

PRODUCTION_INSTALLER_NAMES = tuple(item.name for item in PRODUCTION_INSTALLERS)
DEFAULT_PRODUCTION_RUNTIME_INSTALLER = ProductionRuntimeInstaller(PRODUCTION_INSTALLERS)


def install_production_runtime() -> tuple[str, ...]:
    """Install the proven production compatibility/presentation chain once."""

    return DEFAULT_PRODUCTION_RUNTIME_INSTALLER.install()


__all__ = [
    "DEFAULT_PRODUCTION_RUNTIME_INSTALLER",
    "Installer",
    "PRODUCTION_INSTALLERS",
    "PRODUCTION_INSTALLER_NAMES",
    "ProductionRuntimeInstaller",
    "RuntimeInstaller",
    "install_production_runtime",
]
