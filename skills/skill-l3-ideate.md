---
name: skill-l3-ideate
description: L3 Ideation subplane — generate and record research ideas.
trigger: l3_subplane == "ideation"
---

# L3 Ideation

You are in the ideation subplane of L3 derivation.

## Active artifact

`L3/ideation/active_idea.md`

## What to do

1. Record the central idea statement.
2. Explain why this idea is worth pursuing (motivation).
3. Note prior work and risks.
4. Do not start planning or analysis yet.

## Exit condition

Advance to **planning** when `active_idea.md` has filled frontmatter fields
`idea_statement` and `motivation`, plus headings `## Idea Statement` and `## Motivation`.

## Allowed transitions

- Forward: `planning`
- Backedges: none (this is the entry subplane)
