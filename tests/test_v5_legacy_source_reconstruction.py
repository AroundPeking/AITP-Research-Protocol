from __future__ import annotations

import json


def _write_migration_run(ws, *, topic="canonical-topic", claim_id="claim-canonical"):
    run = ws.root / "migrations" / "legacy-v5-lossless-source-test"
    run.mkdir(parents=True)
    summary = {
        "kind": "legacy_v5_lossless_migration_report",
        "run_id": "legacy-v5-lossless-source-test",
        "workspace": str(ws.base),
        "legacy_root": str(ws.base / "research" / "aitp-topics"),
        "v5_root": str(ws.root),
        "output_dir": str(run),
        "totals": {
            "topic_count": 1,
            "legacy_file_count": 2,
            "post_legacy_file_count": 2,
            "legacy_manifest_hash_stable": True,
            "legacy_manifest_change_count": 0,
            "structured_file_count": 2,
            "archive_reference_count": 0,
            "accounted_file_count": 2,
            "topics_with_errors": 0,
            "missing_archive_record_files": 0,
            "summary_inputs_trusted": False,
        },
        "topics": [
            {
                "topic": topic,
                "status": "ok",
                "file_count": 2,
                "audit_mapped_file_count": 2,
                "structured_file_count": 2,
                "archive_reference_count": 0,
                "accounted_file_count": 2,
                "missing_expected_paths": [],
                "can_write_v5_records": True,
                "active_claim_id": claim_id,
                "written_records": {
                    "topics": 1,
                    "claims": 1,
                    "evidence": 0,
                    "reference_locations": 0,
                    "sensemaking_reports": 0,
                    "trace_events": 0,
                    "memory_entries": 0,
                },
                "preserved_source_refs": 0,
                "summary_inputs_trusted": False,
            }
        ],
    }
    verification = {
        "kind": "legacy_v5_lossless_migration_verification",
        "run_id": "legacy-v5-lossless-source-test",
        "file_accounting_ok": True,
        "manifest_check": {"pre_count": 2, "post_count": 2, "missing": 0, "extra": 0, "changed": 0},
        "archive_reference_check": {
            "archive_records_checked": 0,
            "archive_records_expected": 0,
            "registry_archive_reference_count": 0,
            "problem_count": 0,
            "problems": [],
        },
        "markdown_readability_check": {
            "markdown_files_checked": 2,
            "problem_count": 0,
            "problems": [],
        },
        "brief_check": [],
        "all_checks_ok": True,
    }
    (run / "migration_summary.json").write_text(json.dumps(summary), encoding="utf-8")
    (run / "verification_report.json").write_text(json.dumps(verification), encoding="utf-8")
    return run


def _seed_reviewed_legacy_topic(tmp_path):
    from brain.v5.legacy_semantic_review import record_legacy_semantic_review_result
    from brain.v5.models import ClaimRecord
    from brain.v5.store import write_record
    from brain.v5.workspace import create_topic, init_workspace

    ws = init_workspace(tmp_path / "v5")
    create_topic(ws, "canonical-topic", context_id="legacy-context", title="Canonical")
    write_record(
        ws.registry_dir("claims") / "claim-canonical.md",
        ClaimRecord(
            claim_id="claim-canonical",
            topic_id="canonical-topic",
            statement="Finite-size counting identifies the edge sector.",
            evidence_profile="legacy_import",
            confidence_state="legacy_seed",
            active_uncertainty="Legacy semantic review required.",
        ),
    )
    run = _write_migration_run(ws)
    legacy_topic = ws.base / "research" / "aitp-topics" / "canonical-topic"
    candidate = legacy_topic / "L3" / "candidates" / "candidate-counting.md"
    derivation = legacy_topic / "L3" / "derive" / "active_derivation.md"
    candidate.parent.mkdir(parents=True)
    derivation.parent.mkdir(parents=True)
    candidate.write_text("# Candidate\n\nFinite-size counting identifies the edge sector.\n", encoding="utf-8")
    derivation.write_text("# Derivation\n\n1. Define the sector. 2. Compare counting.\n", encoding="utf-8")
    review = record_legacy_semantic_review_result(
        ws,
        migration_dir=run,
        topic="canonical-topic",
        status="needs_revision",
        summary="Claim statement was reviewed; source reconstruction still needs a typed reconstruction path.",
        active_claim_id="claim-canonical",
        reviewed_legacy_refs=[f"legacy_candidate:{candidate}", f"legacy_l3_process:{derivation}"],
        reviewed_typed_refs=["claim-canonical"],
        remaining_actions=["complete_source_reconstruction"],
    )
    return ws, run, review, candidate, derivation


def test_legacy_source_reconstruction_plan_uses_reviewed_l3_refs(tmp_path):
    from brain.v5.legacy_source_reconstruction import build_legacy_source_reconstruction_plan
    from brain.v5.public_surfaces import require_valid_public_surface

    ws, run, review, candidate, derivation = _seed_reviewed_legacy_topic(tmp_path)

    plan = build_legacy_source_reconstruction_plan(ws, migration_dir=run, topic="canonical-topic")

    assert require_valid_public_surface("legacy_source_reconstruction_plan", plan) == plan
    assert plan["repair_status"] == "proposed_repairs"
    assert plan["can_update_kernel_state"] is False
    assert plan["can_update_claim_trust"] is False
    assert plan["latest_semantic_review"]["review_id"] == review.review_id
    assert plan["proposed_repairs"] == [
        {
            "repair_type": "reconstruction_path_evidence_backfill",
            "target_ref": "claim-canonical",
            "current_missing_component": "reconstruction_path",
            "proposed_evidence_type": "source_reconstruction",
            "proposed_status": "supports",
            "proposed_supports_outputs": ["reconstruction_path"],
            "source_refs": [f"legacy_candidate:{candidate}", f"legacy_l3_process:{derivation}"],
            "basis_refs": [f"legacy_candidate:{candidate}", f"legacy_l3_process:{derivation}", review.review_id],
            "mutation_authority": "typed_review_and_apply_separately",
        }
    ]


def test_legacy_source_reconstruction_plan_accepts_review_action_phrase(tmp_path):
    from brain.v5.legacy_semantic_review import record_legacy_semantic_review_result
    from brain.v5.legacy_source_reconstruction import build_legacy_source_reconstruction_plan

    ws, run, _review, candidate, derivation = _seed_reviewed_legacy_topic(tmp_path)
    review = record_legacy_semantic_review_result(
        ws,
        migration_dir=run,
        topic="canonical-topic",
        status="needs_revision",
        summary="Natural-language review action asks for reconstruction-path completion.",
        active_claim_id="claim-canonical",
        reviewed_legacy_refs=[f"legacy_candidate:{candidate}", f"legacy_l3_process:{derivation}"],
        reviewed_typed_refs=["claim-canonical"],
        remaining_actions=[
            "Complete definitions, assumptions_or_scope, dependency_graph, reconstruction_path, and failure_conditions before promotion."
        ],
    )

    plan = build_legacy_source_reconstruction_plan(ws, migration_dir=run, topic="canonical-topic")

    assert plan["repair_status"] == "proposed_repairs"
    assert plan["latest_semantic_review"]["review_id"] == review.review_id
    assert plan["proposed_repairs"][0]["repair_type"] == "reconstruction_path_evidence_backfill"


def test_legacy_source_reconstruction_apply_writes_reconstruction_path_evidence(tmp_path):
    from brain.v5.evidence import list_evidence_for_claim
    from brain.v5.legacy_source_reconstruction import apply_legacy_source_reconstruction_repair
    from brain.v5.public_surfaces import require_valid_public_surface
    from brain.v5.source_reconstruction import audit_source_reconstruction

    ws, run, review, _candidate, _derivation = _seed_reviewed_legacy_topic(tmp_path)

    payload = apply_legacy_source_reconstruction_repair(
        ws,
        migration_dir=run,
        topic="canonical-topic",
        repair_type="reconstruction_path_evidence_backfill",
        review_id=review.review_id,
    )

    assert require_valid_public_surface("legacy_source_reconstruction_apply", payload) == payload
    assert payload["applied"] is True
    assert payload["evidence_id"]
    assert payload["can_update_kernel_state"] is True
    assert payload["can_update_claim_trust"] is False
    evidence = list_evidence_for_claim(ws, "claim-canonical")
    assert [record.evidence_id for record in evidence] == [payload["evidence_id"]]
    assert evidence[0].evidence_type == "source_reconstruction"
    assert evidence[0].supports_outputs == ["reconstruction_path"]
    audit = audit_source_reconstruction(ws, claim_id="claim-canonical")
    assert "reconstruction_path" not in audit["missing_components"]


def test_legacy_source_reconstruction_cli_mcp_and_runtime_surface(tmp_path, capsys):
    from brain.v5.cli import main
    from brain.v5.mcp_tools import aitp_v5_build_legacy_source_reconstruction_plan
    from brain.v5.runtime_entrypoints import runtime_entrypoints

    ws, run, _review, _candidate, _derivation = _seed_reviewed_legacy_topic(tmp_path)

    assert main([
        "--base",
        str(ws.base),
        "legacy",
        "source-reconstruction-plan",
        "--migration-dir",
        str(run),
        "--topic",
        "canonical-topic",
    ]) == 0
    cli_payload = json.loads(capsys.readouterr().out)
    mcp_payload = aitp_v5_build_legacy_source_reconstruction_plan(
        str(ws.base),
        migration_dir=str(run),
        topic="canonical-topic",
    )

    assert cli_payload["kind"] == "legacy_source_reconstruction_plan"
    assert mcp_payload["kind"] == "legacy_source_reconstruction_plan"
    assert runtime_entrypoints()["legacy_source_reconstruction_plan"] == {
        "cli": "aitp-v5 legacy source-reconstruction-plan <args>",
        "mcp": "aitp_v5_build_legacy_source_reconstruction_plan",
        "surface": "legacy_source_reconstruction_plan",
    }
