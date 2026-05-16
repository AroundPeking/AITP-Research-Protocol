"""Code workspace and source-state provenance for AITP v5."""

from __future__ import annotations

from brain.v5.ids import prefixed_id, short_hash
from brain.v5.models import CodeStateRecord, CodeWorkspaceRecord
from brain.v5.paths import WorkspacePaths
from brain.v5.store import write_record


def record_code_workspace(
    ws: WorkspacePaths,
    *,
    topic_id: str,
    session_id: str,
    repo_id: str,
    worktree_path: str,
    branch_name: str,
    base_commit: str,
    purpose: str,
    upstream_tracking_branch: str = "",
    write_scope: list[str] | None = None,
    active_claim: str = "",
    active_attempt: str = "",
    status: str = "active",
    cleanup_plan: str = "",
) -> CodeWorkspaceRecord:
    """Record an isolated code workspace used by a topic/session."""

    workspace_id = prefixed_id("code-workspace", f"{repo_id}:{topic_id}:{session_id}:{branch_name}")
    record = CodeWorkspaceRecord(
        workspace_id=workspace_id,
        topic_id=topic_id,
        session_id=session_id,
        repo_id=repo_id,
        worktree_path=worktree_path,
        branch_name=branch_name,
        base_commit=base_commit,
        purpose=purpose,
        upstream_tracking_branch=upstream_tracking_branch,
        write_scope=write_scope or [],
        active_claim=active_claim,
        active_attempt=active_attempt,
        status=status,
        cleanup_plan=cleanup_plan,
    )
    write_record(
        ws.registry_dir("code_workspaces") / f"{workspace_id}.md",
        record,
        body=f"# Code Workspace\n\nRepository: `{repo_id}`\n\nPurpose: {purpose}\n",
    )
    return record


def record_code_state(
    ws: WorkspacePaths,
    *,
    repo_id: str,
    upstream_remote: str,
    upstream_branch: str,
    upstream_commit: str,
    local_branch: str,
    worktree_path: str,
    dirty: bool,
    patch_id: str = "",
    diff_hash: str = "",
    build_config: dict | None = None,
    runtime_environment: dict | None = None,
    linked_records: dict | None = None,
    known_divergence: str = "",
) -> CodeStateRecord:
    """Record the exact code state used for a code-dependent result."""

    basis = ":".join(
        [
            repo_id,
            upstream_remote,
            upstream_branch,
            upstream_commit,
            local_branch,
            patch_id,
            diff_hash,
        ]
    )
    suffix = short_hash(basis, 8)
    code_state_id = f"code-state-{repo_id}-{suffix}"
    record = CodeStateRecord(
        code_state_id=code_state_id,
        repo_id=repo_id,
        upstream_remote=upstream_remote,
        upstream_branch=upstream_branch,
        upstream_commit=upstream_commit,
        local_branch=local_branch,
        worktree_path=worktree_path,
        dirty=dirty,
        patch_id=patch_id,
        diff_hash=diff_hash,
        build_config=build_config or {},
        runtime_environment=runtime_environment or {},
        linked_records=linked_records or {},
        known_divergence=known_divergence,
    )
    write_record(
        ws.registry_dir("code_states") / f"{code_state_id}.md",
        record,
        body=(
            "# Code State\n\n"
            f"Repository: `{repo_id}`\n\n"
            f"Upstream: `{upstream_remote}/{upstream_branch}` at `{upstream_commit}`\n"
        ),
    )
    return record
