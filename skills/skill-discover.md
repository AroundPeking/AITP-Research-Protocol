---
name: skill-discover
description: Discover posture — find, evaluate, and register sources before reading.
trigger: posture == "discover"
---

# Discover Posture

## MANDATORY: AskUserQuestion rule

When you need to ask the user ANY question (clarification, scope, direction, missing info), you MUST:
1. Call `ToolSearch(query="select:AskUserQuestion", max_results=1)` to load the tool.
2. Call `AskUserQuestion(questions=[{...}])` with your question and options.
NEVER type questions as plain text. ALWAYS use the popup tool.

---

You are in the source discovery phase. Your job is to find and register all relevant materials before the deep reading begins.

## <HARD-GATE>
Do NOT advance to L1 until the researcher confirms source coverage is adequate.
Do NOT register sources the researcher hasn't explicitly asked for.
Do NOT search/read code or papers directly — register them as sources first.
</HARD-GATE>

## Checklist
You MUST create a task for each item and complete them in order:

1. **Check L2 first** — `aitp_query_l2_index(topics_root)`. Report: what's already known? What domains are populated? This prevents re-deriving known results.
2. **Ask: what is the single most important source?** — ONE question via AskUserQuestion. Target the most central reference first (paper, codebase, dataset). Do NOT ask "what sources do you need?" (invites vague lists). Ask specifically: "What's the primary reference for this topic?"
3. **Register that source** — `aitp_register_source(...)`. Fill all metadata fields: source_type, title, fidelity, physical_system, method_category, source_role, epistemic_tier. Show the result.
4. **Record in registry** — update `L0/source_registry.md` with: Prior L2 Knowledge (from step 1), the registered source, and gaps you notice.
5. **Ask: what next?** — ONE question: "Is there another key source, or is coverage adequate?" Repeat steps 3-4 for each source the researcher names.
6. **Present coverage summary** — state: total sources, areas covered, identified gaps. Ask: "Ready to advance to L1, or should we hunt for sources in these gap areas?"
7. **Advance** — `aitp_advance_to_l1(topics_root, topic_slug)` only after researcher confirms.

## One Question At A Time

- Each round targets ONE source or ONE gap.
- Do not present a list of "potential sources to register." Let the researcher drive.
- If the researcher says "直接做" or "just go": register the sources they've already mentioned, mark search_status as "focused", record deferred gaps in `## Gaps And Next Sources`, and advance.

## Source Types

Sources go beyond literature. When the researcher names a source, help them classify it:
- **Papers and preprints** — journal articles, arXiv preprints, conference proceedings
- **Datasets** — experimental data, simulation outputs, benchmark results
- **Code** — reference implementations, computational libraries, notebooks
- **Books and lectures** — textbook chapters, lecture notes, review articles
- **Experiments** — lab protocols, measurement setups, raw observations

## Required artifacts

- `L0/source_registry.md` — master inventory with all required headings
- `L0/sources/*.md` — individual source files (created by `aitp_register_source`)

## Gate requirements

Before advancing to L1:
- `L0/source_registry.md` exists with all required headings filled: `## Search Methodology`, `## Source Inventory`, `## Coverage Assessment`, `## Overall Verdict`, `## Gaps And Next Sources`
- `source_count` > 0 in frontmatter
- `search_status` is set (not empty)
- `## Overall Verdict` has substantive content (min 200 chars — not placeholder text)

## Exit condition

Before advancing, load `skill-physicist-check`:
1. Query L2 for what's already known. Record in `## Prior L2 Knowledge`.
2. If L2 has relevant results, flag them for the human.
3. If nothing exists, state "no prior L2 knowledge on this topic."

Move on to L1 only after the researcher confirms the source coverage is adequate.
Call `aitp_advance_to_l1` to transition.

## Check progress at any time

`L3/tex/flow_notebook.tex` is auto-regenerated after every subplane advance, candidate submission, L4 review, and promotion.
