from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _read_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def research_report_paths(service: Any, *, topic_slug: str) -> dict[str, Path]:
    runtime_root = service._runtime_root(topic_slug)
    return {
        "json": runtime_root / "research_report.active.json",
        "note": runtime_root / "research_report.active.md",
    }


def _recommended_skill_rows(service: Any) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for skill_name, purpose in (
        ("aitp-problem-framing", "Frame the topic as a real physics problem with motivation and bounded scope."),
        ("aitp-derivation-discipline", "Write derivations as explicit theoretical-physics arguments with checks and caveats."),
        ("aitp-l3-l4-round", "Record each bounded L3-L4 research round as a scientific cycle."),
        ("aitp-current-claims-auditor", "State what the topic currently believes, what is partial, and what remains blocked."),
        ("aitp-topic-report-author", "Assemble the topic into a physicist-readable report with main text and appendices."),
    ):
        rows.append(
            {
                "skill_name": skill_name,
                "path": service._relativize(service.repo_root / "skills" / skill_name / "SKILL.md"),
                "purpose": purpose,
            }
        )
    return rows


def _collect_iteration_rounds(service: Any, *, topic_slug: str, run_id: str | None) -> list[dict[str, Any]]:
    if not run_id:
        return []
    iterations_root = service._feedback_run_root(topic_slug, run_id) / "iterations"
    if not iterations_root.exists():
        return []
    rounds: list[dict[str, Any]] = []
    for iteration_root in sorted(path for path in iterations_root.iterdir() if path.is_dir()):
        plan = _read_json(iteration_root / "plan.contract.json") or {}
        l4_return = _read_json(iteration_root / "l4_return.json") or {}
        synthesis = _read_json(iteration_root / "l3_synthesis.json") or {}
        rounds.append(
            {
                "iteration_id": iteration_root.name,
                "round_question": str(plan.get("round_question") or plan.get("selected_action_summary") or plan.get("verification_focus") or "").strip(),
                "physical_hypothesis": str(plan.get("physical_hypothesis") or "").strip(),
                "plan_summary": str(plan.get("verification_focus") or plan.get("selected_action_summary") or "").strip(),
                "pass_conditions": _string_list(plan.get("pass_conditions")),
                "failure_signals": _string_list(plan.get("failure_signals")),
                "checks_performed": _string_list(l4_return.get("checks_performed")),
                "returned_result_summary": str(l4_return.get("returned_result_summary") or "").strip(),
                "understanding_delta": str(synthesis.get("understanding_delta") or synthesis.get("synthesis_summary") or "").strip(),
                "next_step_summary": str(synthesis.get("next_step_summary") or "").strip(),
                "conclusion_status": str(synthesis.get("conclusion_status") or "").strip(),
                "staging_decision": str(synthesis.get("staging_decision") or "").strip(),
            }
        )
    return rounds


def _derive_claim_status(candidate_row: dict[str, Any], comparison_row: dict[str, Any] | None, derivation_row: dict[str, Any] | None) -> str:
    if list(candidate_row.get("promotion_blockers") or []):
        return "blocked"
    if derivation_row is None:
        return "candidate_under_test"
    if comparison_row is None:
        return "candidate_under_test"
    outcome = str(comparison_row.get("outcome") or "").strip().lower()
    limitations = _string_list(comparison_row.get("limitations"))
    if outcome in {"partial_match", "mixed", "qualified_match"} or limitations:
        return "validated_partial"
    if outcome in {"match", "confirmed", "accepted"}:
        return "current_working_result"
    if outcome in {"blocked", "rejected", "failed"}:
        return "blocked"
    return "candidate_under_test"


def _build_current_claims(
    service: Any,
    *,
    candidate_rows: list[dict[str, Any]],
    derivation_rows: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
    iteration_rounds: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    latest_next_step = str((iteration_rounds[-1].get("next_step_summary") if iteration_rounds else "") or "").strip()
    claims: list[dict[str, Any]] = []
    for row in candidate_rows:
        candidate_id = str(row.get("candidate_id") or "").strip()
        derivation_row = next(
            (
                item
                for item in derivation_rows
                if str(item.get("derivation_id") or item.get("candidate_ref_id") or "").strip() == candidate_id
                or str(item.get("title") or "").strip() == str(row.get("title") or "").strip()
            ),
            None,
        )
        comparison_row = next(
            (
                item
                for item in comparison_rows
                if str(item.get("candidate_ref_id") or "").strip() == candidate_id
            ),
            None,
        )
        limitation = ""
        if comparison_row is not None:
            limitation = "; ".join(_string_list(comparison_row.get("limitations")))
        if not limitation and list(row.get("promotion_blockers") or []):
            limitation = "; ".join(str(item).strip() for item in row.get("promotion_blockers") or [] if str(item).strip())
        support_bits = []
        if derivation_row is not None:
            support_bits.append("L3 derivation")
        if comparison_row is not None:
            support_bits.append("L2 comparison receipt")
        if row.get("supporting_regression_question_ids"):
            support_bits.append("regression question")
        if row.get("supporting_oracle_ids"):
            support_bits.append("oracle")
        claims.append(
            {
                "candidate_id": candidate_id,
                "claim": str(row.get("summary") or row.get("title") or candidate_id or "candidate").strip(),
                "status": _derive_claim_status(row, comparison_row, derivation_row),
                "support": ", ".join(support_bits) or "candidate only",
                "limitation": limitation or "none declared",
                "next_action": latest_next_step or "Continue the bounded research loop.",
            }
        )
    return claims


def _build_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Research Report",
        "",
        f"- Topic slug: `{payload.get('topic_slug') or '(missing)'}`",
        f"- Run id: `{payload.get('run_id') or '(missing)'}`",
        f"- Updated at: `{payload.get('updated_at') or '(missing)'}`",
        "",
        "## Problem",
        "",
        str((payload.get("problem") or {}).get("question") or "(missing)"),
        "",
        "## Physical Motivation",
        "",
        str(payload.get("physical_motivation") or "(missing)"),
        "",
        "## Setup",
        "",
    ]
    setup = payload.get("setup") or {}
    for header, key in (
        ("Scope", "scope"),
        ("Assumptions", "assumptions"),
        ("Notation", "notation"),
    ):
        lines.extend([f"### {header}", ""])
        values = setup.get(key) or []
        if values:
            for item in values:
                lines.append(f"- {item}")
        else:
            lines.append("- (none)")
        lines.append("")

    lines.extend(["## Current Claims", ""])
    for row in payload.get("current_claims") or []:
        lines.append(f"### {row.get('claim') or '(missing)'}")
        lines.append("")
        lines.append(f"- Status: `{row.get('status') or '(missing)'}`")
        lines.append(f"- Support: {row.get('support') or '(missing)'}")
        lines.append(f"- Limitation: {row.get('limitation') or '(missing)'}")
        lines.append(f"- Next action: {row.get('next_action') or '(missing)'}")
        lines.append("")

    lines.extend(["## Recommended Skills", ""])
    for row in payload.get("recommended_skills") or []:
        lines.append(f"- `{row.get('skill_name') or '(missing)'}` — `{row.get('path') or '(missing)'}`")
        lines.append(f"  - {row.get('purpose') or '(missing)'}")
    if not (payload.get("recommended_skills") or []):
        lines.append("- (none)")
    lines.append("")
    return "\n".join(lines)


def materialize_research_report(
    service: Any,
    *,
    topic_slug: str,
    run_id: str | None,
    updated_by: str,
) -> dict[str, Any]:
    resolved_run_id = str(run_id or service._resolve_run_id(topic_slug, run_id) or "").strip()
    runtime_root = service._runtime_root(topic_slug)
    research_contract = _read_json(runtime_root / "research_question.contract.json") or {}
    idea_packet = _read_json(runtime_root / "idea_packet.json") or {}
    unfinished_work = _read_json(runtime_root / "unfinished_work.json") or {}
    candidate_rows = service._candidate_rows_for_run(topic_slug, resolved_run_id)
    derivation_rows = service._load_derivation_rows(topic_slug, resolved_run_id) if resolved_run_id else []
    comparison_rows = service._load_l2_comparison_rows(topic_slug, resolved_run_id) if resolved_run_id else []
    iteration_rounds = _collect_iteration_rounds(service, topic_slug=topic_slug, run_id=resolved_run_id or None)
    current_claims = _build_current_claims(
        service,
        candidate_rows=candidate_rows,
        derivation_rows=derivation_rows,
        comparison_rows=comparison_rows,
        iteration_rounds=iteration_rounds,
    )

    source_titles = [
        str(row.get("source_title") or row.get("source_id") or "").strip()
        for row in ((research_contract.get("l1_source_intake") or {}).get("reading_depth_rows") or [])
        if str(row.get("source_title") or row.get("source_id") or "").strip()
    ]
    literature_position = (
        "Primary source basis: " + ", ".join(source_titles)
        if source_titles
        else "Primary source basis has not been summarized yet."
    )
    open_problems = [
        str(item.get("summary") or item.get("title") or item.get("question") or "").strip()
        for item in (unfinished_work.get("items") or [])
        if str(item.get("summary") or item.get("title") or item.get("question") or "").strip()
    ]
    if not open_problems:
        open_problems = _string_list(research_contract.get("open_ambiguities"))

    payload = {
        "status": "available",
        "topic_slug": topic_slug,
        "run_id": resolved_run_id,
        "updated_at": _now_iso(),
        "updated_by": updated_by,
        "problem": {
            "question": str(research_contract.get("question") or research_contract.get("title") or "").strip(),
            "literature_position": literature_position,
        },
        "physical_motivation": str(idea_packet.get("novelty_target") or idea_packet.get("initial_idea") or "").strip(),
        "setup": {
            "scope": _string_list(research_contract.get("scope")),
            "assumptions": _string_list(research_contract.get("assumptions")),
            "notation": _string_list(research_contract.get("formalism_and_notation")),
            "deliverables": _string_list(research_contract.get("deliverables")),
        },
        "candidate_routes": [
            {
                "candidate_id": str(row.get("candidate_id") or "").strip(),
                "title": str(row.get("title") or row.get("candidate_id") or "").strip(),
                "summary": str(row.get("summary") or "").strip(),
                "question": str(row.get("question") or "").strip(),
                "status": str(row.get("status") or "").strip(),
                "validation_route": str(row.get("proposed_validation_route") or "").strip(),
                "assumptions": _string_list(row.get("assumptions")),
            }
            for row in candidate_rows
        ],
        "iteration_rounds": iteration_rounds,
        "current_claims": current_claims,
        "current_derivation_spine": [
            row for row in derivation_rows if str(row.get("derivation_kind") or "").strip() != "failed_attempt"
        ],
        "failed_routes": [
            row for row in derivation_rows if str(row.get("derivation_kind") or "").strip() == "failed_attempt"
        ],
        "comparison_receipts": comparison_rows,
        "current_conclusion": str((iteration_rounds[-1].get("understanding_delta") if iteration_rounds else "") or "").strip(),
        "open_problems": open_problems,
        "recommended_skills": _recommended_skill_rows(service),
    }

    paths = research_report_paths(service, topic_slug=topic_slug)
    _write_json(paths["json"], payload)
    _write_text(paths["note"], _build_markdown(payload))
    return {
        **payload,
        "path": str(paths["json"]),
        "note_path": str(paths["note"]),
    }

