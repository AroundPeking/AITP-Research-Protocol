from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


def _bootstrap_path() -> None:
    package_root = Path(__file__).resolve().parents[1]
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))


_bootstrap_path()

from knowledge_hub.aitp_service import AITPService


def test_materialize_research_report_creates_runtime_surface_and_recommended_skills() -> None:
    with tempfile.TemporaryDirectory() as td:
        kernel_root = Path(td)
        service = AITPService(kernel_root=kernel_root, repo_root=Path.cwd().resolve())

        topic_slug = "demo-topic"
        run_id = "run-001"
        runtime_root = kernel_root / "topics" / topic_slug / "runtime"
        run_root = kernel_root / "topics" / topic_slug / "L3" / "runs" / run_id
        iteration_root = run_root / "iterations" / "iteration-001"
        runtime_root.mkdir(parents=True, exist_ok=True)
        iteration_root.mkdir(parents=True, exist_ok=True)

        (runtime_root / "research_question.contract.json").write_text(
            json.dumps(
                {
                    "title": "Demo Topic",
                    "question": "Can the bounded derivation be reconstructed and benchmark-checked without hiding the normalization caveat?",
                    "scope": ["Keep the bounded route explicit."],
                    "assumptions": ["Weak coupling."],
                    "formalism_and_notation": ["Use the source convention before translating benchmark notation."],
                    "open_ambiguities": ["One normalization factor remains unresolved."],
                    "l1_source_intake": {
                        "reading_depth_rows": [
                            {"source_title": "Lecture Notes A", "reading_depth": "full_read"},
                            {"source_title": "Benchmark Note B", "reading_depth": "multi_pass"},
                        ]
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (runtime_root / "idea_packet.json").write_text(
            json.dumps(
                {
                    "status": "approved_for_execution",
                    "initial_idea": "Turn the source derivation into a bounded research notebook route.",
                    "novelty_target": "Make the normalization caveat explicit.",
                    "first_validation_route": "Benchmark comparison",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (runtime_root / "unfinished_work.json").write_text(
            json.dumps(
                {
                    "items": [
                        {"summary": "Recover the omitted factor from the benchmark convention note.", "status": "pending"}
                    ]
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (run_root / "candidate_ledger.jsonl").write_text(
            json.dumps(
                {
                    "candidate_id": "candidate:demo-bound",
                    "candidate_type": "derivation_object",
                    "title": "Bounded derivation candidate",
                    "summary": "A bounded candidate with one unresolved normalization caveat.",
                    "question": "Does the benchmark convention preserve the same coefficient?",
                    "status": "ready_for_validation",
                    "proposed_validation_route": "benchmark_review",
                    "assumptions": ["Weak coupling."],
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        (run_root / "derivation_records.jsonl").write_text(
            json.dumps(
                {
                    "derivation_id": "candidate:demo-bound",
                    "title": "Source reconstruction",
                    "body": "Starting from the source statement we derive the bounded coefficient and keep the convention explicit.",
                    "derivation_kind": "source_reconstruction",
                    "status": "in_progress",
                    "assumptions": ["Weak coupling."],
                    "source_refs": ["Lecture Notes A §2"],
                    "provenance_note": "AI provisional reasoning.",
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        (run_root / "l2_comparison_receipts.jsonl").write_text(
            json.dumps(
                {
                    "comparison_id": "comparison:demo",
                    "candidate_ref_id": "candidate:demo-bound",
                    "title": "Benchmark comparison",
                    "comparison_summary": "The main backbone agrees, but one factor remains unresolved.",
                    "compared_unit_ids": ["derivation:demo-l2"],
                    "comparison_scope": "bounded benchmark route",
                    "outcome": "partial_match",
                    "limitations": ["One normalization factor remains unresolved."],
                },
                ensure_ascii=False,
                separators=(",", ":"),
            )
            + "\n",
            encoding="utf-8",
        )
        (iteration_root / "plan.contract.json").write_text(
            json.dumps(
                {
                    "selected_action_summary": "Check the normalization bridge against the benchmark note.",
                    "pass_conditions": ["Keep the factor bookkeeping explicit."],
                    "failure_signals": ["A hidden factor appears."],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (iteration_root / "l4_return.json").write_text(
            json.dumps(
                {"returned_result_status": "partial", "returned_result_summary": "The main backbone survives but one factor remains unresolved."},
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        (iteration_root / "l3_synthesis.json").write_text(
            json.dumps(
                {
                    "conclusion_status": "continue_iteration",
                    "synthesis_summary": "The route remains useful but the caveat is still active.",
                    "next_step_summary": "Recover the omitted factor before promotion.",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        payload = service.materialize_research_report(
            topic_slug=topic_slug,
            run_id=run_id,
            updated_by="test",
        )

        assert payload["status"] == "available"
        assert payload["problem"]["question"].startswith("Can the bounded derivation")
        assert "normalization caveat" in payload["physical_motivation"]
        assert payload["recommended_skills"]
        assert any(item["skill_name"] == "aitp-topic-report-author" for item in payload["recommended_skills"])
        assert payload["current_claims"]
        assert payload["current_claims"][0]["status"] == "validated_partial"
        assert payload["iteration_rounds"]
        assert "normalization bridge" in payload["iteration_rounds"][0]["round_question"]
        assert Path(payload["path"]).exists()
        assert Path(payload["note_path"]).exists()

