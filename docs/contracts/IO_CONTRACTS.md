# AITP Layer I/O Contracts v1.0

Status: authoritative, subordinate to AITP_SPEC.md.
Purpose: Define explicit input/output contracts for every protocol layer.
         All development MUST verify changes against these contracts.

## Principle

Each layer is a black box with defined inputs and outputs. Changes within
a layer MUST NOT break downstream consumers. The contract defines what the
layer PROMISES to produce and what it REQUIRES to function.

Tests in `tests/test_io_contracts.py` validate these contracts mechanically.

---

## L0 — Source Acquisition

### Input (what must exist before L0 work begins)
| Input | Provider | Format |
|-------|----------|--------|
| `state.md` | bootstrap | stage=L0, posture=discover, lane set |
| `L0/source_registry.md` | bootstrap | scaffold with source_count=0 |

### Output (what L0 MUST produce)
| Output | Consumer | Contract |
|--------|----------|----------|
| `L0/source_registry.md` | L1 gate | source_count ≥ 1, search_status filled |
| `L0/sources/*.md` | L1 reading | ≥ 1 source file with source_id, type, title |

### Gate (conditions to advance to L1)
| Check | Enforced by |
|-------|------------|
| source_registry.md exists | evaluate_l0_stage |
| source_count non-empty | evaluate_l0_stage |
| search_status non-empty | evaluate_l0_stage |
| ≥ 3 body headings present | evaluate_l0_stage |
| ≥ 1 source file in L0/sources/ | evaluate_l0_stage |

### Transition: L0 → L1
| Tool | Pre-condition | Post-condition |
|------|--------------|----------------|
| `aitp_advance_to_l1` | gate_status == "ready" | stage = "L1", posture = "read" |

---

## L1 — Reading and Framing

### Input
| Input | Provider | Format |
|-------|----------|--------|
| L1 scaffolds (6 artifacts) | advance_to_l1 | empty frontmatter + headings |
| Source files from L0 | register_source | source_id, type, title, fidelity |
| L2 knowledge graph | query_l2_index | existing concepts, theorems |

### Output
| Output | Consumer | Required Fields |
|--------|----------|-----------------|
| `question_contract.md` | L1 gate, L3 context | bounded_question, scope_boundaries, target_quantities |
| `source_basis.md` | L1 gate | core_sources, peripheral_sources |
| `convention_snapshot.md` | L1 gate, L3 derivation | notation_choices, unit_conventions |
| `derivation_anchor_map.md` | L1 gate, L3 derivation | starting_anchors, anchor_count |
| `contradiction_register.md` | L1 gate, L4 validation | blocking_contradictions |
| `source_toc_map.md` | L1 gate | sources_with_toc, coverage_status |
| `L1/intake/**/*.md` | L1 gate, L3/L2 | source_id, section_id, extraction_status, completeness_confidence |

### Gate
| Check | Enforced by |
|-------|------------|
| All 6 artifacts exist + frontmatter non-empty + headings present | evaluate_l1_stage |
| Question semantic validity: stem, scope exclusion, competing hypotheses | _check_question_semantic_validity |
| Coverage: extracted sections have intake notes, confidence ≥ low | evaluate_l1_stage |

### Transition: L1 → L3
| Tool | Pre-condition | Post-condition |
|------|--------------|----------------|
| `aitp_advance_to_l3` | gate_status == "ready" | stage = "L3", posture = "derive", l3_activity = "ideate" |

---

## L3 — Flexible Workspace

### Input
| Input | Provider | Format |
|-------|----------|--------|
| All 6 L1 artifacts + intake notes | L1 gate pass | filled frontmatter + body |
| L2 knowledge graph | query_l2_index | reusable knowledge |
| Registered sources | L0 | source files |

### Output
| Output | Consumer | Contract |
|--------|----------|----------|
| `L3/<activity>/active_*.md` | L3 gate | activity-specific frontmatter + headings |
| `L3/candidates/<id>.md` | L4 validation | claim, evidence, regime_of_validity |
| `L3/ideas/<id>.md` | L3 ideation | idea_statement, motivation |

### Activities and their contracts

| Activity | Artifact | Required Fields | Required Headings |
|----------|----------|-----------------|-------------------|
| ideate | active_idea.md | idea_statement, motivation | Idea Statement, Motivation |
| derive | active_derivation.md | derivation_count, all_steps_justified | Derivation Chains, Step-by-Step Trace |
| trace-derivation | active_trace.md | source_id, derivation_count | Source Reference, Derivation Chains |
| gap-audit | active_gaps.md | gap_count, blocking_gaps | Unstated Assumptions, Correspondence Check |
| connect | active_connect.md | connection_summary | Concepts Being Connected, Proposed Edges |
| integrate | active_integration.md | integration_statement, findings | Integration Statement, Findings |
| distill | active_distillation.md | distilled_claim, evidence_summary | Distilled Claim, Evidence Summary |

### Gate
| Check | Enforced by |
|-------|------------|
| Current activity artifact exists + frontmatter non-empty + headings present | evaluate_l3_stage |

### Transition: L3 → L4 (via candidate submission)
| Tool | Pre-condition | Post-condition |
|------|--------------|----------------|
| `aitp_submit_candidate` | current activity artifact filled | candidate.md created in L3/candidates/ |

### Re-entry: L4 → L3
| Tool | Pre-condition | Post-condition |
|------|--------------|----------------|
| `aitp_return_to_l3_from_l4` | stage=L4, ≥1 review exists | stage=L3, l3_activity=integrate |

---

## L4 — Validation

### Input
| Input | Provider | Format |
|-------|----------|--------|
| Candidate from L3 | submit_candidate | claim, evidence, regime_of_validity |
| L1 artifacts | L1 | conventions, assumptions, anchors |
| L2 knowledge graph | query_l2 | conflicting claims to check |

### Output
| Output | Consumer | Contract |
|--------|----------|----------|
| `L4/reviews/<id>.md` | L4 gate, promotion | outcome, devils_advocate, check_results |
| `L4/scripts/*.py` | L4 gate (numeric lanes) | evidence_scripts |
| `L4/outputs/*` | L4 gate (numeric lanes) | evidence_outputs |

### Gate
| Check | Enforced by |
|-------|------------|
| ≥ 1 candidate exists in L3/candidates/ | evaluate_l4_stage |
| Each candidate has a review in L4/reviews/ | evaluate_l4_stage |
| ≥ 1 candidate status == "validated" | evaluate_l4_stage |
| Review body has ## Counterargument or similar | evaluate_l4_stage |

### Transition: L4 → Promotion
| Tool | Pre-condition | Post-condition |
|------|--------------|----------------|
| `aitp_request_promotion` | stage=L4/L2, candidate=validated, L4 review exists with outcome=pass | candidate status = pending_approval |

### L2 Promotion
| Tool | Pre-condition | Post-condition |
|------|--------------|----------------|
| `aitp_resolve_promotion_gate` | status = pending_approval | status = approved_for_promotion or rejected |
| `aitp_promote_candidate` | status = approved_for_promotion | promoted to global L2, l2_path recorded |

---

## Cross-Cutting: Execution Brief

### Input
| Input | Provider |
|-------|----------|
| Topic state.md | bootstrap/advance tools |

### Output (ALL stages)
| Field | Guarantee |
|-------|-----------|
| topic_slug | always present |
| stage | L0, L1, L3, L4, L2 (L5 redirected to L1) |
| posture | discover, read, frame, derive, verify |
| gate_status | ready or blocked_* |
| missing_requirements | list of specific fixes needed |
| skill | which skill to load |
| immediate_allowed_work | what the agent can do now |
| immediate_blocked_work | what the agent cannot do |

---

## Testing Philosophy

Every layer contract MUST have:
1. **Input validation test**: given valid inputs, gate passes
2. **Blocking test**: given missing inputs, gate blocks with specific message
3. **Transition test**: advance tool produces correct post-condition
4. **Output format test**: artifacts have required frontmatter + headings

Run: `python -m pytest tests/test_io_contracts.py`
