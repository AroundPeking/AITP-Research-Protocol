#!/usr/bin/env python
"""Isolated acceptance for the compiled L2 knowledge report surface."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
KERNEL_ROOT = SCRIPT_PATH.parents[2]
REPO_ROOT = SCRIPT_PATH.parents[4]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", default=str(KERNEL_ROOT))
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--work-root")
    parser.add_argument("--json", action="store_true")
    return parser


def ensure_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Expected artifact is missing: {path}")


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_cli_json(*, package_root: Path, kernel_root: Path, repo_root: Path, args: list[str]) -> dict[str, Any]:
    command = [
        sys.executable,
        "-m",
        "knowledge_hub.aitp_cli",
        "--kernel-root",
        str(kernel_root),
        "--repo-root",
        str(repo_root),
        *args,
    ]
    completed = subprocess.run(
        command,
        cwd=package_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "unknown error"
        raise RuntimeError(f"{' '.join(command)} failed: {detail}")
    return json.loads(completed.stdout)


def main() -> int:
    args = build_parser().parse_args()
    package_root = Path(args.package_root).expanduser().resolve()
    repo_root = Path(args.repo_root).expanduser().resolve()
    work_root = (
        Path(args.work_root).expanduser().resolve()
        if args.work_root
        else Path(tempfile.mkdtemp(prefix="aitp-l2-knowledge-report-acceptance-")).resolve()
    )
    kernel_root = work_root / "kernel"
    shutil.copytree(package_root / "canonical", kernel_root / "canonical", dirs_exist_ok=True)
    shutil.copytree(package_root / "schemas", kernel_root / "schemas", dirs_exist_ok=True)
    shutil.copytree(package_root / "runtime" / "scripts", kernel_root / "runtime" / "scripts", dirs_exist_ok=True)
    (kernel_root / "runtime" / "schemas").mkdir(parents=True, exist_ok=True)
    bundle_schema = package_root / "runtime" / "schemas" / "progressive-disclosure-runtime-bundle.schema.json"
    (kernel_root / "runtime" / "schemas" / bundle_schema.name).write_text(
        bundle_schema.read_text(encoding="utf-8"),
        encoding="utf-8",
    )

    unique_suffix = work_root.name
    provisional_title = f"Knowledge report provisional note {unique_suffix}"
    contradiction_title = f"Knowledge report contradiction {unique_suffix}"

    run_cli_json(
        package_root=package_root,
        kernel_root=kernel_root,
        repo_root=repo_root,
        args=["seed-l2-direction", "--direction", "tfim-benchmark-first", "--json"],
    )
    run_cli_json(
        package_root=package_root,
        kernel_root=kernel_root,
        repo_root=repo_root,
        args=[
            "stage-l2-provisional",
            "--topic-slug",
            "demo-topic",
            "--entry-kind",
            "workflow_draft",
            "--title",
            provisional_title,
            "--summary",
            "A provisional reusable workflow draft for the benchmark-first route.",
            "--json",
        ],
    )

    first_payload = run_cli_json(
        package_root=package_root,
        kernel_root=kernel_root,
        repo_root=repo_root,
        args=["compile-l2-knowledge-report", "--json"],
    )

    run_cli_json(
        package_root=package_root,
        kernel_root=kernel_root,
        repo_root=repo_root,
        args=[
            "stage-negative-result",
            "--title",
            contradiction_title,
            "--summary",
            "The provisional benchmark route failed outside the bounded regime.",
            "--failure-kind",
            "regime_mismatch",
            "--json",
        ],
    )

    second_payload = run_cli_json(
        package_root=package_root,
        kernel_root=kernel_root,
        repo_root=repo_root,
        args=["compile-l2-knowledge-report", "--json"],
    )

    first_json = Path(first_payload["json_path"])
    first_md = Path(first_payload["markdown_path"])
    second_json = Path(second_payload["json_path"])
    second_md = Path(second_payload["markdown_path"])
    for path in (first_json, first_md, second_json, second_md):
        ensure_exists(path)
    check(first_json.name == "workspace_knowledge_report.json", "Expected the compiled knowledge report JSON artifact name.")
    check(first_md.name == "workspace_knowledge_report.md", "Expected the compiled knowledge report markdown artifact name.")
    check(second_json.name == "workspace_knowledge_report.json", "Expected the second compiled knowledge report JSON artifact name.")
    check(second_md.name == "workspace_knowledge_report.md", "Expected the second compiled knowledge report markdown artifact name.")

    first_report = first_payload["payload"]
    second_report = second_payload["payload"]
    check(
        first_report["summary"]["canonical_row_count"] >= 9,
        "Expected the knowledge report to include the seeded canonical direction units.",
    )
    check(
        first_report["summary"]["staging_row_count"] >= 1,
        "Expected the knowledge report to include staged provisional knowledge rows.",
    )
    check(
        "workspace_staging_manifest" in first_payload["supporting_artifacts"],
        "Expected the knowledge report to reference the staging manifest.",
    )
    check(
        any(row["authority_level"] == "non_authoritative_staging" for row in first_report["knowledge_rows"]),
        "Expected at least one non-authoritative staging knowledge row.",
    )
    check(
        second_report["change_summary"]["previous_report_found"],
        "Expected the second knowledge-report compile to detect the previous compiled snapshot.",
    )
    check(
        second_report["summary"]["contradiction_row_count"] >= 1,
        "Expected the second knowledge report to surface a contradiction-watch row.",
    )
    check(
        any(
            row["knowledge_state"] == "contradiction_watch"
            and contradiction_title in str(row.get("title") or "")
            for row in second_report["knowledge_rows"]
        ),
        "Expected the staged negative result to appear as a contradiction-watch knowledge row.",
    )

    payload = {
        "status": "success",
        "work_root": str(work_root),
        "kernel_root": str(kernel_root),
        "checks": {
            "first_total_rows": first_report["summary"]["total_rows"],
            "first_staging_rows": first_report["summary"]["staging_row_count"],
            "second_contradiction_rows": second_report["summary"]["contradiction_row_count"],
            "second_added_count": second_report["change_summary"]["added_count"],
            "second_updated_count": second_report["change_summary"]["updated_count"],
            "previous_report_found": second_report["change_summary"]["previous_report_found"],
        },
        "artifacts": {
            "first_json": str(first_json),
            "first_markdown": str(first_md),
            "second_json": str(second_json),
            "second_markdown": str(second_md),
            "staging_manifest": first_payload["supporting_artifacts"]["workspace_staging_manifest"],
            "graph_report": first_payload["supporting_artifacts"]["workspace_graph_report"],
            "knowledge_report_markdown": str(second_md),
        },
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
