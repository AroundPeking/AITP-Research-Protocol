---
artifact_kind: l1_convention_snapshot
notation_choices: 'Protocol layers: L0(discover)→L1(read)→L2(cross-topic KG)→L3(derive)→L4(validate)→L5(write). Tool naming: aitp_<verb>_<noun>. Skill naming: skill-<stage>-<subplane>.md. Adversarial collaborator: the agent-in-skill that asks Socratic questions, not checklist items.'
required_fields:
- notation_choices
- unit_conventions
stage: L1
unit_conventions: 'Code: Python 3.10+, FastMCP framework, pytest, PyYAML. Storage: Markdown files with YAML frontmatter (no JSON, no SQL). File naming: snake_case for slugs, kebab-case for artifact directories.'
---
# Convention Snapshot

## Notation Choices

- **Protocol layers**: L0 (discover) → L1 (read/frame) → L2 (cross-topic knowledge graph) → L3 (derive, research or study mode) → L4 (validate) → L5 (write)
- **Tool naming**: `aitp_<verb>_<noun>` e.g., `aitp_create_l2_node`, `aitp_query_l2`
- **Skill naming**: `skill-<stage>-<subplane>.md` for stage-specific, descriptive names for cross-cutting skills
- **Adversarial collaborator**: The persona embedded in each skill file that asks Socratic/critical questions — modeled after a skeptical but constructive peer reviewer or co-author
- **"Python never judges"**: A design invariant — no Python function returns a content-quality verdict, trust assessment, or physics correctness claim

## Unit Conventions

- Python 3.10+, FastMCP framework
- pytest for testing, PyYAML for frontmatter parsing
- All persistence: Markdown files with YAML frontmatter (no JSON, no SQL, no embedings DB)
- File naming: snake_case for slugs, kebab-case for artifact directories

## Sign Conventions

- **Remove, don't add**: Default action is deleting tools, not creating new ones
- **Skill over Python**: When in doubt, put logic in skill files (LLM-mediated), not in Python (deterministic but dumb)
- **Storage is sacred**: File I/O must be atomic and reliable — this is Python's only real responsibility

## Metric Or Coordinate Conventions

- Code measured in: tool count (~15 target), lines of Python (targeting significant reduction from 3273), test coverage (must not regress)
- Quality measured in: how well the protocol enables a real physics research conversation, not in checkboxes checked

## Unresolved Tensions

1. Semantic search — can we get good enough results without embedding models? (Pure Python: token overlap + concept aliases + LaTeX normalization)
2. Gate evaluation — if Python doesn't check content, what signals "you're not ready to advance"? Answer: skill-level adversarial questions that the agent must answer honestly
3. Backward compatibility — existing topics have state.md fields the new protocol won't use (l3_mode, gate_status variants, loop state). Migration strategy: new code reads old fields gracefully, writes only new fields
