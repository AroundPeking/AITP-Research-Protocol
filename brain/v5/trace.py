"""Lightweight trace events for AITP v5 harness audits."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from brain.v5.hook_protocol_contracts import (
    require_valid_hook_trace_event_payload,
    require_valid_hook_trace_event_record,
)


@dataclass
class TraceEvent:
    event_id: str
    session_id: str
    topic_id: str
    event_type: str
    risk_level: str
    claim_id: str = ""
    payload: dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    kind: str = "trace_event"


def append_trace_event(path: str | Path, event: TraceEvent) -> None:
    """Append one JSONL trace event."""

    trace_path = Path(path)
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    with trace_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(asdict(event), ensure_ascii=False, sort_keys=True))
        handle.write("\n")


def hook_trace_event_path(ws) -> Path:
    """Return the runtime trace path for persisted hook output."""

    return ws.root / "runtime" / "hook_trace_events.jsonl"


def persist_hook_trace_event(ws, hook_payload: dict[str, Any]) -> dict[str, Any]:
    """Persist a post-tool hook trace payload without turning it into evidence."""

    valid_payload = require_valid_hook_trace_event_payload(hook_payload)
    event = TraceEvent(**valid_payload["event"])
    trace_path = hook_trace_event_path(ws)
    append_trace_event(trace_path, event)
    record = {
        "ok": True,
        "kind": "hook_trace_event_record",
        "event_id": event.event_id,
        "session_id": event.session_id,
        "topic_id": event.topic_id,
        "claim_id": event.claim_id,
        "event_type": event.event_type,
        "risk_level": event.risk_level,
        "source_kind": valid_payload["kind"],
        "source_hook": valid_payload["hook_name"],
        "trace_path": str(trace_path),
        "summary_inputs_trusted": False,
        "can_update_claim_trust": False,
        "writes_trace_event": True,
    }
    return require_valid_hook_trace_event_record(record)


def read_trace_events(path: str | Path) -> list[TraceEvent]:
    """Read JSONL trace events."""

    trace_path = Path(path)
    if not trace_path.exists():
        return []
    events: list[TraceEvent] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        events.append(TraceEvent(**json.loads(line)))
    return events
