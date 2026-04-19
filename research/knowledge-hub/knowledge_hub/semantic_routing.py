from __future__ import annotations

from .lane_contract_defaults import (
    full_lane_config,
    research_mode_to_template_mode_map,
)


def _normalize(value: str | None) -> str:
    return str(value or "").strip().lower()


LANES = {
    "formal_theory",
    "toy_numeric",
    "first_principles",
    "theory_synthesis",
    "code_method",
}


def canonical_template_mode(research_mode: str | None) -> str:
    return research_mode_to_template_mode_map().get(
        _normalize(research_mode), "code_method"
    )


def canonical_lane(*, template_mode: str | None, research_mode: str | None) -> str:
    cfg = full_lane_config()
    rm = _normalize(research_mode)
    if rm:
        mapping = cfg.get("research_mode_to_lane") or {}
        if rm in mapping:
            return mapping[rm]
        if rm != "exploratory_general":
            return "code_method"
    tm = _normalize(template_mode)
    if tm == "formal_theory":
        return "formal_theory"
    if tm == "toy_numeric":
        return "toy_numeric"
    return "code_method"


def canonical_validation_mode(template_mode: str | None, research_mode: str | None) -> str:
    cfg = full_lane_config()
    rm = _normalize(research_mode)
    if rm:
        mapping = cfg.get("research_mode_to_validation_mode") or {}
        if rm in mapping:
            return mapping[rm]
    tm = _normalize(template_mode)
    if tm == "formal_theory":
        return "formal"
    if tm == "toy_numeric":
        return "numerical"
    return "hybrid"
