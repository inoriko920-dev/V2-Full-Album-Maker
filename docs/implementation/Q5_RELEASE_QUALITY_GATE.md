# Q5 — Release Quality Gate

Status: **PASS — stable v2.0.0 published**

## Release identity

- Stable version: `2.0.0`
- Stable tag: `v2.0.0`
- Tag target / exact Q4 candidate:
  `d2ce2ccac62cdcd8994a38251a5b547c8460421e`
- Q5 workflow run:
  `37617534800`
- Q5 control-workflow head:
  `9f36f58f7a02099142647e6936114e6ad32211cb`
- GitHub Release ID:
  `405709866`
- Published at:
  `2026-10-07T11:57:27Z`
- Release URL:
  `https://github.com/inoriko920-dev/V2-Full-Album-Maker/releases/tag/v2.0.0`

## Exact published portable asset

- File:
  `Full-Album-Maker-v2.0.0-Windows-Portable.zip`
- Bytes:
  `189554128`
- SHA-256:
  `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`
- GitHub release asset ID:
  `618557916`
- GitHub asset digest:
  `sha256:4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`

Published checksum asset:
- `SHA256SUMS.txt`
- release asset ID: `618557920`
- asset SHA-256:
  `1c6ea915fcfc4ce26c7327b23929880c0a3d26ee5abce7c8a4e0d91a712da082`

The published portable ZIP is byte-identical to the frozen Q4-tested ZIP.

## Q5 no-rebuild proof

Q5 does not call:
- `build/build_portable.ps1`;
- PyInstaller;
- any packaging/build operation that could create a replacement ZIP.

The Q5 workflow:
1. starts from the frozen Q4 candidate ancestry;
2. downloads Q4 Actions artifact ID `11480755092`;
3. extracts the wrapper artifact;
4. validates inner ZIP filename, byte length, SHA-256, and `SHA256SUMS.txt`;
5. validates embedded `CAPABILITIES.json`, `RELEASE_MANIFEST.json`, and notices;
6. re-runs portable smoke on the exact downloaded inner ZIP;
7. publishes that same inner ZIP;
8. downloads the published release asset again;
9. recomputes SHA-256 and byte length;
10. verifies the stable tag target.

Q5 final evidence:
- `exact_zip_rebuilt = false`
- `published_asset_redownload_verified = true`

## Frozen Q4 identity re-verification

Before publication Q5 verified:
- Q4 candidate SHA:
  `d2ce2ccac62cdcd8994a38251a5b547c8460421e`
- Q4 run:
  `37615631835`
- Q4 artifact ID:
  `11480755092`
- Q4 portable ZIP SHA-256:
  `4c0f2205a0a0a77d3da819ca11e4a6e57298f2003a20f132533a1b29760280ad`
- Q4 ZIP bytes:
  `189554128`

All values matched exactly.

## Embedded provenance re-verification

Q5 opened the exact inner ZIP and validated:
- application version is 2.0.0;
- embedded build commit is the exact Q4 candidate SHA;
- embedded release manifest equals repository canonical release manifest;
- embedded FFmpeg block equals the manifest;
- embedded font block equals the manifest;
- THIRD_PARTY_NOTICES contains the exact shipping FFmpeg asset/digest/release tag.

Result:
- **PASS**

## Exact ZIP smoke before publication

Q5 extracted the exact frozen Q4 ZIP into a path containing:
- spaces;
- Unicode punctuation;
- apostrophe.

The smoke ran with:
- global Python removed from PATH;
- global FFmpeg removed from PATH;
- Gemini API key absent;
- Google API key absent.

Result:
- portable executable launches;
- bundled render works;
- ffprobe verifies audio + video;
- GUI version identity is v2.0.0;
- smoke report is `ok=true`.

Result:
- **PASS**

## Secret / metadata recheck

Q5 rechecked:
- private-key patterns;
- GitHub token patterns;
- Google API key patterns;
- OpenAI-like secret patterns;
- stable release manifest version.

Result:
- **PASS**

## Rollback evidence

Previous stable rollback tag:
- `v1.5.0`

Q5 verified it exists as a published non-draft, non-prerelease stable release.

Application rollback remains side-by-side:
- retain/download the previous stable portable folder;
- do not rewrite project data automatically;
- project-data rollback remains a separate contract.

## Publication verification

After GitHub Release creation Q5:
- downloaded `Full-Album-Maker-v2.0.0-Windows-Portable.zip` from the release;
- recomputed SHA-256;
- recomputed byte length;
- downloaded `SHA256SUMS.txt`;
- verified both match frozen Q4 identity;
- queried the release API;
- queried the tag ref API;
- verified release is neither draft nor prerelease;
- verified `refs/tags/v2.0.0` points directly to exact candidate
  `d2ce2ccac62cdcd8994a38251a5b547c8460421e`.

Result:
- **PASS**

## Q5 workflow iteration history

Q5 failures were fail-closed and occurred before publication:

1. Run `37617273595`
   - workflow YAML invalid because a PowerShell here-string escaped the YAML
     `run:` indentation;
   - no jobs ran;
   - no tag/release created.

2. Run `37617407295`
   - Q5 entered the job but the no-rebuild guard self-matched the literal
     `PyInstaller` text in its own assertion;
   - publication and all later steps were skipped;
   - no tag/release created.

3. Run `37617534800`
   - all pre-publication gates PASS;
   - stable release publication PASS;
   - published asset re-download identity verification PASS;
   - Q5 evidence upload PASS.

## Q5 evidence artifact

Actions artifact:
- ID: `11481041761`
- Name: `q5-release-evidence`
- Digest:
  `sha256:e916c0962f0ec2cb1d56db919c78838587e90b342ea583ccae71e12bf40c1788`

It contains final release evidence and the release notes used by Q5.

## Gate conclusion

Q5: **PASS**

The STEP 10 quality sequence is complete:
- Q2 Integration: PASS
- Q3 Infrastructure: PASS
- Q4 Windows Artifact: PASS
- Q5 Release: PASS

Full Album Maker **v2.0.0 stable is published**.

No further quality/release gate is pending in the approved STEP 00–11 workflow.
