from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def build_remediation_tasks(*, topic_slug: str, round_rows: list[dict[str, Any]]) -> dict[str, Any]:
    items: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for round_row in round_rows:
        round_id = str(round_row.get("iteration_id") or "").strip()
        hard_blocks = set(round_row.get("hard_blocking_gaps") or [])
        for missing_block in round_row.get("missing_blocks") or []:
            key = (round_id, str(missing_block))
            if key in seen:
                continue
            seen.add(key)
            items.append(
                {
                    "task_id": f"remediation:{topic_slug}:{round_id}:{missing_block}",
                    "status": "pending",
                    "topic_slug": topic_slug,
                    "source_round_id": round_id,
                    "round_type": round_row.get("round_type"),
                    "missing_block": missing_block,
                    "blocks_claim_use": missing_block in hard_blocks,
                    "recommended_round_type": round_row.get("round_type"),
                    "summary": f"Repair notebook obligation '{missing_block}' for {round_id}.",
                    "expected_writeback_paths": [
                        f"topics/{topic_slug}/runtime/research_report.active.json",
                        f"topics/{topic_slug}/runtime/unfinished_work.json",
                    ],
                }
            )
    return {
        "status": "available",
        "topic_slug": topic_slug,
        "updated_at": _now_iso(),
        "items": items,
    }


def write_remediation_tasks(runtime_root: Path, payload: dict[str, Any]) -> None:
    runtime_root.mkdir(parents=True, exist_ok=True)
    (runtime_root / "remediation_tasks.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (runtime_root / "remediation_tasks.md").write_text(
        "# Remediation Tasks\n\n"
        + ("\n".join(f"- `{item['task_id']}`: {item['summary']}" for item in payload.get("items") or []) or "- (none)")
        + "\n",
        encoding="utf-8",
    )
