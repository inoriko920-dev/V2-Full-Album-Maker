# Third-party notices

## FFmpeg

Windows portable builds bundle the GPL static x86_64 variant from
BtbN/FFmpeg-Builds because Full Album Maker uses the libx264 and libx265
encoders. The FFmpeg executable and its codec libraries are separate third-party
software and are not covered by the MIT license of Full Album Maker.

The V2 release candidate uses the immutable pin recorded in
`build/release_manifest.json`:

- Provider: `BtbN/FFmpeg-Builds`
- Release ID: `402633211`
- Release tag: `autobuild-2026-10-03-18-14`
- Asset ID: `608288215`
- Asset: `ffmpeg-N-127142-g12b7b9891b-win64-gpl.zip`
- SHA-256: `a885f564dee2b60f69ab866c6c89b96ae531fc2ee1f24ff8b5b1a6d29960a96b`
- Version family: `master N-127142-g12b7b9891b`

The build uses the dated GitHub release URL and verifies the exact SHA-256
before extraction. Any content change fails the build until the release manifest
is intentionally reviewed and updated.

The portable folder also includes the FFmpeg license/readme supplied by the
pinned distribution when present. Source/build information is available from
the FFmpeg project and BtbN/FFmpeg-Builds.

## Noto Sans

The Windows portable build includes Noto Sans as its deterministic fallback font
for FFmpeg/fontconfig text rendering.

- Source: `google/fonts`
- Pinned commit: `23e54b51ddffbc7713c583748e3bd86f62b1fa4a`
- Source path: `ofl/notosans/NotoSans[wdth,wght].ttf`
- License: SIL Open Font License 1.1

The corresponding `NotoSans-OFL.txt` is included beside the font in the
portable folder. User-selected custom font files are not copied into a project
implicitly; users remain responsible for those custom assets and their licenses.

## PySide6 / Qt

The desktop UI uses PySide6 / Qt. Their licensing terms are separate from the
MIT license of Full Album Maker.

The V2 Windows release candidate pins:
- PySide6 `6.11.2`
- PySide6_Addons `6.11.2`
- PySide6_Essentials `6.11.2`
- shiboken6 `6.11.2`

Review the applicable Qt/PySide licensing terms before commercial
redistribution.

## PyInstaller and build-time Python packages

The Windows portable artifact is produced with the exact versions in
`build/requirements-windows.lock`, including PyInstaller `6.22.3`.
These build-time packages retain their own upstream licenses.
