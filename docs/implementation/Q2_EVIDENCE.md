# Q2 Integration Evidence

Status: **PASS**

## Branch / candidate

- Branch: `quality-q2-integration`
- M9 base:
  `16e151ccc8cb72e662df268eb4be0074b8226e56`
- Q2 workflow commit:
  `2670bb6de4892043e11236110e3f28736fd8f20a`
- validated fix/candidate:
  `98a8f096990f1135989997f4047340c3b5bbb270`
- successful Actions run:
  `37601017717`

## Full regression floor

Inventory:
- 123 Python test files
- planning minimum: 115

Full pytest:
- 557 passed
- 93 skipped
- 0 failed
- 59.26 s

## Focused integration

Cross-workspace/session/lifecycle:
- 60 passed
- 0 failed

M0–M9 ownership smoke:
- 72 passed
- 4 skipped
- 0 failed

## First-run failure evidence

Initial Actions run:
`37600732187`

Full pytest result:
- 553 passed
- 93 skipped
- 4 failed

All four failures were `tests/test_async_import.py` and shared one cause:
`async_import.probe_duration` compatibility surface had disappeared after M5
facade routing.

Q2 treated this as a real regression, not a stale test.

## Remediation evidence

`async_import.py` now keeps a direct-window compatibility
`MediaProbeService` adapter whose callbacks resolve the legacy monkeypatchable
probe surfaces at call time.

AppKernel production windows continue to capture the exact bound M5
MediaProbeService, so the compatibility fix does not restore legacy production
ownership.

The successful second run proves both:
- old direct-window behavior is compatible again;
- M0–M9 facade ownership contracts remain green.

## Scope discipline

Q2 diff from the final M9 head contains only:
- Q2 workflow;
- the demonstrated async-import compatibility regression fix.

No Q3/Q4/Q5 work is included.

## Final-head rule

A documentation-only final Q2 commit follows this evidence. The same Q2
workflow must remain green on that final branch head before handoff is complete.
