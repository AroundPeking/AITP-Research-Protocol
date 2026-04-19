---
name: skill-explore
description: Explore mode — discover literature, register sources, record initial ideas.
trigger: status == "new"
---

# Explore Mode

You are in **explore** mode. Your job: discover relevant literature and register sources.

## What to Do

1. **Search for literature** related to the research question in `state.md`.
   - Use arXiv search, Google Scholar, or references the human provides.
   - For each relevant paper, note the arXiv ID.

2. **Register each source** by calling:
   ```
   aitp_register_source(
     topics_root, topic_slug,
     source_id="author-keyword-year",
     source_type="paper",
     title="Full Paper Title",
     arxiv_id="2401.12345",
     fidelity="arxiv_preprint",
     notes="Why this paper is relevant"
   )
   ```

3. **Read key papers** to identify:
   - Core claims and results
   - Methods used
   - Open questions
   - Connections to other work

4. **Record initial ideas** in `L3/derivations.md` using:
   ```
   aitp_record_derivation(
     topics_root, topic_slug,
     derivation_id="idea-1",
     kind="ideation",
     title="Brief idea description",
     status="speculative",
     content="What you noticed and why it might matter"
   )
   ```

5. **When you have registered at least one source**, update status:
   ```
   aitp_update_status(topics_root, topic_slug, status="sources_registered")
   ```

## Rules

- Do NOT form formal candidates yet. Ideas in explore mode are speculative.
- Do NOT skip reading the source. Registering without reading is a protocol violation.
- Mark every idea as speculative. Do not merge speculation with source-grounded claims.
- If the human provides a direction, follow it. If not, search broadly first.

## When to Transition

Transition to **intake** (skill-intake) when:
- At least one source is registered AND
- You have a basic understanding of what the topic is about.

Ask the human: "I've found [N] sources. Should I start analyzing them in depth?"
