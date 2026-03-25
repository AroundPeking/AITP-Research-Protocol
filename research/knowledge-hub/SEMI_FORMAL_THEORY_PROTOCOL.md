# Semi-Formal Theory Protocol

This file defines the current AITP target state for theory-heavy work.

The primary near-term goal is not full Lean closure.
The primary goal is a source-grounded, gap-honest, semi-formal theory layer
that is clear enough for controlled derivation, regression, promotion, and
later translation into Lean or another formal backend.

## 1. Position

For formal-theory topics, AITP should treat the semi-formal layer as the main
working backend.

That means:

- operator-readable notes and typed units are first-class artifacts,
- definitions, assumptions, regime limits, equations, and derivation steps stay
  explicit,
- unresolved gaps stay visible rather than being compressed into fluent prose,
- and Lean export is a downstream bridge, not the definition of success for
  every topic.

## 2. What counts as semi-formal

A semi-formal theory artifact is stronger than an informal note and weaker than
a theorem-prover-checked proof.

It should make explicit at least:

- the bounded object or statement,
- the assumptions and regime,
- the key equations or local symbolic steps,
- the source anchors,
- the local derivation spine or proof obligations,
- the current trust boundary,
- and the remaining open gaps or cited-source recovery debt.

If those surfaces are missing, the artifact is still informal.

## 3. Why AITP uses this as the default

Physics usually needs a semantic compression step before proof assistant export:

- a topic must be cut into bounded theorem or definition families,
- physical intuition must be separated from theorem-grade statements,
- conventions and regimes must be fixed,
- and cross-source equivalence must be made explicit instead of assumed.

AITP therefore should not pretend that every useful theory artifact must
already be Lean-ready before it can become durable `L2` knowledge.

## 4. Required trust-boundary rule

Every promoted semi-formal family should say what it does and does not close.

Examples:

- local Witten-side derivation is explicit,
- primary cited-source fragments exist locally,
- broader cross-source fusion remains open,
- statement is suitable for future Lean export,
- or statement is not yet clean enough for export.

This boundary must be recorded in durable artifacts rather than left in chat.

## 5. Promotion rule

Promotion into `L2` is allowed for semi-formal theory artifacts when they are:

- source-grounded,
- scoped and assumption-explicit,
- gap-honest,
- regression-backed when applicable,
- and clear about downstream formalization status.

Promotion into `L2` does not imply:

- full proof closure,
- full cited-source reconstruction,
- or completed Lean formalization.

## 6. Downstream formalization rule

Lean export is a downstream action on top of the semi-formal layer.

Use Lean-facing export only after the local semi-formal packet is already
stable enough that:

- the theorem or definition boundary is clear,
- the source-faithfulness story is explicit,
- major prerequisite debt is known,
- and the trust boundary is acceptable to preserve during export.

If the semi-formal packet is still mixed, wide, or source-ambiguous, split or
refine it before building a Lean bridge.

## 7. Required fields for semi-formal family leaders

For flagship theorem, proof-state, source-fusion, or source-map artifacts, keep
these explicit where relevant:

- `trust_boundary`
- `semi_formal_contract`
- `translation_readiness`

Exact storage shape may vary by backend, but those three ideas must remain
materialized.

## 8. Runtime expectation

Runtime should keep this protocol visible whenever theory-formal work is
active.

Runtime may prepare Lean bridges.
Runtime must not silently collapse the semi-formal layer into a fake
"already formalized" status just because a bounded export packet exists.

## 9. Witten exemplar rule

The Witten topological-phases exemplar is a canonical test of this protocol.

It should remain usable as a semi-formal package even while:

- TKNN, Haldane, Jackiw-Rebbi, Callan-Harvey, and Friedan source recovery
  continue,
- conflict records preserve anomaly-versus-lattice distinctions,
- and only selected slices are ready for later Lean translation.
