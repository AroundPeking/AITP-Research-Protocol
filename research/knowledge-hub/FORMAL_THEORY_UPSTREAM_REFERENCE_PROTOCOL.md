# Formal Theory Upstream Reference Protocol

This file defines the public AITP contract for long-lived upstream references
used by formal-theory and Lean-facing work.

These upstreams are not frozen canonical truth.
They are the living discussion and code surfaces that AITP should keep in view
when deciding what to formalize, how to package it, and whether nearby work
already exists upstream.

## 1. Why this exists

Formal-theory work drifts when it only reads local notes:

- existing upstream formalizations are duplicated unknowingly,
- statement granularity is chosen without current community practice,
- naming and namespace choices drift away from nearby Lean conventions,
- or a live community discussion is treated as theorem truth without durable provenance.

This protocol makes those upstream reference surfaces explicit.

## 2. Required living upstreams

For Lean-facing AITP work, keep these two upstream surfaces in the long-term
reference set:

1. Lean Zulip Autoformalization discussion surface
   - primary narrow URL:
     - `https://leanprover.zulipchat.com/#narrow/channel/583336-Autoformalization`
   - public archive fallback for related autoformalization discussion:
     - `https://leanprover-community.github.io/archive/stream/219941-Machine-Learning-for-Theorem-Proving/topic/autoformalization.3F.html`
2. `physlib` upstream code surface
   - `https://github.com/leanprover-community/physlib`

Projects may add more upstreams later, but these two should remain visible
unless a future protocol explicitly supersedes them.

## 3. Role separation

Treat the two upstreams differently:

- Lean Zulip Autoformalization:
  - living discussion surface
  - useful for workflow ideas, current obstacles, tactic patterns, scoping
    choices, and community practice
  - not a substitute for a theorem statement, proof artifact, or cited source
- `physlib`:
  - durable code and artifact surface
  - useful for existing declarations, file layout, naming patterns,
    prerequisite packaging, and reusable nearby formalization fragments
  - still requires explicit provenance because the upstream may move

## 4. When consultation is mandatory

For formal-theory topics, consult these upstreams at least when:

- bootstrapping or resuming a Lean-facing topic,
- choosing the bounded theorem/definition family for a Lean bridge,
- deciding namespace, file layout, or declaration granularity,
- checking whether nearby formalizations already exist upstream,
- evaluating whether a local proof scaffold matches current Lean-community
  practice,
- or before claiming novelty for a formalization plan.

For purely numerical or code-method topics, this protocol may remain inactive.

## 5. Provenance rule

When these upstreams influence work, persist the consultation result
explicitly.

For Lean Zulip discussion, record:

- the exact thread or narrow URL when available,
- access date,
- one bounded takeaway,
- and any unresolved caveat about discussion status or missing code.

For `physlib`, record:

- repository URL,
- commit SHA or branch snapshot consulted,
- file paths or declaration names reviewed,
- and the bounded relevance to the current AITP topic.

Those records should enter normal AITP artifacts such as `L0` source notes,
runtime follow-up notes, Lean-bridge notes, or proof-obligation writeback.

## 6. Non-equivalence rule

Live discussion does not equal proof.
Existing upstream code does not automatically equal local reuse approval.

AITP must not:

- treat a Zulip discussion as theorem truth,
- infer that upstream existence removes the need for local bounded claims,
- or skip local proof-obligation, gap, or verification surfaces because a
  nearby upstream artifact exists.

These upstreams inform the route.
They do not replace the route.

## 7. Access limitation rule

The Lean Zulip narrow URL is a dynamic community surface and may be partially
visible depending on archive/public-access state.

If the exact narrow thread cannot be read in the current environment:

- record that access limitation explicitly,
- consult the public archive fallback or other public upstream traces when
  available,
- and do not silently pretend that the missing discussion was reviewed.

## 8. Runtime expectation

When formal-theory or Lean-bridge work is active, runtime and operator-facing
surfaces should keep this protocol visible enough that an agent does not forget
to check living upstream practice before exporting or promoting a bounded
formal claim family.

## 9. Script boundary

Scripts may:

- point to the required upstream surfaces,
- scaffold consultation reminders,
- and record machine-readable provenance fields.

Scripts may not:

- claim that an upstream discussion settled a theorem,
- convert community discussion into canonical `L2` truth without normal AITP
  gates,
- or hide which upstream commit/thread was actually consulted.
