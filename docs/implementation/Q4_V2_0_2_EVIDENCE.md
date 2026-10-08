# Q4 v2.0.2 — Frozen Windows Artifact Evidence

Status: **PASS / FROZEN — NOT PUBLISHED**

## Exact Q4 artifact identity

| Evidence field | Exact value |
| --- | --- |
| Semantic version | `2.0.2` |
| Q4 **source and ZIP build commit** | `2678b9f93364334c7eaf9ebad9ef7e079533716f` |
| Q4 GitHub Actions run | `37732261424` |
| Q4 Windows job | `113163826631` |
| Actions artifact ID | `11530243260` |
| Actions artifact name | `q4-v2.0.2-windows-artifact-candidate` |
| Inner portable ZIP filename | `Full-Album-Maker-v2.0.2-Windows-Portable.zip` |
| **Inner portable ZIP bytes** | `189599767` |
| **Inner portable ZIP SHA-256** | `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64` |
| Windows regression | `769 passed` |
| Pinned FFmpeg external-filter-script | `1 passed` |
| Publication | `false` |

Frozen tuple: `2.0.2 | 2678b9f93364334c7eaf9ebad9ef7e079533716f | 11530243260 | Full-Album-Maker-v2.0.2-Windows-Portable.zip | 189599767 | 701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64`

Proof: https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37732261424

The GitHub Actions **wrapper** ZIP is not the inner portable ZIP: wrapper size `189252606` bytes, wrapper digest `sha256:8508ff4efa643ec8b2a7efeb32b516c39c7b30bb8992142c4ac3f15929293faa`. Do not confuse wrapper and inner ZIP checksums. Artifact was not expired when recorded; verify availability again before Q5.

## Gate checks

- Q4 workflow run status `completed`, conclusion `success`.
- `769 passed` in complete Windows regression; separate real pinned FFmpeg external-script filter test `1 passed`.
- PyInstaller Windows x86_64 portable onedir created by existing pinned build script.
- Extracted Windows ZIP portable smoke passed in Unicode/apostrophe path without global Python, global FFmpeg or provider API keys. Output contained audio and video streams.
- Manifest version `2.0.2`, package `__version__`, project metadata, embedded `CAPABILITIES.json`, asset file layout and notices all matched.
- Pinned FFmpeg distribution digest remains `a885f564dee2b60f69ab866c6c89b96ae531fc2ee1f24ff8b5b1a6d29960a96b`.
- Q4 secret scan and embedded provenance validation PASS.
- Q4 generated and verified `SHA256SUMS.txt` and uploaded the exact inner ZIP, checksum and Q4 evidence.
- PR #41 generic Windows CI `37732297838` PASS on same frozen candidate commit.
- PR #41 merged to `main` as `6cb54bc2e640113791d8e39da9d727a30f343926`. **This merge SHA is NOT the frozen ZIP build SHA.**
- Post-merge protected `main` CI run `37732736075`: verify PASS independently.

## Immutable old releases

- Previous latest stable `v2.0.1` tag target `35a8c195469d49d7f7938b31761ceb17c4c720e0`; ZIP SHA256 `6c97461ee3472973fc9b7950952287ae5aab9ffe2dffbe6a1fb0c236353d4a5d`.
- `v2.0.0` remains preserved.
- Original `inoriko920-dev/Full-Album-Maker` repo must never be modified.

## Q5 no-rebuild handoff — not yet published

Q5 must use a **new v2.0.2 workflow** and verify all the following, failing closed before publication:

1. Exact Q4 source SHA `2678b9f93364334c7eaf9ebad9ef7e079533716f` is an ancestor of the Q5 control branch. After freeze, only Q5 control file and docs may differ.
2. Q4 Actions run `37732261424` is completed SUCCESS with matching exact SHA.
3. GitHub Actions artifact ID `11530243260`, name `q4-v2.0.2-windows-artifact-candidate`, is not expired and originated from the frozen Q4 run.
4. Download **the same artifact**, extract its Actions wrapper, then verify inner ZIP filename, exact `189599767` bytes and SHA-256 `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64` and `SHA256SUMS.txt`.
5. Verify old stable `v2.0.1` is published for rollback; `v2.0.2` tag and release do not exist.
6. Inspect embedded version, Python/FFmpeg/font pins, manifests, third-party notices and secrets. Re-extract and smoke-test unchanged ZIP offline with audio + video.
7. Only after all checks PASS, create `v2.0.2` tag pointing to exact Q4 source SHA and release with **the same ZIP**, no rebuilding/repacking.
8. Download published ZIP and checksum, verify byte size, digest and tag; save independent Q5 evidence.

**Q4 PASS does not authorize a claim that v2.0.2 has been published.**
