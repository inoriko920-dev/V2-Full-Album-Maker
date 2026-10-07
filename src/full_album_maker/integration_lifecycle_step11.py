from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import tempfile
from typing import Callable
from uuid import uuid4

from .atomic_io import atomic_write_text
from .editor_models import ProjectDocument
from .integration_core_step11 import normalized_project_hash, project_token
from .paths import data_dir


RECOVERY_FORMAT = "full-album-maker-step11-recovery"
RECOVERY_VERSION = 1
_RECOVERY_SESSION_PREFIX = ".fam-recovery-session-"


def _session_lock_handle(handle) -> bool:
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


def _session_unlock_handle(handle) -> None:
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


class RecoverySessionLease:
    """OS-owned lease proving that one editor recovery session is still live."""

    def __init__(self, root: str | Path, session_id: str = "") -> None:
        self.root = Path(root)
        self.session_id = str(session_id or uuid4().hex)
        self.path = self.root / f"{_RECOVERY_SESSION_PREFIX}{self.session_id}.lock"
        self._handle = None

    def start(self) -> str:
        if self._handle is not None:
            return self.session_id
        self.root.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o600)
        handle = os.fdopen(fd, "r+b", buffering=0)
        if os.fstat(handle.fileno()).st_size == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if not _session_lock_handle(handle):
            handle.close()
            raise ValueError("Gagal memperoleh recovery session lease.")
        self._handle = handle
        return self.session_id

    def close(self) -> None:
        handle = self._handle
        self._handle = None
        if handle is not None:
            _session_unlock_handle(handle)
            handle.close()
        try:
            self.path.unlink(missing_ok=True)
        except OSError:
            pass

    def session_alive(self, session_id: str) -> bool:
        session_id = str(session_id or "")
        if not session_id:
            return False
        if session_id == self.session_id and self._handle is not None:
            return True
        path = self.root / f"{_RECOVERY_SESSION_PREFIX}{session_id}.lock"
        if not path.exists():
            return False
        try:
            fd = os.open(path, os.O_RDWR)
            handle = os.fdopen(fd, "r+b", buffering=0)
        except OSError:
            return True
        try:
            handle.seek(0)
            if not _session_lock_handle(handle):
                return True
            _session_unlock_handle(handle)
        finally:
            handle.close()
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        return False


def recovery_path_for_session(
    root: str | Path,
    project_token_value: str,
    session_id: str,
) -> Path:
    safe_token = "".join(
        ch for ch in str(project_token_value) if ch.isalnum() or ch in "-_"
    )[:64] or "unknown"
    safe_session = "".join(
        ch for ch in str(session_id) if ch.isalnum() or ch in "-_"
    )[:64] or "legacy"
    return Path(root) / f"{safe_token}.{safe_session}.json"


@dataclass(frozen=True)
class AutosaveRequest:
    generation: int
    project_token: str
    revision: int
    signature: str
    source_project_path: str
    document_payload: dict
    owner_session_id: str = ""

    def document(self) -> ProjectDocument:
        return ProjectDocument.from_dict(deepcopy(self.document_payload))


@dataclass(frozen=True)
class AutosaveStatus:
    latest_generation: int = 0
    latest_revision: int = 0
    latest_signature: str = ""
    last_success_generation: int = 0
    last_success_revision: int = 0
    last_success_signature: str = ""
    last_error: str = ""

    @property
    def pending(self) -> bool:
        return self.latest_generation > self.last_success_generation


@dataclass(frozen=True)
class RecoveryEnvelope:
    project_token: str
    revision: int
    signature: str
    source_project_path: str
    saved_at_utc: str
    document_payload: dict
    owner_session_id: str = ""

    def document(self) -> ProjectDocument:
        document = ProjectDocument.from_dict(deepcopy(self.document_payload))
        if document.revision != self.revision:
            raise ValueError("Revision recovery tidak cocok dengan payload ProjectDocument.")
        if normalized_project_hash(document) != self.signature:
            raise ValueError("Signature recovery tidak cocok dengan ProjectDocument.")
        return document

    def to_dict(self) -> dict:
        return {
            "format": RECOVERY_FORMAT,
            "version": RECOVERY_VERSION,
            "project_token": self.project_token,
            "revision": self.revision,
            "signature": self.signature,
            "source_project_path": self.source_project_path,
            "saved_at_utc": self.saved_at_utc,
            "owner_session_id": self.owner_session_id,
            "document": deepcopy(self.document_payload),
        }

    @classmethod
    def from_dict(cls, raw: object) -> "RecoveryEnvelope":
        if not isinstance(raw, dict):
            raise ValueError("Recovery envelope bukan object JSON.")
        if raw.get("format") != RECOVERY_FORMAT or int(raw.get("version", 0)) != RECOVERY_VERSION:
            raise ValueError("Format/versi recovery STEP11 tidak didukung.")
        document_payload = raw.get("document")
        if not isinstance(document_payload, dict):
            raise ValueError("Recovery tidak berisi ProjectDocument.")
        item = cls(
            project_token=str(raw.get("project_token", "")),
            revision=int(raw.get("revision", 0)),
            signature=str(raw.get("signature", "")),
            source_project_path=str(raw.get("source_project_path", "")),
            saved_at_utc=str(raw.get("saved_at_utc", "")),
            document_payload=deepcopy(document_payload),
            owner_session_id=str(raw.get("owner_session_id", "") or ""),
        )
        if not item.project_token or not item.signature:
            raise ValueError("Recovery tidak memiliki identity/signature.")
        item.document()
        return item


class IntegrationRecoveryStore:
    """Atomic STEP11 recovery file, intentionally separate from canonical project."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else data_dir() / "recovery" / "integration_autosave_v2.json"

    def write(self, request: AutosaveRequest) -> RecoveryEnvelope:
        document = request.document()
        envelope = RecoveryEnvelope(
            project_token=request.project_token,
            revision=request.revision,
            signature=request.signature,
            source_project_path=request.source_project_path,
            saved_at_utc=datetime.now(timezone.utc).isoformat(),
            document_payload=document.to_dict(),
            owner_session_id=request.owner_session_id,
        )
        # Revalidate exact serialized envelope before publishing.
        RecoveryEnvelope.from_dict(envelope.to_dict())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        atomic_write_text(
            self.path,
            json.dumps(envelope.to_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return envelope

    def discover(self) -> RecoveryEnvelope | None:
        if not self.path.is_file():
            return None
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return RecoveryEnvelope.from_dict(raw)
        except Exception:
            return None

    def load_strict(self) -> RecoveryEnvelope:
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        return RecoveryEnvelope.from_dict(raw)

    def clear(self) -> None:
        self.path.unlink(missing_ok=True)


class DebouncedAutosaveCoordinator:
    """Pure generation/coalescing state for UI timer + background writer.

    `request()` captures an immutable committed revision. A UI-level debounce timer
    later calls `take_pending()`. The returned request can be written on a worker.
    `complete()` ignores stale generations for user-facing latest-success state.
    Autosave never marks canonical dirty state saved.
    """

    def __init__(self) -> None:
        self._generation = 0
        self._latest: AutosaveRequest | None = None
        self._status = AutosaveStatus()

    @property
    def status(self) -> AutosaveStatus:
        return self._status

    def request(
        self,
        document: ProjectDocument,
        *,
        project_path: str = "",
        token: str = "",
        owner_session_id: str = "",
    ) -> AutosaveRequest:
        snapshot = document.clone()
        snapshot.validate()
        self._generation += 1
        identity = token or project_token(snapshot, project_path)
        request = AutosaveRequest(
            generation=self._generation,
            project_token=identity,
            revision=snapshot.revision,
            signature=normalized_project_hash(snapshot),
            source_project_path=str(project_path or ""),
            document_payload=snapshot.to_dict(),
            owner_session_id=str(owner_session_id or ""),
        )
        self._latest = request
        self._status = AutosaveStatus(
            latest_generation=request.generation,
            latest_revision=request.revision,
            latest_signature=request.signature,
            last_success_generation=self._status.last_success_generation,
            last_success_revision=self._status.last_success_revision,
            last_success_signature=self._status.last_success_signature,
            last_error=self._status.last_error,
        )
        return request

    def take_pending(self) -> AutosaveRequest | None:
        request = self._latest
        self._latest = None
        return request

    def complete(self, request: AutosaveRequest, *, success: bool, error: str = "") -> AutosaveStatus:
        current = self._status
        # A stale worker may finish after a newer edit. Keep its file on disk as a
        # valid snapshot, but never claim the latest revision autosaved.
        is_latest = request.generation == current.latest_generation
        if success and is_latest:
            self._status = AutosaveStatus(
                latest_generation=current.latest_generation,
                latest_revision=current.latest_revision,
                latest_signature=current.latest_signature,
                last_success_generation=request.generation,
                last_success_revision=request.revision,
                last_success_signature=request.signature,
                last_error="",
            )
        elif not success and is_latest:
            self._status = AutosaveStatus(
                latest_generation=current.latest_generation,
                latest_revision=current.latest_revision,
                latest_signature=current.latest_signature,
                last_success_generation=current.last_success_generation,
                last_success_revision=current.last_success_revision,
                last_success_signature=current.last_success_signature,
                last_error=str(error or "Autosave gagal."),
            )
        return self._status


def request_from_document(
    document: ProjectDocument,
    *,
    project_path: str = "",
    generation: int = 1,
    owner_session_id: str = "",
) -> AutosaveRequest:
    """Deterministic helper for recovery tests/tools without coordinator state."""

    snapshot = document.clone()
    return AutosaveRequest(
        generation=int(generation),
        project_token=project_token(snapshot, project_path),
        revision=snapshot.revision,
        signature=normalized_project_hash(snapshot),
        source_project_path=str(project_path or ""),
        document_payload=snapshot.to_dict(),
        owner_session_id=str(owner_session_id or ""),
    )


def extract_project_document_from_saved_json(path: str | Path) -> ProjectDocument:
    """Understand both native ProjectDocument v2 and the legacy compatibility envelope."""

    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("File project bukan object JSON.")
    if raw.get("format") == "full-album-maker-project":
        return ProjectDocument.from_dict(raw)
    embedded = raw.get("album_document_v2")
    if isinstance(embedded, dict):
        return ProjectDocument.from_dict(embedded)
    raise ValueError("File project tidak membawa ProjectDocument authoritative.")


def verify_persisted_document(path: str | Path, expected: ProjectDocument) -> bool:
    restored = extract_project_document_from_saved_json(path)
    return normalized_project_hash(restored) == normalized_project_hash(expected)


def save_verified_legacy_project(
    path: str | Path,
    project,
    expected: ProjectDocument,
    *,
    verifier: Callable[[str | Path, ProjectDocument], bool] = verify_persisted_document,
) -> str:
    """Stage, semantically verify, then atomically publish a legacy project envelope.

    The canonical target is never touched until the staged JSON has been parsed
    back into the authoritative ProjectDocument and its normalized hash matches
    the expected document. Stage and target live in the same directory so
    os.replace is an atomic same-filesystem publish.
    """

    target = Path(path)
    if target.suffix.lower() != ".json":
        target = target.with_suffix(".json")
    target.parent.mkdir(parents=True, exist_ok=True)

    fd, stage_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".stage.json",
        dir=str(target.parent),
    )
    os.close(fd)
    stage = Path(stage_name)
    try:
        payload = json.dumps(project.to_dict(), ensure_ascii=False, indent=2)
        atomic_write_text(stage, payload, encoding="utf-8")
        if not verifier(stage, expected):
            raise ValueError(
                "Project staged tidak sama dengan ProjectDocument authoritative."
            )
        os.replace(stage, target)
        return str(target)
    finally:
        stage.unlink(missing_ok=True)
