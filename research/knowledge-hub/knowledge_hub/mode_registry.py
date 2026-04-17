"""Single source of truth for AITP runtime mode names.

The new 3-mode system (explore / learn / implement) replaces the old 4-mode
system (discussion / explore / verify / promote).  All other modules import
constants and helpers from here instead of hard-coding mode strings.

Key protocol rule (ME1): "L2 promotion is NOT a separate mode.  It is an
operation triggered within learn or implement."
"""

from __future__ import annotations

from typing import Any

# ── Canonical mode names (protocol-aligned) ────────────────────────────

VALID_RUNTIME_MODES: frozenset[str] = frozenset({"explore", "learn", "implement"})

DEFAULT_RUNTIME_MODE: str = "explore"

# ── Sub-modes per canonical mode ────────────────────────────────────────

SUBMODES: dict[str, frozenset[str]] = {
    "learn": frozenset({"derivation", "numerical"}),
    "implement": frozenset({"code", "formal", "experimental"}),
}

ALL_VALID_SUBMODES: frozenset[str] = frozenset(
    s for subset in SUBMODES.values() for s in subset
)

# ── Legacy → canonical mapping ─────────────────────────────────────────

_LEGACY_MODE_MAP: dict[str, str] = {
    "discussion": "explore",
    "verify": "learn",
    "promote": "implement",
}

# ── Declared-state mapping (protocol manifest states) ───────────────────

VALID_DECLARED_STATES: frozenset[str] = frozenset({
    "bootstrapped",
    "exploring",
    "learning",
    "implementing",
    "completed",
})

_MODE_TO_DECLARED_STATE: dict[str, str] = {
    "explore": "exploring",
    "learn": "learning",
    "implement": "implementing",
}

# ── Operation signals (NOT modes, but action categories) ────────────────

VERIFY_OPERATION_SIGNALS: frozenset[str] = frozenset({
    "select_validation_route",
    "materialize_execution_task",
    "dispatch_execution_task",
    "await_execution_result",
    "ingest_execution_result",
    "prepare_lean_bridge",
    "review_proof_repair_plan",
})

PROMOTE_OPERATION_SIGNALS: frozenset[str] = frozenset({
    "l2_promotion_review",
    "request_promotion",
    "approve_promotion",
    "reject_promotion",
    "promote_candidate",
    "auto_promote_candidate",
})

VERIFY_TRIGGERS: frozenset[str] = frozenset({
    "verification_route_selection",
    "proof_completion_review",
    "contradiction_detected",
})

# ── Helpers ─────────────────────────────────────────────────────────────


def normalize_runtime_mode(mode: Any) -> str:
    """Return a canonical mode name, mapping legacy names to new ones.

    Returns DEFAULT_RUNTIME_MODE ("explore") for unknown or empty values.
    """
    raw = str(mode or "").strip().lower()
    if raw in VALID_RUNTIME_MODES:
        return raw
    if raw in _LEGACY_MODE_MAP:
        return _LEGACY_MODE_MAP[raw]
    return DEFAULT_RUNTIME_MODE


def declared_state_for_mode(mode: str) -> str:
    """Map a canonical mode to its declared state for protocol manifest."""
    return _MODE_TO_DECLARED_STATE.get(normalize_runtime_mode(mode), "exploring")


def is_verify_operation(action_type: str) -> bool:
    """True when the action type is a verification operation."""
    return action_type in VERIFY_OPERATION_SIGNALS


def is_promote_operation(action_type: str) -> bool:
    """True when the action type is a promotion operation."""
    return action_type in PROMOTE_OPERATION_SIGNALS


def has_verify_signals(*, action_type: str = "", triggers: set[str] | None = None) -> bool:
    """True when any verification signal is present."""
    if action_type in VERIFY_OPERATION_SIGNALS:
        return True
    if triggers and bool(triggers & VERIFY_TRIGGERS):
        return True
    return False


def has_promote_signals(*, action_type: str = "", triggers: set[str] | None = None) -> bool:
    """True when any promotion signal is present."""
    if action_type in PROMOTE_OPERATION_SIGNALS:
        return True
    return False
