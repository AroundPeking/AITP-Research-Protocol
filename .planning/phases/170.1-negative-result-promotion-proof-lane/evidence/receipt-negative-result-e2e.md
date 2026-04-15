# Phase 170.1 Evidence Receipt: Negative-Result E2E Proof

**Date:** 2026-04-13
**Operator:** phase-170.1-runner
**Topic slug:** `hs-model-otoc-lyapunov-exponent-failure`

## Summary

One honest physics-failure bounded route traveled from topic bootstrap through
the public front door into L2 staging as `contradiction_watch`.

## Step-by-step receipts

### Step 1: Failure scenario chosen

- **Lane B topic reused:** `haldane-shastry-model-quantum-chaos-and-lyapunov-spectrum`
- **Failure question:** "Does the Haldane-Shastry model exhibit a well-defined OTOC-based quantum Lyapunov exponent at finite N?"
- **Expected answer:** No. The HS model is integrable; OTOC growth is power-law, not exponential; the MSS chaos bound does not apply.
- **Failure kind:** `regime_mismatch`

### Step 2: Fresh topic bootstrapped through public front door

- **Bootstrap command:** `aitp bootstrap --topic "hs-model-otoc-lyapunov-exponent-failure" --statement "..."` 
- **Conformance:** 27/27 pass
- **Topic state:** `runtime/topics/hs-model-otoc-lyapunov-exponent-failure/topic_state.json`
- **Conformance state:** `runtime/topics/hs-model-otoc-lyapunov-exponent-failure/conformance_state.json`

### Step 3: Negative result recorded via scratchpad

- **Entry ID:** `scratch-negative-result-2026-04-13t23-03-43-08-00`
- **Failure kind:** `regime_mismatch`
- **Scratchpad active:** `negative_result_count: 1`
- **Scratchpad path:** `runtime/topics/hs-model-otoc-lyapunov-exponent-failure/scratchpad.active.json`

### Step 4: Staged into L2 and compiled as contradiction_watch

- **Stage command:** `python -m knowledge_hub.aitp_cli stage-negative-result --title "HS model OTOC Lyapunov exponent: regime mismatch" --summary "..." --failure-kind regime_mismatch --updated-by phase-170.1-runner --json`
- **Staged entry ID:** `staging:hs-model-otoc-lyapunov-exponent-regime-mismatch`
- **Entry kind:** `negative_result`
- **Status:** `staged`
- **Authoritative:** `false`
- **Staged entry path:** `canonical/staging/entries/staging--hs-model-otoc-lyapunov-exponent-regime-mismatch.json`
- **Staged note path:** `canonical/staging/entries/staging--hs-model-otoc-lyapunov-exponent-regime-mismatch.md`

- **Compile command:** `python -m knowledge_hub.aitp_cli compile-l2-knowledge-report --json`
- **Compiled report:** `canonical/compiled/workspace_knowledge_report.json`
- **Contradiction row count:** 6 (1 real + 5 pre-existing synthetic)
- **HS model row in knowledge_rows:**
  - `knowledge_state: "contradiction_watch"`
  - `authority_level: "non_authoritative_staging"`
  - `change_status: "added"`

### Step 5: Durable evidence

- This receipt file
- RUNBOOK-D.md (reproduction steps)
- SUMMARY.md (phase completion summary)

## Key artifact pointers

| Artifact | Path |
|----------|------|
| Topic state | `runtime/topics/hs-model-otoc-lyapunov-exponent-failure/topic_state.json` |
| Conformance state | `runtime/topics/hs-model-otoc-lyapunov-exponent-failure/conformance_state.json` |
| Scratchpad active | `runtime/topics/hs-model-otoc-lyapunov-exponent-failure/scratchpad.active.json` |
| Scratchpad entries | `runtime/topics/hs-model-otoc-lyapunov-exponent-failure/scratchpad.entries.jsonl` |
| Staged entry (JSON) | `canonical/staging/entries/staging--hs-model-otoc-lyapunov-exponent-regime-mismatch.json` |
| Staged entry (MD) | `canonical/staging/entries/staging--hs-model-otoc-lyapunov-exponent-regime-mismatch.md` |
| Staging manifest | `canonical/staging/workspace_staging_manifest.json` |
| Compiled report (JSON) | `canonical/compiled/workspace_knowledge_report.json` |
| Compiled report (MD) | `canonical/compiled/workspace_knowledge_report.md` |

## Acceptance criteria checklist

- [x] One fresh topic bootstrapped through the public front door with a bounded question designed to fail
- [x] The bounded loop discovers the failure honestly (physics-grounded: HS model is integrable)
- [x] `record_negative_result_payload()` writes a durable negative result entry
- [x] `stage-negative-result` stages the entry into L2 staging manifest
- [x] `compile-l2-knowledge-report` marks it as `contradiction_watch`
- [x] The scratchpad reflects `negative_result_count >= 1`
- [x] All receipts saved in `evidence/` directory
- [x] RUNBOOK-D.md written with reproduction steps
