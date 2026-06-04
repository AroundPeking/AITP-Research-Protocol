"""Curated legacy-topic migration into v5 typed records.

The generic legacy bridge preserves files and candidate notes.  This module
adds a small, explicit curation layer for priority theoretical-physics topics
whose current scientific status is known well enough to become typed v5
records: active claim, evidence, status, validation contract, open obligations,
and a topic-local migration index.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from brain.v5.evidence import record_evidence
from brain.v5.legacy_bridge import migrate_legacy_topic_to_v5, scan_legacy_topic
from brain.v5.markdown import write_md
from brain.v5.paths import WorkspacePaths
from brain.v5.research_state import attach_artifact, create_proof_obligation, update_claim_status
from brain.v5.sensemaking import record_sensemaking_report
from brain.v5.validation import create_validation_contract
from brain.v5.workspace import bind_session, create_claim, create_context, create_topic


@dataclass(frozen=True)
class CuratedArtifactSpec:
    path: str
    artifact_type: str
    summary: str


@dataclass(frozen=True)
class CuratedEvidenceSpec:
    evidence_type: str
    status: str
    summary: str
    supports_outputs: list[str] = field(default_factory=list)
    artifact_paths: list[str] = field(default_factory=list)
    source_refs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CuratedObligationSpec:
    statement: str
    obligation_type: str
    status: str
    next_action: str
    required_evidence: list[str] = field(default_factory=list)
    proof_strategy: list[str] = field(default_factory=list)
    failure_modes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CuratedTopicSpec:
    topic_id: str
    context_id: str
    session_id: str
    title: str
    claim_statement: str
    evidence_profile: str
    confidence_state: str
    active_uncertainty: str
    maturity_level: str
    claim_status: str
    scope: str
    risk: str
    next_action: str
    assumptions: list[str]
    open_gaps: list[str]
    non_claims: str = ""
    strongest_failure_mode: str = ""
    artifacts: list[CuratedArtifactSpec] = field(default_factory=list)
    evidence: list[CuratedEvidenceSpec] = field(default_factory=list)
    obligations: list[CuratedObligationSpec] = field(default_factory=list)
    validation_checks: list[str] = field(default_factory=list)
    validation_failure_modes: list[str] = field(default_factory=list)
    validation_outputs: list[str] = field(default_factory=list)
    sensemaking_title: str = ""
    sensemaking_summary: str = ""
    next_actions: list[str] = field(default_factory=list)


def migrate_curated_legacy_topic_to_v5(
    ws: WorkspacePaths,
    topic_dir: str | Path,
    *,
    context_id: str = "",
    session_id: str = "",
) -> dict[str, Any]:
    """Migrate one known legacy topic and add curated v5 records."""

    root = Path(topic_dir)
    summary = scan_legacy_topic(root)
    spec = _spec_for_topic(summary.topic_slug)
    if context_id:
        spec = _replace(spec, context_id=context_id)
    if session_id:
        spec = _replace(spec, session_id=session_id)

    generic = migrate_legacy_topic_to_v5(
        ws,
        root,
        context_id=spec.context_id,
        session_id=f"{spec.session_id}-legacy-preserve",
    )

    create_context(ws, spec.context_id, title=spec.context_id)
    create_topic(ws, spec.topic_id, context_id=spec.context_id, title=spec.title)
    claim = create_claim(
        ws,
        topic_id=spec.topic_id,
        statement=spec.claim_statement,
        evidence_profile=spec.evidence_profile,
        confidence_state=spec.confidence_state,
        active_uncertainty=spec.active_uncertainty,
        scope=spec.scope,
        non_claims=spec.non_claims,
        strongest_failure_mode=spec.strongest_failure_mode,
    )

    artifact_by_path, missing_artifacts = _attach_curated_artifacts(ws, root, spec, claim.claim_id)
    evidence_ids = _record_curated_evidence(ws, spec, claim.claim_id, artifact_by_path)

    contract = create_validation_contract(
        ws,
        topic_id=spec.topic_id,
        claim_id=claim.claim_id,
        required_checks=spec.validation_checks,
        failure_modes=spec.validation_failure_modes,
        required_evidence_outputs=spec.validation_outputs,
        validator_role="curated_legacy_migration_review",
    )

    obligation_ids = []
    for obligation in spec.obligations:
        record = create_proof_obligation(
            ws,
            topic_id=spec.topic_id,
            claim_id=claim.claim_id,
            statement=obligation.statement,
            obligation_type=obligation.obligation_type,
            status=obligation.status,
            maturity_level=spec.maturity_level,
            next_action=obligation.next_action,
            required_evidence=obligation.required_evidence,
            proof_strategy=obligation.proof_strategy,
            failure_modes=obligation.failure_modes,
            evidence_refs=evidence_ids,
            artifact_ids=list(artifact_by_path.values()),
        )
        obligation_ids.append(record.obligation_id)

    status = update_claim_status(
        ws,
        topic_id=spec.topic_id,
        claim_id=claim.claim_id,
        maturity_level=spec.maturity_level,
        claim_status=spec.claim_status,
        scope=spec.scope,
        risk=spec.risk,
        next_action=spec.next_action,
        assumptions=spec.assumptions,
        open_gaps=spec.open_gaps,
        evidence_refs=evidence_ids,
        artifact_ids=list(artifact_by_path.values()),
        human_gate_required=True,
    )

    report = record_sensemaking_report(
        ws,
        topic_id=spec.topic_id,
        claim_id=claim.claim_id,
        title=spec.sensemaking_title or "Curated legacy-to-v5 migration",
        summary=spec.sensemaking_summary,
        evidence_refs=evidence_ids,
        open_questions=spec.open_gaps,
        next_actions=spec.next_actions,
        validation_status="migration_orientation",
    )

    bind_session(
        ws,
        spec.session_id,
        topic_id=spec.topic_id,
        context_id=spec.context_id,
        active_claim=claim.claim_id,
        active_route="curated_legacy_migration",
        interaction_profile="collaborator",
    )
    index_path = _write_curated_index(
        ws,
        spec=spec,
        claim_id=claim.claim_id,
        status_id=status.status_id,
        contract_id=contract.contract_id,
        evidence_ids=evidence_ids,
        artifact_ids=list(artifact_by_path.values()),
        obligation_ids=obligation_ids,
        report_id=report.report_id,
        missing_artifacts=missing_artifacts,
        generic_result=generic,
    )

    written = _merge_written_records(
        generic.get("written_records", {}),
        {
            "topics": [spec.topic_id],
            "claims": [claim.claim_id],
            "evidence": evidence_ids,
            "reference_locations": [],
            "sensemaking_reports": [report.report_id],
            "trace_events": [],
            "memory_entries": [],
            "artifacts": list(artifact_by_path.values()),
            "claim_statuses": [status.status_id],
            "proof_obligations": obligation_ids,
            "validation_contracts": [contract.contract_id],
            "indexes": [str(index_path)],
        },
    )

    return {
        "kind": "legacy_topic_migration_result",
        "topic_id": spec.topic_id,
        "context_id": spec.context_id,
        "session_id": spec.session_id,
        "active_claim_id": claim.claim_id,
        "written_records": written,
        "preserved_source_refs": generic.get("preserved_source_refs", []),
        "curation": {
            "claim_status_id": status.status_id,
            "validation_contract_id": contract.contract_id,
            "proof_obligation_ids": obligation_ids,
            "sensemaking_report_id": report.report_id,
            "artifact_ids": list(artifact_by_path.values()),
            "missing_artifacts": missing_artifacts,
            "index_path": str(index_path),
            "legacy_preservation_session_id": f"{spec.session_id}-legacy-preserve",
        },
        "summary_inputs_trusted": False,
    }


def known_curated_legacy_topics() -> list[str]:
    return sorted(_CURATED_SPECS)


def _replace(spec: CuratedTopicSpec, **changes: Any) -> CuratedTopicSpec:
    data = dict(spec.__dict__)
    data.update(changes)
    return CuratedTopicSpec(**data)


def _attach_curated_artifacts(
    ws: WorkspacePaths,
    topic_root: Path,
    spec: CuratedTopicSpec,
    claim_id: str,
) -> tuple[dict[str, str], list[str]]:
    artifact_by_path: dict[str, str] = {}
    missing: list[str] = []
    for item in spec.artifacts:
        path = _resolve_path(topic_root, item.path)
        if not path.exists():
            missing.append(str(path))
            continue
        artifact = attach_artifact(
            ws,
            topic_id=spec.topic_id,
            claim_id=claim_id,
            artifact_type=item.artifact_type,
            uri=path.as_posix(),
            summary=item.summary,
            metadata={
                "migration_role": "curated_legacy_evidence",
                "legacy_topic_path": topic_root.as_posix(),
            },
        )
        artifact_by_path[item.path] = artifact.artifact_id
    return artifact_by_path, missing


def _record_curated_evidence(
    ws: WorkspacePaths,
    spec: CuratedTopicSpec,
    claim_id: str,
    artifact_by_path: dict[str, str],
) -> list[str]:
    evidence_ids: list[str] = []
    for item in spec.evidence:
        artifact_ids = [artifact_by_path[path] for path in item.artifact_paths if path in artifact_by_path]
        evidence = record_evidence(
            ws,
            topic_id=spec.topic_id,
            claim_id=claim_id,
            evidence_type=item.evidence_type,
            status=item.status,
            summary=item.summary,
            supports_outputs=item.supports_outputs,
            source_refs=item.source_refs,
            artifact_ids=artifact_ids,
        )
        evidence_ids.append(evidence.evidence_id)
    return evidence_ids


def _write_curated_index(
    ws: WorkspacePaths,
    *,
    spec: CuratedTopicSpec,
    claim_id: str,
    status_id: str,
    contract_id: str,
    evidence_ids: list[str],
    artifact_ids: list[str],
    obligation_ids: list[str],
    report_id: str,
    missing_artifacts: list[str],
    generic_result: dict[str, Any],
) -> Path:
    path = ws.topic_dir(spec.topic_id) / "indexes" / "legacy_v5_curated_migration.md"
    body = "\n".join(
        [
            f"# Curated Legacy v5 Migration: {spec.topic_id}",
            "",
            "This index is generated by `brain.v5.curated_legacy_migration`.",
            "It is a migration/control-plane artifact and does not promote the claim to L2.",
            "",
            f"Active claim: `{claim_id}`",
            f"Claim status: `{status_id}`",
            f"Validation contract: `{contract_id}`",
            f"Sensemaking report: `{report_id}`",
            "",
            "## Evidence Records",
            *[f"- `{item}`" for item in evidence_ids],
            "",
            "## Artifact Records",
            *[f"- `{item}`" for item in artifact_ids],
            "",
            "## Proof Obligations",
            *[f"- `{item}`" for item in obligation_ids],
            "",
            "## Missing Artifacts",
            *([f"- `{item}`" for item in missing_artifacts] or ["- none"]),
            "",
            "## Legacy Preservation",
            f"Generic migration active claim: `{generic_result.get('active_claim_id', '')}`",
            "Generic migration records preserve legacy sources, candidates, and process notes as untrusted evidence.",
            "",
        ]
    )
    write_md(
        path,
        {
            "kind": "legacy_v5_curated_migration_index",
            "topic_id": spec.topic_id,
            "claim_id": claim_id,
            "status_id": status_id,
            "validation_contract_id": contract_id,
            "summary_inputs_trusted": False,
        },
        body,
    )
    return path


def _merge_written_records(base: dict[str, Any], extra: dict[str, list[str]]) -> dict[str, list[str]]:
    required = [
        "topics",
        "claims",
        "evidence",
        "reference_locations",
        "sensemaking_reports",
        "trace_events",
        "memory_entries",
    ]
    merged: dict[str, list[str]] = {}
    for key in required:
        merged[key] = _unique([*(base.get(key) or []), *(extra.get(key) or [])])
    for key, values in extra.items():
        if key not in merged:
            merged[key] = _unique(values)
    return merged


def _resolve_path(topic_root: Path, value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return topic_root / path


def _unique(values: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value not in seen:
            out.append(value)
            seen.add(value)
    return out


_CURATED_SPECS: dict[str, CuratedTopicSpec] = {
    "qsgw-headwing-update-librpa": CuratedTopicSpec(
        topic_id="qsgw-headwing-update-librpa",
        context_id="librpa-qsgw",
        session_id="v5-qsgw-headwing-update-librpa",
        title="QSGW Head-Wing Update Algorithm in LibRPA",
        claim_statement=(
            "LibRPA QSGW head-wing update evidence supports a scoped algorithm "
            "and route taxonomy, but the topic is not L2-ready until both L4 "
            "reviews and true-frozen reuse validation are recorded."
        ),
        evidence_profile="code_method",
        confidence_state="review_blocked",
        active_uncertainty=(
            "MgO evidence is strongest, BN is partial, Si is not improved, and "
            "true-frozen dielectric reuse failed before iteration-2 reuse."
        ),
        maturity_level="formula-identified",
        claim_status="blocked_by_missing_l4_reviews",
        scope=(
            "ABACUS/PyATB/LibRPA QSGW head-only, head-wing, old velocity-frozen, "
            "and true dielectric-frozen routes as of the 2026-06-04 reports."
        ),
        risk="High: route semantics, k-convergence evidence, and reuse behavior are not all closed.",
        next_action="Record L4 reviews for cand-headwing-rotation-v1 and headwing-algorithm-trace-v1.",
        assumptions=[
            "Report-level MgO/BN/Si summaries are orientation until linked to reviewed artifacts.",
            "Old frozen routes are diagnostic because they froze PyATB velocity, not LibRPA dielectric head/wing.",
            "True-frozen first-iteration capture does not prove reuse semantics.",
        ],
        open_gaps=[
            "missing review for cand-headwing-rotation-v1",
            "missing review for headwing-algorithm-trace-v1",
            "true-frozen dielectric reuse not validated",
        ],
        non_claims=(
            "No universal material claim, no L2 promotion, and no claim that true-frozen "
            "reuse works after iteration 1."
        ),
        strongest_failure_mode="A route label or frozen/reuse semantic mismatch can turn diagnostic rows into false final evidence.",
        artifacts=[
            CuratedArtifactSpec("state.md", "legacy_state", "Legacy topic state showing L4 blocked review status."),
            CuratedArtifactSpec("L3/candidates/cand-headwing-rotation-v1.md", "legacy_candidate", "Velocity rotation and recomputation candidate."),
            CuratedArtifactSpec("L3/candidates/headwing-algorithm-trace-v1.md", "legacy_candidate", "Eleven-step head-wing algorithm trace candidate."),
            CuratedArtifactSpec("L3/gap-audit/active_gaps.md", "legacy_gap_audit", "Legacy active gaps for head-wing implementation validation."),
            CuratedArtifactSpec("L3/runs/run-001-headwing-trace/result_summary.md", "legacy_run_summary", "Head-wing trace run summary."),
            CuratedArtifactSpec("L3/runs/run-001-headwing-trace/derivation_records.md", "legacy_derivation", "Head-wing trace derivation records."),
            CuratedArtifactSpec(
                "F:/AI_Workspace/Theoretical-Physics/research/librpa/reports/qsgw_headwing_update_aitp_research_order_20260604.md",
                "research_report",
                "Curated AITP research-order report for QSGW head-wing update.",
            ),
        ],
        evidence=[
            CuratedEvidenceSpec(
                "curated_report",
                "supports",
                "MgO is the strongest current positive evidence; BN is partial; Si does not show a clear improvement.",
                ["evidence_or_provenance", "minimal_check"],
                ["F:/AI_Workspace/Theoretical-Physics/research/librpa/reports/qsgw_headwing_update_aitp_research_order_20260604.md"],
            ),
            CuratedEvidenceSpec(
                "candidate_claim",
                "supports",
                "Two submitted legacy candidates define the velocity-rotation fix and end-to-end head-wing trace.",
                ["evidence_or_provenance"],
                ["L3/candidates/cand-headwing-rotation-v1.md", "L3/candidates/headwing-algorithm-trace-v1.md"],
            ),
            CuratedEvidenceSpec(
                "negative_control",
                "mixed",
                "Old frozen routes are diagnostic-only because their dielectric head/wing was still recomputed.",
                ["failure_mode"],
                ["F:/AI_Workspace/Theoretical-Physics/research/librpa/reports/qsgw_headwing_update_aitp_research_order_20260604.md"],
            ),
            CuratedEvidenceSpec(
                "incomplete_validation",
                "inconclusive",
                "True-frozen dielectric pilots captured iteration 1 but crashed before reuse, so reuse semantics remain unresolved.",
                ["minimal_check", "failure_mode"],
                ["F:/AI_Workspace/Theoretical-Physics/research/librpa/reports/qsgw_headwing_update_aitp_research_order_20260604.md"],
            ),
        ],
        obligations=[
            CuratedObligationSpec(
                "Complete the L4 review for cand-headwing-rotation-v1.",
                "l4_review",
                "open",
                "Review velocity-basis rotation, recomputation placement, MPI/reference semantics, and route invariants.",
                ["review artifact", "code-source anchors", "runtime marker evidence"],
            ),
            CuratedObligationSpec(
                "Complete the L4 review for headwing-algorithm-trace-v1.",
                "l4_review",
                "open",
                "Review the 11-step trace from velocity input through W consumption and final band output.",
                ["review artifact", "source line anchors", "route-to-output trace"],
            ),
            CuratedObligationSpec(
                "Validate true-frozen dielectric reuse beyond first-iteration capture.",
                "runtime_validation",
                "open",
                "Implement or locate persistent dielectric cache support, then run a two-iteration sbatch smoke requiring capture plus reuse markers.",
                ["sbatch log", "capture marker", "reuse marker"],
                failure_modes=["jobs crash before reuse", "wing/head route invariant violated"],
            ),
        ],
        validation_checks=[
            "review cand-headwing-rotation-v1",
            "review headwing-algorithm-trace-v1",
            "separate final rows from diagnostic rows",
            "validate true-frozen capture and reuse markers",
        ],
        validation_failure_modes=[
            "missing_l4_review",
            "diagnostic_route_treated_as_final",
            "true_frozen_reuse_unverified",
        ],
        validation_outputs=["evidence_or_provenance", "minimal_check", "failure_mode"],
        sensemaking_title="QSGW head-wing v5 migration status",
        sensemaking_summary=(
            "The topic has enough typed evidence for a scoped route taxonomy and "
            "candidate-review work plan, but not for trust promotion. The active "
            "v5 claim is intentionally review-blocked."
        ),
        next_actions=[
            "write L4 review for cand-headwing-rotation-v1",
            "write L4 review for headwing-algorithm-trace-v1",
            "repair and validate true-frozen dielectric reuse if still needed",
        ],
    ),
    "quantum-chaos-long-range-spin-chains": CuratedTopicSpec(
        topic_id="quantum-chaos-long-range-spin-chains",
        context_id="quantum-chaos",
        session_id="v5-quantum-chaos-long-range-spin-chains-alpha-axis",
        title="Quantum Chaos in Long-Range Power-Law Heisenberg Spin Chains",
        claim_statement=(
            "The alpha-axis proof currently supports the conditional theorem "
            "SC(L, eta) plus complete exception boundary implies generic "
            "finite-alpha residual fullness, but it does not prove the all-L "
            "unconditional theorem."
        ),
        evidence_profile="formal_theory",
        confidence_state="conditional_theorem_candidate",
        active_uncertainty=(
            "Four all-L proof gaps remain: corrected separator family, A2 replacement sufficiency, "
            "T2 connector theorem, and all-L L=12,A2 exception isolation."
        ),
        maturity_level="theorem-candidate",
        claim_status="conditional_ready_unconditional_blocked",
        scope=(
            "Alpha-axis residual-fullness proof program after the 2026-06-04 HS workspace migration."
        ),
        risk="High: finite certificates and theorem-level lemmas do not close the all-L theorem.",
        next_action="Work one open proof obligation at a time, starting with the corrected separator-family theorem.",
        assumptions=[
            "The migrated HS workspace audit is provenance accounting, not semantic proof.",
            "Finite rational/mod-p certificates are exact only in their stated ranges.",
            "No all-L unconditional claim is allowed until all four obligations close.",
        ],
        open_gaps=[
            "corrected separator-family theorem",
            "A2 T1+T2 replacement sufficiency",
            "T2 connector theorem",
            "all-L L=12,A2 exception isolation",
        ],
        non_claims="This migration does not claim all-L unconditional generic finite-alpha residual fullness.",
        strongest_failure_mode="Promoting finite connector evidence or a conditional theorem as an unconditional all-L theorem.",
        artifacts=[
            CuratedArtifactSpec("runtime/provenance/hs-workspace-migration-20260604/MIGRATION_AUDIT.md", "migration_audit", "HS workspace migration audit."),
            CuratedArtifactSpec("L3/plan/alpha-axis-aitp-migration-map-20260604.md", "migration_map", "Research-order placement map for the HS migration."),
            CuratedArtifactSpec("L3/derive/alpha-axis-proof/MIGRATION_INDEX.md", "proof_index", "Alpha-axis proof migration index."),
            CuratedArtifactSpec("L3/derive/alpha-axis-proof/notes/alpha_axis_remaining_proof_stratification_20260604.md", "proof_status", "Current proof stratification and open gaps."),
            CuratedArtifactSpec("L3/gap-audit/active_gaps.md", "gap_audit", "Active alpha-axis proof gap audit."),
            CuratedArtifactSpec("L3/integrate/jhep-alpha-axis-20260604/main.tex", "manuscript_source", "JHEP alpha-axis manuscript source."),
            CuratedArtifactSpec("L3/integrate/jhep-alpha-axis-20260604/main.pdf", "manuscript_pdf", "JHEP alpha-axis compiled manuscript PDF."),
            CuratedArtifactSpec("L3/derive/alpha-axis-proof/notes/alpha_axis_k3_exactQ_L9_L22_finite_certificate_20260602.md", "finite_certificate", "Exact rational connector finite certificate."),
        ],
        evidence=[
            CuratedEvidenceSpec(
                "migration_accounting",
                "supports",
                "The HS external workspace was copied into research-order AITP locations with zero missing files in the audited families.",
                ["evidence_or_provenance"],
                ["runtime/provenance/hs-workspace-migration-20260604/MIGRATION_AUDIT.md", "L3/plan/alpha-axis-aitp-migration-map-20260604.md"],
            ),
            CuratedEvidenceSpec(
                "conditional_theorem_status",
                "supports",
                "The proof stratification states the safe theorem as conditional on SC(L, eta) and complete exception boundary.",
                ["scoped_claim", "evidence_or_provenance", "minimal_check"],
                ["L3/derive/alpha-axis-proof/notes/alpha_axis_remaining_proof_stratification_20260604.md"],
            ),
            CuratedEvidenceSpec(
                "finite_certificate",
                "supports",
                "Exact finite evidence includes L=9..22 connector certificates, L=12,A2 common line and split, and A2 evidence through L=44.",
                ["minimal_check"],
                ["L3/derive/alpha-axis-proof/notes/alpha_axis_remaining_proof_stratification_20260604.md", "L3/derive/alpha-axis-proof/notes/alpha_axis_k3_exactQ_L9_L22_finite_certificate_20260602.md"],
            ),
            CuratedEvidenceSpec(
                "open_gap_audit",
                "inconclusive",
                "The active gap audit lists four all-L gaps that block the unconditional theorem.",
                ["failure_mode"],
                ["L3/gap-audit/active_gaps.md"],
            ),
            CuratedEvidenceSpec(
                "manuscript_build",
                "supports",
                "The migrated JHEP manuscript source/PDF are preserved as integration artifacts, not validation of the theorem.",
                ["evidence_or_provenance"],
                ["L3/integrate/jhep-alpha-axis-20260604/main.tex", "L3/integrate/jhep-alpha-axis-20260604/main.pdf"],
            ),
        ],
        obligations=[
            CuratedObligationSpec(
                "Prove the corrected separator-family theorem for every admissible non-exceptional row.",
                "all_l_theorem",
                "open",
                "Show the chosen separator has square-free characteristic polynomial in all required rows.",
                ["uniform proof", "failure cases", "exception boundary"],
                ["signed-bracelet or Young-lattice structural proof"],
            ),
            CuratedObligationSpec(
                "Prove A2 T1+T2 replacement-family sufficiency for L=4 mod 8 rows with L>=20.",
                "all_l_theorem",
                "open",
                "Close the multiplicity bound, simple-spectrum proof, and connector compatibility.",
                ["all-L upper bound", "simple spectrum proof", "connector compatibility"],
            ),
            CuratedObligationSpec(
                "Prove the T2 connector theorem after the separator is chosen.",
                "all_l_theorem",
                "open",
                "Prove that commuting with the separator and T2 forces a scalar operator.",
                ["uniform connector proof"],
            ),
            CuratedObligationSpec(
                "Isolate the L=12,A2 exception in an all-L classification.",
                "exception_boundary",
                "open",
                "Prove no other rows have common radial-shell lines, or give the complete parametrized exception family.",
                ["exception classification"],
            ),
        ],
        validation_checks=[
            "separate theorem-level lemmas from finite certificates",
            "verify four all-L proof obligations remain open",
            "prevent unconditional theorem wording before obligations close",
            "preserve manuscript and ledgers as artifacts, not L2 memory",
        ],
        validation_failure_modes=[
            "finite_scan_overpromoted",
            "conditional_theorem_overpromoted",
            "exception_boundary_incomplete",
        ],
        validation_outputs=["scoped_claim", "evidence_or_provenance", "minimal_check", "failure_mode"],
        sensemaking_title="Alpha-axis v5 migration status",
        sensemaking_summary=(
            "The migration produces a v5 active claim that is strong but explicitly conditional. "
            "The v5 next actions are the four open all-L obligations rather than a legacy L3/L4 stage branch."
        ),
        next_actions=[
            "attack the corrected separator-family theorem",
            "keep manuscript wording conditional",
            "record any new finite evidence as bounded evidence only",
        ],
    ),
    "gw-dmft": CuratedTopicSpec(
        topic_id="gw-dmft",
        context_id="gw-dmft",
        session_id="v5-gw-dmft-workflow-conventions",
        title="GW+DMFT Workflow, cRPA, and Double Counting",
        claim_statement=(
            "The current GW+DMFT topic supports a source-grounded workflow map and "
            "validation plan, but no implementation-level or L2 scientific claim "
            "should be formed before Matsubara, projector, cRPA, and double-counting conventions are aligned."
        ),
        evidence_profile="formal_theory",
        confidence_state="framing_only",
        active_uncertainty=(
            "Slide-deck formulas must be cross-mapped to primary GW+DMFT/QSGW+DMFT/GW+EDMFT references before candidate formation."
        ),
        maturity_level="exploratory",
        claim_status="framed_not_candidate",
        scope=(
            "QSGW/GW, cRPA, DMFT/CTQMC workflow framing with local self-energy, screened interaction, and double-counting checks."
        ),
        risk="High: sign, frequency, projector, and double-counting conventions can invalidate the workflow.",
        next_action="Read registered primary sources and derive the Matsubara local GW double-counting convention.",
        assumptions=[
            "The WeChat slide deck is an orientation source, not a final derivation.",
            "No relevant trusted L2 memory was found for this topic on 2026-06-04.",
            "QSGW+DMFT and GW+EDMFT branches must remain separate until self-consistency assumptions are explicit.",
        ],
        open_gaps=[
            "Matsubara conventions for chi_loc, Sigma_DC, and epsilon_H_DC",
            "projector normalization and local orbital basis definitions",
            "cRPA sign convention for W_loc = (1 - chi_loc U)^-1 U",
            "Hartree double-counting sign when embedding into lattice self-energy",
            "primary-literature cross-map before candidate claim",
        ],
        non_claims="No production workflow, benchmark, material prediction, or L2 promotion is claimed.",
        strongest_failure_mode="A sign or frequency convention mismatch makes Sigma_bar or W_loc algebraically wrong.",
        artifacts=[
            CuratedArtifactSpec("state.md", "legacy_state", "Legacy GW+DMFT topic state."),
            CuratedArtifactSpec("L1/question_contract.md", "question_contract", "Bounded GW+DMFT question contract."),
            CuratedArtifactSpec("L1/source_basis.md", "source_basis", "Source basis identifying the slide deck and missing literature depth."),
            CuratedArtifactSpec("L3/gw-dmft-research-brief.md", "research_brief", "GW+DMFT L3 research brief."),
            CuratedArtifactSpec("L3/plan/active_plan.md", "active_plan", "GW+DMFT convention-alignment work plan."),
        ],
        evidence=[
            CuratedEvidenceSpec(
                "question_contract",
                "supports",
                "The topic is bounded to workflow consistency, local self-energy correction, screened interaction, and double-counting validation.",
                ["evidence_or_provenance"],
                ["L1/question_contract.md"],
            ),
            CuratedEvidenceSpec(
                "source_basis",
                "mixed",
                "The slide deck supplies the first workflow map, but primary literature remains a required next step.",
                ["evidence_or_provenance", "failure_mode"],
                ["L1/source_basis.md"],
            ),
            CuratedEvidenceSpec(
                "research_brief",
                "supports",
                "The L3 brief separates QSGW+DMFT fixed/static U, dynamic U, and fully self-consistent GW+EDMFT branches.",
                ["minimal_check"],
                ["L3/gw-dmft-research-brief.md"],
            ),
            CuratedEvidenceSpec(
                "validation_plan",
                "supports",
                "The active plan names convention alignment, local double-counting derivation, and limiting-case validation before candidate formation.",
                ["minimal_check"],
                ["L3/plan/active_plan.md"],
            ),
        ],
        obligations=[
            CuratedObligationSpec(
                "Translate the slide-deck real-time factors into explicit Matsubara conventions.",
                "convention_alignment",
                "open",
                "Write the frequency/sign convention map for chi_loc, Sigma_DC, and epsilon_H_DC.",
                ["source cross-map", "equation derivation"],
            ),
            CuratedObligationSpec(
                "Check projector normalization and local-orbital basis definitions.",
                "definition_check",
                "open",
                "Record the projector convention and its effect on G_loc and local polarization.",
                ["definition anchors", "basis convention"],
            ),
            CuratedObligationSpec(
                "Verify the cRPA/W_loc sign convention used in W_loc = (1 - chi_loc U)^-1 U.",
                "algebra_check",
                "open",
                "Cross-check the polarization sign against registered primary sources.",
                ["primary-source equation anchors", "limiting-case table"],
            ),
            CuratedObligationSpec(
                "Derive and validate the local GW/Hartree double-counting subtraction before candidate formation.",
                "double_counting_derivation",
                "open",
                "Compare Sigma_imp - Sigma_DC + epsilon_H_DC with primary references and limiting cases.",
                ["Matsubara derivation", "limiting-case validation"],
            ),
        ],
        validation_checks=[
            "primary source cross-map",
            "Matsubara sign/frequency convention alignment",
            "projector normalization check",
            "local GW and Hartree double-counting limiting cases",
        ],
        validation_failure_modes=[
            "slide_deck_overtrusted",
            "qsgw_dmft_and_gw_edmft_mixed",
            "double_counting_sign_error",
            "projector_normalization_error",
        ],
        validation_outputs=["evidence_or_provenance", "minimal_check", "failure_mode"],
        sensemaking_title="GW+DMFT v5 framing status",
        sensemaking_summary=(
            "The topic is now represented as a v5 framing claim with explicit open obligations. "
            "Its next action is convention/source work, not an L3 candidate or L2 memory write."
        ),
        next_actions=[
            "read the five registered primary sources",
            "cross-map slide bibliography keys to exact source records",
            "derive Matsubara local GW double-counting and limiting cases",
        ],
    ),
}


def _spec_for_topic(topic_id: str) -> CuratedTopicSpec:
    try:
        return _CURATED_SPECS[topic_id]
    except KeyError as exc:
        known = ", ".join(known_curated_legacy_topics())
        raise ValueError(f"no curated v5 migration spec for topic {topic_id!r}; known: {known}") from exc
