# Semantic Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Centralize lane/research-mode/template-mode routing so first_principles and theory_synthesis are preserved correctly.

**Architecture:** Add a dedicated semantic routing helper module with canonicalization functions for template mode, lane, and validation mode. Delegate existing AITP service mapping helpers to the new module and update runtime profiles with the new theory_synthesis profile.

**Tech Stack:** Python, pytest, JSON runtime configuration.

---

### Task 1: Add semantic routing tests

**Files:**
- Create: `research/knowledge-hub/tests/test_semantic_routing.py`
- Test: `research/knowledge-hub/tests/test_semantic_routing.py`

- [ ] **Step 1: Write the failing tests**

```python
from knowledge_hub.semantic_routing import (
    canonical_lane,
    canonical_template_mode,
    canonical_validation_mode,
)


def test_canonical_lane_preserves_first_principles():
    assert canonical_lane(template_mode="toy_numeric", research_mode="first_principles") == "first_principles"


def test_canonical_lane_preserves_theory_synthesis():
    assert canonical_lane(template_mode="code_method", research_mode="theory_synthesis") == "theory_synthesis"


def test_canonical_template_mode_for_theory_synthesis():
    assert canonical_template_mode("theory_synthesis") == "code_method"


def test_canonical_validation_mode_for_first_principles():
    assert canonical_validation_mode("toy_numeric", "first_principles") == "numerical"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest research/knowledge-hub/tests/test_semantic_routing.py -q`

Expected: FAIL because `knowledge_hub.semantic_routing` does not exist yet.

### Task 2: Implement semantic routing helper

**Files:**
- Create: `research/knowledge-hub/knowledge_hub/semantic_routing.py`
- Modify: `research/knowledge-hub/knowledge_hub/aitp_service.py`

- [ ] **Step 1: Write minimal helper implementation**

```python
from __future__ import annotations

from typing import Iterable


LANES = {
    "formal_theory",
    "toy_numeric",
    "first_principles",
    "theory_synthesis",
    "code_method",
}


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
    normalized_template = _normalize(template_mode)
    normalized_research = _normalize(research_mode)
    if normalized_template == "formal_theory" or normalized_research == "formal_derivation":
        return "formal"
    if normalized_template == "toy_numeric" or normalized_research in {"toy_model", "first_principles"}:
        return "numerical"
    return "hybrid"
```

- [ ] **Step 2: Delegate AITP service mapping helpers**

```python
from .semantic_routing import (
    canonical_lane,
    canonical_template_mode,
    canonical_validation_mode,
)


def _template_mode_to_research_mode(self, template_mode: str | None) -> str:
    normalized = str(template_mode or "").strip().lower()
    mapping = {
        "formal_theory": "formal_derivation",
        "toy_numeric": "toy_model",
        "code_method": "exploratory_general",
    }
    return mapping.get(normalized, normalized or "exploratory_general")


def _research_mode_to_template_mode(self, research_mode: str | None) -> str:
    return canonical_template_mode(research_mode)


def _validation_mode_for_template(self, template_mode: str | None) -> str:
    return canonical_validation_mode(template_mode, None)


def _lane_for_modes(self, *, template_mode: str | None, research_mode: str | None) -> str:
    return canonical_lane(template_mode=template_mode, research_mode=research_mode)
```

- [ ] **Step 3: Run tests to verify they pass**

Run: `python -m pytest research/knowledge-hub/tests/test_semantic_routing.py -q`

Expected: PASS.

### Task 3: Add theory_synthesis research mode profile

**Files:**
- Modify: `research/knowledge-hub/runtime/research_mode_profiles.json`

- [ ] **Step 1: Add the theory_synthesis profile**

```json
    "theory_synthesis": {
      "label": "Theory synthesis",
      "description": "For orchestrating cross-derivation synthesis, concept consolidation, and integration across formal and numerical lanes while keeping the evidence ledger explicit.",
      "default_surface": "formal",
      "default_executor_kind": "codex_cli",
      "default_runtime_lane": "codex",
      "reasoning_profile": "high",
      "reproducibility_expectations": [
        "Persist synthesis claims with explicit tracebacks to prior derivations or validations.",
        "Record assumption merges, scope constraints, and any unresolved contradictions.",
        "Separate synthesized conclusions from open conjectures and speculative bridges."
      ],
      "note_expectations": [
        "L2 note: promote only consolidated theory statements with clear provenance.",
        "L3 note: maintain a synthesis notebook that tracks which fragments were merged.",
        "L4 note: summarize what integrations were completed and which are pending validation."
      ]
    }
```

- [ ] **Step 2: Run tests again if needed**

Run: `python -m pytest research/knowledge-hub/tests/test_semantic_routing.py -q`

Expected: PASS.

### Task 4: Commit

**Files:**
- Create: `research/knowledge-hub/knowledge_hub/semantic_routing.py`
- Create: `research/knowledge-hub/tests/test_semantic_routing.py`
- Modify: `research/knowledge-hub/knowledge_hub/aitp_service.py`
- Modify: `research/knowledge-hub/runtime/research_mode_profiles.json`

- [ ] **Step 1: Commit the changes**

Run:
```bash
git add research/knowledge-hub/knowledge_hub/semantic_routing.py \
  research/knowledge-hub/tests/test_semantic_routing.py \
  research/knowledge-hub/knowledge_hub/aitp_service.py \
  research/knowledge-hub/runtime/research_mode_profiles.json
git commit -m "feat: centralize lane and research mode routing"
```

Expected: commit created.
