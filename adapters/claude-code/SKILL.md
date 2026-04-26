---
name: aitp-runtime
description: Reference note for the Claude Code adapter surface; the active Claude bootstrap lives in hooks/, skills/, and deploy/templates/claude-code/.
---

# Claude Code Adapter Reference

The public Claude Code path is SessionStart-first:

1. Run `python scripts/aitp-pm.py install --agent claude-code`
2. SessionStart injects `using-aitp` before substantive theory work
3. MCP tools available as `mcp__aitp__aitp_*`

## Phase behavior

During Claude Code topic work:

1. If the idea is vague, run the clarification sub-protocol before normal
   `L0 -> L1 -> L3 -> L4 -> L2` execution
2. Clarification rounds target scope, assumptions, and target_claims, with
   at most 3 rounds and 1-3 questions per round
3. Non-trivial checkpoints should become decision points, not only chat prose
4. Session summaries should be written back as chronicles
5. Always call `aitp_get_execution_brief` before deciding what to do next
6. Use `AskUserQuestion` for ALL user questions — never type options as plain text
