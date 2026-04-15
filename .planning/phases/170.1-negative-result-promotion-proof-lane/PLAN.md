# Phase 170.1 Plan: Negative-Result Promotion Proof Lane

**Axis:** Axis 2 (inter-layer connection) + Axis 1 (layer capability/honesty)
**Status:** Complete
**Date:** 2026-04-13

## Goal

Prove one bounded failed route can land as canonical `negative_result` with the
same honesty and durability as a positive promotion.

## Motivation

- `negative_result` now has a schema and promotion path via
  `record_negative_result_payload()` and the `stage-negative-result` CLI surface
- The `l2_compiler` marks `negative_result` entries as `contradiction_watch` in
  the compiled knowledge report
- The L2 knowledge-report acceptance script (`run_l2_knowledge_report_acceptance.py`)
  already verifies that a staged negative result appears as a
  `contradiction_watch` knowledge row
- But no full **real-topic** route has proven that an honest failure case can
  travel from topic bootstrap → bounded loop → negative result → L2 staging
  → contradiction_watch with durable receipts
- The milestone should prove that AITP learns from failed bounded routes rather
  than only from successful ones

## Background: What surfaces exist

### Negative-result recording

- `scratchpad_support.record_negative_result_payload()` writes a `negative_result`
  entry into the topic's scratchpad entries, with fields: `summary`,
  `failure_kind`, `details`, `run_id`, `candidate_id`, `related_artifacts`
- The scratchpad payload tracks `negative_result_count` and
  `latest_negative_result_summary`

### Negative-result staging

- `l2_compiler._staging_knowledge_state()` marks any entry with
  `entry_kind == "negative_result"` as `contradiction_watch`
- `stage-negative-result` CLI command stages a negative result into the L2
  staging manifest

### Acceptance evidence

- `run_l2_knowledge_report_acceptance.py` stages a negative result with
  `failure_kind: regime_mismatch` and verifies it appears as
  `contradiction_watch` in the compiled knowledge report
- But this acceptance script uses synthetic fixtures on an isolated temp kernel,
  not a real topic through the public front door

## Plan (170.1-01): One honest negative-result promotion proof

### Step 1: Choose the failure scenario

Pick a bounded route that will genuinely fail. Good candidates:

- **Portability extrapolation** — try to extrapolate a result from one regime
  (e.g., weak coupling) to another (strong coupling) where it is known not to
  hold
- **Regime mismatch** — try to apply a toy-model technique outside its validity
  regime (e.g., apply perturbation theory at strong coupling)
- **Conjecture refutation** — start with a plausible but false conjecture and
  let the bounded loop discover the counterexample

**Chosen scenario:** Use one of the three existing Phase 170 topics and
introduce a deliberately bounded sub-route that will fail honestly. The best
candidate is the **Lane B** topic
(`haldane-shastry-model-quantum-chaos-and-lyapunov-spectrum`) because:
- It is a `toy_model` mode, which is the least-tested lane
- Quantum chaos indicators can be shown to fail in certain limits
- The failure is physics-honest rather than engineering-synthetic

### Step 2: Bootstrap a failure-bound sub-topic through the public front door

- Use `AITPService().new_topic()` to create a fresh topic with a bounded
  question that is expected to fail
- Example: "Does the Haldane-Shastry model exhibit a well-defined OTOC-based
  quantum Lyapunov exponent at finite N?"
- The answer should be: no, not in the naive sense, because the HS model is
  integrable and OTOC growth does not follow the exponential chaos-bound
  pattern at finite N

### Step 3: Run a bounded loop that discovers the failure

- Run `aitp loop` on the failure-bound topic
- The bounded loop should discover that the OTOC does not grow exponentially
  for the integrable HS model
- Record this as a `negative_result` via `record_negative_result_payload()`

### Step 4: Stage the negative result into L2

- Use `stage-negative-result` CLI to stage the negative result
- Run `compile-l2-knowledge-report` to verify the negative result appears as
  `contradiction_watch`
- Verify the scratchpad reflects the negative result count and summary

### Step 5: Durable evidence

- Save all receipts in `evidence/` directory
- Write a RUNBOOK-D.md with the full reproduction steps
- Verify the acceptance test surface handles this real negative result correctly

## Acceptance criteria

- [ ] One fresh topic bootstrapped through the public front door with a
      bounded question designed to fail
- [ ] The bounded loop discovers the failure honestly (not synthetic)
- [ ] `record_negative_result_payload()` writes a durable negative result entry
- [ ] `stage-negative-result` stages the entry into L2 staging manifest
- [ ] `compile-l2-knowledge-report` marks it as `contradiction_watch`
- [ ] The scratchpad reflects `negative_result_count >= 1`
- [ ] All receipts saved in `evidence/` directory
- [ ] RUNBOOK-D.md written with reproduction steps

## Risks

1. **The bounded loop may not discover the failure in one step** — may need
   multiple loop iterations or manual intervention to record the negative result
2. **The CLI surface may have gaps for negative-result staging** — the
   acceptance script proves the surface works with synthetic fixtures but real
   topic flow may expose issues
3. **Choosing a too-trivial failure** — the failure must be physics-honest, not
   just a deliberately wrong input
