"""Tests for mechanical_completion_preflight (backlog 999.73).

The preflight runs zero-cost mechanical checks before the expensive
topic-completion assessment. It validates run resolution, operation
baseline status, candidate existence, follow-up debt, and gap status
without invoking any LLM or writing any new artifacts.
"""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

import sys


def _bootstrap_path() -> None:
    package_root = Path(__file__).resolve().parents[1]
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))


_bootstrap_path()

from knowledge_hub.aitp_service import AITPService


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=True) for row in rows) + "\n",
        encoding="utf-8",
    )


class MechanicalCompletionPreflightTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        self.kernel_root = self.root / "kernel"
        self.repo_root = self.root / "repo"
        self.package_root = Path(__file__).resolve().parents[1]
        self.kernel_root.mkdir(parents=True)
        self.repo_root.mkdir(parents=True)
        (self.kernel_root / "schemas").mkdir(parents=True, exist_ok=True)
        (self.kernel_root / "runtime" / "schemas").mkdir(parents=True, exist_ok=True)
        for schema_path in (self.package_root / "schemas").glob("*.json"):
            shutil.copyfile(schema_path, self.kernel_root / "schemas" / schema_path.name)
        shutil.copyfile(
            self.package_root / "runtime" / "schemas" / "progressive-disclosure-runtime-bundle.schema.json",
            self.kernel_root / "runtime" / "schemas" / "progressive-disclosure-runtime-bundle.schema.json",
        )
        shutil.copytree(
            self.package_root / "runtime" / "scripts",
            self.kernel_root / "runtime" / "scripts",
            dirs_exist_ok=True,
        )
        self.service = AITPService(kernel_root=self.kernel_root, repo_root=self.repo_root)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _bootstrap_topic(
        self,
        topic_slug: str = "test-topic",
        run_id: str = "run-001",
        *,
        with_candidates: bool = True,
        with_latest_run: bool = True,
    ) -> None:
        """Create a minimal topic with topic_state pointing to run_id.

        Candidate ledger lives at topics/{slug}/L3/runs/{run_id}/candidate_ledger.jsonl.
        """
        runtime = self.kernel_root / "topics" / topic_slug / "runtime"
        _write_json(runtime / "topic_state.json", {
            "topic_slug": topic_slug,
            "latest_run_id": run_id if with_latest_run else "",
            "resume_stage": "L3",
            "last_materialized_stage": "L3",
            "research_mode": "formal_derivation",
            "summary": "Test topic for preflight checks.",
        })
        _write_json(runtime / "interaction_state.json", {
            "human_request": "Test preflight.",
            "decision_surface": {"selected_action_id": "action:test:work", "decision_source": "heuristic"},
        })
        _write_jsonl(runtime / "action_queue.jsonl", [
            {"action_id": "action:test:work", "status": "pending", "action_type": "manual_followup", "summary": "Do work.", "auto_runnable": False, "queue_source": "heuristic"},
        ])
        if with_candidates:
            cand_path = (
                self.kernel_root / "topics" / topic_slug / "L3"
                / "runs" / run_id / "candidate_ledger.jsonl"
            )
            _write_jsonl(cand_path, [
                {"candidate_id": "candidate:test-1", "topic_completion_status": "promotion-ready"},
            ])

    def _write_operation(
        self,
        topic_slug: str,
        run_id: str,
        operation_id: str,
        baseline_status: str,
    ) -> None:
        op_dir = (
            self.kernel_root / "topics" / topic_slug / "L4"
            / "runs" / run_id / "operations" / operation_id
        )
        _write_json(op_dir / "operation_manifest.json", {
            "operation_id": operation_id,
            "baseline_status": baseline_status,
            "operation_type": "proof",
        })

    def test_preflight_blocked_when_no_run_id(self) -> None:
        """Topic with no latest_run_id should block on run_id_resolved."""
        self._bootstrap_topic(with_latest_run=False)
        result = self.service.mechanical_completion_preflight(topic_slug="test-topic", run_id=None)
        mp = result["mechanical_preflight"]
        run_check = next(c for c in mp["checks"] if c["check"] == "run_id_resolved")
        self.assertEqual(run_check["status"], "blocked")

    def test_preflight_pass_with_minimal_topic(self) -> None:
        """A minimal topic with candidates and no blockers should pass all checks."""
        self._bootstrap_topic(with_candidates=True)
        result = self.service.mechanical_completion_preflight(topic_slug="test-topic", run_id="run-001")
        mp = result["mechanical_preflight"]
        self.assertEqual(mp["status"], "pass")
        self.assertEqual(mp["blocked_count"], 0)

    def test_preflight_blocked_by_unconfirmed_operation(self) -> None:
        """An operation with baseline_status='planned' should block."""
        self._bootstrap_topic()
        self._write_operation("test-topic", "run-001", "op-001", "planned")
        result = self.service.mechanical_completion_preflight(topic_slug="test-topic", run_id="run-001")
        mp = result["mechanical_preflight"]
        self.assertEqual(mp["status"], "blocked")
        op_check = next(c for c in mp["checks"] if c["check"] == "operations_baseline_confirmed")
        self.assertEqual(op_check["status"], "blocked")
        self.assertIn("detail", op_check)
        self.assertEqual(len(op_check["detail"]), 1)

    def test_preflight_pass_with_confirmed_operation(self) -> None:
        """An operation with baseline_status='pass' should not block."""
        self._bootstrap_topic()
        self._write_operation("test-topic", "run-001", "op-001", "pass")
        result = self.service.mechanical_completion_preflight(topic_slug="test-topic", run_id="run-001")
        mp = result["mechanical_preflight"]
        op_check = next(c for c in mp["checks"] if c["check"] == "operations_baseline_confirmed")
        self.assertEqual(op_check["status"], "pass")

    def test_preflight_blocked_by_no_candidates(self) -> None:
        """A topic with no candidate rows should block on candidates_exist."""
        self._bootstrap_topic(with_candidates=False)
        result = self.service.mechanical_completion_preflight(topic_slug="test-topic", run_id="run-001")
        cand_check = next(c for c in result["mechanical_preflight"]["checks"] if c["check"] == "candidates_exist")
        self.assertEqual(cand_check["status"], "blocked")

    def test_preflight_pass_with_candidates(self) -> None:
        """A topic with candidate rows should pass candidates_exist."""
        self._bootstrap_topic(with_candidates=True)
        result = self.service.mechanical_completion_preflight(topic_slug="test-topic", run_id="run-001")
        cand_check = next(c for c in result["mechanical_preflight"]["checks"] if c["check"] == "candidates_exist")
        self.assertEqual(cand_check["status"], "pass")

    def test_preflight_blocked_by_pending_followup(self) -> None:
        """A spawned follow-up child topic should block followup_debt_clear."""
        self._bootstrap_topic()
        runtime = self.kernel_root / "topics" / "test-topic" / "runtime"
        child_return_path = str(
            self.kernel_root / "topics" / "test-topic--followup--child" / "runtime" / "followup_return_packet.json"
        )
        _write_jsonl(runtime / "followup_subtopics.jsonl", [
            {
                "child_topic_slug": "test-topic--followup--child",
                "parent_topic_slug": "test-topic",
                "status": "spawned",
                "query": "Test follow-up.",
                "return_packet_path": child_return_path,
            },
        ])
        result = self.service.mechanical_completion_preflight(topic_slug="test-topic", run_id="run-001")
        followup_check = next(c for c in result["mechanical_preflight"]["checks"] if c["check"] == "followup_debt_clear")
        self.assertEqual(followup_check["status"], "blocked")

    def test_preflight_pass_when_followup_reintegrated(self) -> None:
        """A reintegrated follow-up child should not block."""
        self._bootstrap_topic()
        runtime = self.kernel_root / "topics" / "test-topic" / "runtime"
        child_return_path = str(
            self.kernel_root / "topics" / "test-topic--followup--child" / "runtime" / "followup_return_packet.json"
        )
        _write_jsonl(runtime / "followup_subtopics.jsonl", [
            {
                "child_topic_slug": "test-topic--followup--child",
                "parent_topic_slug": "test-topic",
                "status": "reintegrated",
                "query": "Test follow-up.",
                "return_packet_path": child_return_path,
            },
        ])
        _write_jsonl(runtime / "followup_reintegration.jsonl", [
            {
                "child_topic_slug": "test-topic--followup--child",
                "parent_topic_slug": "test-topic",
                "status": "reintegrated",
            },
        ])
        result = self.service.mechanical_completion_preflight(topic_slug="test-topic", run_id="run-001")
        followup_check = next(c for c in result["mechanical_preflight"]["checks"] if c["check"] == "followup_debt_clear")
        self.assertEqual(followup_check["status"], "pass")

    def test_preflight_blocked_by_open_gaps(self) -> None:
        """Candidates with promotion_blockers should block gap_packets_clear."""
        self._bootstrap_topic(with_candidates=False)
        cand_path = (
            self.kernel_root / "topics" / "test-topic" / "L3"
            / "runs" / "run-001" / "candidate_ledger.jsonl"
        )
        _write_jsonl(cand_path, [
            {
                "candidate_id": "candidate:test-1",
                "topic_completion_status": "promotion-ready",
                "promotion_blockers": ["Missing cited definition."],
            },
        ])
        result = self.service.mechanical_completion_preflight(topic_slug="test-topic", run_id="run-001")
        gap_check = next(c for c in result["mechanical_preflight"]["checks"] if c["check"] == "gap_packets_clear")
        self.assertEqual(gap_check["status"], "blocked")

    def _make_topic_ready_for_deeper_execution(self, topic_slug: str) -> None:
        """Write a session_start contract and acknowledge reads so the gate passes."""
        runtime = self.kernel_root / "topics" / topic_slug / "runtime"
        _write_json(runtime / "session_start.contract.json", {
            "topic_slug": topic_slug,
            "updated_at": "2026-04-17T00:00:00+00:00",
            "artifacts": {
                "session_start_note_path": str(runtime / "session_start.generated.md"),
                "runtime_protocol_note_path": str(runtime / "runtime_protocol.generated.md"),
            },
            "must_read_now": [],
        })
        _write_jsonl(runtime / "required_read_receipts.jsonl", [
            {"path": str(runtime / "session_start.generated.md"), "generation": "2026-04-17T00:00:00+00:00"},
            {"path": str(runtime / "runtime_protocol.generated.md"), "generation": "2026-04-17T00:00:00+00:00"},
        ])
        (runtime / "session_start.generated.md").write_text("# Session start\n", encoding="utf-8")
        (runtime / "runtime_protocol.generated.md").write_text("# Runtime protocol\n", encoding="utf-8")

    def test_assess_topic_completion_short_circuits_on_preflight_blocked(self) -> None:
        """assess_topic_completion should return early when preflight is blocked."""
        self._bootstrap_topic(with_candidates=False)
        self._make_topic_ready_for_deeper_execution("test-topic")
        result = self.service.assess_topic_completion(topic_slug="test-topic", run_id="run-001")
        self.assertTrue(result.get("preflight_blocked"))
        self.assertEqual(result["mechanical_preflight"]["status"], "blocked")

    def test_assess_topic_completion_skip_preflight(self) -> None:
        """assess_topic_completion with skip_preflight should bypass preflight."""
        self._bootstrap_topic(with_candidates=True)
        self._make_topic_ready_for_deeper_execution("test-topic")
        result = self.service.assess_topic_completion(
            topic_slug="test-topic", run_id="run-001", skip_preflight=True,
        )
        self.assertFalse(result.get("preflight_blocked"))
        self.assertNotIn("mechanical_preflight", result)

    def test_preflight_returns_structured_checks(self) -> None:
        """Every check should have check, status, summary keys."""
        self._bootstrap_topic(with_candidates=True)
        result = self.service.mechanical_completion_preflight(topic_slug="test-topic", run_id="run-001")
        mp = result["mechanical_preflight"]
        self.assertIn("status", mp)
        self.assertIn("blocked_count", mp)
        self.assertIn("total_checks", mp)
        self.assertIn("checks", mp)
        for check in mp["checks"]:
            self.assertIn("check", check)
            self.assertIn("status", check)
            self.assertIn("summary", check)
            self.assertIn(check["status"], ("pass", "blocked"))

    def test_preflight_no_operations_passes(self) -> None:
        """When no operations exist, operations_exist check should pass."""
        self._bootstrap_topic(with_candidates=True)
        result = self.service.mechanical_completion_preflight(topic_slug="test-topic", run_id="run-001")
        op_check = next(c for c in result["mechanical_preflight"]["checks"] if c["check"] == "operations_exist")
        self.assertEqual(op_check["status"], "pass")


if __name__ == "__main__":
    unittest.main()
