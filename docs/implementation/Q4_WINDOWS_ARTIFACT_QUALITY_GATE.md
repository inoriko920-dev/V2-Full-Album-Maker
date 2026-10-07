# Q4 — Windows Artifact Quality Gate

Status: **PASS — exact Windows artifact validated and frozen**

## Scope

Q4 is the STEP 10/11 Windows Artifact Quality Gate.

It prepares and validates the exact Windows x86_64 portable candidate that may
later be published by Q5. Q4 does **not** publish a stable GitHub Release.

## Exact Q4 candidate identity

- Version: `2.0.0`
- Candidate commit:
  `d2ce2ccac62cdcd8994a38251a5b547c8460421e`
- GitHub Actions run:
  `37615631835`
- Workflow artifact:
  `q4-windows-artifact-candidate`
- GitHub artifact ID:
  `11480755092`
- Portable ZIP:
  `Full-Album-Maker-v2.0.0-Windows-Portable.zip`
- Portable ZIP bytes:
  `189554128`
- Portable ZIP SHA-256:
  `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`

This semantic version + candidate commit + ZIP SHA-256 is the Q4 artifact
identity.

Q5 must use this exact tested ZIP. It must not rebuild a similar ZIP.

## Canonical release manifest

Q4 adds:

`build/release_manifest.json`

This is the canonical source of truth for:
- target stable version;
- Windows platform contract;
- Python version;
- pip version;
- pinned Python build packages;
- pinned FFmpeg provider/release/asset/digest;
- pinned Noto Sans commit/license;
- artifact naming/checksum contract.

Repeated release metadata is now verified against this manifest instead of
being independently hardcoded across build surfaces.

## v2.0.0 candidate version

The candidate version is now aligned across:
- `src/full_album_maker/__init__.py`;
- `pyproject.toml`;
- `build/release_manifest.json`;
- `docs/RELEASE_NOTES_v2.0.0.md`.

The release notes explicitly state that the candidate is **not published** until
Q5 approves the exact Q4 artifact.

## FFmpeg provenance blocker resolved

The stale THIRD_PARTY_NOTICES FFmpeg record was replaced by the exact shipping
Q4 pin:

- Provider: BtbN/FFmpeg-Builds
- Release ID: 402633211
- Release tag: `autobuild-2026-10-03-18-14`
- Asset ID: 608288215
- Asset: `ffmpeg-N-127142-g12b7b9891b-win64-gpl.zip`
- Version family: `master N-127142-g12b7b9891b`
- SHA-256:
  `a885f564dee2b60f69ab866c6c89b96ae531fc2ee1f24ff8b5b1a6d29960a96b`

The build downloads the dated release URL and verifies this digest before
extraction.

## Build validation vs stable publication separation

The old `.github/workflows/build-windows-portable.yml` stable-publication
behavior was removed.

It now:
- has `contents: read`;
- builds and validates the candidate;
- uploads validation artifacts;
- contains no `gh release create`;
- cannot automatically create a stable GitHub Release from a main push.

Stable publication remains a separate Q5 action.

## Windows build result

Q4 uses:
- runner: `windows-2025`;
- Python: `3.12.10`;
- pip: `26.2.1`;
- PySide6: `6.11.2`;
- PyInstaller: `6.22.3`;
- pinned BtbN Windows FFmpeg described above;
- pinned Noto Sans commit
  `23e54b51ddffbc7713c583748e3bd86f62b1fa4a`.

Full Windows regression during artifact creation:
- **651 passed**
- **0 failed**

PyInstaller onedir build: **PASS**

## Extracted ZIP isolation smoke

The exact final ZIP was extracted into a path containing:
- spaces;
- Unicode punctuation;
- apostrophe.

The portable smoke ran with:
- global Python removed from PATH;
- global FFmpeg removed from PATH;
- `GEMINI_API_KEY` absent;
- `GOOGLE_API_KEY` absent.

Result:
- portable executable launched successfully;
- bundled FFmpeg/ffprobe were used;
- report `ok=true`;
- API key detected: false;
- verified output streams: audio + video;
- sample output duration: 0.2 seconds;
- sample output bytes: 5644;
- GUI title includes v2.0.0.

Extracted-ZIP isolation smoke: **PASS**

## Windows-only external filter script capability

Q3 correctly deferred the `-/filter_complex` capability because Ubuntu FFmpeg
6.1.1 does not support this Windows shipping-build option.

Q4 re-ran:

`tests/test_editor_v2_s12_performance.py::test_real_ffmpeg_accepts_external_filter_script`

against the exact pinned Windows FFmpeg.

Shipping FFmpeg version:
`N-127142-g12b7b9891b-20261003`

Result:
- **1 passed**
- external filter script capability: **PASS**

This closes the Windows-only blocker carried from Q3.

## Supply-chain / provenance evidence

Q4 verifies:
- package lock versions against release manifest;
- application version against release manifest;
- FFmpeg digest and provenance against notices;
- font commit against notices;
- release build workflow cannot auto-publish;
- exact ZIP checksum;
- bundled `RELEASE_MANIFEST.json`;
- bundled `CAPABILITIES.json`;
- bundled license/notices;
- bundled FFmpeg/ffprobe;
- bundled Noto Sans + OFL;
- repository secret scan.

Secret scan: **PASS**

## Capability report

The portable artifact contains `CAPABILITIES.json` version 2.

It records:
- application version 2.0.0;
- candidate build commit;
- exact release-manifest FFmpeg block;
- exact font block;
- exact Python/build package block;
- offline/manual workflow support;
- global Python not required;
- global FFmpeg not required;
- Windows external-filter capability required and proven by Q4.

## Q4 iteration history

Q4 failures were not waived.

1. Run `37603685220`
   - failed because `__init__.py` contained a literal `\n` sequence;
   - source byte corrected.

2. Run `37603800092`
   - reached full Windows regression;
   - exposed three old release tests that still required pre-V2 hardcoded metadata
     and automatic main-branch release behavior.

3. Run `37604262538`
   - after converting old release tests to the V2 manifest/publication contract,
     reached 649 passed;
   - exposed two stale test-name references / a self-referential string check.

4. Run `37614957123`
   - full Q4 artifact gate PASS on the pre-freeze candidate.

5. Run `37615631835`
   - artifact-freeze workflow revision validated;
   - final Q4 candidate PASS;
   - this run owns the exact artifact identity listed above.

## Artifact freeze

The Q4 workflow now ignores `docs/**`-only pushes.

This allows governance/evidence documentation to be committed after the
artifact is frozen without generating a replacement ZIP.

Therefore:
- Q4 tested candidate remains
  `d2ce2ccac62cdcd8994a38251a5b547c8460421e`;
- Q4 tested ZIP remains SHA-256
  `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`;
- later documentation commits are **not** release candidates.

## Gate conclusion

Q4: **PASS**

Q5 is the next and only allowed release gate.

Q5 must:
- use candidate commit `d2ce2ccac62cdcd8994a38251a5b547c8460421e`;
- retrieve artifact `q4-windows-artifact-candidate` from run
  `37615631835`;
- verify the inner portable ZIP SHA-256 exactly;
- rerun required release-level verification without rebuilding the ZIP;
- publish that exact ZIP only after Q5 PASS;
- publish checksum/release notes/provenance with the same identity.

Q5 is not started in this turn.
