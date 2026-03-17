# Promotion policy

This file defines the first-pass promotion rules into Layer 2.

## Core rule

Layer 2 stores settled reusable units, not coordination debt.
This now applies to both human-governed `L2` and theory-formal `L2_auto`.

Keep outside Layer 2:
- promotion queues,
- unresolved prerequisite backlogs,
- bridge backlogs,
- research blockers,
- run-local TODOs,
- active conjecture piles,
- scratch derivation fragments that still need adjudication.

Those belong in Layer 3.

## Allowed promotion routes

### Default human-reviewed route: `L3 -> L4 -> L2`

This is the normal path for anything that required:
- active research interpretation,
- derivation work,
- execution,
- contradiction checking,
- numerical or formal validation,
- or explicit adjudication.

Required conditions:
- a candidate object exists in Layer 3,
- the validation target is explicit,
- a Layer 4 record captures the checks performed,
- provenance is preserved back to the relevant source and run artifacts,
- the promoted unit is smaller and more reusable than the whole run summary.

### Human exception route: `L1 -> L2`

Allow direct promotion only when all of the following are true:
- the item is already reusable across runs,
- the abstraction level is appropriate for canonical storage,
- source anchoring is explicit,
- assumptions and regime are explicit,
- no additional Layer 3 exploration or Layer 4 execution is needed,
- the item is low-risk enough that direct promotion will not create canonical debt.

Typical candidates:
- a clean concept definition,
- a narrow source-anchored claim card,
- a small warning note about a documented limitation.

Do not treat `L1 -> L2` as the default.

### Theory-formal auto route: `L3 -> L4_auto -> L2_auto`

This route exists for theory-formal units that are precise enough to survive an
AI-reviewed gate before human curation.

Required conditions:
- the candidate belongs to a theory-formal family such as `definition_card`,
  `notation_card`, `equation_card`, `assumption_card`, `regime_card`,
  `theorem_card`, `proof_fragment`, `derivation_step`, `example_card`,
  `caveat_card`, `equivalence_map`, or `symbol_binding`,
- the backend explicitly allows auto canonical promotion for the target domain,
- a theory packet records the coverage audit inputs and outputs,
- coverage over assumptions, notation, regime, and local dependencies is explicit,
- multi-agent or equivalent independent consensus has been recorded when the backend requires it,
- merge-vs-create has been checked against the existing canonical target.

This is intended for high-granularity theory intake, not for report-shaped
summaries.

### Theory-formal direct route: `L1 -> L2_auto`

Allow direct `L1 -> L2_auto` only when all of the following are true:
- the source item is already sharply scoped and formally reusable,
- the object is low-risk enough that no intervening Layer 3 interpretation is required,
- the backend policy explicitly allows direct auto promotion for that domain,
- coverage and consensus gates still pass.

Typical candidates:
- a clean symbol binding with unambiguous scope,
- a source-anchored formal definition,
- a notation card with explicit binding context.

Do not treat `L1 -> L2_auto` as the default.

### Reconciliation route: `L2_auto -> L2`

Use this route when an `L2_auto` item has accumulated enough evidence or human
review to enter the human-governed canonical layer.

Required conditions:
- the auto-promoted unit has stable identity,
- any merge with an existing `L2` unit is explicit,
- the human review rationale records whether the object was accepted as-is or reshaped.

## Forbidden routes

Direct `L1 -> L4 -> L2` is not allowed.
Direct `L1 -> L4_auto -> L2_auto` is not allowed.
Direct `L3 -> L2_auto` without the documented auto gates is not allowed.

If Layer 4 is involved, Layer 3 must exist first as the explicit staging surface.

## Promotion gate

Before promoting any unit, ask:
- Is the object reusable beyond this source or run?
- Are the assumptions explicit?
- Is the regime of validity explicit?
- Is the notation or symbol binding explicit enough for later reuse?
- Is provenance structural rather than decorative?
- Is the object better represented as a typed unit than as a run summary?
- Has the needed `L3` or `L4` scrutiny actually happened?
- If this is entering `L2_auto`, did the coverage audit confirm the local
  dependency surface?
- If this is entering `L2_auto`, did consensus reach the backend-required threshold?
- If a same-identity canonical target already exists, should this merge instead
  of creating a new node?
- If this depends on a numerical method, has an appropriate public or analytic baseline been reproduced first?
- If this depends on a non-trivial theory method, has the method been decomposed into atomic concepts and dependency links first?
- Is this settled enough for the canonical layer, or is it still coordination debt?

If the answer to any of these is no, keep the item out of Layer 2.

## Decision outcomes

Use one of these outcomes at the end of a promotion review:
- `accepted`: promote to Layer 2 now
- `deferred`: keep in Layer 3 until more work exists
- `rejected`: do not canonicalize in the current form
- `needs_revision`: reshape the object, then review again

## Writeback rule

Do not write back one monolithic summary when the actual reusable output is multiple typed units.

Prefer decomposed promotion such as:
- one `concept`,
- one `definition_card`,
- one `notation_card`,
- one `assumption_card`,
- one `regime_card`,
- one `equation_card`,
- one `theorem_card`,
- one `proof_fragment`,
- one `derivation_step`,
- one `example_card`,
- one `caveat_card`,
- one `equivalence_map`,
- one `symbol_binding`,
- one `claim_card`,
- one `derivation_object`,
- one `validation_pattern`,
- one `warning_note`.

This is how Layer 2 compounds without turning into a report graveyard.
