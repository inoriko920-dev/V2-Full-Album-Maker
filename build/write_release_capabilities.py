from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
MANIFEST_PATH = REPO_ROOT / "build" / "release_manifest.json"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from full_album_maker import __version__


def _manifest() -> dict[str, object]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if int(data.get("schema_version", 0)) != 1:
        raise RuntimeError("release_manifest.json schema_version tidak didukung.")
    if data.get("target_stable_version") != __version__:
        raise RuntimeError(
            "Versi aplikasi tidak sama dengan target_stable_version release manifest: "
            f"{__version__} != {data.get('target_stable_version')}"
        )
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--output", default="CAPABILITIES.json")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    output = root / args.output
    manifest = _manifest()

    payload = {
        "format": "full-album-maker-capability-report",
        "version": 2,
        "app_version": __version__,
        "release_tag": f"v{__version__}",
        "build_commit": os.environ.get("GITHUB_SHA", "unknown"),
        "platform": manifest["platform"],
        "offline_manual_workflow": True,
        "api_key_required_for_manual_edit_preview_render": False,
        "global_python_required": False,
        "global_ffmpeg_required": False,
        "bundled": {
            "ffmpeg": manifest["ffmpeg"],
            "python_build": {
                "python": manifest["python"]["version"],
                "pip": manifest["python"]["pip"],
                **manifest["python_packages"],
            },
            "font": manifest["font"],
        },
        "artifact_contract": manifest["artifact"],
        "features": {
            "packed_timeline": "supported",
            "free_timeline_gap_silence": "supported",
            "free_timeline_explicit_crossfade": "supported",
            "spectrum_mixed_audio_parity": "supported",
            "circular_spectrum": "supported; showfreqs + bounded polar geq remap",
            "circular_spectrum_internal_side_max": 512,
            "ten_builtin_templates": "supported",
            "custom_templates": "supported",
            "bulk_song_cover_manager": "supported",
            "per_song_visual_image_video": "supported; photo motion + video loop/freeze + cut/fade/slide transitions",
            "ai_editor": "optional; requires configured provider key only for AI actions",
            "ai_editor_v14_parity": [
                "bulk cover assign/clear/auto-match",
                "song visual assign/clear/auto-match/style",
                "circular spectrum add/configure",
                "packed/free timeline mode",
                "free song start/crossfade timing",
            ],
            "ai_context_media_privacy": "stable IDs + safe basenames only; no locator/path/API key",
        },
        "q4_validation_contract": {
            "long_project_model": "200 songs x 54 seconds = 3 hours",
            "portable_zip_smoke": [
                "relocated Unicode/space/apostrophe path",
                "no global Python on PATH",
                "no global FFmpeg on PATH",
                "no Gemini/Google API key",
                "real bundled-FFmpeg A/V render",
                "ffprobe audio+video verification",
                "Qt Foundation production main-window construction",
            ],
            "windows_external_filter_script": "required",
        },
        "limitations": [
            "CI does not fully encode a three-hour album; it compile-stresses the 200-song/3-hour project and separately performs short real FFmpeg renders.",
            "Circular Spectrum bounds the expensive polar remap to at most 512x512 pixels before scaling to the requested layer box.",
            "User-selected custom font_path assets remain the user's responsibility; the portable build bundles Noto Sans as its deterministic fallback font asset.",
            "AI actions are unavailable without an API key, while manual editing/template/preview/render remain available offline.",
            "Gemini may translate user language into supported intents, but local exact-ID/query validation remains authoritative and ambiguous media is never guessed.",
        ],
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
