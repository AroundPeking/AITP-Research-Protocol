# Install Claude Code Adapter

## Prerequisites

- Python 3.10+
- Claude Code installed locally

## Install the AITP runtime

From the repository root:

```bash
python -m pip install -e research/knowledge-hub
aitp doctor
```

## Install the Claude Code wrapper

```bash
aitp install-agent --agent claude-code --scope user
```

This installs:

- the `using-aitp` gatekeeper under `~/.claude/skills/using-aitp/`
- the `aitp-runtime` skill under `~/.claude/skills/aitp-runtime/`
- command files under `~/.claude/commands/`
- an MCP setup note for the optional `aitp-mcp` tool surface

For a project-local install that Claude Code can load at session start:

```bash
aitp install-agent --agent claude-code --scope project --target-root /path/to/theory-workspace
```

That writes into the workspace-native Claude directory:

- `.claude/skills/using-aitp/`
- `.claude/skills/aitp-runtime/`
- `.claude/commands/`

## Recommended entrypoint

Use:

```bash
aitp session-start "<task>"
```

Then continue with `aitp loop ...` or `aitp resume ...` after the runtime
bundle exists. Use `aitp bootstrap ...` only to create a new topic shell.

Session-start invariant:

- if the user says `继续这个 topic`, `continue this topic`, `this topic`, or `current topic`, Claude Code should treat that as a current-topic-memory request immediately
- it should only fall back to the latest topic if current-topic memory is missing
- it should only ask for a slug when the request remains genuinely ambiguous after checking durable memory

## Verify

Claude Code should now be able to:

- route substantial research work through `aitp session-start`
- load the stricter `using-aitp` session-start constraint from `.claude/skills/using-aitp/`
- read the runtime protocol bundle first
- resolve `继续这个 topic` against durable current-topic memory before asking for a slug
- refuse to count missing-conformance work as AITP work

## Manual fallback

Reference assets still live at:

- `adapters/claude-code/SKILL.md`
- `adapters/claude-code/commands/`

## Remove

See [`docs/UNINSTALL.md`](UNINSTALL.md).
