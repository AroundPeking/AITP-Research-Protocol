# W1+W2 Implementation Plan

Code-change implementation plan for the first two workstreams from the
[physicist-usable protocol surface design](2026-04-18-aitp-physicist-usable-protocol-surface-design.md).

All paths are relative to `research/knowledge-hub/`.

## Code trace summary

### W1: Where generic contract defaults originate

The active research contract is constructed in
`knowledge_hub/topic_shell_support.py`, method
`_build_research_question_shell_payload` (around line 1689). The payload dict
is built with `_coalesce_list(existing_value, default_value)` — if existing
is non-empty it wins; otherwise the generic default is used.

Generic defaults that must become lane-aware:

| Field | Location | Current default | Problem |
|-------|----------|----------------|---------|
| `observables` | `topic_shell_support.py:1760-1765` | "Declared candidate ids, bounded claims, and validation outcomes." | Identical across all lanes; zero physics content |
| `target_claims` | `topic_shell_support.py:1643-1646` | `[candidate_id]` or `[action_id]` | Runtime-internal identifiers, not scientific claims |
| `deliverables` | `topic_shell_support.py:1647-1651` | "Persist the active research question, validation route, and bounded next action as durable runtime artifacts." | Identical boilerplate across all lanes |

The renderer is `knowledge_hub/kernel_markdown_renderers.py:237`
(`render_research_question_contract_markdown`) — it renders from the payload
dict into markdown. No change needed there; the fix is upstream in default
generation.

The `_coalesce_list` pattern means: if the existing contract already has a
non-empty value, it is preserved. The fix only needs to improve the *fallback*
defaults, so existing human-curated contracts are never overwritten.

### W2: Where `inspect_resume_state` originates

Three injection points in `runtime/scripts/orchestrate_topic.py`:

| Line | Trigger | Summary string |
|------|---------|---------------|
| 1439 | post-promotion, no further actions | "Inspect the promoted Layer 2 writeback artifacts and current topic-completion surface before opening another bounded route." |
| 1539 | should_advance_past_staged_l2_review is False | "Inspect the compiled L1 vault before continuing." or "Inspect the current L2 staging manifest before continuing." |
| 1556 | queue is empty (no pending rows anywhere) | "No explicit pending actions were found; inspect the runtime resume state." |

The decision pipeline in `runtime/scripts/decide_next_action.py`:

- `select_default_action` (line 605): returns `None, None` when queue is empty
- `build_next_action_decision` (line 817): sets `decision_mode = "no_action"` when default is None
- `build_next_action_markdown` (line 967): renders the markdown; when selected is None, outputs "No action is currently selected."

The summary string at line 1557 ("No explicit pending actions were found; inspect
the runtime resume state.") is the worst offender. Lines 1439 and 1539 are
better but still use runtime jargon.

---

## W1: Lane-aware research-contract semantics

### Step 1: Write failing tests

**File:** `tests/test_lane_contract_defaults.py` (new)

Tests:

1. `test_formal_derivation_observables_contain_physics_terms` — given
   `template_mode=formal_theory, research_mode=formal_derivation`, the
   lane-aware observables default list contains at least one term from
   {"theorem", "closure", "proof", "derivation", "formal"} (not an exact
   match; use substring check).

2. `test_toy_model_observables_contain_model_terms` — given
   `template_mode=code_method, research_mode=exploratory_general` with topic
   content suggesting toy model, observables default contains at least one
   term from {"model", "observable", "finite-size", "regime", "benchmark"}.

3. `test_first_principles_observables_contain_method_terms` — given
   `template_mode=code_method, research_mode=exploratory_general` with topic
   content suggesting first-principles, observables default contains at
   least one term from {"code", "method", "convergence", "basis set", "grid"}.

4. `test_target_claims_not_action_id_pattern` — for all lanes, the
   target_claims default does not match the regex `^action:[^:]+:\d+$`.

5. `test_deliverables_not_generic_template` — for all lanes, the deliverables
   default is not identical to the current generic string
   "Persist the active research question, validation route, and bounded
   next action as durable runtime artifacts."

6. `test_existing_contract_values_preserved` — when existing_observables is
   non-empty, the result equals existing_observables (no overwrite).

7. `test_lane_unrecognized_falls_back_to_generic` — when lane cannot be
   determined, the result is the current generic default (no regression).

### Step 2: Create the lane-defaults helper

**File:** `knowledge_hub/lane_contract_defaults.py` (new)

Responsibilities:

- `detect_lane(template_mode, research_mode, topic_content_hints) -> str`
  — returns one of `"formal_derivation"`, `"toy_model"`,
  `"first_principles"`, or `"generic"`.
  Detection logic:
  - `template_mode == "formal_theory"` → `formal_derivation`
  - `template_mode == "code_method"` and topic content has
    toy-model signals (model family, lattice, hamiltonian, small system)
    → `toy_model`
  - `template_mode == "code_method"` and topic content has first-principles
    signals (DFT, GW, QMC, basis set, convergence) → `first_principles`
  - otherwise → `generic`

- `lane_observables(lane, topic_context) -> list[str]`
  — returns lane-specific observables defaults.

- `lane_target_claims(lane, topic_context, candidate_rows, selected_action) -> list[str]`
  — returns lane-specific target claims. When `candidate_rows` has real
  claims, use those; otherwise synthesize from `topic_context.question`.

- `lane_deliverables(lane, topic_context) -> list[str]`
  — returns lane-specific deliverables.

The `topic_context` parameter is a lightweight dict with keys like
`question`, `scope`, `source_basis_refs` — extracted from the existing
research contract and source index.

### Step 3: Wire into `topic_shell_support.py`

**File:** `knowledge_hub/topic_shell_support.py`

Changes at lines 1643-1768:

```python
# Before (line 1643-1646):
target_claim_defaults = self._dedupe_strings(
    [str(row.get("candidate_id") or "").strip() for row in candidate_rows ...]
    or [str((selected_pending_action or {}).get("action_id") or "").strip()]
)

# After:
from .lane_contract_defaults import (
    detect_lane, lane_observables, lane_target_claims, lane_deliverables,
)

lane = detect_lane(
    template_mode=template_mode,
    research_mode=research_mode,
    topic_content_hints={
        "question": active_question,
        "scope": existing_research.get("scope") or [],
        "source_basis_refs": self._research_source_basis_refs(topic_slug=topic_slug, source_rows=source_rows),
        "l1_source_intake": l1_source_intake,
    },
)
target_claim_defaults = lane_target_claims(
    lane=lane,
    topic_context={"question": active_question, "scope": existing_research.get("scope") or []},
    candidate_rows=candidate_rows,
    selected_action=selected_pending_action,
)
```

Similarly for `observables` (line 1760) and `deliverables` (line 1647).

### Step 4: Run tests and verify

- `tests/test_lane_contract_defaults.py` — all pass
- `tests/test_aitp_service.py` — existing contract rendering tests pass
- Spot-check 2-3 real topic contracts to confirm improvement

### File ownership

| File | Action | Owner |
|------|--------|-------|
| `knowledge_hub/lane_contract_defaults.py` | Create | W1 |
| `knowledge_hub/topic_shell_support.py` | Modify lines 1643-1768 | W1 |
| `tests/test_lane_contract_defaults.py` | Create | W1 |

---

## W2: Research-facing next-action synthesis

### Step 1: Write failing tests

**File:** `tests/test_next_action_synthesis.py` (new)

Tests:

1. `test_empty_queue_research_synthesis` — given a topic with non-empty
   `research_question.contract` question field and empty action queue,
   `synthesize_research_next_action` returns a summary that contains at
   least one noun/phrase from the contract question, not the string
   "inspect the runtime resume state."

2. `test_empty_queue_truly_empty_topic` — given a topic with no contract,
   no source index, no run directory, the result is labelled as a bootstrap
   action (action_type can remain `inspect_resume_state` but summary
   contains "bootstrap" or "initialize").

3. `test_generic_l1_summary_rephrased` — given a queue entry with summary
   "Inspect the compiled L1 vault before continuing." and a contract with
   a real physics question, the synthesis returns a summary containing at
   least one physics-specific term from the contract.

4. `test_post_promotion_summary_keeps_content` — given a queue entry with
   summary "Inspect the promoted Layer 2 writeback artifacts...", the
   synthesis returns a summary that still mentions L2 promotion but is
   phrased as research work, not shell maintenance.

5. `test_no_contract_question_falls_back` — when no contract question exists,
   the synthesis falls back to a generic but non-runtime-jargon summary.

### Step 2: Create the synthesis helper

**File:** `knowledge_hub/next_action_synthesis.py` (new)

Responsibilities:

- `synthesize_research_next_action(
    topic_slug, research_contract, source_index, queue_head, topic_state
  ) -> dict` with keys `summary`, `action_type`, `is_bootstrap`.

Logic:

1. If `research_contract.question` is non-empty:
   - Extract up to 3 key noun phrases from the question
   - If queue is empty (root cause A): return summary like
     "Bootstrap the research workflow for [key phrase] before continuing."
   - If queue has entry with generic summary (root cause B): return summary
     like "Recover [missing thing from contract] for [key phrase] before
     continuing interpretation."

2. If `research_contract.question` is empty but source index is non-empty:
   - Return "Register the source basis for [topic slug] and formulate the
     bounded research question."

3. If everything is empty (true bootstrap):
   - Return "Initialize the research workspace for this topic."
   - Set `is_bootstrap = True`

4. The function never returns the literal string "inspect the runtime
   resume state" as the summary.

### Step 3: Wire into `orchestrate_topic.py`

**File:** `runtime/scripts/orchestrate_topic.py`

Changes at lines 1433-1450 (post-promotion inspect):
```python
# Before (line 1439):
"action_type": "inspect_resume_state",
"summary": "Inspect the promoted Layer 2 writeback artifacts...",

# After:
from knowledge_hub.next_action_synthesis import synthesize_research_next_action
synth = synthesize_research_next_action(
    topic_slug=topic_state["topic_slug"],
    research_contract=research_contract,
    source_index=source_index,
    queue_head=None,  # post-promotion, no further queue head
    topic_state=topic_state,
)
{
    ...
    "action_type": "inspect_resume_state",  # keep for internal compat
    "summary": synth["summary"],
    ...
}
```

Changes at lines 1533-1547 (L1/L2 staging inspect):
Same pattern — call `synthesize_research_next_action` with the queue head
and contract, use the returned summary.

Changes at lines 1549-1564 (empty queue fallback):
Same pattern — this is the most important one since it generates the worst
summary.

The `research_contract` and `source_index` need to be available at these
points. They should already be loaded earlier in the function; if not, add
loading calls.

### Step 4: Wire into `decide_next_action.py` markdown renderer

**File:** `runtime/scripts/decide_next_action.py`

At `build_next_action_markdown` (line 967): no change needed here because
the summary string is already in the payload dict by the time it reaches
this function. The fix is upstream in `orchestrate_topic.py`.

However, for the heuristic path in `build_next_action_decision` (line 817),
when `decision_mode == "no_action"`, the reason string at line 824
("No pending actions remain, so there is nothing to dispatch.") should be
improved to a research-shaped sentence. This requires passing the research
contract to `build_next_action_decision`.

### Step 5: Run tests and verify

- `tests/test_next_action_synthesis.py` — all pass
- `tests/test_runtime_scripts.py` — existing decide_next_action tests pass
- `tests/test_aitp_service.py` — existing orchestration tests pass
- Spot-check 2-3 real topic `next_action_decision.md` files

### File ownership

| File | Action | Owner |
|------|--------|-------|
| `knowledge_hub/next_action_synthesis.py` | Create | W2 |
| `runtime/scripts/orchestrate_topic.py` | Modify lines 1433-1564 | W2 |
| `runtime/scripts/decide_next_action.py` | Minor modify line 824 | W2 |
| `tests/test_next_action_synthesis.py` | Create | W2 |

---

## Execution order

```
W1-Step1 (tests)  ──→  W1-Step2 (helper)  ──→  W1-Step3 (wire)  ──→  W1-Step4 (verify)
                          │
                          └── W1 helper is a dependency for W2 synthesis (topic_context extraction)

W2-Step1 (tests)  ──→  W2-Step2 (helper)  ──→  W2-Step3 (wire orchestrate)  ──→  W2-Step4 (minor)  ──→  W2-Step5 (verify)
```

W1 and W2 can proceed in parallel at the test-writing and helper-creation
phases. The wire-in steps are sequential within each workstream but independent
across workstreams.

## Bundle sync

Both workstreams touch files under `knowledge_hub/` and `runtime/scripts/`.
The `_bundle/` directory under `knowledge_hub/` contains copies of runtime
scripts. After all changes land, the bundle must be regenerated to stay in
sync. This is a separate manual or CI step, not part of the TDD cycle.

## Risk notes

1. **_coalesce_list contract**: The existing `_coalesce_list` returns
   `existing` if truthy, else `defaults`. Lane-aware defaults replace the
   `defaults` argument only. Existing human-curated values are never
   overwritten. This is safe.

2. **Lane detection heuristics**: The `detect_lane` function uses keyword
   heuristics on topic content. This is intentionally simple — if a topic
   cannot be confidently classified, it falls back to `"generic"`, which
   preserves the current behavior exactly.

3. **Summary string stability**: Some acceptance tests assert exact summary
   strings. After W2, these assertions may need updating. The test changes
   are listed in W2-Step5.

4. **`inspect_resume_state` as action_type**: The internal action type is
   kept for backward compatibility. Only the summary string changes in the
   human-facing surface. This means internal routing logic is unaffected.
