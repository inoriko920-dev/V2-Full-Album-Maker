# STEP 04 — Hardening Decisions

Status: **PASS**

This file is the fast-reference summary. The detailed STEP 04 DOCX remains the canonical planning artifact.

## D04 Decisions
- D04-01 — TaskToken is mandatory for new async task identity; legacy guards map into it gradually.
- D04-02 — ProcessSupervisor owns subprocess spawn/cancel/terminate/kill/reap and pipe draining.
- D04-03 — ApplicationLifecycleService owns deterministic app-close ordering.
- D04-04 — Project switch is transactional; project generation invalidation happens before stale completion can commit.
- D04-05 — Retry/backoff belongs to service boundaries and requires idempotency.
- D04-06 — Canonical Save remains immutable committed snapshot -> stage -> semantic verification -> atomic publish.
- D04-07 — Recovery candidate classifications are CORRUPT / STALE / SAME / NEWER / FOREIGN.
- D04-08 — Render journal recovery becomes a strict TransactionRecoveryService contract.
- D04-09 — Cache corruption degrades to MISS/regenerate; never project corruption.
- D04-10 — AI/network failure must not block manual editing/render/save.
- D04-11 — Stable project token + generation is the target stale-result guard.
- D04-12 — Sanitized diagnostics is a cross-service policy.
- D04-13 — Shutdown waits are bounded; no post-close project mutation is allowed.
- D04-14 — Failure injection is mandatory acceptance evidence for lifecycle/persistence/render changes.
- D04-15 — Existing safety code is retired only after new ownership proves parity and stronger lifecycle guarantees.

## Implementation Order for Later SOL Work
H1 typed AppError/result/diagnostic helpers -> H2 TaskToken/TaskScope/TaskSupervisor -> H3 ProcessSupervisor -> H4 ApplicationLifecycleService -> H5 ProjectPersistence recovery classification -> H6 CacheManager failure policy -> H7 migrate async stale guards -> H8 migrate RenderAsyncBridge -> H9 diagnostics -> H10 fault-injection + Windows portable lifecycle tests.

## Hard No-Go
- No big cleanup before replacement ownership is proven.
- No daemon thread treated as sufficient lifecycle ownership.
- No unbounded wait during shutdown.
- No arbitrary process-kill by name.
- No silent trust/deletion of corrupt recovery/journal evidence.
- No project mutation from background workers.
- No direct blocking network/FFmpeg call on the UI thread.
- No clearing dirty state after failed Save.
- No raw API key/bearer credential in logs.
