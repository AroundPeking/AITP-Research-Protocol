# Install Codex Adapter

## Prerequisites

- Python 3.10+
- Codex CLI installed locally

## Install the AITP runtime

From the repository root:

```bash
python -m pip install -e research/knowledge-hub
aitp doctor
```

On Windows-native, you can also verify the repo-local launchers directly:

```cmd
scripts\aitp-local.cmd doctor
scripts\aitp-codex-local.cmd --help
```

## Install the Codex wrapper

```bash
aitp install-agent --agent codex --scope user
```

This installs:

- the `using-aitp` skill as the conversation-level AITP gatekeeper
- the `aitp-runtime` skill into your active Codex skill roots
- the `aitp` MCP registration when supported

If you want a separate theory workspace to run bare `codex` in an AITP-first
way, install the project skill into that workspace root:

```bash
aitp install-agent --agent codex --scope project --target-root /path/to/theory-workspace
```

That writes:

- `.agents/skills/using-aitp/`
- `.agents/skills/aitp-runtime/`
- workspace-local wrappers under `.agents/bin/`

- `aitp`
- `aitp.cmd`
- `aitp-codex`
- `aitp-codex.cmd`
- `aitp-mcp`
- `aitp-mcp.cmd`

Windows-native example:

```cmd
scripts\aitp-local.cmd install-agent --agent codex --scope project --target-root D:\theory-workspace
```

The generated `.agents\bin\aitp.cmd` and `.agents\bin\aitp-codex.cmd` wrappers
pin `AITP_KERNEL_ROOT` to the cloned repository and do not depend on WSL.

## Recommended entrypoints

For normal topic work:

```bash
aitp loop --topic "<topic>" --human-request "<task>"
```

For Codex-driven implementation or execution:

```bash
aitp session-start "<task>"
aitp-codex "<task>"
aitp-codex --current-topic "<task>"
aitp-codex --topic-slug <topic_slug> "<task>"
aitp-codex --latest-topic "<task>"
```

With `using-aitp` installed, the intended Codex App UX is still natural language
first. For example, the user should be able to say:

- `帮我开一个新 topic：Topological phases from modular data。先做问题定义、范围和初始验证路线。`
- `继续这个 topic，方向改成 low-energy effective theory`

and let the hidden implementation path route through `aitp-codex`.

The preferred hidden routing order is:

1. plain `aitp-codex "<task>"` with auto-routing
2. `aitp session-start "<task>"` when you want to materialize routing and runtime state before continuing
3. `--current-topic`
4. `--latest-topic`
5. explicit `--topic-slug`

Session-start invariant:

- if the user says `继续这个 topic`, `continue this topic`, `this topic`, or `current topic`, Codex should resolve that against durable current-topic memory first
- it should only fall back to latest-topic memory if current-topic memory is missing
- it should only ask for a slug when the request remains genuinely ambiguous after checking durable memory
- it should materialize and read `session_start.generated.md` before `runtime_protocol.generated.md`

## Verify

Codex should now be able to:

- use `using-aitp` to decide whether the task must enter AITP before any substantial response
- enter topic work through the AITP runtime surface
- read `session_start.generated.md` first
- read `runtime_protocol.generated.md`
- read `promotion_gate.md` when a candidate is approaching Layer 2
- treat missing conformance as a hard failure for AITP work
- use `aitp-codex` as the stronger wrapper path for coding tasks
- require `aitp request-promotion ...` plus human approval before `aitp promote ...`

## Manual fallback

If you do not want config mutation, the reference skill still lives at:

- `adapters/codex/SKILL.md`

## Remove

See [`docs/UNINSTALL.md`](UNINSTALL.md).
