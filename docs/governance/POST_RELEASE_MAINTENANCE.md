# Post-release Maintenance Policy

Status: active after stable v2.0.0.

## Stable immutability

Published stable releases are immutable references.

For v2.0.0:
- tag: `v2.0.0`
- exact candidate: `d2ce2ccac62cdcd8994a38251a5b547c8460421e`
- Windows portable SHA-256:
  `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`

Do not:
- move or recreate the stable tag;
- replace an existing stable release asset;
- overwrite its checksum;
- rebuild a different ZIP and present it as the same release.

## Maintenance workflow

Future changes start from current `main` and use a dedicated branch.

Preferred flow:
1. create maintenance/feature branch;
2. make the smallest scoped change;
3. run focused tests;
4. open a pull request to `main`;
5. require Windows validation when build/runtime/release paths are touched;
6. merge only after validation is green;
7. use a new semantic version for any new published artifact.

## Versioning after v2.0.0

Examples:
- bug fix only: v2.0.1
- backward-compatible feature set: v2.1.0
- breaking project/schema/workflow change: v3.0.0

Never reuse v2.0.0 for a changed binary.

## Release rules

A future release must preserve the same separation already proven by Q4/Q5:
- artifact build/validation first;
- freeze exact candidate + artifact digest;
- release gate retrieves and verifies the frozen artifact;
- release gate must not rebuild the stable ZIP;
- post-publication re-download and SHA-256 verification are required.

## Main-branch protection

Repository-level branch protection/ruleset should be enabled manually for
`main` because the current ChatGPT GitHub connection does not have repository
administration permission.

Recommended settings:
- require pull request before merge;
- require status checks;
- include the Windows validation check for relevant changes;
- block force pushes;
- block branch deletion;
- restrict direct pushes where appropriate.

Tracking issue:
- #1 — Post-release hardening: protect main branch


## v2.0.1 stable immutable reference — October 8, 2026

The maintenance release v2.0.1 has passed Q4 and Q5, and is now the latest stable:

- tag: `v2.0.1`
- exact candidate/tag commit: `35a8c195469d49d7f7938b31761ceb17c4c720e0`
- exact Windows ZIP: `Full-Album-Maker-v2.0.1-Windows-Portable.zip`
- exact portable ZIP bytes: `189598786`
- portable ZIP SHA-256: `6c97461ee3472973fc9b7950952287ae5aab9ffe2dffbe6a1fb0c236353d4a5d`
- Q4 Actions run: `37724287381`
- Q5 Actions run: `37725395630`
- Q5 GitHub Release: https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.1
- evidence: `docs/implementation/Q5_V2_0_1_EVIDENCE.md`.

Both v2.0.0 and v2.0.1 are immutable releases. Preserve each tag, exact ZIP and checksum. v2.0.0 is now the previous stable rollback option; v1.5.0 remains older historical stable. Future changed binaries require new version numbers, new frozen Q4 evidence and Q5 no-rebuild publication.


## v2.0.2 stable immutable reference — October 8, 2026

The latest published stable version is now **v2.0.2**:
- tag `v2.0.2` directly points to exact Q4 build SHA `2678b9f93364334c7eaf9ebad9ef7e079533716f`.
- exact Windows portable ZIP `Full-Album-Maker-v2.0.2-Windows-Portable.zip`, `189599767` bytes.
- ZIP SHA-256: `701e0b68de17ec30ad17620d5cb5ef47e29bb28ca36ad0c95e5c242757c70c64`.
- Q4 run `37732261424`, Q5 run `37733519371`, release ID `406458763`.
- https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.2
- Full evidence `docs/implementation/Q5_V2_0_2_EVIDENCE.md`.

Published stable v2.0.2, v2.0.1, v2.0.0 and v1.5.0 tags, release assets and checksums are all immutable. Do not move tags, replace ZIPs or re-run historical controls to overwrite an existing release. Future executable changes require a new semantic version and entirely new Q4/Q5 evidence.
