# Adapter Assets

These adapter assets document how different agents enter the same AITP
contract surface.

Supported reference adapters:

| Agent | Adapter Doc | Bootstrap Assets |
|-------|-------------|-----------------|
| Claude Code | `adapters/claude-code/SKILL.md` | `/.claude-plugin`, `/hooks`, `deploy/templates/claude-code/`, `skills/` |
| Codex | `adapters/codex/SKILL.md` | `/.codex`, `skills/` |
| OpenClaw | `adapters/openclaw/SKILL.md` | adapter only |
| OpenCode | `adapters/opencode/SKILL.md` | `~/.config/opencode/plugins/aitp.js`, `deploy/templates/opencode/aitp-plugin.js`, `skills/`

All adapters assume an available `aitp` executable on `PATH`.
