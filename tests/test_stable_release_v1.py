from __future__ import annotations

import json
import re
from pathlib import Path
import subprocess
import sys
import tomllib

from full_album_maker import __version__
from full_album_maker.project_dirty import _update_window_title


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((ROOT / "build" / "release_manifest.json").read_text(encoding="utf-8"))
CHECKOUT_SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"
SETUP_PYTHON_SHA = "5fda3b95a4ea91299a34e894583c3862153e4b97"
UPLOAD_ARTIFACT_SHA = "043fb46d1a93c77aae656e7c1c64a875d1fc6a0a"


def test_stable_version_is_consistent_across_package_metadata():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    parts = __version__.split(".")
    assert len(parts) == 3 and all(part.isdigit() for part in parts)
    assert __version__ == MANIFEST["target_stable_version"]
    assert pyproject["project"]["version"] == __version__
    notes = ROOT / f"docs/RELEASE_NOTES_v{__version__}.md"
    assert notes.exists()
    text = notes.read_text(encoding="utf-8")
    assert f"Full-Album-Maker-v{__version__}-Windows-Portable.zip" in text
    # Current stable requires the independent no-rebuild Q5 evidence.
    if __version__ == "2.0.4":
        assert "Status: **Stable — Q5 Release Quality Gate PASS**" in text
        assert "Q4 and Q5 PASS" in text
        assert "af5af1ce24aba17ff68d469390a0c3d21f80f44d" in text
        assert "888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b" in text
        evidence = (ROOT / "docs/implementation/Q5_V2_0_4_EVIDENCE.md").read_text(encoding="utf-8")
        assert "Status: **PASS — Stable v2.0.4 PUBLISHED**" in evidence
        assert "exact_zip_rebuilt = false" in evidence
        assert "published_asset_redownload_verified = true" in evidence
        assert "406580160" in evidence
    # Require real Q5 audit proof for the published v2.0.3 stable.
    elif __version__ == "2.0.3":
        assert "Status: **Stable — Q5 Release Quality Gate PASS**" in text
        assert "Q4 and Q5 PASS" in text
        assert "ee61ca0af5d15cdc51af91ad48e05bc2b641f49d" in text
        assert "b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0" in text
        evidence = (ROOT / "docs/implementation/Q5_V2_0_3_EVIDENCE.md").read_text(encoding="utf-8")
        assert "Status: **PASS — Stable v2.0.3 PUBLISHED**" in evidence
        assert "exact_zip_rebuilt = false" in evidence
        assert "published_asset_redownload_verified = true" in evidence
        assert "406491420" in evidence
    else:
        assert "Status: **Stable" in text



def test_published_v203_identity_remains_immutable_while_preparing_patch():
    notes = (ROOT / "docs/RELEASE_NOTES_v2.0.3.md").read_text(encoding="utf-8")
    assert "Status: **Stable — Q5 Release Quality Gate PASS**" in notes
    assert "Q4 and Q5 PASS" in notes
    assert "ee61ca0af5d15cdc51af91ad48e05bc2b641f49d" in notes
    assert "b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0" in notes
    evidence = (ROOT / "docs/implementation/Q5_V2_0_3_EVIDENCE.md").read_text(encoding="utf-8")
    assert "Status: **PASS — Stable v2.0.3 PUBLISHED**" in evidence
    assert "exact_zip_rebuilt = false" in evidence
    assert "published_asset_redownload_verified = true" in evidence
    assert "406491420" in evidence


def test_published_v202_identity_remains_immutable_while_preparing_patch():
    notes = (ROOT / "docs/RELEASE_NOTES_v2.0.2.md").read_text(encoding="utf-8")
    assert "Status: **Stable — Q5 Release Quality Gate PASS**" in notes
    assert "Q4 and Q5 PASS" in notes
    assert "2678b9f93364334c7eaf9ebad9ef7e079533716f" in notes
    assert "701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64" in notes
    evidence = (ROOT / "docs/implementation/Q5_V2_0_2_EVIDENCE.md").read_text(encoding="utf-8")
    assert "Status: **PASS — Stable v2.0.2 PUBLISHED**" in evidence
    assert "exact_zip_rebuilt = false" in evidence
    assert "published_asset_redownload_verified = true" in evidence
    assert "406458763" in evidence


def test_published_v201_identity_remains_immutable_while_preparing_patch():
    notes = (ROOT / "docs/RELEASE_NOTES_v2.0.1.md").read_text(encoding="utf-8")
    assert "Status: **Stable — Q5 Release Quality Gate PASS**" in notes
    assert "Q4 and Q5 PASS" in notes
    assert "35a8c195469d49d7f7938b31761ceb17c4c720e0" in notes
    assert "6c97461ee3472973fc9b7950952287ae5aab9ffe2dffbe6a1fb0c236353d4a5d" in notes
    evidence = (ROOT / "docs/implementation/Q5_V2_0_1_EVIDENCE.md").read_text(encoding="utf-8")
    assert "Status: **PASS — Stable v2.0.1 PUBLISHED**" in evidence
    assert "exact_zip_rebuilt = false" in evidence
    assert "published_asset_redownload_verified = true" in evidence


def test_published_v200_identity_remains_immutable_while_preparing_patch():
    notes = (ROOT / "docs/RELEASE_NOTES_v2.0.0.md").read_text(encoding="utf-8")
    assert "Status: **Stable" in notes
    assert "Q5 Release Quality Gate PASS" in notes
    assert "Full-Album-Maker-v2.0.0-Windows-Portable.zip" in notes
    assert "4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad" in notes
    assert "d2ce2ccac62cdcd8994a38251a5b547c8460421e" in notes


def test_window_title_exposes_stable_version():
    class DummyWindow:
        _current_project_path = ""

        def is_project_dirty(self) -> bool:
            return False

        def setWindowTitle(self, value: str) -> None:
            self.title = value

    window = DummyWindow()
    _update_window_title(window)
    assert window.title == f"Full Album Maker v{__version__}"


def test_capability_report_records_release_identity_and_manifest_pins(tmp_path: Path):
    subprocess.run(
        [
            sys.executable,
            str(ROOT / "build" / "write_release_capabilities.py"),
            "--root",
            str(tmp_path),
        ],
        cwd=ROOT,
        check=True,
    )
    payload = json.loads((tmp_path / "CAPABILITIES.json").read_text(encoding="utf-8"))
    assert payload["app_version"] == __version__
    assert payload["release_tag"] == f"v{__version__}"
    assert payload["platform"] == MANIFEST["platform"]
    assert payload["bundled"]["ffmpeg"] == MANIFEST["ffmpeg"]
    assert payload["bundled"]["font"] == MANIFEST["font"]
    assert payload["bundled"]["python_build"]["python"] == MANIFEST["python"]["version"]
    assert payload["bundled"]["python_build"]["pip"] == MANIFEST["python"]["pip"]
    assert payload["artifact_contract"] == MANIFEST["artifact"]


def test_build_workflow_validates_only_and_cannot_auto_publish_stable():
    workflow = (ROOT / ".github" / "workflows" / "build-windows-portable.yml").read_text(
        encoding="utf-8"
    )
    local_build = (ROOT / "build" / "build_portable.ps1").read_text(encoding="utf-8")
    q4 = (ROOT / ".github" / "workflows" / "v2-q4-windows-artifact.yml").read_text(
        encoding="utf-8"
    )

    assert "contents: read" in workflow
    assert "contents: write" not in workflow
    assert "gh release create" not in workflow
    assert "Publish stable GitHub Release" not in workflow
    assert "build/release_manifest.json" in workflow
    assert "Build and smoke exact Windows portable candidate" in workflow
    assert "upload-artifact" in workflow

    assert f"actions/checkout@{CHECKOUT_SHA}" in workflow
    assert f"actions/setup-python@{SETUP_PYTHON_SHA}" in workflow
    assert f"actions/upload-artifact@{UPLOAD_ARTIFACT_SHA}" in workflow

    assert "build\\release_manifest.json" in local_build
    assert "Full Album Maker.exe" in local_build
    assert "--portable-smoke" in local_build
    assert "ChecksumFileName" in local_build
    assert "RELEASE_MANIFEST.json" in local_build

    assert "quality-q4-windows-artifact" in q4
    assert "test_real_ffmpeg_accepts_external_filter_script" in q4
    assert "publication_performed" in q4
    assert '"publication_performed": False' in q4
    assert not re.search(r"(?m)^\\s*gh release create\\b", q4)


def test_notice_provenance_matches_canonical_manifest():
    notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    ffmpeg = MANIFEST["ffmpeg"]
    for value in (
        ffmpeg["provider"],
        ffmpeg["release_tag"],
        ffmpeg["asset_name"],
        ffmpeg["sha256"],
        str(ffmpeg["release_id"]),
        str(ffmpeg["asset_id"]),
    ):
        assert str(value) in notices

    assert MANIFEST["font"]["commit"] in notices
    assert MANIFEST["python_packages"]["PySide6"] in notices
