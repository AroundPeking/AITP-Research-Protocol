---
artifact_kind: l1_source_basis
core_sources: 'current-mcp-server-codebase, protocol-critique-20260424, adversarial-collaborator-design'
peripheral_sources: 'existing-7-topics, test-suite-5000-lines, claude-skills-v2'
required_fields:
- core_sources
- peripheral_sources
stage: L1
---
# Source Basis

## Core Sources

1. **current-mcp-server-codebase**: `brain/mcp_server.py` (3273 lines, 50 @mcp.tool()), `brain/state_model.py` (912 lines, gate evaluators, templates, constants). This is the substrate to be refactored. Every tool function, every gate evaluator, every template is candidate for deletion or rewrite.

2. **protocol-critique-20260424**: The 26-problem analysis from a theoretical physicist's perspective. Organized by: gate quality (4 problems), L2 knowledge representation (6), mathematical verification (4), trust model (4), workflow (5), scaling (3). This is the "what's broken" reference.

3. **adversarial-collaborator-design**: Design direction note establishing: Python = storage + search only; Skills = role-based adversarial prompts; L2 = conversationally curated; no autonomous LLM-self-validation loops. This is the "where we're going" reference.

## Peripheral Sources

- Existing 7 AITP topics (real usage data showing what's working and what's not)
- Test suite ~5000 lines (what behaviors are currently promised)
- `.claude/skills/` v2 skill files (reference for what good skills look like)

## Source Roles

| Source | Role |
|--------|------|
| mcp_server.py + state_model.py | Primary substrate — what gets cut/rewritten |
| protocol-critique | Requirements document — what must be fixed |
| adversarial-collaborator-design | Architecture vision — how it should work |
| Test suite | Compatibility constraint — what must not break |
| Existing 7 topics | Migration constraint — data must survive |

## Reading Depth

All sources are local, relatively short (< 5000 lines total), and already deeply analyzed. No need for extended reading phase — move quickly to design (L3).

## Why Each Source Matters

- **codebase**: You can't refactor what you haven't read
- **critique**: 26 specific bugs/gaps, each is a design constraint
- **design note**: The positive vision — if the critique says "don't do X", the design note says "do Y instead"
