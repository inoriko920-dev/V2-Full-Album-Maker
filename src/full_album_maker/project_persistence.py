"""V2 project persistence facade introduced in migration M3.

This boundary wraps the existing proven project/recovery persistence behavior.
It does not own UI state, project editing, recent-project UX, or recovery prompts.
ProjectDocument remains the authoritative domain state.
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from enum import Enum
import json
import os
from pathlib import Path
import tempfile
import time
from typing import Any, Iterator

from .atomic_io import atomic_write_text
from .editor_models import ProjectDocument, ProjectSchemaError
from .integration_core_step11 import normalized_project_hash, project_token
from .integration_lifecycle_step11 import (
    AutosaveRequest,
    IntegrationRecoveryStore,
    RecoveryEnvelope,
    save_verified_legacy_project,
)
from .project_migrations import detect_project_payload, migrate_project_v1


_PROJECT_LOCK_TIMEOUT_SECONDS = 2.0


class ProjectPersistenceConflict(ValueError):
    """Raised when the canonical project changed after this session loaded it."""


def _lock_handle(handle) -> bool:
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


def _unlock_handle(handle) -> None:
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
def _project_file_lock(target: Path) -> Iterator[None]:
    lock_path = target.with_name(f".{target.name}.fam-project.lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    handle = os.fdopen(fd, "r+b", buffering=0)
    try:
        if os.fstat(handle.fileno()).st_size == 0:
            handle.write(b"0")
            handle.flush()
        deadline = time.monotonic() + _PROJECT_LOCK_TIMEOUT_SECONDS
        while not _lock_handle(handle):
            if time.monotonic() >= deadline:
                raise ProjectPersistenceConflict(
                    "File project sedang disimpan oleh instance aplikasi lain. "
                    "Coba lagi setelah proses simpan tersebut selesai."
                )
            time.sleep(0.02)
        try:
            yield
        finally:
            _unlock_handle(handle)
    finally:
        handle.close()


class RecoveryClassification(str, Enum):
    CORRUPT = "CORRUPT"
    STALE = "STALE"
    SAME = "SAME"
    NEWER = "NEWER"
    FOREIGN = "FOREIGN"


@dataclass(frozen=True, slots=True)
class RecoveryAssessment:
    classification: RecoveryClassification
    envelope: RecoveryEnvelope | None = None
    document: ProjectDocument | None = None
    detail: str = ""


class ProjectPersistence:
    """Single persistence facade for ProjectDocument save/load/recovery.

    Canonical Save contract:
    immutable ProjectDocument snapshot -> same-directory stage ->
    semantic read-back verification -> atomic os.replace publication.

    Compatibility-envelope save delegates to the already proven STEP11 writer,
    which implements the same stage/verify/publish contract.
    """

    def _target(self, path: str | Path) -> Path:
        target = Path(path)
        if target.suffix.lower() != ".json":
            target = target.with_suffix(".json")
        return target

    @staticmethod
    def _semantic_equal(left: ProjectDocument, right: ProjectDocument) -> bool:
        return normalized_project_hash(left) == normalized_project_hash(right)

    def load_document(
        self,
        path: str | Path,
        *,
        migrate_legacy: bool = True,
    ) -> ProjectDocument:
        source = Path(path)
        raw = json.loads(source.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ProjectSchemaError("File project bukan object JSON.")

        # STEP11 compatibility envelope may carry the authoritative v2 document
        # inside the legacy Project payload.
        embedded = raw.get("album_document_v2")
        if isinstance(embedded, dict):
            return ProjectDocument.from_dict(embedded)

        kind = detect_project_payload(raw)
        if kind == "project_v2":
            return ProjectDocument.from_dict(raw)
        if kind == "project_v1" and migrate_legacy:
            return migrate_project_v1(raw, name=source.stem)
        if kind == "project_v1":
            raise ProjectSchemaError("Project legacy membutuhkan migrasi eksplisit.")
        if kind == "timeline_v1":
            raise ProjectSchemaError(
                "File ini TimelinePlan v1, bukan file Project yang dapat dibuka langsung."
            )
        if kind == "future_project":
            raise ProjectSchemaError("Versi proyek lebih baru belum didukung.")
        raise ProjectSchemaError("Format file proyek tidak didukung.")

    def document_hash_on_disk(
        self,
        path: str | Path,
    ) -> str:
        target = self._target(path)
        if not target.is_file():
            return ""
        return normalized_project_hash(
            self.load_document(target, migrate_legacy=False)
        )

    def _assert_expected_disk_hash(
        self,
        target: Path,
        expected_disk_hash: str | None,
    ) -> None:
        if expected_disk_hash is None:
            return
        current = self.document_hash_on_disk(target)
        if str(current) != str(expected_disk_hash):
            raise ProjectPersistenceConflict(
                "Project di disk berubah sejak dibuka/disimpan oleh sesi ini. "
                "Simpan dibatalkan agar perubahan instance lain tidak tertimpa. "
                "Buka ulang project atau gunakan Save As ke file lain."
            )

    def verify_document(
        self,
        path: str | Path,
        expected: ProjectDocument,
    ) -> bool:
        expected_snapshot = expected.clone()
        expected_snapshot.validate()
        restored = self.load_document(path, migrate_legacy=False)
        return self._semantic_equal(restored, expected_snapshot)

    def save_document(
        self,
        path: str | Path,
        document: ProjectDocument,
        *,
        expected_disk_hash: str | None = None,
    ) -> str:
        """Publish a native ProjectDocument v2 with optional optimistic guard."""

        target = self._target(path)
        target.parent.mkdir(parents=True, exist_ok=True)

        snapshot = document.clone()
        snapshot.validate()
        payload = json.dumps(
            snapshot.to_dict(),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        ) + "\n"

        with _project_file_lock(target):
            self._assert_expected_disk_hash(target, expected_disk_hash)
            fd, stage_name = tempfile.mkstemp(
                prefix=f".{target.name}.",
                suffix=".stage.json",
                dir=str(target.parent),
            )
            os.close(fd)
            stage = Path(stage_name)
            try:
                atomic_write_text(stage, payload, encoding="utf-8")
                if not self.verify_document(stage, snapshot):
                    raise ValueError(
                        "Project staged tidak sama dengan ProjectDocument authoritative."
                    )
                os.replace(stage, target)
                return str(target)
            finally:
                stage.unlink(missing_ok=True)

    def save_compatibility(
        self,
        path: str | Path,
        legacy_project: Any,
        document: ProjectDocument,
        *,
        expected_disk_hash: str | None = None,
    ) -> str:
        """Publish compatibility envelope without overwriting external changes."""

        snapshot = document.clone()
        snapshot.validate()
        target = self._target(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        with _project_file_lock(target):
            self._assert_expected_disk_hash(target, expected_disk_hash)
            return save_verified_legacy_project(
                target,
                legacy_project,
                snapshot,
                verifier=self.verify_document,
            )

    def recovery_store(self, path: str | Path) -> IntegrationRecoveryStore:
        return IntegrationRecoveryStore(path)

    def write_recovery(
        self,
        path: str | Path,
        request: AutosaveRequest,
    ) -> RecoveryEnvelope:
        return self.recovery_store(path).write(request)

    def clear_recovery(self, path: str | Path) -> None:
        self.recovery_store(path).clear()

    def assess_recovery(
        self,
        path: str | Path,
        canonical_document: ProjectDocument,
        *,
        canonical_path: str | Path = "",
    ) -> RecoveryAssessment | None:
        """Classify one recovery candidate without mutating/deleting evidence."""

        store = self.recovery_store(path)
        if not store.path.is_file():
            return None

        canonical = canonical_document.clone()
        canonical.validate()

        try:
            envelope = store.load_strict()
            recovered = envelope.document()
        except Exception as exc:
            return RecoveryAssessment(
                RecoveryClassification.CORRUPT,
                detail=f"{type(exc).__name__}: {exc}",
            )

        expected_token = project_token(canonical, str(canonical_path or ""))
        if envelope.project_token != expected_token:
            return RecoveryAssessment(
                RecoveryClassification.FOREIGN,
                envelope=envelope,
                document=recovered,
                detail="Recovery project token tidak cocok dengan project aktif.",
            )

        if self._semantic_equal(recovered, canonical):
            return RecoveryAssessment(
                RecoveryClassification.SAME,
                envelope=envelope,
                document=recovered,
            )

        if envelope.revision < canonical.revision:
            return RecoveryAssessment(
                RecoveryClassification.STALE,
                envelope=envelope,
                document=recovered,
            )

        return RecoveryAssessment(
            RecoveryClassification.NEWER,
            envelope=envelope,
            document=recovered,
        )


DEFAULT_PROJECT_PERSISTENCE = ProjectPersistence()


__all__ = [
    "DEFAULT_PROJECT_PERSISTENCE",
    "ProjectPersistence",
    "ProjectPersistenceConflict",
    "RecoveryAssessment",
    "RecoveryClassification",
]
