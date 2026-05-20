"""Small machine-readable hook runner payload builders."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def build_pre_tool_event_runner(runtime: str, session_id: str, payload_path: str | Path) -> dict[str, Any]:
    path = str(Path(payload_path))
    return {
        "kind": "pre_tool_event_runner",
        "runtime": runtime,
        "session_id": session_id,
        "bridge_payload_source": "payload_path",
        "payload_path": path,
        "platform_event_placeholder": "<platform-event-json>",
        "argv": [
            "aitp-v5",
            "adapter",
            "pre-tool-event",
            runtime,
            session_id,
            "--bridge-path",
            path,
            "--event-json",
            "<platform-event-json>",
        ],
        "truth_source": "typed_records",
        "summary_inputs_trusted": False,
        "can_update_kernel_state": False,
        "can_update_claim_trust": False,
    }
