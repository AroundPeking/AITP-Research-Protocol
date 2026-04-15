#!/usr/bin/env python
"""Acceptance for HS positive/negative coexistence on repo-local L2 surfaces."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
KERNEL_ROOT = SCRIPT_PATH.parents[2]
REPO_ROOT = SCRIPT_PATH.parents[4]

if str(KERNEL_ROOT) not in sys.path:
    sys.path.insert(0, str(KERNEL_ROOT))

from knowledge_hub.aitp_service import AITPService  # noqa: E402


POSITIVE_UNIT_ID = "claim:hs-like-chaos-window-finite-size-core"
NEGATIVE_ENTRY_ID = "staging:hs-model-otoc-lyapunov-exponent-regime-mismatch"
COEXISTENCE_QUERY = (
    "HS-like finite-size chaos window robust core OTOC Lyapunov exponent regime mismatch"
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", default=str(KERNEL_ROOT))
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--work-root")
    parser.add_argument(
        "--updated-by",
        default="hs-positive-negative-coexistence-acceptance",
    )
    parser.add_argument("--json", action="store_true")
    return parser


def ensure_exists(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Expected artifact is missing: {path}")


def check(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_python_json(command: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
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
        else Path(tempfile.mkdtemp(prefix="hspn-")).resolve()
    )
    kernel_root = work_root / "knowledge-hub"

    positive_script = package_root / "runtime" / "scripts" / "run_hs_positive_l2_acceptance.py"
    positive_payload = run_python_json(
        [
            sys.executable,
            str(positive_script),
            "--package-root",
            str(package_root),
            "--repo-root",
            str(repo_root),
            "--work-root",
            str(work_root),
            "--updated-by",
            args.updated_by,
            "--json",
        ]
    )

    service = AITPService(kernel_root=kernel_root, repo_root=repo_root)
    compile_map_payload = service.compile_l2_workspace_map()
    compile_graph_payload = service.compile_l2_graph_report()
    compile_report_payload = service.compile_l2_knowledge_report()
    consult_payload = service.consult_l2(
        query_text=COEXISTENCE_QUERY,
        retrieval_profile="l4_adjudication",
        include_staging=True,
        max_primary_hits=8,
    )

    knowledge_rows = {
        str(row.get("knowledge_id") or "").strip(): row
        for row in (compile_report_payload.get("payload") or {}).get("knowledge_rows", [])
    }
    positive_row = knowledge_rows.get(POSITIVE_UNIT_ID) or {}
    negative_row = knowledge_rows.get(NEGATIVE_ENTRY_ID) or {}
    canonical_ids = sorted(
        {
            str(row.get("id") or "").strip()
            for row in [
                *(consult_payload.get("primary_hits") or []),
                *(consult_payload.get("expanded_hits") or []),
            ]
            if str(row.get("id") or "").strip()
        }
    )
    staged_ids = sorted(
        {
            str(row.get("entry_id") or "").strip()
            for row in (consult_payload.get("staged_hits") or [])
            if str(row.get("entry_id") or "").strip()
        }
    )

    check(
        positive_row.get("authority_level") == "authoritative_canonical",
        "Expected HS positive row to stay authoritative.",
    )
    check(
        positive_row.get("knowledge_state") == "trusted",
        "Expected HS positive row to stay trusted.",
    )
    check(
        negative_row.get("authority_level") == "non_authoritative_staging",
        "Expected HS negative row to stay staging.",
    )
    check(
        negative_row.get("knowledge_state") == "contradiction_watch",
        "Expected HS negative row to compile as contradiction_watch.",
    )
    check(
        bool(positive_row.get("provenance_refs") or []),
        "Expected HS positive row provenance refs to remain populated.",
    )
    check(
        bool(negative_row.get("provenance_refs") or []),
        "Expected HS negative row provenance refs to remain populated.",
    )
    check(
        POSITIVE_UNIT_ID in canonical_ids,
        "Expected consultation to surface the authoritative HS positive row.",
    )
    check(
        NEGATIVE_ENTRY_ID in staged_ids,
        "Expected consultation staged hits to surface the HS negative row.",
    )

    negative_entry_path = (
        kernel_root
        / "canonical"
        / "staging"
        / "entries"
        / "staging--hs-model-otoc-lyapunov-exponent-regime-mismatch.json"
    )
    report_json_path = Path(compile_report_payload["json_path"])
    report_markdown_path = Path(compile_report_payload["markdown_path"])
    for path in (
        negative_entry_path,
        report_json_path,
        report_markdown_path,
        Path(compile_map_payload["json_path"]),
        Path(compile_graph_payload["json_path"]),
        Path(positive_payload["promotion"]["canonical_mirror_path"]),
    ):
        ensure_exists(path)

    payload = {
        "status": "success",
        "work_root": str(work_root),
        "kernel_root": str(kernel_root),
        "positive_acceptance": {
            "topic_slug": positive_payload["topic_slug"],
            "run_id": positive_payload["run_id"],
            "target_unit_id": POSITIVE_UNIT_ID,
            "canonical_mirror_path": positive_payload["promotion"]["canonical_mirror_path"],
            "workspace_knowledge_report": positive_payload["repo_local_l2"]["workspace_knowledge_report"]["json_path"],
        },
        "negative_result": {
            "entry_id": NEGATIVE_ENTRY_ID,
            "entry_json_path": str(negative_entry_path),
        },
        "knowledge_report": {
            "json_path": str(report_json_path),
            "markdown_path": str(report_markdown_path),
            "positive_row": positive_row,
            "negative_row": negative_row,
        },
        "consultation": {
            "query_text": COEXISTENCE_QUERY,
            "retrieval_profile": "l4_adjudication",
            "canonical_ids": canonical_ids,
            "staged_ids": staged_ids,
        },
        "compiled_reports": {
            "workspace_memory_map": compile_map_payload["json_path"],
            "workspace_graph_report": compile_graph_payload["json_path"],
            "workspace_knowledge_report": str(report_json_path),
        },
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=True, indent=2))
    else:
        print(json.dumps(payload, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
