---
artifact_kind: l1_derivation_anchor_map
required_fields:
- starting_anchors
stage: L1
starting_anchors: '50 MCP tools as baseline; protocol-critique 26 problems as requirements; adversarial-collaborator-design as target architecture; test suite as compatibility constraint'
---
# Derivation Anchor Map

## Source Anchors

| Anchor | Source | What it provides |
|--------|--------|------------------|
| Current tool inventory | mcp_server.py | 50 tools to triage (keep/cut/rewrite) |
| Gate evaluators | state_model.py | L0/L1/L3/L4/L5 evaluation logic to simplify |
| L2 infrastructure | mcp_server.py lines 2187-3100 | Node/edge/tower CRUD, query, visualization |
| Skill architecture | skills/*.md (20 files) | Reference for what adversarial skills should replace |
| 26 problems | critique | Design constraints — each must be addressed |
| Test suite | tests/*.py (12 files) | "Do not break" contract |

## Missing Steps

1. Which 15 tools survive? (Triage decision — not derivable from sources alone, requires design judgment)
2. What does an adversarial skill file look like concretely? (Template to design)
3. How does semantic search work without embeddings? (Algorithm to specify)

## Candidate Starting Points

1. **Start from tools**: List all 50 tools, classify each as keep/cut/rewrite, implement cuts first
2. **Start from skills**: Write one exemplary adversarial skill, then reshape Python to support it
3. **Start from L2**: Fix search (highest-leverage Python change), then do tool reduction

Recommended: **Start from tools (route 1)** — triage is the clearest first step.
