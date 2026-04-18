# AITP Physicist-Style Topic Report Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make AITP produce topic-level notebooks that read like a serious theoretical-physics research report while still preserving the full protocol/audit trail.

**Architecture:** Keep existing ledgers and promotion gates as the machine-facing source of truth, but add one report-facing runtime surface that derives a physicist-readable narrative: problem, motivation, setup, candidate routes, iterative L3-L4 rounds, current claims, caveats, and open problems. Then refactor the XeLaTeX notebook compiler so the main text follows that narrative and pushes provenance/log-heavy material into appendices.

**Tech Stack:** Python runtime surfaces in `research/knowledge-hub/knowledge_hub/`, JSON/JSONL runtime artifacts under `topics/<slug>/runtime/` and `topics/<slug>/L3/runs/<run_id>/`, XeLaTeX + `ctex` notebook compiler, `pytest`.

---

## File map

### Core protocol / docs

- Create: `docs/protocols/TOPIC_RESEARCH_REPORT_PROTOCOL.md`
- Modify: `docs/AITP_SPEC.md`
- Modify: `docs/PROJECT_INDEX.md`
- Modify: `docs/protocols/L3_execution_protocol.md`
- Modify: `research/knowledge-hub/RESEARCH_EXECUTION_GUARDRAILS.md`
- Modify: `research/knowledge-hub/runtime/DECLARATIVE_RUNTIME_CONTRACTS.md`
- Modify: `research/knowledge-hub/runtime/README.md`

### Runtime derivation / report support

- Create: `research/knowledge-hub/knowledge_hub/research_report_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/aitp_service.py`
- Modify: `research/knowledge-hub/knowledge_hub/topic_shell_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/runtime_bundle_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/l3_derivation_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/l3_comparison_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/iteration_journal_support.py`

### Notebook compiler

- Modify: `research/knowledge-hub/knowledge_hub/research_notebook_support.py`

### Sample / tests

- Modify: `research/knowledge-hub/runtime/scripts/run_jones_chapter4_finite_product_formal_closure_acceptance.py`
- Create: `research/knowledge-hub/tests/test_research_report_support.py`
- Modify: `research/knowledge-hub/tests/test_research_notebook_support.py`
- Modify: `research/knowledge-hub/tests/test_l3_derivation_support.py`
- Modify: `research/knowledge-hub/tests/test_runtime_scripts.py`

---

### Task 1: Define The Report-Facing Protocol Surface

**Files:**
- Create: `docs/protocols/TOPIC_RESEARCH_REPORT_PROTOCOL.md`
- Modify: `docs/AITP_SPEC.md`
- Modify: `docs/protocols/L3_execution_protocol.md`
- Modify: `research/knowledge-hub/runtime/DECLARATIVE_RUNTIME_CONTRACTS.md`
- Modify: `research/knowledge-hub/runtime/README.md`
- Modify: `research/knowledge-hub/RESEARCH_EXECUTION_GUARDRAILS.md`
- Modify: `docs/PROJECT_INDEX.md`

- [ ] **Step 1: Write down the new report-facing data contract**

Add a protocol doc that defines one derived runtime artifact:

`topics/<topic_slug>/runtime/research_report.active.json|md`

It should declare these sections explicitly:

- `problem`
- `physical_motivation`
- `literature_position`
- `scope_statement`
- `out_of_scope`
- `setup`
- `candidate_routes`
- `iteration_rounds`
- `current_claims`
- `current_derivation_spine`
- `current_caveats`
- `open_problems`
- `appendix_refs`

- [ ] **Step 2: Record the source-to-report mapping**

Document which existing AITP surfaces feed each report section:

- `research_question.contract.json` -> problem / scope / setup
- `idea_packet.json` -> motivation / why-this-route / evidence bar
- `L1` intake + vault -> literature position / source roles / comparator basis
- `derivation_records.jsonl` -> derivation spine / failed routes
- `l2_comparison_receipts.jsonl` -> current claim boundaries / reusable comparison
- `iterations/*/{plan,l4_return,l3_synthesis}.json` -> round-by-round research narrative
- `candidate_ledger.jsonl` -> current claims
- `unfinished_work.json` -> open problems

- [ ] **Step 3: Make the protocol state the physicist-facing ordering rule**

Write the main ordering rule explicitly:

Main text should read like:

1. problem and motivation
2. background / literature role
3. setup and notation
4. working hypotheses and routes
5. iterative research rounds
6. current stable derivation and claims
7. conclusion and open problems

Appendices should contain provenance maps, full catalogs, logs, and lower-priority failed routes.

- [ ] **Step 4: Update the docs index**

Add `TOPIC_RESEARCH_REPORT_PROTOCOL.md` and the report runtime artifact to `docs/PROJECT_INDEX.md`.

- [ ] **Step 5: Verify doc coverage**

Run:

```powershell
rg -n "research_report.active|Topic Research Report|physicist" docs research/knowledge-hub/runtime
```

Expected:

- new protocol doc is present
- runtime docs mention the report surface
- project index links to it

---

### Task 2: Add A Durable Report Runtime Surface

**Files:**
- Create: `research/knowledge-hub/knowledge_hub/research_report_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/topic_shell_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/aitp_service.py`
- Modify: `research/knowledge-hub/knowledge_hub/runtime_bundle_support.py`
- Test: `research/knowledge-hub/tests/test_research_report_support.py`

- [ ] **Step 1: Write the failing tests**

Create tests that assert `research_report.active.json` contains:

- a non-empty `problem.question`
- a non-empty `physical_motivation`
- a non-empty `setup.assumptions`
- at least one `candidate_routes[*]`
- at least one `current_claims[*]`
- a `current_claims[*].status` chosen from a small controlled set
- a non-empty `open_problems`

Also add a test that the main report can be derived even if only some surfaces exist, with graceful fallback.

- [ ] **Step 2: Implement the derived payload builder**

In `research_report_support.py`, build:

```python
def materialize_research_report(
    service,
    *,
    topic_slug: str,
    run_id: str | None,
    updated_by: str,
) -> dict[str, Any]:
    ...
```

The payload should derive:

- `problem.question` from `research_question.contract.question`
- `physical_motivation` from `idea_packet.initial_idea` + `novelty_target`
- `literature_position` from L1 source roles / reading depth rows
- `setup` from contract scope + assumptions + notation
- `candidate_routes` from `candidate_ledger`
- `iteration_rounds` from iteration plan/return/synthesis packets
- `current_claims` from candidates + comparison receipts + synthesis
- `current_derivation_spine` from non-failed derivation records
- `current_caveats` from comparison limitations + failed route summaries
- `open_problems` from unfinished work + explicit blockers

- [ ] **Step 3: Define stable claim status categories**

Implement a single status vocabulary for `current_claims`:

- `source_reconstruction_only`
- `candidate_under_test`
- `validated_partial`
- `current_working_result`
- `blocked`
- `rejected_route`

The report builder should derive one of these from:

- derivation presence
- comparison receipt presence
- theory-packet readiness (if relevant)
- latest iteration synthesis

- [ ] **Step 4: Materialize the runtime files**

Write:

- `topics/<topic_slug>/runtime/research_report.active.json`
- `topics/<topic_slug>/runtime/research_report.active.md`

and wire them into `ensure_topic_shell_surfaces` / `topic_status` / runtime bundle output.

- [ ] **Step 5: Verify the new runtime surface**

Run:

```powershell
python -m pytest research/knowledge-hub/tests/test_research_report_support.py -q
```

Expected:

- all new report tests pass

---

### Task 3: Enrich L3/L4 Data So The Report Has Real Physics Content

**Files:**
- Modify: `research/knowledge-hub/knowledge_hub/l3_derivation_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/l3_comparison_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/iteration_journal_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/aitp_service.py`
- Test: `research/knowledge-hub/tests/test_l3_derivation_support.py`

- [ ] **Step 1: Write the failing tests for structured derivation metadata**

Add tests that `record_l3_derivation(...)` can optionally persist:

- `derivation_role`
- `goal`
- `starting_point`
- `key_steps`
- `consistency_checks`
- `where_caveat_enters`

while preserving backward compatibility for older rows.

- [ ] **Step 2: Extend derivation rows without breaking old callers**

Add optional fields to the persisted derivation rows and markdown rendering.

Use these semantics:

- `derivation_role`: `current_spine`, `failed_route`, `auxiliary_check`, `source_reconstruction`
- `goal`: what this derivation is trying to establish
- `starting_point`: the first equation/definition
- `key_steps`: short ordered list of real conceptual steps
- `consistency_checks`: special cases / factor checks / sign checks
- `where_caveat_enters`: where the route stops being clean

- [ ] **Step 3: Extend comparison receipts**

Add optional fields to comparison receipts:

- `claim_effect`
- `understanding_delta`
- `promotion_effect`

These fields let the report say not just “what was compared,” but “what changed in our understanding.”

- [ ] **Step 4: Extend iteration packets**

Make iteration packets able to carry:

- `round_question`
- `physical_hypothesis`
- `checks_performed`
- `understanding_delta`
- `route_decision_reason`

If the packet does not provide these fields, the report builder should still synthesize usable prose from the existing fields.

- [ ] **Step 5: Re-run the derivation gate tests**

Run:

```powershell
python -m pytest research/knowledge-hub/tests/test_l3_derivation_support.py -q
```

Expected:

- current derivation/comparison/theory-packet gate behavior still passes
- new structured metadata tests pass

---

### Task 4: Add A Proper “Current Claims / Results” Layer

**Files:**
- Modify: `research/knowledge-hub/knowledge_hub/research_report_support.py`
- Modify: `research/knowledge-hub/knowledge_hub/topic_shell_support.py`
- Test: `research/knowledge-hub/tests/test_research_report_support.py`

- [ ] **Step 1: Write failing tests for current claim tables**

Add tests that the report surface derives a `current_claims` table where each entry includes:

- `claim`
- `status`
- `support`
- `limitation`
- `next_action`

- [ ] **Step 2: Derive claims from candidates plus report evidence**

The derivation rule should be:

- if candidate exists but no comparison -> `candidate_under_test`
- if derivation + comparison + unresolved limitation -> `validated_partial`
- if derivation + comparison + no active limitation and latest synthesis supports it -> `current_working_result`
- if blocked by missing source/theory packet -> `blocked`

- [ ] **Step 3: Add non-claims / regime boundary output**

Derive:

- `regime_boundaries`
- `non_claims`
- `what_is_not_established`

from:

- open ambiguities
- comparison limitations
- failed routes marked as conceptually important

- [ ] **Step 4: Verify the claim status surface**

Run:

```powershell
python -m pytest research/knowledge-hub/tests/test_research_report_support.py -q
```

Expected:

- report tests now include stable result/claim tables

---

### Task 5: Refactor The XeLaTeX Notebook Into A Physicist-Style Report

**Files:**
- Modify: `research/knowledge-hub/knowledge_hub/research_notebook_support.py`
- Test: `research/knowledge-hub/tests/test_research_notebook_support.py`

- [ ] **Step 1: Write the failing notebook-structure tests**

The notebook tests should require these main sections in order:

1. `Research Question And Background`
2. `Setup, Notation, And Regime`
3. `Working Ideas, Hypotheses, And Candidate Routes`
4. `Iterative L3-L4 Research Record`
5. `Current Claims And Stable Results`
6. `Consolidated Derivation`
7. `Conclusion And Open Problems`

Appendices:

- `Source Provenance And Reading Map`
- `Failed Routes And Strategy Memory`
- `Candidate Catalog`
- `Chronological Entry Log`

- [ ] **Step 2: Make the compiler consume `research_report.active.*` first**

Refactor `_rebuild_latex(...)` so the main body is driven by the new report surface rather than directly by each raw ledger.

Use raw ledgers only as fallback.

- [ ] **Step 3: Add a proper current-claims table**

Render a compact table with:

- claim
- status
- support
- limitation
- next action

This should be the first thing a physicist can scan to understand “what this topic currently believes.”

- [ ] **Step 4: Split “Consolidated Derivation” from “Iterative Record”**

Main rule:

- `Iterative L3-L4 Research Record` = process
- `Consolidated Derivation` = current best scientific spine

Failed attempts should only stay in the main text if they are flagged as conceptually decisive; otherwise they move to appendix.

- [ ] **Step 5: Improve derivation rendering for physics use**

Add structured rendering for:

- `goal`
- `starting_point`
- ordered `key_steps`
- `consistency_checks`
- `where_caveat_enters`

Also extend body escaping so the compiler can safely preserve:

- `$...$`
- `$$...$$`
- `\begin{equation}...\end{equation}`
- `\begin{align}...\end{align}`
- `\begin{gather}...\end{gather}`

without escaping them away.

- [ ] **Step 6: Add a proper conclusion section**

Render:

- current result summary
- what is actually established
- what is not established
- next required research move

This should read like the ending of a real theory-group notebook memo, not a generic “open items” list.

- [ ] **Step 7: Verify notebook output**

Run:

```powershell
python -m pytest research/knowledge-hub/tests/test_research_notebook_support.py -q
```

Expected:

- all notebook section-order and content tests pass

---

### Task 6: Update Sample / Acceptance Paths So The New Surface Is Real

**Files:**
- Modify: `research/knowledge-hub/runtime/scripts/run_jones_chapter4_finite_product_formal_closure_acceptance.py`
- Modify: `research/knowledge-hub/tests/test_runtime_scripts.py`

- [ ] **Step 1: Ensure the sample/acceptance script emits the new report-facing data**

Before final notebook generation, make the script persist:

- structured derivation spine fields
- structured comparison receipt fields
- an iteration packet with `round_question`, `checks_performed`, `understanding_delta`

- [ ] **Step 2: Add an acceptance assertion for the report surface**

Extend runtime script tests so at least one acceptance path asserts:

- `research_report.active.json` exists
- `current_claims` is non-empty
- `Consolidated Derivation` and `Conclusion` appear in the compiled `.tex`

- [ ] **Step 3: Run the focused runtime-script slice**

Run:

```powershell
python -m pytest research/knowledge-hub/tests/test_runtime_scripts.py -q -k "formal_real_topic_dialogue_acceptance or positive_negative_l2_coexistence"
```

Expected:

- both targeted acceptance slices pass

---

### Task 7: Regenerate The Public Sample PDF And Review It Like A Physicist

**Files:**
- Modify: `research/knowledge-hub/knowledge_hub/research_notebook_support.py`
- Output: `output/pdf/aitp-topic-archive-sample-v4/...`

- [ ] **Step 1: Generate a fresh sample topic archive**

Build a new sample that explicitly includes:

- one main source reconstruction
- one decisive failed route
- one comparison receipt
- one full L3-L4 iteration round
- one current-claims table row

- [ ] **Step 2: Compile with XeLaTeX**

Run:

```powershell
python - <<'PY'
from pathlib import Path
from knowledge_hub.research_notebook_support import compile_notebook
print(compile_notebook(Path(r"output/pdf/aitp-topic-archive-sample-v4/topic-root/topics/chern-response-demo-topic/L3")))
PY
```

Expected:

- `compiled: true`

- [ ] **Step 3: Render preview pages and review them**

Check:

- opening pages read like a physics report, not a machine log
- current-claims table is easy to scan
- iterative round page reads like “plan / test / result / understanding change”
- appendices clearly look archival, not central

- [ ] **Step 4: Commit**

```powershell
git add docs/protocols/TOPIC_RESEARCH_REPORT_PROTOCOL.md `
  docs/AITP_SPEC.md `
  docs/PROJECT_INDEX.md `
  docs/protocols/L3_execution_protocol.md `
  research/knowledge-hub/RESEARCH_EXECUTION_GUARDRAILS.md `
  research/knowledge-hub/runtime/DECLARATIVE_RUNTIME_CONTRACTS.md `
  research/knowledge-hub/runtime/README.md `
  research/knowledge-hub/knowledge_hub/research_report_support.py `
  research/knowledge-hub/knowledge_hub/aitp_service.py `
  research/knowledge-hub/knowledge_hub/topic_shell_support.py `
  research/knowledge-hub/knowledge_hub/runtime_bundle_support.py `
  research/knowledge-hub/knowledge_hub/l3_derivation_support.py `
  research/knowledge-hub/knowledge_hub/l3_comparison_support.py `
  research/knowledge-hub/knowledge_hub/iteration_journal_support.py `
  research/knowledge-hub/knowledge_hub/research_notebook_support.py `
  research/knowledge-hub/runtime/scripts/run_jones_chapter4_finite_product_formal_closure_acceptance.py `
  research/knowledge-hub/tests/test_research_report_support.py `
  research/knowledge-hub/tests/test_research_notebook_support.py `
  research/knowledge-hub/tests/test_l3_derivation_support.py `
  research/knowledge-hub/tests/test_runtime_scripts.py
git commit -m "feat: add physicist-style topic report surface and notebook"
```

---

## Verification checklist

- [ ] `research_report.active.json|md` exists for topic shells
- [ ] current claims are explicit and status-tagged
- [ ] iteration rounds include “question / test / result / understanding change”
- [ ] consolidated derivation is separated from the process log
- [ ] appendices hold provenance and full audit trails
- [ ] notebook still compiles with `xelatex` + `ctex`
- [ ] existing runtime-script acceptance suite remains green

## Recommended execution order

1. Task 1
2. Task 2
3. Task 3
4. Task 4
5. Task 5
6. Task 6
7. Task 7

Task 2 and Task 3 can overlap after Task 1 is stable, but Task 5 should wait until the report surface exists.

