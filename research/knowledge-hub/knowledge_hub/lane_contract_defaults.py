"""Lane-aware defaults for the active research contract.

When a topic has no human-curated values for observables, target_claims, or
deliverables, the runtime falls back to generic template text that carries zero
physics content.  This module replaces those generic defaults with lane-specific
alternatives derived from ``template_mode``, ``research_mode``, and the topic's
existing content.

All functions are pure — they only read their inputs and return lists of strings.
"""

from __future__ import annotations

from typing import Any


def detect_lane(
    *,
    template_mode: str,
    research_mode: str,
    topic_content_hints: dict[str, Any] | None = None,
) -> str:
    hints = topic_content_hints or {}
    tm = str(template_mode or "").strip().lower()
    if tm == "formal_theory":
        return "formal_derivation"

    rm = str(research_mode or "").strip().lower()
    if tm == "code_method":
        text = _hint_text(hints)
        if _looks_like_toy_model(text):
            return "toy_model"
        if _looks_like_first_principles(text):
            return "first_principles"

    return "generic"


def lane_observables(lane: str, topic_context: dict[str, Any]) -> list[str]:
    question = str((topic_context or {}).get("question") or "").strip()
    ctx = lane

    if ctx == "formal_derivation":
        base = [
            "Formal closure or proof target for the bounded question.",
            "Source theorem dependencies and notation lock status.",
            "Proof obligation completeness versus gap-honesty check.",
        ]
        if question:
            base.insert(0, f"Bounded formal question: {question}")
        return base

    if ctx == "toy_model":
        base = [
            "Model family and Hamiltonian or action specification.",
            "Observable family and finite-size or parameter regime.",
            "Benchmark or comparator convergence behaviour.",
        ]
        if question:
            base.insert(0, f"Bounded model question: {question}")
        return base

    if ctx == "first_principles":
        base = [
            "Code or method family and implementation basis.",
            "Convergence target (basis set, grid, sampling).",
            "Benchmark or reference comparator result.",
        ]
        if question:
            base.insert(0, f"Bounded method question: {question}")
        return base

    return [
        "Declared candidate ids, bounded claims, and validation outcomes.",
        "Promotion readiness, gap honesty, and whether the topic must return to L0.",
    ]


def lane_target_claims(
    lane: str,
    topic_context: dict[str, Any],
    candidate_rows: list[dict[str, Any]] | None = None,
    selected_action: dict[str, Any] | None = None,
) -> list[str]:
    question = str((topic_context or {}).get("question") or "").strip()
    claims: list[str] = []

    if candidate_rows:
        for row in candidate_rows:
            cid = str(row.get("candidate_id") or "").strip()
            if cid and not _is_runtime_action_id(cid):
                claims.append(cid)

    if claims:
        return claims

    if question:
        short = question[:120] + ("..." if len(question) > 120 else "")
        claims.append(f"Bounded claim: {short}")
        return claims

    if selected_action:
        aid = str(selected_action.get("action_id") or "").strip()
        if aid:
            claims.append(aid)
            return claims

    return ["(no bounded claim registered yet)"]


def lane_deliverables(lane: str, topic_context: dict[str, Any]) -> list[str]:
    question = str((topic_context or {}).get("question") or "").strip()
    ctx = lane

    if ctx == "formal_derivation":
        base = [
            "Complete derivation chain persisted in L3 with explicit theorem dependencies.",
            "Notation lock and definition table matching the active formalism.",
            "Proof or closure obligation list with completion status.",
        ]
        return base

    if ctx == "toy_model":
        base = [
            "Model specification and parameter table persisted in L3.",
            "Numerical results with convergence evidence and error estimates.",
            "Benchmark comparison table against reference or analytic values.",
        ]
        return base

    if ctx == "first_principles":
        base = [
            "Method specification, basis set, and convergence parameters persisted in L3.",
            "Computed observables with convergence evidence.",
            "Benchmark comparison against reference data or analytic limits.",
        ]
        return base

    return [
        "Persist the active research question, validation route, and bounded next action as durable runtime artifacts.",
        "Write derivation/proof or execution evidence into the appropriate AITP layer before claiming completion.",
        "Produce Layer-appropriate outputs that can later be promoted into durable L2 knowledge when justified.",
    ]


def _is_runtime_action_id(value: str) -> bool:
    import re
    return bool(re.match(r"^action:[^:]+:\d+$", value))


def _hint_text(hints: dict[str, Any]) -> str:
    parts: list[str] = []
    for key in ("question", "scope", "source_basis_refs"):
        val = hints.get(key)
        if isinstance(val, str) and val.strip():
            parts.append(val.strip())
        elif isinstance(val, list):
            parts.extend(str(v).strip() for v in val if str(v).strip())
    l1 = hints.get("l1_source_intake") or {}
    for sub_key in ("assumption_rows", "interpretation_rows"):
        for row in l1.get(sub_key) or []:
            for field in ("assumption", "interpretation", "text"):
                v = str(row.get(field) or "").strip()
                if v:
                    parts.append(v)
    return " ".join(parts).lower()


_TOY_MODEL_SIGNALS = {
    "lattice", "hamiltonian", "ising", "heisenberg", "haldane",
    "spin chain", "toy model", "finite-size", "finite size",
    "exact diagonalization", "tfim", "su(2)", "mps", "dmrg",
}

_FIRST_PRINCIPLES_SIGNALS = {
    "dft", "density functional", "gw", "qsgw", "bethe-salpeter", "bse",
    "qmc", "quantum monte carlo", "basis set", "plane wave", "pseudopotential",
    "convergence", "librpa", "abinit", "vasp", "quantum espresso",
}


def _looks_like_toy_model(text: str) -> bool:
    return any(s in text for s in _TOY_MODEL_SIGNALS)


def _looks_like_first_principles(text: str) -> bool:
    return any(s in text for s in _FIRST_PRINCIPLES_SIGNALS)
