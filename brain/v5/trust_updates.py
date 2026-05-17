"""Trust-changing action preflight for AITP v5."""

from __future__ import annotations

from dataclasses import asdict

from brain.v5.models import ClaimRecord, CodeStateRecord, TrustUpdateRequest
from brain.v5.paths import WorkspacePaths
from brain.v5.policy import evaluate_policy
from brain.v5.store import list_records
from brain.v5.workspace import get_claim

_SUMMARY_SOURCE_KINDS = {
    "derived_summary",
    "summary_orientation",
    "task_plan",
    "findings",
    "progress",
}


def preflight_trust_update(ws: WorkspacePaths, request: TrustUpdateRequest) -> dict:
    """Check whether a trust-changing request may mutate kernel state.

    The preflight returns a typed policy payload only. It does not update the
    claim, confidence state, evidence ledger, validation state, or L2 memory.
    """

    claim = get_claim(ws, request.claim_id)
    code_states = _resolve_code_states(ws, claim, request.code_state_ids)
    source_kind = request.source_kind.strip().lower()
    decision = evaluate_policy(
        action=request.action,
        claim=claim,
        code_states=code_states,
        evidence_refs=request.evidence_refs,
        context={
            "source_kind": source_kind,
            "source_ref": request.source_ref,
            "orientation_only": source_kind in _SUMMARY_SOURCE_KINDS,
        },
    )
    return {
        "kind": "trust_update_preflight",
        "request": asdict(request),
        "request_id": request.request_id,
        "action": request.action,
        "session_id": request.session_id,
        "topic_id": request.topic_id,
        "claim_id": request.claim_id,
        "requested_state": request.requested_state,
        "allowed": decision.allowed,
        "mutation_allowed_after_preflight": decision.allowed,
        "policy_reasons": [asdict(reason) for reason in decision.reasons],
        "required_actions": decision.required_actions,
        "evidence_refs": list(request.evidence_refs),
        "code_state_ids": [state.code_state_id for state in code_states],
        "truth_source": "typed_records",
        "summary_inputs_trusted": False,
        "can_update_kernel_state": False,
    }


def _resolve_code_states(
    ws: WorkspacePaths,
    claim: ClaimRecord,
    requested_ids: list[str],
) -> list[CodeStateRecord]:
    states = list_records(ws.registry_dir("code_states"), CodeStateRecord)
    if requested_ids:
        wanted = set(requested_ids)
        return [state for state in states if state.code_state_id in wanted]
    return [state for state in states if _record_links_to_claim(state.linked_records, claim.claim_id)]


def _record_links_to_claim(linked_records: dict, claim_id: str) -> bool:
    for value in linked_records.values():
        if value == claim_id:
            return True
        if isinstance(value, list) and claim_id in value:
            return True
    return False
