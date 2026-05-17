from __future__ import annotations


def test_fqhe_toy_numeric_claim_emits_sector_counting_finite_size_intents():
    from brain.v5.models import ClaimRecord, FlowDecision
    from brain.v5.question_intents import generate_question_intents

    claim = ClaimRecord(
        claim_id="claim-fqhe-counting",
        topic_id="fqhe",
        statement="Entanglement spectrum counting identifies the FQHE edge sector.",
        evidence_profile="toy_numeric",
        confidence_state="hypothesis",
        active_uncertainty="finite-size reliability of the counting signature",
    )
    flow = FlowDecision(profile="guided", reason="new toy numerical claim")

    intents = generate_question_intents(claim, flow)

    intent_types = {intent.intent_type for intent in intents}
    assert "object_relation_check" in intent_types
    assert "finite_size_or_cutoff_check" in intent_types
    assert any("sector" in intent.target_objects for intent in intents)
    assert any("counting" in intent.target_objects for intent in intents)


def test_librpa_gw_code_claim_emits_formula_code_provenance_benchmark_intents():
    from brain.v5.models import ClaimRecord, FlowDecision
    from brain.v5.question_intents import generate_question_intents

    claim = ClaimRecord(
        claim_id="claim-librpa-gw",
        topic_id="librpa-gw",
        statement="The modified self-energy kernel reproduces the Si GW benchmark.",
        evidence_profile="code_method",
        confidence_state="locally_checked",
        active_uncertainty="formula-code translation and code state provenance",
    )
    flow = FlowDecision(profile="rigorous", reason="formula-code risk")

    intents = generate_question_intents(claim, flow)

    intent_types = {intent.intent_type for intent in intents}
    assert "formula_code_invariant_check" in intent_types
    assert "benchmark_consistency_check" in intent_types
    assert "provenance_check" in intent_types
    assert any("self-energy" in intent.target_objects for intent in intents)


def test_teacher_mode_can_request_prerequisite_and_misconception_intents():
    from brain.v5.interaction import resolve_interaction_profile
    from brain.v5.models import ClaimRecord, FlowDecision
    from brain.v5.question_intents import generate_question_intents

    claim = ClaimRecord(
        claim_id="claim-qg",
        topic_id="quantum-gravity",
        statement="The algebraic constraint closes under the proposed quantum gravity bracket.",
        evidence_profile="formal_theory",
        confidence_state="hypothesis",
        active_uncertainty="which definitions and hidden assumptions are needed",
    )
    flow = FlowDecision(profile="guided", reason="formal-theory learning discussion")
    interaction = resolve_interaction_profile("teacher", risk_level="guided", max_questions=3)

    intents = generate_question_intents(claim, flow, interaction=interaction)

    intent_types = {intent.intent_type for intent in intents}
    assert "prerequisite_check" in intent_types
    assert "misconception_check" in intent_types


def test_question_engine_expands_intents_but_preserves_intent_metadata():
    from brain.v5.models import ClaimRecord, FlowDecision
    from brain.v5.question_engine import generate_questions

    claim = ClaimRecord(
        claim_id="claim-librpa-gw",
        topic_id="librpa-gw",
        statement="The modified self-energy kernel reproduces the Si GW benchmark.",
        evidence_profile="code_method",
        confidence_state="locally_checked",
        active_uncertainty="formula-code translation and code state provenance",
    )
    flow = FlowDecision(profile="rigorous", reason="formula-code risk")

    questions = generate_questions(claim, flow)

    assert all(question.intent_id for question in questions)
    assert all(question.intent_type for question in questions)
    assert any(question.intent_type == "formula_code_invariant_check" for question in questions)
    assert any("LLM may rephrase" in question.expansion_boundary for question in questions)


def test_question_intents_have_llm_expansion_boundaries():
    from brain.v5.models import ClaimRecord, FlowDecision
    from brain.v5.question_intents import generate_question_intents

    claim = ClaimRecord(
        claim_id="claim-symmetry",
        topic_id="formal-theory",
        statement="The proposed low-energy limit preserves the required symmetry.",
        evidence_profile="formal_theory",
        confidence_state="hypothesis",
        active_uncertainty="possible limit mismatch and dimension mismatch",
    )
    flow = FlowDecision(profile="rigorous", reason="sanity check needed")

    intents = generate_question_intents(claim, flow)

    assert any(intent.intent_type == "limit_symmetry_dimension_check" for intent in intents)
    assert all("must preserve intent_type" in intent.expansion_boundary for intent in intents)
    assert all(intent.kernel_prompt for intent in intents)
