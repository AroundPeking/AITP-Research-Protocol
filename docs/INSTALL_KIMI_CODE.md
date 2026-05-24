# Kimi Code AITP v5 Setup

Kimi Code integration has three parts:

1. Skills: install `using-aitp` and `aitp-runtime` from `deploy/templates/kimi-code/`.
2. MCP: configure Kimi Code to expose `brain/v5/native_mcp.py` as the `aitp` MCP server.
3. Hooks: merge AITP v5 lifecycle hooks into `.kimi/config.toml`.

Kimi's official docs describe configuration, MCP, hooks, and skills: <https://www.kimi.com/code/docs/>. The verified local CLI path for Kimi CLI 1.35.0 is explicit loading with `--config-file`, `--mcp-config-file`, and `--skills-dir`.

## MCP

Example project `.kimi/mcp.json`:

```json
{
  "mcpServers": {
    "aitp": {
      "command": "python",
      "args": [
        "C:/path/to/AITP-Research-Protocol/brain/v5/native_mcp.py"
      ]
    }
  }
}
```

The current Kimi CLI also supports global MCP registration:

```powershell
kimi mcp add --transport stdio aitp -- python C:/path/to/AITP-Research-Protocol/brain/v5/native_mcp.py
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
kimi mcp test aitp
```

The UTF-8 variables avoid Windows GBK console failures when Kimi prints Unicode status symbols.

## Hooks

From the AITP repo root:

```powershell
python -m brain.v5.cli --base <workspace> adapter install-hooks kimi-code <session-id> --settings .kimi/config.toml
python -m brain.v5.cli --base <workspace> adapter install-audit kimi-code --settings .kimi/config.toml
python -m brain.v5.cli adapter smoke-coverage
```

Run Kimi with the project assets:

```powershell
kimi --work-dir <workspace> --config-file .kimi/config.toml --mcp-config-file $env:USERPROFILE\.kimi\mcp.json --skills-dir .kimi\skills
```

The installer preserves existing TOML by replacing only the marked AITP block:

```toml
# BEGIN AITP V5 KIMI HOOKS
[[hooks]]
event = "PreToolUse"
matcher = "*"
command = "..."

[[hooks]]
event = "PostToolUse"
matcher = "*"
command = "..."
# END AITP V5 KIMI HOOKS
```

## Contract

Kimi hooks are runtime guards. They may block unsafe pre-tool actions and write trace events after tool use, but they do not update claim trust. Scientific state still lives in typed v5 records.
