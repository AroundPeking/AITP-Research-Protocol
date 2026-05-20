"""Runtime hook protocol contracts for AITP v5 adapter packets."""

from __future__ import annotations

from typing import Any

from brain.v5.adapter_protocols import mandatory_hook_protocols
from brain.v5.contracts import ContractResult, _require_bool_value, _require_list, _require_mapping


def validate_runtime_hook_protocols(payload: Any, path: str, result: ContractResult) -> None:
    """Validate lifecycle hook metadata advertised to runtime adapters."""

    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return

    for hook_name, expected_protocol in mandatory_hook_protocols().items():
        protocol = payload.get(hook_name)
        _require_mapping(protocol, f"{path}.{hook_name}", result)
        if not isinstance(protocol, dict):
            continue

        for key in ("lifecycle_event", "output_kind", "state_mutation"):
            if protocol.get(key) != expected_protocol[key]:
                result.add(f"{path}.{hook_name}.{key}", f"must be {expected_protocol[key]!r}")

        for key in ("command", "required_inputs"):
            _require_list(protocol.get(key), f"{path}.{hook_name}.{key}", result)
            if isinstance(protocol.get(key), list) and protocol[key] != expected_protocol[key]:
                result.add(f"{path}.{hook_name}.{key}", f"must be {expected_protocol[key]!r}")

        _require_bool_value(
            protocol.get("may_block"),
            expected_protocol["may_block"],
            f"{path}.{hook_name}.may_block",
            result,
        )
        if protocol.get("block_exit_code") != expected_protocol["block_exit_code"]:
            result.add(
                f"{path}.{hook_name}.block_exit_code",
                f"must be {expected_protocol['block_exit_code']!r}",
            )
        _require_bool_value(
            protocol.get("summary_inputs_trusted"),
            expected_protocol["summary_inputs_trusted"],
            f"{path}.{hook_name}.summary_inputs_trusted",
            result,
        )


def validate_runtime_hook_installation(
    payload: Any,
    path: str,
    runtime: Any,
    runtime_hook_protocols: Any,
    result: ContractResult,
) -> None:
    """Validate runtime hook installation metadata against hook protocols."""

    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    if not isinstance(runtime, str) or not isinstance(runtime_hook_protocols, dict):
        return

    from brain.v5.hook_install_templates import build_runtime_hook_installation

    expected = build_runtime_hook_installation(runtime, runtime_hook_protocols)
    if payload != expected:
        result.add(path, "must match build_runtime_hook_installation(runtime, runtime_hook_protocols)")
