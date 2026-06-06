"""Host-agnostic policy for research moments in a process graph slice."""

from __future__ import annotations

from typing import Any


_ACTIVE_STATUSES = {"open", "active"}


def build_host_agnostic_moment_policy(
    *,
    session_id: str,
    topic_id: str,
    claim_id: str,
    open_obligations: list[dict[str, Any]],
    source_backtrace: list[dict[str, Any]],
    relation_neighborhood: list[dict[str, Any]],
    exploratory_records: list[dict[str, Any]],
    trust_boundary_reasons: list[str],
) -> dict[str, Any]:
    """Return read-only policy decisions for recording, exploration, and trust boundaries."""

    decisions: list[dict[str, Any]] = []
    decisions.extend(_recording_decisions(open_obligations))
    decisions.extend(_source_backtrace_decisions(source_backtrace))
    decisions.extend(_relation_brainstorm_decisions(relation_neighborhood))
    decisions.extend(_exploratory_decisions(exploratory_records))
    decisions.extend(_trust_boundary_decisions(source_backtrace, decisions))
    decisions = _dedupe_decisions(decisions)

    return {
        "ok": True,
        "kind": "host_agnostic_moment_policy",
        "session_id": session_id,
        "topic_id": topic_id,
        "claim_id": claim_id,
        "policy_axes": ["recording", "brainstorming", "backtrace", "trust_boundary"],
        "decisions": decisions,
        "recommended_moments": [_moment_summary(item) for item in decisions],
        "trust_boundary_reasons": list(trust_boundary_reasons),
        "adapter_rule": "hosts may read this policy for orientation, then call typed kernel entrypoints before trust changes",
        "derived_from": "process_graph_slice",
        "truth_source": "typed_records",
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _recording_decisions(open_obligations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        _decision(
            moment="record_or_validate_open_obligation",
            decision_type="recording",
            action_kind="record_evidence_or_validation",
            required_now=True,
            reason="open proof obligation requires typed evidence or validation",
            target_type="proof_obligation",
            target_id=str(obligation["obligation_id"]),
            topic_id=str(obligation.get("topic_id") or ""),
            claim_id=str(obligation.get("claim_id") or ""),
            target_record=obligation,
            record_entrypoints=["aitp_v5_record_evidence", "aitp_v5_record_validation_result"],
            required_before_trust_change=[
                "record typed evidence or validation for the open obligation",
                "run aitp_v5_preflight_trust_update",
            ],
        )
        for obligation in open_obligations
    ]


def _source_backtrace_decisions(source_backtrace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    decisions = []
    for item in source_backtrace:
        missing = list(item.get("missing_components") or [])
        if not missing:
            continue
        decisions.append(
            _decision(
                moment="backtrace_source_reconstruction",
                decision_type="backtrace",
                action_kind="reconstruct_missing_source_components",
                required_now=True,
                reason="missing source reconstruction components",
                target_type="claim",
                target_id=str(item.get("claim_id") or ""),
                topic_id=str(item.get("topic_id") or ""),
                claim_id=str(item.get("claim_id") or ""),
                target_record=item,
                missing_components=missing,
                record_entrypoints=[
                    "aitp_v5_record_exploratory_record",
                    "aitp_v5_record_reference_location",
                    "aitp_v5_register_source_asset",
                ],
                exploration_entrypoints=["aitp_v5_record_exploratory_record"],
                required_before_trust_change=[
                    "backtrace missing source components to typed records",
                    "record evidence only after source and provenance are explicit",
                    "run aitp_v5_preflight_trust_update",
                ],
            )
        )
    return decisions


def _relation_brainstorm_decisions(relations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    decisions = []
    for relation in relations:
        if str(relation.get("status") or "").strip().lower() != "hypothesis":
            continue
        decisions.append(
            _decision(
                moment="brainstorm_relation_path",
                decision_type="brainstorming",
                action_kind="brainstorm_relation_path_before_validation",
                required_now=False,
                reason="object relation is still a hypothesis",
                target_type="object_relation",
                target_id=str(relation.get("relation_id") or ""),
                topic_id=str(relation.get("topic_id") or ""),
                claim_id=str(relation.get("claim_id") or ""),
                target_record=relation,
                exploration_entrypoints=["aitp_v5_record_exploratory_record"],
                required_before_trust_change=[
                    "convert relation-path brainstorm into typed evidence or validation",
                    "run aitp_v5_preflight_trust_update",
                ],
            )
        )
    return decisions


def _exploratory_decisions(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    decisions = []
    for record in records:
        status = str(record.get("status") or "")
        if status not in _ACTIVE_STATUSES:
            continue
        record_id = str(record.get("record_id") or "")
        exploration_type = str(record.get("exploration_type") or "")
        if exploration_type == "question_decomposition":
            decisions.append(
                _decision(
                    moment="direction.brainstorm",
                    decision_type="brainstorming",
                    action_kind="steer_next_local_analysis",
                    required_now=False,
                    reason="open question decomposition should steer the next local analysis",
                    target_type="exploratory_record",
                    target_id=record_id,
                    topic_id=str(record.get("topic_id") or ""),
                    claim_id=str(record.get("claim_id") or ""),
                    session_id=str(record.get("session_id") or ""),
                    target_record=record,
                    exploration_entrypoints=["aitp_v5_record_exploratory_record"],
                )
            )
        if exploration_type == "relation_path_brainstorm":
            decisions.append(
                _decision(
                    moment="brainstorm_relation_path",
                    decision_type="brainstorming",
                    action_kind="continue_relation_path_brainstorm",
                    required_now=False,
                    reason="relation path brainstorming is open",
                    target_type="exploratory_record",
                    target_id=record_id,
                    topic_id=str(record.get("topic_id") or ""),
                    claim_id=str(record.get("claim_id") or ""),
                    session_id=str(record.get("session_id") or ""),
                    target_record=record,
                    exploration_entrypoints=["aitp_v5_record_exploratory_record"],
                )
            )
        if exploration_type in {"source_asset", "backtrace_step"}:
            decisions.append(
                _decision(
                    moment="backtrace_source_reconstruction",
                    decision_type="backtrace",
                    action_kind="continue_source_or_backtrace_record",
                    required_now=False,
                    reason="exploratory source/backtrace record is still open",
                    target_type="exploratory_record",
                    target_id=record_id,
                    topic_id=str(record.get("topic_id") or ""),
                    claim_id=str(record.get("claim_id") or ""),
                    session_id=str(record.get("session_id") or ""),
                    target_record=record,
                    exploration_entrypoints=["aitp_v5_record_exploratory_record"],
                )
            )
        if record.get("original_question") and record.get("local_question"):
            decisions.append(
                _decision(
                    moment="audit_original_question_drift",
                    decision_type="brainstorming",
                    action_kind="check_local_question_against_original",
                    required_now=False,
                    reason="exploratory local question must stay tied to the original question",
                    target_type="exploratory_record",
                    target_id=record_id,
                    topic_id=str(record.get("topic_id") or ""),
                    claim_id=str(record.get("claim_id") or ""),
                    session_id=str(record.get("session_id") or ""),
                    target_record=record,
                    exploration_entrypoints=["aitp_v5_record_exploratory_record"],
                )
            )
    return decisions


def _trust_boundary_decisions(source_backtrace: list[dict[str, Any]], decisions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    claim_ids = {str(item.get("claim_id") or "") for item in source_backtrace if item.get("claim_id")}
    risky_targets = [item for item in decisions if item["required_before_trust_change"]]
    if not risky_targets:
        return []
    if not claim_ids:
        claim_ids = {
            str(item["target_id"])
            for item in risky_targets
            if item["target_type"] == "claim" and item.get("target_id")
        }
    return [
        _decision(
            moment="trust_boundary_before_claim_update",
            decision_type="trust_boundary",
            action_kind="block_trust_change_until_policy_prerequisites_are_met",
            required_now=True,
            reason="recording, brainstorming, or backtrace prerequisites exist before any claim-trust update",
            target_type="claim",
            target_id=claim_id,
            claim_id=claim_id,
            required_before_trust_change=[
                "resolve required recording/backtrace/brainstorm policy decisions",
                "run aitp_v5_preflight_trust_update",
            ],
        )
        for claim_id in sorted(claim_ids)
    ]


def _decision(
    *,
    moment: str,
    decision_type: str,
    action_kind: str,
    required_now: bool,
    reason: str,
    target_type: str,
    target_id: str,
    topic_id: str = "",
    claim_id: str = "",
    session_id: str = "",
    target_record: dict[str, Any] | None = None,
    record_entrypoints: list[str] | None = None,
    exploration_entrypoints: list[str] | None = None,
    required_before_trust_change: list[str] | None = None,
    missing_components: list[str] | None = None,
) -> dict[str, Any]:
    record_points = record_entrypoints or []
    exploration_points = exploration_entrypoints or []
    trust_prerequisites = required_before_trust_change or []
    return {
        "moment": moment,
        "decision_type": decision_type,
        "action_kind": action_kind,
        "required_now": required_now,
        "reason": reason,
        "target_type": target_type,
        "target_id": target_id,
        "missing_components": missing_components or [],
        "record_entrypoints": record_points,
        "exploration_entrypoints": exploration_points,
        "entrypoints": _entrypoints(record_points, exploration_points, trust_prerequisites),
        "payload_hints": _payload_hints(
            action_kind=action_kind,
            target_type=target_type,
            target_id=target_id,
            topic_id=topic_id,
            claim_id=claim_id,
            session_id=session_id,
            target_record=target_record or {},
            record_entrypoints=record_points,
            exploration_entrypoints=exploration_points,
        ),
        "required_before_trust_change": trust_prerequisites,
        "trust_boundary": bool(trust_prerequisites),
        "summary_inputs_trusted": False,
        "orientation_only": True,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }


def _moment_summary(decision: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "moment": decision["moment"],
        "reason": decision["reason"],
        "target_type": decision["target_type"],
        "target_id": decision["target_id"],
        "decision_type": decision["decision_type"],
        "required_now": decision["required_now"],
        "trust_boundary": decision["trust_boundary"],
    }
    if decision["missing_components"]:
        summary["missing_components"] = list(decision["missing_components"])
    return summary


def _dedupe_decisions(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen = set()
    result = []
    for item in items:
        key = (item["moment"], item["decision_type"], item["target_type"], item["target_id"])
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


def _payload_hints(
    *,
    action_kind: str,
    target_type: str,
    target_id: str,
    topic_id: str,
    claim_id: str,
    session_id: str,
    target_record: dict[str, Any],
    record_entrypoints: list[str],
    exploration_entrypoints: list[str],
) -> list[dict[str, Any]]:
    hints: list[dict[str, Any]] = []
    for entrypoint in [*record_entrypoints, *exploration_entrypoints]:
        hint = _payload_hint(
            entrypoint=entrypoint,
            action_kind=action_kind,
            target_type=target_type,
            target_id=target_id,
            topic_id=topic_id,
            claim_id=claim_id,
            session_id=session_id,
            target_record=target_record,
        )
        if hint is not None:
            hints.append(hint)
    return hints


def _payload_hint(
    *,
    entrypoint: str,
    action_kind: str,
    target_type: str,
    target_id: str,
    topic_id: str,
    claim_id: str,
    session_id: str,
    target_record: dict[str, Any],
) -> dict[str, Any] | None:
    base = {
        "entrypoint": entrypoint,
        "action_kind": action_kind,
        "target_type": target_type,
        "target_id": target_id,
        "orientation_only": True,
        "summary_inputs_trusted": False,
        "can_update_claim_trust": False,
    }
    if entrypoint == "aitp_v5_record_evidence":
        return {
            **base,
            "record_action": "record_evidence",
            "required_fields": ["topic_id", "claim_id", "evidence_type", "status", "summary"],
            "draft": _clean_mapping(
                {
                    "topic_id": topic_id,
                    "claim_id": claim_id,
                    "evidence_type": _evidence_type_for_target(target_type, action_kind),
                    "status": "supports",
                    "summary": _placeholder("source-grounded evidence summary"),
                    "supports_outputs": _supports_outputs(target_record),
                    "source_refs": _source_refs(target_record),
                }
            ),
        }
    if entrypoint == "aitp_v5_record_reference_location":
        return {
            **base,
            "record_action": "record_reference_location",
            "required_fields": ["topic_id", "connector_id", "location_type", "uri", "label"],
            "draft": _clean_mapping(
                {
                    "topic_id": topic_id,
                    "claim_id": claim_id,
                    "connector_id": _placeholder("connector id"),
                    "location_type": "paper_section",
                    "uri": _placeholder("source URI"),
                    "label": _placeholder("source label"),
                    "status": "located",
                    "summary": _placeholder("orientation-only source pointer summary"),
                }
            ),
        }
    if entrypoint == "aitp_v5_register_source_asset":
        return {
            **base,
            "record_action": "register_source_asset",
            "required_fields": ["topic_id", "asset_type", "uri", "title"],
            "draft": _clean_mapping(
                {
                    "topic_id": topic_id,
                    "claim_id": claim_id,
                    "asset_type": "paper",
                    "uri": _placeholder("source URI"),
                    "title": _placeholder("source title"),
                    "source_kind": "literature",
                }
            ),
        }
    if entrypoint == "aitp_v5_record_exploratory_record":
        return {
            **base,
            "record_action": "record_exploratory_record",
            "required_fields": ["topic_id", "exploration_type", "title", "focal_question", "summary"],
            "draft": _clean_mapping(
                {
                    "topic_id": topic_id,
                    "claim_id": claim_id,
                    "session_id": session_id,
                    "exploration_type": _exploration_type_for_action(action_kind),
                    "title": _exploration_title(action_kind),
                    "focal_question": _placeholder("local question to record"),
                    "summary": _placeholder("orientation-only exploration summary"),
                    "original_question": target_record.get("original_question", ""),
                    "local_question": target_record.get("local_question", ""),
                    "object_ids": list(target_record.get("object_ids") or []),
                    "relation_ids": list(target_record.get("relation_ids") or []),
                    "source_refs": _source_refs(target_record),
                    "unresolved_points": list(target_record.get("unresolved_points") or []),
                    "next_actions": list(target_record.get("next_actions") or []),
                }
            ),
        }
    if entrypoint == "aitp_v5_record_validation_result":
        return {
            **base,
            "record_action": "record_validation_result",
            "required_fields": ["topic_id", "claim_id", "contract_id", "tool_run_id", "status", "summary"],
            "draft": _clean_mapping(
                {
                    "topic_id": topic_id,
                    "claim_id": claim_id,
                    "contract_id": _placeholder("validation contract id"),
                    "tool_run_id": _placeholder("tool run id"),
                    "status": "partial",
                    "summary": _placeholder("validation result summary"),
                    "checked_outputs": _supports_outputs(target_record),
                }
            ),
        }
    return None


def _evidence_type_for_target(target_type: str, action_kind: str) -> str:
    if target_type == "proof_obligation":
        return "proof_obligation_resolution"
    if "source" in action_kind or "backtrace" in action_kind:
        return "source_reconstruction"
    return "process_record"


def _exploration_type_for_action(action_kind: str) -> str:
    if "relation_path" in action_kind:
        return "relation_path_brainstorm"
    if "source" in action_kind or "backtrace" in action_kind:
        return "backtrace_step"
    if "original" in action_kind:
        return "question_decomposition"
    return "steering_checkpoint"


def _exploration_title(action_kind: str) -> str:
    if "relation_path" in action_kind:
        return "Record relation-path brainstorm"
    if "source" in action_kind or "backtrace" in action_kind:
        return "Record source backtrace step"
    if "original" in action_kind:
        return "Record original-question drift check"
    return "Record research steering checkpoint"


def _supports_outputs(record: dict[str, Any]) -> list[str]:
    for key in ("required_evidence", "missing_components"):
        values = record.get(key)
        if isinstance(values, list):
            return [str(value) for value in values if str(value)]
    return []


def _source_refs(record: dict[str, Any]) -> list[str]:
    values = record.get("source_refs")
    if isinstance(values, list):
        return [str(value) for value in values if str(value)]
    return []


def _placeholder(label: str) -> str:
    return f"<{label}>"


def _clean_mapping(value: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, item in value.items():
        if item == "" or item == [] or item == {}:
            continue
        result[key] = item
    return result


def _entrypoints(
    record_entrypoints: list[str],
    exploration_entrypoints: list[str],
    required_before_trust_change: list[str],
) -> list[str]:
    result: list[str] = []
    for value in [*record_entrypoints, *exploration_entrypoints]:
        if value and value not in result:
            result.append(value)
    if any("aitp_v5_preflight_trust_update" in value for value in required_before_trust_change):
        result.append("aitp_v5_preflight_trust_update")
    return result
