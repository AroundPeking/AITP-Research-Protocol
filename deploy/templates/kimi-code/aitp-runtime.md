---
name: aitp-runtime
description: Use after AITP routing has claimed the task; continue theory work through the v2 protocol loop instead of ad hoc browsing or free-form synthesis.
---

# AITP Runtime (v2) — Kimi Code

## CRITICAL: Mandatory tool-first behavior

- Topics root is ALWAYS: `{{TOPICS_ROOT}}`
- ALWAYS pass this exact string as `topics_root` to every AITP tool call.
- NEVER use Grep/Glob/Read to inspect AITP topic state. Use AITP tools only.
- ALWAYS call `aitp_get_execution_brief` before deciding what to do next.
- ALWAYS use `AskUserQuestion` for user questions. NEVER type options as plain text.

## Environment gate (mandatory first step)

- AITP v2 runs as an MCP server. Tools are available directly as `aitp_*`.
- Read the protocol manual: `{{REPO_ROOT}}/brain/PROTOCOL.md`

## Agent decision loop

Every iteration MUST start with `aitp_get_execution_brief`:

```
TOPICS_ROOT = "{{TOPICS_ROOT}}"

while topic is not complete:
    brief = aitp_get_execution_brief(TOPICS_ROOT, topic_slug)

    if brief.gate_status starts with "blocked":
        # Fix the flagged artifact using AITP tools or file edits
        continue

    if brief.gate_status == "ready":
        Match on brief.stage:
            "L0" → Execute discover posture (see L0 section below)
            "L1" → Fill remaining L1 artifacts or advance to L3
            "L3" → Work on active subplane artifact, then advance
            "L5" → Fill provenance files, then draft paper
        continue
```

## No-hook state recovery

Kimi Code has no session-start / compact / stop hooks. Therefore:

1. **At the start of EVERY turn** that involves an active AITP topic, call `aitp_get_execution_brief` FIRST to re-orient.
2. **After context compaction**, the execution brief is your only source of truth — it contains the full state you need to resume.
3. **If the user says "继续" or "继续这个 topic"** without specifying which one, call `aitp_list_topics` to find the most recently updated active topic.

## Popup gates (AskUserQuestion)

### Rule 1: Protocol transition popups

When an AITP tool returns a result containing `popup_gate`, you MUST call `AskUserQuestion` before proceeding:

```
result = aitp_advance_to_l3(TOPICS_ROOT, topic_slug)
if result has "popup_gate":
    pg = result["popup_gate"]
    Call AskUserQuestion(questions=[{
        "question": pg["question"],
        "header": pg["header"],
        "options": pg["options"],
        "multi_select": false,
    }])
```

Tools that may return `popup_gate`:
- `aitp_advance_to_l3` — L1→L3 transition confirmation
- `aitp_submit_candidate` — candidate submission confirmation
- `aitp_request_promotion` — promotion approval gate
- `aitp_submit_l4_review` — non-pass review outcome handling
- `aitp_advance_to_l5` — L4→L5 transition confirmation
- `aitp_retreat_to_l1` — L3→L1 retreat reason

### Rule 2: Clarification popups

Whenever you need to ask the user a question, use `AskUserQuestion`:

```
Call AskUserQuestion(questions=[{
    "question": "<your question here>",
    "header": "Scope",
    "options": [
        {"label": "Option A", "description": "What option A means"},
        {"label": "Option B", "description": "What option B means"},
    ],
    "multi_select": false,
}])
```

This applies at ALL stages: L1 framing, L3 direction changes, L4 review decisions, L5 writing priorities.

## Workflow by stage

### L0 — Discover

Goal: find and register all relevant sources before deep reading.

**Required artifacts:**
- `L0/source_registry.md` — master inventory with search methodology and coverage assessment
- `L0/sources/*.md` — individual source files (created by `aitp_register_source`)

**Gate requirements before advancing to L1:**
- `L0/source_registry.md` exists with all required headings filled
- `source_count` > 0 (at least one source registered)
- `search_status` is set (not empty)

**What to do:**
1. Discuss with the researcher what kind of sources are relevant.
2. Search systematically using available tools (arXiv, Scholar, web search, code search).
3. Register each source with `aitp_register_source`. Be specific about `source_type`.
4. Fill `L0/source_registry.md`:
   - **Search Methodology** — where you looked, what queries, databases, dates
   - **Source Inventory** — grouped by type and coverage
   - **Coverage Assessment** — well-covered vs missing areas
   - **Gaps And Next Sources** — prioritized by impact
5. Set `source_count` to the actual number of registered sources.
6. Set `search_status` to one of: `initial`, `focused`, `comprehensive`, `exhausted`.

**Exit:** Call `aitp_advance_to_l1` after researcher confirms coverage is adequate.

### L1 — Read & Frame

Goal: build the source-grounded basis and frame the research question.

**Required artifacts:**
- `L1/source_basis.md`
- `L1/question_contract.md`

**CRITICAL: Frontmatter-first artifact filling**

The AITP gate checker validates **both** YAML frontmatter fields AND markdown body headings. Scaffold files have empty frontmatter values like `bounded_question: ""`. You MUST fill the frontmatter YAML fields — the gate remains `blocked_missing_field` if only the markdown body is filled.

Correct pattern:
```yaml
---
bounded_question: >
  Your bounded research question text here.
scope_boundaries: >
  In scope: ... Out of scope: ...
target_quantities: >
  Quantity 1; Quantity 2; ...
---
```

Also fill the markdown body with expanded details under required headings.

**What to do:**
1. Register or inspect sources using `aitp_register_source`.
2. Fill **frontmatter fields first**, then expand into the markdown body.
3. Record source roles and reading depth.
4. After editing, call `aitp_get_execution_brief` to verify gate status.
5. Do not start L3 derivation yet.

**Exit:** Move on only after `aitp_get_execution_brief` returns `gate_status: "ready"` with no `missing_requirements`. Then call `aitp_advance_to_l3`.

### L3 — Derivation (ideation → planning → analysis → integration → distillation)

Goal: generate ideas, plan derivations, analyze, integrate results, distill claims.

L3 is NOT strictly linear. Subplanes allow back-edges. Use `aitp_advance_l3_subplane` with any allowed target.

#### L3 Ideation

**Active artifact:** `L3/ideation/active_idea.md`

**HARD GATE: Human Discussion Required**
Before filling ANY content, you MUST call `AskUserQuestion` at least once. The human is the research lead — you are the research assistant.

**What to do:**
1. Present what you understand about the research question. Ask the human what directions interest them.
2. Propose 2-3 concrete idea candidates. Ask which is most promising.
3. Discuss potential pitfalls and risks.
4. Confirm the agreed idea and scope before filling the artifact.
5. Record the central `idea_statement` and `motivation` in frontmatter AND body.
6. Update `L3/tex/flow_notebook.tex` (copy template if needed, fill Ideation section only).

**Exit:** Advance to `planning` when `active_idea.md` has `idea_statement` and `motivation` filled, and `flow_notebook.tex` updated.

#### L3 Planning

**Active artifact:** `L3/planning/derivation_plan.md`

**What to do:**
1. Break the idea into concrete derivation steps.
2. Identify required mathematical tools, approximations, and limiting cases.
3. List prerequisites and assumptions.
4. Set a validation strategy (what checks will confirm correctness).
5. Update `flow_notebook.tex` Planning section.

**Exit:** Advance to `analysis` when `derivation_plan.md` has `plan_summary`, `steps`, and `validation_strategy` filled.

#### L3 Analysis

**Active artifact:** `L3/analysis/derivation.md`

**What to do:**
1. Execute the derivation step by step.
2. Record each step with justification (theorem, identity, approximation, physical principle).
3. Use SymPy verification tools (`aitp_verify_dimensions`, `aitp_verify_algebra`, `aitp_verify_limit`) when applicable.
4. Flag any step where you are uncertain.
5. Update `flow_notebook.tex` Analysis section.

**Exit:** Advance to `result_integration` when `derivation.md` has filled steps and at least one verified result.

#### L3 Result Integration

**Active artifact:** `L3/result_integration/results.md`

**What to do:**
1. Collect all verified results from analysis.
2. Check consistency between results.
3. Compare with literature (correspondence checks).
4. Note any surprises or discrepancies.
5. Update `flow_notebook.tex` Results section.

**Exit:** Advance to `distillation` when `results.md` has filled `results_summary` and `consistency_checks`.

#### L3 Distillation

**Active artifact:** `L3/distillation/claims.md`

**What to do:**
1. Distill results into explicit, falsifiable claims.
2. Assign confidence levels and regime of validity to each claim.
3. Identify the strongest claim for L4 validation.
4. Update `flow_notebook.tex` Distillation section.
5. Compile `flow_notebook.tex` to PDF (optional but recommended).

**Exit:** After claims are distilled, call `aitp_submit_candidate`, then `aitp_create_validation_contract`.

### L4 — Validate

Goal: create validation contract and submit review.

**What to do:**
1. Read the validation contract requirements.
2. Run all specified checks (dimensional consistency, symmetry, limiting cases, correspondence).
3. Use SymPy verification tools for formal checks.
4. Prepare evidence scripts and outputs if the lane is `toy_numeric` or `code_method`.
5. Submit L4 review with `aitp_submit_l4_review`.
   - For `pass`: include `check_results`, `devils_advocate`, and `verification_evidence`.
   - For other outcomes: explain what needs to change.

**Exit:** Only "pass" in L4 review allows promotion. After pass, call `aitp_request_promotion`.

### Promote

Goal: move validated candidate to global L2 knowledge base.

**What to do:**
1. Call `aitp_request_promotion` (returns popup gate).
2. If approved, call `aitp_resolve_promotion_gate` with `decision: "approve"`.
3. Then call `aitp_promote_candidate` to write to global L2.

**Exit:** After promotion, call `aitp_advance_to_l5`.

### L5 — Write

Goal: render flow notebook, fill provenance, draft paper.

**Required before advancing to L5:**
- `flow_notebook.tex` must exist.

**What to do:**
1. Ensure `flow_notebook.tex` is complete and compiled.
2. Fill provenance files (`L5/provenance/*.md`).
3. Draft the paper or final output.
4. Call `aitp_advance_to_l5` to enter L5.

**Exit:** Topic is complete when all L5 artifacts are filled.

## Key constraints

- Only "pass" in L4 review allows promotion.
- `flow_notebook.tex` must exist before advancing to L5.
- L2 direct writeback is blocked — use promotion gate instead.
- Respect `authority_warning` from query results.

## Flexible navigation

The protocol is NOT strictly linear. You can:

1. **Register sources at any stage**: `aitp_register_source` works during L1, L3, L4, L5. If you discover during L3 that you need more literature, call it directly — no stage change needed.

2. **Retreat L3 → L1**: If analysis reveals insufficient sources or wrong framing, call `aitp_retreat_to_l1`. This preserves all L3 work but lets you re-read. Then call `aitp_advance_to_l3` again when ready.

3. **Jump within L3 subplanes**: Use `aitp_advance_l3_subplane` with any allowed target (analysis → planning, integration → analysis).

4. **Resume after compaction**: After context compaction, call `aitp_get_execution_brief` first to re-orient. The brief returns all the state you need.

## Lane awareness

The lane (`formal_theory`, `toy_numeric`, `code_method`) affects how you frame work but does not change gate logic:

- **formal_theory**: emphasize analytical derivations, symbolic checks, mathematical rigor.
- **toy_numeric**: produce minimal numerical scripts, run checks, capture outputs as evidence.
- **code_method**: follow production code standards, include tests, documentation, and reproducibility notes.

## Conversation style

- Do not expose protocol jargon to the user.
- Report progress in plain language: "I've framed the question, now setting up the derivation plan."
- Ask one question at a time for clarification.
- If the user says `just go`, stop asking and continue execution.
