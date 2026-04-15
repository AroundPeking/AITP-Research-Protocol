# Plan: 173.1-01 — Promote one bounded positive `LibRPA QSGW` unit into authoritative canonical L2 and prove compiled/read-path parity

**Phase:** 173.1
**Axis:** Axis 2 (inter-layer connection) + Axis 4 (human evidence)
**Requirements:** REQ-QSGW-03, REQ-QSGW-04

## Goal

Take the bounded `LibRPA QSGW` deterministic-reduction consistency core from
Phase `173` and land it as one authoritative canonical `L2` claim with durable
promotion receipts, repo-local mirror writeback, and `consult-l2` parity.

## Planned Route

### Step 1: Lock the promoted unit target and human-gated route

**Artifacts to write during execution:**
- `.planning/phases/173.1-librpa-qsgw-positive-promotion-to-authoritative-l2/TARGET.md`
- `.planning/phases/173.1-librpa-qsgw-positive-promotion-to-authoritative-l2/RUNBOOK.md`

Pin down:

- fresh topic slug
- bounded candidate id
- authoritative target unit id
- canonical mirror path
- consultation query
- explicit preserved non-claims

### Step 2: Add the isolated positive-L2 acceptance lane

**Files:**
- `research/knowledge-hub/runtime/scripts/run_librpa_qsgw_positive_l2_acceptance.py`
- `research/knowledge-hub/tests/test_runtime_scripts.py`

The script should:

- reuse the Phase `173` target-contract acceptance on a fresh work root
- materialize a minimal TPKN backend
- run `request_promotion`, `approve_promotion`, and `promote_candidate`
- verify the canonical claim-card mirror exists
- verify the compiled workspace knowledge report includes the promoted claim
- verify `consult-l2` returns the same promoted claim

### Step 3: Keep the promotion honest and bounded

**Likely files touched if needed:**
- `research/knowledge-hub/runtime/scripts/run_librpa_qsgw_positive_l2_acceptance.py`
- helper modules only if a real promotion gap appears

Do not widen this phase into:

- full QSGW convergence claims
- broad workflow portability claims
- topic-skill projection workarounds unrelated to the bounded promoted claim

### Step 4: Leave durable evidence for phase closure

**Artifacts to write during execution:**
- `.planning/phases/173.1-librpa-qsgw-positive-promotion-to-authoritative-l2/SUMMARY.md`
- `.planning/phases/173.1-librpa-qsgw-positive-promotion-to-authoritative-l2/evidence/`

## Acceptance Criteria

- [ ] one bounded `LibRPA QSGW` candidate lands as an authoritative canonical `L2` claim
- [ ] backend writeback receipt is durable and replayable
- [ ] repo-local canonical mirror exists for the promoted claim
- [ ] compiled workspace knowledge report and `consult-l2` agree on the promoted claim
- [ ] one dedicated acceptance lane proves the route mechanically
