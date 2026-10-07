# STEP 10 — Testing, Regression, Stress, Benchmark, dan Release Quality Gate

## Status
PASS — planning complete. Coding remains BLOCKED.

## Scope
STEP 10 defines the complete proof system for V2: test pyramid, feature parity, architecture contracts, concurrency/fault injection, long-album stress, performance regression, UI visual/responsive evidence, real FFmpeg, exact Windows portable artifact validation, flaky-test policy, and release promotion gates. No source/test/workflow implementation was changed.

## Audited Baseline
- 115 Python test files already exist.
- Existing workflows cover feature steps, integration, release QA, and Windows portable build.
- Existing real-FFmpeg tests verify actual output paths.
- Existing 200-song x 54-second fixtures represent roughly 3 hours in Packed and Free modes with a 2-second resolver ceiling.
- Existing UI capture tooling covers all 9 workspaces.
- Existing Windows release path pins Python/dependencies, FFmpeg digest, Noto Sans commit, PyInstaller, and checksum generation.
- Extracted-ZIP portable smoke isolates global Python, FFmpeg, and API keys and verifies audio+video output.

## Quality Layers
- L0 Static / Supply
- L1 Unit / Domain
- L2 Contract / Adapter
- L3 Integration / UI
- L4 Real Infrastructure
- L5 Concurrency / Fault
- L6 Windows Artifact
- L7 Release Candidate

## Decisions D10-01..D10-20
1. Existing 115-file suite/workflows are the minimum regression floor.
2. Declared Python >=3.11 support requires a Python 3.11 compatibility lane or an explicit support-floor change.
3. Feature parity is behavior-based and mapped through FeatureParityRegistry.
4. Every facade/port requires legacy-vs-new contract evidence before legacy retirement.
5. Characterization tests preserve meaningful behavior; normalization cannot hide regressions.
6. Concurrency tests assert terminal/post-state and bounded resource behavior.
7. Destructive boundaries require injected failure proofs.
8. Media/path fixtures are local, deterministic, versioned, and external-URL independent.
9. Animation/Beat/Spectrum need evaluator plus real/parity evidence.
10. Real FFmpeg testing is tiered R0–R5; mocks never replace critical real integration.
11. 200-song/~3-hour structural stress remains mandatory; long real encode is risk-triggered.
12. Performance comparisons use same-environment baselines; >10% regression requires investigation.
13. Functional UI PASS and pixel-match PASS are separate claims.
14. AI quality gates prioritize local safety, atomicity, stale protection, and offline independence.
15. Supply-chain/license/pinning/secret failures block release.
16. Final portable smoke runs against the extracted, versioned ZIP.
17. No unexplained flaky release blocker can be waived by retries.
18. Tests cannot be changed merely to bless a regression.
19. Every RC has an evidence manifest tied to exact commit/artifact.
20. Quality gates Q0–Q5 control promotion.

## Quality Gate Ladder
- Q0 Developer: compile + focused unit/contract.
- Q1 Slice: touched feature parity + relevant fault/concurrency.
- Q2 Integration: full pytest + cross-workspace/session/lifecycle.
- Q3 Infrastructure: real FFmpeg + UI captures + structural benchmarks.
- Q4 Windows Artifact: exact portable build + extracted smoke + supply-chain gates.
- Q5 Release: all blockers closed + evidence manifest + rollback/handoff ready.

## Hard Release Blockers
- Any MUST KEEP feature regression.
- Data-loss/canonical overwrite safety failure.
- Orphan process/post-close mutation defect.
- Failed project roundtrip/migration/recovery invariant.
- Render success without verified published output.
- Real FFmpeg regression in affected path.
- Windows portable isolation/smoke/checksum failure.
- Secret/license/provenance blocker.
- Unexplained flaky release blocker.
- Known critical crash on supported standard workflow.

## Planned Quality Infrastructure T1..T12
FeatureParityRegistry; shared deterministic fixtures; adapter contract harness; lifecycle race/leak harness; persistence fault injection; RenderEngine real-FFmpeg/transaction harness; Beat fixtures; UI capture matrix; performance baseline comparator; unified RC evidence manifest; Python 3.11 compatibility lane or explicit support-floor revision; exact V2 Windows artifact gate.

## Next STEP
STEP 11 — Windows Portable Build, Release, Rollback, dan Final Handoff.

Coding remains BLOCKED. After STEP 11 planning completes, all STEP 00–11 source-of-truth planning artifacts must be placed in the V2 repository before implementation begins.
