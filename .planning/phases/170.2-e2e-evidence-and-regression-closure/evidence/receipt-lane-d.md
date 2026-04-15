# Receipt Lane D: Negative Result (HS Model OTOC Failure)

**Lane:** D (negative-result proof)
**Research mode:** `exploratory_general` (auto-selected)
**Topic slug:** `hs-model-otoc-lyapunov-exponent-failure`
**Date:** 2026-04-14

## What was proven

The AITP negative-result pipeline works end-to-end for a real physics topic:

1. A bounded failure scenario was chosen with physics-honest justification
   (HS model is integrable → no well-defined OTOC Lyapunov exponent)
2. The topic was bootstrapped through the public front door
3. `record_negative_result_payload()` wrote a durable negative result entry
4. `stage-negative-result` staged it into the L2 staging manifest
5. `compile-l2-knowledge-report` marked it as `contradiction_watch`

## Primary receipt

The detailed step-by-step receipt is in Phase 170.1's evidence directory:

`.planning/phases/170.1-negative-result-promotion-proof-lane/evidence/receipt-negative-result-e2e.md`

## Cross-lane context

This lane intentionally reuses the same physics system as Lane B (Haldane-Shastry
model) but asks a question designed to fail. The negative result is:

- **Failure kind:** `regime_mismatch`
- **Summary:** The HS model is integrable and does not exhibit quantum chaos,
  so OTOC-based Lyapunov exponent extraction yields no well-defined positive exponent.
- **Scratchpad entry ID:** `scratch-negative-result-2026-04-13t23-03-43-08-00`
- **Staging entry ID:** `staging:hs-model-otoc-lyapunov-exponent-regime-mismatch`

## Compiled knowledge report evidence

After staging and compilation:

- `contradiction_row_count: 6` (1 real + 5 synthetic)
- HS model entry appears with `knowledge_state: "contradiction_watch"`
- `authority_level: "non_authoritative_staging"`
- `change_status: "added"`

## Conformance

| Check | Result |
|-------|--------|
| Topic created via public front door | Yes |
| No hidden seed state used | Yes |
| Conformance audit: 27/27 pass | Confirmed |
| Negative result recorded via scratchpad | Confirmed |
| Staged into L2 manifest | Confirmed |
| Compiled as `contradiction_watch` | Confirmed |

## Runbook

See `RUNBOOK-D.md` in `.planning/phases/170.1-negative-result-promotion-proof-lane/`.

## Regression replay

See Phase 170.1 RUNBOOK-D.md for full reproduction steps. Quick summary:

```bash
# 1. Bootstrap topic
aitp bootstrap --topic "HS model OTOC Lyapunov exponent failure" --statement "..."

# 2. Record negative result via Python API
# record_negative_result_payload(topic_slug, summary, failure_kind, ...)

# 3. Stage into L2
python -m knowledge_hub.aitp_cli stage-negative-result --title "..." --summary "..." --failure-kind regime_mismatch

# 4. Compile knowledge report
python -m knowledge_hub.aitp_cli compile-l2-knowledge-report

# 5. Verify contradiction_watch appears
# Check workspace_knowledge_report.json for knowledge_state: "contradiction_watch"
```
