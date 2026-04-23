"""Tests for the autonomous L3↔L4 research loop (ralph-loop mechanism)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from brain import mcp_server
from tests.test_l4_l2_memory import _bootstrap_with_candidate


class ResearchLoopStartStopTests(unittest.TestCase):
    def test_start_research_loop_sets_active_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            tr = repo_root / "topics" / "demo-topic"

            result = mcp_server.aitp_start_research_loop(
                tmp, "demo-topic", max_cycles=5, candidate_id=cand_id,
            )
            self.assertIn("loop", result.lower())

            fm, _ = mcp_server._parse_md(tr / "state.md")
            self.assertTrue(fm["research_loop_active"])
            self.assertEqual(fm["research_loop_max_cycles"], 5)

    def test_stop_research_loop_clears_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            tr = repo_root / "topics" / "demo-topic"

            mcp_server.aitp_start_research_loop(tmp, "demo-topic", max_cycles=3, candidate_id=cand_id)
            result = mcp_server.aitp_stop_research_loop(tmp, "demo-topic", reason="done")
            self.assertIn("stopped", result.lower() + " loop")

            fm, _ = mcp_server._parse_md(tr / "state.md")
            self.assertFalse(fm["research_loop_active"])

    def test_get_loop_status_shows_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)

            mcp_server.aitp_start_research_loop(tmp, "demo-topic", max_cycles=5, candidate_id=cand_id)
            status = mcp_server.aitp_get_loop_status(tmp, "demo-topic")
            self.assertTrue(status["loop_active"])
            self.assertEqual(status["max_cycles"], 5)
            self.assertEqual(status["cycle_count"], 0)


class VersionedReviewTests(unittest.TestCase):
    def test_review_creates_versioned_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            tr = repo_root / "topics" / "demo-topic"

            mcp_server.aitp_start_research_loop(tmp, "demo-topic", max_cycles=3, candidate_id=cand_id)
            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "fail", "Step 3 error.",
            )

            # Should have both latest and versioned review
            reviews_dir = tr / "L4" / "reviews"
            self.assertTrue((reviews_dir / f"{cand_id}.md").exists())
            self.assertTrue((reviews_dir / f"{cand_id}_v1.md").exists())

            # Versioned review should have l4_cycle field
            v1_fm, _ = mcp_server._parse_md(reviews_dir / f"{cand_id}_v1.md")
            self.assertEqual(v1_fm.get("l4_cycle"), 1)

    def test_two_cycles_create_v1_and_v2(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            tr = repo_root / "topics" / "demo-topic"

            mcp_server.aitp_start_research_loop(tmp, "demo-topic", max_cycles=3, candidate_id=cand_id)

            # Cycle 1: fail
            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "fail", "Error.",
            )
            mcp_server.aitp_return_to_l3_from_l4(tmp, "demo-topic", reason="post_l4_revision")

            # Cycle 2: pass
            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "pass", "OK.",
            )

            reviews_dir = tr / "L4" / "reviews"
            self.assertTrue((reviews_dir / f"{cand_id}_v1.md").exists())
            self.assertTrue((reviews_dir / f"{cand_id}_v2.md").exists())

            v1_fm, _ = mcp_server._parse_md(reviews_dir / f"{cand_id}_v1.md")
            v2_fm, _ = mcp_server._parse_md(reviews_dir / f"{cand_id}_v2.md")
            self.assertEqual(v1_fm["outcome"], "fail")
            self.assertEqual(v2_fm["outcome"], "pass")


class LoopCycleTrackingTests(unittest.TestCase):
    def test_return_to_l3_increments_cycle_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            tr = repo_root / "topics" / "demo-topic"

            mcp_server.aitp_start_research_loop(tmp, "demo-topic", max_cycles=5, candidate_id=cand_id)
            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "fail", "Error.",
            )
            result = mcp_server.aitp_return_to_l3_from_l4(
                tmp, "demo-topic", reason="post_l4_revision",
            )

            self.assertEqual(result.get("l4_cycle"), 1)

            fm, _ = mcp_server._parse_md(tr / "state.md")
            self.assertEqual(fm["l4_cycle_count"], 1)
            self.assertTrue(result.get("loop_active"))

    def test_loop_auto_stops_at_max_cycles(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            tr = repo_root / "topics" / "demo-topic"

            mcp_server.aitp_start_research_loop(tmp, "demo-topic", max_cycles=1, candidate_id=cand_id)

            # Cycle 1: fail and return
            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "fail", "Error.",
            )
            result = mcp_server.aitp_return_to_l3_from_l4(
                tmp, "demo-topic", reason="post_l4_revision",
            )
            # Loop should auto-stop because max_cycles=1 reached
            self.assertFalse(result.get("loop_active"))
            self.assertIn("stopped", result.get("message", "").lower())

    def test_loop_status_shows_cycle_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            tr = repo_root / "topics" / "demo-topic"

            mcp_server.aitp_start_research_loop(tmp, "demo-topic", max_cycles=3, candidate_id=cand_id)

            # Cycle 1
            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "fail", "Error.",
            )
            mcp_server.aitp_return_to_l3_from_l4(tmp, "demo-topic", reason="post_l4_revision")

            status = mcp_server.aitp_get_loop_status(tmp, "demo-topic")
            self.assertEqual(status["cycle_count"], 1)
            self.assertTrue(status["loop_active"])

    def test_stop_returns_summary_with_all_versioned_reviews(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            tr = repo_root / "topics" / "demo-topic"

            mcp_server.aitp_start_research_loop(tmp, "demo-topic", max_cycles=5, candidate_id=cand_id)

            # Cycle 1: fail
            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "fail", "Error.",
            )
            mcp_server.aitp_return_to_l3_from_l4(tmp, "demo-topic", reason="post_l4_revision")

            # Cycle 2: pass
            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "pass", "OK.",
            )

            result = mcp_server.aitp_stop_research_loop(tmp, "demo-topic", reason="converged")
            # Should mention cycle history
            self.assertIn("1", str(result))
            self.assertIn("2", str(result))


class LoopPopupGateBehaviorTests(unittest.TestCase):
    def test_loop_active_nonpass_suppresses_popup(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)

            mcp_server.aitp_start_research_loop(tmp, "demo-topic", max_cycles=3, candidate_id=cand_id)
            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            result = mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "fail", "Error.",
            )
            # When loop active, popup gate should be suppressed
            msg = result.get("message", "").lower()
            self.assertNotIn("popup", msg)
            self.assertIn("loop", msg)

    def test_loop_active_pass_auto_stops_if_configured(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)

            mcp_server.aitp_start_research_loop(
                tmp, "demo-topic", max_cycles=3,
                stop_on_pass=True, candidate_id=cand_id,
            )
            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            result = mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "pass", "All good.",
            )
            msg = result.get("message", "").lower()
            self.assertIn("auto-stop", msg)


class AutonomousReturnTests(unittest.TestCase):
    def test_return_to_l3_gives_autonomous_instructions_when_loop_active(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)

            mcp_server.aitp_start_research_loop(tmp, "demo-topic", max_cycles=5, candidate_id=cand_id)
            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "fail", "Sign error.",
            )
            result = mcp_server.aitp_return_to_l3_from_l4(
                tmp, "demo-topic", reason="post_l4_revision",
            )
            # Should tell the agent what to do next autonomously
            msg = result.get("message", "").lower()
            self.assertIn("l3", msg)
            self.assertTrue(result.get("loop_active"))

    def test_return_to_l3_without_loop_shows_normal_message(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)

            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "fail", "Sign error.",
            )
            result = mcp_server.aitp_return_to_l3_from_l4(
                tmp, "demo-topic", reason="post_l4_revision",
            )
            # Without loop, should not have autonomous instructions
            self.assertFalse(result.get("loop_active"))
            self.assertIn("L3", result.get("message", ""))


class PopupGateResearchLoopOptionTests(unittest.TestCase):
    def test_non_pass_review_shows_research_loop_option(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)

            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            result = mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "fail", "Error.",
            )

            gate = result.get("popup_gate", {})
            self.assertIsNotNone(gate, "Non-pass review without loop should have popup_gate")
            labels = [opt["label"] for opt in gate.get("options", [])]
            self.assertIn("Start research loop", labels)

            # Verify the option mentions aitp_start_research_loop
            loop_opt = [o for o in gate["options"] if o["label"] == "Start research loop"][0]
            self.assertIn("aitp_start_research_loop", loop_opt["description"])

    def test_loop_active_nonpass_does_not_show_popup(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)

            mcp_server.aitp_start_research_loop(tmp, "demo-topic", max_cycles=3, candidate_id=cand_id)
            mcp_server.aitp_create_validation_contract(
                tmp, "demo-topic", cand_id,
                mandatory_checks=["dimensional_consistency"],
            )
            result = mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "fail", "Error.",
            )
            # Loop active: no popup gate
            self.assertIsNone(result.get("popup_gate"))

    def test_all_non_pass_outcomes_show_loop_option(self):
        for outcome in ["fail", "partial_pass", "contradiction", "stuck", "timeout"]:
            with self.subTest(outcome=outcome):
                with tempfile.TemporaryDirectory() as tmp:
                    repo_root, cand_id = _bootstrap_with_candidate(tmp)

                    mcp_server.aitp_create_validation_contract(
                        tmp, "demo-topic", cand_id,
                        mandatory_checks=["dimensional_consistency"],
                    )
                    result = mcp_server.aitp_submit_l4_review(
                        tmp, "demo-topic", cand_id, outcome, "Review note.",
                    )

                    gate = result.get("popup_gate")
                    self.assertIsNotNone(gate, f"{outcome} should have popup_gate")
                    labels = [opt["label"] for opt in gate.get("options", [])]
                    self.assertIn("Start research loop", labels)


if __name__ == "__main__":
    unittest.main()
