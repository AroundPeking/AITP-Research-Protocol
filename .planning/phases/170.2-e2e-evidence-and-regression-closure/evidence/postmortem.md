# Cross-Lane Postmortem: Milestone v1.96

**Date:** 2026-04-14
**Milestone:** v1.96 "Real Topic Promotion E2E Proof"

## What worked

### Public front door is mode-agnostic and honest

All three research modes (`formal_theory`, `toy_model`, `first_principles`)
bootstrap correctly through `AITPService().new_topic()`. The conformance
audit surface (27 checks) passes identically for all modes. No mode-specific
bootstrap failures were observed.

### Negative-result pipeline is physically honest

The HS model OTOC Lyapunov exponent failure was chosen with genuine physics
justification (integrability → no chaos). The pipeline:

- Recorded the failure with correct `failure_kind: "regime_mismatch"`
- Staged it into L2 without falsifying success
- Compiled it as `contradiction_watch` — clearly non-authoritative but durable

This proves the protocol can handle honest negative results without silently
dropping them or inflating them into false positive claims.

### Conformance audit surface is solid

27/27 pass for all four topics. The same check set works regardless of mode,
which means the conformance surface is genuinely mode-agnostic rather than
having mode-specific gaps that were not exercised.

## What was NOT proven

### No L4->L2 promotion completed for any positive lane

All three positive lanes are stuck at L3 bootstrap. The full promotion
pipeline (L0 source registration → L1 analysis → L3 candidate → L4
validation → L2 promotion) was not exercised for any of them. This means:

- We proved the front door works, not the full research pipeline
- The promotion gate, approval flow, and TPKN writeback remain untested
  for these specific topics
- Previous milestones (v1.95, Jones E2E) tested promotion on other topics,
  but not on these three research modes

### first_principles -> code_method mapping untested

Lane C (`first_principles` / LibRPA QSGW) was expected to test the
`first_principles` → `code_method` mapping when referencing an upstream
codebase. This mapping was never exercised because the topic stopped at
bootstrap.

### Toy model acceptance surface untested

Lane B (`toy_model` / HS model) was expected to surface toy-model-specific
acceptance criteria (convergence checks, benchmark workflows). These were
never reached.

## Gaps and friction points

### 1. Empty evidence directories after Phase 170

Phase 170 created `evidence/lane-a/`, `evidence/lane-b/`, `evidence/lane-c/`
directories but left them empty. The receipts were only written during
Phase 170.2 closure. This gap means Phase 170's evidence was incomplete
for ~1 day.

**Recommendation:** Evidence receipts should be written as part of each
phase's execution, not deferred to the closure phase.

### 2. `topic_state.json` missing `created_at` and `current_stage`

All four topics have `null` for `created_at` and `current_stage` in their
`topic_state.json`. This is a cosmetic gap (the conformance state and
resume_stage are correct) but it makes audit harder.

**Recommendation:** Populate `created_at` and `current_stage` during
bootstrap.

### 3. Pre-existing LSP type errors in `scratchpad_support.py` and `l2_compiler.py`

These are not caused by v1.96 work but they appear in diagnostics every
time files in those modules are touched. They should be cleaned up in a
separate phase.

## Honest scope assessment

v1.96 proved:

- ✅ Public front door works for all three research modes
- ✅ Negative-result pipeline is physically honest and durable
- ✅ Conformance audit is mode-agnostic
- ✅ All four proof lanes have durable receipts and runbooks
- ✅ Regression replay is mechanical

v1.96 did NOT prove:

- ❌ Full L0→L2 promotion for formal derivation topics
- ❌ Full L0→L2 promotion for toy model topics
- ❌ Full L0→L2 promotion for first_principles topics
- ❌ first_principles → code_method mapping
- ❌ Toy model convergence/benchmark acceptance

## Future work

1. **Phase 171+:** Run at least one positive lane through full L0→L2 promotion
2. **Type error cleanup:** Fix pre-existing LSP errors in scratchpad_support.py and l2_compiler.py
3. **Metadata gap:** Populate `created_at` and `current_stage` during bootstrap
4. **Evidence hygiene:** Write receipts during each phase, not deferred
