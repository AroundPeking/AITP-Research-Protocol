"""Tests for next_action_synthesis: research-facing next-action summary generation."""

from __future__ import annotations

import unittest

from knowledge_hub.next_action_synthesis import synthesize_research_next_action


class TestEmptyQueueSynthesis(unittest.TestCase):
    def test_research_synthesis_uses_question(self):
        result = synthesize_research_next_action(
            topic_slug="haldane-shastry-chaos",
            research_contract={"question": "Is the Haldane gap stable under perturbation?"},
            source_index=[],
            queue_head=None,
            topic_state={"latest_run_id": "run-001"},
        )
        self.assertFalse(result["is_bootstrap"])
        self.assertIn("Haldane", result["summary"])
        self.assertNotIn("inspect the runtime resume state", result["summary"].lower())

    def test_empty_queue_with_sources(self):
        result = synthesize_research_next_action(
            topic_slug="haldane-shastry-chaos",
            research_contract={"question": "Spectral gap bound"},
            source_index=[{"source_id": "arxiv:2401.0001"}],
            queue_head=None,
            topic_state={"latest_run_id": "run-001"},
        )
        self.assertIn("source basis", result["summary"].lower())

    def test_truly_empty_topic_is_bootstrap(self):
        result = synthesize_research_next_action(
            topic_slug="new-topic",
            research_contract={},
            source_index=[],
            queue_head=None,
            topic_state={},
        )
        self.assertTrue(result["is_bootstrap"])
        self.assertIn("Initialize", result["summary"])
        self.assertEqual(result["action_type"], "inspect_resume_state")


class TestGenericSummaryRephrasing(unittest.TestCase):
    def test_l1_vault_summary_rephrased(self):
        result = synthesize_research_next_action(
            topic_slug="scrpa-variational-closure",
            research_contract={"question": "SCRPA variational closure for the random phase approximation"},
            queue_head={"summary": "Inspect the compiled L1 vault before continuing."},
            topic_state={"latest_run_id": "run-001"},
        )
        self.assertIn("source basis", result["summary"].lower())
        self.assertNotIn("L1 vault", result["summary"])

    def test_empty_queue_runtime_summary_rephrased(self):
        result = synthesize_research_next_action(
            topic_slug="scrpa-variational-closure",
            research_contract={"question": "SCRPA variational closure for RPA"},
            queue_head={"summary": "No explicit pending actions were found; inspect the runtime resume state."},
            topic_state={"latest_run_id": "run-001"},
        )
        self.assertIn("SCRPA", result["summary"])
        self.assertNotIn("runtime resume state", result["summary"].lower())

    def test_post_promotion_summary_rephrased(self):
        result = synthesize_research_next_action(
            topic_slug="witten-tp-formal-close",
            research_contract={"question": "Witten topological phase formal closure"},
            queue_head={"summary": "Inspect the promoted Layer 2 writeback artifacts before continuing."},
            topic_state={"latest_run_id": "run-002"},
        )
        self.assertIn("promoted reusable outcome", result["summary"].lower())
        self.assertNotIn("Layer 2 writeback artifacts", result["summary"])

    def test_good_summary_preserved(self):
        good = "Recover the missing literature basis for the OTOC shoulder question."
        result = synthesize_research_next_action(
            topic_slug="otoc-shoulder",
            research_contract={"question": "OTOC shoulder question"},
            queue_head={"summary": good},
            topic_state={"latest_run_id": "run-001"},
        )
        self.assertEqual(result["summary"], good)


class TestNoContractFallback(unittest.TestCase):
    def test_no_question_with_sources(self):
        result = synthesize_research_next_action(
            topic_slug="some-topic",
            research_contract={},
            source_index=[{"source_id": "arxiv:2401.0001"}],
            queue_head=None,
            topic_state={},
        )
        self.assertIn("Register the source basis", result["summary"])
        self.assertFalse(result["is_bootstrap"])

    def test_no_question_no_sources_with_run(self):
        result = synthesize_research_next_action(
            topic_slug="some-topic",
            research_contract={},
            source_index=[],
            queue_head=None,
            topic_state={"latest_run_id": "run-001"},
        )
        self.assertIn("Resume", result["summary"])
        self.assertFalse(result["is_bootstrap"])


if __name__ == "__main__":
    unittest.main()
