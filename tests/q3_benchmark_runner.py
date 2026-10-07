from __future__ import annotations

import argparse
import json
from pathlib import Path
import statistics
import tempfile
import time

from full_album_maker.editor_models import MediaAsset, ProjectDocument, SongInstance, seconds_to_tick
from full_album_maker.s11_render_graph import S11FFmpegCompiler, windows_command_line_length
from full_album_maker.timeline_resolver import TimelineResolver


SONG_COUNT = 200
SONG_SECONDS = 54.0


def long_document(mode: str) -> ProjectDocument:
    doc = ProjectDocument.new_empty(f"Q3 benchmark {mode}")
    doc.canvas.width = 320
    doc.canvas.height = 240
    doc.playlist.mode = mode
    duration_tick = seconds_to_tick(SONG_SECONDS)
    for index in range(SONG_COUNT):
        locator = f"C:/Q3 Benchmark/Lagu {index + 1:03d}.wav"
        asset = MediaAsset(
            kind="audio",
            locator=locator,
            original_name=Path(locator).name,
            source_duration_tick=duration_tick,
        )
        doc.media.append(asset)
        doc.playlist.entries.append(
            SongInstance(
                asset_id=asset.asset_id,
                display_title=f"Lagu {index + 1:03d}",
                source_out_tick=duration_tick,
                free_start_tick=index * duration_tick if mode == "free" else None,
            )
        )
    doc.validate()
    return doc


def median_ms(callable_, *, warmup: int, samples: int, loops: int) -> float:
    for _ in range(warmup):
        callable_()
    values: list[float] = []
    for _ in range(samples):
        started = time.perf_counter()
        for _ in range(loops):
            callable_()
        values.append((time.perf_counter() - started) * 1000.0 / loops)
    return float(statistics.median(values))


def run() -> dict[str, object]:
    resolver = TimelineResolver()
    packed = long_document("packed")
    free = long_document("free")

    packed_resolve = median_ms(lambda: resolver.resolve(packed), warmup=2, samples=9, loops=8)
    free_resolve = median_ms(lambda: resolver.resolve(free), warmup=2, samples=9, loops=8)

    with tempfile.TemporaryDirectory(prefix="fam-q3-bench-") as raw:
        root = Path(raw)
        compiler = S11FFmpegCompiler("ffmpeg.exe")
        counter = {"packed": 0, "free": 0}

        def compile_mode(mode: str, document: ProjectDocument):
            counter[mode] += 1
            idx = counter[mode]
            return compiler.compile_video(
                document,
                root / f"{mode}-{idx}.mp4",
                root / f"work-{mode}-{idx}",
            )

        packed_compile = median_ms(lambda: compile_mode("packed", packed), warmup=1, samples=7, loops=2)
        free_compile = median_ms(lambda: compile_mode("free", free), warmup=1, samples=7, loops=2)
        packed_cmd = compile_mode("packed", packed)
        free_cmd = compile_mode("free", free)

    packed_resolved = resolver.resolve(packed)
    free_resolved = resolver.resolve(free)
    return {
        "song_count": SONG_COUNT,
        "song_seconds": SONG_SECONDS,
        "duration_seconds": packed_resolved.duration_tick / 240_000,
        "packed_resolve_ms": packed_resolve,
        "free_resolve_ms": free_resolve,
        "packed_compile_ms": packed_compile,
        "free_compile_ms": free_compile,
        "packed_command_chars": windows_command_line_length(packed_cmd.args),
        "free_command_chars": windows_command_line_length(free_cmd.args),
        "packed_errors": list(packed_resolved.errors),
        "free_errors": list(free_resolved.errors),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    ns = parser.parse_args()
    result = run()
    path = Path(ns.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
