---
name: skill-l3-distill
description: L3 Distillation subplane — extract final claims from integrated results.
trigger: l3_subplane == "distillation"
---

# L3 Distillation

You are in the distillation subplane of L3 derivation.

## Active artifact

`L3/distillation/active_distillation.md`

## What to do

1. Extract the distilled claim from integrated findings.
2. Summarize the supporting evidence.
3. Assign a confidence level.
4. List remaining open questions.

## Exit condition

When `active_distillation.md` has filled frontmatter fields `distilled_claim`
and `evidence_summary`, plus headings `## Distilled Claim` and `## Evidence Summary`,
the L3 flow is complete. You may then:
- Emit `L3/tex/flow_notebook.tex` via `aitp_render_flow_notebook`.
- Advance to L4 for adjudication.

## Allowed transitions

- Forward: L4 adjudication
- Backedges: `result_integration`
