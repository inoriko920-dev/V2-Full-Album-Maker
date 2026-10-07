# Q5 Release Evidence

Status: **PASS_PUBLISHED**

## Stable release

- Version: `2.0.0`
- Tag: `v2.0.0`
- Release ID: `405709866`
- Published: `2026-10-07T11:57:27Z`
- Release URL:
  `https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.0`

## Candidate / tag target

`d2ce2ccac62cdcd8994a38251a5b547c8460421e`

Git ref verification:
- ref: `refs/tags/v2.0.0`
- object type: `commit`
- object SHA:
  `d2ce2ccac62cdcd8994a38251a5b547c8460421e`

## Published ZIP

`Full-Album-Maker-v2.0.0-Windows-Portable.zip`

- bytes: `189554128`
- expected Q4 SHA-256:
  `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`
- GitHub release asset digest:
  `sha256:4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`
- release asset ID: `618557916`

Q5 downloaded the published asset after release creation and re-hashed it.

Result:
- byte length match: PASS
- SHA-256 match: PASS
- exact Q4 asset identity: PASS

## Published checksum

- asset: `SHA256SUMS.txt`
- asset ID: `618557920`
- asset digest:
  `sha256:1c6ea915fcfc4ce26c7327b23929880c0a3d26ee5abce7c8a4e0d91a712da082`

Expected checksum line:

`4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad  Full-Album-Maker-v2.0.0-Windows-Portable.zip`

Result:
- PASS

## Pre-publication checks

- no-rebuild guard: PASS
- tag unused before release: PASS
- release unused before release: PASS
- rollback v1.5.0 stable release: PASS
- frozen Q4 artifact download: PASS
- Q4 ZIP size/digest: PASS
- embedded manifest/provenance: PASS
- exact ZIP isolated smoke: PASS
- no global Python: PASS
- no global FFmpeg: PASS
- no Gemini/Google API key: PASS
- audio+video output: PASS
- secret scan: PASS
- stable version metadata: PASS

## Publication checks

- GitHub Release creation: PASS
- draft: false
- prerelease: false
- exact tag target: PASS
- required assets present: PASS
- release-asset redownload: PASS
- release-asset SHA-256: PASS

## Workflow

Successful Q5 workflow:
- run: `37617534800`
- control head:
  `9f36f58f7a02099142647e6936114e6ad32211cb`

Q5 evidence artifact:
- ID: `11481041761`
- digest:
  `sha256:e916c0962f0ec2cb1d56db919c78838587e90b342ea583ccae71e12bf40c1788`

## Rollback

Last-known-good previous stable:
- `v1.5.0`

Application rollback is side-by-side and does not silently roll project data
backward.

## Final conclusion

The exact Q4-tested ZIP was published without rebuild and independently
re-downloaded from the stable release to prove identity.

**Q5 PASS.**
