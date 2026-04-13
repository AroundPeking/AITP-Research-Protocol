# Phase 171.1 Summary: L2 Surface Hardening Under Real Positive/Negative Coexistence

**Status:** Done
**Date:** 2026-04-14
**Axis:** Axis 1 (layer capability) + Axis 3 (durable data recording)

## What was done

Phase 171.1 turned the Phase `171` positive-L2 landing into a stricter L2 trust
proof by forcing one authoritative positive theorem row and one staged
`negative_result -> contradiction_watch` row to coexist on the same compiled
and consultation surfaces.

### Code and surface changes

| Area | Change |
|------|--------|
| Staging retrieval parity | `l2_staging.py` now refreshes `canonical/staging/staging_index.jsonl` whenever the workspace staging manifest is materialized, so staged negative results become visible to `consult-l2(include_staging=True)`. |
| Coexistence acceptance lane | `run_positive_negative_l2_coexistence_acceptance.py` now replays the fresh formal positive landing, stages one bounded negative result with overlapping query terms, and proves compiled/report/consult coexistence on an isolated work root. |
| Regression coverage | `test_l2_graph_activation.py` now checks positive authoritative rows and contradiction rows together; `test_runtime_scripts.py` now checks the isolated coexistence acceptance script end to end. |

## Acceptance criteria

- [x] Compiled knowledge report includes both the positive authoritative row and the contradiction-watch row
- [x] The positive row remains `authoritative_canonical/trusted`
- [x] The negative row remains `non_authoritative_staging/contradiction_watch`
- [x] Provenance refs remain present on both rows
- [x] `consult-l2(..., include_staging=True)` exposes both sides without mixing authority
- [x] A dedicated coexistence acceptance lane runs mechanically on an isolated work root

## Evidence

### Stored in this phase directory

| Artifact | Location | Purpose |
|----------|----------|---------|
| `pytest-coexistence-unit.txt` | `phases/171.1-l2-surface-hardening-under-real-positive-negative-coexistence/evidence/` | Unit-level proof that compiled report + consultation preserve positive/negative authority separation |
| `pytest-coexistence-script.txt` | `phases/171.1-l2-surface-hardening-under-real-positive-negative-coexistence/evidence/` | Isolated runtime-script proof for the coexistence acceptance lane |
| `positive-negative-l2-coexistence-acceptance.json` | `phases/171.1-l2-surface-hardening-under-real-positive-negative-coexistence/evidence/` | Raw standalone coexistence payload with theorem row, contradiction row, and consultation ids |
| `receipt.md` | `phases/171.1-l2-surface-hardening-under-real-positive-negative-coexistence/evidence/` | Human-readable replay receipt with commands and key row states |

### Key verified facts

- Positive theorem id: `theorem:jones-ch4-finite-product`
- Negative contradiction row id: `staging:jones-finite-product-theorem-classification-failure`
- Knowledge report theorem row state: `authoritative_canonical / trusted`
- Knowledge report negative row state: `non_authoritative_staging / contradiction_watch`
- Coexistence query: `Jones finite product theorem classification failure`
- `consult-l2` canonical ids include `theorem:jones-ch4-finite-product`
- `consult-l2` staged ids include `staging:jones-finite-product-theorem-classification-failure`

## What this phase proved

1. Repo-local L2 can now expose a real authoritative positive formal theorem
   and a real staged contradiction row together without flattening their
   authority labels.
2. Staged negative results are now visible to the consultation surface through
   the same durable staging index that the compiled report logic already
   expects.
3. The coexistence proof is replayable on an isolated work root rather than
   only in the main repository state.

## What remains for the milestone

Phase `171.2` remains: write the replay/runbook closure and route the deferred
`toy_model` and `first_principles` blockers into explicit next actions.
