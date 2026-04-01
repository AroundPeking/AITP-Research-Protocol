# Requirements: v1.2 Projection-First Formal-Theory Seed

**Defined:** 2026-04-01
**Core Value:** AITP must turn vague but meaningful research starts into bounded, durable, and explainable runtime state without pretending uncertainty is already resolved.

## v1.2 Requirements

### Formal-Theory Applicability

- [ ] **FTS-01**: A bounded `formal_theory` topic can compile a `topic_skill_projection` only when a concrete run exposes ready theorem-facing trust artifacts plus at least one strategy-memory row.
- [ ] **FTS-02**: If the formal-theory trust gate, run id, or strategy memory is missing, the service returns `blocked` or `not_applicable` honestly and does not materialize a false projection candidate.
- [ ] **FTS-03**: Formal-theory projections preserve reusable execution guidance while staying explicitly separate from theorem truth claims, proof closure, or automatic mathematical promotion.

### Runtime Read Path

- [ ] **RTS-01**: Runtime status, dashboard, and `must_read_now` surfaces expose the formal-theory projection only when its status is `available`.
- [ ] **RTS-02**: Adapter/bootstrap auto-load behavior stays unchanged; the milestone only adds formal-theory projection visibility through existing runtime read paths.

### Jones Seed Exemplar

- [ ] **JNS-01**: The Jones Chapter 4 finite-product acceptance lane can generate a formal-theory `topic_skill_projection` under the new applicability rules.
- [ ] **JNS-02**: The Jones seed acceptance writes the projection candidate row and exercises the same human-reviewed promotion route into backend `units/topic-skill-projections/`.

### Docs And Trust Semantics

- [ ] **DOC-01**: Repo docs explain that a formal-theory `topic_skill_projection` is reusable execution memory, not a theorem certificate or proof-complete knowledge object.

## Future Requirements

- **AUTO-01**: After at least one non-`code_method` seed closes honestly, decide whether any projection family should become adapter/bootstrap auto-load eligible.
- **MULTI-01**: Generalize projection-first formal-theory support beyond one bounded exemplar only after the seed lane proves the trust semantics are stable.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Adapter/bootstrap auto-load of formal-theory projections | The projection must first prove itself as read-path-only execution memory |
| Broad multi-topic formal-theory rollout in one milestone | One bounded seed exemplar is the right trust-preserving step |
| Auto-promotion of formal-theory projections | v1 projection families remain human-reviewed only |
| Packaging-first product work | The current bottleneck is projection quality and trust semantics, not installer polish |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| FTS-01 | Phase 6 | Planned |
| FTS-02 | Phase 6 | Planned |
| FTS-03 | Phase 6 | Planned |
| RTS-01 | Phase 7 | Planned |
| RTS-02 | Phase 7 | Planned |
| JNS-01 | Phase 8 | Planned |
| JNS-02 | Phase 8 | Planned |
| DOC-01 | Phase 9 | Planned |

**Coverage:**
- v1.2 requirements: 8 total
- Mapped to phases: 8
- Unmapped: 0

---
*Requirements defined: 2026-04-01*
*Last updated: 2026-04-01 after selecting the projection-first formal-theory seed direction*
