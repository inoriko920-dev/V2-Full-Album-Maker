# Q4 v2.0.4 — Frozen Windows Portable Artifact Evidence

Status: **PASS / FROZEN — NOT PUBLISHED**

## Exact frozen Q4 identity

| Field | Frozen value |
| --- | --- |
| Version | `2.0.4` |
| Exact Q4 candidate source and build commit | `af5af1ce24aba17ff68d469390a0c3d21f80f44d` |
| Q4 Actions run | `37745568166` |
| Q4 Windows job | `113206108661` |
| GitHub Actions artifact ID | `11536240883` |
| GitHub Actions artifact name | `q4-v2.0.4-windows-artifact-candidate` |
| **Inner portable ZIP** | `Full-Album-Maker-v2.0.4-Windows-Portable.zip` |
| **Inner portable ZIP bytes** | `189599237` |
| **Inner portable ZIP SHA-256** | `888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b` |
| Complete Windows regression | `782 passed` |
| Pinned FFmpeg external-filter-script | `1 passed` |
| Publication | `false` |

**Frozen tuple:** `2.0.4 | af5af1ce24aba17ff68d469390a0c3d21f80f44d | 11536240883 | Full-Album-Maker-v2.0.4-Windows-Portable.zip | 189599237 | 888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b`

- Q4 workflow: https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37745568166
- Generic Windows PR #54 check on exact same source SHA: https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37745591187

### Important: GitHub artifact wrapper is **not** the inner portable ZIP

- Actions wrapper artifact ID: `11536240883`.
- Wrapper size: **189251989 bytes** (different from the **inner** ZIP's 189599237).
- Wrapper digest: `sha256:451481ce54804278b8f8fe5aee66c05a4457ac6d9416a844d24fa734b7393e01` (**not** the inner ZIP's digest).
- The artifact was **not expired** when inspected. Reported expiration: `2027-01-06T07:46:55Z`.

Q5 MUST retrieve the exact Q4 wrapper by artifact ID, then extract and independently verify the **inner ZIP** filename, byte size and SHA-256 above. Do not confuse or substitute wrapper and inner hashes.

## Verified Q4 gates

1. Q4 workflow `37745568166` finished `completed/success` on the **exact source SHA** `af5af1ce24aba17ff68d469390a0c3d21f80f44d`.
2. Pre-build metadata/publication safety: `Q4_RELEASE_METADATA_AND_PUBLICATION_SAFETY_PASS`.
3. Complete Windows Pytest regression: **782 passed**, zero reported failures; pinned real Windows FFmpeg external-filter-script **1 passed**.
4. Windows x86_64 PyInstaller onedir build succeeded; the emitted portable ZIP and SHA256SUMS.txt were checked for exact byte/hash correspondence.
5. Extracted Unicode/apostrophe-path isolated portable smoke succeeded: `Smoke portable: OK (0.2s; 5644 bytes; audio, video)`. No global Python/FFmpeg or provider API keys were present.
6. Bundled `CAPABILITIES.json`, exact `RELEASE_MANIFEST.json`, pinned Python **3.12.10**, FFmpeg SHA-256 `a885f564dee2b60f69ab866c6c89b96ae531fc2ee1f24ff8b5b1a6d29960a96b`, bundled Noto Sans/third-party notices, no auto-publication, and secret scan all passed.
7. Exact Q4 evidence log recorded `extracted_unicode_apostrophe_smoke=PASS`, `global_python_isolation=PASS`, `global_ffmpeg_isolation=PASS`, `api_key_absent=PASS`, `audio_video_probe=PASS`, `external_filter_script=PASS`, `publication_performed=false`, `q5_required=true`, `stable_v203_immutable=true`.
8. GitHub Actions artifact `11536240883` uploaded successfully under `q4-v2.0.4-windows-artifact-candidate`.
9. Generic Windows PR #54 run `37745591187` also finished `completed/success`, with **782 passed**, portable audio/video smoke PASS.
10. PR #54 was squash-merged to protected main at **`1ebbb49d0ecfc2da1b450d5f7142af879728a9d9`**. **That merge SHA is not the frozen Q4 build SHA.**

## Post-Q4 protected-main validation — separate required gate

The protected-main workflow run created by PR #54 merge is **`37746119351`** targeting `1ebbb49d0ecfc2da1b450d5f7142af879728a9d9`. Its final success must be independently verified **before Q5 starts**. Merely completing Q4 on the PR SHA does not satisfy this separate protected-main check.

## Published rollback baseline

- The latest published stable still is **v2.0.3**, unchanged.
- Its exact tag/source SHA remains `ee61ca0af5d15cdc51af91ad48e05bc2b641f49d`.
- Published portable ZIP bytes: `189599847`.
- Published portable ZIP SHA-256: `b2b2a3c7bac889f63ca2d84ffc65b035533ab22b22dc5c31e22bd1d1ae7247f0`.
- Its Q5 proof remains `docs/implementation/Q5_V2_0_3_EVIDENCE.md`.
- v2.0.2/v2.0.1/v2.0.0 and the original `inoriko920-dev/Full-Album-Maker` repository remain untouched.

## Q5 mandatory no-rebuild handoff — NOT STARTED

1. First confirm protected-main Q4 merge run `37746119351` **PASS**; confirm any subsequent evidence-documentation PR and protected-main CI do not alter the frozen Q4 ZIP source.
2. Create a **new** version-specific v2.0.4 Q5 workflow only; do not edit/re-use earlier publication controls.
3. Confirm new `v2.0.4` tag and GitHub release do **not** already exist and the previous `v2.0.3` stable exists for rollback.
4. Verify Q4 run ID `37745568166` was successful on exact source SHA `af5af1ce24aba17ff68d469390a0c3d21f80f44d`; verify artifact ID `11536240883` belongs to that run and is not expired.
5. Download Q4 artifact wrapper by **ID**, extract exact `Full-Album-Maker-v2.0.4-Windows-Portable.zip` and SHA256SUMS.txt; verify inner ZIP size `189599237` and SHA-256 `888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b`.
6. Recheck bundled capabilities, build commit, manifest, FFmpeg, fonts, third-party notices, and no secret exposure.
7. Run offline extracted exact ZIP audio/video smoke without global Python/FFmpeg or API keys. **Do not rebuild, repack or recompress.**
8. Only after all checks PASS, publish the exact ZIP/checksum with new tag pointing to the **frozen Q4 source SHA**, never Q4 merge or Q5 control SHA.
9. Re-download release ZIP/SHA256SUMS and verify hash/bytes/tag commit and stable flags.
10. Record **separate Q5 publication evidence** and update public stable README/handoff only after actual successful publication.

**Q4 PASS/FROZEN is not proof of published v2.0.4. Q5 remains strictly blocked until its gates pass.**
