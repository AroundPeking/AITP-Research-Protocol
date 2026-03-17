from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


def _load_module(module_name: str, relative_path: str):
    kernel_root = Path(__file__).resolve().parents[1]
    target_path = kernel_root / relative_path
    if str(target_path.parent) not in sys.path:
        sys.path.insert(0, str(target_path.parent))
    spec = importlib.util.spec_from_file_location(module_name, target_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {target_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RuntimeScriptTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.knowledge_root = Path(self._tmpdir.name)
        (self.knowledge_root / "runtime").mkdir(parents=True, exist_ok=True)
        (self.knowledge_root / "feedback").mkdir(parents=True, exist_ok=True)
        (self.knowledge_root / "validation").mkdir(parents=True, exist_ok=True)
        (self.knowledge_root / "source-layer").mkdir(parents=True, exist_ok=True)
        self.orchestrate_topic = _load_module(
            "aitp_orchestrate_topic_test",
            "runtime/scripts/orchestrate_topic.py",
        )
        self.sync_topic_state = _load_module(
            "aitp_sync_topic_state_test",
            "runtime/scripts/sync_topic_state.py",
        )

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _write_json(self, relative_path: str, payload: dict) -> None:
        path = self.knowledge_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    def _write_jsonl(self, relative_path: str, rows: list[dict]) -> None:
        path = self.knowledge_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "".join(json.dumps(row, ensure_ascii=True) + "\n" for row in rows),
            encoding="utf-8",
        )

    def test_infer_resume_state_handles_accepted_and_needs_revision(self) -> None:
        accepted = self.sync_topic_state.infer_resume_state(
            intake_status=None,
            feedback_status=None,
            latest_decision={"verdict": "accepted", "fallback_targets": []},
            closed_loop_decision=None,
        )
        needs_revision = self.sync_topic_state.infer_resume_state(
            intake_status=None,
            feedback_status=None,
            latest_decision={
                "verdict": "needs_revision",
                "fallback_targets": ["feedback/topics/demo-topic/runs/2026-03-13-demo"],
            },
            closed_loop_decision=None,
        )

        self.assertEqual(accepted[0], "L2")
        self.assertEqual(needs_revision[0], "L3")

    def test_pending_split_contract_action_detects_unapplied_contract(self) -> None:
        self._write_json(
            "runtime/closed_loop_policies.json",
            {
                "candidate_split_policy": {
                    "enabled": True,
                    "auto_apply_contracts": True,
                    "contract_filename": "candidate_split.contract.json",
                    "receipt_filename": "candidate_split_receipts.jsonl",
                }
            },
        )
        self._write_json(
            "feedback/topics/demo-topic/runs/2026-03-13-demo/candidate_split.contract.json",
            {
                "contract_version": 1,
                "splits": [
                    {
                        "source_candidate_id": "candidate:demo",
                        "reason": "Split one wide candidate into smaller units.",
                        "child_candidates": [],
                        "deferred_fragments": [],
                    }
                ],
            },
        )

        actions = self.orchestrate_topic.pending_split_contract_action(
            self.knowledge_root,
            {"topic_slug": "demo-topic", "latest_run_id": "2026-03-13-demo"},
            {"declared_contract_path": None},
        )

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["action_type"], "apply_candidate_split_contract")

    def test_auto_promotion_actions_detect_ready_candidate(self) -> None:
        self._write_json(
            "runtime/closed_loop_policies.json",
            {
                "auto_promotion_policy": {
                    "enabled": True,
                    "default_backend_id": "backend:theoretical-physics-knowledge-network",
                    "trigger_candidate_statuses": ["ready_for_validation"],
                    "theory_formal_candidate_types": ["definition_card"],
                }
            },
        )
        self._write_jsonl(
            "feedback/topics/demo-topic/runs/2026-03-13-demo/candidate_ledger.jsonl",
            [
                {
                    "candidate_id": "candidate:demo-definition",
                    "candidate_type": "definition_card",
                    "title": "Demo Definition",
                    "summary": "A bounded definition.",
                    "topic_slug": "demo-topic",
                    "run_id": "2026-03-13-demo",
                    "origin_refs": [],
                    "question": "Can the definition be promoted?",
                    "assumptions": [],
                    "proposed_validation_route": "bounded-smoke",
                    "intended_l2_targets": ["definition:demo-definition"],
                    "status": "ready_for_validation",
                }
            ],
        )
        self._write_json(
            "validation/topics/demo-topic/runs/2026-03-13-demo/theory-packets/candidate-demo-definition/coverage_ledger.json",
            {"status": "pass"},
        )
        self._write_json(
            "validation/topics/demo-topic/runs/2026-03-13-demo/theory-packets/candidate-demo-definition/agent_consensus.json",
            {"status": "ready"},
        )

        actions = self.orchestrate_topic.auto_promotion_actions(
            self.knowledge_root,
            {"topic_slug": "demo-topic", "latest_run_id": "2026-03-13-demo"},
            {"declared_contract_path": None},
        )

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["action_type"], "auto_promote_candidate")
        self.assertEqual(actions[0]["handler_args"]["candidate_id"], "candidate:demo-definition")

    def test_deferred_reactivation_actions_detect_ready_entry(self) -> None:
        self._write_json(
            "runtime/closed_loop_policies.json",
            {
                "deferred_buffer_policy": {
                    "enabled": True,
                    "auto_reactivate": True,
                }
            },
        )
        self._write_json(
            "runtime/topics/demo-topic/deferred_candidates.json",
            {
                "buffer_version": 1,
                "topic_slug": "demo-topic",
                "updated_at": "2026-03-17T00:00:00+08:00",
                "updated_by": "aitp-cli",
                "entries": [
                    {
                        "entry_id": "deferred:demo",
                        "source_candidate_id": "candidate:demo",
                        "title": "Deferred Demo",
                        "summary": "Deferred until a follow-up source appears.",
                        "reason": "Missing source.",
                        "status": "buffered",
                        "reactivation_conditions": {
                            "source_ids_any": ["paper:followup-source"]
                        },
                        "reactivation_candidate": {
                            "candidate_id": "candidate:demo-reactivated"
                        },
                    }
                ],
            },
        )
        self._write_jsonl(
            "source-layer/topics/demo-topic/source_index.jsonl",
            [
                {
                    "source_id": "paper:followup-source",
                    "title": "Follow-up Source",
                    "summary": "Contains the missing resolution.",
                }
            ],
        )

        actions = self.orchestrate_topic.deferred_reactivation_actions(
            self.knowledge_root,
            {"topic_slug": "demo-topic", "latest_run_id": "2026-03-13-demo"},
            {"declared_contract_path": None},
        )

        self.assertEqual(len(actions), 1)
        self.assertEqual(actions[0]["action_type"], "reactivate_deferred_candidate")
        self.assertEqual(actions[0]["handler_args"]["entry_id"], "deferred:demo")


if __name__ == "__main__":
    unittest.main()
