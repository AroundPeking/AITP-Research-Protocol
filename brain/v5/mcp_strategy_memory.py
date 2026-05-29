"""MCP wrappers for topic-local strategy memory."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from brain.v5.public_surfaces import require_valid_public_surface
from brain.v5.strategy_memory import record_strategy_memory
from brain.v5.workspace import init_workspace


def _ws(base: str):
    return init_workspace(Path(base))


def aitp_v5_record_strategy_memory(
    base: str, *, topic_id: str, run_id: str, strategy_type: str, outcome: str,
    lesson: str, next_time_rule: str, scope: str = "",
    source_refs: list[str] | None = None, status: str = "active",
) -> dict:
    memory = record_strategy_memory(
        _ws(base),
        topic_id=topic_id,
        run_id=run_id,
        strategy_type=strategy_type,
        outcome=outcome,
        lesson=lesson,
        next_time_rule=next_time_rule,
        scope=scope,
        source_refs=source_refs,
        status=status,
    )
    return require_valid_public_surface("strategy_memory_record", {"ok": True, **asdict(memory)})
