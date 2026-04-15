#!/usr/bin/env python
"""Shared closure audit for cross-runtime deep-execution parity."""

from __future__ import annotations

import argparse
import copy
import json
import tempfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

from run_runtime_parity_acceptance import (
    KERNEL_ROOT,
    REPO_ROOT,
    claude_probe_payload,
    codex_baseline_payload,
    opencode_probe_payload,
)


RUNTIME_ORDER = ("codex", "claude_code", "opencode")
PARITY_TARGETS = ("claude_code", "opencode")
LIVE_EVIDENCE_REQUIRED_CHECKS = (
    "bootstrap_consumed_before_first_substantive_action",
    "human_interaction_posture_visible",
    "autonomy_posture_visible",
    "wait_state_matches_contract",
    "continue_state_matches_contract",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", default=str(KERNEL_ROOT))
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--work-root")
    parser.add_argument("--live-evidence-root")
    parser.add_argument("--json", action="store_true")
    return parser


def _artifact_labels(report: dict[str, Any]) -> set[str]:
    return {
        str(row.get("label") or "").strip()
        for row in (report.get("checked_artifacts") or [])
        if str(row.get("label") or "").strip()
    }


def _live_first_turn_schema_path() -> Path:
    return Path(__file__).resolve().parents[1] / "schemas" / "runtime-live-first-turn-evidence.schema.json"


def _load_live_first_turn_schema() -> dict[str, Any]:
    return json.loads(_live_first_turn_schema_path().read_text(encoding="utf-8"))


def _validate_live_first_turn_evidence(payload: dict[str, Any], *, expected_runtime: str) -> dict[str, Any]:
    Draft202012Validator(_load_live_first_turn_schema()).validate(payload)
    runtime = str(payload.get("runtime") or "").strip()
    if runtime != expected_runtime:
        raise ValueError(f"live evidence runtime mismatch: expected {expected_runtime}, got {runtime or '(empty)'}")
    if str(payload.get("status") or "") == "verified":
        checks = payload.get("checks") or {}
        missing = [name for name in LIVE_EVIDENCE_REQUIRED_CHECKS if checks.get(name) is not True]
        if missing:
            joined = ", ".join(missing)
            raise ValueError(f"verified live evidence for {expected_runtime} is missing passing checks: {joined}")
    return payload


def load_live_first_turn_evidence(*, live_evidence_root: Path | None) -> dict[str, dict[str, Any]]:
    if live_evidence_root is None:
        return {}

    evidence_by_runtime: dict[str, dict[str, Any]] = {}
    for runtime in PARITY_TARGETS:
        evidence_path = live_evidence_root / f"{runtime}.live-first-turn.json"
        if not evidence_path.exists():
            continue
        payload = json.loads(evidence_path.read_text(encoding="utf-8"))
        validated_payload = _validate_live_first_turn_evidence(payload, expected_runtime=runtime)
        validated_payload["_evidence_path"] = str(evidence_path)
        evidence_by_runtime[runtime] = validated_payload
    return evidence_by_runtime


def _apply_live_first_turn_evidence(
    reports: dict[str, dict[str, Any]],
    *,
    live_first_turn_evidence: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    evidence_by_runtime = live_first_turn_evidence or {}
    normalized_reports = copy.deepcopy(reports)
    for runtime in PARITY_TARGETS:
        evidence = evidence_by_runtime.get(runtime)
        if not evidence or str(evidence.get("status") or "") != "verified":
            continue
        report = normalized_reports[runtime]
        report["bounded_probe_status"] = report.get("status")
        report["status"] = "parity_verified"
        report["blockers"] = []
        report["falls_short_of_codex_baseline"] = []
        report["live_first_turn_evidence"] = evidence
    return normalized_reports


def build_cross_runtime_parity_audit(
    reports: dict[str, dict[str, Any]],
    *,
    live_first_turn_evidence: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    normalized_reports = _apply_live_first_turn_evidence(
        reports,
        live_first_turn_evidence=live_first_turn_evidence,
    )
    baseline = normalized_reports["codex"]
    claude_report = normalized_reports["claude_code"]
    opencode_report = normalized_reports["opencode"]
    status_by_runtime = {
        runtime: str((report or {}).get("status") or "unknown")
        for runtime, report in normalized_reports.items()
    }

    equivalent_surfaces: list[dict[str, Any]] = []
    if all(bool((normalized_reports[runtime].get("bootstrap_receipt") or {}).get("contains_using_aitp")) for runtime in PARITY_TARGETS):
        equivalent_surfaces.append(
            {
                "surface": "native_bootstrap_receipt",
                "summary": "Claude Code and OpenCode both produce a native bootstrap receipt that injects `using-aitp` before the bounded AITP runtime lane begins.",
                "supporting_runtimes": list(PARITY_TARGETS),
            }
        )

    core_artifact_labels = {"topic_state", "loop_state", "session_runtime_protocol", "status_runtime_protocol"}
    if core_artifact_labels.issubset(_artifact_labels(claude_report)) and core_artifact_labels.issubset(_artifact_labels(opencode_report)):
        equivalent_surfaces.append(
            {
                "surface": "bounded_runtime_artifacts",
                "summary": "Claude Code and OpenCode both reach the same bounded AITP runtime artifact family that the Codex baseline expects: topic state, loop state, and runtime protocol surfaces.",
                "supporting_runtimes": list(RUNTIME_ORDER),
            }
        )

    if all(str(normalized_reports[runtime].get("load_profile") or "") == "light" for runtime in RUNTIME_ORDER):
        equivalent_surfaces.append(
            {
                "surface": "light_profile_continuity",
                "summary": "Codex, Claude Code, and OpenCode all preserve the bounded light runtime profile for the shared topic probe.",
                "supporting_runtimes": list(RUNTIME_ORDER),
            }
        )

    if all(bool((normalized_reports[runtime].get("status_payload") or {}).get("selected_action_id")) for runtime in RUNTIME_ORDER):
        equivalent_surfaces.append(
            {
                "surface": "bounded_next_action_visibility",
                "summary": "All three runtimes preserve a bounded `selected_action_id` through `status`, so the next action remains explicit after bootstrap and loop materialization.",
                "supporting_runtimes": list(RUNTIME_ORDER),
            }
        )

    if all(
        bool((((normalized_reports[runtime].get("posture_contracts") or {}).get("status")) or {}).get("human_interaction_posture_present"))
        and bool((((normalized_reports[runtime].get("posture_contracts") or {}).get("status")) or {}).get("autonomy_posture_present"))
        for runtime in RUNTIME_ORDER
    ):
        equivalent_surfaces.append(
            {
                "surface": "status_posture_contracts",
                "summary": "Codex, Claude Code, and OpenCode all expose human-control posture plus autonomous-continuation posture through the machine-readable status surface.",
                "supporting_runtimes": list(RUNTIME_ORDER),
            }
        )

    verified_live_evidence = [
        runtime
        for runtime in PARITY_TARGETS
        if str(((live_first_turn_evidence or {}).get(runtime) or {}).get("status") or "") == "verified"
    ]
    if set(verified_live_evidence) == set(PARITY_TARGETS):
        equivalent_surfaces.append(
            {
                "surface": "live_first_turn_bootstrap_consumption",
                "summary": "Claude Code and OpenCode both carry verified live first-turn evidence showing that bootstrap context is consumed before the first substantive agent action and that the human-control posture contract stays visible.",
                "supporting_runtimes": list(PARITY_TARGETS),
            }
        )

    degraded_surface_by_runtime = {
        "claude_code": "Claude Code is still verified through the SessionStart receipt plus downstream runtime artifacts, not through one live Claude Code first-turn proof.",
        "opencode": "OpenCode is still verified through direct plugin-hook execution plus downstream runtime artifacts, not through one live restarted OpenCode first-turn proof.",
    }
    degraded_surfaces = [
        {
            "runtime": runtime,
            "surface": "live_first_turn_bootstrap_consumption",
            "summary": degraded_surface_by_runtime[runtime],
        }
        for runtime in PARITY_TARGETS
        if str(normalized_reports[runtime].get("status") or "") != "parity_verified"
    ]

    open_gaps = [
        {
            "runtime": runtime,
            "blockers": list(normalized_reports[runtime].get("blockers") or []),
            "falls_short_of_codex_baseline": list(normalized_reports[runtime].get("falls_short_of_codex_baseline") or []),
        }
        for runtime in PARITY_TARGETS
        if list(normalized_reports[runtime].get("blockers") or [])
        or list(normalized_reports[runtime].get("falls_short_of_codex_baseline") or [])
    ]

    audit_status = "audited_with_open_gaps" if open_gaps else "parity_verified"
    return {
        "report_kind": "cross_runtime_parity_audit",
        "status": audit_status,
        "baseline_runtime": "codex",
        "baseline_status": str(baseline.get("status") or "unknown"),
        "parity_targets": list(PARITY_TARGETS),
        "status_by_runtime": status_by_runtime,
        "equivalent_surfaces": equivalent_surfaces,
        "degraded_surfaces": degraded_surfaces,
        "open_gaps": open_gaps,
        "live_first_turn_evidence": {
            runtime: (live_first_turn_evidence or {}).get(runtime)
            for runtime in PARITY_TARGETS
            if (live_first_turn_evidence or {}).get(runtime)
        },
        "notes": [
            "This is the closure report for v1.67 cross-runtime deep-execution parity.",
            "The milestone closes on honest bounded evidence rather than on an overclaimed full live-app parity assertion.",
        ],
        "runtime_reports": normalized_reports,
    }


def run_cross_runtime_parity_audit(
    *,
    package_root: Path,
    repo_root: Path,
    work_root: Path,
    live_evidence_root: Path | None = None,
) -> dict[str, Any]:
    reports = {
        "codex": codex_baseline_payload(package_root=package_root, repo_root=repo_root, work_root=work_root / "codex"),
        "claude_code": claude_probe_payload(package_root=package_root, repo_root=repo_root, work_root=work_root / "claude_code"),
        "opencode": opencode_probe_payload(package_root=package_root, repo_root=repo_root, work_root=work_root / "opencode"),
    }
    live_first_turn_evidence = load_live_first_turn_evidence(live_evidence_root=live_evidence_root)
    audit = build_cross_runtime_parity_audit(
        reports,
        live_first_turn_evidence=live_first_turn_evidence,
    )
    audit["work_root"] = str(work_root)
    if live_evidence_root is not None:
        audit["live_evidence_root"] = str(live_evidence_root)
    return audit


def main() -> int:
    args = build_parser().parse_args()
    package_root = Path(args.package_root).expanduser().resolve()
    repo_root = Path(args.repo_root).expanduser().resolve()
    work_root = (
        Path(args.work_root).expanduser().resolve()
        if args.work_root
        else Path(tempfile.mkdtemp(prefix="aitp-runtime-parity-audit-")).resolve()
    )
    live_evidence_root = (
        Path(args.live_evidence_root).expanduser().resolve()
        if args.live_evidence_root
        else None
    )
    payload = run_cross_runtime_parity_audit(
        package_root=package_root,
        repo_root=repo_root,
        work_root=work_root,
        live_evidence_root=live_evidence_root,
    )

    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(
            "runtime parity audit\n"
            f"status: {payload['status']}\n"
            f"baseline: {payload['baseline_runtime']}={payload['baseline_status']}\n"
            f"open_gaps: {len(payload['open_gaps'])}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
