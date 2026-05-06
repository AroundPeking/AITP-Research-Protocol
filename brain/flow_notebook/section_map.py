"""Section → source artifact mapping and ordering for the flow notebook.

SECTION_ORDER defines the canonical section sequence.
SECTION_SOURCES maps each section name to its source artifact globs.

Renamed from v1:
- session_history → session_metadata (protocol metadata, demoted)
- derivation → derivation_journey (moved up in order)
- synthesis → synthesis_claims
- open_questions → negative_results
- l2_knowledge → canonical_knowledge
"""

SECTION_ORDER: list[str] = [
    "research_question",
    "source_landscape",
    "conventions",
    "derivation_journey",
    "synthesis_claims",
    "validation",
    "negative_results",
    "canonical_knowledge",
    "domain_context",
    "session_metadata",
    "execution_provenance",
]

SECTION_SOURCES: dict[str, list[str]] = {
    "research_question":    ["L1/question_contract.md"],
    "source_landscape":     ["L0/source_registry.md", "L0/sources/*.md",
                             "L1/source_basis.md", "L1/source_cross_map.md"],
    "conventions":          ["L1/convention_snapshot.md"],
    "session_metadata":     ["state.md", "runtime/sessions.md"],
    "derivation_journey":   ["L3/ideate/active_idea.md", "L3/plan/active_plan.md",
                             "L3/derive/active_derivation.md",
                             "L3/trace-derivation/active_trace.md",
                             "L3/gap-audit/active_gaps.md",
                             "L3/connect/active_connect.md",
                             "L3/integrate/active_integration.md",
                             "L3/ideas/*.md"],
    "synthesis_claims":     ["L3/distill/active_distillation.md",
                             "L3/candidates/*.md"],
    "validation":           ["L4/reviews/*.md", "L4/outputs/*.md",
                             "L4/validation_contract.md", "state.md"],
    "canonical_knowledge":  [],
    "domain_context":       ["contracts/domain-manifest.md"],
    "negative_results":     ["L3/deferred.md", "L3/ideas/*.md",
                             "L1/contradiction_register.md"],
    "execution_provenance": ["runtime/log.md"],
}
