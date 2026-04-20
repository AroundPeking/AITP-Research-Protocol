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


def _dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, dict)]


def _as_text(value: Any) -> str:
    return str(value or "").strip()


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
                "round_type": _as_text(plan.get("round_type")),
                "round_question": _as_text(plan.get("round_question") or plan.get("selected_action_summary") or plan.get("verification_focus")),
                "physical_hypothesis": _as_text(plan.get("physical_hypothesis")),
                "plan_summary": _as_text(plan.get("verification_focus") or plan.get("selected_action_summary")),
                "setup_and_regime": _as_text(
                    plan.get("setup_and_regime")
                    or plan.get("setup_summary")
                    or plan.get("regime")
                    or plan.get("configuration_summary")
                ),
                "observable_definition": _as_text(
                    plan.get("observable_definition")
                    or plan.get("observable")
                    or l4_return.get("observable_definition")
                    or l4_return.get("observable")
                ),
                "pass_conditions": _string_list(plan.get("pass_conditions")),
                "failure_signals": _string_list(plan.get("failure_signals")),
                "checks_performed": _string_list(l4_return.get("checks_performed")),
                "returned_result_summary": _as_text(l4_return.get("returned_result_summary")),
                "anomaly_or_failure_analysis": _as_text(
                    l4_return.get("anomaly_or_failure_analysis")
                    or l4_return.get("failure_analysis")
                    or synthesis.get("failure_analysis")
                ),
                "understanding_delta": _as_text(
                    synthesis.get("understanding_delta") or synthesis.get("synthesis_summary")
                ),
                "next_step_summary": _as_text(synthesis.get("next_step_summary")),
                "conclusion_status": _as_text(synthesis.get("conclusion_status")),
                "staging_decision": _as_text(synthesis.get("staging_decision")),
                "_plan": plan,
                "_l4_return": l4_return,
                "_synthesis": synthesis,
            }
        )
    return rounds


_ROUND_REQUIRED_BLOCKS: dict[str, list[str]] = {
    "derivation_round": [
        "round_question",
        "derivation_spine",
        "assumptions_and_regime",
        "open_obligation_list",
        "next_plan",
    ],
    "source_restoration_round": [
        "round_question",
        "target_source_location",
        "source_anchor_table",
        "source_omissions",
        "l3_restoration",
        "open_obligation_list",
        "next_plan",
    ],
    "numerical_or_benchmark_round": [
        "round_question",
        "test_plan",
        "setup_and_regime",
        "observable_definition",
        "pass_conditions",
        "result_summary",
        "anomaly_or_failure_analysis",
        "next_plan",
    ],
    "synthesis_round": [
        "phase_question",
        "what_was_learned",
        "current_best_statement_candidates",
        "excluded_routes_summary",
        "open_obligation_list",
        "next_plan",
    ],
}

_ROUND_HARD_BLOCKING: dict[str, set[str]] = {
    "derivation_round": {"round_question", "derivation_spine", "source_anchor_table", "convention_ledger"},
    "source_restoration_round": {"round_question", "target_source_location", "source_anchor_table", "source_omissions", "l3_restoration"},
    "numerical_or_benchmark_round": {
        "round_question",
        "test_plan",
        "setup_and_regime",
        "observable_definition",
        "pass_conditions",
        "result_summary",
        "anomaly_or_failure_analysis",
    },
    "synthesis_round": {"phase_question", "what_was_learned", "current_best_statement_candidates", "excluded_routes_summary"},
}


def _default_round_type(round_row: dict[str, Any], derivation_rows: list[dict[str, Any]]) -> str:
    explicit = _as_text(round_row.get("round_type"))
    if explicit:
        return explicit
    if derivation_rows:
        return "derivation_round"
    if round_row.get("observable_definition") or round_row.get("setup_and_regime"):
        return "numerical_or_benchmark_round"
    return "synthesis_round"


def _has_stepwise_derivation(derivation_rows: list[dict[str, Any]]) -> bool:
    for row in derivation_rows:
        audit = row.get("derivation_step_audit") or {}
        if bool(audit.get("has_full_auditable_spine")):
            return True
        steps = _dict_list(row.get("derivation_steps"))
        if steps and all(
            str(step.get("equation") or "").strip()
            and str(step.get("justification") or "").strip()
            and str(step.get("step_origin") or "").strip()
            for step in steps
        ):
            return True
    return False


def _has_source_anchors(derivation_rows: list[dict[str, Any]]) -> bool:
    return any(
        _dict_list(row.get("source_anchor_table")) or _string_list(row.get("source_refs"))
        for row in derivation_rows
    )


def _has_source_anchor_table(derivation_rows: list[dict[str, Any]]) -> bool:
    return any(_dict_list(row.get("source_anchor_table")) for row in derivation_rows)


def _source_anchor_table_rows(derivation_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for derivation_row in derivation_rows:
        derivation_id = _as_text(derivation_row.get("derivation_id"))
        title = _as_text(derivation_row.get("title") or derivation_id)
        for anchor_row in _dict_list(derivation_row.get("source_anchor_table")):
            rows.append(
                {
                    "derivation_id": derivation_id,
                    "title": title,
                    "step_label": _as_text(anchor_row.get("step_label")),
                    "source_anchor": _as_text(anchor_row.get("source_anchor")),
                    "formula_anchor": _as_text(anchor_row.get("formula_anchor")),
                    "step_origin": _as_text(anchor_row.get("step_origin")),
                    "equation_excerpt": _as_text(anchor_row.get("equation_excerpt")),
                    "anchor_notes": _as_text(anchor_row.get("anchor_notes")),
                }
            )
    return rows


def _target_source_location(derivation_rows: list[dict[str, Any]]) -> str:
    for row in derivation_rows:
        target = _as_text(row.get("target_source_location"))
        if target:
            return target
        for anchor_row in _dict_list(row.get("source_anchor_table")):
            formula_anchor = _as_text(anchor_row.get("formula_anchor"))
            if formula_anchor:
                return formula_anchor
            source_anchor = _as_text(anchor_row.get("source_anchor"))
            if source_anchor:
                return source_anchor
    return ""


def _build_convention_ledger(research_contract: dict[str, Any]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for item in _string_list(research_contract.get("formalism_and_notation")):
        rows.append(
            {
                "symbol": "",
                "meaning": item,
                "normalization": "",
                "source": "research_question.contract.json",
                "bridge_status": "declared",
                "notes": "",
            }
        )
    for row in _dict_list((research_contract.get("l1_source_intake") or {}).get("notation_tension_candidates")):
        summary = _as_text(row.get("summary") or row.get("description"))
        if not summary:
            continue
        rows.append(
            {
                "symbol": "",
                "meaning": "Notation tension",
                "normalization": "",
                "source": "l1_source_intake.notation_tension_candidates",
                "bridge_status": "open",
                "notes": summary,
            }
        )
    return rows


def _triggered_blocks_for_round(
    *,
    round_type: str,
    convention_ledger: list[dict[str, str]],
    derivation_rows: list[dict[str, Any]],
    failed_routes: list[dict[str, Any]],
) -> list[str]:
    blocks: list[str] = []
    if round_type in {"derivation_round", "source_restoration_round"} and (
        derivation_rows or _has_source_anchors(derivation_rows)
    ):
        blocks.append("source_anchor_table")
    if convention_ledger:
        blocks.append("convention_ledger")
    if failed_routes and round_type in {"synthesis_round", "derivation_round"}:
        blocks.append("failure_route_note")
    return blocks


def _present_blocks_for_round(
    *,
    round_type: str,
    round_row: dict[str, Any],
    derivation_rows: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    convention_ledger: list[dict[str, str]],
    failed_routes: list[dict[str, Any]],
    research_contract: dict[str, Any],
) -> set[str]:
    present: set[str] = {"open_obligation_list"}
    if round_type == "derivation_round":
        if _as_text(round_row.get("round_question")):
            present.add("round_question")
            present.add("test_plan")
        if _has_stepwise_derivation(derivation_rows):
            present.add("derivation_spine")
        if _string_list(research_contract.get("assumptions")) or any(_string_list(row.get("assumptions")) for row in derivation_rows):
            present.add("assumptions_and_regime")
        if _as_text(round_row.get("next_step_summary")):
            present.add("next_plan")
    elif round_type == "source_restoration_round":
        if _as_text(round_row.get("round_question")):
            present.add("round_question")
        if _target_source_location(derivation_rows):
            present.add("target_source_location")
        if _has_source_anchor_table(derivation_rows):
            present.add("source_anchor_table")
        if any(_as_text(row.get("source_omissions")) for row in derivation_rows):
            present.add("source_omissions")
        if any(
            _as_text(row.get("l3_restoration_notes")) or _dict_list(row.get("derivation_steps"))
            for row in derivation_rows
        ):
            present.add("l3_restoration")
        if _as_text(round_row.get("next_step_summary")):
            present.add("next_plan")
    elif round_type == "numerical_or_benchmark_round":
        if _as_text(round_row.get("round_question")):
            present.add("round_question")
            present.add("test_plan")
        if _as_text(round_row.get("setup_and_regime")):
            present.add("setup_and_regime")
        if _as_text(round_row.get("observable_definition")):
            present.add("observable_definition")
        if _string_list(round_row.get("pass_conditions")):
            present.add("pass_conditions")
        if _as_text(round_row.get("returned_result_summary")):
            present.add("result_summary")
        if _as_text(round_row.get("anomaly_or_failure_analysis")):
            present.add("anomaly_or_failure_analysis")
        if _as_text(round_row.get("next_step_summary")):
            present.add("next_plan")
    else:
        if _as_text(round_row.get("round_question")):
            present.add("phase_question")
        if _as_text(round_row.get("understanding_delta")):
            present.add("what_was_learned")
        if candidate_rows:
            present.add("current_best_statement_candidates")
        if failed_routes:
            present.add("excluded_routes_summary")
        if _as_text(round_row.get("next_step_summary")):
            present.add("next_plan")

    if convention_ledger:
        present.add("convention_ledger")
    if _has_source_anchor_table(derivation_rows):
        present.add("source_anchor_table")
    if failed_routes:
        present.add("failure_route_note")
    return present


def _legacy_status_from_readiness(readiness: str) -> str:
    if readiness == "stable":
        return "current_working_result"
    if readiness == "qualified":
        return "validated_partial"
    return "blocked"


def _round_recommended_type_for_missing_block(round_type: str, missing_block: str) -> str:
    if missing_block in {"derivation_spine", "source_anchor_table", "source_omissions", "l3_restoration"}:
        return "source_restoration_round" if missing_block in {"source_anchor_table", "source_omissions", "l3_restoration"} else "derivation_round"
    if missing_block in {"observable_definition", "setup_and_regime", "anomaly_or_failure_analysis", "pass_conditions", "result_summary"}:
        return "numerical_or_benchmark_round"
    return round_type


def _enrich_rounds(
    *,
    iteration_rounds: list[dict[str, Any]],
    candidate_rows: list[dict[str, Any]],
    derivation_rows: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
    convention_ledger: list[dict[str, str]],
    research_contract: dict[str, Any],
) -> list[dict[str, Any]]:
    failed_routes = [
        row for row in derivation_rows if _as_text(row.get("derivation_kind")) == "failed_attempt"
    ]
    enriched: list[dict[str, Any]] = []
    for round_row in iteration_rounds:
        round_type = _default_round_type(round_row, derivation_rows)
        required_blocks = list(_ROUND_REQUIRED_BLOCKS.get(round_type, []))
        for block in _triggered_blocks_for_round(
            round_type=round_type,
            convention_ledger=convention_ledger,
            derivation_rows=derivation_rows,
            failed_routes=failed_routes,
        ):
            if block not in required_blocks:
                required_blocks.append(block)
        present_blocks = _present_blocks_for_round(
            round_type=round_type,
            round_row=round_row,
            derivation_rows=derivation_rows,
            candidate_rows=candidate_rows,
            convention_ledger=convention_ledger,
            failed_routes=failed_routes,
            research_contract=research_contract,
        )
        missing_blocks = [block for block in required_blocks if block not in present_blocks]
        hard_blocking_gaps = [
            block for block in missing_blocks if block in _ROUND_HARD_BLOCKING.get(round_type, set())
        ]

        qualified_gaps: list[str] = []
        if not hard_blocking_gaps:
            for row in comparison_rows:
                qualified_gaps.extend(_string_list(row.get("limitations")))
            if _as_text(round_row.get("conclusion_status")) == "continue_iteration":
                qualified_gaps.extend(_string_list(research_contract.get("open_ambiguities")))

        claim_readiness = "blocked"
        if not hard_blocking_gaps:
            claim_readiness = "qualified" if qualified_gaps or missing_blocks else "stable"

        enriched.append(
            {
                **{k: v for k, v in round_row.items() if not k.startswith("_")},
                "round_type": round_type,
                "required_blocks": required_blocks,
                "present_blocks": sorted(present_blocks),
                "missing_blocks": missing_blocks,
                "hard_blocking_gaps": hard_blocking_gaps,
                "qualified_gaps": qualified_gaps,
                "claim_readiness": claim_readiness,
                "eligible_for_current_claims": claim_readiness in {"qualified", "stable"},
                "must_feed_unfinished_work": bool(missing_blocks),
            }
        )
    return enriched


def _merge_unfinished_items(
    unfinished_work: dict[str, Any],
    *,
    round_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    items = _dict_list(unfinished_work.get("items"))
    seen = {
        (
            _as_text(item.get("source_round_id")),
            _as_text(item.get("missing_block")),
        )
        for item in items
    }
    for round_row in round_rows:
        if not round_row.get("must_feed_unfinished_work"):
            continue
        round_id = _as_text(round_row.get("iteration_id"))
        round_type = _as_text(round_row.get("round_type"))
        hard_blocks = set(_string_list(round_row.get("hard_blocking_gaps")))
        for missing_block in _string_list(round_row.get("missing_blocks")):
            key = (round_id, missing_block)
            if key in seen:
                continue
            seen.add(key)
            items.append(
                {
                    "summary": f"Repair notebook obligation '{missing_block}' for {round_id}.",
                    "status": "pending",
                    "source_round_id": round_id,
                    "missing_block": missing_block,
                    "blocks_claim_use": missing_block in hard_blocks,
                    "recommended_round_type": _round_recommended_type_for_missing_block(round_type, missing_block),
                }
            )
    unfinished_work["items"] = items
    return unfinished_work


def _build_statement_rows(
    *,
    candidate_rows: list[dict[str, Any]],
    comparison_rows: list[dict[str, Any]],
    round_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    if any(row.get("claim_readiness") == "blocked" for row in round_rows):
        overall_readiness = "blocked"
    elif any(row.get("claim_readiness") == "qualified" for row in round_rows):
        overall_readiness = "qualified"
    else:
        overall_readiness = "stable"

    current_best_statements: list[dict[str, Any]] = []
    active_routes_not_yet_claim_worthy: list[dict[str, Any]] = []
    legacy_current_claims: list[dict[str, Any]] = []

    latest_next_step = _as_text(round_rows[-1].get("next_step_summary")) if round_rows else ""
    for row in candidate_rows:
        candidate_id = _as_text(row.get("candidate_id"))
        limitations: list[str] = []
        for comparison_row in comparison_rows:
            if _as_text(comparison_row.get("candidate_ref_id")) == candidate_id:
                limitations.extend(_string_list(comparison_row.get("limitations")))
        for round_row in round_rows:
            if round_row.get("claim_readiness") == "blocked":
                for block in _string_list(round_row.get("hard_blocking_gaps")):
                    limitations.append(f"Missing obligation block: {block}")

        statement_row = {
            "candidate_id": candidate_id,
            "statement": _as_text(row.get("summary") or row.get("title") or candidate_id or "candidate"),
            "validity_regime": "; ".join(_string_list(row.get("assumptions"))) or "regime not yet stated",
            "depends_on": [
                entry
                for entry in [
                    "L3 derivation" if overall_readiness != "blocked" or True else "",
                    "L2 comparison receipt" if comparison_rows else "",
                    *[f"round:{_as_text(round_row.get('iteration_id'))}" for round_row in round_rows],
                ]
                if entry
            ],
            "breaks_if": limitations[0] if limitations else "No explicit failure trigger recorded.",
            "still_unclosed": limitations,
            "claim_readiness": overall_readiness,
            "next_action": latest_next_step or "Continue the bounded research loop.",
        }
        legacy_current_claims.append(
            {
                "candidate_id": candidate_id,
                "claim": statement_row["statement"],
                "status": _legacy_status_from_readiness(overall_readiness),
                "support": ", ".join(statement_row["depends_on"]) or "candidate only",
                "limitation": "; ".join(statement_row["still_unclosed"]) or "none declared",
                "next_action": statement_row["next_action"],
            }
        )
        if overall_readiness == "blocked":
            active_routes_not_yet_claim_worthy.append(statement_row)
        else:
            current_best_statements.append(statement_row)

    return current_best_statements, active_routes_not_yet_claim_worthy, legacy_current_claims


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
        "## Physical Target",
        "",
        str(payload.get("physical_target") or "(missing)"),
        "",
        "## Physical Motivation",
        "",
        str(payload.get("physical_motivation") or "(missing)"),
        "",
        "## Convention Ledger",
        "",
    ]
    for row in payload.get("convention_ledger") or []:
        lines.append(
            f"- {row.get('meaning') or '(missing)'}"
            f" [status: {row.get('bridge_status') or 'unknown'}]"
        )
        if row.get("notes"):
            lines.append(f"  - {row['notes']}")
    if not (payload.get("convention_ledger") or []):
        lines.append("- (none)")
    lines.extend(
        [
            "",
        "## Setup",
        "",
        ]
    )
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

    lines.extend(["## Source Anchor Table", ""])
    if payload.get("target_source_location"):
        lines.append(f"- Target source location: {payload.get('target_source_location')}")
    for row in payload.get("source_anchor_table") or []:
        lines.append(
            "- "
            + " | ".join(
                [
                    f"derivation={row.get('title') or row.get('derivation_id') or '(missing)'}",
                    f"step={row.get('step_label') or '(missing)'}",
                    f"source={row.get('source_anchor') or '(none)'}",
                    f"formula={row.get('formula_anchor') or '(none)'}",
                    f"origin={row.get('step_origin') or '(none)'}",
                ]
            )
        )
    if not (payload.get("source_anchor_table") or []):
        lines.append("- (none)")
    lines.append("")

    lines.extend(["## Current Best Statements", ""])
    for row in payload.get("current_best_statements") or []:
        lines.append(f"### {row.get('statement') or '(missing)'}")
        lines.append("")
        lines.append(f"- Claim readiness: `{row.get('claim_readiness') or '(missing)'}`")
        lines.append(f"- Validity regime: {row.get('validity_regime') or '(missing)'}")
        lines.append(f"- Depends on: {', '.join(row.get('depends_on') or []) or '(missing)'}")
        lines.append(f"- Breaks if: {row.get('breaks_if') or '(missing)'}")
        lines.append(f"- Still unclosed: {'; '.join(row.get('still_unclosed') or []) or '(none)'}")
        lines.append(f"- Next action: {row.get('next_action') or '(missing)'}")
        lines.append("")
    if not (payload.get("current_best_statements") or []):
        lines.append("- (none)")
        lines.append("")

    lines.extend(["## Active But Not Yet Claim-Worthy Routes", ""])
    for row in payload.get("active_routes_not_yet_claim_worthy") or []:
        lines.append(f"- {row.get('statement') or '(missing)'}")
        lines.append(f"  - blocked by: {'; '.join(row.get('still_unclosed') or []) or '(missing)'}")
    if not (payload.get("active_routes_not_yet_claim_worthy") or []):
        lines.append("- (none)")
    lines.append("")

    lines.extend(["## Open Obligations", ""])
    for row in payload.get("open_obligations") or []:
        lines.append(f"- {row.get('summary') or '(missing)'}")
        lines.append(f"  - missing block: {row.get('missing_block') or '(missing)'}")
        lines.append(f"  - recommended round type: {row.get('recommended_round_type') or '(missing)'}")
    if not (payload.get("open_obligations") or []):
        lines.append("- (none)")
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
    convention_ledger = _build_convention_ledger(research_contract)
    round_development = _enrich_rounds(
        candidate_rows=candidate_rows,
        derivation_rows=derivation_rows,
        comparison_rows=comparison_rows,
        iteration_rounds=iteration_rounds,
        convention_ledger=convention_ledger,
        research_contract=research_contract,
    )
    unfinished_work = _merge_unfinished_items(unfinished_work, round_rows=round_development)
    source_anchor_table = _source_anchor_table_rows(derivation_rows)
    target_source_location = _target_source_location(derivation_rows)

    source_titles = [
        _as_text(row.get("source_title") or row.get("source_id"))
        for row in ((research_contract.get("l1_source_intake") or {}).get("reading_depth_rows") or [])
        if _as_text(row.get("source_title") or row.get("source_id"))
    ]
    literature_position = (
        "Primary source basis: " + ", ".join(source_titles)
        if source_titles
        else "Primary source basis has not been summarized yet."
    )
    current_best_statements, active_routes_not_yet_claim_worthy, legacy_current_claims = _build_statement_rows(
        candidate_rows=candidate_rows,
        comparison_rows=comparison_rows,
        round_rows=round_development,
    )

    unfinished_items = _dict_list(unfinished_work.get("items"))
    open_problems = [
        _as_text(item.get("summary") or item.get("title") or item.get("question"))
        for item in unfinished_items
        if _as_text(item.get("summary") or item.get("title") or item.get("question"))
    ] or _string_list(research_contract.get("open_ambiguities"))
    current_dispute_or_bottleneck = ""
    if _string_list(research_contract.get("open_ambiguities")):
        current_dispute_or_bottleneck = _string_list(research_contract.get("open_ambiguities"))[0]
    elif convention_ledger:
        current_dispute_or_bottleneck = _as_text(convention_ledger[0].get("notes") or convention_ledger[0].get("meaning"))

    payload = {
        "status": "available",
        "topic_slug": topic_slug,
        "run_id": resolved_run_id,
        "updated_at": _now_iso(),
        "updated_by": updated_by,
        "problem": {
            "question": _as_text(research_contract.get("question") or research_contract.get("title")),
            "literature_position": literature_position,
        },
        "physical_target": _as_text(
            (research_contract.get("target_claims") or [None])[0]
            or (research_contract.get("observables") or [None])[0]
            or research_contract.get("question")
        ),
        "observables_or_decision_targets": _string_list(
            research_contract.get("observables") or research_contract.get("target_claims")
        ),
        "core_equations_or_targets": _string_list(
            research_contract.get("core_equations") or research_contract.get("deliverables")
        ),
        "current_dispute_or_bottleneck": current_dispute_or_bottleneck,
        "physical_motivation": _as_text(
            idea_packet.get("novelty_target") or idea_packet.get("initial_idea")
        ),
        "setup": {
            "scope": _string_list(research_contract.get("scope")),
            "assumptions": _string_list(research_contract.get("assumptions")),
            "notation": _string_list(research_contract.get("formalism_and_notation")),
            "deliverables": _string_list(research_contract.get("deliverables")),
        },
        "convention_ledger": convention_ledger,
        "target_source_location": target_source_location,
        "source_anchor_table": source_anchor_table,
        "candidate_routes": [
            {
                "candidate_id": _as_text(row.get("candidate_id")),
                "title": _as_text(row.get("title") or row.get("candidate_id")),
                "summary": _as_text(row.get("summary")),
                "question": _as_text(row.get("question")),
                "status": _as_text(row.get("status")),
                "validation_route": _as_text(row.get("proposed_validation_route")),
                "assumptions": _string_list(row.get("assumptions")),
            }
            for row in candidate_rows
        ],
        "round_development": round_development,
        "iteration_rounds": round_development,
        "main_derivation_spine": [
            row for row in derivation_rows if _as_text(row.get("derivation_kind")) != "failed_attempt"
        ],
        "current_best_statements": current_best_statements,
        "active_routes_not_yet_claim_worthy": active_routes_not_yet_claim_worthy,
        "current_claims": legacy_current_claims,
        "current_derivation_spine": [
            row for row in derivation_rows if _as_text(row.get("derivation_kind")) != "failed_attempt"
        ],
        "failed_routes": [
            row for row in derivation_rows if _as_text(row.get("derivation_kind")) == "failed_attempt"
        ],
        "excluded_routes": [
            row for row in derivation_rows if _as_text(row.get("derivation_kind")) == "failed_attempt"
        ],
        "comparison_receipts": comparison_rows,
        "current_conclusion": _as_text(
            (round_development[-1].get("understanding_delta") if round_development else "")
        ),
        "open_obligations": unfinished_items,
        "open_problems": open_problems,
        "recommended_skills": _recommended_skill_rows(service),
    }

    paths = research_report_paths(service, topic_slug=topic_slug)
    _write_json(runtime_root / "unfinished_work.json", unfinished_work)
    _write_json(paths["json"], payload)
    _write_text(paths["note"], _build_markdown(payload))
    return {
        **payload,
        "path": str(paths["json"]),
        "note_path": str(paths["note"]),
    }

