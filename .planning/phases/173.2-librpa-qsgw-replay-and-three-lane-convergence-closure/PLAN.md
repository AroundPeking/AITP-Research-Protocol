# Plan: 173.2-01 — Replay the positive `LibRPA QSGW` proof and write the three-lane convergence closure

**Phase:** 173.2
**Axis:** Axis 4 (human evidence) + Axis 5 (agent-facing roadmap clarity)
**Requirements:** REQ-QSGW-05

## Goal

Turn the bounded `LibRPA QSGW` authoritative-L2 landing from Phase `173.1`
into a replayable proof package, then write one explicit note that the three
requested research directions now each have a bounded positive baseline.

## Planned Route

### Step 1: Re-run the `LibRPA QSGW` positive-L2 receipts mechanically

**Commands to preserve as evidence:**
- `python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -k "librpa_qsgw_positive_l2_acceptance_script_runs_on_isolated_work_root" -q`
- `python research/knowledge-hub/runtime/scripts/run_librpa_qsgw_positive_l2_acceptance.py --json`

Store the raw outputs under this phase's `evidence/` directory.

### Step 2: Write one short replay runbook

**Artifact:**
- `.planning/phases/173.2-librpa-qsgw-replay-and-three-lane-convergence-closure/RUNBOOK.md`

The runbook should explain:

- what to run for the bounded `LibRPA QSGW` authoritative landing
- what success looks like on the promoted claim, canonical mirror path, and
  consultation ids

### Step 3: Write the three-lane convergence note

**Artifact:**
- `.planning/phases/173.2-librpa-qsgw-replay-and-three-lane-convergence-closure/evidence/three-lane-convergence.md`

Make explicit that the three bounded baselines are now:

- formal theory: `v1.97`
- toy model: `v1.98`
- first-principles / code-method: `v1.99`

### Step 4: Close the phase with summary and state updates

**Artifacts:**
- `.planning/phases/173.2-librpa-qsgw-replay-and-three-lane-convergence-closure/SUMMARY.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`

## Acceptance Criteria

- [ ] one replayable acceptance lane proves the bounded positive `LibRPA QSGW` route mechanically
- [ ] one runbook explains how to replay that positive-L2 proof end to end
- [ ] one durable note makes the three-lane convergence baseline explicit
- [ ] milestone `v1.99` is left ready for lifecycle handling
