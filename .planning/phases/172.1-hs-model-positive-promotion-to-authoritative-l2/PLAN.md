# Plan: 172.1-01 — Promote one bounded positive HS-model unit into authoritative canonical L2 and prove compiled/read-path parity

**Phase:** 172.1
**Axis:** Axis 2 (inter-layer connection) + Axis 4 (human evidence)
**Requirements:** REQ-HS-03, REQ-HS-04

## Goal

Take the benchmark-backed HS-like finite-size chaos-window core from Phase
`172` and land it as one authoritative canonical `L2` claim with durable
promotion receipts, repo-local mirror writeback, and `consult-l2` parity.

## Planned Route

### Step 1: Lock the promoted unit target and human-gated route

**Artifacts to write during execution:**
- `.planning/phases/172.1-hs-model-positive-promotion-to-authoritative-l2/TARGET.md`
- `.planning/phases/172.1-hs-model-positive-promotion-to-authoritative-l2/RUNBOOK.md`

Pin down:

- fresh topic slug
- reference candidate id
- authoritative target unit id
- canonical mirror path
- consultation query
- preserved HS negative comparator

### Step 2: Add the isolated positive-L2 acceptance lane

**Files:**
- `research/knowledge-hub/runtime/scripts/run_hs_positive_l2_acceptance.py`
- `research/knowledge-hub/tests/test_runtime_scripts.py`

The script should:

- reuse the Phase `172` target-contract acceptance on a fresh work root
- materialize a minimal TPKN backend
- run `request_promotion`, `approve_promotion`, and `promote_candidate`
- verify the canonical claim-card mirror exists
- verify the compiled workspace knowledge report includes the promoted claim
- verify `consult-l2` returns the same promoted claim

### Step 3: Re-verify promotion-gate bindings

**Commands to preserve as evidence:**
- `python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "transition_history_acceptance_script_runs_on_isolated_work_root or human_modification_record_acceptance_script_runs_on_isolated_work_root" -q`

Use this as supporting evidence that the promotion route still honors the
CLI-side actor fields required by the human-gated HS promotion lane.

### Step 4: Leave durable evidence for phase closure

**Artifacts to write during execution:**
- `.planning/phases/172.1-hs-model-positive-promotion-to-authoritative-l2/SUMMARY.md`
- `.planning/phases/172.1-hs-model-positive-promotion-to-authoritative-l2/evidence/`

## Acceptance Criteria

- [ ] one bounded HS-like positive candidate lands as an authoritative canonical `L2` claim
- [ ] backend writeback receipt is durable and replayable
- [ ] repo-local canonical mirror exists for the promoted claim
- [ ] compiled workspace knowledge report and `consult-l2` agree on the promoted claim
- [ ] promotion-gate binding acceptances still pass on isolated work roots
- [ ] one dedicated acceptance lane proves the route mechanically
