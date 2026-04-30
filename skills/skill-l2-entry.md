---
name: skill-l2-entry
description: L2 Knowledge Entry — retrieve prior knowledge before starting a topic, and record distilled knowledge after completing a topic phase. Three-layer retrieval: entries (Grep) → graph (MCP) → tower (MCP).
trigger: topic bootstrap, session resume, or phase completion
---

# L2 Knowledge Entry

## MANDATORY: AskUserQuestion rule

When you need to ask the user ANY question, use `AskUserQuestion`. NEVER type options as plain text.

---

## Part A: Retrieval (topic start)

Executed at topic bootstrap, session resume, or whenever the user asks "what do we know about X".

### Layer 1: Entries (file-based, Grep)

Search the `L2/entries/` directory for prior knowledge:

```
Glob(pattern="L2/entries/*.md", path=$TOPICS_ROOT)
Grep(pattern="role: <target>", path="L2/entries/")
```

Query patterns by use case:

| Question | Grep |
|----------|------|
| "What's known about system X?" | `grep -l "system_id:.*<slug>" L2/entries/*.md` |
| "Verified claims?" | `grep -l "role: claim.*status: verified" L2/entries/*.md` |
| "Known pitfalls for method X?" | `grep -l "role: pitfall" L2/entries/*.md` |
| "What methods exist?" | `grep -l "role: method" L2/entries/*.md` |
| "Open questions?" | `grep -l "role: question" L2/entries/*.md` |

Read matching entries to get full details (templates, workflow steps, symptoms/fixes).

### Layer 2: Graph (MCP)

Query the concept graph for theoretical relationships:

```
aitp_query_l2_index(topics_root)                    → domain taxonomy
aitp_query_l2_graph(topics_root, query="<concept>") → matching nodes + edges
```

### Layer 3: Tower (MCP)

Check regime boundaries:

```
aitp_visualize_eft_tower(topics_root, tower_id="<id>")
aitp_query_l2_graph(topics_root, node_type="regime_boundary")
```

### Synthesis

Present to the researcher as:

```
PRIOR KNOWLEDGE: <system/method>
  Verified:   <list of claims with status=verified>
  Unverified: <list of claims with status=unverified or failed>
  Pitfalls:   <list of known issues>
  Questions:  <list of open questions>
  Concepts:   <relevant graph nodes>
  Regime:     <applicable tower layers>
```

This becomes the `## Prior L2 Knowledge` section in `L0/source_registry.md`.

---

## Part B: Recording (topic phase completion)

Executed after L4 validation, after a pitfall is discovered, or when the researcher explicitly asks to record.

### Entry roles and when to record

| Role | When | Mandatory facets |
|------|------|-----------------|
| **claim** | L4 pass, confirmed result, or formula derivation | `claim_type`, `statement`, `mathematical_expression`, `evidence_type` |
| **system** | First time studying this physical system | `system_type`, `formula_or_identifier`, `reference_values` |
| **method** | First time using/validating a workflow | `method_type`, `toolchain`, `steps` |
| **pitfall** | Any bug, crash, or subtle issue encountered | `symptom`, `cause`, `fix`, `affects_methods` |
| **question** | Open problem identified but not yet pursued | `question_statement`, `competing_hypotheses` |

### Entry file format

Save as `L2/entries/<role>-<slug>.md`:

```markdown
---
entry_id: <unique-slug>
role: claim | system | method | pitfall | question
title: <one-line summary>
lane: [formal_theory | toy_numeric | code_method]
status: verified | consistent | unverified | failed | conjectured
regime: <when does this hold?>

# Role-specific below ---
claim_type: theorem | result | approximation | negative_result | definition | equation
statement: <the claim in one sentence>
mathematical_expression: <LaTeX if applicable>
observable: <what quantity>
evidence_type: analytic_proof | numerical | experimental | code_derived
# ... OR ...
system_type: material | hamiltonian | field_theory | lattice_model | phase | spacetime
formula_or_identifier: <chemical formula / Hamiltonian / Lagrangian>
reference_values: <known benchmarks>
# ... OR ...
method_type: numerics | analytics | experiment | code
toolchain: [<tools>]
steps: [<step1>, <step2>, ...]
# ... OR ...
symptom: <what the user sees>
cause: <root cause>
fix: <how to resolve>
affects_methods: [<method slugs>]
# ... OR ...
question_statement: <the research question>
competing_hypotheses: [<possible answers>]

source_ref: topic:<topic-slug>
updated: YYYY-MM-DD
---

# <Title>

<Human-readable explanation, prose, formulas, code snippets.>

## Relationships
- derives_from: <other-entry-id>
- verified_by: <other-entry-id>
- blocked_by: <other-entry-id>
```

### Entry quality rules

1. **status must be honest.** If a calculation failed or a formula is untested, status is `unverified` or `failed`. Never `verified` without independent confirmation.
2. **Pitfalls must be complete.** Symptom + cause + fix. Without all three, the next person can't debug.
3. **Methods must have templates.** If it's a code method and there's a working INPUT/librpa.in, embed or link it.
4. **Provenance mandatory.** Every entry must record `source_ref`.
5. **One file per fact.** Don't put unrelated claims in one file. Atomic entries are queryable; long documents are buried.
