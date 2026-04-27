"""End-to-end test: full research workflow from L0 to L2 knowledge graph.

Scenario: A theoretical physicist studies the quantum harmonic oscillator,
registers sources, fills L1, works through L3 activities, submits candidates,
validates via L4, promotes to global L2, and builds the knowledge graph with
typed nodes, edges, and correspondence checks.

Uses v4 flexible workspace (no separate study mode).
"""

from pathlib import Path

import pytest

from brain.mcp_server import (
    aitp_switch_l3_activity,
    aitp_advance_to_l1,
    aitp_advance_to_l3,
    aitp_bootstrap_topic,

    aitp_create_l2_edge,
    aitp_create_l2_node,
    aitp_create_l2_tower,

    aitp_get_execution_brief,
    aitp_get_status,
    aitp_register_source,
    aitp_merge_subgraph_delta,
    aitp_promote_candidate,
    aitp_query_l2_graph,
    aitp_request_promotion,
    aitp_resolve_promotion_gate,

    aitp_submit_candidate,
    aitp_submit_l4_review,
    aitp_update_l2_node,
    _parse_md,
    _topic_root,
    _write_md,
)

TOPIC = "qho-study"


# ---- Fixtures ----

def _setup_td(tmp_path: Path) -> str:
    (tmp_path / "topics").mkdir()
    return str(tmp_path)


def _bootstrap_and_fill(td):
    """Bootstrap topic, fill L0 + L1 gates, return topic root path."""
    aitp_bootstrap_topic(td, TOPIC, "QHO Energy Spectrum",
                         "What are the energy eigenvalues of the QHO?")

    tr = _topic_root(td, TOPIC)

    # Register source
    aitp_register_source(td, TOPIC, "griffiths-qm-ch2", "textbook",
                         title="Griffiths QM Chapter 2",
                         notes="The quantum harmonic oscillator: algebraic method.")

    # Fill L0 gate
    _write_md(
        tr / "L0" / "source_registry.md",
        {"artifact_kind": "l0_source_registry", "stage": "L0",
         "source_count": 1, "search_status": "complete"},
        "# Source Registry\n\n## Search Methodology\nTextbook.\n\n"
        "## Source Inventory\ngriffiths-qm-ch2\n\n## Coverage Assessment\nAdequate.\n\n"
        "## Overall Verdict\nCoverage sufficient.\n\n"
        "## Gaps And Next Sources\nNone.\n",
    )

    # Advance to L1
    r = aitp_advance_to_l1(td, TOPIC)
    assert "L1" in r or "advanced" in r.lower()

    # Fill all L1 artifacts
    _write_md(
        tr / "L1" / "question_contract.md",
        {"artifact_kind": "l1_question_contract", "stage": "L1",
         "bounded_question": "What are the energy eigenvalues and eigenstates of the 1D QHO?",
         "scope_boundaries": "Single particle, 1D, non-relativistic. Does NOT ask about relativistic or coupled oscillators.",
         "target_quantities": "Energy spectrum E_n = (n+1/2) hbar omega, eigenstates |n>.",
         "competing_hypotheses": "Alternative: the spectrum may be continuous if the potential is unbounded."},
        "# Question Contract\n\n## Bounded Question\nQHO energy spectrum.\n\n"
        "## Competing Hypotheses\nAlternative: continuous spectrum for unbounded potential.\n\n"
        "## Scope Boundaries\n1D NRQM. Does NOT ask about relativistic or coupled oscillators.\n\n"
        "## Target Quantities Or Claims\nE_n = (n+1/2) hbar omega.\n\n"
        "## Non-Success Conditions\nIf zero-point energy is zero, the claim is falsified.\n",
    )
    _write_md(
        tr / "L1" / "source_basis.md",
        {"artifact_kind": "l1_source_basis", "stage": "L1",
         "core_sources": "griffiths-qm-ch2", "peripheral_sources": "none"},
        "# Source Basis\n\n## Core Sources\ngriffiths-qm-ch2\n\n## Peripheral Sources\nnone\n\n"
        "## Why Each Source Matters\nCore derivation source.\n",
    )
    _write_md(
        tr / "L1" / "convention_snapshot.md",
        {"artifact_kind": "l1_convention_snapshot", "stage": "L1",
         "notation_choices": "Dirac bra-ket, natural units hbar=c=1.",
         "unit_conventions": "Natural units."},
        "# Convention Snapshot\n\n## Notation Choices\nDirac bra-ket.\n\n"
        "## Unit Conventions\nNatural units.\n\n## Unresolved Tensions\nNone.\n",
    )
    _write_md(
        tr / "L1" / "derivation_anchor_map.md",
        {"artifact_kind": "l1_derivation_anchor_map", "stage": "L1",
         "starting_anchors": "eq-2.44 (ladder operators)", "anchor_count": 1},
        "# Derivation Anchor Map\n\n## Source Anchors\neq-2.44\n\n"
        "## Candidate Starting Points\nLadder operator algebra.\n",
    )
    _write_md(
        tr / "L1" / "contradiction_register.md",
        {"artifact_kind": "l1_contradiction_register", "stage": "L1",
         "blocking_contradictions": "none"},
        "# Contradiction Register\n\n## Unresolved Source Conflicts\nNone.\n\n## Blocking Status\nnone\n",
    )
    _write_md(
        tr / "L1" / "source_toc_map.md",
        {"artifact_kind": "l1_source_toc_map", "stage": "L1",
         "sources_with_toc": "sakurai", "total_sections": 1,
         "coverage_status": "complete"},
        "# Source TOC Map\n\n## Per-Source TOC\n\n"
        "### sakurai (TOC confidence: high)\n\n"
        "- [s1] Angular Momentum -- status: extracted  -> intake: L1/intake/sakurai/s1.md\n\n"
        "## Coverage Summary\n\n## Deferred Sections\n\n## Extraction Notes\n",
    )
    # Create intake note for extracted section (required by L1 quality gate)
    intake_dir = tr / "L1" / "intake" / "sakurai"
    intake_dir.mkdir(parents=True, exist_ok=True)
    _write_md(
        intake_dir / "s1.md",
        {"artifact_kind": "l1_section_intake", "source_id": "sakurai",
         "section_id": "s1", "section_title": "Angular Momentum",
         "extraction_status": "extracted", "completeness_confidence": "high",
         "updated_at": "2025-01-01T00:00:00Z"},
        "# Angular Momentum\n\n## Section Summary (skim)\nAngular momentum algebra.\n\n"
        "## Key Concepts\nLadder operators.\n\n## Equations Found\n[J_i, J_j] = i hbar eps_ijk J_k.\n\n"
        "## Physical Claims\nSpectrum of J^2 and J_z.\n\n## Prerequisites\nQM basics.\n\n"
        "## Cross-References\nNone.\n\n## Completeness Self-Assessment\nConfidence: **high**\n",
    )
    return tr


def _fill_activity_artifact(td, activity, artifact_name, frontmatter, body_text):
    """Fill a L3 activity's active artifact with content."""
    tr = _topic_root(td, TOPIC)
    path = tr / "L3" / activity / artifact_name
    _write_md(path, frontmatter, body_text)


# ---- E2E: Full research workflow ----

class TestE2EStudyWorkflow:
    """Complete research lifecycle: L0 -> L1 -> L3 -> L4 -> promote -> L2 graph."""

    def test_full_study_lifecycle(self, tmp_path):
        td = _setup_td(tmp_path)
        tr = _bootstrap_and_fill(td)

        # STEP 1: Verify L1 is ready, advance to L3
        brief = aitp_get_execution_brief(td, TOPIC)
        assert brief["stage"] == "L1"
        assert brief["gate_status"] == "ready"

        r = aitp_advance_to_l3(td, TOPIC)
        assert "L3" in str(r)

        s = aitp_get_status(td, TOPIC)
        assert s["stage"] == "L3"

        # STEP 2: ideate -- decompose the QHO source
        _fill_activity_artifact(td, "ideate", "active_idea.md", {
            "artifact_kind": "l3_active_idea",
            "stage": "L3",
            "idea_statement": "Decompose Griffiths QM Ch2 into atomic concepts",
            "motivation": "Extract ladder operator method and QHO energy spectrum",
        }, (
            "# Active Idea\n\n"
            "## Idea Statement\nDecompose Griffiths QM Ch2 into atomic concepts.\n\n"
            "## Motivation\nExtract ladder operator method for QHO spectrum.\n\n"
            "## Risk Assessment\nLow -- textbook material.\n"
        ))

        # Verify artifact was written
        dec_path = tr / "L3" / "ideate" / "active_idea.md"
        assert dec_path.exists()
        fm, body = _parse_md(dec_path)
        assert "Decompose" in body

        # STEP 3: Switch to plan
        r = aitp_switch_l3_activity(td, TOPIC, "plan")
        assert "plan" in r.lower()

        _fill_activity_artifact(td, "plan", "active_plan.md", {
            "artifact_kind": "l3_active_plan",
            "stage": "L3",
            "plan_statement": "Trace the ladder operator derivation step-by-step",
            "derivation_route": "Define a, a-dagger -> [a,a-dagger]=1 -> H = hbar omega (N+1/2) -> E_n",
        }, (
            "# Active Plan\n\n"
            "## Plan Statement\nTrace the ladder operator derivation step-by-step.\n\n"
            "## Derivation Route\nDefine ladder ops -> commutator -> H -> spectrum.\n\n"
            "## Risk Assessment\nWell-trodden path.\n"
        ))

        # STEP 4: Switch to derive
        r = aitp_switch_l3_activity(td, TOPIC, "derive")
        assert "derive" in r.lower()

        _fill_activity_artifact(td, "derive", "active_derivation.md", {
            "artifact_kind": "l3_active_derivation",
            "stage": "L3",
            "derivation_count": 4,
            "all_steps_justified": "yes",
        }, (
            "# Active Derivation\n\n"
            "## Derivation Chains\nQHO via ladder operators.\n\n"
            "## Step-by-Step Trace\n"
            "1. Define a, a-dagger from x,p.\n"
            "2. Compute [a, a-dagger] = 1.\n"
            "3. Show H = hbar omega (N + 1/2).\n"
            "4. Derive E_n = (n+1/2) hbar omega.\n\n"
            "## Feynman Self-Check\nCan explain to first-year grad student.\n"
        ))

        # STEP 5: Switch to gap-audit
        r = aitp_switch_l3_activity(td, TOPIC, "gap-audit")
        assert "gap-audit" in r.lower()

        _fill_activity_artifact(td, "gap-audit", "active_gaps.md", {
            "artifact_kind": "l3_active_gaps",
            "stage": "L3",
            "gap_count": 2,
            "blocking_gaps": "none",
        }, (
            "# Active Gap Audit\n\n"
            "## Unstated Assumptions\n"
            "1. [minor] Canonical commutation [x,p]=i hbar.\n"
            "2. [minor] Unbounded harmonic potential.\n\n"
            "## Correspondence Check\n"
            "Classical limit n -> inf matches equipartition.\n\n"
            "## Severity Assessment\nAll minor, no blocking gaps.\n"
        ))

        # STEP 6: Submit candidates
        r1 = aitp_submit_candidate(
            td, TOPIC, "ladder-operator-method",
            title="Ladder Operator Method for QHO",
            claim="The algebraic method using ladder operators a and a-dagger yields "
                  "the QHO energy spectrum E_n = (n+1/2) hbar omega.",
            evidence="Step-by-step derivation traced in derive activity.",
            candidate_type="atomic_concept",
            regime_of_validity="Non-relativistic QM, 1D, spinless particle",
        )
        assert "Submitted" in str(r1)

        r2 = aitp_submit_candidate(
            td, TOPIC, "zero-point-energy",
            title="Zero-Point Energy of QHO",
            claim="The ground state energy of the 1D QHO is E_0 = hbar omega / 2.",
            evidence="Derived from H = hbar omega (N + 1/2) with N|0> = 0.",
            candidate_type="result",
            regime_of_validity="1D QHO, non-relativistic",
        )
        assert "Submitted" in str(r2)

        # Verify candidates were created
        cand_dir = tr / "L3" / "candidates"
        assert (cand_dir / "ladder-operator-method.md").exists()
        assert (cand_dir / "zero-point-energy.md").exists()

        # STEP 7: Set topic stage to L4 for promotion
        state_fm, state_body = _parse_md(tr / "state.md")
        state_fm["stage"] = "L4"
        _write_md(tr / "state.md", state_fm, state_body)

        # STEP 8: L4 validation
        r = aitp_submit_l4_review(
            td, TOPIC, "ladder-operator-method",
            outcome="pass",
            notes="All checks pass.",
            check_results={
                "dimensional_consistency": "pass: [H] = [hbar omega] = energy",
                "limiting_case_check": "pass: classical limit recovered",
            },
            devils_advocate="Assumes harmonic potential; anharmonic corrections unverified.",
        )
        assert "pass" in str(r).lower()

        # Verify candidate status updated
        fm1, _ = _parse_md(cand_dir / "ladder-operator-method.md")
        assert fm1["status"] == "validated"

        # STEP 9: Promotion pipeline
        r = aitp_request_promotion(td, TOPIC, "ladder-operator-method")
        assert "pending_approval" in str(r).lower()

        r = aitp_resolve_promotion_gate(td, TOPIC, "ladder-operator-method", "approve")
        assert "approve" in r.lower()

        r = aitp_promote_candidate(td, TOPIC, "ladder-operator-method")
        assert "Promoted" in r

        # Repeat for zero-point-energy
        aitp_submit_l4_review(td, TOPIC, "zero-point-energy", outcome="pass",
                              check_results={"all": "pass"},
                              devils_advocate="Rapid promotion check.")
        aitp_request_promotion(td, TOPIC, "zero-point-energy")
        aitp_resolve_promotion_gate(td, TOPIC, "zero-point-energy", "approve")
        r = aitp_promote_candidate(td, TOPIC, "zero-point-energy")
        assert "Promoted" in r

        # STEP 10: Create L2 graph nodes
        r = aitp_create_l2_node(td, "qho-hamiltonian", "concept",
                                "QHO Hamiltonian via Ladder Operators",
                                source_ref="ref:griffiths-qm-ch2",
                                physical_meaning="H = hbar omega (N + 1/2)",
                                mathematical_expression="H = hbar omega (a-dagger a + 1/2)",
                                regime_of_validity="1D QHO, non-relativistic",
                                domain="quantum-many-body")
        assert "Created" in r

        # STEP 11: Create typed edges
        r = aitp_create_l2_edge(td, "zpe-from-hamiltonian", "zero-point-energy",
                                "qho-hamiltonian", "derives_from",
                                source_ref="ref:griffiths-qm-ch2",
                                regime_condition="1D QHO, N|0>=0")
        assert "Created" in r

        # STEP 12: Merge subgraph delta
        delta = aitp_merge_subgraph_delta(td, TOPIC,
            nodes=[
                {"node_id": "coherent-states", "type": "concept",
                 "title": "Coherent States of QHO",
                 "regime_of_validity": "1D QHO",
                 "physical_meaning": "Minimum uncertainty states."},
            ],
            edges=[
                {"from_node": "coherent-states", "to_node": "qho-hamiltonian",
                 "type": "uses"},
            ],
            missing_prerequisites=["displacement-operator"],
        )
        assert isinstance(delta, dict)
        assert delta["nodes_created"] == 1
        assert delta["edges_created"] == 1

        # STEP 13: Final graph query
        full_graph = aitp_query_l2_graph(td)
        node_count = len(full_graph["nodes"])
        edge_count = len(full_graph["edges"])
        assert node_count >= 4, f"Expected >=4 nodes, got {node_count}"
        assert edge_count >= 1, f"Expected >=1 edges, got {edge_count}"

    def test_conflict_detection_on_promotion(self, tmp_path):
        """Verify conflict detection when promoting conflicting claims."""
        td = _setup_td(tmp_path)
        tr = _bootstrap_and_fill(td)
        aitp_advance_to_l3(td, TOPIC)

        # Submit, validate, promote first candidate
        aitp_submit_candidate(td, TOPIC, "energy-formula",
                              title="Energy Formula",
                              claim="E_n = (n+1/2) hbar omega",
                              candidate_type="result",
                              regime_of_validity="1D QHO")

        # Set stage to L4
        state_fm, state_body = _parse_md(tr / "state.md")
        state_fm["stage"] = "L4"
        _write_md(tr / "state.md", state_fm, state_body)

        aitp_submit_l4_review(td, TOPIC, "energy-formula", outcome="pass",
                              check_results={"dimensional_consistency": "pass"},
                              devils_advocate="Test review for conflict detection.")
        aitp_request_promotion(td, TOPIC, "energy-formula")
        aitp_resolve_promotion_gate(td, TOPIC, "energy-formula", "approve")
        r = aitp_promote_candidate(td, TOPIC, "energy-formula")
        assert "Promoted" in r

        # Submit a CONFLICTING claim with the same ID
        aitp_submit_candidate(td, TOPIC, "energy-formula",
                              title="Energy Formula v2",
                              claim="E_n = n hbar omega (WRONG!)",
                              candidate_type="result",
                              regime_of_validity="1D QHO")
        # Manually set status to trigger conflict detection
        cand_path = tr / "L3" / "candidates" / "energy-formula.md"
        fm, body = _parse_md(cand_path)
        fm["status"] = "approved_for_promotion"
        _write_md(cand_path, fm, body)

        r = aitp_promote_candidate(td, TOPIC, "energy-formula")
        assert "Conflict" in r or "conflict" in r.lower()

    def test_trust_evolution(self, tmp_path):
        """Verify trust level progression through the evolution ladder."""
        td = _setup_td(tmp_path)

        # Create node with source_grounded (default)
        aitp_create_l2_node(td, "test-concept", "concept", "Test Concept",
                            source_ref="source-1", domain="quantum-many-body",
                            physical_meaning="A test concept for trust evolution")
        graph = aitp_query_l2_graph(td, query="test concept")
        node = graph["nodes"][0]
        assert node["trust_basis"] == "source_grounded"

        # Upgrade to multi_source_confirmed
        aitp_update_l2_node(td, "test-concept", trust_level="multi_source_confirmed")
        graph = aitp_query_l2_graph(td, query="test concept")
        node = graph["nodes"][0]
        assert node["trust_basis"] == "multi_source_confirmed"

        # Upgrade to validated
        aitp_update_l2_node(td, "test-concept", trust_level="validated")
        graph = aitp_query_l2_graph(td, query="test concept")
        node = graph["nodes"][0]
        assert node["trust_basis"] == "validated"

        # Upgrade to independently_verified
        aitp_update_l2_node(td, "test-concept", trust_level="independently_verified")
        graph = aitp_query_l2_graph(td, query="test concept")
        node = graph["nodes"][0]
        assert node["trust_basis"] == "independently_verified"


if __name__ == "__main__":
    pytest.main([__file__])
