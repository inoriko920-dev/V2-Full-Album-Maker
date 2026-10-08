"""Keep public README aligned with verified, published stable identity.

The README is the first page a Windows user sees on GitHub. In particular it
must not regress to old recovery-only copy after a new stable is published.
"""

from pathlib import Path

from full_album_maker import __version__


ROOT = Path(__file__).resolve().parents[1]


def test_readme_describes_current_stable_download_and_checksum() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    notes = ROOT / f"docs/RELEASE_NOTES_v{__version__}.md"
    assert notes.is_file()
    notes_text = notes.read_text(encoding="utf-8")
    assert "Status: **Stable — Q5 Release Quality Gate PASS**" in notes_text
    assert "Q4 and Q5 PASS" in notes_text

    filename = f"Full-Album-Maker-v{__version__}-Windows-Portable.zip"
    assert f"Full Album Maker v{__version__}" in readme
    assert f"releases/download/v{__version__}/{filename}" in readme
    assert f"releases/download/v{__version__}/SHA256SUMS.txt" in readme
    assert f"docs/RELEASE_NOTES_v{__version__}.md" in readme

    evidence = ROOT / f"docs/implementation/Q5_V{__version__.replace('.', '_')}_EVIDENCE.md"
    assert evidence.is_file()
    evidence_text = evidence.read_text(encoding="utf-8")
    assert "published_asset_redownload_verified = true" in evidence_text
    assert "exact_zip_rebuilt = false" in evidence_text
    # The public checksum and exact immutable Q4 target must come from the
    # completed release gate rather than a candidate or local build.
    import re
    hashes = set(re.findall(r"(?<![a-f0-9])[a-f0-9]{64}(?![a-f0-9])", notes_text))
    assert hashes.intersection(re.findall(r"(?<![a-f0-9])[a-f0-9]{64}(?![a-f0-9])", readme))
    assert "Repository asli" in readme
    assert "Source code asli belum sepenuhnya dipulihkan" not in readme


def test_readme_preserves_historical_rescue_checksums() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "eadd0453d2e4b7d253e5cfd4e0b79ee07dccd0fd8df71d028e2c31b63ec7523d" in readme
    assert "b0d571692f925296022f146c39dce388b4717a43417e7f80132bd3aa52a9d853" in readme
