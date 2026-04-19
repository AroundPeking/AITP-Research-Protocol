---
name: skill-intake
description: Intake mode — analyze each source in depth, extract assumptions and methods.
trigger: status == "sources_registered"
---

# Intake Mode

You are in **intake** mode. Your job: analyze each registered source in depth.

## What to Do

1. **Read each source** in `L0/sources/`. For each source:

2. **Create an intake note** by writing a Markdown file at `L1/intake/<source-id>.md`:

   ```markdown
   ---
   source_id: hs-1988
   reading_depth: close_read
   analyzed: 2026-04-19
   ---

   # Intake: Haldane & Shastry (1988)

   ## Core Claims
   - [List main results with evidence sentences]

   ## Key Assumptions
   - [Structural assumptions, not keywords]

   ## Methods
   - [Mathematical/computational methods used]

   ## Notation
   - $S_i$ = spin operator at site i
   - [All symbols defined]

   ## Open Questions
   - [What the source leaves unresolved]

   ## Connections
   - [Links to other sources in L0]
   ```

3. **Detect contradictions** between sources. If found, note them in the intake.

4. **Extract derivation anchors** — specific equations, theorems, or results that
   could serve as starting points for later L3 work.

5. **When all sources have intake notes**, update status:
   ```
   aitp_update_status(topics_root, topic_slug, status="intake_done")
   ```

## Rules

- Every claim in L1 is **provisional**. Mark it as such.
- Do not skip assumption extraction. "Obvious" assumptions are often the most important.
- Record notation precisely. Notation conflicts between sources must be noted.
- Reading depth: aim for `close_read` for core sources, `scan` for peripheral ones.

## When to Transition

Transition to **derive** (skill-derive) when:
- All registered sources have intake notes AND
- You understand the key assumptions and methods AND
- You have at least one idea for what to investigate.
