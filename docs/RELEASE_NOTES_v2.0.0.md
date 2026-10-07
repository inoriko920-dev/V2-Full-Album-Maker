# Full Album Maker v2.0.0 — Release Notes

Status: **Stable — Q5 Release Quality Gate PASS**

Full Album Maker v2.0.0 was published only after Q5 verified the exact
Q4-tested Windows portable artifact. The stable asset was not rebuilt.

## Major V2 changes

- AppKernel / CompositionRoot is the explicit production wiring boundary.
- Central TaskSupervisor lifecycle and stale-result protection.
- ProjectPersistence owns canonical save/load/recovery behavior.
- AppKernel-owned RenderEngine facade preserves proven FFmpeg compiler semantics.
- MediaProbeService, PreviewEngine, and CacheManager centralize media
  infrastructure ownership.
- BeatAnalysisService provides deterministic derived beat events without
  modifying master audio.
- WorkspaceRegistry owns all nine production workspace routes.
- Proven obsolete legacy route bridges were retired.
- Production bootstrap ownership was consolidated into one ordered runtime
  installer boundary.
- Q2 full integration regression, Q3 infrastructure, Q4 Windows artifact, and
  Q5 release gates all passed.

## Stable Windows portable

Published asset:
- `Full-Album-Maker-v2.0.0-Windows-Portable.zip`
- SHA-256:
  `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`
- bytes: `189554128`

Stable tag:
- `v2.0.0`

Exact candidate:
- `d2ce2ccac62cdcd8994a38251a5b547c8460421e`

The portable bundle includes:
- Python 3.12.10 build runtime;
- pinned Python package lock;
- pinned BtbN Windows FFmpeg/ffprobe with SHA-256 verification;
- Noto Sans pinned by immutable google/fonts commit;
- PyInstaller onedir application;
- release manifest, capabilities report, notices, and license material;
- checksum file for the exact ZIP.

## Release verification

Q5:
- retrieved the existing Q4 artifact instead of rebuilding;
- verified exact ZIP filename, byte length, and SHA-256;
- verified embedded release manifest, capabilities, FFmpeg provenance, and font
  provenance;
- re-ran the extracted exact ZIP smoke from a Unicode/apostrophe path;
- removed global Python/FFmpeg and API keys from the smoke environment;
- verified real audio+video output;
- published the exact Q4 ZIP;
- downloaded the published release ZIP again and re-verified the same SHA-256;
- verified the stable tag points to the exact Q4 candidate.

## Rollback

Previous stable remains:
- `v1.5.0`

Updates use side-by-side portable folders. Application rollback does not
silently rewrite project data.
