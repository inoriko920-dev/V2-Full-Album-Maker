from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import tempfile
import threading
import time
from typing import Any, Iterable, Iterator, Mapping
from uuid import uuid4

from .media_library_model import (
    MediaAsset, MediaMetadata, MediaStatus, MediaType, normalize_tags, stable_asset_id,
)

VIDEO_EXTENSIONS = frozenset({'.mp4', '.mov', '.mkv', '.webm', '.avi', '.m4v', '.wmv'})
AUDIO_EXTENSIONS = frozenset({'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.opus'})
PHOTO_EXTENSIONS = frozenset({'.jpg', '.jpeg', '.png', '.webp'})
SUPPORTED_EXTENSIONS = VIDEO_EXTENSIONS | AUDIO_EXTENSIONS | PHOTO_EXTENSIONS
IGNORED_DIRECTORY_NAMES = frozenset({'.git', '.svn', '__pycache__', 'node_modules', '.cache'})


def media_type_for_path(path: str | Path) -> MediaType | None:
    suffix = Path(path).suffix.casefold()
    if suffix in VIDEO_EXTENSIONS:
        return MediaType.VIDEO
    if suffix in AUDIO_EXTENSIONS:
        return MediaType.AUDIO
    if suffix in PHOTO_EXTENSIONS:
        return MediaType.PHOTO
    return None


def canonical_path_key(path: str | Path) -> str:
    source = Path(path).expanduser().resolve(strict=False)
    # os.path.normcase preserves platform filesystem semantics better than
    # unconditional lowercasing on case-sensitive systems.
    return os.path.normcase(str(source))


_SIDECAR_LOCK_TIMEOUT_SECONDS = 2.0


def _lock_file_handle(handle) -> bool:
    if os.name == "nt":
        import msvcrt

        try:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False

    import fcntl

    try:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


def _unlock_file_handle(handle) -> None:
    try:
        if os.name == "nt":
            import msvcrt

            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            return

        import fcntl

        fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except OSError:
        pass


@contextmanager
def _sidecar_file_lock(target: Path) -> Iterator[None]:
    lock_path = target.with_name(f".{target.name}.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    handle = os.fdopen(fd, "r+b", buffering=0)
    try:
        if os.fstat(handle.fileno()).st_size == 0:
            handle.write(b"0")
            handle.flush()
        deadline = time.monotonic() + _SIDECAR_LOCK_TIMEOUT_SECONDS
        while not _lock_file_handle(handle):
            if time.monotonic() >= deadline:
                raise OSError(
                    "Metadata Media sedang disimpan oleh instance aplikasi lain. "
                    "Coba lagi sesaat."
                )
            time.sleep(0.02)
        try:
            yield
        finally:
            _unlock_file_handle(handle)
    finally:
        handle.close()


class SidecarStoreError(OSError):
    """Base error for media sidecar persistence failures."""


class SidecarCorruptionError(SidecarStoreError):
    """Raised when an existing sidecar cannot be trusted or parsed safely."""


class SidecarUnsupportedVersion(SidecarStoreError):
    """Raised when a newer/unknown sidecar schema must not be overwritten."""


def _validate_sidecar_record(asset_id: object, value: object) -> None:
    if not isinstance(asset_id, str) or not asset_id:
        raise SidecarCorruptionError("ID asset sidecar tidak valid.")
    if not isinstance(value, dict):
        raise SidecarCorruptionError(
            f"Record sidecar {asset_id!r} bukan object JSON."
        )
    if "favorite" in value and not isinstance(value["favorite"], bool):
        raise SidecarCorruptionError(
            f"Field favorite record {asset_id!r} tidak valid."
        )
    for name in ("tags", "collections"):
        if name not in value:
            continue
        raw = value[name]
        if (
            not isinstance(raw, list)
            or not all(isinstance(item, str) for item in raw)
        ):
            raise SidecarCorruptionError(
                f"Field {name} record {asset_id!r} tidak valid."
            )
    if "description" in value and not isinstance(value["description"], str):
        raise SidecarCorruptionError(
            f"Field description record {asset_id!r} tidak valid."
        )
    if "imported_at" in value:
        raw = value["imported_at"]
        if isinstance(raw, bool) or not isinstance(raw, (int, float)):
            raise SidecarCorruptionError(
                f"Field imported_at record {asset_id!r} tidak valid."
            )


def _read_sidecar_records(target: Path, version: int) -> dict[str, "SidecarRecord"]:
    if not target.exists():
        return {}
    try:
        text = target.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    except (OSError, UnicodeError) as exc:
        raise SidecarCorruptionError(
            f"Sidecar metadata tidak dapat dibaca: {exc}"
        ) from exc
    try:
        raw = json.loads(text)
    except json.JSONDecodeError as exc:
        raise SidecarCorruptionError(
            f"Sidecar metadata JSON rusak: {exc}"
        ) from exc
    if not isinstance(raw, dict):
        raise SidecarCorruptionError("Root sidecar metadata bukan object JSON.")
    found_version = raw.get("version")
    if found_version != version:
        raise SidecarUnsupportedVersion(
            f"Versi sidecar metadata tidak didukung: {found_version!r} "
            f"(aplikasi mendukung {version})."
        )
    records = raw.get("records")
    if not isinstance(records, dict):
        raise SidecarCorruptionError("Field records sidecar metadata tidak valid.")
    clean: dict[str, SidecarRecord] = {}
    for asset_id, value in records.items():
        _validate_sidecar_record(asset_id, value)
        clean[asset_id] = SidecarRecord.from_mapping(value)
    return clean


def _cleanup_sidecar_temps(target: Path) -> int:
    removed = 0
    for candidate in target.parent.glob(f"{target.name}.*.tmp"):
        try:
            candidate.unlink(missing_ok=True)
            removed += 1
        except OSError:
            pass
    return removed


def _write_sidecar_records(
    target: Path,
    version: int,
    records: Mapping[str, "SidecarRecord"],
) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "version": version,
        "records": {
            key: {
                "favorite": value.favorite,
                "tags": list(value.tags),
                "description": value.description,
                "collections": list(value.collections),
                "imported_at": value.imported_at,
            }
            for key, value in sorted(records.items())
        },
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    fd, tmp = tempfile.mkstemp(
        prefix=target.name + ".",
        suffix=".tmp",
        dir=str(target.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, target)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


class SidecarMigrationConflict(ValueError):
    """Raised when relink metadata cannot be moved without losing destination data."""


@dataclass(frozen=True)
class SidecarRecord:
    favorite: bool = False
    tags: tuple[str, ...] = ()
    description: str = ''
    collections: tuple[str, ...] = ()
    imported_at: float = 0.0

    @classmethod
    def from_mapping(cls, raw: Mapping[str, Any]) -> 'SidecarRecord':
        tags = raw.get('tags', ())
        collections = raw.get('collections', ())
        if not isinstance(tags, (list, tuple)):
            tags = ()
        if not isinstance(collections, (list, tuple)):
            collections = ()
        try:
            imported_at = float(raw.get('imported_at', 0.0) or 0.0)
        except (TypeError, ValueError):
            imported_at = 0.0
        return cls(
            favorite=bool(raw.get('favorite', False)),
            tags=normalize_tags(str(x) for x in tags),
            description=str(raw.get('description', '') or '').strip(),
            collections=normalize_tags(str(x) for x in collections),
            imported_at=max(0.0, imported_at),
        )


class MediaSidecarStore:
    """Per-project media metadata with merge-safe, corruption-safe persistence."""

    VERSION = 1

    def __init__(self, project_path: str | Path | None = None) -> None:
        self.project_path = Path(project_path).expanduser() if project_path else None
        self._records: dict[str, SidecarRecord] = {}
        self._loaded = False
        self._dirty_records: set[str] = set()
        self._pending_migrations: list[tuple[str, str]] = []
        self.last_recovery_warning = ""
        self.quarantined_path: Path | None = None
        self.persistence_blocked = False

    @property
    def path(self) -> Path | None:
        if self.project_path is None:
            return None
        return self.project_path.with_suffix(self.project_path.suffix + ".media.json")

    def _quarantine_corrupt_store(
        self,
        target: Path,
        reason: Exception,
    ) -> Path | None:
        if not target.exists():
            self.last_recovery_warning = (
                "Metadata media tidak dapat dibaca, tetapi file sidecar sudah "
                "tidak ada. Metadata dibuka kosong."
            )
            return None

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        quarantine = target.with_name(
            f"{target.stem}.corrupt-{timestamp}-{uuid4().hex[:8]}{target.suffix}"
        )
        try:
            os.replace(target, quarantine)
        except OSError:
            try:
                shutil.copy2(target, quarantine)
            except OSError as backup_exc:
                self.persistence_blocked = True
                self.last_recovery_warning = (
                    "Metadata media rusak dan tidak dapat dikarantina. "
                    "Persistence metadata dinonaktifkan agar file asli tidak "
                    f"tertimpa ({backup_exc})."
                )
                return None
            try:
                target.unlink(missing_ok=True)
            except OSError:
                self.persistence_blocked = True
                self.last_recovery_warning = (
                    "Metadata media rusak berhasil disalin ke karantina, tetapi "
                    "file asli tidak dapat dipindahkan/dihapus. Persistence "
                    "dinonaktifkan agar bukti asli tidak tertimpa."
                )
                self.quarantined_path = quarantine
                return quarantine

        self.quarantined_path = quarantine
        self.last_recovery_warning = (
            "Metadata media rusak telah dikarantina sebagai "
            f"{quarantine.name}. Aplikasi memakai metadata kosong/terakhir yang "
            "masih ada di memori; file karantina dipertahankan untuk recovery."
        )
        return quarantine

    def _unsupported_version(self, target: Path, exc: Exception) -> None:
        self.persistence_blocked = True
        self.last_recovery_warning = (
            "Versi metadata media pada disk tidak didukung oleh aplikasi ini. "
            "File asli dipertahankan dan persistence metadata dinonaktifkan agar "
            f"format yang lebih baru tidak tertimpa ({exc})."
        )

    def _read_latest_for_write(self, target: Path) -> dict[str, SidecarRecord]:
        if self.persistence_blocked:
            raise SidecarStoreError(
                self.last_recovery_warning
                or "Persistence metadata media sedang dinonaktifkan."
            )
        try:
            return _read_sidecar_records(target, self.VERSION)
        except SidecarUnsupportedVersion as exc:
            self._unsupported_version(target, exc)
            raise
        except SidecarCorruptionError as exc:
            self._quarantine_corrupt_store(target, exc)
            # Preserve every last-known-good local record for an explicit retry.
            self._dirty_records.update(self._records)
            raise SidecarCorruptionError(
                "Metadata media di disk rusak dan sudah diamankan ke karantina. "
                "Perubahan saat ini belum disimpan; coba simpan lagi untuk "
                "membuat sidecar baru dari metadata terakhir yang masih valid."
            ) from exc

    def load(self) -> dict[str, SidecarRecord]:
        if self._loaded:
            return dict(self._records)
        self._loaded = True
        target = self.path
        if target is None:
            return {}
        with _sidecar_file_lock(target):
            _cleanup_sidecar_temps(target)
            try:
                self._records = _read_sidecar_records(target, self.VERSION)
            except SidecarUnsupportedVersion as exc:
                self._unsupported_version(target, exc)
                self._records = {}
            except SidecarCorruptionError as exc:
                self._quarantine_corrupt_store(target, exc)
                self._records = {}
        self._clear_local_pending()
        return dict(self._records)

    def get(self, asset_id: str) -> SidecarRecord:
        if not self._loaded:
            self.load()
        return self._records.get(str(asset_id), SidecarRecord())

    def records(self) -> dict[str, SidecarRecord]:
        if not self._loaded:
            self.load()
        return dict(self._records)

    @staticmethod
    def _apply_one_migration(
        latest: dict[str, SidecarRecord],
        old_id: str,
        new_id: str,
    ) -> None:
        old = latest.get(old_id)
        if old is None:
            return
        destination = latest.get(new_id)
        if destination is not None and destination != old:
            raise SidecarMigrationConflict(
                "Metadata tujuan relink sudah ada dan berbeda; migrasi dibatalkan "
                "agar tag/favorit/deskripsi tidak hilang."
            )
        latest.pop(old_id, None)
        latest[new_id] = old if destination is None else destination

    def _apply_local_pending(
        self,
        latest: dict[str, SidecarRecord],
    ) -> dict[str, SidecarRecord]:
        for old_id, new_id in self._pending_migrations:
            self._apply_one_migration(latest, old_id, new_id)
        for dirty_id in tuple(self._dirty_records):
            local = self._records.get(dirty_id)
            if local is not None:
                latest[dirty_id] = local
        return latest

    def _clear_local_pending(self) -> None:
        self._dirty_records.clear()
        self._pending_migrations.clear()

    def _commit_single_record(self, asset_id: str, record: SidecarRecord) -> None:
        target = self.path
        if target is None:
            self._records[asset_id] = record
            self._dirty_records.add(asset_id)
            return
        with _sidecar_file_lock(target):
            latest = self._apply_local_pending(
                self._read_latest_for_write(target)
            )
            latest[asset_id] = record
            _write_sidecar_records(target, self.VERSION, latest)
            _cleanup_sidecar_temps(target)
        self._records = latest
        self._loaded = True
        self._clear_local_pending()

    def set(self, asset_id: str, record: SidecarRecord, *, persist: bool = True) -> None:
        if not self._loaded:
            self.load()
        key = str(asset_id)
        if persist and self.path is not None:
            self._commit_single_record(key, record)
            return
        self._records[key] = record
        self._dirty_records.add(key)

    def update(
        self,
        asset_id: str,
        *,
        favorite: bool | None = None,
        tags: Iterable[str] | None = None,
        description: str | None = None,
        collections: Iterable[str] | None = None,
        imported_at: float | None = None,
        persist: bool = True,
    ) -> SidecarRecord:
        key = str(asset_id)
        target = self.path
        if persist and target is not None:
            with _sidecar_file_lock(target):
                latest = self._apply_local_pending(
                    self._read_latest_for_write(target)
                )
                current = latest.get(key, SidecarRecord())
                record = SidecarRecord(
                    favorite=current.favorite if favorite is None else bool(favorite),
                    tags=current.tags if tags is None else normalize_tags(tags),
                    description=current.description if description is None else str(description).strip(),
                    collections=current.collections if collections is None else normalize_tags(collections),
                    imported_at=current.imported_at if imported_at is None else max(0.0, float(imported_at)),
                )
                latest[key] = record
                _write_sidecar_records(target, self.VERSION, latest)
                _cleanup_sidecar_temps(target)
            self._records = latest
            self._loaded = True
            self._clear_local_pending()
            return record

        current = self.get(key)
        record = SidecarRecord(
            favorite=current.favorite if favorite is None else bool(favorite),
            tags=current.tags if tags is None else normalize_tags(tags),
            description=current.description if description is None else str(description).strip(),
            collections=current.collections if collections is None else normalize_tags(collections),
            imported_at=current.imported_at if imported_at is None else max(0.0, float(imported_at)),
        )
        self._records[key] = record
        self._dirty_records.add(key)
        return record

    def migrate_asset_id(self, old_id: str, new_id: str, *, persist: bool = True) -> None:
        old_id = str(old_id)
        new_id = str(new_id)
        if old_id == new_id:
            return
        target = self.path
        if persist and target is not None:
            with _sidecar_file_lock(target):
                latest = self._apply_local_pending(
                    self._read_latest_for_write(target)
                )
                self._apply_one_migration(latest, old_id, new_id)
                _write_sidecar_records(target, self.VERSION, latest)
                _cleanup_sidecar_temps(target)
            self._records = latest
            self._loaded = True
            self._clear_local_pending()
            return

        if not self._loaded:
            self.load()
        old = self._records.get(old_id)
        destination = self._records.get(new_id)
        if old is not None and destination is not None and destination != old:
            raise SidecarMigrationConflict(
                "Metadata tujuan relink sudah ada dan berbeda; migrasi dibatalkan "
                "agar metadata lama tidak tertimpa."
            )
        self._records.pop(old_id, None)
        if old is not None:
            self._records[new_id] = old if destination is None else destination
            self._dirty_records.add(new_id)
        self._dirty_records.discard(old_id)
        self._pending_migrations.append((old_id, new_id))

    def rebind_project_path(
        self,
        project_path: str | Path | None,
        *,
        carry_current: bool = True,
        persist: bool = True,
    ) -> bool:
        new_path = Path(project_path).expanduser() if project_path else None
        old_path = self.project_path
        if old_path == new_path:
            return False

        if not self._loaded:
            self.load()

        current_records = dict(self._records)
        current_migrations = list(self._pending_migrations)

        self.project_path = new_path
        self.last_recovery_warning = ""
        self.quarantined_path = None
        self.persistence_blocked = False
        if not carry_current:
            self._records = {}
            self._loaded = False
            self._clear_local_pending()
            self.load()
            return True

        self._records = current_records
        self._loaded = True
        self._dirty_records = set(current_records)
        self._pending_migrations = current_migrations

        if persist and self.path is not None:
            self.save()
        return True

    def save(self) -> bool:
        target = self.path
        if target is None:
            return False
        if not self._loaded:
            self.load()

        with _sidecar_file_lock(target):
            latest = self._apply_local_pending(
                self._read_latest_for_write(target)
            )
            _write_sidecar_records(target, self.VERSION, latest)
            _cleanup_sidecar_temps(target)

        self._records = latest
        self._loaded = True
        self._clear_local_pending()
        return True

def _safe_stat(path: Path) -> tuple[MediaStatus, int | None, float | None, float]:
    try:
        stat = path.stat()
    except OSError:
        return MediaStatus.MISSING, None, None, 0.0
    # Creation time is platform-dependent. We expose ctime as filesystem
    # timestamp and label it accordingly in the inspector instead of claiming EXIF creation.
    return MediaStatus.READY, int(stat.st_size), float(stat.st_ctime), float(stat.st_mtime)


def asset_from_item(item: Any, media_type: MediaType, store: MediaSidecarStore | None = None) -> MediaAsset:
    path = str(getattr(item, 'path', '') or '')
    asset_id = stable_asset_id(path, media_type)
    sidecar = store.get(asset_id) if store is not None else SidecarRecord()
    source = Path(path)
    status, size, created_at, modified_at = _safe_stat(source)
    duration = getattr(item, 'duration', None)
    try:
        duration = float(duration) if duration is not None and float(duration) >= 0 else None
    except (TypeError, ValueError):
        duration = None
    width = _positive_int(getattr(item, 'width', None))
    height = _positive_int(getattr(item, 'height', None))
    fps = _positive_float(getattr(item, 'fps', None))
    metadata_error = str(getattr(item, 'metadata_error', '') or '').strip()
    if status == MediaStatus.READY and metadata_error:
        status = MediaStatus.METADATA_ERROR
    imported_at = sidecar.imported_at or modified_at
    display = str(getattr(item, 'display_title', '') or '').strip() or source.name or path
    return MediaAsset(
        asset_id=asset_id,
        path=path,
        display_name=display,
        media_type=media_type,
        status=status,
        favorite=sidecar.favorite,
        tags=sidecar.tags,
        description=sidecar.description,
        collections=sidecar.collections,
        metadata=MediaMetadata(
            duration=duration,
            width=width,
            height=height,
            fps=fps,
            size_bytes=size,
            created_at=created_at,
            container=str(getattr(item, 'container', '') or ''),
            codec=str(getattr(item, 'codec', '') or ''),
            detail=metadata_error,
        ),
        imported_at=imported_at,
    )


def _positive_int(value: Any) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _positive_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def build_project_assets(project: Any, image_items: Iterable[Any], store: MediaSidecarStore | None = None) -> list[MediaAsset]:
    values: list[MediaAsset] = []
    for item in getattr(project, 'audios', ()):
        values.append(asset_from_item(item, MediaType.AUDIO, store))
    for item in image_items:
        values.append(asset_from_item(item, MediaType.PHOTO, store))
    for item in getattr(project, 'videos', ()):
        values.append(asset_from_item(item, MediaType.VIDEO, store))
    return values


def scan_folder(root: str | Path, cancel: threading.Event | None = None) -> Iterator[Path]:
    """Yield supported files recursively without following directory symlinks."""
    start = Path(root).expanduser()
    if not start.is_dir():
        return
    cancel = cancel or threading.Event()
    stack = [start]
    while stack and not cancel.is_set():
        current = stack.pop()
        try:
            entries = sorted(current.iterdir(), key=lambda p: p.name.casefold(), reverse=True)
        except (OSError, PermissionError):
            continue
        for entry in entries:
            if cancel.is_set():
                return
            try:
                if entry.is_symlink():
                    continue
                if entry.is_dir():
                    if entry.name.casefold() not in IGNORED_DIRECTORY_NAMES and not entry.name.startswith('.'):
                        stack.append(entry)
                elif entry.is_file() and entry.suffix.casefold() in SUPPORTED_EXTENSIONS:
                    yield entry
            except (OSError, PermissionError):
                continue


@dataclass(frozen=True)
class FolderScanResult:
    paths: tuple[str, ...]
    canceled: bool
    elapsed_seconds: float


def collect_folder_paths(root: str | Path, cancel: threading.Event | None = None) -> FolderScanResult:
    started = time.perf_counter()
    token = cancel or threading.Event()
    paths = tuple(str(path) for path in scan_folder(root, token))
    return FolderScanResult(paths=paths, canceled=token.is_set(), elapsed_seconds=time.perf_counter() - started)
