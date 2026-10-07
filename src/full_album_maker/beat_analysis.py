"""M6 deterministic BeatAnalysis service.

BeatAnalysis is derived/cacheable data only. It is deliberately separate from
authored BeatResponse behavior and never changes ProjectDocument timing or
master audio. The current FFmpeg Spectrum remains canonical.
"""

from __future__ import annotations

from array import array
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, replace
import hashlib
import json
import math
import os
from pathlib import Path
import statistics
import subprocess
import tempfile
from typing import Callable, Iterator, Sequence

from .app_errors import TaskCancelledError
from .cache_manager import CacheManager
from .media_probe_service import SourceFingerprint
from .paths import ffmpeg_path
from .task_lifecycle import TaskHandle, TaskSupervisor, TaskToken


ANALYSIS_FORMAT = "fam-beat-analysis"
ANALYZER_VERSION = "m6-v1"
DEFAULT_SAMPLE_HZ = 50
DEFAULT_MIN_INTERVAL_SECONDS = 0.18
DEFAULT_LOOKBACK_SECONDS = 0.24


class BeatAnalysisError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class BeatEvent:
    time_seconds: float
    strength: float

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.time_seconds)) or float(self.time_seconds) < 0:
            raise ValueError("BeatEvent time_seconds tidak valid.")
        if not math.isfinite(float(self.strength)) or not 0.0 <= float(self.strength) <= 1.0:
            raise ValueError("BeatEvent strength harus 0..1.")


@dataclass(frozen=True, slots=True)
class BeatAnalysisResult:
    source_path: str
    fingerprint_token: str
    sample_hz: int
    duration_seconds: float
    envelope: tuple[float, ...]
    beats: tuple[BeatEvent, ...]
    available: bool = True
    reason: str = ""
    cache_hit: bool = False
    analyzer_version: str = ANALYZER_VERSION

    @property
    def is_reactive(self) -> bool:
        return bool(self.available and self.beats)

    def as_cache_payload(self, *, cache_version: int) -> dict[str, object]:
        return {
            "format": ANALYSIS_FORMAT,
            "cache_version": int(cache_version),
            "analyzer_version": self.analyzer_version,
            "fingerprint_token": self.fingerprint_token,
            "sample_hz": int(self.sample_hz),
            "duration_seconds": round(float(self.duration_seconds), 6),
            "envelope": [round(float(value), 6) for value in self.envelope],
            "beats": [
                {
                    "time_seconds": round(float(event.time_seconds), 6),
                    "strength": round(float(event.strength), 6),
                }
                for event in self.beats
            ],
        }


EnvelopeDecoder = Callable[[Path, int, TaskToken | None], Sequence[float]]


def _unavailable(
    source: Path,
    fingerprint_token: str,
    sample_hz: int,
    reason: str,
) -> BeatAnalysisResult:
    return BeatAnalysisResult(
        source_path=str(source),
        fingerprint_token=str(fingerprint_token),
        sample_hz=max(1, int(sample_hz)),
        duration_seconds=0.0,
        envelope=(),
        beats=(),
        available=False,
        reason=str(reason or "Beat analysis tidak tersedia."),
    )


def _decode_envelope_ffmpeg(
    source: Path,
    sample_hz: int,
    token: TaskToken | None,
) -> tuple[float, ...]:
    """Decode a compact amplitude envelope without touching source/master audio.

    FFmpeg performs mono conversion, rectification, low-pass smoothing, and
    aggressive downsampling before bytes reach Python. At 50 Hz the derived
    stream is ~200 bytes/second, so analysis memory scales with low-rate derived
    samples rather than source PCM or video FPS.
    """

    tool = ffmpeg_path()
    if not tool:
        raise BeatAnalysisError("FFmpeg tidak ditemukan untuk Beat Analysis.")
    if token is not None:
        token.raise_if_cancelled()

    hz = max(20, min(200, int(sample_hz)))
    cutoff = max(4.0, min(18.0, hz * 0.24))
    filter_graph = (
        "aformat=sample_fmts=flt:channel_layouts=mono,"
        "aresample=8000,"
        "aeval=abs(val(0)),"
        f"lowpass=f={cutoff:.3f},"
        f"aresample={hz}"
    )
    command = [
        tool,
        "-nostdin",
        "-v",
        "error",
        "-i",
        str(source),
        "-map",
        "0:a:0",
        "-vn",
        "-sn",
        "-dn",
        "-af",
        filter_graph,
        "-f",
        "f32le",
        "-acodec",
        "pcm_f32le",
        "pipe:1",
    ]
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            check=False,
            timeout=300,
        )
    except subprocess.TimeoutExpired as exc:
        raise BeatAnalysisError("Beat Analysis melewati batas waktu FFmpeg.") from exc
    except OSError as exc:
        raise BeatAnalysisError(f"FFmpeg Beat Analysis gagal dijalankan: {exc}") from exc

    if token is not None:
        token.raise_if_cancelled()
    if proc.returncode != 0:
        detail = (proc.stderr or b"").decode("utf-8", errors="replace").strip()
        raise BeatAnalysisError(
            "FFmpeg tidak dapat mengekstrak envelope audio."
            + (f" {detail[:500]}" if detail else "")
        )

    raw = array("f")
    try:
        raw.frombytes(proc.stdout or b"")
    except (ValueError, EOFError) as exc:
        raise BeatAnalysisError("Envelope Beat Analysis tidak valid.") from exc
    return tuple(float(value) for value in raw)


def _normalized_envelope(values: Sequence[float]) -> tuple[float, ...]:
    clean: list[float] = []
    for raw in values:
        try:
            value = float(raw)
        except (TypeError, ValueError):
            value = 0.0
        if not math.isfinite(value) or value < 0.0:
            value = 0.0
        clean.append(value)

    if not clean:
        return ()
    peak = max(clean)
    if peak <= 1e-9:
        return tuple(0.0 for _ in clean)
    return tuple(round(min(1.0, value / peak), 6) for value in clean)


def detect_beats(
    envelope: Sequence[float],
    sample_hz: int,
    *,
    min_interval_seconds: float = DEFAULT_MIN_INTERVAL_SECONDS,
    lookback_seconds: float = DEFAULT_LOOKBACK_SECONDS,
) -> tuple[BeatEvent, ...]:
    """Pure deterministic transient detector over the derived envelope."""

    hz = max(1, int(sample_hz))
    values = _normalized_envelope(envelope)
    if len(values) < 3 or max(values, default=0.0) <= 1e-9:
        return ()

    lookback = max(2, int(round(hz * max(0.05, float(lookback_seconds)))))
    onset: list[float] = [0.0] * len(values)
    running = 0.0
    window: list[float] = []

    for index, value in enumerate(values):
        baseline = running / len(window) if window else 0.0
        onset[index] = max(0.0, value - baseline)
        window.append(value)
        running += value
        if len(window) > lookback:
            running -= window.pop(0)

    mean = statistics.fmean(onset)
    variance = statistics.fmean((value - mean) ** 2 for value in onset)
    threshold = max(0.06, mean + 1.15 * math.sqrt(max(0.0, variance)))
    candidates: list[tuple[int, float]] = []
    for index in range(1, len(onset) - 1):
        strength = onset[index]
        if (
            strength >= threshold
            and values[index] >= 0.12
            and strength >= onset[index - 1]
            and strength > onset[index + 1]
        ):
            candidates.append((index, strength))

    if not candidates:
        return ()

    min_gap = max(1, int(round(hz * max(0.08, float(min_interval_seconds)))))
    selected: list[tuple[int, float]] = []
    for index, strength in sorted(candidates, key=lambda item: (-item[1], item[0])):
        if all(abs(index - existing) >= min_gap for existing, _ in selected):
            selected.append((index, strength))

    max_strength = max(strength for _, strength in selected)
    return tuple(
        BeatEvent(
            time_seconds=round(index / hz, 6),
            strength=round(min(1.0, strength / max_strength), 6),
        )
        for index, strength in sorted(selected)
    )


class BeatAnalysisService:
    """AppKernel-owned M6 service for derived beat analysis.

    Async work is submitted through the existing M2 TaskSupervisor. This service
    creates no ThreadPoolExecutor and owns no independent Python worker pool.
    """

    def __init__(
        self,
        *,
        cache_manager: CacheManager,
        task_supervisor: TaskSupervisor,
        decoder: EnvelopeDecoder = _decode_envelope_ffmpeg,
        sample_hz: int = DEFAULT_SAMPLE_HZ,
    ) -> None:
        if not isinstance(cache_manager, CacheManager):
            raise TypeError("cache_manager harus CacheManager.")
        if not isinstance(task_supervisor, TaskSupervisor):
            raise TypeError("task_supervisor harus TaskSupervisor.")
        if not callable(decoder):
            raise TypeError("decoder BeatAnalysisService harus callable.")
        hz = int(sample_hz)
        if not 20 <= hz <= 200:
            raise ValueError("sample_hz Beat Analysis harus 20..200.")
        self.cache_manager = cache_manager
        self.task_supervisor = task_supervisor
        self.sample_hz = hz
        self._decoder = decoder
        self._scope = task_supervisor.get_or_create_scope("beat-analysis")

    @property
    def generation(self) -> int:
        return self._scope.generation

    def invalidate(self, reason: str = "Konteks Beat Analysis berubah.") -> int:
        return self._scope.invalidate(reason)

    def _cache_key(self, fingerprint: SourceFingerprint) -> tuple[str, str]:
        version = self.cache_manager.version("beat-analysis")
        fingerprint_token = fingerprint.cache_token(version)
        raw = (
            f"{ANALYZER_VERSION}|cache={version}|hz={self.sample_hz}|"
            f"min={DEFAULT_MIN_INTERVAL_SECONDS:.6f}|"
            f"lookback={DEFAULT_LOOKBACK_SECONDS:.6f}|{fingerprint_token}"
        ).encode("utf-8")
        return hashlib.sha256(raw).hexdigest(), fingerprint_token

    def cache_path(self, path: str | Path) -> Path:
        fingerprint = SourceFingerprint.capture(path)
        key, _token = self._cache_key(fingerprint)
        return self.cache_manager.root("beat-analysis") / f"{key}.json"

    def _load_cache(
        self,
        source: Path,
        cache_path: Path,
        fingerprint_token: str,
    ) -> BeatAnalysisResult | None:
        if not self.cache_manager.entry_usable(cache_path):
            return None
        try:
            payload = json.loads(cache_path.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("payload bukan object")
            if payload.get("format") != ANALYSIS_FORMAT:
                raise ValueError("format cache salah")
            if int(payload.get("cache_version", -1)) != self.cache_manager.version("beat-analysis"):
                raise ValueError("versi cache salah")
            if payload.get("analyzer_version") != ANALYZER_VERSION:
                raise ValueError("versi analyzer salah")
            if payload.get("fingerprint_token") != fingerprint_token:
                raise ValueError("fingerprint cache stale")
            if int(payload.get("sample_hz", -1)) != self.sample_hz:
                raise ValueError("sample_hz cache salah")

            raw_envelope = payload.get("envelope")
            raw_beats = payload.get("beats")
            if not isinstance(raw_envelope, list) or not isinstance(raw_beats, list):
                raise ValueError("isi cache tidak valid")
            envelope = _normalized_envelope(raw_envelope)
            beats = tuple(
                BeatEvent(
                    time_seconds=float(item["time_seconds"]),
                    strength=float(item["strength"]),
                )
                for item in raw_beats
                if isinstance(item, dict)
            )
            duration = float(payload.get("duration_seconds", 0.0))
            if not math.isfinite(duration) or duration < 0:
                raise ValueError("durasi cache tidak valid")
            return BeatAnalysisResult(
                source_path=str(source),
                fingerprint_token=fingerprint_token,
                sample_hz=self.sample_hz,
                duration_seconds=duration,
                envelope=envelope,
                beats=beats,
                available=True,
                cache_hit=True,
            )
        except (OSError, UnicodeError, json.JSONDecodeError, TypeError, ValueError, KeyError):
            self.cache_manager.evict("beat-analysis", cache_path)
            return None

    def _write_cache(self, cache_path: Path, result: BeatAnalysisResult) -> None:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        payload = result.as_cache_payload(
            cache_version=self.cache_manager.version("beat-analysis")
        )
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
        fd, temp_name = tempfile.mkstemp(
            prefix=cache_path.name + ".",
            suffix=".tmp",
            dir=str(cache_path.parent),
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, cache_path)
        finally:
            try:
                os.unlink(temp_name)
            except FileNotFoundError:
                pass
            except OSError:
                pass

    def analyze(
        self,
        path: str | Path,
        *,
        token: TaskToken | None = None,
    ) -> BeatAnalysisResult:
        source = Path(path).expanduser()
        if token is not None:
            token.raise_if_cancelled()

        fingerprint = SourceFingerprint.capture(source)
        key, fingerprint_token = self._cache_key(fingerprint)
        if fingerprint.tier == "F0" or not source.is_file():
            return _unavailable(
                source,
                fingerprint_token,
                self.sample_hz,
                "Source audio tidak ditemukan; fallback non-reactive digunakan.",
            )

        cache_path = self.cache_manager.root("beat-analysis") / f"{key}.json"
        cached = self._load_cache(source, cache_path, fingerprint_token)
        if cached is not None:
            return cached

        try:
            raw = self._decoder(source, self.sample_hz, token)
            if token is not None:
                token.raise_if_cancelled()
            envelope = _normalized_envelope(raw)
        except TaskCancelledError:
            raise
        except Exception as exc:
            return _unavailable(
                source,
                fingerprint_token,
                self.sample_hz,
                f"Beat Analysis tidak tersedia: {exc}",
            )

        # A changing source must never publish analysis under the old fingerprint.
        after = SourceFingerprint.capture(source)
        _after_key, after_token = self._cache_key(after)
        if after_token != fingerprint_token:
            return _unavailable(
                source,
                after_token,
                self.sample_hz,
                "Source berubah saat Beat Analysis; hasil lama diabaikan.",
            )

        beats = detect_beats(envelope, self.sample_hz)
        result = BeatAnalysisResult(
            source_path=str(source),
            fingerprint_token=fingerprint_token,
            sample_hz=self.sample_hz,
            duration_seconds=round(len(envelope) / self.sample_hz, 6),
            envelope=envelope,
            beats=beats,
            available=True,
        )
        try:
            self._write_cache(cache_path, result)
        except OSError:
            # Cache is disposable. A cache write failure must not invalidate a
            # valid derived analysis result or project state.
            pass
        return result

    def submit(
        self,
        path: str | Path,
        *,
        task_name: str = "",
    ) -> TaskHandle[BeatAnalysisResult]:
        source = str(Path(path).expanduser())
        return self.task_supervisor.submit(
            self._scope,
            lambda token: self.analyze(source, token=token),
            task_name=task_name or f"beat-analysis:{Path(source).name}",
        )


_CURRENT_BEAT_ANALYSIS_SERVICE: ContextVar[BeatAnalysisService | None] = ContextVar(
    "full_album_maker_current_beat_analysis_service",
    default=None,
)


def current_beat_analysis_service() -> BeatAnalysisService | None:
    return _CURRENT_BEAT_ANALYSIS_SERVICE.get()


@contextmanager
def bind_beat_analysis_service(
    service: BeatAnalysisService,
) -> Iterator[BeatAnalysisService]:
    if not isinstance(service, BeatAnalysisService):
        raise TypeError("service harus BeatAnalysisService.")
    token = _CURRENT_BEAT_ANALYSIS_SERVICE.set(service)
    try:
        yield service
    finally:
        _CURRENT_BEAT_ANALYSIS_SERVICE.reset(token)


__all__ = [
    "ANALYSIS_FORMAT",
    "ANALYZER_VERSION",
    "BeatAnalysisError",
    "BeatAnalysisResult",
    "BeatAnalysisService",
    "BeatEvent",
    "DEFAULT_SAMPLE_HZ",
    "bind_beat_analysis_service",
    "current_beat_analysis_service",
    "detect_beats",
]
