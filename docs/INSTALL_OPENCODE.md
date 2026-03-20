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

- the `aitp-runtime` skill into the OpenCode skill root when the workspace or user config exposes one
- the AITP command harness
- `/aitp`, `/aitp-resume`, `/aitp-loop`, and `/aitp-audit` command files
- an `mcp.aitp` local server entry when config mutation is allowed

If you want a separate theory workspace to run bare `opencode` in an AITP-first
way, install the project bundle into that workspace root:

```bash
aitp install-agent --agent opencode --scope project --target-root /path/to/theory-workspace
```

That writes:

- `commands/AITP_COMMAND_HARNESS.md`
- `commands/aitp.md`, `aitp-resume.md`, `aitp-loop.md`, and `aitp-audit.md`
- `skills/aitp-runtime/SKILL.md`
- `skills/aitp-runtime/AITP_MCP_SETUP.md`
- `AITP_MCP_CONFIG.json`

## Recommended entrypoint

Use the loop-oriented path:

```bash
aitp loop --topic-slug <topic_slug> --human-request "<task>"
```

The installed OpenCode command bundle is designed to route existing topics
through `aitp loop` by default rather than through free-form browsing.

## Verify

OpenCode should now be able to:

- read the installed `aitp-runtime` skill when the active OpenCode setup loads the local skill root
- enter the AITP runtime through the installed commands
- read `runtime_protocol.generated.md` before doing deeper work
- refresh conformance on exit

If the local skill root is not active, the installed `/aitp` command bundle is
still the explicit AITP entry surface.

## Manual fallback

If you want the reference assets only, they still live at:

- `adapters/opencode/SKILL.md`
- `adapters/opencode/AITP_MCP_SETUP.md`
- `adapters/opencode/AITP_COMMAND_HARNESS.md`
- `adapters/opencode/commands/`

## Remove

See [`docs/UNINSTALL.md`](UNINSTALL.md).
