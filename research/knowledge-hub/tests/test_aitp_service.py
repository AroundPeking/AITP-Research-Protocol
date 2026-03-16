from __future__ import annotations

import json
import tempfile
import textwrap
import unittest
from pathlib import Path

import sys


def _bootstrap_path() -> None:
    package_root = Path(__file__).resolve().parents[1]
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))


_bootstrap_path()

from knowledge_hub.aitp_service import AITPService


class _LoopStubService(AITPService):
    def orchestrate(self, **kwargs):  # noqa: ANN003
        topic_slug = kwargs.get("topic_slug") or "demo-topic"
        runtime_root = self.kernel_root / "runtime" / "topics" / topic_slug
        runtime_root.mkdir(parents=True, exist_ok=True)
        (runtime_root / "topic_state.json").write_text(
            json.dumps(
                {
                    "topic_slug": topic_slug,
                    "latest_run_id": "2026-03-13-demo",
                    "resume_stage": "L3",
                },
                ensure_ascii=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (runtime_root / "action_queue.jsonl").write_text(
            json.dumps(
                {
                    "action_id": "action:demo-topic:01",
                    "status": "pending",
                    "auto_runnable": True,
                    "action_type": "skill_discovery",
                    "handler_args": {"queries": ["finite-size benchmark"]},
                },
                ensure_ascii=True,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        return {
            "topic_slug": topic_slug,
            "runtime_root": str(runtime_root),
        }

    def audit(self, *, topic_slug: str, phase: str = "entry", updated_by: str = "aitp-cli"):
        runtime_root = self.kernel_root / "runtime" / "topics" / topic_slug
        runtime_root.mkdir(parents=True, exist_ok=True)
        (runtime_root / "conformance_state.json").write_text(
            json.dumps({"overall_status": "pass"}, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )
        return {
            "topic_slug": topic_slug,
            "phase": phase,
            "conformance_state": {"overall_status": "pass"},
        }

    def capability_audit(self, *, topic_slug: str, updated_by: str = "aitp-cli"):
        runtime_root = self.kernel_root / "runtime" / "topics" / topic_slug
        payload = {
            "topic_slug": topic_slug,
            "overall_status": "ready",
            "sections": {"runtime": {}},
            "recommendations": [],
        }
        (runtime_root / "capability_registry.json").write_text(
            json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )
        (runtime_root / "capability_report.md").write_text("# Capability audit\n", encoding="utf-8")
        return {
            **payload,
            "capability_registry_path": str(runtime_root / "capability_registry.json"),
            "capability_report_path": str(runtime_root / "capability_report.md"),
        }

    def audit_operation_trust(self, *, topic_slug: str, run_id: str | None = None, updated_by: str = "aitp-cli"):
        return {
            "topic_slug": topic_slug,
            "run_id": run_id or "2026-03-13-demo",
            "overall_status": "pass",
            "operations": [],
            "recommendations": [],
            "trust_audit_path": str(self.kernel_root / "validation" / "topics" / topic_slug / "runs" / "2026-03-13-demo" / "trust_audit.json"),
            "trust_report_path": str(self.kernel_root / "validation" / "topics" / topic_slug / "runs" / "2026-03-13-demo" / "trust_audit.md"),
        }

    def _discover_skills(self, *, topic_slug: str, queries: list[str], updated_by: str, agent_target: str = "openclaw"):
        runtime_root = self.kernel_root / "runtime" / "topics" / topic_slug
        (runtime_root / "skill_discovery.json").write_text(
            json.dumps({"queries": queries}, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )
        (runtime_root / "skill_recommendations.md").write_text("# Skill recommendations\n", encoding="utf-8")
        return {
            "skill_discovery_path": str(runtime_root / "skill_discovery.json"),
            "skill_recommendations_path": str(runtime_root / "skill_recommendations.md"),
            "queries": queries,
        }


class AITPServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.root = Path(self._tmpdir.name)
        self.kernel_root = self.root / "kernel"
        self.repo_root = self.root / "repo"
        self.kernel_root.mkdir(parents=True)
        self.repo_root.mkdir(parents=True)
        (self.kernel_root / "canonical").mkdir(parents=True, exist_ok=True)
        self.service = AITPService(kernel_root=self.kernel_root, repo_root=self.repo_root)

    def tearDown(self) -> None:
        self._tmpdir.cleanup()

    def _write_runtime_state(self, topic_slug: str = "demo-topic", run_id: str = "2026-03-13-demo") -> Path:
        runtime_root = self.kernel_root / "runtime" / "topics" / topic_slug
        runtime_root.mkdir(parents=True, exist_ok=True)
        (runtime_root / "topic_state.json").write_text(
            json.dumps(
                {
                    "topic_slug": topic_slug,
                    "latest_run_id": run_id,
                    "resume_stage": "L3",
                },
                ensure_ascii=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return runtime_root

    def _write_candidate(self, topic_slug: str = "demo-topic", run_id: str = "2026-03-13-demo") -> Path:
        feedback_root = self.kernel_root / "feedback" / "topics" / topic_slug / "runs" / run_id
        feedback_root.mkdir(parents=True, exist_ok=True)
        ledger_path = feedback_root / "candidate_ledger.jsonl"
        row = {
            "candidate_id": "candidate:demo-candidate",
            "candidate_type": "concept",
            "title": "Demo Promoted Concept",
            "summary": "A bounded demo concept for testing the promotion gate and external writeback.",
            "topic_slug": topic_slug,
            "run_id": run_id,
            "origin_refs": [
                {
                    "id": "paper:demo-source",
                    "layer": "L0",
                    "object_type": "source",
                    "path": "source-layer/topics/demo-topic/source_index.jsonl",
                    "title": "Demo Source",
                    "summary": "Public source entry for promotion testing.",
                }
            ],
            "question": "Can this candidate be promoted through a human approval gate into an external L2 backend?",
            "assumptions": ["The example is bounded and non-scientific."],
            "proposed_validation_route": "bounded-smoke",
            "intended_l2_targets": ["concept:demo-promoted-concept"],
            "status": "ready_for_validation",
        }
        ledger_path.write_text(json.dumps(row, ensure_ascii=True) + "\n", encoding="utf-8")
        source_root = self.kernel_root / "source-layer" / "topics" / topic_slug
        source_root.mkdir(parents=True, exist_ok=True)
        (source_root / "source_index.jsonl").write_text(
            json.dumps(
                {
                    "source_id": "paper:demo-source",
                    "source_type": "paper",
                    "title": "Demo Source",
                    "topic_slug": topic_slug,
                    "provenance": {
                        "authors": ["Demo Author"],
                        "published": "2026-03-13T00:00:00+08:00",
                        "updated": "2026-03-13T00:00:00+08:00",
                        "abs_url": "https://example.org/demo",
                        "pdf_url": "https://example.org/demo.pdf",
                        "source_url": "https://example.org/demo.tar.gz",
                    },
                    "acquired_at": "2026-03-13T00:00:00+08:00",
                    "summary": "Demo source summary.",
                },
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
        return ledger_path

    def _write_fake_tpkn_repo(self) -> Path:
        tpkn_root = self.root / "tpkn"
        for relative in (
            "docs",
            "schema",
            "scripts",
            "sources",
            "units/concepts",
            "units/claims",
            "units/derivations",
            "units/methods",
            "units/bridges",
            "units/warnings",
            "edges",
            "indexes",
            "portal",
            "human-mirror",
        ):
            (tpkn_root / relative).mkdir(parents=True, exist_ok=True)
        (tpkn_root / "docs" / "PROTOCOLS.md").write_text("# Demo\n", encoding="utf-8")
        (tpkn_root / "docs" / "L2_RETRIEVAL_PROTOCOL.md").write_text("# Demo\n", encoding="utf-8")
        (tpkn_root / "docs" / "OBJECT_MODEL.md").write_text("# Demo\n", encoding="utf-8")
        (tpkn_root / "docs" / "L2_BRIDGE_PROTOCOL.md").write_text("# Demo\n", encoding="utf-8")
        (tpkn_root / "edges" / "edges.jsonl").write_text("", encoding="utf-8")
        (tpkn_root / "schema" / "unit.schema.json").write_text(
            json.dumps({"title": "demo-unit-schema"}, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )
        (tpkn_root / "schema" / "source-manifest.schema.json").write_text(
            json.dumps({"title": "demo-source-schema"}, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )
        (tpkn_root / "scripts" / "kb.py").write_text(
            textwrap.dedent(
                """\
                from __future__ import annotations

                import json
                import sys
                from pathlib import Path

                ROOT = Path(__file__).resolve().parents[1]
                UNIT_DIRS = {
                    "concept": ROOT / "units" / "concepts",
                    "claim": ROOT / "units" / "claims",
                    "derivation": ROOT / "units" / "derivations",
                    "method": ROOT / "units" / "methods",
                    "bridge": ROOT / "units" / "bridges",
                    "warning": ROOT / "units" / "warnings",
                }

                def read_json(path: Path) -> dict:
                    return json.loads(path.read_text(encoding="utf-8"))

                def build() -> None:
                    rows = []
                    for unit_type, unit_dir in UNIT_DIRS.items():
                        unit_dir.mkdir(parents=True, exist_ok=True)
                        for path in sorted(unit_dir.glob("*.json")):
                            payload = read_json(path)
                            rows.append(
                                {
                                    "id": payload["id"],
                                    "type": payload["type"],
                                    "title": payload["title"],
                                    "summary": payload["summary"],
                                    "path": str(path.relative_to(ROOT)),
                                    "domain": payload.get("domain"),
                                    "subdomain": payload.get("subdomain"),
                                    "tags": payload.get("tags") or [],
                                    "aliases": payload.get("aliases") or [],
                                    "dependencies": payload.get("dependencies") or [],
                                    "related_units": payload.get("related_units") or [],
                                    "formalization_status": payload.get("formalization_status"),
                                    "validation_status": payload.get("validation_status"),
                                    "maturity": payload.get("maturity"),
                                    "source_anchor_count": len(payload.get("source_anchors") or []),
                                }
                            )
                    unit_index = ROOT / "indexes" / "unit_index.jsonl"
                    unit_index.parent.mkdir(parents=True, exist_ok=True)
                    unit_index.write_text(
                        "".join(json.dumps(row, ensure_ascii=False) + "\\n" for row in rows),
                        encoding="utf-8",
                    )

                def main() -> int:
                    if len(sys.argv) < 2:
                        return 1
                    command = sys.argv[1]
                    if command == "check":
                        return 0
                    if command == "build":
                        build()
                        return 0
                    return 1

                if __name__ == "__main__":
                    raise SystemExit(main())
                """
            ),
            encoding="utf-8",
        )
        return tpkn_root

    def test_service_accepts_string_paths(self) -> None:
        (self.repo_root / "AGENTS.md").write_text("# test\n", encoding="utf-8")
        (self.repo_root / "research" / "knowledge-hub").mkdir(parents=True, exist_ok=True)
        service = AITPService(
            kernel_root=str(self.kernel_root),
            repo_root=str(self.repo_root),
        )

        self.assertEqual(service.kernel_root, self.kernel_root.resolve())
        self.assertEqual(service.repo_root, self.repo_root.resolve())

    def test_scaffold_baseline_writes_expected_artifacts(self) -> None:
        payload = self.service.scaffold_baseline(
            topic_slug="demo-topic",
            run_id="2026-03-13-demo",
            title="Public finite-size benchmark baseline",
            reference="arXiv:0000.00000",
            agreement_criterion="curves agree qualitatively and peak order matches",
        )

        plan = Path(payload["paths"]["baseline_plan"])
        results = Path(payload["paths"]["baseline_results"])
        summary = Path(payload["paths"]["baseline_summary"])

        self.assertTrue(plan.exists())
        self.assertTrue(results.exists())
        self.assertTrue(summary.exists())
        rows = [json.loads(line) for line in results.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["status"], "planned")

    def test_scaffold_atomic_understanding_writes_expected_artifacts(self) -> None:
        payload = self.service.scaffold_atomic_understanding(
            topic_slug="demo-topic",
            run_id="2026-03-13-demo",
            method_title="Finite-size spectral diagnostic",
        )

        concept_map = Path(payload["paths"]["atomic_concept_map"])
        graph = Path(payload["paths"]["derivation_dependency_graph"])
        summary = Path(payload["paths"]["understanding_summary"])

        self.assertTrue(concept_map.exists())
        self.assertTrue(graph.exists())
        self.assertTrue(summary.exists())
        concept_payload = json.loads(concept_map.read_text(encoding="utf-8"))
        graph_payload = json.loads(graph.read_text(encoding="utf-8"))
        self.assertEqual(concept_payload["status"], "planned")
        self.assertEqual(graph_payload["status"], "planned")

    def test_materialize_runtime_protocol_bundle_writes_expected_artifacts(self) -> None:
        runtime_root = self._write_runtime_state()
        (runtime_root / "topic_state.json").write_text(
            json.dumps(
                {
                    "topic_slug": "demo-topic",
                    "latest_run_id": "2026-03-13-demo",
                    "resume_stage": "L3",
                    "last_materialized_stage": "L3",
                    "research_mode": "formal_derivation",
                    "backend_bridge_count": 1,
                    "backend_bridges": [
                        {
                            "backend_id": "backend:formal-theory-note-library",
                            "title": "Formal Theory Note Library",
                            "backend_type": "human_note_library",
                            "status": "active",
                            "card_path": "canonical/backends/formal-theory-note-library.json",
                            "card_status": "present",
                            "backend_root": "/tmp/formal-theory-notes",
                            "artifact_granularity": "One derivation-focused note is the atomic backend artifact.",
                            "artifact_kinds": ["formal_theory_note"],
                            "canonical_targets": ["concept", "derivation_object"],
                            "l0_registration_script": "source-layer/scripts/register_local_note_source.py",
                            "source_count": 1,
                            "source_ids": ["local_note:modular-flow-outline"],
                        }
                    ],
                    "research_mode_profile": {
                        "reproducibility_expectations": ["Keep backend provenance explicit."],
                        "note_expectations": ["Write a human-readable derivation note."],
                    },
                },
                ensure_ascii=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (runtime_root / "interaction_state.json").write_text(
            json.dumps(
                {
                    "human_request": "run a bounded public protocol check",
                    "delivery_contract": {
                        "rule": "Outputs must cite exact artifact paths and justify the chosen layer."
                    },
                    "human_edit_surfaces": [
                        {
                            "surface": "runtime_queue_contract",
                            "path": "runtime/topics/demo-topic/action_queue_contract.generated.md",
                            "role": "editable queue contract snapshot",
                        }
                    ],
                    "action_queue_surface": {
                        "queue_source": "heuristic",
                        "declared_contract_path": None,
                        "generated_contract_path": "runtime/topics/demo-topic/action_queue_contract.generated.json",
                        "generated_contract_note_path": "runtime/topics/demo-topic/action_queue_contract.generated.md",
                    },
                    "decision_surface": {
                        "decision_mode": "continue_unfinished",
                        "decision_source": "heuristic",
                        "decision_contract_status": "missing",
                        "control_note_path": None,
                        "selected_action_id": "action:demo-topic:01",
                    },
                },
                ensure_ascii=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (runtime_root / "agent_brief.md").write_text("# Brief\n", encoding="utf-8")
        (runtime_root / "operator_console.md").write_text("# Console\n", encoding="utf-8")
        (runtime_root / "action_queue_contract.generated.md").write_text("# Queue\n", encoding="utf-8")
        (runtime_root / "conformance_report.md").write_text("# Conformance\n", encoding="utf-8")
        (runtime_root / "promotion_gate.json").write_text(
            json.dumps(
                {
                    "status": "approved",
                    "candidate_id": "candidate:demo-candidate",
                    "candidate_type": "concept",
                    "backend_id": "backend:theoretical-physics-knowledge-network",
                    "target_backend_root": "/tmp/tpkn",
                    "approved_by": "human",
                    "promoted_units": [],
                },
                ensure_ascii=True,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (runtime_root / "promotion_gate.md").write_text("# Promotion gate\n", encoding="utf-8")
        (runtime_root / "action_queue.jsonl").write_text(
            json.dumps(
                {
                    "action_id": "action:demo-topic:01",
                    "status": "pending",
                    "action_type": "inspect_resume_state",
                    "summary": "Inspect the current runtime state.",
                    "auto_runnable": False,
                    "queue_source": "heuristic",
                },
                ensure_ascii=True,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )

        result = self.service._materialize_runtime_protocol_bundle(
            topic_slug="demo-topic",
            updated_by="aitp-cli",
            human_request="run a bounded public protocol check",
        )

        protocol_json = Path(result["runtime_protocol_path"])
        protocol_note = Path(result["runtime_protocol_note_path"])
        self.assertTrue(protocol_json.exists())
        self.assertTrue(protocol_note.exists())
        payload = json.loads(protocol_json.read_text(encoding="utf-8"))
        self.assertEqual(payload["human_request"], "run a bounded public protocol check")
        self.assertEqual(payload["priority_rules"][0]["source"], "control_note_or_decision_contract")
        self.assertEqual(payload["action_queue_surface"]["queue_source"], "heuristic")
        self.assertEqual(payload["backend_bridges"][0]["backend_id"], "backend:formal-theory-note-library")
        self.assertEqual(payload["promotion_gate"]["status"], "approved")
        self.assertEqual(
            payload["backend_bridges"][0]["l0_registration_script"],
            "source-layer/scripts/register_local_note_source.py",
        )
        self.assertIn("Prefer durable `next_actions.contract.json`", protocol_note.read_text(encoding="utf-8"))
        self.assertIn("backend:formal-theory-note-library", protocol_note.read_text(encoding="utf-8"))
        self.assertIn("## L2 promotion gate", protocol_note.read_text(encoding="utf-8"))
        self.assertIn("source-layer/scripts/register_local_note_source.py", protocol_note.read_text(encoding="utf-8"))

    def test_operation_trust_registry_blocks_until_gate_is_satisfied(self) -> None:
        self._write_runtime_state()
        payload = self.service.scaffold_operation(
            topic_slug="demo-topic",
            run_id="2026-03-13-demo",
            title="Small-system validation backend",
            kind="numerical",
        )
        manifest = Path(payload["manifest_path"])
        summary = Path(payload["summary_path"])
        self.assertTrue(manifest.exists())
        self.assertTrue(summary.exists())

        blocked = self.service.audit_operation_trust(
            topic_slug="demo-topic",
            run_id="2026-03-13-demo",
        )
        self.assertEqual(blocked["overall_status"], "blocked")

        self.service.update_operation(
            topic_slug="demo-topic",
            run_id="2026-03-13-demo",
            operation="Small-system validation backend",
            baseline_status="passed",
            artifact_paths=["validation/topics/demo-topic/runs/2026-03-13-demo/results/benchmark.json"],
        )
        passed = self.service.audit_operation_trust(
            topic_slug="demo-topic",
            run_id="2026-03-13-demo",
        )
        self.assertEqual(passed["overall_status"], "pass")
        self.assertEqual(passed["operations"][0]["trust_ready"], True)

    def test_capability_audit_writes_registry(self) -> None:
        self._write_runtime_state()
        self.service.scaffold_operation(
            topic_slug="demo-topic",
            run_id="2026-03-13-demo",
            title="Finite-size validation baseline",
            kind="numerical",
        )
        self.service.update_operation(
            topic_slug="demo-topic",
            run_id="2026-03-13-demo",
            operation="Finite-size validation baseline",
            baseline_status="passed",
        )
        self.service.audit_operation_trust(
            topic_slug="demo-topic",
            run_id="2026-03-13-demo",
        )

        payload = self.service.capability_audit(topic_slug="demo-topic")
        registry = Path(payload["capability_registry_path"])
        report = Path(payload["capability_report_path"])
        self.assertTrue(registry.exists())
        self.assertTrue(report.exists())
        self.assertEqual(payload["overall_status"], "ready")
        self.assertEqual(payload["sections"]["layers"]["L2"]["status"], "present")
        self.assertEqual(payload["sections"]["capabilities"]["operation_trust"]["status"], "present")

    def test_doctor_reports_layer_roots_and_protocol_contracts(self) -> None:
        for filename in (
            "LAYER_MAP.md",
            "ROUTING_POLICY.md",
            "COMMUNICATION_CONTRACT.md",
            "AUTONOMY_AND_OPERATOR_MODEL.md",
            "L2_CONSULTATION_PROTOCOL.md",
            "INDEXING_RULES.md",
            "L0_SOURCE_LAYER.md",
        ):
            (self.kernel_root / filename).write_text("# present\n", encoding="utf-8")

        payload = self.service.ensure_cli_installed()

        self.assertEqual(payload["layer_roots"]["L2"]["status"], "present")
        self.assertEqual(payload["protocol_contracts"]["layer_map"]["status"], "present")

    def test_run_topic_loop_writes_loop_state_and_executes_auto_actions(self) -> None:
        service = _LoopStubService(kernel_root=self.kernel_root, repo_root=self.repo_root)
        payload = service.run_topic_loop(
            topic_slug="demo-topic",
            human_request="find capability gaps",
            max_auto_steps=2,
        )

        loop_state_path = Path(payload["loop_state_path"])
        self.assertTrue(loop_state_path.exists())
        loop_state = json.loads(loop_state_path.read_text(encoding="utf-8"))
        self.assertEqual(loop_state["exit_conformance"], "pass")
        self.assertEqual(payload["auto_actions"]["executed"][0]["status"], "completed")
        self.assertTrue(Path(payload["runtime_protocol"]["runtime_protocol_path"]).exists())
        self.assertTrue(Path(payload["runtime_protocol"]["runtime_protocol_note_path"]).exists())

    def test_request_and_approve_promotion_gate_write_runtime_artifacts(self) -> None:
        self._write_runtime_state()
        self._write_candidate()

        requested = self.service.request_promotion(
            topic_slug="demo-topic",
            candidate_id="candidate:demo-candidate",
            backend_id="backend:theoretical-physics-knowledge-network",
        )
        self.assertEqual(requested["status"], "pending_human_approval")
        self.assertTrue(Path(requested["promotion_gate_path"]).exists())
        self.assertTrue(Path(requested["promotion_gate_note_path"]).exists())

        approved = self.service.approve_promotion(
            topic_slug="demo-topic",
            candidate_id="candidate:demo-candidate",
        )
        self.assertEqual(approved["status"], "approved")
        gate_payload = json.loads(Path(approved["promotion_gate_path"]).read_text(encoding="utf-8"))
        self.assertEqual(gate_payload["approved_by"], "aitp-cli")

    def test_promote_candidate_writes_tpkn_unit_and_decision(self) -> None:
        self._write_runtime_state()
        self._write_candidate()
        tpkn_root = self._write_fake_tpkn_repo()
        self.service.request_promotion(
            topic_slug="demo-topic",
            candidate_id="candidate:demo-candidate",
            backend_id="backend:theoretical-physics-knowledge-network",
            target_backend_root=str(tpkn_root),
        )
        self.service.approve_promotion(
            topic_slug="demo-topic",
            candidate_id="candidate:demo-candidate",
        )

        payload = self.service.promote_candidate(
            topic_slug="demo-topic",
            candidate_id="candidate:demo-candidate",
            target_backend_root=str(tpkn_root),
            domain="demo-domain",
            subdomain="demo-subdomain",
        )

        unit_path = Path(payload["target_unit_path"])
        decision_path = Path(payload["promotion_decision_path"])
        consultation_result_path = Path(payload["consultation"]["consultation_result_path"])
        self.assertTrue(unit_path.exists())
        self.assertTrue(decision_path.exists())
        self.assertTrue(consultation_result_path.exists())
        unit_payload = json.loads(unit_path.read_text(encoding="utf-8"))
        self.assertEqual(unit_payload["id"], "concept:demo-promoted-concept")
        self.assertEqual(unit_payload["domain"], "demo-domain")
        decision_rows = [json.loads(line) for line in decision_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(decision_rows[-1]["verdict"], "accepted")
        gate_payload = json.loads(Path(payload["promotion_gate_path"]).read_text(encoding="utf-8"))
        self.assertEqual(gate_payload["status"], "promoted")
        candidate_rows = [
            json.loads(line)
            for line in (self.kernel_root / "feedback" / "topics" / "demo-topic" / "runs" / "2026-03-13-demo" / "candidate_ledger.jsonl").read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertEqual(candidate_rows[0]["status"], "promoted")

    def test_execute_auto_actions_supports_literature_followup_search(self) -> None:
        topic_slug = "demo-topic"
        run_id = "2026-03-13-demo"
        runtime_root = self.kernel_root / "runtime" / "topics" / topic_slug
        runtime_root.mkdir(parents=True, exist_ok=True)
        handler_path = self.kernel_root / "runtime" / "scripts" / "fake_literature_followup.py"
        handler_path.parent.mkdir(parents=True, exist_ok=True)
        handler_path.write_text(
            textwrap.dedent(
                """\
                #!/usr/bin/env python3
                from __future__ import annotations

                import argparse
                import json
                from pathlib import Path

                parser = argparse.ArgumentParser()
                parser.add_argument("--topic-slug", required=True)
                parser.add_argument("--run-id", required=True)
                parser.add_argument("--query", required=True)
                parser.add_argument("--priority")
                parser.add_argument("--target-source-type")
                parser.add_argument("--max-results")
                parser.add_argument("--updated-by", required=True)
                args = parser.parse_args()

                knowledge_root = Path(__file__).resolve().parents[2]
                receipts_path = (
                    knowledge_root
                    / "validation"
                    / "topics"
                    / args.topic_slug
                    / "runs"
                    / args.run_id
                    / "literature_followup_receipts.jsonl"
                )
                receipts_path.parent.mkdir(parents=True, exist_ok=True)
                payload = {
                    "topic_slug": args.topic_slug,
                    "run_id": args.run_id,
                    "query": args.query,
                    "priority": args.priority,
                    "target_source_type": args.target_source_type,
                    "max_results": args.max_results,
                    "updated_by": args.updated_by,
                    "status": "completed",
                }
                with receipts_path.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(payload, ensure_ascii=True) + "\\n")
                print(json.dumps(payload, ensure_ascii=True))
                """
            ),
            encoding="utf-8",
        )
        queue_path = runtime_root / "action_queue.jsonl"
        queue_path.write_text(
            json.dumps(
                {
                    "action_id": "action:demo-topic:literature-followup:01",
                    "status": "pending",
                    "auto_runnable": True,
                    "action_type": "literature_followup_search",
                    "handler": str(handler_path),
                    "handler_args": {
                        "run_id": run_id,
                        "query": "hs control-path baseline",
                        "priority": "medium",
                        "target_source_type": "paper",
                        "max_results": 2,
                    },
                },
                ensure_ascii=True,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )

        payload = self.service._execute_auto_actions(
            topic_slug=topic_slug,
            updated_by="aitp-cli",
            max_auto_steps=1,
            default_skill_queries=None,
        )

        self.assertEqual(payload["executed"][0]["status"], "completed")
        self.assertEqual(payload["executed"][0]["result"]["receipt"]["status"], "completed")
        receipt_path = (
            self.kernel_root
            / "validation"
            / "topics"
            / topic_slug
            / "runs"
            / run_id
            / "literature_followup_receipts.jsonl"
        )
        self.assertTrue(receipt_path.exists())
        receipt_rows = [json.loads(line) for line in receipt_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(receipt_rows[0]["query"], "hs control-path baseline")
        queue_row = json.loads(queue_path.read_text(encoding="utf-8").splitlines()[0])
        self.assertEqual(queue_row["status"], "completed")

    def test_install_agent_writes_wrapper_files(self) -> None:
        codex_target = self.root / "codex-skill"
        result = self.service.install_agent(
            agent="codex",
            scope="user",
            target_root=str(codex_target),
        )

        self.assertEqual(result["installed"][0]["kind"], "skill")
        skill_path = codex_target / ".agents" / "skills" / "aitp-runtime" / "SKILL.md"
        setup_path = codex_target / ".agents" / "skills" / "aitp-runtime" / "AITP_MCP_SETUP.md"
        self.assertTrue(skill_path.exists())
        self.assertTrue(setup_path.exists())
        self.assertIn("aitp loop", skill_path.read_text(encoding="utf-8"))
        self.assertIn("aitp operation-init", skill_path.read_text(encoding="utf-8"))
        self.assertIn("codex mcp add aitp", setup_path.read_text(encoding="utf-8"))

        opencode_target = self.root / "opencode-commands"
        result = self.service.install_agent(
            agent="opencode",
            scope="user",
            target_root=str(opencode_target),
        )
        installed_paths = {Path(item["path"]).name for item in result["installed"]}
        self.assertIn("AITP_COMMAND_HARNESS.md", installed_paths)
        self.assertIn("aitp.md", installed_paths)
        self.assertIn("aitp-resume.md", installed_paths)
        self.assertIn("aitp-loop.md", installed_paths)
        self.assertIn("aitp-audit.md", installed_paths)
        self.assertIn("AITP_MCP_CONFIG.json", installed_paths)

        claude_target = self.root / "claude-runtime"
        result = self.service.install_agent(
            agent="claude-code",
            scope="user",
            target_root=str(claude_target),
        )
        installed_paths = {Path(item["path"]).name for item in result["installed"]}
        self.assertIn("SKILL.md", installed_paths)
        self.assertIn("aitp.md", installed_paths)
        self.assertIn("aitp-loop.md", installed_paths)
        self.assertIn("aitp-audit.md", installed_paths)
        self.assertIn("AITP_MCP_SETUP.md", installed_paths)
