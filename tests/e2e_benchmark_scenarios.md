# AITP End-to-End Benchmark Test Scenarios

These are natural-language conversation scenarios designed to test the complete
AITP protocol from a theoretical physicist's perspective. Each scenario covers
a different research lane and exercises different protocol paths.

An agent passes a scenario when it can drive the full conversation to the
stated end state using only AITP tools, respecting all gate constraints.

---

## Scenario A: Formal Theory — Quantum Anomaly in 2+1D Gauge Theory

**Lane**: formal_theory
**Coverage**: L1→L3→L4→L3→L5→L2 (golden path with L4 return loop)
**Difficulty**: Standard

### Setup
- Topics root: `<temp>/aitp-topics`
- Topic slug: `chern-simons-anomaly`
- Lane: `formal_theory`

### Conversation Script

**Turn 1 (Human):**
> I want to study whether a 2+1 dimensional Chern-Simons gauge theory with
> gauge group U(N) at level k develops a parity anomaly when coupled to
> massless Dirac fermions in the fundamental representation.

**Agent should:**
1. Call `aitp_bootstrap_topic` with lane=`formal_theory`
2. Call `aitp_get_execution_brief` — should show L1, blocked
3. Explain the L1 scaffolding process and ask which sources to register

**Turn 2 (Human):**
> The key references are: arXiv:1805.06306 (Witten on CS theory),
> arXiv:1609.04370 (Redlich on parity anomalies), and Chapter 22 of
> Weinberg QFT Vol II.

**Agent should:**
1. Call `aitp_register_source` for each paper (3 calls)
2. For the book, register with `source_type="book"` and note chapter range
3. Ask about convention choices (metric signature, CS level convention)

**Turn 3 (Human):**
> Use mostly-minus metric (+--) and the conventional CS normalization
> S_CS = k/(4π) ∫ tr(A ∧ dA + 2/3 A ∧ A ∧ A). Natural units ℏ=c=1.

**Agent should:**
1. Use `aitp_ingest_knowledge` for each source
2. Fill `convention_snapshot.md` with the stated conventions
3. Fill remaining L1 artifacts: `question_contract.md`, `source_basis.md`,
   `derivation_anchor_map.md`, `contradiction_register.md`
4. Call `aitp_get_execution_brief` — should show gate_status=ready

**Turn 4 (Human):**
> Let's start the derivation.

**Agent should:**
1. Call `aitp_advance_to_l3` — enters ideation subplane
2. Invoke `scientific-brainstorming` skill (Pattern B)
3. Conduct ideation discussion (minimum 2 AskUserQuestion rounds)
4. Fill `active_idea.md` with idea_statement and motivation

**Turn 5 (Human):**
> I want to compute the one-loop effective action for the Dirac fermion
> coupled to the background CS gauge field and check if there's a
> correction to the level: k → k ± N/2 (sign depending on fermion mass sign).

**Agent should:**
1. Call `aitp_advance_l3_subplane("planning")`
2. Create a derivation route for computing the fermion determinant
3. Fill `active_plan.md`
4. Advance to analysis

**Turn 6 (Human):**
> Go ahead with the calculation.

**Agent should:**
1. Call `aitp_advance_l3_subplane("analysis")`
2. Work through the one-loop determinant computation:
   - Start from the Dirac operator in 2+1D
   - Regularize the determinant (Pauli-Villars or zeta function)
   - Extract the CS level shift
3. Fill `active_analysis.md` with the computation
4. Advance through result_integration and distillation
5. Call `aitp_submit_candidate` with the claim: "The one-loop effective action
   of N massless Dirac fermions in the fundamental of U(N) CS theory at level k
   produces a level shift Δk = N·sgn(m)/2, rendering the theory inconsistent
   unless N·sgn(m)/2 ∈ ℤ."

**Turn 7 (Human):**
> Run validation.

**Agent should:**
1. Call `aitp_create_validation_contract` with checks:
   - dimensional_consistency, limiting_case_check (N=1 should match known result),
   - correspondence_check (large-k limit should recover classical CS),
   - symmetry_compatibility (parity transformation behavior)
2. Perform analytical verification:
   - Check all terms have correct dimensions
   - Verify N=1 reproduces Redlich's result
   - Check large-k limit
3. Call `aitp_submit_l4_review` with outcome="pass", using check_results as
   primary evidence (formal_theory lane)
4. Call `aitp_return_to_l3_from_l4` — mandatory return

**Turn 8 (Human):**
> Looks good. Let's write it up.

**Agent should:**
1. Ask the human to confirm persist (MANDATORY per protocol)
2. Update `flow_notebook.tex` with the derivation
3. Call `aitp_advance_to_l5`
4. Fill L5 provenance artifacts

**Verification checkpoints:**
- [ ] `state.md` shows stage=L5 at end
- [ ] `L3/candidates/` has exactly 1 candidate
- [ ] `L4/reviews/` has exactly 1 review with outcome=pass
- [ ] `L4/validation_contract.md` exists with 4 mandatory checks
- [ ] `flow_notebook.tex` exists and contains the level shift derivation
- [ ] `L5_writing/outline.md` is filled
- [ ] `runtime/log.md` has events for: bootstrap, advance_to_l3, submit_candidate,
      l4_review, return_to_l3, advance_to_l5

---

## Scenario B: Toy Numeric — Level Spacing Statistics in Haldane-Shastry Model

**Lane**: toy_numeric
**Coverage**: L1→L3→L4(fail)→L3→L4(pass)→L5 with lane switch
**Difficulty**: Advanced (multi-cycle L4 loop)

### Setup
- Topics root: `<temp>/aitp-topics`
- Topic slug: `hs-level-spacing`
- Lane: `toy_numeric`

### Conversation Script

**Turn 1 (Human):**
> I want to check if the Haldane-Shastry spin chain has a chaos window —
> a parameter regime where the level spacing distribution transitions from
> Poisson to Wigner-Dyson as I add a perturbation.

**Agent should:**
1. Bootstrap topic with `toy_numeric` lane
2. Register sources: Haldane (1988) PRL, Shastry (1988) PRL, and
   a random matrix theory review (e.g., Mehta's book)
3. Fill L1 artifacts

**Turn 2 (Human):**
> Start with L=12,13,14 spins (half-integer spin-1/2). The perturbation
> parameter ε multiplies a nearest-neighbor Heisenberg term added to the
> long-range HS Hamiltonian. Compute level spacing for ε = 0, 0.1, 0.5, 1.0.

**Agent should:**
1. Advance to L3
2. Ideation: brainstorm the idea — use Brody distribution fitting
3. Planning: outline the numerical route (exact diagonalization → unfold → spacing)
4. Analysis: write Jupyter notebook code for exact diag and spacing analysis
5. Distillation: submit candidate with preliminary claim

**Turn 3 (Human):**
> The first round of L4 validation.

**Agent should:**
1. Create validation contract requiring:
   - dimensional_consistency: Hamiltonian is dimensionless (J=1 units)
   - limiting_case_check: ε=0 should give Poisson (integrable)
   - correspondence_check: ε→∞ should give Wigner-Dyson (chaotic limit)
2. Write validation scripts
3. Submit L4 review — **outcome = partial_pass**:
   - Level spacing for L=12,13 looks correct
   - But L=14 shows anomalous behavior — the degeneracy handling may be wrong
   - Missing: finite-size scaling analysis

**Turn 4 (Human):**
> Fix the degeneracy issue and add finite-size scaling.

**Agent should:**
1. Call `aitp_return_to_l3_from_l4(reason="post_l4_revision")`
2. Return to analysis, fix the degeneracy splitting code
3. Add finite-size scaling analysis (Brody parameter β vs 1/L)
4. Re-distill, re-submit candidate

**Turn 5 (Human):**
> Run validation again. Also, I think we should switch to code_method lane
> since we need production-quality diagonalization for L=16.

**Agent should:**
1. Call `aitp_switch_lane("code_method", reason="need production diag for L=16")`
2. Create new validation contract (now evidence_scripts are REQUIRED)
3. Write proper production scripts in `L4/scripts/`
4. Execute on Fisher server via ssh-mcp
5. Submit L4 review with outcome="pass", including:
   - evidence_scripts, evidence_outputs
   - data_provenance for every data point
6. Return to L3

**Turn 6 (Human):**
> Confirmed. Write the paper.

**Agent should:**
1. Update flow_notebook.tex
2. Advance to L5
3. Generate comparison charts using mcp-server-chart (Pattern A)

**Verification checkpoints:**
- [ ] `state.md` shows lane changed from `toy_numeric` to `code_method`
- [ ] `L4/reviews/` has 2 reviews: partial_pass and pass
- [ ] Second L4 review has evidence_scripts and data_provenance
- [ ] `runtime/log.md` records lane switch with reason
- [ ] flow_notebook.tex has v1 (partial) and v2 (complete) sections

---

## Scenario C: Cross-Topic Knowledge Reuse — QSGW Band Gap Correction

**Lane**: code_method
**Coverage**: Multi-topic workflow with L2 knowledge sharing
**Difficulty**: Advanced (cross-topic)

### Setup
- Topics root: `<temp>/aitp-topics`
- Two topics: `qsgw-bn-bands` and `qsgw-bn-effective-mass`
- Lane: `code_method`

### Conversation Script (Topic A)

**Turn 1 (Human):**
> I want to compute the quasiparticle band gap of hexagonal BN using QSGW
> and validate it against experiment (5.97 eV).

**Agent should:**
1. Bootstrap `qsgw-bn-bands` topic
2. Register sources: the QSGW methodology paper, BN experimental data
3. Fill L1, advance to L3
4. Ideation → planning → analysis (run QSGW calculation on Fisher)
5. Distillation: submit candidate "QSGW predicts hBN band gap of 6.1 eV"
6. L4: validate against experiment (pass)
7. Promote to L2: `aitp_request_promotion` → `aitp_resolve_promotion_gate("approve")`
   → `aitp_promote_candidate`

### Conversation Script (Topic B)

**Turn 2 (Human):**
> Now I want to compute the effective mass tensor near the valence band
> maximum of hBN. This builds on the QSGW calculation we just did.

**Agent should:**
1. Bootstrap `qsgw-bn-effective-mass`
2. Call `aitp_query_l2(query="BN band")` — should find the promoted QSGW result
3. Register the promoted L2 knowledge as a source for Topic B
4. Fill L1 noting the dependency on the QSGW calculation
5. Advance to L3, plan the effective mass calculation using the QSGW band structure
6. Submit candidate with `depends_on=["qsgw-bn-bands"]`
7. Validate, promote

**Verification checkpoints:**
- [ ] Global `L2/` has 2 promoted candidates
- [ ] Topic B's `L1/source_basis.md` references the L2 promoted knowledge
- [ ] Topic B's candidate has `depends_on` field in frontmatter
- [ ] `aitp_query_l2` returns both promoted claims

---

## Scenario D: Failure and Recovery — L4 Contradiction with L2 Knowledge

**Lane**: formal_theory
**Coverage**: L4 contradiction → retreat to L1 → re-frame → new derivation
**Difficulty**: Edge case (contradiction handling)

### Setup
- Topics root: `<temp>/aitp-topics`
- Pre-seeded: L2 has a promoted claim "The topological entanglement entropy
  of a chiral spin liquid on the kagome lattice is γ = ln 2"
- Topic slug: `kagome-tee-reexamine`
- Lane: `formal_theory`

### Conversation Script

**Turn 1 (Human):**
> I think the topological entanglement entropy on the kagome lattice is
> actually γ = ln 3, not ln 2, because the ground state has a Z₃ symmetry.

**Agent should:**
1. Bootstrap topic, fill L1
2. Register the conflicting L2 knowledge as a source
3. Advance to L3, derive the argument for γ = ln 3
4. Submit candidate

**Turn 2 (Human):**
> Validate this.

**Agent should:**
1. Create validation contract with correspondence_check against L2
2. The check reveals: the new claim γ = ln 3 contradicts the L2 claim γ = ln 2
3. Submit L4 review with outcome="contradiction"
4. Present options: (a) retreat to L1 and re-examine assumptions,
   (b) the L2 knowledge may be wrong, (c) different regimes

**Turn 3 (Human):**
> Actually, I think the issue is that the L2 result was for a different
> Hamiltonian (Heisenberg, not XXZ). Let me re-frame.

**Agent should:**
1. Call `aitp_retreat_to_l1(reason="L2 contradiction — different Hamiltonian regime")`
2. Update `question_contract.md` to specify XXZ Hamiltonian
3. Update `contradiction_register.md` to note the regime mismatch
4. Re-advance to L3 with the corrected framing
5. Re-derive and submit updated candidate with explicit regime: "For the XXZ
   model on the kagome lattice with Δ > 1, the topological entanglement entropy is γ = ln 3"

**Verification checkpoints:**
- [ ] `runtime/log.md` records retreat_to_l1 with reason
- [ ] `L1/contradiction_register.md` documents the L2 conflict and regime mismatch
- [ ] `state.md` shows the retreat and re-advance history
- [ ] Final candidate explicitly scopes the regime (XXZ, Δ > 1)

---

## Scenario E: Topic Lifecycle — Fork, Archive, and Restore

**Lane**: mixed (starts formal_theory, forks to toy_numeric)
**Coverage**: Lifecycle tools: fork, archive, restore, session resume
**Difficulty**: Standard (lifecycle management)

### Setup
- Topics root: `<temp>/aitp-topics`

### Conversation Script

**Turn 1 (Human):**
> I'm studying the Hubbard model on the triangular lattice. Let's set up
> a formal_theory topic.

**Agent should:**
1. Bootstrap `triangular-hubbard` with `formal_theory` lane
2. Fill L1, advance to L3
3. During analysis, derive a sum rule for the double occupancy
4. In ideation, notice a side-question about the magnetic susceptibility

**Turn 2 (Human):**
> The susceptibility question is interesting enough to be its own topic.
> Fork it.

**Agent should:**
1. Call `aitp_fork_topic(parent_slug="triangular-hubbard", child_slug="triangular-susceptibility",
   title="Magnetic Susceptibility of Triangular Lattice Hubbard Model",
   question="Compute the zero-temperature magnetic susceptibility of the triangular lattice Hubbard model at half-filling.",
   reason="Side-discovery from double occupancy analysis")`
2. Verify child topic has L1 copies
3. Switch to the new topic

**Turn 3 (Human):**
> Actually, let me pause the susceptibility topic for now. I want to focus
> on the main Hubbard model.

**Agent should:**
1. Call `aitp_archive_topic("triangular-susceptibility", reason="prioritizing parent topic",
   reason_category="paused")`
2. Continue working on `triangular-hubbard`

**Turn 4 (Human):**
> [Simulate session break. New session starts.]

**Agent should:**
1. Call `aitp_session_resume("triangular-hubbard")`
2. Get resumption context with recent events
3. Pick up from where it left off
4. Also check: `aitp_restore_topic("triangular-susceptibility")` when ready to resume

**Verification checkpoints:**
- [ ] Child topic `triangular-susceptibility` exists with L1 copies
- [ ] Child's `state.md` has `forked_from: triangular-hubbard`
- [ ] Parent's `runtime/log.md` records the fork
- [ ] Child was archived and can be restored
- [ ] `aitp_session_resume` returns recent log entries

---

## Scoring Rubric

For each scenario, score the agent on:

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Gate compliance | 30% | Never skips stages, always checks execution brief before advancing |
| Tool usage | 20% | Uses correct tools in correct order, respects lane-specific evidence rules |
| Mandatory interactions | 20% | Conducts required AskUserQuestion rounds at L3 subplanes |
| Artifact quality | 15% | Artifacts have filled frontmatter and body headings per templates |
| Edge case handling | 15% | Correctly handles contradictions, failures, lane switches, lifecycle ops |

**Pass threshold**: ≥ 70% aggregate score
**Excellence threshold**: ≥ 90% aggregate score

---

## Running These Scenarios

These scenarios are designed as natural-language benchmarks for any AITP-compatible
agent. To run:

1. Create a fresh topics_root directory
2. Start a new agent session
3. Provide the human turns verbatim
4. Evaluate agent responses against the expected behavior
5. Score using the rubric above

For automated testing, each scenario can be converted to a pytest test that
creates the topic, simulates tool calls, and verifies the final state matches
the verification checkpoints.
