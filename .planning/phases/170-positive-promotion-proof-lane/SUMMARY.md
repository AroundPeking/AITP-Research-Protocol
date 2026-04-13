# Phase 170 Summary: Three-Mode Positive Promotion Proof Lane

**Status:** Bootstrap complete for all three lanes. Promotion execution pending.
**Date:** 2026-04-14

## What was done

1. **Codex branch merged** — 6 commits from `codex/phase-169-l2-canonical-schema-extension` merged into main (Phase 169/169.1/169.2 completion + v1.95 archive + v1.96 start)

2. **Phase 170 PLAN.md rewritten** — expanded from single Jones/von Neumann positive proof to three research-mode proof lanes per user request

3. **Three fresh topics bootstrapped through the public front door:**

| Lane | Topic Slug | Research Mode | Conformance | Resume Stage |
|------|-----------|---------------|-------------|-------------|
| A | `von-neumann-algebra-factor-type-classification-proof` | `formal_derivation` | ✅ 27/27 pass | L3 |
| B | `haldane-shastry-model-quantum-chaos-and-lyapunov-spectrum` | `toy_model` | ✅ all pass | L3 |
| C | `librpa-qsgw-convergence-verification-for-h2o-tight-basis` | `first_principles` | ✅ all pass | L3 |

## Evidence

- All three topics entered through the public AITP front door via `AITPService().new_topic()`
- No hidden seed state was used
- All three conformance audits passed
- Runtime topic shells materialized in `research/knowledge-hub/runtime/topics/`
- Runbooks written: RUNBOOK-A.md, RUNBOOK-B.md, RUNBOOK-C.md

## What remains for each lane

Each lane is now at L3 (candidate_shaping) with next action = L0 source expansion:

- **Lane A:** Register Jones (1983) sources → derive Type I classification → promote
- **Lane B:** Register HS model sources → compute chaos indicators → promote (may surface toy_model acceptance gaps)
- **Lane C:** Register LibRPA/QSGW sources → verify convergence → promote (tests first_principles→code_method mapping)

## Key findings

1. **Public front door works for all three research modes** — `new_topic()` correctly routes `formal_theory` → `formal_derivation`, `toy_model` → `toy_model`, `first_principles` → `first_principles`
2. **Conformance audit surface is mode-agnostic** — same 27 checks pass for all modes
3. **No mode-specific bootstrap failures** — all three lanes bootstrapped cleanly
4. **Promotion pipeline execution** requires further bounded loop steps (L0→L1→L3→L4→L2) which need source registration and analysis work

## Deferred

- Actual promotion execution (L4→L2) for each lane — requires running the bounded loop through source registration, analysis, and validation
- Cross-lane surface parity check (Step 4) — blocked on promotion completion
- Negative-result proof (Phase 170.1) — depends on Phase 170
