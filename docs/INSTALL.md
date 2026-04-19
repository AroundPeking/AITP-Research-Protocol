# Install Guide

This is the consolidated install index for AITP.

## Common baseline

All supported runtime surfaces share the same kernel install step:

```bash
python -m pip install aitp-kernel
aitp --version
aitp doctor
```

If `aitp` is not on `PATH` yet on Windows-native and you are working from a
local checkout, use the repo-local launcher:

```cmd
scripts\aitp-local.cmd doctor
```

Common prerequisites:

- Python 3.10+
- the runtime surface you actually want to use locally
- Git only if you choose a repo-backed adapter or contributor workflow
- your durable personal kernel should live under `~/.aitp/kernel`

The default user-facing install expects your local topic state, runtime
projections, and private research data to live under `~/.aitp/kernel`
(`%USERPROFILE%\\.aitp\\kernel` on Windows).
The repo itself should stay project code, protocol, and public docs only.

The runtime package currently declares `python_requires=">=3.10"` in
`research/knowledge-hub/setup.py`.

## Optional PaperQA integration

AITP can expose a PaperQA-backed topic consultation path without making it a
hard dependency of the kernel.

If you want `aitp consult-paperqa`, use a Python 3.11+ environment and install:

```bash
python -m pip install "aitp-kernel[paperqa]"
```

Important boundary:

- the core AITP kernel still supports Python 3.10+
- the optional `paperqa` extra requires Python 3.11+
- `consult-paperqa` also expects provider-prefixed LiteLLM model names such as
  `anthropic/claude-3-5-sonnet-20240620`

## Contributor / local-dev install

If you are changing this repository itself, keep the editable install lane:

```bash
python -m pip install -e research/knowledge-hub
aitp doctor
```

If you also want the optional PaperQA integration in local development, use:

```bash
python -m pip install -e "research/knowledge-hub[paperqa]"
```

That path is still the right one for runtime development, local patching, and
repo-backed adapter workflows.
Keep your day-to-day research kernel outside the repo and point local commands
at it with `--kernel-root` when you do not want to use the default user kernel.

## Pick your runtime

- Codex: [`docs/INSTALL_CODEX.md`](INSTALL_CODEX.md)
- OpenCode: [`docs/INSTALL_OPENCODE.md`](INSTALL_OPENCODE.md)
- Claude Code: [`docs/INSTALL_CLAUDE_CODE.md`](INSTALL_CLAUDE_CODE.md)
- OpenClaw: [`docs/INSTALL_OPENCLAW.md`](INSTALL_OPENCLAW.md)

## Migration and cleanup

- older editable-install migration:
  [`docs/MIGRATE_LOCAL_INSTALL.md`](MIGRATE_LOCAL_INSTALL.md)
- PyPI build and publish workflow:
  [`docs/PUBLISH_PYPI.md`](PUBLISH_PYPI.md)
- adapter/runtime removal:
  [`docs/UNINSTALL.md`](UNINSTALL.md)

## Verification

After installation, run:

```bash
aitp doctor
aitp doctor --json
```

`aitp doctor` now renders a front-door install summary for Codex, Claude Code,
and OpenCode, while treating OpenClaw as a specialized lane.
For Claude Code, that readiness now includes both SessionStart assets and the
native AITP MCP registration.
That readiness view is about install/bootstrap truth. It is not the same thing
as deep-execution parity.

For machine-readable verification, inspect:

- `runtime_convergence.front_door_runtimes_converged`
- `deep_execution_parity.baseline_status`
- `deep_execution_parity.pending_targets`
- `full_convergence_repair.command`
- `runtime_support_matrix.runtimes.codex.status`
- `runtime_support_matrix.runtimes.claude_code.status`
- `runtime_support_matrix.runtimes.opencode.status`
- `runtime_support_matrix.runtimes.<runtime>.remediation`
- `runtime_support_matrix.deep_execution_parity.runtimes.<runtime>.status`

If a runtime is not `ready`, use that runtime's
`runtime_support_matrix.runtimes.<runtime>.remediation.command`, then rerun
`runtime_support_matrix.runtimes.<runtime>.remediation.followup_command`.

If a runtime is front-door `ready` but still not deep-execution equivalent to
Codex, inspect the shared parity harness command from
`runtime_support_matrix.deep_execution_parity.runtimes.<runtime>.acceptance_command`.

Use the runtime-specific install docs above when you need platform-specific
bootstrap details after the shared kernel install succeeds.

For the shared first-run path after install verification, continue with:

- [`docs/QUICKSTART.md`](QUICKSTART.md)
