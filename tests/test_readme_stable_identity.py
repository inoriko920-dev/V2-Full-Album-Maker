"""Prevent the public README from drifting from the verified Q5 release."""

import re
from pathlib import Path

import pytest

from full_album_maker import __version__ as CURRENT_VERSION

# README must match the Q5-verified published stable, not an earlier candidate.
PUBLISHED_STABLE = "2.0.4"


ROOT = Path(__file__).resolve().parents[1]


def _capture(text: str, pattern: str, field: str) -> str:
    match = re.search(pattern, text, flags=re.MULTILINE)
    assert match is not None, f"Missing or malformed {field}"
    return match.group(1)


def _table_code(text: str, label: str) -> str:
    return _capture(
        text,
        rf"^\|\s*{re.escape(label)}\s*\|\s*`([^`\r\n]+)`\s*\|\s*$",
        label,
    )


def _verify_exact_published_identity(readme: str, notes: str, evidence: str) -> None:
    """Match the three *named* release fields, never an arbitrary common hash."""
    q5_sha = _table_code(evidence, "Exact portable ZIP SHA-256")
    readme_sha = _table_code(readme, "SHA-256")
    notes_sha = _capture(notes, r"^- ZIP SHA-256:\s*`([0-9a-f]{64})`\s*\.?$", "release notes ZIP SHA-256")
    assert re.fullmatch(r"[0-9a-f]{64}", q5_sha), "Invalid Q5 ZIP SHA-256"
    assert readme_sha == notes_sha == q5_sha, "Published portable ZIP SHA-256 does not match Q5"

    q5_bytes = _table_code(evidence, "Exact ZIP bytes")
    readme_bytes = _capture(
        readme, r"^\|\s*Ukuran\s*\|\s*\*\*([0-9.]+) byte\*\*\s*\|\s*$",
        "README ZIP size",
    ).replace(".", "")
    notes_bytes = _capture(
        notes, r"^- ZIP size:\s*\*\*(\d+) bytes\*\*\.?$", "release notes ZIP size",
    )
    assert q5_bytes.isdecimal(), "Invalid Q5 ZIP size"
    assert readme_bytes == notes_bytes == q5_bytes, "Published ZIP byte size does not match Q5"

    q5_commit = _table_code(evidence, "Exact Q4 candidate source and tag commit")
    readme_commit = _table_code(readme, "Commit sumber rilis")
    notes_commit = _capture(
        notes,
        rf"^- Tag: `v{re.escape(PUBLISHED_STABLE)}`, targets exact Q4 source commit `([0-9a-f]{{40}})`\.$",
        "release notes Q4 commit",
    )
    assert re.fullmatch(r"[0-9a-f]{40}", q5_commit), "Invalid Q5 source commit"
    assert readme_commit == notes_commit == q5_commit, "Published tag commit does not match Q5"
    assert _table_code(evidence, "Stable version and tag") == f"v{PUBLISHED_STABLE}"


def _release_documents() -> tuple[str, str, str]:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    notes = ROOT / f"docs/RELEASE_NOTES_v{PUBLISHED_STABLE}.md"
    evidence = ROOT / f"docs/implementation/Q5_V{PUBLISHED_STABLE.replace('.', '_')}_EVIDENCE.md"
    assert notes.is_file(), "Published version release notes are missing"
    assert evidence.is_file(), "Published version Q5 evidence is missing"
    return readme, notes.read_text(encoding="utf-8"), evidence.read_text(encoding="utf-8")


def test_readme_describes_current_stable_download_and_checksum() -> None:
    readme, notes, evidence = _release_documents()
    assert "Status: **Stable — Q5 Release Quality Gate PASS**" in notes
    assert "Q4 and Q5 PASS" in notes
    assert "published_asset_redownload_verified = true" in evidence
    assert "exact_zip_rebuilt = false" in evidence

    filename = f"Full-Album-Maker-v{PUBLISHED_STABLE}-Windows-Portable.zip"
    assert f"Full Album Maker v{PUBLISHED_STABLE}" in readme
    assert f"releases/download/v{PUBLISHED_STABLE}/{filename}" in readme
    assert f"releases/download/v{PUBLISHED_STABLE}/SHA256SUMS.txt" in readme
    assert f"docs/RELEASE_NOTES_v{PUBLISHED_STABLE}.md" in readme
    _verify_exact_published_identity(readme, notes, evidence)
    assert "Repository asli" in readme
    assert "Source code asli belum sepenuhnya dipulihkan" not in readme


def test_unrelated_hash_cannot_hide_wrong_public_zip_checksum() -> None:
    readme, notes, evidence = _release_documents()
    published_sha = _table_code(readme, "SHA-256")
    bad_readme = readme.replace(
        f"| SHA-256 | `{published_sha}` |", f"| SHA-256 | `{'0' * 64}` |",
    )
    assert bad_readme != readme
    with pytest.raises(AssertionError, match="Published portable ZIP SHA-256"):
        _verify_exact_published_identity(bad_readme, notes, evidence)


def test_wrong_release_commit_is_rejected() -> None:
    readme, notes, evidence = _release_documents()
    published_commit = _table_code(readme, "Commit sumber rilis")
    bad_readme = readme.replace(
        f"| Commit sumber rilis | `{published_commit}` |",
        f"| Commit sumber rilis | `{'0' * 40}` |",
    )
    assert bad_readme != readme
    with pytest.raises(AssertionError, match="Published tag commit"):
        _verify_exact_published_identity(bad_readme, notes, evidence)



def test_current_version_matches_published_verified_release() -> None:
    assert CURRENT_VERSION == PUBLISHED_STABLE == "2.0.4"
    notes = (ROOT / "docs/RELEASE_NOTES_v2.0.4.md").read_text(encoding="utf-8")
    assert "Status: **Stable — Q5 Release Quality Gate PASS**" in notes
    assert "Q4 and Q5 PASS" in notes
    evidence = (ROOT / "docs/implementation/Q5_V2_0_4_EVIDENCE.md").read_text(encoding="utf-8")
    assert "Status: **PASS — Stable v2.0.4 PUBLISHED**" in evidence
    assert "exact_zip_rebuilt = false" in evidence
    assert "published_asset_redownload_verified = true" in evidence
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "releases/download/v2.0.4/" in readme


def test_readme_preserves_historical_rescue_checksums() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "eadd0453d2e4b7d253e5cfd4e0b79ee07dccd0fd8df71d028e2c31b63ec7523d" in readme
    assert "b0d571692f925296022f146c39dce388b4717a43417e7f80132bd3aa52a9d853" in readme
