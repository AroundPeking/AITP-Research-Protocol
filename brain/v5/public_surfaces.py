"""Shared validation entrypoints for public AITP v5 surfaces."""

from __future__ import annotations

from typing import Any, Callable

_PUBLIC_SURFACE_NAMES = (
    "adapter_packet",
    "adapter_protocol_registry",
    "execution_brief",
    "session_summary_bundle",
    "summary_orientation",
    "trust_update_apply",
    "trust_update_preflight",
)
_PUBLIC_SURFACE_VALIDATOR_REF = "brain.v5.public_surfaces.require_valid_public_surface"


def public_surface_names() -> tuple[str, ...]:
    """Return the names of public payload surfaces with contract gates."""

    return _PUBLIC_SURFACE_NAMES


def public_surface_validator_ref() -> str:
    """Return the stable import path for validating public payload surfaces."""

    return _PUBLIC_SURFACE_VALIDATOR_REF


def require_valid_public_surface(surface_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Validate a public payload by stable surface name."""

    validator = _validators().get(surface_name)
    if validator is None:
        raise ValueError(f"unknown public surface: {surface_name}")
    return validator(payload)


def _validators() -> dict[str, Callable[[dict[str, Any]], dict[str, Any]]]:
    from brain.v5.contracts import (
        require_valid_adapter_packet,
        require_valid_adapter_protocol_registry,
        require_valid_execution_brief,
        require_valid_session_summary_bundle,
        require_valid_summary_orientation,
        require_valid_trust_update_apply,
        require_valid_trust_update_preflight,
    )

    return {
        "adapter_packet": require_valid_adapter_packet,
        "adapter_protocol_registry": require_valid_adapter_protocol_registry,
        "execution_brief": require_valid_execution_brief,
        "session_summary_bundle": require_valid_session_summary_bundle,
        "summary_orientation": require_valid_summary_orientation,
        "trust_update_apply": require_valid_trust_update_apply,
        "trust_update_preflight": require_valid_trust_update_preflight,
    }
