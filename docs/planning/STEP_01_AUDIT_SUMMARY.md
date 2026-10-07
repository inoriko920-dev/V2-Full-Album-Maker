# STEP 01 — Audit Repo Lama dan Kontrak Perilaku

## Status
**PASS**

No application source, dependency, UI, schema, renderer, or workflow implementation was changed during STEP 01.

## Baseline Audited
- Repository: `inoriko920-dev/V2-Full-Album-Maker`
- Baseline main commit: `e3bc35b024654271cd594703f1402f9b003b1b08`
- Copy integrity from old repository: 372 blobs, 0 missing, 0 extra, 0 SHA/mode mismatch.

## Structural Findings
- 149 Python source files.
- 115 Python test files.
- 17 GitHub workflows.
- 30 runtime `install_*()` activations are executed by production `main.py`.
- The final window is composed through both inheritance and ordered runtime method/widget patches.

## Authoritative State
- `ProjectDocument` schema v2 is the editor project truth.
- `EditorController` owns validated transactions, revision, global Undo/Redo, and dirty signature.
- `EditorSession` owns transient editor selection/playhead/zoom/snap around that controller.
- STEP11 `SelectionStore` carries stable-ID shared selection context.
- Legacy `Project` remains a compatibility/persistence bridge and must not become a second authoritative editor state.

## Production Render Chain
`Step10 RenderExecutor -> Step08FFmpegCompiler -> V13FFmpegCompiler -> S11FFmpegCompiler -> FFmpegV2Compiler`

The final render contract includes:
- immutable RenderSnapshot,
- critical preflight,
- media integrity checks,
- runtime encoder probing/fallback,
- cancellable FFmpeg processing,
- ffprobe output verification,
- transactional publication and rollback.

## Frozen Timeline Semantics
- Packed: contiguous active songs; no implicit crossfade.
- Free: explicit start tick; gaps render as silence.
- Overlap requires an exact valid crossfade.
- Triple/ambiguous overlap is rejected.
- Packed <-> Free conversion is explicit and undoable.
- Integer timebase remains 240000 ticks/second.

## AI Contract
- Gemini is optional and acts as an intent planner, not a second editor.
- Context must remain sanitized: stable IDs + safe names, no raw media paths or API keys.
- Ambiguity, stale revision, unknown IDs, or permission violations produce zero project mutation.
- Project mutation executes locally through validated action/command contracts.
- Manual/offline editing and rendering remain first-class.

## Primary Risk Register
- R-01 P0: order-dependent runtime patch chain.
- R-02 P0: legacy Project <-> ProjectDocument bridge.
- R-03 P0: multiple historical render classes/path names.
- R-04 P0: asynchronous worker/callback lifecycle.
- R-05 P1: runtime workspace/widget replacement and hidden ownership.
- R-06 P1: per-domain cache policies.
- R-07 P1: release publish is not idempotent for an already-existing version/tag.
- R-08 P1: persistence compatibility across legacy envelope, sidecar, and extensions.
- R-09 P1: large feature modules and change-isolation cost.
- R-10 P2: historical/versioned modules and documentation increase handoff complexity.

## Behavior Contract IDs
C-01 old repository read-only; C-02 UI/concept preservation; C-03 manual offline; C-04 one authoritative editor state; C-05 global Undo/Redo; C-06 stable identity; C-07 Packed timeline; C-08 Free timeline; C-09 preview/final parity; C-10 AI fail-closed; C-11 AI privacy; C-12 immutable render snapshot; C-13 critical preflight; C-14 transactional output; C-15 verified output; C-16 save integrity; C-17 autosave separation; C-18 project compatibility; C-19 Windows portable target; C-20 Gemini key-pool security/failover.

## CI/Release Finding
The baseline V2 workflow for `e3bc35b...` passed regression tests, real FFmpeg checks, Windows EXE build, portable ZIP creation, artifact upload, and isolated smoke. The workflow failed only at publishing `v1.5.0` because a previous run had already created that release/tag. Treat this as release-workflow idempotence debt, not an engine/runtime regression.

## STEP 02 Constraint
External repositories/components are **candidate only**. STEP 02 must score them against the contracts above for license, maturity, maintenance, packaging, portability, parity, benchmark benefit, migration risk, and rollback feasibility.
