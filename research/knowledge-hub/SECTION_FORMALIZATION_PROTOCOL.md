# Section Formalization Protocol

This file defines the current AITP kernel contract for section-oriented
formal-theory automation.

## 1. Why this exists

Many theory sources do not become Lean-ready all at once.
Definitions, theorem bridges, and worked examples often stabilize at different
rates.

AITP should therefore not treat "the whole paper" as the only meaningful
formalization unit when the source already exposes stable local section
boundaries.

## 2. Canonical bounded unit

When an upstream source manifest exposes stable section ids, those section ids
are the default bounded progression units for formal-theory work.

Examples:

- one section can already have a compiled local Lean shadow,
- another section can remain at theorem-statement or topology-alignment level,
- and an example section can remain a stub plus explicit `open_gap`.

That unevenness is acceptable.
Collapsing it into one fake global "fully Leanized" status is not acceptable.

## 3. Required section surfaces

For an active section-oriented topic, AITP should keep enough durable artifacts
to answer:

- which source section is active,
- what local packet boundary is claimed,
- what local Lean shadow exists,
- what section-local open gaps remain,
- and what regression prompts guard against status drift.

These surfaces may live in topic-local artifacts or in the downstream typed
backend, but they must be durable and inspectable.

## 4. Status rule

A compiled section shadow does not imply:

- whole-topic proof closure,
- cited-source completeness,
- or readiness for automatic promotion of neighboring sections.

AITP should preserve distinctions such as:

- source-mapped
- statement-scaffolded
- locally-compiled
- bridge-open
- example-open

Exact labels may vary, but the distinctions must remain materialized.

## 5. Runtime expectation

When formal-theory or Lean-bridge work is active, runtime should keep this
protocol visible enough that an agent does not silently skip the section
boundary and jump straight to whole-topic claims.

Runtime and doctor surfaces should expose the protocol itself as a first-class
contract.

## 6. Queue and regression expectation

Section-oriented topics should route unresolved work and regression checks at
the section level when possible.

That means:

- theorem-bridge debt should remain distinct from example debt,
- abstract/concrete equivalence debt should remain distinct from local compiled
  definition sections,
- and section regressions should test for boundary honesty, not only for broad
  fluency.

## 7. Lean shadow rule

AITP may treat a section as usefully Lean-facing when it has:

- a truthful local module,
- current upstream name alignment,
- and an explicit statement of what is still missing.

AITP must not:

- hide missing bridge proofs behind a compiled file,
- treat a stub section as completed mathematics,
- or auto-promote a whole topic merely because one section compiles.

## 8. Jones exemplar

The Jones 2015 operator-algebra branch is the current exemplar for this
protocol:

- commutants
- operator topologies
- bicommutant theorem bridge
- concrete von Neumann algebra definition packet
- multiplication-operator example backlog

The purpose of this protocol is to let those sections advance unevenly while
remaining self-consistent and auditable.
