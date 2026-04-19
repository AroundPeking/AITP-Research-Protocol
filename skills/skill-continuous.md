---
name: skill-continuous
description: Resume mode — restore workflow after session break or context compaction.
trigger: any status after session break
---

# Resume Mode

Your session was interrupted (context compaction, new session, or break).
This skill helps you pick up where you left off.

## What to Do

1. **Read topic state** by calling:
   ```
   aitp_get_status(topics_root, topic_slug)
   ```

2. **Check for popups** (blockers requiring human input):
   ```
   aitp_get_popup(topics_root, topic_slug)
   ```
   If there is a popup, resolve it FIRST before continuing.

3. **Determine where you are** based on status:

   | Status | Where You Left Off | Next Skill |
   |--------|-------------------|------------|
   | `new` | Just started, no sources | skill-explore |
   | `sources_registered` | Sources found, not analyzed | skill-intake |
   | `intake_done` | Sources analyzed, no candidates | skill-derive |
   | `candidate_ready` | Candidate submitted, not validated | skill-validate |
   | `validated` | Candidate validated, not promoted | skill-promote |
   | `promoted` | Candidate promoted to L2 | Ask human for next direction |
   | `blocked` | Something is stuck | Read `state.md` to understand blocker |

4. **Read relevant files** to rebuild context:
   - `state.md` — current status and research question
   - `L3/derivations.md` — what derivations have been done
   - `L3/candidates/*.md` — what candidates exist
   - `L4/reviews/*.md` — what validation has been done

5. **Inject the appropriate skill** and continue work.

## Rules

- Do NOT start from scratch. Read what already exists.
- Do NOT assume the status is correct. Verify by checking actual files.
- If the status doesn't match the files (e.g., status says "intake_done" but
  no intake files exist), fix the status:
  ```
  aitp_update_status(topics_root, topic_slug, status="<correct_status>")
  ```
- If you find work that was in progress but not recorded, record it now.

## After Resume

Once you've rebuilt context and injected the correct skill, continue the
workflow from where it was. Do not repeat completed steps.
