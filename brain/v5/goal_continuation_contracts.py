"""Contracts for goal continuation audit packets."""

from __future__ import annotations

from typing import Any


def require_valid_goal_continuation_packet(payload: dict[str, Any]) -> dict[str, Any]:
    assert payload.get("kind") == "goal_continuation_packet"
    assert payload.get("orientation_only") is True
    assert payload.get("can_update_claim_trust") is False
    assert payload.get("can_update_kernel_state") is False
    assert "packet_id" in payload
    assert "files" in payload
    return payload
