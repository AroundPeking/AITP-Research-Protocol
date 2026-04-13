# Phase 171.2 Summary: Positive Replay And Deferred Mode Routing

**Status:** Done
**Date:** 2026-04-14
**Axis:** Axis 4 (human evidence) + Axis 5 (agent-facing roadmap clarity)

## What was done

Phase 171.2 closed milestone `v1.97` at the phase level.

### Replay closure

- replayed the fresh positive-L2 proof mechanically
- replayed the positive/negative coexistence proof mechanically
- wrote one milestone-level replay runbook (`RUNBOOK-P.md`)

### Deferred-mode routing

- wrote explicit blocker and next-action notes for the user-requested
  `HS model` toy-model lane
- wrote explicit blocker and next-action notes for the user-requested
  `LibRPA QSGW` first-principles / code-method lane

## Acceptance criteria

- [x] One runbook explains how to replay the positive-L2 proof end to end
- [x] Raw replay receipts are stored under this phase
- [x] `REQ-L2POS-04` is satisfied by explicit replay evidence
- [x] Toy-model blockers and next actions are written explicitly
- [x] First-principles blockers and next actions are written explicitly
- [x] `REQ-L2POS-05` is satisfied by durable routing notes rather than chat memory

## Evidence

| Artifact | Location | Purpose |
|----------|----------|---------|
| `replay-formal-positive-l2.json` | `phases/171.2-positive-replay-and-deferred-mode-routing/evidence/` | Raw replay of the fresh positive authoritative-L2 landing |
| `replay-positive-negative-coexistence.json` | `phases/171.2-positive-replay-and-deferred-mode-routing/evidence/` | Raw replay of positive/negative coexistence on compiled + consult surfaces |
| `pytest-positive-mirror.txt` | `phases/171.2-positive-replay-and-deferred-mode-routing/evidence/` | Targeted canonical-mirror regression receipt |
| `pytest-coexistence-unit.txt` | `phases/171.2-positive-replay-and-deferred-mode-routing/evidence/` | Targeted coexistence regression receipt |
| `deferred-lane-routing.md` | `phases/171.2-positive-replay-and-deferred-mode-routing/evidence/` | Explicit blockers and next actions for `HS model` and `LibRPA QSGW` |

## Outcome

With Phase `171.2`, all three phases of milestone `v1.97` are complete:

- Phase `171`: fresh formal positive lane to authoritative `L2` ✅
- Phase `171.1`: positive/negative L2 coexistence hardening ✅
- Phase `171.2`: replay closure and deferred-mode routing ✅

The milestone is now ready for lifecycle handling: audit, complete, and
cleanup.
