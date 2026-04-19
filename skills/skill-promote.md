---
name: skill-promote
description: Promote mode — guide validated candidates through L2 promotion gate.
trigger: status == "validated"
---

# Promote Mode

You are in **promote** mode. Your job: guide validated candidates through the
L2 promotion gate with human approval.

## What to Do

1. **Request promotion** for each validated candidate:
   ```
   aitp_request_promotion(topics_root, topic_slug, candidate_id="level-spacing-wigner")
   ```

2. **Present the promotion gate to the human.** Tell them:
   - What the candidate claims
   - What evidence supports it
   - What validation passed
   - What assumptions remain

3. **Ask for approval:**
   "Candidate '[title]' has passed validation. It claims [brief claim].
    Should I promote it to reusable knowledge (L2)?"

4. **On human approval**, call:
   ```
   aitp_resolve_popup(topics_root, topic_slug, choice_index=0, comment="Human approved")
   ```
   This writes the candidate content to `L2/canonical/<id>.md`.

5. **On revision request**, call:
   ```
   aitp_resolve_popup(topics_root, topic_slug, choice_index=1, comment="What needs fixing")
   ```
   Then return to derive mode.

6. **After promotion**, update topic status:
   ```
   aitp_update_status(topics_root, topic_slug, status="promoted")
   ```

## Rules

- **L2 promotion ALWAYS requires human approval.** No exceptions.
- Do not auto-promote without asking the human.
- Present the evidence honestly, including gaps and assumptions.
- If the candidate is too wide (mixes multiple claims), split it first.
  Each promoted unit should be bounded and self-contained.

## Promotion Trace

Every promotion must leave a trace in the candidate file:
- `status: promoted`
- `promoted_at: <timestamp>`
- `promotion_comment: <why approved>`
- The resulting L2 file path

## After Promotion

After promoting a candidate:
- Ask the human if they want to continue with another candidate
- Or explore new directions
- Or move to writing (L5)
