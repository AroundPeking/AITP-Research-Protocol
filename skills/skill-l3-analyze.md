---
name: skill-l3-analyze
description: L3 Analysis subplane — execute derivations and calculations.
trigger: l3_subplane == "analysis"
---

# L3 Analysis

## MANDATORY: AskUserQuestion rule

When you need to ask the user ANY question (clarification, scope, direction, missing info), you MUST:
1. Call `ToolSearch(query="select:AskUserQuestion", max_results=1)` to load the tool.
2. Call `AskUserQuestion(questions=[{...}])` with your question and options.
NEVER type questions or options as plain text. ALWAYS use the popup tool.

---

You are in the analysis subplane of L3 derivation.

## Active artifact

`L3/analysis/active_analysis.md`

## What to do

1. Execute the planned derivation steps.
2. Record the method used and results so far.
3. Flag any anomalies or unexpected findings.
4. Do not finalize claims yet.

## Exit condition

Advance to **result_integration** when `active_analysis.md` has filled frontmatter fields
`analysis_statement` and `method`, plus headings `## Analysis Statement` and `## Method`.

## Allowed transitions

- Forward: `result_integration`
- Backedges: `ideation`, `planning`
