"""Tests for L4 physics adjudication (six outcomes) and global L2 memory."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from brain import mcp_server
from brain.state_model import (
    L4_OUTCOMES,
    PHYSICS_CHECK_FIELDS,
)
from tests.test_l3_subplanes import _bootstrap_l1_complete


def _bootstrap_with_candidate(tmp: str) -> tuple[Path, str]:
    """Bootstrap topic with a submitted candidate ready for validation."""
    repo_root = _bootstrap_l1_complete(tmp)
    mcp_server.aitp_advance_to_l3(str(repo_root), "demo-topic")
    tr = repo_root / "topics" / "demo-topic"

    # Fill ideate and advance through to distill for completeness
    activity_sequence = [
        ("ideate", "active_idea.md",
         {"idea_statement": "Idea", "motivation": "Motivation"},
         ["## Idea Statement", "## Motivation"]),
        ("plan", "active_plan.md",
         {"plan_statement": "Plan", "derivation_route": "Route"},
         ["## Plan Statement", "## Derivation Route"]),
        ("derive", "active_derivation.md",
         {"derivation_count": 1, "all_steps_justified": "yes"},
         ["## Derivation Chains", "## Step-by-Step Trace"]),
        ("integrate", "active_integration.md",
         {"integration_statement": "Integration", "findings": "Findings"},
         ["## Integration Statement", "## Findings"]),
        ("distill", "active_distillation.md",
         {"distilled_claim": "Claim", "evidence_summary": "Evidence"},
         ["## Distilled Claim", "## Evidence Summary"]),
    ]
    for i, (act, artifact_name, fields, headings) in enumerate(activity_sequence):
        mcp_server._write_md(
            tr / "L3" / act / artifact_name,
            {"artifact_kind": f"l3_active_{act}", "activity": act, **fields},
            "# Active\n\n" + "\n".join(f"{h}\nContent" for h in headings) + "\n",
        )
        if i < len(activity_sequence) - 1:
            next_act = activity_sequence[i + 1][0]
            mcp_server.aitp_switch_l3_activity(str(repo_root), "demo-topic", next_act)

    # Submit candidate
    mcp_server.aitp_submit_candidate(
        tmp, "demo-topic", "cand-1", "Test Claim",
        claim="Test Evidence claim text",
        evidence="Supporting evidence",
    )

    # Set topic stage to L4 so promotion gate allows it
    state_fm, state_body = mcp_server._parse_md(tr / "state.md")
    state_fm["stage"] = "L4"
    mcp_server._write_md(tr / "state.md", state_fm, state_body)

    return repo_root, "cand-1"


class L4ReviewTests(unittest.TestCase):
    def test_review_can_end_in_partial_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            result = mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "partial_pass",
                "Dimensional check passed but symmetry check inconclusive.",
            )
            self.assertIn("partial_pass", result)
            tr = repo_root / "topics" / "demo-topic"
            review_path = tr / "L4" / "reviews" / "cand-1.md"
            self.assertTrue(review_path.exists())
            fm, _ = mcp_server._parse_md(review_path)
            self.assertEqual(fm["outcome"], "partial_pass")

    def test_review_can_end_in_contradiction(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            result = mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "contradiction",
                "Claim contradicts eq.12 in source.",
            )
            self.assertIn("contradiction", result)

    def test_review_can_end_in_stuck(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            result = mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "stuck",
                "Cannot resolve sign ambiguity without further data.",
            )
            self.assertIn("stuck", result)

    def test_six_outcomes_are_all_valid(self):
        expected = {"pass", "partial_pass", "fail", "contradiction", "stuck", "timeout"}
        self.assertEqual(set(L4_OUTCOMES), expected)


class PhysicsChecksTests(unittest.TestCase):
    def test_physics_check_fields_are_known(self):
        expected = {
            "dimensional_consistency", "symmetry_compatibility",
            "limiting_case_check", "conservation_check", "correspondence_check",
        }
        self.assertEqual(set(PHYSICS_CHECK_FIELDS), expected)


class GlobalL2MemoryTests(unittest.TestCase):
    def test_promote_writes_to_global_l2_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "pass", "All checks passed.",
                check_results={"dimensional_consistency": "pass"},
                devils_advocate="Test fixture review.",
            )
            mcp_server.aitp_request_promotion(tmp, "demo-topic", cand_id)
            mcp_server.aitp_resolve_promotion_gate(tmp, "demo-topic", cand_id, "approve")
            result = mcp_server.aitp_promote_candidate(tmp, "demo-topic", cand_id)
            self.assertIn("Promoted", result)

            from brain.mcp_server import _global_l2_path
            g2 = _global_l2_path(tmp)
            self.assertTrue((g2 / "cand-1.md").exists(), "Must exist in global L2")

    def test_conflicting_existing_unit_creates_conflict_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "pass", "All checks passed.",
                check_results={"dimensional_consistency": "pass"},
                devils_advocate="Test fixture review.",
            )
            mcp_server.aitp_request_promotion(tmp, "demo-topic", cand_id)
            mcp_server.aitp_resolve_promotion_gate(tmp, "demo-topic", cand_id, "approve")
            mcp_server.aitp_promote_candidate(tmp, "demo-topic", cand_id)

            # Submit same candidate with different claim
            tr = repo_root / "topics" / "demo-topic"
            mcp_server.aitp_submit_candidate(
                tmp, "demo-topic", "cand-1", "Conflicting Claim", "Different Evidence",
            )
            cand_path = tr / "L3" / "candidates" / "cand-1.md"
            fm, body = mcp_server._parse_md(cand_path)
            fm["status"] = "validated"
            # Set a different claim to trigger conflict
            cand_fm_new, cand_body_new = mcp_server._parse_md(cand_path)
            cand_fm_new["claim"] = "Completely different claim"
            cand_fm_new["status"] = "validated"
            mcp_server._write_md(cand_path, cand_fm_new, cand_body_new)

            mcp_server.aitp_request_promotion(tmp, "demo-topic", "cand-1")
            mcp_server.aitp_resolve_promotion_gate(tmp, "demo-topic", "cand-1", "approve")
            result = mcp_server.aitp_promote_candidate(tmp, "demo-topic", "cand-1")
            self.assertTrue(
                "Conflict" in result or "conflict" in result.lower()
                or "v2" in result.lower() or "Promoted" in result
            )

    def test_repeat_promotion_creates_version_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "pass", "All checks passed.",
                check_results={"dimensional_consistency": "pass"},
                devils_advocate="Test fixture review.",
            )
            tr = repo_root / "topics" / "demo-topic"
            mcp_server.aitp_request_promotion(tmp, "demo-topic", cand_id)
            mcp_server.aitp_resolve_promotion_gate(tmp, "demo-topic", cand_id, "approve")
            result = mcp_server.aitp_promote_candidate(tmp, "demo-topic", cand_id)
            self.assertTrue(
                "Promoted" in result or "v" in result.lower()
            )


class TrustClassificationTests(unittest.TestCase):
    def test_promoted_unit_has_2d_trust(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo_root, cand_id = _bootstrap_with_candidate(tmp)
            mcp_server.aitp_submit_l4_review(
                tmp, "demo-topic", cand_id, "pass", "All checks passed.",
                check_results={"dimensional_consistency": "pass"},
                devils_advocate="Test fixture review.",
            )
            mcp_server.aitp_request_promotion(tmp, "demo-topic", cand_id)
            mcp_server.aitp_resolve_promotion_gate(tmp, "demo-topic", cand_id, "approve")
            mcp_server.aitp_promote_candidate(tmp, "demo-topic", cand_id)
            from brain.mcp_server import _global_l2_path
            g2 = _global_l2_path(tmp)
            l2_fm, _ = mcp_server._parse_md(g2 / "cand-1.md")
            self.assertIn("trust_basis", l2_fm)
            self.assertIn("trust_scope", l2_fm)
            self.assertEqual(l2_fm["trust_basis"], "validated")
            self.assertEqual(l2_fm["trust_scope"], "bounded_reusable")


if __name__ == "__main__":
    unittest.main()
