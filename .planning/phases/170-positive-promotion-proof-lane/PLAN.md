# Plan: 170-01 — Three research-mode positive promotion proofs into canonical L2

**Phase:** 170
**Axis:** Axis 2 (inter-layer connection) + Axis 4 (human evidence and read-path trust)
**Requirements:** REQ-E2E-01, REQ-E2E-02

## Goal

Prove that the repaired promotion pipeline can carry **three real bounded
topics** — one per research mode — from the public AITP front door through
bounded validation into canonical `L2`, with durable runtime/read-path receipts
showing that the promoted unit actually landed.

The three proof lanes are:

| Lane | Research mode | Topic | Why this mode |
|------|--------------|-------|---------------|
| A | `formal_theory` | von Neumann algebras (type classification) | Existing acceptance infrastructure (`run_jones_chapter4_*_acceptance.py`) |
| B | `toy_model` | Haldane-Shastry model / quantum chaos | Currently only smoke/profile acceptance — needs promotion to full proof lane |
| C | `code_method` / `first_principles` | LibRPA QSGW convergence verification | Existing acceptance infrastructure, maps to `code_method` in `semantic_routing.py` |

## Context

`v1.95` closed the engineering gaps that blocked promotion:

1. `negative_result` and runtime proof packet schemas now have canonical and
   package-level contract surfaces
2. promotion gates and auto-promotion now expose runtime schema context
3. the front door now has bounded `status`, zero-config `hello`, and
   post-bootstrap `next_action_hint`

What is still unproven is the end-to-end route on a fresh real topic — and
crucially, whether the route works across **all three research modes** the
protocol defines. A single-mode proof would not demonstrate the mode-dispatch
surface is honest.

## Steps

### Step 1: Lane A — Formal theory proof (von Neumann algebras)

**Artifacts:**
- `.planning/phases/170-positive-promotion-proof-lane/RUNBOOK-A.md`
- `.planning/phases/170-positive-promotion-proof-lane/TARGET-A.md`
- `.planning/phases/170-positive-promotion-proof-lane/evidence/lane-a/`

Select a fresh bounded topic on von Neumann algebra type classification that
can realistically reach `L2` with the current stack.

The runbook must record:
- fresh topic slug (e.g. `vna-type-classification-finite-factor`)
- public front-door command
- bounded loop request targeting `formal_theory` mode
- promotion command sequence
- expected canonical unit family (concept, workflow, physical_picture)
- receipt locations

**Acceptance:**
- Uses existing `formal_theory` acceptance infrastructure
- `audit_formal_theory` CLI surface already shipped
- This is the most mature lane; should close first

### Step 2: Lane B — Toy model proof (Haldane-Shastry / quantum chaos)

**Artifacts:**
- `.planning/phases/170-positive-promotion-proof-lane/RUNBOOK-B.md`
- `.planning/phases/170-positive-promotion-proof-lane/TARGET-B.md`
- `.planning/phases/170-positive-promotion-proof-lane/evidence/lane-b/`

Select a bounded topic on the Haldane-Shastry spin chain or quantum chaos
in this model.

**Critical note:** The `toy_model` acceptance surface is currently only
smoke/profile level. This lane will likely surface gaps that require code
changes:
- Add `run_toy_model_promotion_acceptance.py` if not present
- Ensure `semantic_routing.py` correctly routes `toy_model` topics
- Verify the bounded loop can produce a promotable candidate from a
  numerics-oriented topic

The runbook must record:
- fresh topic slug (e.g. `hs-model-quantum-chaos-lyapunov`)
- public front-door command
- bounded loop request targeting `toy_model` mode
- any acceptance infrastructure gaps discovered
- promotion command sequence and receipt locations

### Step 3: Lane C — Code method proof (LibRPA QSGW convergence)

**Artifacts:**
- `.planning/phases/170-positive-promotion-proof-lane/RUNBOOK-C.md`
- `.planning/phases/170-positive-promotion-proof-lane/TARGET-C.md`
- `.planning/phases/170-positive-promotion-proof-lane/evidence/lane-c/`

Select a bounded topic on LibRPA QSGW convergence verification — e.g.,
verifying that a known convergence property holds for a standard test case.

**Mode mapping:** LibRPA QSGW maps to `first_principles` in
`semantic_routing.py`, which is grouped with `toy_model` for validation-mode
selection. However, the existing acceptance tests in
`run_scrpa_control_plane_acceptance.py` and `runtime_projection_handler.py`
use `code_method`. Use whichever mode the semantic router actually selects
for the topic; record the mapping decision.

The runbook must record:
- fresh topic slug (e.g. `librpa-qsgw-h2o-convergence-verification`)
- public front-door command
- bounded loop request targeting the appropriate code-oriented mode
- promotion command sequence and receipt locations

### Step 4: Cross-lane surface parity check

**Files:**
- `research/knowledge-hub/knowledge_hub/aitp_service.py`
- `research/knowledge-hub/knowledge_hub/topic_shell_support.py`
- `research/knowledge-hub/knowledge_hub/runtime_bundle_support.py`
- related tests

After all three lanes produce (or attempt) promotion, check:
- Do `status`, runtime protocol note, topic dashboard, and replay surfaces
  expose the same promotion receipt for **all three modes**?
- Are there mode-specific visibility gaps?

Patch read-path surfaces for parity if needed. Do not widen into new
promotion policy or unrelated UX redesign.

### Step 5: Leave durable evidence for milestone closure

**Artifacts:**
- `.planning/phases/170-positive-promotion-proof-lane/SUMMARY.md`
- `.planning/phases/170-positive-promotion-proof-lane/evidence/`

Record for each lane:
- exact commands run
- receipt paths
- promoted unit id and family
- what remained manual, if anything
- which mode-specific gaps were discovered
- whether the lane succeeded or honestly failed
- whether the route is strong enough to serve as the baseline positive proof
  for `v1.96`

## Must Do

- use **fresh** public-front-door topic slugs for each lane
- keep each proof bounded; prove one real promoted unit per lane, not
  whole-topic closure
- verify the canonical backend receipt and runtime/read-path receipt parity
  for **all three modes**
- keep all evidence durable in files, not only in chat
- record any acceptance infrastructure gaps discovered per lane
- if a lane fails honestly, record the failure as evidence rather than
  silently skipping it

## Must Not Do

- do not bypass the public front door with hidden seed state
- do not redefine what counts as canonical `L2` promotion
- do not force a theorem-grade proof lane if a smaller real bounded positive
  unit is the honest first closure target
- do not mix the negative-result proof into this phase (that stays in 170.1)
- do not collapse the three lanes into one — each mode must prove its own
  end-to-end route
- do not skip a lane just because its acceptance infrastructure is weaker

## Evidence

- [ ] Lane A: one fresh `formal_theory` topic enters through the public front
      door and promotes into canonical `L2`
- [ ] Lane B: one fresh `toy_model` topic enters through the public front door
      and either promotes or honestly documents why the current `toy_model`
      surface cannot yet reach `L2`
- [ ] Lane C: one fresh `code_method`/`first_principles` topic enters through
      the public front door and promotes into canonical `L2`
- [ ] all three backend receipt paths are durable and replayable
- [ ] `status` and runtime/read-path surfaces expose the same promotion result
      for all completed lanes
- [ ] one acceptance lane per mode proves the route mechanically (or documents
      the gap)
