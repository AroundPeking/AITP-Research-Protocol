"""Validation contract records for AITP v5."""

from __future__ import annotations

from brain.v5.ids import prefixed_id
from brain.v5.models import ValidationContractRecord
from brain.v5.paths import WorkspacePaths
from brain.v5.store import write_record


def create_validation_contract(
    ws: WorkspacePaths,
    *,
    topic_id: str,
    claim_id: str,
    required_checks: list[str] | None = None,
    failure_modes: list[str] | None = None,
    required_evidence_outputs: list[str] | None = None,
    tool_recipe_ids: list[str] | None = None,
    executor_ids: list[str] | None = None,
    validator_role: str = "adversarial_reviewer",
) -> ValidationContractRecord:
    contract_id = prefixed_id(
        "validation-contract",
        f"{topic_id}:{claim_id}:{validator_role}",
        max_slug=64,
    )
    record = ValidationContractRecord(
        contract_id=contract_id,
        topic_id=topic_id,
        claim_id=claim_id,
        required_checks=required_checks or [],
        failure_modes=failure_modes or [],
        required_evidence_outputs=required_evidence_outputs or [],
        tool_recipe_ids=tool_recipe_ids or [],
        executor_ids=executor_ids or [],
        validator_role=validator_role,
    )
    write_record(
        ws.registry_dir("validation_contracts") / f"{contract_id}.md",
        record,
        body=f"# Validation Contract: {contract_id}\n\n"
        f"Required checks: {', '.join(record.required_checks)}\n"
        f"Failure modes: {', '.join(record.failure_modes)}\n"
        f"Tool recipes: {', '.join(record.tool_recipe_ids)}\n"
        f"Executors: {', '.join(record.executor_ids)}\n",
    )
    return record
