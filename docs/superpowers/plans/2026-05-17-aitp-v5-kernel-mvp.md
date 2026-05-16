# AITP v5 Kernel MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Build the first working AITP v5 kernel slice: filesystem store, session binding, claim state, flow profile resolution, dynamic physics questions, execution brief, and code provenance records.

**Architecture:** Add an isolated `brain/v5/` package rather than expanding the legacy MCP monolith. The kernel writes Markdown+YAML artifacts under a `.aitp/` workspace and exposes pure Python functions that MCP, CLI, hooks, and skills can call later.

**Tech Stack:** Python standard library, `dataclasses`, `pathlib`, `json`, `hashlib`, `yaml`, `pytest`.

---

## Baseline

Worktree: `C:\Users\samur\.config\superpowers\worktrees\AITP-Research-Protocol\aitp-v5-kernel-mvp`

Branch: `codex/aitp-v5-kernel-mvp`

Baseline command:

```bash
pytest tests/ -q
```

Observed before v5 changes:

```text
72 failed, 113 passed, 2 warnings
```

The MVP uses focused tests under `tests/test_v5_kernel.py` because legacy failures are pre-existing and mostly involve old MCP wrapper compatibility and old L2 graph expectations.

## File Structure

Create:

- `brain/v5/__init__.py`: public kernel exports.
- `brain/v5/ids.py`: stable slug and id helpers.
- `brain/v5/markdown.py`: Markdown+YAML parsing and atomic writes.
- `brain/v5/paths.py`: `.aitp` workspace path model and directory creation.
- `brain/v5/models.py`: dataclasses and enums for v5 records.
- `brain/v5/store.py`: typed object write/read/list helpers.
- `brain/v5/workspace.py`: workspace, context, topic, claim, and session binding operations.
- `brain/v5/flow.py`: Autopilot/Guided/Research/Adversarial flow resolver.
- `brain/v5/question_engine.py`: deterministic state-conditioned physics question generation.
- `brain/v5/brief.py`: execution brief builder.
- `brain/v5/code.py`: code workspace, code state, and upstream comparison records.
- `tests/test_v5_kernel.py`: focused TDD tests for the MVP slice.

Do not modify in this MVP:

- `brain/mcp_server.py`
- `brain/cli/__init__.py`
- existing legacy tests

## Task 1: Workspace Store And Path Kernel

**Files:**

- Create: `brain/v5/__init__.py`
- Create: `brain/v5/ids.py`
- Create: `brain/v5/markdown.py`
- Create: `brain/v5/paths.py`
- Create: `brain/v5/store.py`
- Test: `tests/test_v5_kernel.py`

- [x] **Step 1: Write failing tests**

Tests:

```python
def test_init_workspace_creates_v5_layout(tmp_path):
    from brain.v5.workspace import init_workspace
    ws = init_workspace(tmp_path)
    assert ws.root == tmp_path / ".aitp"
    assert (ws.root / "registry" / "claims").exists()

def test_markdown_store_round_trips_frontmatter_and_body(tmp_path):
    from brain.v5.markdown import read_md, write_md
    path = tmp_path / "record.md"
    write_md(path, {"kind": "test", "value": 3}, "# Body\n\nHello\n")
    fm, body = read_md(path)
    assert fm == {"kind": "test", "value": 3}
    assert "Hello" in body
```

- [x] **Step 2: Run red**

Run:

```bash
pytest tests/test_v5_kernel.py::test_init_workspace_creates_v5_layout tests/test_v5_kernel.py::test_markdown_store_round_trips_frontmatter_and_body -q
```

Expected: FAIL because `brain.v5` does not exist.

- [x] **Step 3: Implement minimal store**

Implement atomic Markdown writes and `WorkspacePaths.ensure_layout()`.

- [x] **Step 4: Verify green**

Run the same tests. Expected: PASS.

## Task 2: Topic, Context, And Session Binding

**Files:**

- Create/modify: `brain/v5/models.py`
- Modify: `brain/v5/workspace.py`
- Modify: `brain/v5/store.py`
- Test: `tests/test_v5_kernel.py`

- [x] **Step 1: Write failing test**

Test:

```python
def test_topic_context_and_session_binding_are_session_local(tmp_path):
    from brain.v5.workspace import bind_session, create_context, create_topic, get_session_binding, init_workspace
    ws = init_workspace(tmp_path)
    create_context(ws, "topological-order", title="Topological Order")
    create_topic(ws, "fqhe-learning", context_id="topological-order", title="FQHE Learning")
    create_topic(ws, "librpa-gw", context_id="gw-methods", title="LibRPA GW")
    bind_session(ws, session_id="s1", topic_id="fqhe-learning", context_id="topological-order")
    bind_session(ws, session_id="s2", topic_id="librpa-gw", context_id="gw-methods")
    assert get_session_binding(ws, "s1").topic_id == "fqhe-learning"
    assert get_session_binding(ws, "s2").topic_id == "librpa-gw"
```

- [x] **Step 2: Run red**

Run:

```bash
pytest tests/test_v5_kernel.py::test_topic_context_and_session_binding_are_session_local -q
```

Expected: FAIL because session functions do not exist.

- [x] **Step 3: Implement records**

Write:

```text
.aitp/contexts/<context_id>/context.md
.aitp/topics/<topic_id>/topic.md
.aitp/runtime/sessions/<session_id>.md
```

- [x] **Step 4: Verify green**

Run the test. Expected: PASS.

## Task 3: Claims And Flow Resolver

**Files:**

- Modify: `brain/v5/models.py`
- Modify: `brain/v5/workspace.py`
- Create: `brain/v5/flow.py`
- Test: `tests/test_v5_kernel.py`

- [x] **Step 1: Write failing test**

Test:

```python
def test_flow_resolver_keeps_trusted_recipe_light_and_new_claim_heavy(tmp_path):
    from brain.v5.flow import resolve_flow_profile
    from brain.v5.workspace import create_claim, init_workspace
    ws = init_workspace(tmp_path)
    routine = create_claim(ws, topic_id="librpa-gw", statement="Si G0W0 benchmark stays within trusted tolerance.", evidence_profile="code_method", confidence_state="locally_checked", active_uncertainty="routine benchmark rerun", recipe_id="librpa-si-g0w0")
    novel = create_claim(ws, topic_id="fqhe-learning", statement="The proposed finite-size signature detects fractional charge.", evidence_profile="toy_numeric", confidence_state="hypothesis", active_uncertainty="new physical mechanism")
    assert resolve_flow_profile(routine).profile == "autopilot"
    assert resolve_flow_profile(novel).profile == "research"
```

- [x] **Step 2: Run red**

Run:

```bash
pytest tests/test_v5_kernel.py::test_flow_resolver_keeps_trusted_recipe_light_and_new_claim_heavy -q
```

Expected: FAIL because flow functions do not exist.

- [x] **Step 3: Implement resolver**

Rules:

- `hypothesis` or `coherent` -> `research`
- recipe plus routine/rerun/benchmark uncertainty -> `autopilot`
- failure/contradiction/promotion/expensive -> `adversarial`
- fallback -> `guided`

- [x] **Step 4: Verify green**

Run the test. Expected: PASS.

## Task 4: Dynamic Physics Question Engine

**Files:**

- Create: `brain/v5/question_engine.py`
- Modify: `brain/v5/models.py`
- Test: `tests/test_v5_kernel.py`

- [x] **Step 1: Write failing test**

Test:

```python
def test_question_engine_generates_state_conditioned_questions():
    from brain.v5.models import ClaimRecord, FlowDecision
    from brain.v5.question_engine import generate_questions
    claim = ClaimRecord(claim_id="claim-fqhe", topic_id="fqhe", statement="Entanglement spectrum identifies the FQHE edge theory.", evidence_profile="toy_numeric", confidence_state="hypothesis", active_uncertainty="which finite-size signature is reliable")
    flow = FlowDecision(profile="research", reason="new claim", escalation_triggers=[])
    questions = generate_questions(claim, flow, object_relations=["entanglement_spectrum measures edge_mode"])
    text = "\n".join(q.question for q in questions)
    assert "relation" in text.lower()
    assert "failure" in text.lower() or "wrong" in text.lower()
    assert any(q.target_claim == "claim-fqhe" for q in questions)
```

- [x] **Step 2: Run red**

Run:

```bash
pytest tests/test_v5_kernel.py::test_question_engine_generates_state_conditioned_questions -q
```

Expected: FAIL because question engine does not exist.

- [x] **Step 3: Implement deterministic question generation**

Generate 2-5 `QuestionRecord` objects using claim, flow, evidence profile, active uncertainty, and object relations.

- [x] **Step 4: Verify green**

Run the test. Expected: PASS.

## Task 5: Execution Brief Builder

**Files:**

- Create: `brain/v5/brief.py`
- Modify: `brain/v5/workspace.py`
- Test: `tests/test_v5_kernel.py`

- [x] **Step 1: Write failing test**

Test:

```python
def test_execution_brief_combines_session_claim_flow_and_questions(tmp_path):
    from brain.v5.brief import build_execution_brief
    from brain.v5.workspace import bind_session, create_claim, create_topic, init_workspace
    ws = init_workspace(tmp_path)
    create_topic(ws, "fqhe", context_id="topological-order", title="FQHE")
    claim = create_claim(ws, topic_id="fqhe", statement="Entanglement spectrum identifies the edge theory.", evidence_profile="toy_numeric", confidence_state="hypothesis", active_uncertainty="finite-size reliability")
    bind_session(ws, "s1", topic_id="fqhe", context_id="topological-order", active_claim=claim.claim_id)
    brief = build_execution_brief(ws, "s1")
    assert brief["session"]["topic_id"] == "fqhe"
    assert brief["current_focus"]["active_claim"] == claim.claim_id
    assert brief["flow_profile"]["profile"] == "research"
    assert brief["mandatory_reflection"]
    assert "forbidden_now" in brief
```

- [x] **Step 2: Run red**

Run:

```bash
pytest tests/test_v5_kernel.py::test_execution_brief_combines_session_claim_flow_and_questions -q
```

Expected: FAIL because brief builder does not exist.

- [x] **Step 3: Implement brief builder**

Return `session`, `current_focus`, `flow_profile`, `known_context`, `mandatory_reflection`, `next_action_candidates`, `forbidden_now`, and `human_checkpoint`.

- [x] **Step 4: Verify green**

Run the test. Expected: PASS.

## Task 6: Code Worktree Provenance

**Files:**

- Create: `brain/v5/code.py`
- Modify: `brain/v5/models.py`
- Modify: `brain/v5/store.py`
- Test: `tests/test_v5_kernel.py`

- [x] **Step 1: Write failing test**

Test:

```python
def test_code_state_and_workspace_records_make_code_results_reproducible(tmp_path):
    from brain.v5.code import record_code_state, record_code_workspace
    from brain.v5.workspace import init_workspace
    ws = init_workspace(tmp_path)
    cw = record_code_workspace(ws, topic_id="librpa-gw", session_id="s1", repo_id="librpa", worktree_path="D:/worktrees/librpa/headwing-test", branch_name="topic/headwing-test", base_commit="abc123", purpose="test head-wing patch")
    cs = record_code_state(ws, repo_id="librpa", upstream_remote="origin", upstream_branch="master", upstream_commit="abc123", local_branch="topic/headwing-test", worktree_path=cw.worktree_path, dirty=False, patch_id="patch-headwing-v1", build_config={"compiler": "gcc", "cmake_options": ["-DUSE_MPI=ON"]})
    assert cs.code_state_id.startswith("code-state-librpa-")
    assert (ws.root / "registry" / "code_states" / f"{cs.code_state_id}.md").exists()
```

- [x] **Step 2: Run red**

Run:

```bash
pytest tests/test_v5_kernel.py::test_code_state_and_workspace_records_make_code_results_reproducible -q
```

Expected: FAIL because code provenance functions do not exist.

- [x] **Step 3: Implement code provenance records**

Write:

```text
.aitp/registry/code_workspaces/<workspace_id>.md
.aitp/registry/code_states/<code_state_id>.md
```

- [x] **Step 4: Verify green**

Run the test. Expected: PASS.

## Task 7: Verification And Commit

- [x] **Step 1: Run focused v5 tests**

```bash
pytest tests/test_v5_kernel.py -q
```

Expected: PASS.

- [x] **Step 2: Run small existing safety subset**

```bash
pytest tests/test_foundation_safety.py::TestTopicsDirResolution tests/test_foundation_safety.py::TestSlugValidation -q
```

Expected: PASS.

- [x] **Step 3: Commit and push branch**

```bash
git add docs/superpowers/plans/2026-05-17-aitp-v5-kernel-mvp.md brain/v5 tests/test_v5_kernel.py
git commit -m "feat: add aitp v5 kernel mvp"
git push origin codex/aitp-v5-kernel-mvp
```

## Self-Review

Spec coverage:

- Filesystem store: Task 1.
- Multi-session runtime binding: Task 2.
- Claim/evidence/flow profile: Task 3.
- Dynamic physics questions: Task 4.
- Execution brief: Task 5.
- Code worktree provenance: Task 6.

Intentional gaps:

- MCP wrappers, CLI commands, migration, persistent object-relation graph, and subagent auditor packets are deferred until the kernel contract is stable.

