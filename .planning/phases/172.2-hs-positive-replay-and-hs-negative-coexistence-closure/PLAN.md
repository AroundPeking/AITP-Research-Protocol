# Plan: 172.2-01 — Replay the positive HS-model proof, prove coexistence with the HS negative route, and route the deferred QSGW lane

**Phase:** 172.2
**Axis:** Axis 4 (human evidence) + Axis 5 (agent-facing roadmap clarity)
**Requirements:** REQ-HS-04, REQ-HS-05

## Goal

Turn the new authoritative HS positive landing from Phase `172.1` into a
stronger replayable proof by showing that the positive claim and the existing
HS negative comparator coexist honestly on the same compiled and consultation
surfaces, then write the explicit carry-over route for `LibRPA QSGW`.

## Planned Route

### Step 1: Add the isolated HS coexistence acceptance lane

**Files:**
- `research/knowledge-hub/runtime/scripts/run_hs_positive_negative_coexistence_acceptance.py`
- `research/knowledge-hub/tests/test_runtime_scripts.py`

The wrapper should:

- reuse `run_hs_positive_l2_acceptance.py`
- keep the shipped HS negative comparator in staging
- recompile the workspace reports
- run `consult-l2(..., include_staging=True)`
- assert that the positive claim stays authoritative and the HS negative row
  stays `contradiction_watch`

### Step 2: Write one short HS replay runbook

**Artifact:**
- `.planning/phases/172.2-hs-positive-replay-and-hs-negative-coexistence-closure/RUNBOOK.md`

It should explain the coexistence replay command and the success markers for
canonical ids, staged ids, and row authority.

### Step 3: Route the deferred first-principles lane honestly

**Artifact:**
- `.planning/phases/172.2-hs-positive-replay-and-hs-negative-coexistence-closure/evidence/deferred-lane-routing.md`

Write explicit blockers and next actions for the deferred
`LibRPA QSGW` first-principles / code-method lane.

### Step 4: Close the phase with summary and state updates

**Artifacts:**
- `.planning/phases/172.2-hs-positive-replay-and-hs-negative-coexistence-closure/SUMMARY.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/REQUIREMENTS.md`

## Acceptance Criteria

- [ ] one replayable acceptance lane proves the authoritative HS positive claim and staged HS negative comparator coexist honestly
- [ ] compiled knowledge report preserves positive authoritative state and negative contradiction-watch state
- [ ] `consult-l2(..., include_staging=True)` surfaces both sides without authority drift
- [ ] one replay runbook explains how to re-run the coexistence proof
- [ ] deferred `LibRPA QSGW` blockers and next actions are written explicitly
