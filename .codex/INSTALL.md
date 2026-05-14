# Installing AITP For Codex App

This file is the Codex-facing install note for a repo-backed checkout.

The current checkout does not contain the public `aitp-kernel` package source
advertised by older docs. Use the repository-local package manager instead.

## Install

From the repository root:

```powershell
uv run --with pyyaml --with jsonschema --with fastmcp python scripts/aitp-pm.py install --agent codex --scope user
```

Project-local install:

```powershell
uv run --with pyyaml --with jsonschema --with fastmcp python scripts/aitp-pm.py install --agent codex --scope project --target-root <workspace>
```

Restart Codex after installation.

## What This Does

- Copies Codex-native gateway skills from `deploy/codex/skills/`.
- Copies protocol skills from `skills/` with a Codex adapter preamble.
- Writes a best-effort `mcp.json` beside each Codex skill root.
- Records the install in `%USERPROFILE%\.aitp\install-record.json`.

Codex-specific skill roots are preferred:

- `%USERPROFILE%\.codex\skills`
- `%USERPROFILE%\.codex-home\skills`
- `%USERPROFILE%\.codex-switcher\skills`

If none exists, the installer creates `%USERPROFILE%\.codex\skills`.

## Verify

```powershell
uv run --with pyyaml --with jsonschema --with fastmcp python scripts/aitp-pm.py doctor
uv run --with pyyaml --with jsonschema --with fastmcp python -m brain.cli --help
```

Expected Codex assets:

- `using-aitp/SKILL.md`
- `aitp-runtime/SKILL.md`
- `mcp.json` containing an `aitp` MCP server entry

## Important Codex Behavior

Codex does not use Claude-only `AskUserQuestion` or `ToolSearch` names. The
deployed Codex skills map those protocol instructions to Codex behavior:

- Ask the user normally unless a structured Codex input tool is active.
- Wait for explicit user approval at human gates.
- Use actual Codex MCP tool names for AITP tools.
- Do not manually edit AITP topic state if the MCP tools are unavailable.

## Uninstall

```powershell
uv run --with pyyaml --with jsonschema --with fastmcp python scripts/aitp-pm.py uninstall --agent codex --scope user
```
