"""Run-local strategy memory for reusable topic workflow lessons."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from brain.v5.ids import prefixed_id
from brain.v5.paths import WorkspacePaths

_STRATEGY_TYPES = {"search_route", "verification_guardrail", "debug_pattern", "resource_plan", "scope_control"}
_OUTCOMES = {"helped", "failed", "neutral"}


@dataclass
class StrategyMemoryRecord:
    memory_id: str
    topic_id: str
    run_id: str
    strategy_type: str
    outcome: str
    lesson: str
    next_time_rule: str
    scope: str = ""
    source_refs: list[str] = field(default_factory=list)
    status: str = "active"
    summary_inputs_trusted: bool = False
    can_update_claim_trust: bool = False
    kind: str = "strategy_memory"


def record_strategy_memory(
    ws: WorkspacePaths,
    *,
    topic_id: str,
    run_id: str,
    strategy_type: str,
    outcome: str,
    lesson: str,
    next_time_rule: str,
    scope: str = "",
    source_refs: list[str] | None = None,
    status: str = "active",
) -> StrategyMemoryRecord:
    """Append a non-promotional strategy lesson to the topic's run-local ledger."""

    if strategy_type not in _STRATEGY_TYPES:
        raise ValueError(f"strategy_type must be one of {sorted(_STRATEGY_TYPES)}")
    if outcome not in _OUTCOMES:
        raise ValueError(f"outcome must be one of {sorted(_OUTCOMES)}")
    if status not in {"active", "superseded", "archived"}:
        raise ValueError("strategy memory status must be active, superseded, or archived")
    record = StrategyMemoryRecord(
        memory_id=prefixed_id("strategy-memory", f"{topic_id}:{run_id}:{strategy_type}:{lesson}", max_slug=72),
        topic_id=topic_id,
        run_id=run_id,
        strategy_type=strategy_type,
        outcome=outcome,
        lesson=lesson,
        next_time_rule=next_time_rule,
        scope=scope,
        source_refs=source_refs or [],
        status=status,
    )
    path = _run_strategy_memory_path(ws, topic_id, run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(record), ensure_ascii=False, sort_keys=True) + "\n")
    return record


def load_strategy_memory(ws: WorkspacePaths, topic_id: str, *, limit: int = 8) -> dict[str, Any]:
    """Return recent topic-local strategy memory for execution briefs."""

    run_root = ws.topic_dir(topic_id) / "L3" / "runs"
    if not run_root.exists():
        return {"present": False, "items": [], "summary_inputs_trusted": False, "can_update_claim_trust": False}
    items: list[dict[str, Any]] = []
    for path in sorted(run_root.glob("*/strategy_memory.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            item = json.loads(line)
            if item.get("status") == "active":
                items.append(_brief_item(item, path))
    items = items[-limit:]
    return {
        "present": bool(items),
        "items": items,
        "summary_inputs_trusted": False,
        "can_update_claim_trust": False,
    }


def _run_strategy_memory_path(ws: WorkspacePaths, topic_id: str, run_id: str) -> Path:
    return ws.topic_dir(topic_id) / "L3" / "runs" / run_id / "strategy_memory.jsonl"


def _brief_item(item: dict[str, Any], path: Path) -> dict[str, Any]:
    return {
        "memory_id": str(item.get("memory_id") or ""),
        "run_id": str(item.get("run_id") or ""),
        "strategy_type": str(item.get("strategy_type") or ""),
        "outcome": str(item.get("outcome") or ""),
        "lesson": str(item.get("lesson") or ""),
        "next_time_rule": str(item.get("next_time_rule") or ""),
        "scope": str(item.get("scope") or ""),
        "source_refs": list(item.get("source_refs") or []),
        "artifact_path": str(path),
        "orientation_only": True,
    }
