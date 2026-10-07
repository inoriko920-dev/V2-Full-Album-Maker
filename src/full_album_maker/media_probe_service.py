"""M5 normalized media-probe facade around current proven adapters."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, replace
import hashlib
import json
import math
import os
from pathlib import Path
from typing import Callable, Iterator, Mapping


DurationProbe = Callable[[str, str | None], float]
ImageProbe = Callable[[str], Mapping[str, object]]
AudioTagProbe = Callable[[str], tuple[str, str]]


def _canonical_locator(path: str | Path) -> str:
    source = Path(path).expanduser().resolve(strict=False)
    return os.path.normcase(str(source))


@dataclass(frozen=True, slots=True)
class SourceFingerprint:
    """Tiered source-version facts from D05-02.

    F0 = locator only, F1 = size+mtime, F2 = normalized semantic probe facts,
    F3 = optional full SHA-256. Expensive F3 hashing is never automatic.
    """

    locator: str
    size_bytes: int | None = None
    mtime_ns: int | None = None
    semantic_facts: tuple[tuple[str, str], ...] = ()
    full_sha256: str = ""
    device_id: int | None = None
    inode: int | None = None

    @classmethod
    def capture(cls, path: str | Path) -> "SourceFingerprint":
        locator = _canonical_locator(path)
        try:
            stat = Path(path).expanduser().stat()
            return cls(
                locator=locator,
                size_bytes=int(stat.st_size),
                mtime_ns=int(stat.st_mtime_ns),
                device_id=int(getattr(stat, "st_dev", 0) or 0) or None,
                inode=int(getattr(stat, "st_ino", 0) or 0) or None,
            )
        except OSError:
            return cls(locator=locator)

    @property
    def tier(self) -> str:
        if self.full_sha256:
            return "F3"
        if self.semantic_facts:
            return "F2"
        if self.size_bytes is not None and self.mtime_ns is not None:
            return "F1"
        return "F0"

    def same_source_version(self, other: "SourceFingerprint") -> bool:
        if not isinstance(other, SourceFingerprint):
            return False
        if self.locator != other.locator:
            return False
        if self.size_bytes != other.size_bytes or self.mtime_ns != other.mtime_ns:
            return False
        if (
            self.device_id is not None
            and other.device_id is not None
            and self.device_id != other.device_id
        ):
            return False
        if self.inode is not None and other.inode is not None and self.inode != other.inode:
            return False
        return True

    def matches_path(self, path: str | Path) -> bool:
        return self.same_source_version(SourceFingerprint.capture(path))

    def with_semantic(self, facts: Mapping[str, object]) -> "SourceFingerprint":
        normalized = tuple(
            sorted(
                (str(key), str(value))
                for key, value in facts.items()
                if value is not None and str(value) != ""
            )
        )
        return replace(self, semantic_facts=normalized)

    def cache_token(self, namespace_version: int = 1) -> str:
        payload = {
            "v": max(1, int(namespace_version)),
            "locator": self.locator,
            "size": self.size_bytes,
            "mtime_ns": self.mtime_ns,
            "semantic": self.semantic_facts,
            "sha256": self.full_sha256,
            "device_id": self.device_id,
            "inode": self.inode,
        }
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class MediaProbeResult:
    path: str
    media_kind: str
    duration_seconds: float | None
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    container: str = ""
    codec: str = ""
    title: str = ""
    artist: str = ""
    fingerprint: SourceFingerprint | None = None


def _default_duration_probe(path: str, media_kind: str | None) -> float:
    from .media import probe_duration

    return float(probe_duration(path, media_kind))


def _default_image_probe(path: str) -> Mapping[str, object]:
    # Lazy import avoids dragging the Qt-heavy legacy visual module into the
    # AppKernel just because the M5 service is wired.
    from .visual_feature import probe_image

    return probe_image(path)


def _default_audio_tag_probe(path: str) -> tuple[str, str]:
    from .visual_feature import probe_audio_tags

    return probe_audio_tags(path)


def _positive_int(value: object) -> int | None:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return None
    return number if number > 0 else None


def _positive_float(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) and number > 0 else None


class MediaProbeService:
    """Shared normalized probe boundary using current ffprobe/FFmpeg behavior."""

    def __init__(
        self,
        *,
        duration_probe: DurationProbe = _default_duration_probe,
        image_probe: ImageProbe = _default_image_probe,
        audio_tag_probe: AudioTagProbe = _default_audio_tag_probe,
    ) -> None:
        if not callable(duration_probe) or not callable(image_probe) or not callable(audio_tag_probe):
            raise TypeError("Adapter MediaProbeService harus callable.")
        self._duration_probe = duration_probe
        self._image_probe = image_probe
        self._audio_tag_probe = audio_tag_probe

    def probe(self, path: str | Path, media_kind: str) -> MediaProbeResult:
        source = str(Path(path).expanduser())
        kind = str(media_kind).strip().casefold()
        if kind == "image":
            kind = "photo"
        if kind not in {"audio", "video", "photo"}:
            raise ValueError(f"Jenis media tidak dikenal: {media_kind}")

        base = SourceFingerprint.capture(source)
        if base.size_bytes is None or base.mtime_ns is None:
            raise FileNotFoundError(f"Source media tidak tersedia: {Path(source).name}")
        duration: float | None = None
        width: int | None = None
        height: int | None = None
        title = ""
        artist = ""

        if kind == "photo":
            info = self._image_probe(source)
            width = _positive_int(info.get("width"))
            height = _positive_int(info.get("height"))
            duration = 0.0
        else:
            duration = _positive_float(self._duration_probe(source, kind))
            if duration is None:
                raise ValueError(f"Durasi media tidak valid: {Path(source).name}")
            if kind == "audio":
                title, artist = self._audio_tag_probe(source)
                title = str(title or "")
                artist = str(artist or "")

        after = SourceFingerprint.capture(source)
        if not base.same_source_version(after):
            raise RuntimeError(
                f"Source media berubah saat probe: {Path(source).name}"
            )
        fingerprint = after.with_semantic(
            {
                "kind": kind,
                "duration": "" if duration is None else f"{duration:.9f}",
                "width": width,
                "height": height,
            }
        )
        return MediaProbeResult(
            path=source,
            media_kind=kind,
            duration_seconds=duration,
            width=width,
            height=height,
            title=title,
            artist=artist,
            fingerprint=fingerprint,
        )


DEFAULT_MEDIA_PROBE_SERVICE = MediaProbeService()

_CURRENT_MEDIA_PROBE_SERVICE: ContextVar[MediaProbeService | None] = ContextVar(
    "full_album_maker_current_media_probe_service",
    default=None,
)


def current_media_probe_service() -> MediaProbeService | None:
    return _CURRENT_MEDIA_PROBE_SERVICE.get()


@contextmanager
def bind_media_probe_service(service: MediaProbeService) -> Iterator[MediaProbeService]:
    if not isinstance(service, MediaProbeService):
        raise TypeError("service harus MediaProbeService.")
    token = _CURRENT_MEDIA_PROBE_SERVICE.set(service)
    try:
        yield service
    finally:
        _CURRENT_MEDIA_PROBE_SERVICE.reset(token)


__all__ = [
    "DEFAULT_MEDIA_PROBE_SERVICE",
    "MediaProbeResult",
    "MediaProbeService",
    "SourceFingerprint",
    "bind_media_probe_service",
    "current_media_probe_service",
]
