from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import textwrap

import pytest

from full_album_maker import render_queue_step10 as queue_module
from full_album_maker.editor_models import MediaAsset, ProjectDocument, SongInstance, TIMEBASE
from full_album_maker.render_center_model_step10 import (
    RenderJob,
    RenderJobState,
    RenderMetrics,
    build_render_snapshot,
    settings_from_preset,
)
from full_album_maker.render_queue_step10 import (
    RenderQueue,
    RenderQueueStore,
    job_from_dict,
    job_to_dict,
)


def _job(tmp_path: Path, name: str = "queue") -> RenderJob:
    doc = ProjectDocument.new_empty("Queue")
    source = tmp_path / f"{name}.wav"
    source.write_bytes(b"audio")
    audio = MediaAsset(
        kind="audio",
        locator=str(source),
        original_name=source.name,
        source_duration_tick=5 * TIMEBASE,
    )
    doc.media.append(audio)
    doc.playlist.entries.append(
        SongInstance(asset_id=audio.asset_id, display_title=name, source_out_tick=5 * TIMEBASE)
    )
    doc.validate()
    settings = settings_from_preset("youtube_1080p", filename=name, output_folder=str(tmp_path))
    return RenderJob(build_render_snapshot(doc), settings)


def _mark_ready(job: RenderJob) -> None:
    job.transition(RenderJobState.PREFLIGHTING)
    job.transition(RenderJobState.READY)


def test_job_roundtrip_preserves_snapshot_settings_state_and_sanitizes_logs(tmp_path: Path) -> None:
    job = _job(tmp_path)
    _mark_ready(job)
    job.log_lines = ["token=supersecret hello"]
    restored = job_from_dict(job_to_dict(job))
    assert restored.job_id == job.job_id
    assert restored.attempt_id == job.attempt_id
    assert restored.state == RenderJobState.READY
    assert restored.snapshot.snapshot_hash == job.snapshot.snapshot_hash
    assert restored.settings.signature() == job.settings.signature()
    assert "supersecret" not in "\n".join(restored.log_lines)


def test_queue_refuses_draft_and_only_accepts_real_ready_job(tmp_path: Path) -> None:
    store = RenderQueueStore(tmp_path / "queue.json")
    queue = RenderQueue(store)
    job = _job(tmp_path)
    with pytest.raises(ValueError, match="READY"):
        queue.enqueue(job)
    _mark_ready(job)
    queued = queue.enqueue(job)
    assert queued.state == RenderJobState.QUEUED
    assert queue.next_queued() is queued
    assert store.load()[0].state == RenderJobState.QUEUED


def test_restart_marks_active_attempt_interrupted_and_cleans_bound_stage(tmp_path: Path) -> None:
    store = RenderQueueStore(tmp_path / "queue.json")
    job = _job(tmp_path, "recover")
    _mark_ready(job)
    job.transition(RenderJobState.STARTING)
    job.transition(RenderJobState.RUNNING)
    stage = tmp_path / f".{job.settings.final_output.stem}.{job.attempt_id[:8]}.rendering.mp4"
    stage.write_bytes(b"partial")
    unrelated = tmp_path / ".unrelated.rendering.mp4"
    unrelated.write_bytes(b"leave-me")
    store.save([job])

    jobs, changed = store.recover()
    assert changed == (job.attempt_id,)
    assert jobs[0].state == RenderJobState.INTERRUPTED
    assert jobs[0].error_code == "INTERRUPTED_ON_RESTART"
    assert not stage.exists()
    assert unrelated.exists()
    assert store.load()[0].state == RenderJobState.INTERRUPTED


def test_queued_job_survives_restart_but_requires_executor_critical_preflight_later(tmp_path: Path) -> None:
    store = RenderQueueStore(tmp_path / "queue.json")
    job = _job(tmp_path, "queued")
    _mark_ready(job)
    job.transition(RenderJobState.QUEUED)
    store.save([job])
    jobs, changed = store.recover()
    assert changed == ()
    assert jobs[0].state == RenderJobState.QUEUED


def test_retry_creates_new_attempt_in_draft_and_cannot_queue_without_new_preflight(tmp_path: Path) -> None:
    store = RenderQueueStore(tmp_path / "queue.json")
    failed = _job(tmp_path, "failed")
    _mark_ready(failed)
    failed.transition(RenderJobState.STARTING)
    failed.transition(RenderJobState.FAILED)
    store.save([failed])
    queue = RenderQueue(store)
    retry = queue.retry(failed.job_id, failed.attempt_id)
    assert retry.job_id == failed.job_id
    assert retry.attempt_id != failed.attempt_id
    assert retry.state == RenderJobState.DRAFT
    with pytest.raises(ValueError, match="READY"):
        queue.enqueue(retry)


def test_single_active_slot_returns_no_next_job_while_an_attempt_is_running(tmp_path: Path) -> None:
    store = RenderQueueStore(tmp_path / "queue.json")
    first = _job(tmp_path, "first")
    second = _job(tmp_path, "second")
    _mark_ready(first)
    first.transition(RenderJobState.STARTING)
    first.transition(RenderJobState.RUNNING)
    _mark_ready(second)
    second.transition(RenderJobState.QUEUED)
    store.save([first, second])
    queue = RenderQueue(store)
    # Constructor recovery converts the stale RUNNING state to INTERRUPTED,
    # so this process can safely offer the queued item after recovery.
    assert queue.jobs[0].state == RenderJobState.INTERRUPTED
    assert queue.next_queued() is not None

    # A live active state inside the current process blocks dequeue.
    live = _job(tmp_path, "live")
    _mark_ready(live)
    live.transition(RenderJobState.STARTING)
    live.transition(RenderJobState.RUNNING)
    queue.jobs.append(live)
    assert queue.next_queued() is None


def test_corrupt_queue_store_fails_closed_instead_of_silently_dropping_history(tmp_path: Path) -> None:
    path = tmp_path / "queue.json"
    path.write_text("{broken", encoding="utf-8")
    store = RenderQueueStore(path)
    with pytest.raises(ValueError, match="rusak"):
        store.load()



def test_restart_marks_persisted_draft_attempt_interrupted_and_retryable(tmp_path: Path) -> None:
    store = RenderQueueStore(tmp_path / "queue.json")
    draft = _job(tmp_path, "draft-crash-window")
    # Production Render Now persists the attempt before the worker has had a
    # chance to advance DRAFT -> PREFLIGHTING. A crash in that short window
    # must not leave an unretryable DRAFT stranded forever.
    store.save([draft])

    queue = RenderQueue(store)

    assert len(queue.jobs) == 1
    recovered = queue.jobs[0]
    assert recovered.state == RenderJobState.INTERRUPTED
    assert recovered.error_code == "INTERRUPTED_ON_RESTART"
    retry = queue.retry(recovered.job_id, recovered.attempt_id)
    assert retry.state == RenderJobState.DRAFT
    assert retry.attempt_id != recovered.attempt_id


def test_history_trim_never_drops_unfinished_jobs(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(queue_module, "MAX_HISTORY", 3)
    store = RenderQueueStore(tmp_path / "queue.json")

    running = _job(tmp_path, "running-kept")
    _mark_ready(running)
    running.transition(RenderJobState.STARTING)
    running.transition(RenderJobState.RUNNING)

    queued = _job(tmp_path, "queued-kept")
    _mark_ready(queued)
    queued.transition(RenderJobState.QUEUED)

    terminals: list[RenderJob] = []
    for index in range(4):
        job = _job(tmp_path, f"done-{index}")
        _mark_ready(job)
        job.transition(RenderJobState.STARTING)
        job.transition(RenderJobState.RUNNING)
        job.transition(RenderJobState.FINALIZING)
        job.transition(RenderJobState.COMPLETED)
        terminals.append(job)

    # The active/queued attempts are older than several terminal jobs. Retention
    # must prune old terminal history, never unfinished work.
    store.save([running, queued, *terminals])
    loaded = store.load()

    assert running.attempt_id in {job.attempt_id for job in loaded}
    assert queued.attempt_id in {job.attempt_id for job in loaded}
    assert terminals[-1].attempt_id in {job.attempt_id for job in loaded}
    assert len(loaded) == 3


def test_queue_retention_can_exceed_limit_when_all_work_is_unfinished(
    tmp_path: Path,
    monkeypatch,
) -> None:
    monkeypatch.setattr(queue_module, "MAX_HISTORY", 2)
    store = RenderQueueStore(tmp_path / "queue.json")
    queue = RenderQueue(store)

    jobs = []
    for index in range(3):
        job = _job(tmp_path, f"pending-{index}")
        _mark_ready(job)
        queue.enqueue(job)
        jobs.append(job)

    assert len(queue.jobs) == 3
    assert len(store.load()) == 3
    assert {job.attempt_id for job in store.load()} == {
        job.attempt_id for job in jobs
    }



def test_startup_recovery_quarantines_corrupt_queue_without_dropping_bytes(
    tmp_path: Path,
) -> None:
    path = tmp_path / "queue_v1.json"
    original = b'{"format":"full-album-maker-render-queue","version":1,"jobs":['
    path.write_bytes(original)
    store = RenderQueueStore(path)

    queue = RenderQueue(store)

    assert queue.jobs == []
    assert queue.recovery_warning
    assert "dikarantina" in queue.recovery_warning
    assert queue.quarantined_path is not None
    assert queue.quarantined_path.is_file()
    assert queue.quarantined_path.read_bytes() == original
    assert not path.exists()

    fresh = _job(tmp_path, "fresh-after-quarantine")
    _mark_ready(fresh)
    queue.enqueue(fresh)
    assert path.is_file()
    assert store.load()[0].attempt_id == fresh.attempt_id
    assert queue.quarantined_path.read_bytes() == original


def test_malformed_job_entry_is_quarantined_instead_of_crashing_startup(
    tmp_path: Path,
) -> None:
    path = tmp_path / "queue_v1.json"
    path.write_text(
        '{"format":"full-album-maker-render-queue","version":1,'
        '"jobs":[{"job_id":"missing-required-fields"}]}',
        encoding="utf-8",
    )

    queue = RenderQueue(RenderQueueStore(path))

    assert queue.jobs == []
    assert queue.quarantined_path is not None
    assert queue.quarantined_path.exists()
    assert "dikarantina" in queue.recovery_warning


def test_failed_quarantine_blocks_persistence_to_preserve_original(
    tmp_path: Path,
    monkeypatch,
) -> None:
    path = tmp_path / "queue_v1.json"
    original = b"{broken"
    path.write_bytes(original)
    store = RenderQueueStore(path)

    monkeypatch.setattr(queue_module.os, "replace", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("rename denied")))
    monkeypatch.setattr(queue_module.shutil, "copy2", lambda *args, **kwargs: (_ for _ in ()).throw(OSError("copy denied")))

    queue = RenderQueue(store)

    assert queue.jobs == []
    assert store.persistence_blocked is True
    assert "dinonaktifkan" in queue.recovery_warning
    assert path.read_bytes() == original
    with pytest.raises(ValueError, match="dinonaktifkan"):
        store.save([])
    assert path.read_bytes() == original



def test_two_live_queues_merge_new_jobs_without_lost_update(tmp_path: Path) -> None:
    path = tmp_path / "queue_v1.json"
    first = RenderQueue(RenderQueueStore(path))
    second = RenderQueue(RenderQueueStore(path))
    try:
        job_a = _job(tmp_path, "instance-a")
        _mark_ready(job_a)
        first.enqueue(job_a)

        # second still has the stale empty list it loaded at startup.
        assert second.jobs == []
        job_b = _job(tmp_path, "instance-b")
        _mark_ready(job_b)
        second.enqueue(job_b)

        stored = RenderQueueStore(path).load()
        assert {_job.attempt_id for _job in stored} == {
            job_a.attempt_id,
            job_b.attempt_id,
        }
        assert len(stored) == 2
    finally:
        first.close()
        second.close()


def test_live_owner_is_not_false_recovered_or_stage_deleted(tmp_path: Path) -> None:
    path = tmp_path / "queue_v1.json"
    owner = RenderQueue(RenderQueueStore(path))
    observer = None
    replacement = None
    try:
        job = _job(tmp_path, "live-owner")
        _mark_ready(job)
        job.transition(RenderJobState.STARTING)
        job.transition(RenderJobState.RUNNING)
        stage = (
            tmp_path
            / f".{job.settings.final_output.stem}.{job.attempt_id[:8]}.fixture.rendering.mp4"
        )
        stage.write_bytes(b"live-ffmpeg-stage")
        owner.update(job)

        observer = RenderQueue(RenderQueueStore(path))
        persisted = next(
            item for item in observer.jobs if item.attempt_id == job.attempt_id
        )
        assert persisted.state == RenderJobState.RUNNING
        assert stage.read_bytes() == b"live-ffmpeg-stage"
        assert observer.store.session_alive(owner.store.session_id) is True

        owner.close()
        replacement = RenderQueue(RenderQueueStore(path))
        recovered = next(
            item for item in replacement.jobs if item.attempt_id == job.attempt_id
        )
        assert recovered.state == RenderJobState.INTERRUPTED
        assert recovered.error_code == "INTERRUPTED_ON_RESTART"
        assert not stage.exists()
    finally:
        owner.close()
        if observer is not None:
            observer.close()
        if replacement is not None:
            replacement.close()


def test_queued_attempt_claim_is_atomic_across_live_instances(tmp_path: Path) -> None:
    path = tmp_path / "queue_v1.json"
    first = RenderQueue(RenderQueueStore(path))
    second = RenderQueue(RenderQueueStore(path))
    try:
        job = _job(tmp_path, "shared-queued")
        _mark_ready(job)
        first.enqueue(job)

        claimed = first.claim_next_queued()
        assert claimed is not None
        assert claimed.attempt_id == job.attempt_id

        # The second instance sees the QUEUED state, but the live owner lease
        # makes the claim unavailable instead of starting the same job twice.
        assert second.claim_next_queued() is None

        first.close()
        reclaimed = second.claim_next_queued()
        assert reclaimed is not None
        assert reclaimed.attempt_id == job.attempt_id
    finally:
        first.close()
        second.close()


def test_stale_instance_cannot_overwrite_attempt_owned_by_live_process(
    tmp_path: Path,
) -> None:
    path = tmp_path / "queue_v1.json"
    owner = RenderQueue(RenderQueueStore(path))
    stale = RenderQueue(RenderQueueStore(path))
    try:
        job = _job(tmp_path, "owned-active")
        _mark_ready(job)
        job.transition(RenderJobState.STARTING)
        job.transition(RenderJobState.RUNNING)
        owner.update(job)

        stale.refresh()
        stale_copy = next(
            item for item in stale.jobs if item.attempt_id == job.attempt_id
        )
        stale_copy.metrics = RenderMetrics(percent=99.0)
        with pytest.raises(ValueError, match="dimiliki instance aplikasi lain"):
            stale.update(stale_copy)

        persisted = RenderQueueStore(path).load()[0]
        assert persisted.metrics.percent != 99.0
        assert persisted.state == RenderJobState.RUNNING
    finally:
        owner.close()
        stale.close()


def test_real_second_process_does_not_recover_live_queue_owner(tmp_path: Path) -> None:
    path = tmp_path / "queue_v1.json"
    repo_root = Path(__file__).resolve().parents[1]
    env = dict(os.environ)
    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(repo_root / "src") + (
        os.pathsep + current_pythonpath if current_pythonpath else ""
    )

    holder = textwrap.dedent(
        r"""
        import sys
        import time
        from pathlib import Path
        from full_album_maker.editor_models import MediaAsset, ProjectDocument, SongInstance, TIMEBASE
        from full_album_maker.render_center_model_step10 import RenderJob, RenderJobState, build_render_snapshot, settings_from_preset
        from full_album_maker.render_queue_step10 import RenderQueue, RenderQueueStore

        root = Path(sys.argv[1])
        store_path = Path(sys.argv[2])
        source = root / "process-owner.wav"
        source.write_bytes(b"audio")
        doc = ProjectDocument.new_empty("Process Owner")
        asset = MediaAsset(kind="audio", locator=str(source), original_name=source.name, source_duration_tick=5 * TIMEBASE)
        doc.media.append(asset)
        doc.playlist.entries.append(SongInstance(asset_id=asset.asset_id, display_title="owner", source_out_tick=5 * TIMEBASE))
        doc.validate()
        settings = settings_from_preset("youtube_1080p", filename="process-owner", output_folder=str(root))
        job = RenderJob(build_render_snapshot(doc), settings)
        job.transition(RenderJobState.PREFLIGHTING)
        job.transition(RenderJobState.READY)
        job.transition(RenderJobState.STARTING)
        job.transition(RenderJobState.RUNNING)
        stage = root / f".{settings.final_output.stem}.{job.attempt_id[:8]}.fixture.rendering.mp4"
        stage.write_bytes(b"LIVE")
        queue = RenderQueue(RenderQueueStore(store_path))
        queue.update(job)
        print(job.attempt_id, flush=True)
        time.sleep(30)
        """
    )
    process = subprocess.Popen(
        [sys.executable, "-c", holder, str(tmp_path), str(path)],
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    observer = None
    replacement = None
    try:
        assert process.stdout is not None
        attempt_id = process.stdout.readline().strip()
        assert attempt_id

        observer = RenderQueue(RenderQueueStore(path))
        live = next(item for item in observer.jobs if item.attempt_id == attempt_id)
        assert live.state == RenderJobState.RUNNING
        stage = next(tmp_path.glob(f".process-owner.{attempt_id[:8]}.*.rendering.mp4"))
        assert stage.read_bytes() == b"LIVE"

        process.terminate()
        process.wait(timeout=5)

        replacement = RenderQueue(RenderQueueStore(path))
        recovered = next(
            item for item in replacement.jobs if item.attempt_id == attempt_id
        )
        assert recovered.state == RenderJobState.INTERRUPTED
        assert not stage.exists()
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        if observer is not None:
            observer.close()
        if replacement is not None:
            replacement.close()
