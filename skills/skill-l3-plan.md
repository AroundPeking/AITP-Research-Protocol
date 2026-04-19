---
name: skill-l3-plan
description: L3 Planning subplane — design derivation route from idea.
trigger: l3_subplane == "planning"
---

# L3 Planning

You are in the planning subplane of L3 derivation.

## Active artifact

`L3/planning/active_plan.md`

## What to do

1. State the derivation plan.
2. Map the route from starting anchors to target claims.
3. List expected outcomes and milestones.
4. Do not start calculation or analysis yet.

## Exit condition

Advance to **analysis** when `active_plan.md` has filled frontmatter fields
`plan_statement` and `derivation_route`, plus headings `## Plan Statement` and `## Derivation Route`.

## Allowed transitions

- Forward: `analysis`
- Backedges: `ideation`
