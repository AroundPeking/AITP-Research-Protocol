---
name: skill-librpa
description: Domain skill for ABACUS+LibRPA topics. Injects workflow lanes, domain invariants, and concrete validation criteria. Protocol-level concerns (derive-first, externalized spec, execution environment, error classification) are handled by existing AITP skills — this file adds only LibRPA-specific knowledge.
trigger: domain == "abacus-librpa"
---

# ABACUS + LibRPA Domain Skill

Loaded when the topic's domain is `abacus-librpa`, detected via:
1. `contracts/domain-manifest.abacus-librpa.json` in the topic directory
2. `domains: [abacus-librpa]` in `state.md` frontmatter
3. Legacy slug-pattern fallback (slug contains "librpa", "crpa", etc.)

**This skill is additive.** AITP's protocol skills already handle:
- Derive-first discipline → `skill-l3-analyze.md` + Feature Development Playbook Gate G0
- Externalized spec → `EXTERNALIZED_SPEC_PROTOCOL.md`
- Execution environment → `skill-l3-plan.md` (MANDATORY for code_method lanes)
- Operation routing → domain manifest `operations` + `routing.intent_patterns`
- Error classification → domain manifest `skill_hooks.on_error_classify`
- Invariant checking at L4 → Feature Development Playbook Phase 4
- Devil's advocate → `skill-validate.md`

This file provides only what those generic mechanisms don't cover.

## Workflow Lanes

```
Molecule GW:      SCF -> LibRPA
Periodic GW:      SCF -> pyatb -> NSCF -> preprocess -> LibRPA
Periodic GW sym:  SCF(symmetry=1,rpa=1,no SOC) -> copy sidecars -> pyatb -> NSCF(symmetry=-1) -> preprocess -> LibRPA(symmetry flags)
RPA:              SCF -> LibRPA
```

## Domain Invariants

| Invariant | Check method |
|-----------|-------------|
| `shrink_consistency` | ABFS_ORBITAL files match `use_shrink_abfs` in `librpa.in` |
| `same_libri` | ABACUS and LibRPA compiled against same LibRI version |
| `keyword_compat` | No deprecated ABACUS keywords in INPUT |
| `smoke_first` | Minimal test passed before full calculation |
| `toolchain_consistency` | Build and runtime environments match |

When running L4 validation for a `code_method` lane topic, verify all 5 before submitting `outcome="pass"`.

## Target Codes

`abacus`, `librpa`, `libri`, `libcomm`, `pyatb`

## Smoke Test Criteria

Bulk Si 2×2×2, low ecutwfc. Must pass all stages:
SCF → DF → NSCF → LibRPA, with no NaN and `gw_band.dat` existing.

## Escape Hatches

- Domain manifest missing from project: clone from GitHub, copy into `contracts/`, register via `aitp_register_source`.
- `formal_theory` lane: L3/L4 computational requirements are advisory, not blocking.
- User says "skip domain checks": record the skip, mark validation as `partial_pass` (not `pass`).

## References

- oh-my-LibRPA: https://github.com/AroundPeking/oh-my-LibRPA
- Domain manifest: `registry/domain-manifest.abacus-librpa.json`
