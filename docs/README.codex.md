# AITP For Codex App

Codex app uses AITP through native skill discovery plus an AITP MCP server.
This checkout now provides a repository-local Codex adapter path:

```powershell
uv run --with pyyaml --with jsonschema --with fastmcp python scripts/aitp-pm.py install --agent codex --scope user
```

Then restart Codex.

## What Gets Installed

- `using-aitp`: Codex-native front-door routing for theory work.
- `aitp-runtime`: Codex-native runtime loop for L0 -> L1 -> L3 -> L4 -> L2.
- Wrapped protocol skills from `skills/`, with a Codex adapter preamble.
- A best-effort `mcp.json` next to the Codex skill root.

The installer uses Codex-specific roots such as `~/.codex/skills`,
`~/.codex-home/skills`, or `~/.codex-switcher/skills`. It does not rely on the
shared `~/.agents/skills` root by default, so Kimi/other agent deployments are
not clobbered.

## Current Checkout Caveat

Do not use the older public-package commands from stale docs:

```text
python -m pip install aitp-kernel
aitp install-agent --agent codex --scope user
scripts\aitp-local.cmd install-agent --agent codex --scope user
```

Those commands require a package entrypoint that is not present in this
checkout. Use `scripts/aitp-pm.py install --agent codex` instead.

## Verify

```powershell
uv run --with pyyaml --with jsonschema --with fastmcp python scripts/aitp-pm.py doctor
```

The Codex section should show `using-aitp/SKILL.md`, `aitp-runtime/SKILL.md`,
and an `mcp.json` with an `aitp` entry.

For full instructions, see [INSTALL_CODEX.md](INSTALL_CODEX.md).
