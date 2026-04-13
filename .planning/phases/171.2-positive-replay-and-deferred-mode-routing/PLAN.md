# Plan: 171.2-01 — Close the positive-L2 proof with replay evidence and explicit deferred-mode routing

**Phase:** 171.2
**Axis:** Axis 4 (human evidence) + Axis 5 (agent-facing roadmap clarity)
**Requirements:** REQ-L2POS-04, REQ-L2POS-05

## Goal

Make the positive-L2 baseline from Phases `171` and `171.1` replayable as a
single milestone-level package, then write explicit blocker notes for the
deferred `toy_model` and `first_principles` positive-L2 lanes.

## Planned Route

### Step 1: Re-run the positive-L2 receipts mechanically

**Commands to preserve as evidence:**
- `python research/knowledge-hub/runtime/scripts/run_formal_positive_l2_acceptance.py --json`
- `python research/knowledge-hub/runtime/scripts/run_positive_negative_l2_coexistence_acceptance.py --json`
- targeted pytest for Phase `171` and Phase `171.1` regression points

Store the raw outputs under this phase's `evidence/` directory.

### Step 2: Write one milestone-level positive replay runbook

**Artifact:**
- `.planning/phases/171.2-positive-replay-and-deferred-mode-routing/RUNBOOK-P.md`

The runbook should explain:

- what to run for the fresh positive landing
- what to run for coexistence hardening
- what success looks like on authoritative theorem rows, contradiction rows,
  and consultation ids

### Step 3: Route the deferred lanes honestly

**Artifact:**
- `.planning/phases/171.2-positive-replay-and-deferred-mode-routing/evidence/deferred-lane-routing.md`

Write explicit blockers and next actions for:

- `toy_model` positive-L2 closure using the user-requested `HS model`
- `first_principles` positive-L2 closure using the user-requested `LibRPA QSGW`
  / large-codebase lane

### Step 4: Close the phase with summary and state updates

**Artifacts:**
- `.planning/phases/171.2-positive-replay-and-deferred-mode-routing/SUMMARY.md`
- `.planning/ROADMAP.md`
- `.planning/STATE.md`
- `.planning/REQUIREMENTS.md`
- `.planning/MILESTONES.md`

## Acceptance Criteria

- [ ] one runbook explains how to replay the positive-L2 proof end to end
- [ ] raw replay receipts are stored under this phase
- [ ] REQ-L2POS-04 is satisfied by explicit replay evidence
- [ ] toy-model blockers and next actions are written explicitly
- [ ] first-principles blockers and next actions are written explicitly
- [ ] REQ-L2POS-05 is satisfied by durable routing notes rather than chat memory
