"""Tests for lane_contract_defaults: lane-aware contract default generation."""

from __future__ import annotations

import unittest

from knowledge_hub.lane_contract_defaults import (
    detect_lane,
    lane_deliverables,
    lane_observables,
    lane_target_claims,
)


class TestDetectLane(unittest.TestCase):
    def test_formal_theory_template(self):
        self.assertEqual(
            detect_lane(template_mode="formal_theory", research_mode="formal_derivation"),
            "formal_derivation",
        )

    def test_code_method_toy_model_signals(self):
        self.assertEqual(
            detect_lane(
                template_mode="code_method",
                research_mode="exploratory_general",
                topic_content_hints={"question": "TFIM exact diagonalization on a 1D lattice"},
            ),
            "toy_model",
        )

    def test_code_method_first_principles_signals(self):
        self.assertEqual(
            detect_lane(
                template_mode="code_method",
                research_mode="exploratory_general",
                topic_content_hints={"question": "QSGW convergence for BH3 molecule"},
            ),
            "first_principles",
        )

    def test_generic_fallback(self):
        self.assertEqual(
            detect_lane(template_mode="code_method", research_mode="exploratory_general"),
            "generic",
        )

    def test_unknown_template_mode(self):
        self.assertEqual(
            detect_lane(template_mode="unknown", research_mode="anything"),
            "generic",
        )


class TestLaneObservables(unittest.TestCase):
    def test_formal_derivation_has_physics_terms(self):
        result = lane_observables("formal_derivation", {"question": "Witten topological phase formal closure"})
        joined = " ".join(result).lower()
        self.assertIn("formal", joined)

    def test_formal_derivation_includes_question(self):
        result = lane_observables("formal_derivation", {"question": "Witten topological phase formal closure"})
        self.assertTrue(any("witten" in r.lower() for r in result))

    def test_toy_model_has_model_terms(self):
        result = lane_observables("toy_model", {"question": "TFIM exact diagonalization"})
        joined = " ".join(result).lower()
        self.assertTrue(any(term in joined for term in ("model", "hamiltonian", "observable", "benchmark")))

    def test_first_principles_has_method_terms(self):
        result = lane_observables("first_principles", {"question": "QSGW gap for BH3"})
        joined = " ".join(result).lower()
        self.assertTrue(any(term in joined for term in ("method", "convergence", "code", "basis")))

    def test_generic_is_current_default(self):
        result = lane_observables("generic", {})
        self.assertIn("Declared candidate ids", result[0])

    def test_empty_question_still_produces_defaults(self):
        result = lane_observables("formal_derivation", {})
        self.assertTrue(len(result) >= 3)


class TestLaneTargetClaims(unittest.TestCase):
    def test_no_action_id_pattern(self):
        for lane in ("formal_derivation", "toy_model", "first_principles", "generic"):
            result = lane_target_claims(lane, {"question": "Bounded spectral gap question"})
            for claim in result:
                self.assertNotRegex(
                    claim,
                    r"^action:[^:]+:\d+$",
                    f"Lane {lane}: claim should not be a runtime action id",
                )

    def test_uses_question_when_no_candidates(self):
        result = lane_target_claims("formal_derivation", {"question": "Is the Haldane gap stable?"})
        self.assertTrue(any("Haldane" in r for r in result))

    def test_uses_real_candidate_ids(self):
        rows = [{"candidate_id": "claim:spectral-gap-bounded"}]
        result = lane_target_claims("toy_model", {}, candidate_rows=rows)
        self.assertIn("claim:spectral-gap-bounded", result)

    def test_skips_runtime_action_ids_from_candidates(self):
        rows = [{"candidate_id": "action:my-topic:01"}]
        result = lane_target_claims("toy_model", {"question": "Some physics question"})
        self.assertFalse(any("action:my-topic:01" in r for r in result))

    def test_fallback_when_nothing(self):
        result = lane_target_claims("generic", {})
        self.assertTrue(len(result) >= 1)


class TestLaneDeliverables(unittest.TestCase):
    def test_not_generic_template(self):
        generic = (
            "Persist the active research question, validation route, "
            "and bounded next action as durable runtime artifacts."
        )
        for lane in ("formal_derivation", "toy_model", "first_principles"):
            result = lane_deliverables(lane, {})
            self.assertNotEqual(result[0], generic, f"Lane {lane} should have lane-specific deliverables")

    def test_generic_lane_keeps_current(self):
        result = lane_deliverables("generic", {})
        self.assertIn("Persist the active research question", result[0])

    def test_formal_derivation_mentions_derivation(self):
        result = lane_deliverables("formal_derivation", {})
        joined = " ".join(result).lower()
        self.assertIn("derivation", joined)

    def test_toy_model_mentions_model(self):
        result = lane_deliverables("toy_model", {})
        joined = " ".join(result).lower()
        self.assertIn("model", joined)

    def test_first_principles_mentions_method(self):
        result = lane_deliverables("first_principles", {})
        joined = " ".join(result).lower()
        self.assertIn("method", joined)


if __name__ == "__main__":
    unittest.main()
