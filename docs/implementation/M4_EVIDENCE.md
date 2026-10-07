# M4 — RenderEngine Facade Evidence

Status: **PASS**

## Candidate

- Branch: `impl-m4-render-facade`
- M3 rollback/base: `b8ff524b94f85d6b090a846e2b78c18c51983757`
- Validated runtime candidate: `5f7a428945102f08197bdbe91d7036fbff91c750`
- GitHub Actions run: `37591981581`

## Scope Evidence

Runtime changes are limited to:
- new `src/full_album_maker/render_engine.py`;
- AppKernel/CompositionRoot ownership wiring;
- STEP10 Qt async bridge routing through RenderEngine.

No compiler implementation was rewritten. No M5/M6/M7, UI redesign, schema,
dependency, build, or release work is part of M4.

## Q0 / Q1 Results

Main job `m4-render-facade`: **SUCCESS**
- Q0 compile: PASS
- M0–M4 + entrypoint contracts: 43 passed, 1 skipped
- STEP10 render parity: 38 passed
- render safety/lifecycle: 21 passed, 9 skipped
- 200-song/~3-hour packed/free structural stress: 2 passed
- production canonical Save: 1 passed
- nine-workspace read-only production launch characterization: 1 passed

Targeted job `real-ffmpeg-m4`: **SUCCESS**
- 2 passed
- includes the M4 RenderEngine real-FFmpeg test and the existing STEP10
  real-FFmpeg verified-output test.

## Preserved Safety Contract

The real-FFmpeg path is:
RenderEngine -> existing RenderExecutor -> existing compiler chain -> FFmpeg ->
ffprobe verification -> transactional publication.

The final file is not published before verification. Existing cancellation,
staging cleanup, output/source collision checks, capability policy, and log
sanitization remain in the underlying proven implementation and are covered by
the focused parity/lifecycle tests.

## Lifecycle Note

M4 does not implement H3 ProcessSupervisor. The existing STEP10 process runner
continues to own process termination. RenderEngine adds only an application
facade and an overlapping-attempt guard.

## Final-Head Rule

This evidence records the first validated runtime candidate. The subsequent
evidence/status-only commit changes documentation only. The same
`v2-m4-render-facade.yml` workflow must be green on the final branch head
before handoff is considered complete.
