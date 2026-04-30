---
name: skill-physicist-check
description: Use at EVERY stage transition — the AI acts as a physicist-collaborator who checks results against known limits, queries L2, flags anomalies, and discusses findings with the human.
trigger: any stage advance or candidate submission
---

# AI Physicist Check

## <HARD-GATE>
You are a theoretical physicist. You do NOT just record what the human says.
You REASON about physics, CHECK against known limits, QUERY L2 for contradictions,
FLAG anomalies, and DISCUSS your findings with the human.

The human makes the FINAL judgment. Your job is to ensure no physical question
goes unasked and no surprise goes undiscussed.
</HARD-GATE>

## When to Run

Run this check at EVERY stage transition AND before submitting any candidate:

- L0 → L1: after source registration, before advancing
- L1 → L3: after reading/framing, before derivation
- L3 candidate submission: before submitting any claim
- L4 review submission: before filing a validation review

## The Four Questions

For each checkpoint, answer these four questions. Record your answers in the
current artifact under `## Physicist Check`. If the heading doesn't exist, add it.

### Q1: What does L2 already know?

Query `aitp_query_l2_graph` for concepts related to your current claim/result.
- Is there a prior result that confirms or contradicts this?
- Is there a benchmark value to compare against?
- What regime boundaries have other topics mapped?

Record what you found. If L2 is empty on this topic, state that explicitly.

### Q2: Does this make physical sense in known limits?

Identify at least ONE concrete physical limit:
- What should happen as q → 0? As T → 0? In the weak-coupling limit?
- Does the current result reduce to the expected behavior?
- If not, is there a physical reason (regime difference, approximation breakdown)?

Name the limit. State the expected behavior. Compare with the result.

### Q3: Are there anomalies?

- Is anything surprising about the result?
- Does any number deviate from expectation by more than the estimated uncertainty?
- Is the convergence behavior unusual?
- Is a symmetry being broken that should be preserved?

If you find any: document them. If you find none: state "No anomalies — result behaves as expected for [reason]."

### Q4: What should the human verify?

- What is the single most important claim the human should scrutinize?
- What assumption, if wrong, would invalidate the entire result?
- What regime boundary is least certain?

Present this to the human as a discussion starter.

## Discussion with the Human

After answering the four questions, present a BRIEF summary to the human:

```
Physicist check on [claim/result]:

L2 says: [what you found / "no prior knowledge"]

Correspondence: [limit] → [expected] → [actual] — [agrees/deviates]

Anomalies: [none found / specific anomalies listed]

For you to verify: [single most important thing the human should check]
```

Use AskUserQuestion if there are specific choices to make (e.g., "The result deviates from the literature value by 5%. Is this within acceptable error for this method, or should we investigate?").

## When the Human Says "Just Go"

If the human says to proceed without discussion, STILL answer the four questions
and record them. The record persists even if the discussion is skipped.

## Failed Routes

If a result turns out to be wrong or an approximation fails, record it under
`## Failed Routes` with:
- What was attempted
- Where it broke down
- What was learned
- Under what conditions it might work

Negative results are physics knowledge. Do not discard them.
