"""Tool recipe and tool-run records for AITP v5."""

from __future__ import annotations

from brain.v5.ids import prefixed_id, short_hash
from brain.v5.models import ToolRecipeRecord, ToolRunRecord
from brain.v5.paths import WorkspacePaths
from brain.v5.store import write_record


def register_tool_recipe(
    ws: WorkspacePaths,
    *,
    recipe_id: str,
    tool_family: str,
    tool_name: str,
    purpose: str,
    required_inputs: list[str] | None = None,
    expected_outputs: list[str] | None = None,
    invariants: list[str] | None = None,
) -> ToolRecipeRecord:
    """Register a reusable recipe for a formal, numerical, code, or domain tool."""

    record = ToolRecipeRecord(
        recipe_id=recipe_id,
        tool_family=tool_family,
        tool_name=tool_name,
        purpose=purpose,
        required_inputs=required_inputs or [],
        expected_outputs=expected_outputs or [],
        invariants=invariants or [],
    )
    write_record(
        ws.registry_dir("tool_recipes") / f"{recipe_id}.md",
        record,
        body=f"# Tool Recipe\n\n{purpose}\n",
    )
    return record


def record_tool_run(
    ws: WorkspacePaths,
    *,
    recipe_id: str,
    tool_family: str,
    tool_name: str,
    topic_id: str,
    claim_id: str,
    inputs: dict | None = None,
    outputs: dict | None = None,
    environment: dict | None = None,
    evidence_status: str = "unreviewed",
    code_state_ids: list[str] | None = None,
    artifact_ids: list[str] | None = None,
    source_refs: list[str] | None = None,
) -> ToolRunRecord:
    """Record one tool execution as auditable evidence input."""

    run_basis = ":".join(
        [
            recipe_id,
            tool_family,
            tool_name,
            topic_id,
            claim_id,
            short_hash(str(inputs or {}), 8),
            short_hash(str(outputs or {}), 8),
        ]
    )
    run_id = prefixed_id("tool-run", run_basis, max_slug=72)
    record = ToolRunRecord(
        run_id=run_id,
        recipe_id=recipe_id,
        tool_family=tool_family,
        tool_name=tool_name,
        topic_id=topic_id,
        claim_id=claim_id,
        inputs=inputs or {},
        outputs=outputs or {},
        environment=environment or {},
        evidence_status=evidence_status,
        code_state_ids=code_state_ids or [],
        artifact_ids=artifact_ids or [],
        source_refs=source_refs or [],
    )
    write_record(
        ws.registry_dir("tool_runs") / f"{run_id}.md",
        record,
        body=f"# Tool Run\n\nRecipe: `{recipe_id}`\n\nTool: `{tool_family}:{tool_name}`\n",
    )
    return record
