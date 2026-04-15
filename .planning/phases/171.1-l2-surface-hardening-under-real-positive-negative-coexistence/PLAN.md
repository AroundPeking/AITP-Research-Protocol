# Plan: 171.1-01 — Patch and verify L2 compiler and read-path parity under real positive/negative coexistence

**Phase:** 171.1
**Axis:** Axis 1 (layer capability) + Axis 3 (durable data recording)
**Requirements:** REQ-L2POS-03

## Goal

Turn the Phase `171` positive-L2 proof into a harder L2-trust proof by showing
that one real authoritative positive unit and one real staged
`negative_result -> contradiction_watch` row can coexist on the same compiled
and consultation surfaces without authority drift.

## Planned Route

### Step 1: Write failing coexistence regression tests first

**Files:**
- `research/knowledge-hub/tests/test_l2_graph_activation.py`
- `research/knowledge-hub/tests/test_runtime_scripts.py`

Add tests that require:

- one authoritative theorem-card row and one contradiction-watch staging row
  to appear together in the compiled workspace knowledge report
- authority/provenance labels to remain distinct for the positive and negative
  rows
- `consult-l2(..., include_staging=True)` to expose the positive row on the
  canonical hit side and the negative row on the staged-hit side
- a dedicated coexistence acceptance script to exist and run on an isolated
  work root

Do not write the new acceptance script before these tests fail.

### Step 2: Add one bounded coexistence acceptance lane

**Files:**
- `research/knowledge-hub/runtime/scripts/run_positive_negative_l2_coexistence_acceptance.py`

The script should:

- reuse `run_formal_positive_l2_acceptance.py` for the real positive landing
- add one honest staged negative result that shares lexical/query space with
  the positive theorem
- compile the workspace knowledge report
- run `consult-l2(..., include_staging=True)`
- assert the positive row stays authoritative and the negative row stays a
  contradiction-watch staging row
- emit durable artifact paths and query ids as JSON

### Step 3: Patch only the smallest surface if the coexistence tests expose drift

**Likely files if needed:**
- `research/knowledge-hub/knowledge_hub/l2_compiler.py`
- `research/knowledge-hub/knowledge_hub/l2_graph.py`
- `research/knowledge-hub/knowledge_hub/l2_staging.py`

If the new tests expose missing provenance refs, wrong authority labels, or
consultation blind spots, patch the minimum code necessary. Do not redesign
retrieval or ranking in this phase.

### Step 4: Leave durable evidence for closure

**Artifacts to write during execution:**
- `.planning/phases/171.1-l2-surface-hardening-under-real-positive-negative-coexistence/SUMMARY.md`
- `.planning/phases/171.1-l2-surface-hardening-under-real-positive-negative-coexistence/evidence/`

Store:

- the coexistence acceptance JSON payload
- targeted pytest outputs
- the exact query text that surfaces both rows
- the paths for the authoritative theorem row and contradiction-watch row

## Acceptance Criteria

- [ ] compiled knowledge report includes both the positive authoritative row and the contradiction-watch row
- [ ] the positive row remains `authoritative_canonical/trusted`
- [ ] the negative row remains `non_authoritative_staging/contradiction_watch`
- [ ] provenance refs remain present on both rows
- [ ] `consult-l2(..., include_staging=True)` exposes both sides without mixing authority
- [ ] a dedicated coexistence acceptance lane runs mechanically on an isolated work root

## Must Not Do

- do not turn the negative result into a fake canonical theorem competitor
- do not widen this phase into toy-model or first-principles closure
- do not redesign consultation semantics beyond the coexistence proof
