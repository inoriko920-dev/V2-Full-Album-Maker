# V2 Full-Album-Maker — Project Status

## Current Phase
PLANNING

## Current STEP
STEP 04 — Hardening Stabilitas, Lifecycle, Error Handling, dan Recovery

## Gate Status
- STEP 00: PASS
- STEP 01: PASS
- STEP 02: PASS
- STEP 03: PASS
- STEP 04: PASS

## STEP 04 Final Hardening Direction
- Task/process lifecycle uses explicit CREATED -> QUEUED -> STARTING -> RUNNING -> COMPLETING/CANCELLING -> terminal states.
- New async work must carry TaskToken identity with owner scope, project token, project generation, and request generation.
- TaskSupervisor/TaskScope owns asynchronous job lifecycle.
- ProcessSupervisor owns subprocess spawn, pipe draining, cancellation, terminate/kill escalation, wait/reap, and shutdown.
- ApplicationLifecycleService owns deterministic app close ordering.
- Project switch is transactional from the user's perspective; stale old-project completions become no-op.
- Canonical Save remains immutable snapshot -> stage -> semantic verification -> atomic publish.
- Autosave/recovery remains separate from canonical Save.
- Recovery candidates must be classified explicitly as CORRUPT / STALE / SAME / NEWER / FOREIGN.
- Render bundle recovery retains versioned transaction journals and rollback/cleanup semantics.
- Cache corruption degrades to MISS/regenerate and never becomes project corruption.
- AI/network failure never blocks manual editing, save, preview, or render.
- Stable project token + generation is the target stale-result guard, replacing object identity checks over time.
- Diagnostics/logs use one cross-service sanitization policy.
- Shutdown waits are bounded; no project mutation is allowed after session/app generation is invalid.
- Failure-injection evidence is mandatory before replacing existing lifecycle/safety code.

## Current Lifecycle Gaps to Track
- Legacy render and STEP10 render currently have separate cancellation implementations.
- RenderAsyncBridge shutdown is non-blocking and can wind down after UI disposal.
- MediaPreviewCache uses daemon worker threads without an explicit close method in the audited baseline.
- AI and Spectrum preview already have generation invalidation but use service-specific executor shutdown behavior.
- Media import guards stale results using project object identity rather than target project token/generation.
- Recovery discovery safely ignores invalid files but does not yet expose typed corrupt/stale classification.
- Multiple incremental closeEvent layers make shutdown ordering implicit.

These are planning risks, not claims that every current run leaks a process.

## Coding Status
BLOCKED — planning phase.

No STEP 04 source-code, dependency, UI, schema, renderer, workflow, or project-format implementation change was made.

## Next STEP
STEP 05 — Media, Preview, Cache, Timeline, dan Project Data.

STEP 05 must design source identity/fingerprints, media probing, relink, preview request/result contracts, cache namespaces/quotas/invalidation, integer-tick timeline behavior, project-data compatibility, and migration/testing constraints using STEP 04 lifecycle/failure contracts.

## Canonical References
- Master planning DOCX.
- STEP 00 DOCX.
- STEP 01 DOCX.
- STEP 02 DOCX.
- STEP 03 DOCX.
- STEP 04 DOCX.
- docs/planning/STEP_01_AUDIT_SUMMARY.md
- docs/planning/STEP_02_DECISIONS.md
- docs/planning/STEP_03_ARCHITECTURE_DECISIONS.md
- docs/planning/STEP_04_HARDENING_DECISIONS.md
- docs/planning/STEP_04_ARTIFACT_INTEGRITY.txt
- docs/governance/PROJECT_GOVERNANCE.md
- docs/governance/AI_HANDOFF.md
