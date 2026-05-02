---
artifact_kind: l1_question_contract
bounded_question: 'Refactor AITP from 50-tool compliance-checking protocol to ~15-tool
  adversarial-collaborator protocol: Python handles only file persistence + semantic
  search, all physics judgment lives in skill files as Socratic/role-based prompts.'
competing_hypotheses: 'Alternative explanations exist for the target phenomenon. Without
  explicit comparison, the claimed mechanism cannot be distinguished from competing
  hypotheses. [FILL: specific alternatives]'
required_fields:
- bounded_question
- scope_boundaries
- target_quantities
scope_boundaries: 'MCP server brain/mcp_server.py and brain/state_model.py, plus skill
  files. Does NOT include: UI, external MCP integrations, Zotero/Obsidian sync, numerical
  computing infrastructure. Study mode pipeline is in-scope because it feeds L2.'
stage: L1
target_quantities: '1) Tools: cut from 50 to ~15. 2) Gate evaluators: remove content-quality
  pretensions, keep only file-existence checks. 3) L2 search: semantic from substring.
  4) Skill files: rewritten as role-based adversarial prompts. 5) Autonomous loops:
  removed or gated behind human review. 6) All existing tests must still pass (behavior
  preserved where tools remain).'
---
# Question Contract

## Bounded Question

How to refactor the AITP protocol so that:
1. Python (MCP server) handles ONLY file persistence and semantic search (~15 tools)
2. All physics judgment is embedded in skill files as adversarial collaborator prompts
3. The agent behaves like a skeptical theoretical physicist co-author, not a form-filling clerk
4. The protocol gets better with use (L2 knowledge accumulation that actually helps future research)


## Competing Hypotheses

[FILL: specific alternative hypotheses that could explain the same observations. What other answers exist and why might they be wrong?]

## Scope Boundaries

**In scope:**
- `brain/mcp_server.py` tool reduction and restructuring
- `brain/state_model.py` simplification (remove pseudo-intelligent checks)
- L2 knowledge graph: semantic search, concept aliases, LaTeX indexing
- Skill files: adversarial collaborator pattern
- Study mode pipeline: L0→L1→L3 study→L2

**Out of scope:**
- External MCP integrations (Zotero, Obsidian, paper-search, arxiv-latex)
- Numerical computing infrastructure (Jupyter, Fisher server)
- UI/UX beyond the MCP tool interface
- Topic migration scripts for existing 7 topics

## Target Quantities Or Claims

1. **Tool count**: Cut from 50 → 15 (±3)
2. **Gate logic**: `evaluate_l*_stage()` only checks file existence + required headings existence; removed: content quality claims, auto-trust decisions
3. **L2 search**: Replaces Python `in` operator with token-aware matching, concept alias expansion, LaTeX normalization
4. **Skill architecture**: Each skill file defines a ROLE + CRITICAL QUESTIONS, not a checklist
5. **Autonomous loop**: Removed from Python; replaced with skill-level guidance on when to pause for human input
6. **Backward compatibility**: All existing pytest tests pass (where tools still exist)

## Non-Success Conditions

- Creating new Python logic that tries to "verify" physics content
- Adding more required fields to artifacts
- Making the protocol more rigid or checklist-driven
- Breaking existing topic data or test suite

## Uncertainty Markers

- How thin can Python get before file I/O becomes too fragile?
- Can semantic search remain pure-Python (no embeddings API dependency)?
- Will adversarial skill prompts work consistently across different LLM backends?
- Transition path for existing 7 topics (3 in L3 distillation, 2 in L1)
