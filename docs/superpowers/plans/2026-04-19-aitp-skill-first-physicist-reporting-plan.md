# AITP Skill-First Physicist Reporting Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make AITP rely more on repo-native skills for physics-style problem framing, derivation writing, L3-L4 round narration, current-claim auditing, and topic-report authoring, while keeping Python responsible for durable runtime state, gates, and TeX compilation.

**Architecture:** Add a physicist-reporting skill bundle under the repository `skills/` directory, teach the existing `using-aitp` and `aitp-runtime` skills to delegate to that bundle, and create a lightweight runtime surface `research_report.active.json|md` that can store/derive skill-authored report content. Then let the XeLaTeX notebook compiler prefer that report surface before falling back to raw ledgers.

**Tech Stack:** Repo-native `SKILL.md` assets, Python runtime helpers in `research/knowledge-hub/knowledge_hub/`, topic runtime JSON/Markdown surfaces, XeLaTeX + `ctex`, `pytest`.

---

### Task 1: Add the physicist-reporting skill bundle

**Files:**
- Create: `skills/aitp-problem-framing/SKILL.md`
- Create: `skills/aitp-derivation-discipline/SKILL.md`
- Create: `skills/aitp-l3-l4-round/SKILL.md`
- Create: `skills/aitp-current-claims-auditor/SKILL.md`
- Create: `skills/aitp-topic-report-author/SKILL.md`
- Modify: `skills/using-aitp/SKILL.md`
- Modify: `skills/aitp-runtime/SKILL.md`
- Test: `research/knowledge-hub/tests/test_physicist_reporting_skills.py`

### Task 2: Add a runtime report surface that skills can fill or refine

**Files:**
- Create: `research/knowledge-hub/knowledge_hub/research_report_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/aitp_service.py`
- Modify: `research/knowledge-hub/knowledge_hub/topic_shell_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/runtime_bundle_support.py`
- Test: `research/knowledge-hub/tests/test_research_report_support.py`

### Task 3: Let the notebook compiler prefer the report surface

**Files:**
- Modify: `research/knowledge-hub/knowledge_hub/research_notebook_support.py`
- Modify: `research/knowledge-hub/tests/test_research_notebook_support.py`

### Task 4: Update one real acceptance path and regenerate sample output

**Files:**
- Modify: `research/knowledge-hub/runtime/scripts/run_jones_chapter4_finite_product_formal_closure_acceptance.py`
- Modify: `research/knowledge-hub/tests/test_runtime_scripts.py`

### Task 5: Verification

**Run:**

```powershell
python -m pytest research/knowledge-hub/tests/test_physicist_reporting_skills.py -q
python -m pytest research/knowledge-hub/tests/test_research_report_support.py -q
python -m pytest research/knowledge-hub/tests/test_research_notebook_support.py -q
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -q
```

