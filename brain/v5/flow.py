"""Flow profile resolution for AITP v5."""

from __future__ import annotations

from brain.v5.models import ClaimRecord, FlowDecision


_ADVERSARIAL_SIGNALS = (
    "failure",
    "fail",
    "contradiction",
    "conflict",
    "promotion",
    "promote",
    "expensive",
    "publish",
    "trusted memory",
)

_AUTOPILOT_SIGNALS = (
    "routine",
    "rerun",
    "benchmark",
    "trusted",
    "standard",
)


def resolve_flow_profile(claim: ClaimRecord) -> FlowDecision:
    """Choose protocol weight for a claim-local action."""

    uncertainty = claim.active_uncertainty.lower()
    triggers = [signal for signal in _ADVERSARIAL_SIGNALS if signal in uncertainty]
    if triggers:
        return FlowDecision(
            profile="adversarial",
            reason="active uncertainty contains escalation signal",
            escalation_triggers=triggers,
        )

    if claim.recipe_id and any(signal in uncertainty for signal in _AUTOPILOT_SIGNALS):
        return FlowDecision(
            profile="autopilot",
            reason="trusted recipe covers a routine workflow",
            escalation_triggers=[],
        )

    if claim.confidence_state in {"hypothesis", "coherent"}:
        return FlowDecision(
            profile="research",
            reason="claim is still creating or changing physical meaning",
            escalation_triggers=[],
        )

    return FlowDecision(
        profile="guided",
        reason="some physics judgment is needed but no escalation trigger fired",
        escalation_triggers=[],
    )
