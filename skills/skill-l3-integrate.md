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

## Collaborative Discussion (MANDATORY)

Before integrating results, you MUST discuss with the human about what the results mean.
Do NOT just combine numbers into a summary.

Use AskUserQuestion at these checkpoints:

1. **Cross-check discussion**: Present how different analysis results relate.
   Ask: "The OTOC says <X> and Krylov says <Y>. Are these consistent with each other?
   Do you see the same picture I do?"
2. **Gap identification**: Discuss what's missing.
   Ask: "Here are the gaps I've identified: <gaps>. Are there others? Which are
   blocking vs. nice-to-have?"
3. **Consistency with priors**: Compare against known results.
   Ask: "Our findings <vs.> the Chen-Zhou prediction / HS integrable limit / prior work.
   Does the comparison hold up? Any tensions?"
4. **Integration confirmation**: Before advancing to distillation.
   Ask: "The integrated picture is: <summary>. Ready to distill a claim, or do we
   need more analysis first?"

The human may add more discussion rounds at any time. Do NOT rush to fill the artifact.

## Escape Hatches

At ANY point during integration, you may offer these back-paths via AskUserQuestion:

- **Back to analysis** (`aitp_advance_l3_subplane(target="analysis")`): if integration
  reveals analysis gaps
- **Back to planning** (`aitp_advance_l3_subplane(target="planning")`): if integration
  reveals the plan was incomplete
- **Retreat to L1** (`aitp_retreat_to_l1`): if integration reveals fundamental
  framing issues
- **Query L2** (`aitp_query_knowledge`): compare integrated findings against
  validated global knowledge

## Active artifact

`L3/result_integration/active_integration.md`

## What to do

1. Combine analysis results into coherent findings.
2. Run consistency checks against L1 conventions and anchors.
3. Identify remaining gaps.
4. Do not distill yet.

## Flow Notebook — Incremental Update (MANDATORY)

Before advancing out of this subplane, update `L3/tex/flow_notebook.tex`:

1. **If file does NOT exist**: copy template from `<aitp-repo-root>/templates/flow_notebook.tex`
   to `L3/tex/flow_notebook.tex`, fill the **Result Integration** section, leave other sections
   as `{{PLACEHOLDER}}` comments.
2. **If file already exists**: update ONLY the Result Integration section from
   `active_integration.md` using Markdown→LaTeX conversion rules (see skill-l3-distill for
   full rules table).
   Add version comment: `% Updated: <date> — integration revision`.

Do NOT compile to PDF yet. Compilation happens at distillation.

## Exit condition

Advance to **distillation** when `active_integration.md` has filled frontmatter fields
`integration_statement` and `findings`, plus headings `## Integration Statement` and `## Findings`,
AND `flow_notebook.tex` has been updated.

## Allowed transitions

- Forward: `distillation`
- Backedges: `analysis`
