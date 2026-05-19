"""Tests for AITP v5 validation contract records."""

from dataclasses import asdict
from pathlib import Path

import pytest


def _init_ws(tmp_path: Path):
    from brain.v5.workspace import init_workspace

    return init_workspace(tmp_path)


def _setup_claim(tmp_path: Path):
    from brain.v5.workspace import create_claim, create_topic, init_workspace

    ws = init_workspace(tmp_path)
    create_topic(ws, "gw", context_id="gw-methods", title="GW")
    claim = create_claim(
        ws,
        topic_id="gw",
        statement="The modified self-energy kernel reproduces the benchmark.",
        evidence_profile="code_method",
        confidence_state="hypothesis",
        active_uncertainty="formula-code translation",
    )
    return ws, claim


def test_create_validation_contract_requires_claim_checks_and_failure_modes(tmp_path):
    ws, claim = _setup_claim(tmp_path)

    from brain.v5.public_surfaces import require_valid_public_surface
    from brain.v5.validation import create_validation_contract

    contract = create_validation_contract(
        ws,
        topic_id="gw",
        claim_id=claim.claim_id,
        required_checks=["code_state_present", "benchmark_table_within_tolerance"],
        failure_modes=["wrong frequency grid", "dirty worktree"],
        required_evidence_outputs=["evidence_or_provenance", "minimal_check"],
        validator_role="adversarial_reviewer",
    )

    payload = {"ok": True, **asdict(contract)}
    assert contract.kind == "validation_contract"
    assert contract.status == "open"
    assert require_valid_public_surface("validation_contract_record", payload) == payload


def test_validation_contract_rejects_empty_required_checks(tmp_path):
    ws, claim = _setup_claim(tmp_path)

    from brain.v5.contracts import ContractError
    from brain.v5.public_surfaces import require_valid_public_surface
    from brain.v5.validation import create_validation_contract

    contract = create_validation_contract(
        ws,
        topic_id="gw",
        claim_id=claim.claim_id,
        required_checks=[],
        failure_modes=["something"],
        required_evidence_outputs=["something_else"],
    )

    payload = {"ok": True, **asdict(contract)}
    with pytest.raises(ContractError, match="required_checks"):
        require_valid_public_surface("validation_contract_record", payload)


def test_validation_contract_rejects_empty_failure_modes(tmp_path):
    ws, claim = _setup_claim(tmp_path)

    from brain.v5.contracts import ContractError
    from brain.v5.public_surfaces import require_valid_public_surface
    from brain.v5.validation import create_validation_contract

    contract = create_validation_contract(
        ws,
        topic_id="gw",
        claim_id=claim.claim_id,
        required_checks=["code_state_present"],
        failure_modes=[],
        required_evidence_outputs=["evidence_or_provenance"],
    )

    payload = {"ok": True, **asdict(contract)}
    with pytest.raises(ContractError, match="failure_modes"):
        require_valid_public_surface("validation_contract_record", payload)


def test_validation_contract_rejects_empty_required_evidence_outputs(tmp_path):
    ws, claim = _setup_claim(tmp_path)

    from brain.v5.contracts import ContractError
    from brain.v5.public_surfaces import require_valid_public_surface
    from brain.v5.validation import create_validation_contract

    contract = create_validation_contract(
        ws,
        topic_id="gw",
        claim_id=claim.claim_id,
        required_checks=["code_state_present"],
        failure_modes=["dirty worktree"],
        required_evidence_outputs=[],
    )

    payload = {"ok": True, **asdict(contract)}
    with pytest.raises(ContractError, match="required_evidence_outputs"):
        require_valid_public_surface("validation_contract_record", payload)


def test_validation_contract_persists(tmp_path):
    ws, claim = _setup_claim(tmp_path)

    from brain.v5.validation import create_validation_contract
    from brain.v5.store import list_records
    from brain.v5.models import ValidationContractRecord

    contract = create_validation_contract(
        ws,
        topic_id="gw",
        claim_id=claim.claim_id,
        required_checks=["code_state_present"],
        failure_modes=["dirty worktree"],
        required_evidence_outputs=["evidence_or_provenance"],
    )

    records = list_records(ws.registry_dir("validation_contracts"), ValidationContractRecord)
    assert len(records) == 1
    assert records[0].contract_id == contract.contract_id


def test_validation_cli_json_output(tmp_path):
    ws, claim = _setup_claim(tmp_path)

    from brain.v5.cli import main

    result = main(
        [
            "--base",
            str(tmp_path),
            "validation",
            "contract",
            "create",
            "--topic",
            "gw",
            "--claim",
            claim.claim_id,
            "--required-check",
            "code_state_present",
            "--failure-mode",
            "dirty worktree",
            "--required-output",
            "evidence_or_provenance",
        ]
    )
    assert result == 0


def test_validation_mcp_valid_surface(tmp_path):
    ws, claim = _setup_claim(tmp_path)

    from brain.v5.mcp_tools import aitp_v5_create_validation_contract

    result = aitp_v5_create_validation_contract(
        str(tmp_path),
        topic_id="gw",
        claim_id=claim.claim_id,
        required_checks=["code_state_present"],
        failure_modes=["dirty worktree"],
        required_evidence_outputs=["evidence_or_provenance"],
        validator_role="adversarial_reviewer",
    )
    assert result["ok"] is True
    assert result["kind"] == "validation_contract"
    assert result["status"] == "open"


def test_validation_runtime_entrypoint_exists():
    from brain.v5.runtime_entrypoints import runtime_entrypoints

    ep = runtime_entrypoints()
    assert "create_validation_contract" in ep
    assert ep["create_validation_contract"]["surface"] == "validation_contract_record"
