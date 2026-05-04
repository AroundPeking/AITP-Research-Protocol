---
name: aitp-opencode-adapter
description: Reference note for the OpenCode adapter surface; the active OpenCode bootstrap lives in ~/.config/opencode/plugins/aitp.js plus the local skills/ and deploy/templates/claude-code/ for skill content.
---

# OpenCode Adapter Reference

The OpenCode path is plugin-first (equivalent to Claude Code's SessionStart hook):

1. Install `deploy/templates/opencode/aitp-plugin.js` → `~/.config/opencode/plugins/aitp.js`
2. Add `aitp` MCP server to global `~/.config/opencode/opencode.json`
3. Add `aitp_*` to workspace `opencode.json` tools whitelist
4. On every chat init, `experimental.chat.system.transform` injects the adapted `using-aitp` skill

## Architecture

OpenCode uses a plugin-based injection model instead of Claude Code's hook-based model:

| Layer | Claude Code | OpenCode |
|-------|------------|----------|
| Gateway Injection | `hooks/session_start.py` → stdout JSON | `plugins/aitp.js` → `system.transform` |
| Compact Re-injection | `hooks/compact.py` | N/A (agent re-calls `aitp_get_execution_brief`) |
| Skill Source | `deploy/templates/claude-code/using-aitp.md` | **Same file**, adapted at injection time |
| MCP Tools | `mcp__aitp__aitp_*` | `aitp_*` |
| User Questions | `AskUserQuestion` | `question` |
| Tool Discovery | `ToolSearch` | Not needed (always available) |

## Tool adaptation

The plugin reads the canonical `deploy/templates/claude-code/using-aitp.md` and applies these runtime transformations:

- `mcp__aitp__aitp_*` → `aitp_*`
- `AskUserQuestion` → `question`
- `"multiSelect"` → `"multiple"`
- `{{TOPICS_ROOT}}` / `{{REPO_ROOT}}` → resolved paths
- Removes `ToolSearch` references (not applicable)

This means the OpenCode adapter stays in sync with the Claude Code skill — only one canonical source file to maintain.

## Phase behavior

During OpenCode topic work:

1. If the idea is vague, run the clarification sub-protocol before normal `L0 → L1 → L3 → L4 → L2` execution
2. Clarification rounds target scope, assumptions, and target_claims, with at most 3 rounds and 1-3 questions per round
3. Non-trivial checkpoints should become decision points, not only chat prose
4. Session summaries should be written back as chronicles
5. Always call `aitp_get_execution_brief` before deciding what to do next
6. Use the `question` tool for ALL user questions — never type options as plain text

## Config reference

Global `~/.config/opencode/opencode.json`:
```json
{
  "mcp": {
    "aitp": {
      "type": "local",
      "command": ["python", "<AITP_REPO>/brain/mcp_server.py"],
      "enabled": true
    }
  },
  "tools": { "aitp_*": true }
}
```

Workspace `opencode.json`:
```json
{
  "tools": { "aitp_*": true }
}
```
