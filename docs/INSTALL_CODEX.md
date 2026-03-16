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

## Install the Codex wrapper

```bash
aitp install-agent --agent codex --scope user
```

This installs:

- the `aitp-runtime` skill into your active Codex skill roots
- the `aitp` MCP registration when supported

If you want a separate theory workspace to run bare `codex` in an AITP-first
way, install the project skill into that workspace root:

```bash
aitp install-agent --agent codex --scope project --target-root /path/to/theory-workspace
```

That writes `.agents/skills/aitp-runtime/` under the target workspace.

## Recommended entrypoints

For normal topic work:

```bash
aitp loop --topic "<topic>" --human-request "<task>"
```

For Codex-driven implementation or execution:

```bash
aitp-codex --topic-slug <topic_slug> "<task>"
```

## Verify

Codex should now be able to:

- enter topic work through the AITP runtime surface
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
