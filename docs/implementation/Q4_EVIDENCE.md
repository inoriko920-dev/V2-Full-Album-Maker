# Q4 Windows Artifact Evidence

Status: **PASS**

## Exact artifact identity

- Version: `2.0.0`
- Candidate SHA:
  `d2ce2ccac62cdcd8994a38251a5b547c8460421e`
- Actions run:
  `37615631835`
- Actions artifact ID:
  `11480755092`
- Actions artifact name:
  `q4-windows-artifact-candidate`
- Inner portable ZIP:
  `Full-Album-Maker-v2.0.0-Windows-Portable.zip`
- Inner portable ZIP bytes:
  `189554128`
- Inner portable ZIP SHA-256:
  `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`

Q5 must not rebuild this ZIP.

## Windows regression

During exact candidate build:
- 651 passed
- 0 failed

## Pinned Windows FFmpeg

- Asset:
  `ffmpeg-N-127142-g12b7b9891b-win64-gpl.zip`
- Asset SHA-256:
  `a885f564dee2b60f69ab866c6c89b96ae531fc2ee1f24ff8b5b1a6d29960a96b`
- Runtime version:
  `N-127142-g12b7b9891b-20261003`

Windows-only external filter script test:
- 1 passed
- `-/filter_complex`: PASS

## Portable smoke

Extracted Unicode/apostrophe path:
- PASS

Isolation:
- global Python unavailable: PASS
- global FFmpeg unavailable: PASS
- Gemini API key absent: PASS
- Google API key absent: PASS

Output:
- bundled render: PASS
- ffprobe verification: PASS
- audio stream: PASS
- video stream: PASS
- GUI v2.0.0 identity: PASS

Smoke sample:
- duration: 0.2 s
- output size: 5644 bytes

## Supply chain

- canonical release manifest: PASS
- application/manifest version alignment: PASS
- package lock/manifest alignment: PASS
- FFmpeg provenance/notices alignment: PASS
- Noto Sans provenance alignment: PASS
- ZIP checksum: PASS
- embedded RELEASE_MANIFEST.json: PASS
- embedded CAPABILITIES.json: PASS
- bundled FFmpeg/ffprobe: PASS
- bundled font/OFL: PASS
- secret scan: PASS
- automatic stable publication from build workflow: disabled

## Publication

`publication_performed = false`

No stable GitHub Release was created by Q4.

## Artifact freeze rule

The Q4 workflow ignores documentation-only pushes after the artifact-freeze
candidate. Governance/evidence documentation therefore does not create a new
ZIP.

The approved artifact remains the one from Actions run `37615631835`.

## Q5 handoff hard block

Q5 must reject publication if any of these differ:
- candidate SHA;
- semantic version;
- inner ZIP filename;
- inner ZIP SHA-256;
- checksum file contents.

Expected Q5 tuple:

`2.0.0 | d2ce2ccac62cdcd8994a38251a5b547c8460421e | Full-Album-Maker-v2.0.0-Windows-Portable.zip | 4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`
