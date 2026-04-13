# Phase 170.2 Summary: E2E Evidence and Regression Closure

**Status:** Done
**Date:** 2026-04-14
**Axis:** Axis 4 (human evidence) + Axis 3 (durable regression surfaces)

## What was done

Phase 170.2 closed all four proof lanes from milestone v1.96 with durable
evidence, replayable regression runbooks, and an honest cross-lane postmortem.

### Artifacts produced

| Artifact | Location | Purpose |
|----------|----------|---------|
| receipt-lane-a.md | `phases/170/evidence/lane-a/` | Formal derivation (von Neumann) bootstrap receipt |
| receipt-lane-b.md | `phases/170/evidence/lane-b/` | Toy model (HS model) bootstrap receipt |
| receipt-lane-c.md | `phases/170/evidence/lane-c/` | First principles (LibRPA QSGW) bootstrap receipt |
| receipt-lane-d.md | `phases/170.2/evidence/` | Negative-result cross-reference receipt |
| RUNBOOK-E.md | `phases/170.2/` | Master regression runbook for all 4 lanes |
| postmortem.md | `phases/170.2/evidence/` | Cross-lane postmortem with honest scope assessment |
| PLAN.md | `phases/170.2/` | Phase plan (5 steps, 8 acceptance criteria) |

### Acceptance criteria — all met

- [x] Durable receipt for Lane A (formal_derivation)
- [x] Durable receipt for Lane B (toy_model)
- [x] Durable receipt for Lane C (first_principles)
- [x] Durable receipt for Lane D (negative_result)
- [x] Master regression runbook (RUNBOOK-E)
- [x] Cross-lane postmortem
- [x] Phase 170.2 SUMMARY.md
- [x] STATE.md and ROADMAP.md updated

## Key findings

### What v1.96 proved

1. **Public front door is mode-agnostic** — all three research modes
   (`formal_derivation`, `toy_model`, `first_principles`) bootstrap correctly
   through `AITPService().new_topic()` with 27/27 conformance.

2. **Negative-result pipeline is physically honest** — the HS model OTOC
   failure was recorded with `failure_kind: "regime_mismatch"`, staged into L2,
   and compiled as `contradiction_watch` without falsifying success.

3. **Conformance audit surface is solid** — the same 27-check set passes
   identically for all four topics regardless of mode.

4. **Regression replay is mechanical** — RUNBOOK-E provides step-by-step
   replay instructions for all four lanes.

### What v1.96 did NOT prove

1. **No full L0→L2 promotion for any positive lane** — all three stopped at
   L3 bootstrap.
2. **first_principles → code_method mapping untested** — Lane C never
   reached codebase-backed analysis.
3. **Toy model acceptance surface untested** — Lane B never reached
   convergence or benchmark checks.

### Friction points

1. Phase 170 left evidence directories empty — receipts were deferred to
   Phase 170.2.
2. `topic_state.json` has `null` for `created_at` and `current_stage` on all
   four topics (cosmetic gap).
3. Pre-existing LSP type errors in `scratchpad_support.py` and `l2_compiler.py`
   are unrelated but noisy.

## Milestone closure

With Phase 170.2 complete, all three phases of milestone v1.96 are done:

- Phase 170: Three-mode positive promotion proof ✅
- Phase 170.1: Negative-result promotion proof ✅
- Phase 170.2: E2E evidence and regression closure ✅

The milestone proved the promotion pipeline's front door works honestly for all
three research modes and for negative results. The full L0→L2 promotion path
remains the next bounded proof target.
