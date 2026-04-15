# Phase 171 Summary: Formal Positive Lane To Authoritative L2

**Status:** Done
**Date:** 2026-04-14
**Axis:** Axis 2 (inter-layer connection) + Axis 4 (human evidence and read-path trust)

## What was done

Phase 171 closed the first real positive `L0 -> L2` route in `v1.97` for the
formal lane.

The fresh public-front-door Jones wrapper now proves one bounded positive
theorem can:

1. enter through `AITPService().new_topic()` as a fresh `formal_derivation`
   topic,
2. reuse explicit Jones source rows honestly,
3. promote through the existing backend-side formal closure machinery,
4. mirror into repo-local canonical `L2`, and
5. reappear on the compiled L2 and `consult-l2` read surfaces.

### Code and surface changes

| Area | Change |
|------|--------|
| Promotion writeback | `candidate_promotion_support.py` now mirrors successful backend promotions into repo-local canonical `L2` and refreshes the canonical index. |
| L2 graph / consultation | `l2_graph.py` now treats `theorem_card` as a first-class canonical unit family, so theorem mirrors appear in index, compiled reports, and consultation. |
| Positive acceptance lane | `run_formal_positive_l2_acceptance.py` now compiles workspace memory/graph/knowledge reports and checks natural-language `consult-l2` parity after promotion. |
| Regression coverage | `test_aitp_service.py` covers repo-local canonical mirror behavior; `test_l2_graph_activation.py` covers theorem-card index + consultation visibility. |

### Authoritative units proved

| Unit | Role | Repo-local canonical path |
|------|------|---------------------------|
| `theorem:jones-ch4-finite-product` | First authoritative positive theorem landing | `research/knowledge-hub/canonical/theorem-cards/theorem_card--jones-ch4-finite-product.json` |
| `topic_skill_projection:fresh-jones-finite-dimensional-factor-closure` | Reusable route capsule for the fresh formal topic | `research/knowledge-hub/canonical/topic-skill-projections/topic_skill_projection--fresh-jones-finite-dimensional-factor-closure.json` |

## Acceptance criteria

- [x] One fresh `formal_derivation` topic entered through the public front door
- [x] One bounded positive candidate landed as an authoritative canonical `L2` unit
- [x] Backend writeback receipt is durable and replayable
- [x] Promotion gate, canonical writeback, compiled L2 reports, and `consult-l2` agree on the promoted unit
- [x] One dedicated acceptance lane proves the route mechanically

## Evidence

### Stored in this phase directory

| Artifact | Location | Purpose |
|----------|----------|---------|
| `formal-positive-l2-acceptance.json` | `phases/171-formal-positive-lane-to-authoritative-l2/evidence/` | Raw success payload for the fresh public-front-door wrapper, including backend receipts and repo-local L2 parity |
| `pytest-promotion-mirror.txt` | `phases/171-formal-positive-lane-to-authoritative-l2/evidence/` | Targeted proof that promotion writes a repo-local canonical mirror and surfaces it in compiled L2 |
| `pytest-theorem-card-consult.txt` | `phases/171-formal-positive-lane-to-authoritative-l2/evidence/` | Targeted proof that theorem-card units index and retrieve correctly through consultation |
| `receipt.md` | `phases/171-formal-positive-lane-to-authoritative-l2/evidence/` | Human-readable replay receipt with commands and key unit paths |

### Key verified facts

- Fresh topic slug: `fresh-jones-finite-dimensional-factor-closure`
- Bootstrap run id: `2026-04-14-015101-bootstrap`
- Closure run id: `2026-04-14-015101-jones-close`
- Entry conformance: `pass`
- Backend theorem promotion: `promoted`
- Repo-local theorem mirror: `research/knowledge-hub/canonical/theorem-cards/theorem_card--jones-ch4-finite-product.json`
- Repo-local projection mirror: `research/knowledge-hub/canonical/topic-skill-projections/topic_skill_projection--fresh-jones-finite-dimensional-factor-closure.json`
- Compiled L2 parity:
  - `research/knowledge-hub/canonical/compiled/workspace_memory_map.json`
  - `research/knowledge-hub/canonical/compiled/workspace_graph_report.json`
  - `research/knowledge-hub/canonical/compiled/workspace_knowledge_report.json`
- `consult-l2` proof query: `Jones finite product theorem packet`

## What this phase proved

1. The public front door is no longer only a bootstrap surface for the formal
   lane; it can now end at an authoritative positive repo-local `L2` unit.
2. Positive backend promotion is no longer hidden behind an external backend
   only; the same landing now materializes in the repository's canonical L2.
3. The compiled read path and `consult-l2` now expose the same bounded theorem
   that the backend promotion receipts claim.

## What this phase did not prove

1. Positive and negative authoritative rows have not yet been stress-tested
   together on the same compiled/retrieval surfaces. That is Phase `171.1`.
2. The replay lane and carry-over routing for `toy_model` and
   `first_principles` are not closed yet. That is Phase `171.2`.
