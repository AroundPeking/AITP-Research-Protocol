# AITP L3 Decision Points: Human-in-the-Loop at Forks

**Date**: 2026-04-29
**Status**: spec
**Scope**: brain/mcp_server.py + skills/skill-l3-*.md

## Problem

AITP v4.0 consults the human only at stage transitions (L0→L1, L1→L3, L4→L2).
Within L3 (the core derivation workspace), the LLM makes all decisions autonomously
— choice of approximation, judgment of result validity, next direction. The human's
NL steering instructions during a session are not persisted as structured state and
are lost on context compaction or session restart.

## Goal

Let the LLM act as the human's collaborator who does heavy lifting (derivations,
numerical tests) but actively asks the human at key decision forks. The human
remains the decision-maker; the LLM remains the executor.

## Non-goals

- Human typing their own derivations into files (NL conversation suffices)
- Full steering history loaded on session resume (causes context bloat)
- Changes to L0, L1, L4, or L2 stages
- Changes to session_resume mechanism
- New directory structure under topics/

## Design

### One new MCP tool: `aitp_record_decision`

```
aitp_record_decision(
    topics_root: str,
    topic_slug: str,
    decision_id: str,       # slug, e.g. "choose-plasmon-pole-vs-ff"
    question: str,           # what the LLM asked the human
    human_answer: str,       # the human's answer (free text or selected option)
    rationale: str = "",     # why the human chose this
    context: str = "",       # what activity/derivation step this relates to
)
```

Writes an append-only entry to `runtime/decisions.md` with YAML frontmatter:
```yaml
decision_id, question, human_answer, rationale,
context, recorded_at, status (active/superseded/revisited)
```

Returns a brief confirmation. Does NOT block execution — it records,
not gates. Gate behavior remains at stage transitions only.

### Updated L3 skill files

Each L3 skill file gets a new section "## Decision Forks" listing the
scenarios where the LLM MUST call `AskUserQuestion` before proceeding:

**skill-l3-ideate.md** — when proposing research directions:
- "I have N possible approaches. Which should I pursue first?"

**skill-l3-analyze.md** (derive + trace-derivation) — during derivation:
- "I need to pick an approximation. Options: A (simpler, less accurate),
  B (more expensive, more accurate). Which?"
- "This result looks unexpected. [explain]. Proceed or investigate?"
- "The derivation suggests two possible next steps: X or Y. Which?"

**skill-l3-gap-audit.md** — when finding gaps:
- "I found a potential gap: [describe]. Is this a real concern worth
  addressing now, or should we defer?"

**skill-l3-integrate.md** — when synthesizing results:
- "The synthesis suggests [conclusion]. Does this match your physical
  intuition? Any missing pieces?"

**skill-l3-distill.md** — before submitting a candidate:
- "I'm ready to submit this claim for L4 validation. Summary: [claim].
  Any concerns before I proceed?"

The LLM must:
1. Present the decision clearly with options or open-ended ask
2. Record the decision via `aitp_record_decision` after human answers
3. Proceed according to the human's answer

The LLM must NOT:
- Skip asking and guess the human's preference
- Ask about trivial implementation details (only conceptual forks)

### No changes to

- `brain/state_model.py` — no new gate logic
- `brain/sympy_verify.py` — unchanged
- `hooks/` — unchanged
- `skills/skill-discover.md`, `skill-read.md`, `skill-frame.md`,
  `skill-validate.md`, `skill-promote.md` — already have human gates
- Session resume — existing mechanism is sufficient; human decisions
  are in `runtime/decisions.md` and can be read on demand

## Files changed

| File | Change | Lines |
|------|--------|-------|
| `brain/mcp_server.py` | Add `aitp_record_decision` tool | ~40 |
| `skills/skill-l3-ideate.md` | Add Decision Forks section | ~10 |
| `skills/skill-l3-analyze.md` | Add Decision Forks section | ~15 |
| `skills/skill-l3-gap-audit.md` | Add Decision Forks section | ~10 |
| `skills/skill-l3-integrate.md` | Add Decision Forks section | ~10 |
| `skills/skill-l3-distill.md` | Add Decision Forks section | ~10 |
| Total | | ~95 |

## Verification

1. `aitp_record_decision` writes to `runtime/decisions.md` with correct frontmatter
2. Existing tests pass (no breaking changes to state model or existing tools)
3. Manual test: bootstrap a topic, advance to L3, verify skill files instruct LLM to ask at decision forks
