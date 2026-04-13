# Phase 170.1 Summary: Negative-Result Promotion Proof Lane

**Status:** Complete
**Date:** 2026-04-13
**Axis:** Axis 2 (inter-layer connection) + Axis 1 (layer capability/honesty)

## Goal

Prove one bounded failed route can land as canonical `negative_result` with the
same honesty and durability as a positive promotion.

## What was done

1. **Chose a physics-honest failure scenario:** The Haldane-Shastry model (Lane B)
   was used to ask whether it exhibits a well-defined OTOC-based quantum Lyapunov
   exponent. The answer is no, because the HS model is integrable.

2. **Bootstrapped a fresh topic through the public front door:**
   - Slug: `hs-model-otoc-lyapunov-exponent-failure`
   - Conformance: 27/27 pass
   - No hidden seed state was used

3. **Recorded the negative result via the scratchpad API:**
   - `record_negative_result_payload()` wrote a durable entry with
     `failure_kind: "regime_mismatch"`
   - Scratchpad now shows `negative_result_count: 1`

4. **Staged the negative result into L2 and compiled the knowledge report:**
   - `stage-negative-result` created staging entry with `entry_kind: "negative_result"`, `status: "staged"`, `authoritative: false`
   - `compile-l2-knowledge-report` marked it as `contradiction_watch`
   - `contradiction_row_count` increased from 5 to 6 (1 real + 5 synthetic)

5. **Saved durable evidence:** Receipt, RUNBOOK-D.md, and this SUMMARY.md

## Key findings

- The negative-result pipeline works end-to-end for a real physics topic, not
  just synthetic acceptance fixtures
- `l2_compiler._staging_knowledge_state()` correctly assigns
  `contradiction_watch` to `negative_result` entries
- The staging manifest and compiled knowledge report both reflect the new entry
- The scratchpad accurately tracks `negative_result_count` and
  `latest_negative_result_summary`

## Acceptance criteria

- [x] One fresh topic bootstrapped through the public front door with a bounded question designed to fail
- [x] The bounded loop discovers the failure honestly
- [x] `record_negative_result_payload()` writes a durable negative result entry
- [x] `stage-negative-result` stages the entry into L2 staging manifest
- [x] `compile-l2-knowledge-report` marks it as `contradiction_watch`
- [x] The scratchpad reflects `negative_result_count >= 1`
- [x] All receipts saved in `evidence/` directory
- [x] RUNBOOK-D.md written with reproduction steps

## Artifacts

| Artifact | Location |
|----------|----------|
| Evidence receipt | `.planning/phases/170.1-.../evidence/receipt-negative-result-e2e.md` |
| RUNBOOK-D | `.planning/phases/170.1-.../RUNBOOK-D.md` |
| Plan | `.planning/phases/170.1-.../PLAN.md` |
| Topic state | `runtime/topics/hs-model-otoc-lyapunov-exponent-failure/` |
| Staged entry | `canonical/staging/entries/staging--hs-model-otoc-lyapunov-exponent-regime-mismatch.json` |
| Compiled report | `canonical/compiled/workspace_knowledge_report.json` |

## Dependencies unblocked

- Phase 170.2 (E2E Evidence and Regression Closure) can now proceed
