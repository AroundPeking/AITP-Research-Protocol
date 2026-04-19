from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path
from typing import Any


def _bootstrap_path() -> None:
    package_root = Path(__file__).resolve().parents[1]
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))


_bootstrap_path()

from knowledge_hub.aitp_service import AITPService


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _build_service_fixture(
    *,
    round_type: str,
    candidate_rows: list[dict[str, Any]] | None = None,
    derivation_rows: list[dict[str, Any]] | None = None,
    comparison_rows: list[dict[str, Any]] | None = None,
    plan_overrides: dict[str, Any] | None = None,
    l4_return_overrides: dict[str, Any] | None = None,
    synthesis_overrides: dict[str, Any] | None = None,
    unfinished_items: list[dict[str, Any]] | None = None,
) -> tuple[AITPService, str, str, Path]:
    td = tempfile.TemporaryDirectory()
    kernel_root = Path(td.name)
    service = AITPService(kernel_root=kernel_root, repo_root=Path.cwd().resolve())
    service.kernel_root = kernel_root.resolve()

    topic_slug = "demo-topic"
    run_id = "run-001"
    runtime_root = kernel_root / "topics" / topic_slug / "runtime"
    run_root = kernel_root / "topics" / topic_slug / "L3" / "runs" / run_id
    iteration_root = run_root / "iterations" / "iteration-001"
    runtime_root.mkdir(parents=True, exist_ok=True)
    iteration_root.mkdir(parents=True, exist_ok=True)

    _write_json(
        runtime_root / "research_question.contract.json",
        {
            "title": "Demo Topic",
            "question": "Can the bounded derivation be reconstructed and benchmark-checked without hiding the normalization caveat?",
            "scope": ["Keep the bounded route explicit."],
            "assumptions": ["Weak coupling."],
            "observables": ["Hall-response coefficient"],
            "formalism_and_notation": [
                "Use the source convention before translating benchmark notation."
            ],
            "open_ambiguities": ["One normalization factor remains unresolved."],
            "l1_source_intake": {
                "reading_depth_rows": [
                    {"source_title": "Lecture Notes A", "reading_depth": "full_read"},
                    {"source_title": "Benchmark Note B", "reading_depth": "multi_pass"},
                ],
                "notation_tension_candidates": [
                    {
                        "summary": "Lecture Notes A uses k while Benchmark Note B uses sigma_xy for the same response coefficient."
                    }
                ],
            },
        },
    )
    _write_json(
        runtime_root / "idea_packet.json",
        {
            "status": "approved_for_execution",
            "initial_idea": "Turn the source derivation into a bounded research notebook route.",
            "novelty_target": "Make the normalization caveat explicit.",
            "first_validation_route": "Benchmark comparison",
        },
    )
    _write_json(
        runtime_root / "unfinished_work.json",
        {"items": unfinished_items or []},
    )

    _write_jsonl(
        run_root / "candidate_ledger.jsonl",
        candidate_rows
        or [
            {
                "candidate_id": "candidate:demo-bound",
                "candidate_type": "derivation_object",
                "title": "Bounded derivation candidate",
                "summary": "A bounded candidate with one unresolved normalization caveat.",
                "question": "Does the benchmark convention preserve the same coefficient?",
                "status": "ready_for_validation",
                "proposed_validation_route": "benchmark_review",
                "assumptions": ["Weak coupling."],
            }
        ],
    )
    _write_jsonl(run_root / "derivation_records.jsonl", derivation_rows or [])
    _write_jsonl(run_root / "l2_comparison_receipts.jsonl", comparison_rows or [])

    plan_payload = {
        "round_type": round_type,
        "selected_action_summary": "Check the normalization bridge against the benchmark note.",
        "pass_conditions": ["Keep the factor bookkeeping explicit."],
        "failure_signals": ["A hidden factor appears."],
    }
    if plan_overrides:
        plan_payload.update(plan_overrides)
    _write_json(iteration_root / "plan.contract.json", plan_payload)

    l4_payload = {
        "returned_result_status": "partial",
        "returned_result_summary": "The main backbone survives but one factor remains unresolved.",
    }
    if l4_return_overrides:
        l4_payload.update(l4_return_overrides)
    _write_json(iteration_root / "l4_return.json", l4_payload)

    synthesis_payload = {
        "conclusion_status": "continue_iteration",
        "synthesis_summary": "The route remains useful but the caveat is still active.",
        "next_step_summary": "Recover the omitted factor before promotion.",
    }
    if synthesis_overrides:
        synthesis_payload.update(synthesis_overrides)
    _write_json(iteration_root / "l3_synthesis.json", synthesis_payload)

    # Keep the tempdir alive by attaching it to the service object during the test.
    service._test_tempdir = td  # type: ignore[attr-defined]
    return service, topic_slug, run_id, runtime_root


def test_materialize_research_report_builds_physicist_facing_sections_and_qualified_statement() -> None:
    service, topic_slug, run_id, _runtime_root = _build_service_fixture(
        round_type="derivation_round",
        derivation_rows=[
            {
                "derivation_id": "candidate:demo-bound",
                "title": "Source reconstruction",
                "body": "Starting from the source statement we derive the bounded coefficient and keep the convention explicit.",
                "derivation_kind": "source_reconstruction",
                "status": "in_progress",
                "assumptions": ["Weak coupling."],
                "source_refs": ["Lecture Notes A §2 eq.(4)"],
                "provenance_note": "AI provisional reasoning.",
                "derivation_steps": [
                    {
                        "label": "Step 1",
                        "equation": "k = (1/2\\pi) \\int F",
                        "justification": "Source equation.",
                        "source_anchor": "Lecture Notes A §2 eq.(4)",
                        "is_l3_completion": False,
                        "assumption_dependencies": ["Weak coupling."],
                    }
                ],
            }
        ],
        comparison_rows=[
            {
                "comparison_id": "comparison:demo",
                "candidate_ref_id": "candidate:demo-bound",
                "title": "Benchmark comparison",
                "comparison_summary": "The main backbone agrees, but one factor remains unresolved.",
                "compared_unit_ids": ["derivation:demo-l2"],
                "comparison_scope": "bounded benchmark route",
                "outcome": "partial_match",
                "limitations": ["One normalization factor remains unresolved."],
            }
        ],
    )

    payload = service.materialize_research_report(
        topic_slug=topic_slug,
        run_id=run_id,
        updated_by="test",
    )

    assert payload["status"] == "available"
    assert payload["physical_target"]
    assert payload["observables_or_decision_targets"] == ["Hall-response coefficient"]
    assert payload["current_dispute_or_bottleneck"] == "One normalization factor remains unresolved."
    assert payload["convention_ledger"]
    assert payload["round_development"][0]["round_type"] == "derivation_round"
    assert payload["round_development"][0]["claim_readiness"] == "qualified"
    assert payload["round_development"][0]["missing_blocks"] == []
    assert payload["current_best_statements"]
    assert payload["current_best_statements"][0]["claim_readiness"] == "qualified"
    assert payload["active_routes_not_yet_claim_worthy"] == []
    assert Path(payload["path"]).exists()
    assert Path(payload["note_path"]).exists()


def test_derivation_round_without_stepwise_spine_is_blocked_and_backflows_unfinished_work() -> None:
    service, topic_slug, run_id, runtime_root = _build_service_fixture(
        round_type="derivation_round",
        derivation_rows=[
            {
                "derivation_id": "candidate:demo-bound",
                "title": "Source reconstruction",
                "body": "A summary paragraph without a stepwise derivation spine.",
                "derivation_kind": "source_reconstruction",
                "status": "in_progress",
                "assumptions": ["Weak coupling."],
                "source_refs": ["Lecture Notes A §2 eq.(4)"],
                "provenance_note": "AI provisional reasoning.",
            }
        ],
        comparison_rows=[
            {
                "comparison_id": "comparison:demo",
                "candidate_ref_id": "candidate:demo-bound",
                "title": "Benchmark comparison",
                "comparison_summary": "The route looks plausible but is still under-explained.",
                "compared_unit_ids": ["derivation:demo-l2"],
                "comparison_scope": "bounded benchmark route",
                "outcome": "partial_match",
                "limitations": ["One normalization factor remains unresolved."],
            }
        ],
    )

    payload = service.materialize_research_report(
        topic_slug=topic_slug,
        run_id=run_id,
        updated_by="test",
    )

    round_row = payload["round_development"][0]
    assert round_row["claim_readiness"] == "blocked"
    assert "derivation_spine" in round_row["missing_blocks"]
    assert "derivation_spine" in round_row["hard_blocking_gaps"]
    assert payload["current_best_statements"] == []
    assert payload["active_routes_not_yet_claim_worthy"]

    unfinished_payload = json.loads((runtime_root / "unfinished_work.json").read_text(encoding="utf-8"))
    assert any(
        item.get("missing_block") == "derivation_spine"
        and item.get("blocks_claim_use") is True
        for item in unfinished_payload["items"]
    )


def test_numerical_round_requires_observable_definition_but_not_derivation_spine() -> None:
    service, topic_slug, run_id, runtime_root = _build_service_fixture(
        round_type="numerical_or_benchmark_round",
        derivation_rows=[],
        comparison_rows=[],
        plan_overrides={
            "selected_action_summary": "Run the bounded benchmark comparison.",
            "setup_and_regime": "Weak-coupling benchmark window.",
            "observable_definition": "",
        },
        l4_return_overrides={
            "returned_result_summary": "The benchmark run completed and produced one candidate observable trace."
        },
    )

    payload = service.materialize_research_report(
        topic_slug=topic_slug,
        run_id=run_id,
        updated_by="test",
    )

    round_row = payload["round_development"][0]
    assert round_row["round_type"] == "numerical_or_benchmark_round"
    assert "observable_definition" in round_row["missing_blocks"]
    assert "observable_definition" in round_row["hard_blocking_gaps"]
    assert "derivation_spine" not in round_row["missing_blocks"]

    unfinished_payload = json.loads((runtime_root / "unfinished_work.json").read_text(encoding="utf-8"))
    assert any(
        item.get("missing_block") == "observable_definition"
        and item.get("recommended_round_type") == "numerical_or_benchmark_round"
        for item in unfinished_payload["items"]
    )
