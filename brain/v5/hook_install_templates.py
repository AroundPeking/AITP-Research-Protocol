"""Runtime hook installation templates derived from v5 hook protocols."""

from __future__ import annotations

from copy import deepcopy
from typing import Any


_INSTALLATION_MODES = {
    "codex": "explicit_guard_calls",
    "claude_code": "native_lifecycle_hooks",
    "opencode": "plugin_bridge",
}


def build_runtime_hook_installation(runtime: str, runtime_hook_protocols: dict[str, Any]) -> dict[str, Any]:
    """Build runtime-facing hook installation metadata from hook protocols."""

    normalized_runtime = _normalize_runtime(runtime)
    return {
        "kind": "runtime_hook_installation_template",
        "runtime": normalized_runtime,
        "source_protocol_field": "runtime_hook_protocols",
        "installation_mode": _INSTALLATION_MODES[normalized_runtime],
        "native_installer_available": False,
        "summary_inputs_trusted": False,
        "hooks": [
            _hook_template(hook_name, runtime_hook_protocols[hook_name])
            for hook_name in ("pre_commit", "pre_tool", "post_tool")
        ],
        "adapter_rule": "derive_commands_from_runtime_hook_protocols",
    }


def _hook_template(hook_name: str, protocol: dict[str, Any]) -> dict[str, Any]:
    return {
        "hook_name": hook_name,
        "lifecycle_event": protocol["lifecycle_event"],
        "command": deepcopy(protocol["command"]),
        "required_inputs": deepcopy(protocol["required_inputs"]),
        "output_kind": protocol["output_kind"],
        "may_block": protocol["may_block"],
        "state_mutation": protocol["state_mutation"],
    }


def _normalize_runtime(runtime: str) -> str:
    value = runtime.strip().lower().replace("-", "_")
    if value in _INSTALLATION_MODES:
        return value
    return "codex"
