# Phase 173.1 Summary: LibRPA QSGW Positive Promotion To Authoritative L2

**Status:** Done
**Date:** 2026-04-14
**Axis:** Axis 2 (inter-layer connection) + Axis 4 (human evidence)

## What was done

Phase `173.1` closed the authoritative positive-L2 landing for the bounded
`LibRPA QSGW` first-principles lane.

### Code and surface changes

| Area | Change |
|------|--------|
| Positive acceptance lane | `run_librpa_qsgw_positive_l2_acceptance.py` now reuses the fresh Phase `173` target contract, performs the human-gated promotion route, and proves repo-local canonical mirror plus `consult-l2` parity on an isolated work root. |
| Regression coverage | `test_runtime_scripts.py` now covers the isolated `LibRPA QSGW` positive authoritative-L2 wrapper. |

### Authoritative unit proved

| Unit | Role | Repo-local canonical path |
|------|------|---------------------------|
| `claim:librpa-qsgw-deterministic-reduction-consistency-core` | First authoritative positive `LibRPA QSGW` landing | `research/knowledge-hub/canonical/claim-cards/claim_card--librpa-qsgw-deterministic-reduction-consistency-core.json` |

## Acceptance criteria

- [x] One bounded `LibRPA QSGW` candidate lands as an authoritative canonical `L2` claim
- [x] Backend writeback receipt is durable and replayable
- [x] Repo-local canonical mirror exists for the promoted claim
- [x] Compiled workspace knowledge report and `consult-l2` agree on the promoted claim
- [x] One dedicated acceptance lane proves the route mechanically

## Evidence

| Artifact | Location | Purpose |
|----------|----------|---------|
| `librpa-qsgw-positive-l2-acceptance.json` | `phases/173.1-librpa-qsgw-positive-promotion-to-authoritative-l2/evidence/` | Raw positive-L2 success payload with promotion receipts, canonical mirror path, and compiled/report parity |
| `pytest-librpa-qsgw-positive-l2.txt` | `phases/173.1-librpa-qsgw-positive-promotion-to-authoritative-l2/evidence/` | Isolated runtime-script receipt for the `LibRPA QSGW` authoritative-L2 wrapper |
| `receipt.md` | `phases/173.1-librpa-qsgw-positive-promotion-to-authoritative-l2/evidence/` | Human-readable replay receipt with commands and key claim paths |

## Key verified facts

- Fresh topic slug: `librpa-qsgw-deterministic-reduction-consistency-core`
- Fresh run id: `2026-04-14-035044-bootstrap`
- Research mode: `first_principles`
- Promoted claim id: `claim:librpa-qsgw-deterministic-reduction-consistency-core`
- Canonical mirror path:
  `canonical/claim-cards/claim_card--librpa-qsgw-deterministic-reduction-consistency-core.json`
- Compiled workspace knowledge report:
  `canonical/compiled/workspace_knowledge_report.json`
- `consult-l2` proof query:
  `LibRPA QSGW deterministic reduction thread consistency core`

## What this phase proved

1. The remaining user-requested `LibRPA QSGW` lane no longer stops at a target
   contract; it can now land one bounded positive authoritative claim in
   canonical `L2`.
2. The human-gated promotion route is mechanically replayable for this lane
   rather than being hidden behind pre-seeded repo state.
3. Compiled L2 and `consult-l2` now agree on the same bounded `LibRPA QSGW`
   positive authoritative unit.

## What remains for the milestone

Phase `173.2` remains: replay the positive lane and write the three-lane
convergence closure.
