---
name: skill-frame
description: Frame posture — lock conventions, anchors, and contradictions before derivation.
trigger: posture == "frame"
---

# Frame Posture

## MANDATORY: AskUserQuestion rule

When you need to ask the user ANY question (clarification, scope, direction, missing info), you MUST:
1. Call `ToolSearch(query="select:AskUserQuestion", max_results=1)` to load the tool.
2. Call `AskUserQuestion(questions=[{...}])` with your question and options.
NEVER type questions or options as plain text. ALWAYS use the popup tool.

---

You are preparing the topic for honest derivation.

## Required artifacts

- `L1/convention_snapshot.md`
- `L1/derivation_anchor_map.md`
- `L1/contradiction_register.md`

## What to do now

1. Lock notation, unit, sign, and metric conventions.
2. Record derivation anchors from the source basis.
3. Make contradictions explicit and mark whether they block derivation.
4. Do not advance to `L3` while these artifacts are incomplete.

## Exit condition

Move on only when the topic has a usable convention snapshot, at least one derivation anchor, and scoped contradictions.
