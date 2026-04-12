#!/usr/bin/env python
"""Shared closure audit for cross-runtime deep-execution parity."""

from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path
from typing import Any

from run_runtime_parity_acceptance import (
    KERNEL_ROOT,
    REPO_ROOT,
    claude_probe_payload,
    codex_baseline_payload,
    opencode_probe_payload,
)


RUNTIME_ORDER = ("codex", "claude_code", "opencode")
PARITY_TARGETS = ("claude_code", "opencode")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", default=str(KERNEL_ROOT))
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--work-root")
    parser.add_argument("--json", action="store_true")
    return parser


def _artifact_labels(report: dict[str, Any]) -> set[str]:
    return {
        str(row.get("label") or "").strip()
        for row in (report.get("checked_artifacts") or [])
        if str(row.get("label") or "").strip()
    }


def build_cross_runtime_parity_audit(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    baseline = reports["codex"]
    claude_report = reports["claude_code"]
    opencode_report = reports["opencode"]
    status_by_runtime = {runtime: str((report or {}).get("status") or "unknown") for runtime, report in reports.items()}

    equivalent_surfaces: list[dict[str, Any]] = []
    if all(bool((reports[runtime].get("bootstrap_receipt") or {}).get("contains_using_aitp")) for runtime in PARITY_TARGETS):
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

    if all(str(reports[runtime].get("load_profile") or "") == "light" for runtime in RUNTIME_ORDER):
        equivalent_surfaces.append(
            {
                "surface": "light_profile_continuity",
                "summary": "Codex, Claude Code, and OpenCode all preserve the bounded light runtime profile for the shared topic probe.",
                "supporting_runtimes": list(RUNTIME_ORDER),
            }
        )

    if all(bool((reports[runtime].get("status_payload") or {}).get("selected_action_id")) for runtime in RUNTIME_ORDER):
        equivalent_surfaces.append(
            {
                "surface": "bounded_next_action_visibility",
                "summary": "All three runtimes preserve a bounded `selected_action_id` through `status`, so the next action remains explicit after bootstrap and loop materialization.",
                "supporting_runtimes": list(RUNTIME_ORDER),
            }
        )

    degraded_surfaces = [
        {
            "runtime": "claude_code",
            "surface": "live_first_turn_bootstrap_consumption",
            "summary": "Claude Code is still verified through the SessionStart receipt plus downstream runtime artifacts, not through one live Claude Code first-turn proof.",
        },
        {
            "runtime": "opencode",
            "surface": "live_first_turn_bootstrap_consumption",
            "summary": "OpenCode is still verified through direct plugin-hook execution plus downstream runtime artifacts, not through one live restarted OpenCode first-turn proof.",
        },
    ]

    open_gaps = [
        {
            "runtime": runtime,
            "blockers": list(reports[runtime].get("blockers") or []),
            "falls_short_of_codex_baseline": list(reports[runtime].get("falls_short_of_codex_baseline") or []),
        }
        for runtime in PARITY_TARGETS
        if list(reports[runtime].get("blockers") or []) or list(reports[runtime].get("falls_short_of_codex_baseline") or [])
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
        "notes": [
            "This is the closure report for v1.67 cross-runtime deep-execution parity.",
            "The milestone closes on honest bounded evidence rather than on an overclaimed full live-app parity assertion.",
        ],
        "runtime_reports": reports,
    }


def run_cross_runtime_parity_audit(*, package_root: Path, repo_root: Path, work_root: Path) -> dict[str, Any]:
    reports = {
        "codex": codex_baseline_payload(package_root=package_root, repo_root=repo_root, work_root=work_root / "codex"),
        "claude_code": claude_probe_payload(package_root=package_root, repo_root=repo_root, work_root=work_root / "claude_code"),
        "opencode": opencode_probe_payload(package_root=package_root, repo_root=repo_root, work_root=work_root / "opencode"),
    }
    audit = build_cross_runtime_parity_audit(reports)
    audit["work_root"] = str(work_root)
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
    payload = run_cross_runtime_parity_audit(package_root=package_root, repo_root=repo_root, work_root=work_root)

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
