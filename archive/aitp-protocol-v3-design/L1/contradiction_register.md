---
artifact_kind: l1_contradiction_register
blocking_contradictions: 'none'
required_fields:
- blocking_contradictions
stage: L1
---
# Contradiction Register

## Unresolved Source Conflicts

1. **Autonomous loop design**: The current protocol has `aitp_start_research_loop` for LLM-self-validating L3-L4 cycles. The critique identifies this as dangerous (noise amplification). But removing it entirely might make L4 too slow for code_method topics where numerical validation is automated. Resolution: remove autonomous loop from Python, replace with skill-level guidance on "when to pause for human vs when to auto-continue."

2. **Gate evaluation thinness**: If Python gates only check file existence, what prevents an agent from creating empty files and "passing" all gates instantly? Resolution: adversarial skill prompts that make the agent self-assess before calling advance tools. This is trust-in-LLM, not trust-in-Python.

3. **Skill vs Python boundary**: How thin can Python get before the MCP server is just a file I/O wrapper? Is that too thin? Resolution: Python still owns semantic search (algorithmic), atomic writes (reliability), and slug validation (security). These are things Python does better than LLMs.

## Regime Mismatches

- v2 protocol (current) was designed for a single researcher using CLI tools
- v3 protocol (target) operates as an MCP server invoked by LLM agents
- Skill files need to work across different LLM backends (Claude, GPT, etc.) — adversarial prompts must be model-agnostic

## Notation Collisions

- "Stage" vs "layer" vs "subplane" — these three concepts overlap confusingly. Consider simplifying to just "stage" and "mode."
- "L2" means two things: (1) the global cross-topic knowledge graph, (2) the protocol layer between L1 and L3. These are the same thing but the naming is confusing.

## Blocking Status

No blocking contradictions. All tensions have reasonable resolutions. Proceed to L3.
