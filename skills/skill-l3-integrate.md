---
name: skill-l3-integrate
description: L3 Result Integration subplane — combine analysis into findings.
trigger: l3_subplane == "result_integration"
---

# L3 Result Integration

## MANDATORY: AskUserQuestion rule

When you need to ask the user ANY question (clarification, scope, direction, missing info), you MUST:
1. Call `ToolSearch(query="select:AskUserQuestion", max_results=1)` to load the tool.
2. Call `AskUserQuestion(questions=[{...}])` with your question and options.
NEVER type questions or options as plain text. ALWAYS use the popup tool.

---

You are in the result integration subplane of L3 derivation.

## Active artifact

`L3/result_integration/active_integration.md`

## What to do

1. Combine analysis results into coherent findings.
2. Run consistency checks against L1 conventions and anchors.
3. Identify remaining gaps.
4. Do not distill yet.

## Exit condition

Advance to **distillation** when `active_integration.md` has filled frontmatter fields
`integration_statement` and `findings`, plus headings `## Integration Statement` and `## Findings`.

## Allowed transitions

- Forward: `distillation`
- Backedges: `analysis`
