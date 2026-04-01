# Milestones

## v1.1 L2 Topic-Skill Projection (Shipped: 2026-04-01)

**Scope capture:** retrospective milestone note from shipped implementation in commit `6445c59`

**Key accomplishments:**

- `topic_skill_projection` now exists as a legal canonical unit family, backend target, and candidate type
- `AITPService` can compile topic-skill projections from runtime topic state, strategy memory, operation manifests, trust audit, and topic completion surfaces
- runtime topics now materialize `topic_skill_projection.active.json|md` and expose the projection through `topic_status()`, `topic_next()`, dashboard, and runtime protocol read paths
- TFIM is now a real seed exemplar that generates the projection, creates the candidate ledger row, and exercises human-reviewed promotion into `units/topic-skill-projections/`
- auto-promotion is explicitly blocked for this family in v1 while the projection remains human-reviewed execution memory

---

## v1.0 Runtime Hardening (Shipped: 2026-03-31)

**Phases completed:** 5 phases, 7 plans, 10 tasks

**Key accomplishments:**

- Source-backed topic starts now derive sharper idea-packet, research-question, and validation-route defaults from registered source material
- Runtime status surfaces now explain why a topic is here, what route it is following, what evidence returned last, and what human need remains
- Topic-start hardening is now covered by deterministic regressions and a clean runtime test suite
- Steering-style operator checkpoint answers now materialize durable steering artifacts and refreshed runtime routes
- Run-local strategy memory can now be written, surfaced through runtime status, and consulted as bounded route guidance
- The TFIM exact-diagonalization helper now has a real benchmark-first `code_method` acceptance lane inside AITP
- The repository now has an explicit rule for when work belongs to GSD repo execution versus AITP topic execution

---
