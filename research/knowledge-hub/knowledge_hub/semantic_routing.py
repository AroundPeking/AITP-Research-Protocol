from __future__ import annotations


LANES = {
    "formal_theory",
    "toy_numeric",
    "first_principles",
    "theory_synthesis",
    "code_method",
}


def _normalize(value: str | None) -> str:
    return str(value or "").strip().lower()


def canonical_template_mode(research_mode: str | None) -> str:
    normalized = _normalize(research_mode)
    mapping = {
        "formal_derivation": "formal_theory",
        "toy_model": "toy_numeric",
        "first_principles": "toy_numeric",
        "theory_synthesis": "code_method",
        "exploratory_general": "code_method",
    }
    return mapping.get(normalized, "code_method")


def canonical_lane(*, template_mode: str | None, research_mode: str | None) -> str:
    normalized_template = _normalize(template_mode)
    normalized_research = _normalize(research_mode)
    if normalized_template == "formal_theory" or normalized_research == "formal_derivation":
        return "formal_theory"
    if normalized_research == "first_principles":
        return "first_principles"
    if normalized_research == "theory_synthesis":
        return "theory_synthesis"
    if normalized_template == "toy_numeric" or normalized_research == "toy_model":
        return "toy_numeric"
    return "code_method"


def canonical_validation_mode(template_mode: str | None, research_mode: str | None) -> str:
    normalized_template = _normalize(template_mode)
    normalized_research = _normalize(research_mode)
    if normalized_template == "formal_theory" or normalized_research == "formal_derivation":
        return "formal"
    if normalized_template == "toy_numeric" or normalized_research in {"toy_model", "first_principles"}:
        return "numerical"
    return "hybrid"
