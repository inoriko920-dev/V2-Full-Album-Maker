# Q4 v2.0.5 — Frozen Windows Portable Artifact Evidence

Status: **PASS / FROZEN — NOT PUBLISHED**

All values below are from **completed SUCCESS** Q4 Windows workflow and its generated evidence, not planned placeholders.

## Exact frozen Q4 identity

| Field | Verified value |
| --- | --- |
| App candidate version | `2.0.5` |
| Exact Q4 candidate source/build commit | `645fa166aa7a4cdc372b80c82db09026a7ab9b95` |
| Q4 Windows Actions run | `37754857699` |
| Q4 Windows job ID | `113236788584` |
| Actions artifact ID | `11540026862` |
| Actions artifact name | `q4-v2.0.5-windows-artifact-candidate` |
| **Inner portable ZIP** | `Full-Album-Maker-v2.0.5-Windows-Portable.zip` |
| **Inner portable ZIP bytes** | `189598540` |
| **Inner portable ZIP SHA-256** | `8a3cdc694b003cb8d1aff3e9a3e7d68591b0fd3b4106a29cea94dd9f45b82f74` |
| Full regression tests | `791 passed` |
| Pinned Windows FFmpeg real external filter test | `1 passed` |
| Stable publication | `false` |

**Frozen identity tuple:**
`2.0.5 | 645fa166aa7a4cdc372b80c82db09026a7ab9b95 | 37754857699 | 11540026862 | Full-Album-Maker-v2.0.5-Windows-Portable.zip | 189598540 | 8a3cdc694b003cb8d1aff3e9a3e7d68591b0fd3b4106a29cea94dd9f45b82f74`

Q4 workflow proof: https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37754857699

PR #60 exact-head Windows workflow: https://github.com/inoriko920-dev/V2-Full-Album-Maker/actions/runs/37754885928

## GitHub Actions wrapper versus inner portable ZIP — never mix

The GitHub Actions wrapper uploaded by Q4 has the following **different** identity:

- Wrapper artifact ID: `11540026862`.
- Wrapper name: `q4-v2.0.5-windows-artifact-candidate`.
- Wrapper size: **189251417 bytes**.
- Wrapper SHA-256 digest: `sha256:c2e76c52e48a23773e342fc9e2528a218ad66c2aa3a52a1eae6249be0ee7c078`.
- Artifact expired: **false** at evidence collection.
- Reported expiration: `2027-01-06T09:10:52Z`.
- Parent run: `37754857699`, exact head SHA `645fa166aa7a4cdc372b80c82db09026a7ab9b95`.

The Q5 no-rebuild workflow **must** download wrapper `11540026862`, extract **inner** ZIP `Full-Album-Maker-v2.0.5-Windows-Portable.zip`, verify **inner** bytes **189598540** and inner SHA-256 **8a3cdc694b003cb8d1aff3e9a3e7d68591b0fd3b4106a29cea94dd9f45b82f74**, and independently verify `SHA256SUMS.txt`. Wrapper digest must never substitute for inner ZIP digest.

## Verified Q4 gates

1. Q4 workflow `37754857699`, exact candidate commit `645fa166aa7a4cdc372b80c82db09026a7ab9b95`: **completed/success**.
2. Q4 metadata and no-publication safety: `Q4_RELEASE_METADATA_AND_PUBLICATION_SAFETY_PASS`; app `__version__`, `pyproject.toml`, release manifest and unpublished candidate release notes all agreed on `2.0.5`.
3. Full Windows regression: **791 passed**, zero reported failures. Real pinned FFmpeg external-filter script test: **1 passed**.
4. Windows x86_64 PyInstaller onedir build, full bundled Python **3.12.10**, pinned FFmpeg and Noto Sans/no new dependencies: **PASS**.
5. Extracted Unicode/apostrophe-path portable smoke: `Smoke portable: OK (0.2s; 5644 bytes; audio, video)`. It verified `global_python_isolation=PASS`, `global_ffmpeg_isolation=PASS`, `api_key_absent=PASS`, `audio_video_probe=PASS`.
6. Secret scan: `Q4_SECRET_SCAN_PASS`. Bundled `CAPABILITIES.json`, `RELEASE_MANIFEST.json`, font/license and third-party notices: **PASS**.
7. Manifest pinned FFmpeg SHA-256: `a885f564dee2b60f69ab866c6c89b96ae531fc2ee1f24ff8b5b1a6d29960a96b`. Real FFmpeg external-filter test: **PASS**.
8. Exact inner ZIP and SHA256SUMS.txt byte/hash equivalence and bundled build commit provenance **PASS**. The generated Q4 evidence recorded `publication_performed=false`, `q5_required=true`, `stable_v204_immutable=true`.
9. Q4 Actions wrapper was successfully uploaded with ID `11540026862`, linked to the correct Q4 run and source.
10. Independent PR #60 Windows run `37754885928` **completed/success**, with **791 passed** and extracted portable A/V smoke PASS.

## Protected main and evidence-documentation gate — separate from Q4 ZIP

- PR #60 merged the new Q4 workflow to protected `main` as `5b3e4af92ece9b7e36e3209ac8207b802a31df6b`.
- The protected-main CI started as run **`37755534261`** at that merge SHA. **Its final SUCCESS must be checked separately before Q5.**
- This merge SHA **IS NOT** the frozen Q4 build/source SHA. An evidence-documentation PR and its post-merge CI are also required before Q5 begins.

## Latest published stable / rollback (immutable)

Latest **published** stable remains `v2.0.4`, unchanged:
- Tag/source SHA `af5af1ce24aba17ff68d469390a0c3d21f80f44d`.
- Published portable ZIP: `Full-Album-Maker-v2.0.4-Windows-Portable.zip`.
- Exact bytes `189599237`; SHA-256 `888cc98fbb610cc96cd9187ed7e6ca894bfeb87e4e17d3376de0882be642564b`.
- Proof: `docs/implementation/Q4_V2_0_4_EVIDENCE.md`, `docs/implementation/Q5_V2_0_4_EVIDENCE.md`.
- Older v2.0.3/v2.0.2/v2.0.1/v2.0.0 tags/assets stay unchanged. Original `inoriko920-dev/Full-Album-Maker` repository must remain read-only.

## Q5 no-rebuild handoff — **NOT STARTED**

1. Check Q4 protected-main CI `37755534261` **SUCCESS**, this evidence PR exact-head Windows CI **SUCCESS** and resulting protected-main post-merge CI **SUCCESS**.
2. Confirm new `v2.0.5` tag/release **do not** already exist; confirm published v2.0.4 stable and its assets remain intact.
3. Create a **new version-specific** `.github/workflows/v2-q5-v2.0.5-release.yml` on `release/q5-v2.0.5` branched **directly from frozen Q4 source** `645fa166aa7a4cdc372b80c82db09026a7ab9b95`.
4. Its only diff versus frozen Q4 source may be the version-specific Q5 control workflow: no executable or packaging changes, no dependency updates and no ZIP rebuild.
5. Independently verify Q4 run SUCCESS, head SHA, artifact ID/name, wrapper association and expiry. Download exact wrapper `11540026862`; verify inner ZIP filename/bytes/SHA256 and SHA256SUMS exactly as frozen above.
6. Verify embedded version, capabilities, build commit, manifest, pinned Python/FFmpeg/fonts, license/third-party notices, and secrets. Repeat isolated **unchanged ZIP** offline extracted A/V smoke.
7. Only if all gates PASS, publish the exact **inner Q4 ZIP without rebuilding/repacking/recompressing** along with SHA256SUMS.txt; tag `v2.0.5` must target **Q4 source SHA**, not any merge or Q5 control SHA.
8. Re-download published assets and verify exact bytes/hash, tag ref, release flags, source provenance. Fail closed on any mismatch.
9. Archive separate `docs/implementation/Q5_V2_0_5_EVIDENCE.md`, then update README, latest stable notes, project handoff **only after** verified Q5 publication.
10. Preserve all earlier stable releases and original repo.

**Q4 PASS/FROZEN is NOT proof that v2.0.5 is publicly available.**
