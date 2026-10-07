from __future__ import annotations

import json
from pathlib import Path

import pytest

from full_album_maker.editor_models import MediaAsset, ProjectDocument, SongInstance, seconds_to_tick
from full_album_maker.render_service_v2 import EditorRenderService, RenderErrorV2


ROOT = Path(__file__).resolve().parents[1]


class _MaterializingRunner:
    def run(self, args, **kwargs) -> None:
        output = Path(list(args)[-1])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(b"FAKE-MP4")


def _minimal_render_doc(tmp_path: Path) -> ProjectDocument:
    source = tmp_path / "source.wav"
    source.write_bytes(b"not-decoded-by-fake-runner")
    document = ProjectDocument.new_empty("RC")
    asset = MediaAsset(
        kind="audio",
        locator=str(source),
        source_duration_tick=seconds_to_tick(0.25),
    )
    document.media.append(asset)
    document.playlist.entries.append(
        SongInstance(
            asset_id=asset.asset_id,
            source_out_tick=asset.source_duration_tick,
            display_title="RC Song",
        )
    )
    document.validate()
    return document


def test_render_service_appends_mp4_when_save_dialog_returns_no_suffix(tmp_path: Path):
    document = _minimal_render_doc(tmp_path)
    requested = tmp_path / "Album Final"

    result = EditorRenderService(
        ffmpeg="ffmpeg",
        runner=_MaterializingRunner(),
    ).render(document, str(requested))

    output = tmp_path / "Album Final.mp4"
    assert Path(result) == output.resolve()
    assert output.read_bytes() == b"FAKE-MP4"
    assert (tmp_path / "Album Final_YouTube_Chapter.txt").exists()
    assert (tmp_path / "Album Final_Tracklist.txt").exists()
    assert (tmp_path / "Album Final_Timeline_Final.json").exists()
    assert not requested.exists()


def test_render_service_rejects_misleading_non_mp4_suffix(tmp_path: Path):
    document = _minimal_render_doc(tmp_path)
    with pytest.raises(RenderErrorV2, match=r"\.mp4"):
        EditorRenderService(
            ffmpeg="ffmpeg",
            runner=_MaterializingRunner(),
        ).render(document, str(tmp_path / "Album Final.avi"))


def test_local_portable_build_uses_canonical_release_manifest_contract():
    script = (ROOT / "build" / "build_portable.ps1").read_text(encoding="utf-8")
    manifest = json.loads((ROOT / "build" / "release_manifest.json").read_text(encoding="utf-8"))

    assert manifest["schema_version"] == 1
    assert manifest["target_stable_version"] == "2.0.0"
    assert manifest["python"]["version"] == "3.12.10"
    assert manifest["python"]["pip"] == "26.2.1"

    ffmpeg = manifest["ffmpeg"]
    assert ffmpeg["release_tag"] == "autobuild-2026-10-03-18-14"
    assert ffmpeg["asset_name"] == "ffmpeg-N-127142-g12b7b9891b-win64-gpl.zip"
    assert ffmpeg["sha256"] == "a885f564dee2b60f69ab866c6c89b96ae531fc2ee1f24ff8b5b1a6d29960a96b"
    assert "/releases/download/latest/" not in ffmpeg["download_url"]

    required_fragments = (
        "build\\release_manifest.json",
        "target_stable_version",
        "Manifest.ffmpeg.download_url",
        "Manifest.ffmpeg.sha256",
        "Manifest.font.commit",
        "build/requirements-windows.lock",
        'python -m pip install "pip==$PipVersion"',
        "NotoSans.ttf",
        "write_release_capabilities.py",
        "--portable-smoke",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "Get-Command python",
        "Get-Command ffmpeg",
        "output_streams",
        "ChecksumFileName",
        "RELEASE_MANIFEST.json",
    )
    for fragment in required_fragments:
        assert fragment in script

    assert "/releases/download/latest/" not in script
    assert "pip install --upgrade pip" not in script
    assert "pip install -r requirements-dev.txt" not in script
    assert ffmpeg["download_url"] not in script
    assert ffmpeg["sha256"] not in script
