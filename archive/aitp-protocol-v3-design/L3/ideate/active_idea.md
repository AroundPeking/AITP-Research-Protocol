---
artifact_kind: l3_active_idea
idea_statement: 'Tool triage: classify all 50 MCP tools as KEEP (pure storage+search), CUT (pseudo-intelligent checks, self-validation loops), or REWRITE (simplify). Then implement in 4 steps: (1) cut ~30 tools, (2) simplify gate evaluators to file-existence-only, (3) upgrade L2 search from substring to semantic, (4) rewrite skill files as adversarial collaborators.'
motivation: 'Python code trying to encode physics judgment is the root cause of the protocol feeling mechanical. Cutting it back to pure storage+search makes the protocol thinner and smarter — LLMs do the thinking, Python does the filing.'
required_fields:
- idea_statement
- motivation
subplane: ideation
---
# Active Idea

## Idea Statement

**Phase A — Tool Triage**: Classify all 50 MCP tools:
- **KEEP (~15)**: Pure file persistence (bootstrap, register, submit, create_l2_*), query/read (list_topics, get_status, query_l2, query_l2_graph), maintenance (archive, restore, update_status, health_check)
- **CUT (~30)**: Content-quality pretenders (lint_knowledge, check_correspondence, check_composability → these become skill prompts), self-validation loops (start/stop_research_loop, return_to_l3_from_l4), busywork generators (advance_to_l5 with flow_notebook gate, coverage_map), redundant wrappers (ingest_knowledge duplicates register_source, query_knowledge duplicates query_l2)
- **REWRITE (~5)**: Gate evaluators (strip to file-existence only), L2 search (semantic from substring), get_execution_brief (remove stale gate_status from state.md, always live-evaluate)

**Phase B — Implement cuts**: Remove tools from mcp_server.py, remove associated constants from state_model.py, update test files.

**Phase C — Semantic search**: Token-aware matching + concept alias expansion + LaTeX normalization in query_l2 and query_l2_graph.

**Phase D — Adversarial skills**: Rewrite 3 core skills (using-aitp, aitp-runtime, aitp-derivation-loop) with role-based Socratic prompts.

## Motivation

Every line of Python that tries to "verify physics" is a line that:
1. Can't actually verify physics (string comparison ≠ dimensional analysis)
2. Creates false confidence (agent sees "gate ready" and assumes quality)
3. Adds maintenance burden (50 tools, 3273 lines, 12 test files)

Cutting to ~15 tools:
- Makes the protocol honest about what Python can/can't do
- Puts judgment where it belongs (LLM-mediated skill prompts)
- Makes the codebase maintainable
- Every remaining tool has a clear, non-overlapping purpose

## Prior Work

The 26-problem critique identified which tools are problematic and why. The adversarial-collaborator design note sketched the target state. This ideation makes it concrete: which tools live, which die, which change.

## Risk Assessment

| Risk | Mitigation |
|------|-----------|
| Cutting tools breaks existing topics | Keep file formats backward-compatible; cut tools that do computation, not tools that read/write |
| Semantic search without embeddings is weak | Start with alias table + token overlap; if insufficient, add optional embedding dependency later |
| Adversarial skills confuse agents | Write clear, concrete Socratic questions; test with multiple LLM backends |
| Gate too thin → agents bypass protocol | Trust that adversarial skill prompts + human oversight catch more than Python ever could |
