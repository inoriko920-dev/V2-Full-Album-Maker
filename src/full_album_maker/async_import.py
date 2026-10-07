from __future__ import annotations

import threading
from pathlib import Path
from typing import Any

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QFileDialog

from . import ui as ui_module
from . import visual_feature as visual_feature_module
from .media import probe_duration
from .media_probe_service import (
    MediaProbeService,
    SourceFingerprint,
    current_media_probe_service,
)
from .project import MediaItem

_installed = False
_originals: dict[str, Any] = {}


def _legacy_duration_probe(source: str, kind: str | None) -> float:
    # Compatibility surface for direct legacy-window tests/extensions. Production
    # windows launched through AppKernel capture the exact M5 service instead.
    return float(probe_duration(source, kind))


def _legacy_image_probe(source: str):
    return visual_feature_module.probe_image(source)


def _legacy_audio_tag_probe(source: str) -> tuple[str, str]:
    return visual_feature_module.probe_audio_tags(source)


LEGACY_ASYNC_IMPORT_PROBE_SERVICE = MediaProbeService(
    duration_probe=_legacy_duration_probe,
    image_probe=_legacy_image_probe,
    audio_tag_probe=_legacy_audio_tag_probe,
)


class _ImportBridge(QObject):
    finished = Signal(object)


def _path_key(path: str) -> str:
    try:
        return str(Path(path).expanduser().resolve(strict=False)).casefold()
    except OSError:
        return str(Path(path).expanduser().absolute()).casefold()


def _target_paths(window, kind: str) -> set[str]:
    if kind == "video":
        items = window.project.videos
    elif kind == "audio":
        items = window.project.audios
    elif kind == "image":
        items = visual_feature_module.images(window.project)
    else:
        items = []
    return {_path_key(item.path) for item in items}


def _item_source_fingerprint(item: MediaItem) -> SourceFingerprint | None:
    value = getattr(item, "_source_fingerprint", None)
    return value if isinstance(value, SourceFingerprint) else None


def _item_source_still_current(item: MediaItem) -> bool:
    fingerprint = _item_source_fingerprint(item)
    if fingerprint is None:
        return False
    return fingerprint.matches_path(item.path)


def _probe_one(
    kind: str,
    path: str,
    service: MediaProbeService | None = None,
) -> MediaItem:
    probe_service = service or current_media_probe_service() or LEGACY_ASYNC_IMPORT_PROBE_SERVICE
    result = probe_service.probe(path, kind)

    if kind == "video":
        item = MediaItem(path=path, duration=float(result.duration_seconds or 0.0))
        setattr(item, "_source_fingerprint", result.fingerprint)
        return item

    if kind == "audio":
        item = MediaItem(path=path, duration=float(result.duration_seconds or 0.0))
        if result.title:
            setattr(item, "display_title", result.title)
        if result.artist:
            setattr(item, "display_artist", result.artist)
        setattr(item, "metadata_probed", True)
        setattr(item, "_source_fingerprint", result.fingerprint)
        return item

    if kind == "image":
        item = MediaItem(path=path, duration=0.0)
        if result.width is not None:
            setattr(item, "width", int(result.width))
        if result.height is not None:
            setattr(item, "height", int(result.height))
        setattr(item, "_source_fingerprint", result.fingerprint)
        return item

    raise ValueError(f"Jenis media tidak dikenal: {kind}")


def _start_import(window, kind: str, paths: list[str]) -> None:
    if not paths or getattr(window, "_import_closed", False):
        return

    current = _target_paths(window, kind)
    pending: set[str] = window._import_pending_keys
    selected: list[str] = []
    skipped = 0
    for raw in paths:
        path = str(raw).strip()
        if not path:
            continue
        key = _path_key(path)
        if key in current or key in pending:
            skipped += 1
            continue
        pending.add(key)
        selected.append(path)

    if skipped:
        window.log.appendPlainText(f"{skipped} file duplikat/pending dilewati saat impor.")
    if not selected:
        return

    project_ref = window.project
    bridge = window._import_bridge
    probe_service = (
        getattr(window, "_m5_media_probe_service", None)
        or current_media_probe_service()
        or LEGACY_ASYNC_IMPORT_PROBE_SERVICE
    )
    window._import_job_count += 1
    window.log.appendPlainText(
        f"Impor {kind} dimulai di background: {len(selected)} file. UI tetap dapat digunakan."
    )

    def work() -> None:
        items: list[MediaItem] = []
        errors: list[str] = []
        try:
            for path in selected:
                try:
                    items.append(_probe_one(kind, path, probe_service))
                except (ValueError, OSError) as exc:
                    errors.append(str(exc))
                except Exception as exc:  # defensive boundary around codec/decoder tools
                    errors.append(f"Gagal membaca {Path(path).name}: {exc}")
        finally:
            bridge.finished.emit(
                {
                    "kind": kind,
                    "paths": selected,
                    "items": items,
                    "errors": errors,
                    "project_ref": project_ref,
                }
            )

    threading.Thread(target=work, daemon=True, name=f"fam-import-{kind}").start()


def _finish_import(self, payload: dict[str, Any]) -> None:
    kind = str(payload.get("kind", ""))
    paths = [str(x) for x in payload.get("paths", [])]
    items = list(payload.get("items", []))
    errors = [str(x) for x in payload.get("errors", [])]
    project_ref = payload.get("project_ref")

    for path in paths:
        self._import_pending_keys.discard(_path_key(path))
    self._import_job_count = max(0, int(self._import_job_count) - 1)

    if getattr(self, "_import_closed", False):
        return

    if self.project is not project_ref:
        self.log.appendPlainText(
            f"Hasil impor {kind} diabaikan karena proyek aktif sudah berganti."
        )
        return

    existing = _target_paths(self, kind)
    accepted: list[MediaItem] = []
    stale_sources: list[str] = []
    for item in items:
        if not _item_source_still_current(item):
            stale_sources.append(Path(item.path).name or item.path)
            continue
        key = _path_key(item.path)
        if key in existing:
            continue
        existing.add(key)
        accepted.append(item)

    if kind == "video":
        self.project.videos.extend(accepted)
    elif kind == "audio":
        self.project.audios.extend(accepted)
    elif kind == "image":
        visual_feature_module.images(self.project).extend(accepted)

    if kind in {"video", "image"} and accepted:
        order = getattr(self.project, "_visual_order", None)
        if not isinstance(order, list):
            order = []
            setattr(self.project, "_visual_order", order)
        known = {_path_key(value) for value in order}
        for item in accepted:
            key = _path_key(item.path)
            if key not in known:
                order.append(item.path)
                known.add(key)

    if accepted:
        self.invalidate_timeline()
        self.refresh()
        self.log.appendPlainText(
            f"Impor {kind} selesai: {len(accepted)} file ditambahkan ke proyek."
        )
    else:
        self.log.appendPlainText(f"Impor {kind} selesai tanpa file baru.")

    if stale_sources:
        preview = "\n".join(
            f"• {name}: source berubah setelah probe; impor dibatalkan"
            for name in stale_sources[:8]
        )
        more = (
            f"\n• …dan {len(stale_sources) - 8} source lain"
            if len(stale_sources) > 8 else ""
        )
        self.log.appendPlainText(
            f"{len(stale_sources)} file tidak diadopsi karena source berubah:\n"
            f"{preview}{more}"
        )

    if errors:
        preview = "\n".join(f"• {message}" for message in errors[:8])
        more = f"\n• …dan {len(errors) - 8} error lain" if len(errors) > 8 else ""
        self.log.appendPlainText(
            f"{len(errors)} file gagal diimpor:\n{preview}{more}"
        )


def _patched_init(self, *args, **kwargs) -> None:
    self._m5_media_probe_service = (
        current_media_probe_service() or LEGACY_ASYNC_IMPORT_PROBE_SERVICE
    )
    self._import_pending_keys: set[str] = set()
    self._import_job_count = 0
    self._import_closed = False
    # Keep the bridge un-parented. If the window closes while a daemon import
    # worker is winding down, Qt can safely auto-disconnect the dead receiver
    # without the signal source itself having been deleted first.
    self._import_bridge = _ImportBridge()
    self._import_bridge.finished.connect(self._finish_media_import)
    _originals["ui_init"](self, *args, **kwargs)


def _patched_close_event(self, event) -> None:
    _originals["close_event"](self, event)
    if event.isAccepted():
        self._import_closed = True
        self._import_pending_keys.clear()
        self._import_job_count = 0


def _add_video(self) -> None:
    paths, _ = QFileDialog.getOpenFileNames(
        self,
        "Pilih Footage",
        "",
        "Video (*.mp4 *.mov *.mkv *.webm *.avi *.m4v *.wmv)",
    )
    _start_import(self, "video", list(paths))


def _add_audio(self) -> None:
    paths, _ = QFileDialog.getOpenFileNames(
        self,
        "Pilih Lagu",
        "",
        "Audio (*.mp3 *.wav *.flac *.m4a *.aac *.ogg *.opus)",
    )
    _start_import(self, "audio", list(paths))


def _add_image(self) -> None:
    paths, _ = QFileDialog.getOpenFileNames(
        self,
        "Pilih Foto Footage",
        "",
        "Foto (*.jpg *.jpeg *.png *.webp)",
    )
    _start_import(self, "image", list(paths))


def install_async_import() -> None:
    global _installed
    if _installed:
        return
    MainWindow = ui_module.MainWindow
    _originals.update(
        {
            "ui_init": MainWindow.__init__,
            "add_video": MainWindow.add_video,
            "add_audio": MainWindow.add_audio,
            "add_image": MainWindow.add_image,
            "close_event": MainWindow.closeEvent,
        }
    )

    MainWindow.__init__ = _patched_init
    MainWindow.add_video = _add_video
    MainWindow.add_audio = _add_audio
    MainWindow.add_image = _add_image
    MainWindow.closeEvent = _patched_close_event
    MainWindow._finish_media_import = _finish_import
    _installed = True


def uninstall_async_import() -> None:
    global _installed
    if not _installed:
        return
    MainWindow = ui_module.MainWindow
    MainWindow.__init__ = _originals["ui_init"]
    MainWindow.add_video = _originals["add_video"]
    MainWindow.add_audio = _originals["add_audio"]
    MainWindow.add_image = _originals["add_image"]
    MainWindow.closeEvent = _originals["close_event"]
    if hasattr(MainWindow, "_finish_media_import"):
        delattr(MainWindow, "_finish_media_import")
    _originals.clear()
    _installed = False
