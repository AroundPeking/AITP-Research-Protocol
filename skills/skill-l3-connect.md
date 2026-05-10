---
name: skill-l3-connect
description: L3 Connection — propose, verify, and record edges between concepts in the L2 knowledge graph.
trigger: l3_activity == "connect"
---

# L3 Connection

## MANDATORY: AskUserQuestion rule

When you need to ask the user ANY question, you MUST:
1. Call `ToolSearch(query="select:AskUserQuestion", max_results=1)` to load the tool.
2. Call `AskUserQuestion(questions=[{...}])` with your question and options.
NEVER type questions or options as plain text. ALWAYS use the popup tool.

---

Connect is a **sidecar activity** — enter from any other L3 activity, create or verify
L2 knowledge-graph nodes and edges, then return to the previous activity. It has no
gate prerequisites and does not require `completion_status: complete`.

## Common Preamble

### L1 Context
1. `L1/source_basis.md` — which sources anchor the concepts being connected
2. `L1/convention_snapshot.md` — conventions that must align across concepts
3. `L1/contradiction_register.md` — known conflicts that might affect connection validity

### Escape Hatches
- Retreat to L1 (`aitp_retreat_to_l1`): if source anchoring is insufficient
- Query L2 (`aitp_query_l2` / `aitp_query_l2_graph`): check if connection already exists
- Return to previous activity: switch back via `aitp_switch_l3_activity`

### Active Artifact
`L3/connect/active_connect.md`

---

## Entry Profile Detection

Check the execution brief for `entry_profile`. If absent, default to the context from
the previous activity (learn_paper if coming from trace-derivation, explore_idea if
coming from derive).

---

## Scenario A: explore_idea (connecting novel findings)

### Purpose
After producing findings in derive + gap-audit, connect them to existing L2 nodes
or to other novel findings within the topic.

### Discussion Checkpoints
1. **Candidate identification**: Present concepts that might connect. Ask: "Which connections are most promising?"
2. **Edge type selection**: For each connection, ask: "Should this be `generalizes`, `limits_to`, `derives_from`, or something else?"
3. **Evidence threshold**: Ask: "Is the evidence for this connection sufficient, or should we qualify the edge with lower trust?"
4. **Connection confirmation**: Ask: "Proposed edges: <list>. Create them in L2?"

### Connection Evidence Standards
For each proposed connection, at least one of:
1. **Derivation evidence** — the relationship was derived in the current topic
2. **L2 correspondence** — the relationship maps to an existing L2 edge or pattern
3. **Structural match** — the mathematical structures align (same tensor rank, same symmetry group)

Insufficient: "A and B feel related", "they're both in the same field of physics."

### Exit Conditions
- `## Concepts Being Connected` has at least one entry
- `## Proposed Edges` has at least one edge with evidence
- `## Trust Assessment` filled per edge
- Each confirmed edge created via `aitp_create_l2_edge`

---

## Scenario B: learn_paper (connecting source concepts)

### Purpose
After trace-derivation and gap-audit, connect extracted concepts, theorems, and
derivation chains into the L2 knowledge graph.

### What Counts as Evidence
For each proposed connection, at least one of:
1. **Explicit statement** — the source states the relationship directly
2. **Structural implication** — the source's derivation structure implies it
3. **Correspondence mapping** — the result matches a known L2 concept/node
4. **Author's own cross-reference** — the source cites another work establishing the link

Insufficient: "A and B are in the same paper", "they use similar notation".

### Edge vs. Node Decision

| Situation | Action |
|-----------|--------|
| Two existing L2 nodes need linking | Create edge |
| One concept exists in L2, the other doesn't | Create L2 node FIRST, then create edge |
| The relationship itself is a substantive claim | Create a node, then link via edges |
| Unclear whether the relationship is correct | Create edge with low trust + gap note |

### Discussion Checkpoints
1. **Concept inventory**: "I extracted these concepts from the source: <list>. Which should be connected?"
2. **Evidence review**: "Concept A links to B because <evidence>. Is this strong enough?"
3. **Edge type selection**: "The relationship is <description>. Which edge type?"
4. **Trust level**: "This edge has trust <level>. Does that match the source reliability?"
5. **Connection finalization**: "Proposed: <N> edges. Create them in L2?"

### Exit Conditions
- `## Concepts Being Connected` populated
- `## Proposed Edges` has at least one entry with cited evidence
- `## Trust Assessment` assigns trust level per edge
- `aitp_create_l2_edge` called for each confirmed edge

### Discovered Candidates
If connection work reveals a concept not yet in L2 that deserves its own candidate,
list it under `## Discovered Candidates` for handoff to distill. Connect does NOT
submit candidates directly.

## Candidate Types
Connect does not produce candidates directly (it produces L2 edges). But it may surface:
- `atomic_concept` — a concept from the paper missing in L2
- `correspondence_link` — a cross-domain mapping requiring its own node
- `warning_note` — a connection that reveals a contradiction or tension

## Allowed Transitions
- Forward: return to previous activity (any), or advance to integrate
- Backedges: gap-audit (if evidence gaps found), trace-derivation (if source anchoring needed)
