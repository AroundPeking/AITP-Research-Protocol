# Install OpenCode Adapter

## Prerequisites

- Python 3.10+
- OpenCode installed locally

## Install the AITP runtime

From the repository root:

```bash
python -m pip install -e research/knowledge-hub
aitp doctor
```

## Install the OpenCode adapter bundle

```bash
aitp install-agent --agent opencode --scope user
```

This installs:

- the `using-aitp` gatekeeper into the OpenCode skill root
- the `aitp-runtime` skill into the OpenCode skill root
- the AITP command harness
- `/aitp`, `/aitp-resume`, `/aitp-loop`, and `/aitp-audit` command files
- an `mcp.aitp` local server entry when config mutation is allowed

If you want a separate theory workspace to run bare `opencode` in an AITP-first
way, install the project bundle into that workspace root:

```bash
aitp install-agent --agent opencode --scope project --target-root /path/to/theory-workspace
```

That writes:

- `.opencode/commands/AITP_COMMAND_HARNESS.md`
- `.opencode/commands/aitp.md`, `aitp-resume.md`, `aitp-loop.md`, and `aitp-audit.md`
- `.opencode/skills/using-aitp/SKILL.md`
- `.opencode/skills/aitp-runtime/SKILL.md`
- `.opencode/skills/aitp-runtime/AITP_MCP_SETUP.md`
- `.opencode/AITP_MCP_CONFIG.json`

## Recommended entrypoint

Use the session-start path:

```bash
aitp session-start "<task>"
```

Then continue with `aitp loop ...` or `aitp resume ...` after the runtime
bundle exists. The installed OpenCode skill and command bundle are now designed
to treat `继续这个 topic`, `continue this topic`, `this topic`, and
`current topic` as a current-topic-memory request before asking for a slug.

## Verify

OpenCode should now be able to:

- read the installed `using-aitp` and `aitp-runtime` skills when the active OpenCode setup loads the local skill root
- enter the AITP runtime through the installed commands
- resolve `继续这个 topic` against durable current-topic memory before asking for a slug
- read `runtime_protocol.generated.md` before doing deeper work
- refresh conformance on exit

If the local skill root is not active, the installed `/aitp` command bundle is
still the explicit AITP entry surface, and its first step should be
`aitp session-start "$ARGUMENTS"`.

## Manual fallback

If you want the reference assets only, they still live at:

- `adapters/opencode/SKILL.md`
- `adapters/opencode/AITP_MCP_SETUP.md`
- `adapters/opencode/AITP_COMMAND_HARNESS.md`
- `adapters/opencode/commands/`

## Remove

See [`docs/UNINSTALL.md`](UNINSTALL.md).
