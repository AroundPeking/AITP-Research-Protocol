# M1 Semantic Closure And Interaction Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make AITP's lane/mode/transition semantics internally consistent, add a durable interaction-and-stop contract to runtime surfaces, and freeze the `L2` MVP contract without yet implementing seeded graph retrieval.

**Architecture:** First lock semantic drift and interaction behavior with focused regressions, then centralize lane/research-mode mapping in a dedicated helper instead of leaving it implicit inside `aitp_service.py`. Reproject the new interaction contract through topic synopsis, runtime bundle, dashboard, and operator surfaces. Keep `L2` MVP work in this plan contract-only: doc and regression closure now, seeded graph data and traversal in a separate `M2` plan.

**Tech Stack:** Python 3.10+, `pytest`, JSON Schema, Markdown protocol docs, existing `knowledge_hub` runtime helpers

---

## Scope Guard

This plan intentionally covers only `M1: Semantic Closure And Interaction Contract`.

It does **not** implement:

- seeded `L2` graph data,
- graph traversal,
- progressive-disclosure graph retrieval over populated `L2`,
- collaborator-memory persistence,
- or paired-backend drift rebuild workflows.

Those belong to later milestone plans.

## File Structure

### New files

- `research/knowledge-hub/knowledge_hub/semantic_routing.py`
  - one authoritative helper for lane, research-mode, and template-mode normalization
- `research/knowledge-hub/runtime/schemas/result-brief.schema.json`
  - machine-readable contract for the new human-facing result brief surface
- `research/knowledge-hub/tests/test_semantic_routing.py`
  - focused regressions for semantic mapping and lane preservation
- `research/knowledge-hub/canonical/L2_MVP_CONTRACT.md`
  - explicit `M1` contract for MVP node/edge families and deferred activation rules

### Existing files to modify

- `research/knowledge-hub/knowledge_hub/aitp_service.py`
  - remove duplicated lane/research-mode mapping logic and delegate to the new helper
- `research/knowledge-hub/knowledge_hub/source_distillation_support.py`
  - emit canonical lane vocabulary instead of ad hoc `"numerical"` / `"exploratory"`
- `research/knowledge-hub/runtime/research_mode_profiles.json`
  - define the active `theory_synthesis` profile and keep `first_principles` distinct
- `research/knowledge-hub/knowledge_hub/mode_envelope_support.py`
  - expose interaction-class and graph-first consultation semantics inside the runtime contract
- `research/knowledge-hub/knowledge_hub/runtime_truth_service.py`
  - derive `interaction_class`, `stop_status`, `stop_reason`, and result-shape fields for topic synopsis
- `research/knowledge-hub/knowledge_hub/runtime_bundle_support.py`
  - publish the new interaction contract in the progressive-disclosure bundle
- `research/knowledge-hub/knowledge_hub/topic_shell_support.py`
  - materialize and render the new `result_brief.latest.{json,md}` surface
- `research/knowledge-hub/runtime/scripts/interaction_surface_support.py`
  - render interaction-state/operator surfaces with the new interaction contract fields
- `research/knowledge-hub/schemas/topic-synopsis.schema.json`
  - package-local schema update for new lane enum values and interaction fields
- `schemas/topic-synopsis.schema.json`
  - repo-root mirror of the topic synopsis schema update
- `research/knowledge-hub/runtime/schemas/progressive-disclosure-runtime-bundle.schema.json`
  - schema update for the new `interaction_contract` payload and `result_brief` pointer
- `research/knowledge-hub/tests/test_topic_start_regressions.py`
  - update source-distillation expectations to canonical lane names
- `research/knowledge-hub/tests/test_runtime_profiles_and_projections.py`
  - lock interaction-class and runtime-bundle behavior
- `research/knowledge-hub/tests/test_runtime_scripts.py`
  - lock operator-surface rendering and checkpoint behavior
- `research/knowledge-hub/tests/test_schema_contracts.py`
  - schema regressions for topic synopsis, runtime bundle, and result brief
- `research/knowledge-hub/tests/test_aitp_service.py`
  - lock service-level rendering of topic synopsis and result brief
- `research/knowledge-hub/canonical/README.md`
  - link the new MVP contract and mark graph seeding as later work

## Task 1: Centralize Semantic Routing

**Files:**
- Create: `research/knowledge-hub/knowledge_hub/semantic_routing.py`
- Modify: `research/knowledge-hub/knowledge_hub/aitp_service.py`
- Modify: `research/knowledge-hub/runtime/research_mode_profiles.json`
- Test: `research/knowledge-hub/tests/test_semantic_routing.py`

- [ ] **Step 1: Write the failing semantic-routing test**

```python
from __future__ import annotations

import unittest

from knowledge_hub.semantic_routing import (
    canonical_lane,
    canonical_template_mode,
    canonical_validation_mode,
)


class SemanticRoutingTests(unittest.TestCase):
    def test_first_principles_lane_is_not_collapsed_into_toy_numeric(self) -> None:
        self.assertEqual(
            canonical_lane(template_mode="toy_numeric", research_mode="first_principles"),
            "first_principles",
        )

    def test_theory_synthesis_lane_survives_template_fallback(self) -> None:
        self.assertEqual(
            canonical_lane(template_mode="code_method", research_mode="theory_synthesis"),
            "theory_synthesis",
        )
        self.assertEqual(canonical_template_mode("theory_synthesis"), "code_method")

    def test_validation_mode_remains_numerical_for_first_principles(self) -> None:
        self.assertEqual(canonical_validation_mode("toy_numeric", "first_principles"), "numerical")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new test to verify it fails**

Run: `python -m pytest research/knowledge-hub/tests/test_semantic_routing.py -q`

Expected: FAIL with `ModuleNotFoundError: No module named 'knowledge_hub.semantic_routing'`

- [ ] **Step 3: Implement the shared semantic-routing helper and delegate service mapping to it**

```python
from __future__ import annotations

LANE_VALUES = (
    "formal_theory",
    "toy_numeric",
    "first_principles",
    "theory_synthesis",
    "code_method",
)


def _normalize(value: str | None) -> str:
    return str(value or "").strip().lower()


def canonical_template_mode(research_mode: str | None) -> str:
    normalized = _normalize(research_mode)
    mapping = {
        "formal_derivation": "formal_theory",
        "toy_model": "toy_numeric",
        "first_principles": "toy_numeric",
        "theory_synthesis": "code_method",
        "exploratory_general": "code_method",
    }
    return mapping.get(normalized, "code_method")


def canonical_lane(*, template_mode: str | None, research_mode: str | None) -> str:
    normalized_template = _normalize(template_mode)
    normalized_research = _normalize(research_mode)
    if normalized_template == "formal_theory" or normalized_research == "formal_derivation":
        return "formal_theory"
    if normalized_research == "first_principles":
        return "first_principles"
    if normalized_research == "theory_synthesis":
        return "theory_synthesis"
    if normalized_template == "toy_numeric" or normalized_research == "toy_model":
        return "toy_numeric"
    return "code_method"


def canonical_validation_mode(template_mode: str | None, research_mode: str | None) -> str:
    lane = canonical_lane(template_mode=template_mode, research_mode=research_mode)
    if lane == "formal_theory":
        return "formal"
    if lane in {"toy_numeric", "first_principles"}:
        return "numerical"
    return "hybrid"
```

And in `aitp_service.py`, replace the local mapping bodies with:

```python
from .semantic_routing import canonical_lane, canonical_template_mode, canonical_validation_mode

def _research_mode_to_template_mode(self, research_mode: str | None) -> str:
    return canonical_template_mode(research_mode)

def _validation_mode_for_template(self, template_mode: str | None) -> str:
    return canonical_validation_mode(template_mode, None)

def _lane_for_modes(self, *, template_mode: str | None, research_mode: str | None) -> str:
    return canonical_lane(template_mode=template_mode, research_mode=research_mode)
```

Also extend `research_mode_profiles.json` with:

```json
"theory_synthesis": {
  "label": "Theory synthesis",
  "description": "For cross-paper comparison, framework alignment, notation reconciliation, and reusable concept-network construction.",
  "default_surface": "formal",
  "default_executor_kind": "codex_cli",
  "default_runtime_lane": "codex",
  "reasoning_profile": "high",
  "reproducibility_expectations": [
    "Persist the compared source set, normalization choices, and alignment criteria.",
    "Record where terminology is aligned, where assumptions differ, and where equivalence remains unproved.",
    "Keep contradiction and unresolved reduction boundaries explicit."
  ],
  "note_expectations": [
    "L2 note: promote only synthesis outputs with explicit scope, assumptions, and unresolved mismatches.",
    "L3 note: preserve route comparisons, notation mappings, and partial alignment notes.",
    "L4 note: summarize what was reconciled, what remains in tension, and what still requires source recovery."
  ]
}
```

- [ ] **Step 4: Run the targeted tests to verify semantic routing passes**

Run: `python -m pytest research/knowledge-hub/tests/test_semantic_routing.py -q`

Expected: PASS

- [ ] **Step 5: Commit the semantic-routing slice**

```bash
git add research/knowledge-hub/knowledge_hub/semantic_routing.py research/knowledge-hub/knowledge_hub/aitp_service.py research/knowledge-hub/runtime/research_mode_profiles.json research/knowledge-hub/tests/test_semantic_routing.py
git commit -m "feat: centralize lane and research mode routing"
```

## Task 2: Canonicalize Distillation Output And Topic-Synopsis Lane Vocabulary

**Files:**
- Modify: `research/knowledge-hub/knowledge_hub/source_distillation_support.py`
- Modify: `research/knowledge-hub/schemas/topic-synopsis.schema.json`
- Modify: `schemas/topic-synopsis.schema.json`
- Test: `research/knowledge-hub/tests/test_topic_start_regressions.py`
- Test: `research/knowledge-hub/tests/test_schema_contracts.py`

- [ ] **Step 1: Write the failing lane-vocabulary regressions**

```python
def test_distill_from_sources_uses_canonical_toy_numeric_lane(self) -> None:
    distilled = distill_from_sources(
        kernel_root=self.kernel_root,
        source_rows=[
            {
                "source_id": "code:tfim-benchmark",
                "source_type": "code",
                "title": "Tiny TFIM Benchmark",
                "summary": (
                    "We show the exact diagonalization baseline reproduces the first finite-size benchmark. "
                    "This establishes the observable normalization before larger runs."
                ),
                "provenance": {
                    "absolute_path": str(self.root / "inputs" / "missing-benchmark.md"),
                },
            }
        ],
        topic_slug="demo-topic",
    )
    self.assertEqual(distilled["distilled_lane"], "toy_numeric")


def test_topic_synopsis_schema_accepts_expanded_lane_enum(self) -> None:
    payload = self._read_json("schemas/topic-synopsis.schema.json")
    lane_enum = set(payload["properties"]["lane"]["enum"])
    self.assertEqual(
        lane_enum,
        {"formal_theory", "toy_numeric", "first_principles", "theory_synthesis", "code_method"},
    )
```

- [ ] **Step 2: Run the lane-vocabulary tests to verify they fail**

Run: `python -m pytest research/knowledge-hub/tests/test_topic_start_regressions.py -k distill_from_sources_uses_canonical_toy_numeric_lane -q`

Expected: FAIL because the current code returns `"numerical"`

Run: `python -m pytest research/knowledge-hub/tests/test_schema_contracts.py -k topic_synopsis_schema_accepts_expanded_lane_enum -q`

Expected: FAIL because the schema still only allows three lane values

- [ ] **Step 3: Implement canonical lane output in source distillation and update both schema mirrors**

```python
def _distill_lane_and_route(*, source_types: set[str], titles: list[str]) -> tuple[str, str]:
    if any(source_type in source_types for source_type in _FORMAL_SOURCE_TYPES):
        return (
            "formal_theory",
            "Derive the first bounded question from the source material, then identify the key definitions and proof obligations.",
        )
    if any(source_type in source_types for source_type in _NUMERICAL_SOURCE_TYPES):
        return (
            "toy_numeric",
            "Reproduce the baseline benchmark before trusting new results. Then validate the observable definitions and normalization.",
        )
    return (
        "code_method",
        "Define the scope boundaries and the first implementation-backed validation artifact.",
    )
```

And in both topic-synopsis schemas, replace the lane enum block with:

```json
"lane": {
  "type": "string",
  "enum": [
    "formal_theory",
    "toy_numeric",
    "first_principles",
    "theory_synthesis",
    "code_method"
  ]
}
```

- [ ] **Step 4: Run the updated regressions**

Run: `python -m pytest research/knowledge-hub/tests/test_topic_start_regressions.py -k distilled_lane -q`

Expected: PASS

Run: `python -m pytest research/knowledge-hub/tests/test_schema_contracts.py -k topic_synopsis_schema_accepts_expanded_lane_enum -q`

Expected: PASS

- [ ] **Step 5: Commit the lane-vocabulary slice**

```bash
git add research/knowledge-hub/knowledge_hub/source_distillation_support.py research/knowledge-hub/schemas/topic-synopsis.schema.json schemas/topic-synopsis.schema.json research/knowledge-hub/tests/test_topic_start_regressions.py research/knowledge-hub/tests/test_schema_contracts.py
git commit -m "feat: canonicalize distilled lane vocabulary"
```

## Task 3: Add The Runtime Interaction Contract

**Files:**
- Modify: `research/knowledge-hub/knowledge_hub/mode_envelope_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/runtime_truth_service.py`
- Modify: `research/knowledge-hub/knowledge_hub/runtime_bundle_support.py`
- Modify: `research/knowledge-hub/runtime/schemas/progressive-disclosure-runtime-bundle.schema.json`
- Modify: `research/knowledge-hub/schemas/topic-synopsis.schema.json`
- Modify: `schemas/topic-synopsis.schema.json`
- Test: `research/knowledge-hub/tests/test_runtime_profiles_and_projections.py`
- Test: `research/knowledge-hub/tests/test_schema_contracts.py`

- [ ] **Step 1: Write the failing interaction-contract regressions**

```python
def test_build_runtime_mode_contract_emits_interaction_contract_for_checkpoint(self) -> None:
    contract = build_runtime_mode_contract(
        resume_stage="L3",
        load_profile="light",
        idea_packet_status="approved_for_execution",
        operator_checkpoint_status="requested",
        selected_action_type="inspect_resume_state",
        selected_action_summary="Need a route choice.",
        must_read_now=[{"path": "runtime/topics/demo-topic/topic_dashboard.md", "reason": "dashboard"}],
        may_defer_until_trigger=[],
        escalation_triggers=[],
    )
    self.assertEqual(contract["interaction_contract"]["interaction_class"], "checkpoint_question")
    self.assertEqual(contract["interaction_contract"]["stop_status"], "checkpoint_required")


def test_topic_synopsis_runtime_focus_includes_interaction_fields(self) -> None:
    payload = self.service._topic_synopsis_runtime_focus(
        topic_slug="demo-topic",
        topic_state_explainability={
            "current_status_summary": "Waiting on operator confirmation.",
            "why_this_topic_is_here": "A route-changing answer is required.",
            "active_human_need": {"status": "requested", "kind": "benchmark_or_validation_route_choice", "summary": "Choose the benchmark route."},
            "blocker_summary": [],
            "last_evidence_return": {"kind": "none", "summary": "No evidence yet."},
        },
        selected_action_id="action:demo-topic:01",
        selected_action_type="inspect_resume_state",
        selected_action_summary="Choose a route.",
        resume_stage="L3",
        last_materialized_stage="L1",
        dependency_status="clear",
        dependency_summary="No active dependencies.",
        promotion_status="not_requested",
    )
    self.assertEqual(payload["interaction_class"], "checkpoint_question")
    self.assertEqual(payload["stop_status"], "checkpoint_required")
    self.assertEqual(payload["primary_result_shape"], "checkpoint_card")
```

- [ ] **Step 2: Run the focused tests to verify they fail**

Run: `python -m pytest research/knowledge-hub/tests/test_runtime_profiles_and_projections.py -k interaction_contract -q`

Expected: FAIL because `interaction_contract` does not exist yet

Run: `python -m pytest research/knowledge-hub/tests/test_schema_contracts.py -k interaction_contract -q`

Expected: FAIL because the schema does not yet require the new fields

- [ ] **Step 3: Implement the interaction contract and schema updates**

In `mode_envelope_support.py`, add:

```python
def _interaction_contract(*, runtime_mode: str, transition_posture: dict[str, Any], operator_checkpoint_status: str) -> dict[str, Any]:
    if operator_checkpoint_status == "requested" or transition_posture.get("requires_human_checkpoint"):
        return {
            "interaction_class": "checkpoint_question",
            "stop_status": "checkpoint_required",
            "stop_reason": str(transition_posture.get("human_checkpoint_reason") or "A route-changing human decision is required."),
            "primary_result_shape": "checkpoint_card",
        }
    if transition_posture.get("transition_kind") == "backedge_transition" and "capability_gap_blocker" in set(transition_posture.get("triggered_by") or []):
        return {
            "interaction_class": "hard_stop",
            "stop_status": "blocked",
            "stop_reason": str(transition_posture.get("transition_reason") or "A capability blocker prevents honest continuation."),
            "primary_result_shape": "status_update",
        }
    if runtime_mode in {"verify", "promote"}:
        return {
            "interaction_class": "non_blocking_update",
            "stop_status": "continue",
            "stop_reason": "",
            "primary_result_shape": "result_brief",
        }
    return {
        "interaction_class": "silent_continue",
        "stop_status": "continue",
        "stop_reason": "",
        "primary_result_shape": "status_update",
    }
```

And return it from `build_runtime_mode_contract()`:

```python
interaction_contract = _interaction_contract(
    runtime_mode=runtime_mode,
    transition_posture=transition_posture,
    operator_checkpoint_status=operator_checkpoint_status,
)
...
"interaction_contract": interaction_contract,
```

In `runtime_truth_service.py`, extend `runtime_focus` with:

```python
"interaction_class": interaction_contract["interaction_class"],
"stop_status": interaction_contract["stop_status"],
"stop_reason": interaction_contract["stop_reason"],
"primary_result_shape": interaction_contract["primary_result_shape"],
```

Add matching schema fields in both topic-synopsis schema mirrors and the runtime-bundle schema:

```json
"interaction_class": {
  "type": "string",
  "enum": ["silent_continue", "non_blocking_update", "checkpoint_question", "hard_stop"]
},
"stop_status": {
  "type": "string",
  "enum": ["continue", "checkpoint_required", "blocked", "complete"]
},
"stop_reason": {
  "type": "string"
},
"primary_result_shape": {
  "type": "string",
  "enum": ["status_update", "result_brief", "checkpoint_card", "topic_replay_bundle"]
}
```

- [ ] **Step 4: Run the interaction-contract regressions**

Run: `python -m pytest research/knowledge-hub/tests/test_runtime_profiles_and_projections.py -k "interaction_contract or topic_synopsis_runtime_focus_includes_interaction_fields" -q`

Expected: PASS

Run: `python -m pytest research/knowledge-hub/tests/test_schema_contracts.py -k "interaction_contract or topic_synopsis" -q`

Expected: PASS

- [ ] **Step 5: Commit the interaction-contract slice**

```bash
git add research/knowledge-hub/knowledge_hub/mode_envelope_support.py research/knowledge-hub/knowledge_hub/runtime_truth_service.py research/knowledge-hub/knowledge_hub/runtime_bundle_support.py research/knowledge-hub/runtime/schemas/progressive-disclosure-runtime-bundle.schema.json research/knowledge-hub/schemas/topic-synopsis.schema.json schemas/topic-synopsis.schema.json research/knowledge-hub/tests/test_runtime_profiles_and_projections.py research/knowledge-hub/tests/test_schema_contracts.py
git commit -m "feat: add runtime interaction contract"
```

## Task 4: Materialize A Scientist-Facing Result Brief

**Files:**
- Create: `research/knowledge-hub/runtime/schemas/result-brief.schema.json`
- Modify: `research/knowledge-hub/knowledge_hub/topic_shell_support.py`
- Modify: `research/knowledge-hub/runtime/scripts/interaction_surface_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/runtime_bundle_support.py`
- Modify: `research/knowledge-hub/schemas/topic-synopsis.schema.json`
- Modify: `schemas/topic-synopsis.schema.json`
- Modify: `research/knowledge-hub/runtime/schemas/progressive-disclosure-runtime-bundle.schema.json`
- Test: `research/knowledge-hub/tests/test_aitp_service.py`
- Test: `research/knowledge-hub/tests/test_runtime_scripts.py`
- Test: `research/knowledge-hub/tests/test_schema_contracts.py`

- [ ] **Step 1: Write the failing result-brief regressions**

```python
def test_ensure_topic_shell_surfaces_writes_result_brief_surface(self) -> None:
    payload = self.service.ensure_topic_shell_surfaces("demo-topic")
    self.assertTrue(Path(payload["result_brief_json_path"]).exists())
    self.assertTrue(Path(payload["result_brief_markdown_path"]).exists())


def test_result_brief_markdown_surfaces_scope_and_non_claims(self) -> None:
    payload = self.service.ensure_topic_shell_surfaces("demo-topic")
    text = Path(payload["result_brief_markdown_path"]).read_text(encoding="utf-8")
    self.assertIn("## What Changed", text)
    self.assertIn("## Evidence", text)
    self.assertIn("## What This Does Not Yet Justify", text)
```

- [ ] **Step 2: Run the targeted tests to verify they fail**

Run: `python -m pytest research/knowledge-hub/tests/test_aitp_service.py -k "result_brief" -q`

Expected: FAIL because `ensure_topic_shell_surfaces()` does not yet return result-brief paths

- [ ] **Step 3: Implement result-brief generation and wire it into runtime surfaces**

In `topic_shell_support.py`, add:

```python
def build_result_brief_payload(*, topic_slug: str, runtime_focus: dict[str, Any], topic_status_explainability: dict[str, Any]) -> dict[str, Any]:
    return {
        "kind": "result_brief",
        "topic_slug": topic_slug,
        "interaction_class": str(runtime_focus.get("interaction_class") or "status_update"),
        "what_changed": str(runtime_focus.get("summary") or ""),
        "evidence_summary": str(runtime_focus.get("last_evidence_summary") or ""),
        "scope_summary": str(topic_status_explainability.get("current_route_choice") or runtime_focus.get("why_this_topic_is_here") or ""),
        "non_claims": [str(item) for item in (topic_status_explainability.get("blocker_summary") or []) if str(item).strip()],
    }


def render_result_brief_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Result Brief",
        "",
        f"- Topic slug: `{payload['topic_slug']}`",
        f"- Interaction class: `{payload['interaction_class']}`",
        "",
        "## What Changed",
        "",
        payload["what_changed"] or "(none)",
        "",
        "## Evidence",
        "",
        payload["evidence_summary"] or "(none)",
        "",
        "## Scope",
        "",
        payload["scope_summary"] or "(none)",
        "",
        "## What This Does Not Yet Justify",
        "",
    ]
    if payload["non_claims"]:
        lines.extend([f"- {item}" for item in payload["non_claims"]])
    else:
        lines.append("- No active non-claim boundary was recorded.")
    lines.append("")
    return "\n".join(lines)
```

Materialize:

```python
result_brief_json_path = runtime_root / "result_brief.latest.json"
result_brief_markdown_path = runtime_root / "result_brief.latest.md"
```

Add the new pointer to the runtime bundle and topic synopsis truth sources:

```python
"result_brief_path": self._relativize(result_brief_json_path),
```

In both topic-synopsis schema mirrors, extend `truth_sources.required` and `truth_sources.properties` with:

```json
"result_brief_path": {
  "type": [
    "string",
    "null"
  ]
}
```

And in the runtime-bundle schema, add a result-brief pointer inside the runtime truth payload:

```json
"result_brief": {
  "type": "object",
  "required": ["path"],
  "properties": {
    "path": { "type": "string" }
  },
  "additionalProperties": true
}
```

Add the matching JSON schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ResultBrief",
  "type": "object",
  "required": ["kind", "topic_slug", "interaction_class", "what_changed", "evidence_summary", "scope_summary", "non_claims"],
  "properties": {
    "kind": { "type": "string", "const": "result_brief" },
    "topic_slug": { "type": "string", "minLength": 1 },
    "interaction_class": { "type": "string" },
    "what_changed": { "type": "string" },
    "evidence_summary": { "type": "string" },
    "scope_summary": { "type": "string" },
    "non_claims": { "type": "array", "items": { "type": "string" } }
  },
  "additionalProperties": false
}
```

- [ ] **Step 4: Run the result-brief regressions**

Run: `python -m pytest research/knowledge-hub/tests/test_aitp_service.py -k result_brief -q`

Expected: PASS

Run: `python -m pytest research/knowledge-hub/tests/test_schema_contracts.py -k result_brief -q`

Expected: PASS

- [ ] **Step 5: Commit the result-brief slice**

```bash
git add research/knowledge-hub/runtime/schemas/result-brief.schema.json research/knowledge-hub/knowledge_hub/topic_shell_support.py research/knowledge-hub/runtime/scripts/interaction_surface_support.py research/knowledge-hub/knowledge_hub/runtime_bundle_support.py research/knowledge-hub/tests/test_aitp_service.py research/knowledge-hub/tests/test_runtime_scripts.py research/knowledge-hub/tests/test_schema_contracts.py
git commit -m "feat: add runtime result brief surface"
```

## Task 5: Freeze The L2 MVP Contract And Close The Docs/Test Loop

**Files:**
- Create: `research/knowledge-hub/canonical/L2_MVP_CONTRACT.md`
- Modify: `research/knowledge-hub/canonical/README.md`
- Modify: `research/knowledge-hub/tests/test_l2_backend_contracts.py`
- Modify: `research/knowledge-hub/runtime/README.md`

- [ ] **Step 1: Write the failing docs-lock regression**

```python
def test_l2_mvp_contract_doc_exists_and_names_the_m1_subset(self) -> None:
    contract = (self.kernel_root / "canonical" / "L2_MVP_CONTRACT.md").read_text(encoding="utf-8")
    self.assertIn("physical_picture", contract)
    self.assertIn("negative_result", contract)
    self.assertIn("depends_on", contract)
    self.assertIn("warns_about", contract)
    self.assertIn("M2", contract)
```

- [ ] **Step 2: Run the docs-lock test to verify it fails**

Run: `python -m pytest research/knowledge-hub/tests/test_l2_backend_contracts.py -k l2_mvp_contract_doc_exists_and_names_the_m1_subset -q`

Expected: FAIL with `FileNotFoundError` for `canonical/L2_MVP_CONTRACT.md`

- [ ] **Step 3: Write the MVP contract doc and link it from the canonical/runtime docs**

Create `research/knowledge-hub/canonical/L2_MVP_CONTRACT.md` with at least:

```md
# L2 MVP Contract

## Purpose

This document freezes the `M1` MVP knowledge-network subset without yet claiming that seeded graph data or traversal are implemented.

## MVP node families

- `concept`
- `theorem_card`
- `method`
- `assumption_card`
- `physical_picture`
- `warning_note`

## Immediate next extension family

- `negative_result`

## MVP edge families

- `depends_on`
- `uses_method`
- `valid_under`
- `warns_about`
- `contradicts`
- `analogy_to`
- `derived_from_source`

## Activation rule

`M1` freezes the contract.
`M2` activates seeded graph data, traversal, and populated retrieval.
```

And link it from `canonical/README.md`:

```md
- `L2_MVP_CONTRACT.md`
  - frozen `M1` subset for the first useful knowledge-network implementation
```

Also add the new result-brief surface to `runtime/README.md`:

```md
- `topics/<topic_slug>/result_brief.latest.json`
  - machine-readable scientist-facing result summary for the latest bounded change
- `topics/<topic_slug>/result_brief.latest.md`
  - human-readable result brief with evidence and non-claim boundaries
```

- [ ] **Step 4: Run the docs and regression sweep**

Run: `python -m pytest research/knowledge-hub/tests/test_l2_backend_contracts.py -k l2_mvp_contract_doc_exists_and_names_the_m1_subset -q`

Expected: PASS

Run: `python -m pytest research/knowledge-hub/tests/test_semantic_routing.py research/knowledge-hub/tests/test_topic_start_regressions.py research/knowledge-hub/tests/test_runtime_profiles_and_projections.py research/knowledge-hub/tests/test_runtime_scripts.py research/knowledge-hub/tests/test_aitp_service.py research/knowledge-hub/tests/test_schema_contracts.py research/knowledge-hub/tests/test_l2_backend_contracts.py -q`

Expected: PASS

- [ ] **Step 5: Commit the docs and regression-closure slice**

```bash
git add research/knowledge-hub/canonical/L2_MVP_CONTRACT.md research/knowledge-hub/canonical/README.md research/knowledge-hub/runtime/README.md research/knowledge-hub/tests/test_l2_backend_contracts.py
git commit -m "docs: freeze M1 interaction and L2 MVP contracts"
```

## Self-Review

### Spec coverage

- `R1 Axis Semantic Closure`
  - covered by Tasks 1 and 2
- `R2 Research Flow As Graph, Not Just Pipeline`
  - partially covered by Task 3 through graph-first consultation and interaction contract projection
- `R5 L2 Knowledge-Network MVP`
  - covered at contract level by Task 5 only
- `R8 Human-Facing Surfaces`
  - covered by Tasks 3 and 4
- `Workflow Routing Rule`
  - this plan does not implement a new outer-shell router; it only closes the runtime semantics needed underneath that rule

### Explicit gap

This plan does **not** yet implement:

- seeded canonical `L2` nodes,
- `edges.jsonl` population,
- graph traversal,
- collaborator-memory persistence,
- or paired-backend drift audit.

Those require later plans and should not be pulled into `M1`.

### Placeholder scan

- no `TODO`
- no `TBD`
- no cross-task "same as above" references
- every run step has an explicit command and expected outcome

### Type consistency

- canonical lane enum stays:
  - `formal_theory`
  - `toy_numeric`
  - `first_principles`
  - `theory_synthesis`
  - `code_method`
- interaction class stays:
  - `silent_continue`
  - `non_blocking_update`
  - `checkpoint_question`
  - `hard_stop`
- result shape stays:
  - `status_update`
  - `result_brief`
  - `checkpoint_card`
  - `topic_replay_bundle`

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-04-07-m1-semantic-closure-and-interaction-contract.md`. Two execution options:

1. Subagent-Driven (recommended) - I dispatch a fresh subagent per task, review between tasks, fast iteration

2. Inline Execution - Execute tasks in this session using executing-plans, batch execution with checkpoints

Which approach?
