#!/usr/bin/env python
"""Acceptance for a real natural-language dialogue into the toy-model lane."""

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


TOPIC_TITLE = "Fresh HS-like chaos-window finite-size core"
TOPIC_SLUG = "fresh-hs-like-chaos-window-finite-size-core"
TARGET_UNIT_ID = "claim:hs-like-chaos-window-finite-size-core"
QUESTION_TEXT = (
    "Help me study one bounded HS-like chaos-window toy-model result through "
    "the public AITP front door, and keep the route tied to the already-proved "
    "finite-size positive core instead of widening into the weak shoulder or "
    "the exact HS negative comparator."
)
HUMAN_REQUEST = (
    "Open a fresh toy-model topic for the HS-like finite-size chaos-window "
    "core, keep the public route bounded to the benchmark-backed positive "
    "finite-size core, and leave the exact HS OTOC mismatch route explicit as "
    "a negative comparator."
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", default=str(KERNEL_ROOT))
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--work-root")
    parser.add_argument("--updated-by", default="toy-model-real-topic-dialogue-acceptance")
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
        else Path(tempfile.mkdtemp(prefix="trtd-")).resolve()
    )

    positive_script = package_root / "runtime" / "scripts" / "run_hs_positive_l2_acceptance.py"
    payload = run_python_json(
        [
            sys.executable,
            str(positive_script),
            "--package-root",
            str(package_root),
            "--repo-root",
            str(repo_root),
            "--work-root",
            str(work_root),
            "--topic",
            TOPIC_TITLE,
            "--question",
            QUESTION_TEXT,
            "--human-request",
            HUMAN_REQUEST,
            "--updated-by",
            args.updated_by,
            "--json",
        ]
    )

    topic_slug = str(payload.get("topic_slug") or "").strip()
    check(
        topic_slug == TOPIC_SLUG,
        "Expected the fresh toy-model topic slug to stay on the bounded HS-like route.",
    )

    runtime_root = work_root / "knowledge-hub" / "runtime" / "topics" / topic_slug
    interaction_state_path = runtime_root / "interaction_state.json"
    research_question_contract_path = runtime_root / "research_question.contract.json"
    runtime_protocol_note_path = runtime_root / "runtime_protocol.generated.md"
    canonical_mirror_path = Path(payload["artifacts"]["canonical_mirror"])

    for path in (
        interaction_state_path,
        research_question_contract_path,
        runtime_protocol_note_path,
        canonical_mirror_path,
    ):
        ensure_exists(path)

    interaction_state_text = interaction_state_path.read_text(encoding="utf-8")
    research_contract_text = research_question_contract_path.read_text(encoding="utf-8")
    runtime_protocol_note = runtime_protocol_note_path.read_text(encoding="utf-8")
    consultation_ids = list((((payload.get("repo_local_l2") or {}).get("consultation") or {}).get("ids") or []))

    check(
        "HS-like" in interaction_state_text or "chaos-window" in interaction_state_text,
        "Expected interaction_state to preserve the real natural-language toy-model request.",
    )
    check(
        "HS-like" in research_contract_text or "chaos-window" in research_contract_text,
        "Expected the research-question contract to preserve the real natural-language toy-model topic.",
    )
    check(
        "toy_model" in runtime_protocol_note or "toy model" in runtime_protocol_note.lower(),
        "Expected the runtime protocol note to reflect the bounded toy-model route.",
    )
    check(
        TARGET_UNIT_ID in consultation_ids,
        "Expected consult_l2 parity to preserve the bounded HS-like positive claim on the real dialogue route.",
    )

    result = {
        "status": "success",
        "topic_slug": topic_slug,
        "dialogue_inputs": {
            "topic": TOPIC_TITLE,
            "question": QUESTION_TEXT,
            "human_request": HUMAN_REQUEST,
        },
        "entry_artifacts": {
            "interaction_state": str(interaction_state_path),
            "research_question_contract": str(research_question_contract_path),
            "runtime_protocol_note": str(runtime_protocol_note_path),
        },
        "target_contract": payload["target_contract"],
        "promotion": payload["promotion"],
        "repo_local_l2": payload["repo_local_l2"],
        "artifacts": payload["artifacts"],
    }
    if args.json:
        print(json.dumps(result, ensure_ascii=True, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
