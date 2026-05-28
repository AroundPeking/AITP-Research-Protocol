"""MCP wrappers for goal continuation audit packets."""

from __future__ import annotations

import json as _json

from brain.v5.goal_continuation import (
    list_goal_continuations,
    read_latest_goal_continuation,
    write_goal_continuation,
)
from brain.v5.public_surfaces import require_valid_public_surface


def _csv(value: str) -> list[str]:
    return [s.strip() for s in value.split(",") if s.strip()]


def _bool_or_none(value: str) -> bool | None:
    if not value:
        return None
    return value.lower() in ("true", "1", "yes")


def _ws(base: str):
    from brain.v5.workspace import init_workspace
    return init_workspace(base)


def aitp_v5_write_goal_continuation(
    base: str, *, objective: str, changed_files: str = "", tests_run: str = "",
    tests_passed: str = "", smoke_commands: str = "", smoke_passed: str = "",
    readiness_json: str = "{}", next_actions: str = "", trust_boundary: str = "",
    blocking_backlog: str = "", notes: str = "", session_id: str = "",
    commit_ref: str = "",
) -> dict:
    readiness = {}
    if readiness_json and readiness_json != "{}":
        readiness = _json.loads(readiness_json)
    return require_valid_public_surface("goal_continuation_packet", write_goal_continuation(
        _ws(base), objective=objective,
        changed_files=_csv(changed_files),
        tests_run=_csv(tests_run),
        tests_passed=_bool_or_none(tests_passed),
        smoke_commands=_csv(smoke_commands),
        smoke_passed=_bool_or_none(smoke_passed),
        readiness_outcome=readiness or None,
        next_actions=_csv(next_actions),
        trust_boundary=trust_boundary,
        blocking_backlog=_csv(blocking_backlog),
        notes=notes, session_id=session_id, commit_ref=commit_ref,
    ))


def aitp_v5_read_latest_goal_continuation(base: str) -> dict:
    result = read_latest_goal_continuation(_ws(base))
    if result is None:
        return {"kind": "goal_continuation_packet", "found": False}
    return result


def aitp_v5_list_goal_continuations(base: str) -> dict:
    packets = list_goal_continuations(_ws(base))
    return {
        "kind": "goal_continuation_list",
        "count": len(packets),
        "packet_ids": [p.get("packet_id", "") for p in packets],
        "latest_objectives": [
            {"packet_id": p.get("packet_id", ""), "objective": (p.get("objective") or "")[:120]}
            for p in packets[-5:]
        ],
    }
