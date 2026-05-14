# Install Codex App Adapter

Status: repository-local adapter support is available through
`scripts/aitp-pm.py install --agent codex`. The older public-package commands
(`aitp-kernel`, `aitp install-agent --agent codex`, and
`scripts/aitp-local.cmd install-agent`) are not valid for this checkout until
the missing `research/knowledge-hub/knowledge_hub` package source is restored.

## Install From This Checkout

Use `uv` unless your default `python` already has `pyyaml`, `jsonschema`, and
`fastmcp` installed:

```powershell
uv run --with pyyaml --with jsonschema --with fastmcp python scripts/aitp-pm.py install --agent codex --scope user
```

Project-local install:

```powershell
uv run --with pyyaml --with jsonschema --with fastmcp python scripts/aitp-pm.py install --agent codex --scope project --target-root <workspace>
```

The installer deploys:

- Codex-native gateway skills from `deploy/codex/skills/`.
- Protocol skills from `skills/`, wrapped with a Codex adapter preamble that
  maps Claude/Kimi tool names to Codex behavior.
- A best-effort `mcp.json` beside each Codex skill root, using `uv` when
  available so the MCP server has its Python dependencies.

User-scope Codex skill roots are detected in this order when present:

- `%USERPROFILE%\.codex\skills`
- `%USERPROFILE%\.codex-home\skills`
- `%USERPROFILE%\.codex-switcher\skills`

If no Codex-specific root exists, the installer creates
`%USERPROFILE%\.codex\skills`.

## Verify

Run:

```powershell
uv run --with pyyaml --with jsonschema --with fastmcp python scripts/aitp-pm.py doctor
uv run --with pyyaml --with jsonschema --with fastmcp python -m brain.cli --help
```

Inspect deployed skills if needed:

```powershell
Get-ChildItem "$env:USERPROFILE\.codex\skills"
Get-ChildItem "$env:USERPROFILE\.codex-home\skills"
Get-ChildItem "$env:USERPROFILE\.codex-switcher\skills"
```

Codex should discover at least:

- `using-aitp`
- `aitp-runtime`

## Runtime Behavior

Codex does not use Claude-only tools such as `AskUserQuestion` and
`ToolSearch`. The Codex gateway skills say how to map those upstream protocol
phrases:

- Ask the user through Codex's available interaction surface.
- If no structured prompt tool is active, ask one concise plain-text question
  and wait.
- Map `mcp__aitp__aitp_*` examples to the actual AITP MCP tool names exposed
  by Codex.
- If MCP tools are unavailable, diagnose setup instead of manually mutating
  AITP topic state.

## Remove

```powershell
uv run --with pyyaml --with jsonschema --with fastmcp python scripts/aitp-pm.py uninstall --agent codex --scope user
```

For full cleanup guidance, see [UNINSTALL.md](UNINSTALL.md).
