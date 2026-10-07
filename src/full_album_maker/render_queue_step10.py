from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import shutil
import time
from typing import Iterable, Iterator
from uuid import uuid4

from .atomic_io import atomic_write_text
from .paths import data_dir
from .render_center_model_step10 import (
    RenderJob,
    RenderJobState,
    RenderMetrics,
    RenderSettings,
    RenderSnapshot,
)
from .render_executor_step10 import sanitize_render_log


QUEUE_FORMAT = "full-album-maker-render-queue"
QUEUE_VERSION = 1
MAX_HISTORY = 200
_LIVE_ACTIVE_STATES = {
    RenderJobState.PREFLIGHTING,
    RenderJobState.STARTING,
    RenderJobState.RUNNING,
    RenderJobState.PAUSED,
    RenderJobState.FINALIZING,
}
_RECOVER_AS_INTERRUPTED = {
    RenderJobState.DRAFT,
    *_LIVE_ACTIVE_STATES,
}
_TERMINAL_HISTORY_STATES = {
    RenderJobState.COMPLETED,
    RenderJobState.FAILED,
    RenderJobState.CANCELLED,
    RenderJobState.BLOCKED,
    RenderJobState.INTERRUPTED,
}

_QUEUE_LOCK_TIMEOUT_SECONDS = 2.0
_SESSION_LOCK_PREFIX = ".fam-queue-session-"


def _job_key(job: RenderJob) -> tuple[str, str]:
    return (job.job_id, job.attempt_id)


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
def _queue_file_lock(path: Path) -> Iterator[None]:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
    handle = os.fdopen(fd, "r+b", buffering=0)
    try:
        if os.fstat(handle.fileno()).st_size == 0:
            handle.write(b"0")
            handle.flush()
        deadline = time.monotonic() + _QUEUE_LOCK_TIMEOUT_SECONDS
        while not _lock_handle(handle):
            if time.monotonic() >= deadline:
                raise ValueError(
                    "Render Queue sedang dipersist oleh instance aplikasi lain. "
                    "Coba lagi sesaat."
                )
            time.sleep(0.02)
        try:
            yield
        finally:
            _unlock_handle(handle)
    finally:
        handle.close()


def _bounded_history(jobs: Iterable[RenderJob]) -> list[RenderJob]:
    """Trim terminal history without ever dropping unfinished work.

    MAX_HISTORY is a retention target for old terminal attempts, not permission
    to discard live/queued/retry work. If unfinished work alone exceeds the
    target, keep it all and temporarily exceed MAX_HISTORY.
    """
    values = list(jobs)
    if len(values) <= MAX_HISTORY:
        return values

    protected_indices = [
        index
        for index, job in enumerate(values)
        if job.state not in _TERMINAL_HISTORY_STATES
    ]
    remaining = max(0, MAX_HISTORY - len(protected_indices))
    terminal_indices = [
        index
        for index, job in enumerate(values)
        if job.state in _TERMINAL_HISTORY_STATES
    ]
    keep = set(protected_indices)
    if remaining:
        keep.update(terminal_indices[-remaining:])
    return [job for index, job in enumerate(values) if index in keep]


def _snapshot_to_dict(value: RenderSnapshot) -> dict:
    return {
        "project_id": value.project_id,
        "project_revision": value.project_revision,
        "content_signature": value.content_signature,
        "snapshot_hash": value.snapshot_hash,
        "project_json": value.project_json,
        "render_plan_json": value.render_plan_json,
        "duration_tick": value.duration_tick,
        "timebase": value.timebase,
    }


def _snapshot_from_dict(value: dict) -> RenderSnapshot:
    return RenderSnapshot(
        project_id=str(value["project_id"]),
        project_revision=int(value["project_revision"]),
        content_signature=str(value["content_signature"]),
        snapshot_hash=str(value["snapshot_hash"]),
        project_json=str(value["project_json"]),
        render_plan_json=str(value["render_plan_json"]),
        duration_tick=int(value["duration_tick"]),
        timebase=int(value["timebase"]),
    )


def _settings_from_dict(value: dict) -> RenderSettings:
    allowed = {
        "filename", "output_folder", "width", "height", "fps", "video_codec",
        "video_bitrate_bps", "audio_codec", "audio_bitrate_bps", "sample_rate",
        "hardware_mode", "container", "overwrite", "preset_id",
    }
    item = RenderSettings(**{key: value[key] for key in allowed if key in value})
    item.validate()
    return item


def job_to_dict(job: RenderJob) -> dict:
    job.metrics.validate()
    safe_logs: list[str] = []
    for line in job.log_lines[-500:]:
        safe = sanitize_render_log(line)
        if safe:
            safe_logs.append(safe)
    return {
        "job_id": job.job_id,
        "attempt_id": job.attempt_id,
        "state": job.state.value,
        "snapshot": _snapshot_to_dict(job.snapshot),
        "settings": job.settings.canonical_dict(),
        "metrics": asdict(job.metrics),
        "created_at": job.created_at,
        "started_at": job.started_at,
        "finished_at": job.finished_at,
        "error_code": sanitize_render_log(job.error_code, max_length=100),
        "error_message": sanitize_render_log(job.error_message),
        "verified_output": job.verified_output,
        "log_lines": safe_logs,
    }


def job_from_dict(value: dict) -> RenderJob:
    if not isinstance(value, dict):
        raise ValueError("Render job persistence tidak valid.")
    metrics_raw = value.get("metrics") or {}
    metrics = RenderMetrics(
        percent=float(metrics_raw.get("percent", 0.0)),
        rendered_seconds=float(metrics_raw.get("rendered_seconds", 0.0)),
        fps=None if metrics_raw.get("fps") is None else float(metrics_raw["fps"]),
        average_fps=None if metrics_raw.get("average_fps") is None else float(metrics_raw["average_fps"]),
        speed=None if metrics_raw.get("speed") is None else float(metrics_raw["speed"]),
        eta_seconds=None if metrics_raw.get("eta_seconds") is None else float(metrics_raw["eta_seconds"]),
    )
    metrics.validate()
    safe_logs: list[str] = []
    for line in (value.get("log_lines") or [])[-500:]:
        safe = sanitize_render_log(str(line))
        if safe:
            safe_logs.append(safe)
    return RenderJob(
        snapshot=_snapshot_from_dict(value["snapshot"]),
        settings=_settings_from_dict(value["settings"]),
        job_id=str(value["job_id"]),
        attempt_id=str(value["attempt_id"]),
        state=RenderJobState(str(value.get("state", RenderJobState.DRAFT.value))),
        metrics=metrics,
        created_at=str(value.get("created_at", "")),
        started_at=str(value.get("started_at", "")),
        finished_at=str(value.get("finished_at", "")),
        error_code=sanitize_render_log(str(value.get("error_code", "")), max_length=100),
        error_message=sanitize_render_log(str(value.get("error_message", ""))),
        verified_output=str(value.get("verified_output", "")),
        log_lines=safe_logs,
    )


class RenderQueueStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else data_dir() / "render" / "queue_v1.json"
        self.lock_path = self.path.with_name(f".{self.path.name}.lock")
        self.last_recovery_warning = ""
        self.quarantined_path: Path | None = None
        self.persistence_blocked = False
        self.session_id = ""
        self._session_handle = None
        self._session_path: Path | None = None

    def start_session(self) -> str:
        if self._session_handle is not None:
            return self.session_id
        self.session_id = uuid4().hex
        path = self.path.with_name(f"{_SESSION_LOCK_PREFIX}{self.session_id}.lock")
        path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o600)
        handle = os.fdopen(fd, "r+b", buffering=0)
        if os.fstat(handle.fileno()).st_size == 0:
            handle.write(b"0")
            handle.flush()
        handle.seek(0)
        if not _lock_handle(handle):
            handle.close()
            raise ValueError("Gagal memperoleh session lease Render Queue.")
        self._session_handle = handle
        self._session_path = path
        return self.session_id

    def close_session(self) -> None:
        handle = self._session_handle
        path = self._session_path
        self._session_handle = None
        self._session_path = None
        if handle is not None:
            _unlock_handle(handle)
            handle.close()
        if path is not None:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                pass

    def _owner_path(self, owner_session_id: str) -> Path:
        return self.path.with_name(f"{_SESSION_LOCK_PREFIX}{owner_session_id}.lock")

    def session_alive(self, owner_session_id: str) -> bool:
        owner = str(owner_session_id or "")
        if not owner:
            return False
        if owner == self.session_id and self._session_handle is not None:
            return True
        path = self._owner_path(owner)
        if not path.exists():
            return False
        try:
            fd = os.open(path, os.O_RDWR)
            handle = os.fdopen(fd, "r+b", buffering=0)
        except OSError:
            # Fail closed: an existing lease file that cannot be inspected must
            # not be treated as a dead owner and recovered destructively.
            return True
        try:
            handle.seek(0)
            if not _lock_handle(handle):
                return True
            _unlock_handle(handle)
        finally:
            handle.close()
        try:
            path.unlink(missing_ok=True)
        except OSError:
            pass
        return False

    def _load_records_unlocked(
        self,
    ) -> tuple[list[RenderJob], dict[tuple[str, str], str]]:
        if not self.path.exists():
            return [], {}
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Render queue store rusak/tidak dapat dibaca: {exc}") from exc
        if not isinstance(raw, dict) or raw.get("format") != QUEUE_FORMAT or raw.get("version") != QUEUE_VERSION:
            raise ValueError("Versi render queue store tidak didukung.")
        values = raw.get("jobs", [])
        if not isinstance(values, list):
            raise ValueError("Daftar render job tidak valid.")
        jobs: list[RenderJob] = []
        owners: dict[tuple[str, str], str] = {}
        for index, item in enumerate(values):
            try:
                job = job_from_dict(item)
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(
                    f"Render job persistence rusak pada item #{index + 1}: {exc}"
                ) from exc
            jobs.append(job)
            owner = str(item.get("owner_session_id", "") or "")
            if owner:
                owners[_job_key(job)] = owner
        return jobs, owners

    def load(self) -> list[RenderJob]:
        jobs, _ = self._load_records_unlocked()
        return jobs

    def _write_records_unlocked(
        self,
        jobs: Iterable[RenderJob],
        owners: dict[tuple[str, str], str] | None = None,
    ) -> list[RenderJob]:
        if self.persistence_blocked:
            raise ValueError(
                "Persistence Render Queue dinonaktifkan karena store rusak "
                "belum berhasil dikarantina."
            )
        owners = owners or {}
        values = _bounded_history(jobs)
        serialized = []
        for job in values:
            item = job_to_dict(job)
            owner = str(owners.get(_job_key(job), "") or "")
            if owner:
                item["owner_session_id"] = owner
            serialized.append(item)
        payload = {
            "format": QUEUE_FORMAT,
            "version": QUEUE_VERSION,
            "jobs": serialized,
        }
        atomic_write_text(
            self.path,
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        return values

    def _quarantine_corrupt_store(self, reason: Exception) -> Path | None:
        if not self.path.exists():
            self.last_recovery_warning = (
                "Riwayat render tidak dapat dibaca, tetapi file sumber sudah tidak ada. "
                "Aplikasi dibuka dengan antrean baru."
            )
            return None

        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        quarantine = self.path.with_name(
            f"{self.path.stem}.corrupt-{timestamp}-{uuid4().hex[:8]}{self.path.suffix}"
        )
        quarantine.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.replace(self.path, quarantine)
        except OSError:
            try:
                shutil.copy2(self.path, quarantine)
            except OSError as backup_exc:
                self.persistence_blocked = True
                self.last_recovery_warning = (
                    "Riwayat render rusak dan tidak dapat dikarantina. "
                    "Aplikasi tetap dibuka, tetapi persistence Render Queue "
                    f"dinonaktifkan agar file asli tidak tertimpa ({backup_exc})."
                )
                return None
            try:
                self.path.unlink(missing_ok=True)
            except OSError:
                pass

        self.quarantined_path = quarantine
        self.last_recovery_warning = (
            "Riwayat Render Queue rusak dan telah dikarantina sebagai "
            f"{quarantine.name}. Aplikasi dibuka dengan antrean baru; "
            "file karantina dipertahankan untuk pemeriksaan/recovery manual."
        )
        return quarantine

    def save(self, jobs: Iterable[RenderJob]) -> None:
        """Compatibility full save used by focused tests/tools.

        Production RenderQueue uses merge_changes() so another live instance's
        disk-only jobs can never be dropped by a stale in-memory list.
        """
        with _queue_file_lock(self.lock_path):
            self._write_records_unlocked(jobs)

    @staticmethod
    def cleanup_orphan_stages(jobs: Iterable[RenderJob]) -> int:
        removed = 0
        seen: set[Path] = set()
        for job in jobs:
            final = job.settings.final_output
            folder = final.parent
            if not folder.is_dir():
                continue
            pattern = f".{final.stem}.{job.attempt_id[:8]}.*.rendering.mp4"
            for candidate in folder.glob(pattern):
                resolved = candidate.resolve(strict=False)
                if resolved in seen:
                    continue
                seen.add(resolved)
                try:
                    candidate.unlink(missing_ok=True)
                    removed += 1
                except OSError:
                    pass
        return removed

    def _recover_dead_owners_unlocked(
        self,
        jobs: list[RenderJob],
        owners: dict[tuple[str, str], str],
    ) -> tuple[tuple[str, ...], bool]:
        changed: list[str] = []
        dirty = False
        dead_jobs: list[RenderJob] = []
        for job in jobs:
            key = _job_key(job)
            owner = str(owners.get(key, "") or "")
            if job.state in _RECOVER_AS_INTERRUPTED:
                if owner and self.session_alive(owner):
                    continue
                job.state = RenderJobState.INTERRUPTED
                job.error_code = "INTERRUPTED_ON_RESTART"
                job.error_message = (
                    "Aplikasi pemilik attempt sudah tidak aktif; resume otomatis "
                    "tidak diklaim aman. Gunakan Retry untuk attempt baru."
                )
                if not job.finished_at:
                    from .render_center_model_step10 import utc_now_iso
                    job.finished_at = utc_now_iso()
                owners.pop(key, None)
                changed.append(job.attempt_id)
                dead_jobs.append(job)
                dirty = True
                continue
            if job.state == RenderJobState.QUEUED and owner and not self.session_alive(owner):
                # A process can die after atomically claiming a queued job but
                # before the worker changes state. Release that claim for another
                # live instance without falsely interrupting the queued work.
                owners.pop(key, None)
                dirty = True

        if dead_jobs and self.cleanup_orphan_stages(dead_jobs):
            dirty = True
        return tuple(changed), dirty

    def recover(self) -> tuple[list[RenderJob], tuple[str, ...]]:
        self.start_session()
        with _queue_file_lock(self.lock_path):
            jobs, owners = self._load_records_unlocked()
            changed, dirty = self._recover_dead_owners_unlocked(jobs, owners)
            if dirty:
                jobs = self._write_records_unlocked(jobs, owners)
            return jobs, changed

    def recover_for_startup(self) -> tuple[list[RenderJob], tuple[str, ...]]:
        """Recover only attempts whose owning process lease is provably dead."""
        self.start_session()
        with _queue_file_lock(self.lock_path):
            try:
                jobs, owners = self._load_records_unlocked()
            except ValueError as exc:
                self._quarantine_corrupt_store(exc)
                return [], ()
            changed, dirty = self._recover_dead_owners_unlocked(jobs, owners)
            if dirty:
                jobs = self._write_records_unlocked(jobs, owners)
            return jobs, changed

    def merge_changes(
        self,
        changes: Iterable[tuple[RenderJob, str]],
    ) -> list[RenderJob]:
        """Merge only locally changed attempts into the latest on-disk queue."""
        self.start_session()
        incoming = list(changes)
        with _queue_file_lock(self.lock_path):
            disk_jobs, owners = self._load_records_unlocked()
            index = {_job_key(job): pos for pos, job in enumerate(disk_jobs)}
            for job, requested_owner in incoming:
                key = _job_key(job)
                existing_owner = str(owners.get(key, "") or "")
                if (
                    existing_owner
                    and existing_owner != self.session_id
                    and self.session_alive(existing_owner)
                ):
                    raise ValueError(
                        "Attempt Render Queue sedang dimiliki instance aplikasi lain; "
                        "state lokal yang stale tidak boleh menimpanya."
                    )
                if key in index:
                    disk_jobs[index[key]] = job
                else:
                    index[key] = len(disk_jobs)
                    disk_jobs.append(job)
                owner = str(requested_owner or "")
                if owner:
                    owners[key] = owner
                else:
                    owners.pop(key, None)
            return self._write_records_unlocked(disk_jobs, owners)

    def claim_next_queued(
        self,
    ) -> tuple[list[RenderJob], RenderJob | None]:
        """Atomically claim one queued attempt so two instances cannot start it."""
        self.start_session()
        with _queue_file_lock(self.lock_path):
            jobs, owners = self._load_records_unlocked()
            _changed, dirty = self._recover_dead_owners_unlocked(jobs, owners)

            # A genuinely live active attempt anywhere in the shared queue owns
            # the global queue slot. Do not start another queued attempt.
            if any(job.state in _LIVE_ACTIVE_STATES for job in jobs):
                if dirty:
                    jobs = self._write_records_unlocked(jobs, owners)
                return jobs, None

            selected: RenderJob | None = None
            for job in jobs:
                if job.state != RenderJobState.QUEUED:
                    continue
                key = _job_key(job)
                owner = str(owners.get(key, "") or "")
                if owner and owner != self.session_id and self.session_alive(owner):
                    continue
                owners[key] = self.session_id
                selected = job
                dirty = True
                break

            if dirty:
                jobs = self._write_records_unlocked(jobs, owners)
            return jobs, selected


class RenderQueue:
    """Persistent shared queue with session-aware cross-process ownership."""

    def __init__(self, store: RenderQueueStore | None = None) -> None:
        self.store = store or RenderQueueStore()
        self.store.start_session()
        self.jobs, _ = self.store.recover_for_startup()
        self.recovery_warning = self.store.last_recovery_warning
        self.quarantined_path = self.store.quarantined_path

    def close(self) -> None:
        self.store.close_session()

    def enqueue(self, job: RenderJob) -> RenderJob:
        """Queue only a job that has already passed real preflight."""
        if job.state != RenderJobState.READY:
            raise ValueError("Job harus READY dari preflight nyata sebelum masuk queue.")
        if any(_job_key(item) == _job_key(job) for item in self.jobs):
            raise ValueError("Attempt render sudah ada di queue/history.")
        job.transition(RenderJobState.QUEUED)
        self.jobs = self.store.merge_changes([(job, "")])
        return job

    def next_queued(self) -> RenderJob | None:
        """In-memory inspection only; production dequeue uses claim_next_queued()."""
        if any(job.state in _LIVE_ACTIVE_STATES for job in self.jobs):
            return None
        return next(
            (job for job in self.jobs if job.state == RenderJobState.QUEUED),
            None,
        )

    def claim_next_queued(self) -> RenderJob | None:
        self.jobs, selected = self.store.claim_next_queued()
        return selected

    def update(self, job: RenderJob) -> None:
        # DRAFT Render Now / Retry preflight and live render states are owned by
        # this process. Terminal states relinquish ownership. QUEUED ownership is
        # assigned only by claim_next_queued(), never by a plain update.
        owner = (
            self.store.session_id
            if job.state in _RECOVER_AS_INTERRUPTED
            else ""
        )
        self.jobs = self.store.merge_changes([(job, owner)])

    def retry(self, job_id: str, attempt_id: str) -> RenderJob:
        # Refresh from disk first so retry cannot target history deleted/replaced
        # by another instance after this process opened.
        latest = self.store.load()
        self.jobs = latest
        source = next(
            (
                job
                for job in self.jobs
                if job.job_id == job_id and job.attempt_id == attempt_id
            ),
            None,
        )
        if source is None:
            raise ValueError("Render job/attempt tidak ditemukan.")
        retry = source.retry()
        # Retry is deliberately DRAFT: it must pass preflight again before
        # enqueue, because source/disk/encoder/output may have changed.
        self.jobs = self.store.merge_changes(
            [(retry, self.store.session_id)]
        )
        return retry

    def refresh(self) -> list[RenderJob]:
        self.jobs = self.store.load()
        return self.jobs

