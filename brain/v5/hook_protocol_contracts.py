"""Runtime hook protocol contracts for AITP v5 adapter packets."""

from __future__ import annotations

from typing import Any

from brain.v5.adapter_protocols import mandatory_hook_protocols
from brain.v5.contracts import (
    ContractError,
    ContractResult,
    _require_bool_value,
    _require_list,
    _require_mapping,
    _require_nonempty_str,
)


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


def validate_codex_hook_bridge(
    payload: dict[str, Any],
    *,
    path: str = "codex_hook_bridge",
) -> ContractResult:
    """Validate the public Codex hook bridge write payload."""

    result = ContractResult()
    _require_mapping(payload, path, result)
    if result.issues:
        return result

    if payload.get("ok") is not True:
        result.add(f"{path}.ok", "must be true")
    if payload.get("kind") != "codex_hook_bridge":
        result.add(f"{path}.kind", "must be 'codex_hook_bridge'")
    if payload.get("runtime") != "codex":
        result.add(f"{path}.runtime", "must be 'codex'")
    if payload.get("source_protocol_field") != "runtime_hook_installation":
        result.add(f"{path}.source_protocol_field", "must be 'runtime_hook_installation'")
    if payload.get("summary_inputs_trusted") is not False:
        result.add(f"{path}.summary_inputs_trusted", "must be false")
    if payload.get("can_update_kernel_state") is not False:
        result.add(f"{path}.can_update_kernel_state", "must be false")

    for key in ("installation_mode", "path"):
        _require_nonempty_str(payload, key, path, result)
    if not isinstance(payload.get("native_installer_available"), bool):
        result.add(f"{path}.native_installer_available", "must be a boolean")

    _require_list(payload.get("guard_calls"), f"{path}.guard_calls", result)
    if isinstance(payload.get("guard_calls"), list):
        for index, guard_call in enumerate(payload["guard_calls"]):
            _validate_codex_guard_call(guard_call, f"{path}.guard_calls[{index}]", result)

    return result


def require_valid_codex_hook_bridge(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a Codex hook bridge payload or raise a contract error."""

    result = validate_codex_hook_bridge(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def validate_claude_code_hook_settings(
    payload: dict[str, Any],
    *,
    path: str = "claude_code_hook_settings",
) -> ContractResult:
    """Validate generated Claude Code hook settings metadata."""

    result = ContractResult()
    _require_mapping(payload, path, result)
    if result.issues:
        return result

    if payload.get("ok") is not True:
        result.add(f"{path}.ok", "must be true")
    if payload.get("kind") != "claude_code_hook_settings":
        result.add(f"{path}.kind", "must be 'claude_code_hook_settings'")
    if payload.get("runtime") != "claude_code":
        result.add(f"{path}.runtime", "must be 'claude_code'")
    if payload.get("source_protocol_field") != "runtime_hook_installation":
        result.add(f"{path}.source_protocol_field", "must be 'runtime_hook_installation'")
    if payload.get("installation_mode") != "native_lifecycle_hooks":
        result.add(f"{path}.installation_mode", "must be 'native_lifecycle_hooks'")
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
    _require_bool_value(payload.get("can_write_trace_events"), True, f"{path}.can_write_trace_events", result)
    for key in ("path",):
        _require_nonempty_str(payload, key, path, result)
    _require_list(payload.get("events"), f"{path}.events", result)
    _require_mapping(payload.get("settings"), f"{path}.settings", result)
    return result


def require_valid_claude_code_hook_settings(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_claude_code_hook_settings(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def validate_hook_trace_event_payload(payload: Any, *, path: str = "hook_trace_event") -> ContractResult:
    """Validate stdout emitted by the post-tool shell hook before persistence."""

    result = ContractResult()
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return result

    if payload.get("kind") != "hook_trace_event":
        result.add(f"{path}.kind", "must be 'hook_trace_event'")
    if payload.get("hook_name") != "post_tool":
        result.add(f"{path}.hook_name", "must be 'post_tool'")
    if payload.get("exit_code") != 0:
        result.add(f"{path}.exit_code", "must be 0")
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _validate_trace_event_payload(payload.get("event"), f"{path}.event", result)
    return result


def require_valid_hook_trace_event_payload(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_hook_trace_event_payload(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def validate_hook_trace_event_record(
    payload: dict[str, Any],
    *,
    path: str = "hook_trace_event_record",
) -> ContractResult:
    """Validate a persisted hook trace-event write result."""

    result = ContractResult()
    _require_mapping(payload, path, result)
    if result.issues:
        return result

    if payload.get("ok") is not True:
        result.add(f"{path}.ok", "must be true")
    if payload.get("kind") != "hook_trace_event_record":
        result.add(f"{path}.kind", "must be 'hook_trace_event_record'")
    if payload.get("source_kind") != "hook_trace_event":
        result.add(f"{path}.source_kind", "must be 'hook_trace_event'")
    if payload.get("source_hook") != "post_tool":
        result.add(f"{path}.source_hook", "must be 'post_tool'")
    _require_bool_value(payload.get("summary_inputs_trusted"), False, f"{path}.summary_inputs_trusted", result)
    _require_bool_value(payload.get("can_update_claim_trust"), False, f"{path}.can_update_claim_trust", result)
    _require_bool_value(payload.get("writes_trace_event"), True, f"{path}.writes_trace_event", result)
    for key in ("event_id", "session_id", "topic_id", "event_type", "risk_level", "trace_path"):
        _require_nonempty_str(payload, key, path, result)
    return result


def require_valid_hook_trace_event_record(payload: dict[str, Any]) -> dict[str, Any]:
    result = validate_hook_trace_event_record(payload)
    if not result.ok:
        raise ContractError(result)
    return payload


def _validate_codex_guard_call(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return

    for key in ("hook_name", "when", "command", "output_kind", "state_mutation"):
        _require_nonempty_str(payload, key, path, result)
    _require_list(payload.get("required_inputs"), f"{path}.required_inputs", result)
    if not isinstance(payload.get("may_block"), bool):
        result.add(f"{path}.may_block", "must be a boolean")


def _validate_trace_event_payload(payload: Any, path: str, result: ContractResult) -> None:
    _require_mapping(payload, path, result)
    if not isinstance(payload, dict):
        return
    if payload.get("kind") != "trace_event":
        result.add(f"{path}.kind", "must be 'trace_event'")
    for key in ("event_id", "session_id", "topic_id", "event_type", "risk_level"):
        _require_nonempty_str(payload, key, path, result)
    _require_mapping(payload.get("payload"), f"{path}.payload", result)
