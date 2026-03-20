# AITP MCP Setup For OpenCode

## User scope

When you run `aitp install-agent --agent opencode --scope user`, the installer
updates `~/.config/opencode/opencode.json` directly and registers the local
`aitp` MCP server there.

## Project or exported bundle scope

- `--scope project` writes the OpenCode config to `.opencode/opencode.json`
- `--target-root /path/to/bundle` writes `AITP_MCP_CONFIG.json` into the bundle root

Merge the generated MCP stanza into the OpenCode config you actually load for
the workspace.

The `aitp` MCP server must forward `AITP_KERNEL_ROOT` and `AITP_REPO_ROOT` to
the installed `aitp-mcp` command.
