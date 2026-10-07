# Full Album Maker v2.0.0 — Release Notes

Status: **Q4 release candidate — not published**

This file is part of the exact v2.0.0 candidate before the Windows Artifact and
Q5 Release gates are complete. A stable GitHub Release is not authorized until
Q5 explicitly approves the exact Q4-tested artifact identity.

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
- Q2 full regression and Q3 infrastructure gates are recorded in repository
  evidence.

## Windows portable candidate

The Q4 candidate is built from `build/release_manifest.json` and includes:
- Python 3.12.10 build runtime;
- pinned Python package lock;
- pinned BtbN Windows FFmpeg/ffprobe with SHA-256 verification;
- Noto Sans pinned by immutable google/fonts commit;
- PyInstaller onedir application;
- release manifest, capabilities report, notices and license material;
- checksum file for the exact ZIP.

Q4 requires the extracted ZIP to work from a Unicode/apostrophe path without
global Python, global FFmpeg, Gemini key, or Google API key and to verify a real
audio+video output using the bundled tools.

## Release status

This candidate is **not published** by the build workflow.

Q5 must approve the exact semantic version + candidate commit + ZIP SHA-256 and
then publish that exact tested ZIP without rebuilding it.
