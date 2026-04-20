---
name: skill-read
description: Read posture — build the source basis before framing or derivation.
trigger: posture == "read"
---

# Read Posture

## MANDATORY: AskUserQuestion rule

When you need to ask the user ANY question (clarification, scope, direction, missing info), you MUST:
1. Call `ToolSearch(query="select:AskUserQuestion", max_results=1)` to load the tool.
2. Call `AskUserQuestion(questions=[{...}])` with your question and options.
NEVER type questions or options as plain text. ALWAYS use the popup tool.

---

You are building the topic's source-grounded basis.

## Required artifacts

- `L1/source_basis.md`
- `L1/question_contract.md`

## What to do now

1. Register or inspect the source basis using `aitp_register_source`.
2. Fill the bounded question if it is still blank.
3. Record source roles and reading depth.
4. Do not start L3 derivation yet.

## Exit condition

Move on only after the source basis and bounded question are explicit.
