# Phase 172.1 Summary: HS Model Positive Promotion To Authoritative L2

**Status:** Done
**Date:** 2026-04-14
**Axis:** Axis 2 (inter-layer connection) + Axis 4 (human evidence)

## What was done

Phase `172.1` closed the authoritative positive-L2 landing for the bounded HS
toy-model lane.

### Code and surface changes

| Area | Change |
|------|--------|
| Positive acceptance lane | `run_hs_positive_l2_acceptance.py` now reuses the fresh Phase `172` target contract, performs the human-gated promotion route, and proves repo-local canonical mirror plus `consult-l2` parity on an isolated work root. |
| Regression coverage | `test_runtime_scripts.py` now covers the isolated HS positive authoritative-L2 wrapper. |
| Promotion-gate support | The isolated transition-history and human-modification-record acceptances were rerun and passed, confirming the HS lane sits on working CLI actor bindings. |

### Authoritative unit proved

| Unit | Role | Repo-local canonical path |
|------|------|---------------------------|
| `claim:hs-like-chaos-window-finite-size-core` | First authoritative positive HS toy-model landing | `research/knowledge-hub/canonical/claim-cards/claim_card--hs-like-chaos-window-finite-size-core.json` |

## Acceptance criteria

- [x] One bounded HS-like positive candidate lands as an authoritative canonical `L2` claim
- [x] Backend writeback receipt is durable and replayable
- [x] Repo-local canonical mirror exists for the promoted claim
- [x] Compiled workspace knowledge report and `consult-l2` agree on the promoted claim
- [x] Promotion-gate binding acceptances still pass on isolated work roots
- [x] One dedicated acceptance lane proves the route mechanically

## Evidence

| Artifact | Location | Purpose |
|----------|----------|---------|
| `hs-positive-l2-acceptance.json` | `phases/172.1-hs-model-positive-promotion-to-authoritative-l2/evidence/` | Raw positive-L2 success payload with promotion receipts, canonical mirror path, and compiled/report parity |
| `pytest-hs-positive-l2.txt` | `phases/172.1-hs-model-positive-promotion-to-authoritative-l2/evidence/` | Isolated runtime-script receipt for the HS authoritative-L2 wrapper |
| `pytest-promotion-bindings.txt` | `phases/172.1-hs-model-positive-promotion-to-authoritative-l2/evidence/` | Supporting proof that the transition-history and human-modification-record acceptance lanes still pass |
| `receipt.md` | `phases/172.1-hs-model-positive-promotion-to-authoritative-l2/evidence/` | Human-readable replay receipt with commands and key claim paths |

## Key verified facts

- Fresh topic slug: `hs-like-finite-size-chaos-window-core`
- Fresh run id: `2026-04-14-025153-bootstrap`
- Research mode: `toy_model`
- Promoted claim id: `claim:hs-like-chaos-window-finite-size-core`
- Canonical mirror path:
  `canonical/claim-cards/claim_card--hs-like-chaos-window-finite-size-core.json`
- Compiled workspace knowledge report:
  `canonical/compiled/workspace_knowledge_report.json`
- `consult-l2` proof query: `HS-like finite-size chaos window robust core`

## What this phase proved

1. The HS toy-model lane no longer stops at a benchmark contract; it can now
   land one bounded positive authoritative claim in canonical `L2`.
2. The human-gated promotion route is mechanically replayable for this lane
   rather than being hidden behind pre-seeded repo state.
3. Compiled L2 and `consult-l2` now agree on the same bounded HS positive
   authoritative unit.

## What remains for the milestone

Phase `172.2` remains: replay the positive lane against the shipped HS
negative comparator on the same compiled and consultation surfaces, then route
the deferred `LibRPA QSGW` lane forward explicitly.
