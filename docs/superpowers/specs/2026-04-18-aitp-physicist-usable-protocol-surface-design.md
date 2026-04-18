# AITP Physicist-Usable Protocol Surface Design

## Review notes (2026-04-18)

This document was reviewed against the repository state at commit
`63d195b7`. Key corrections applied:

1. **File path inventory**: The original spec referenced 10+ files that do
   not exist in the repository. All workstream "Primary files" sections have
   been rewritten to reflect actual paths, with new-file vs modify
   annotations.
2. **Lane mapping**: Added a "Lane taxonomy and runtime mapping" section
   defining how the proposed three-lane taxonomy maps to the existing
   `template_mode` + `research_mode` fields.
3. **Acceptance criteria**: Replaced subjective criteria with mechanically
   testable assertions.
4. **`inspect_resume_state` root cause**: W2 now distinguishes structural
   (queue-empty) from presentational (wrong-summary) fallback and prescribes
   different fixes for each.
5. **Workstream categorisation**: W1–W2 are marked "code change"; W3–W5
   are marked "content lift" with tighter scope; W6 is recast as a
   cross-cutting integration gate.
6. **Design Decision 2 scope**: Clarified that lane-specific contract
   enrichment is a construction-time constraint, not a schema migration.

## Goal

Make the public AITP reference implementation feel like a disciplined
theoretical-physics research workspace rather than a runtime-control shell.

This design targets one bounded but intentionally broad upgrade wave:

1. preserve real physics intent inside the active topic contracts,
2. make human-facing next actions read like research work instead of runtime
   self-maintenance,
3. add a minimal but honest increase in `L0`, `L4`, and `L2` public substance.

The result should keep the current protocol discipline intact while improving
the experience of a physicist who says "continue this topic" and expects to
resume the science rather than inspect the machinery.

## Problem

The repository already does many protocol-first things correctly:

- evidence, artifact, and promotion discipline are explicit,
- runtime state is durable,
- human gates remain visible,
- the public kernel survives real-topic acceptance probes,
- and topic shells are materially generated rather than implied by chat memory.

But the current public implementation still has three user-facing failures.

### 1. Contract truth is weaker than runtime awareness

The runtime frequently knows a concrete physics question from the natural
language request, but the active `research_question.contract` can still collapse
into generic text such as "Clarify, validate, and persist..." or runtime-facing
placeholders such as action ids.

Evidence from the current repository:

- The `observables` field is identical across all inspected topics (formal
  theory, code method, exploratory): "Declared candidate ids, bounded claims,
  and validation outcomes." — zero physics content.
- The `target_claims` field contains only action ids like
  `action:{topic-slug}:01` rather than bounded scientific claims.
- The `deliverables` field is template boilerplate identical across all lanes.

This is the highest-priority failure because the active contract should be the
main bounded statement of the scientific problem. If it only preserves protocol
shape and not the actual physical question, AITP remains protocol-correct but
research-semantically thin.

### 2. Human-facing next steps can degrade into shell maintenance

When the queue is underspecified or a control note does not match a pending
action, the runtime can present `inspect_resume_state` or "persist the redirect
into next_actions.md" as the effective next step.

Evidence from the current repository:

- The `scrpa-variational-closure` topic's `next_action_decision.md` shows
  action type `inspect_resume_state` with summary "No explicit pending actions
  were found; inspect the runtime resume state."
- The `agent_brief.md` surfaces internal status flags like
  `decision_override_present status=inactive` as if they were research actions.

This is acceptable as an internal runtime fallback.
It is not acceptable as the main human-facing research action.

### 3. Public content density lags behind protocol density

`L0` is still heavily arXiv-shaped, `L4` still exposes only one tiny public
numerical starter (the TFIM exact-diagonalization script), and public `L2`
seeds are still sparse compared with the richness of the compiled/runtime
surfaces around them.

This creates a bad asymmetry:

- the system is very good at describing bounded research,
- but still relatively thin at helping the public user immediately perform that
  research in realistic theoretical-physics lanes.

## Scope

This design covers six coordinated workstreams, divided into two categories:

**Code-change workstreams** (mechanical, testable):
1. lane-aware research-contract semantics (W1),
2. research-facing next-action synthesis (W2).

**Content-lift workstreams** (editorial, lane-specific):
3. `L0` source-intake expansion (W3),
4. `L4` validation starter packs (W4),
5. `L2` seed enrichment (W5).

Cross-cutting:
6. acceptance and regression coverage for the above (W6, integration gate).

This is intentionally larger than a narrow bugfix, but it is still bounded.
The goal is not to redesign all of AITP at once.
The goal is to correct the public research-facing experience at the points
where protocol shape currently outruns scientific usability.

## Non-goals

This wave does **not** attempt to:

- replace the current runtime architecture wholesale,
- remove every compatibility surface,
- complete full legacy-path cleanup,
- ship a heavy public numerical backend,
- solve deep-execution parity across every runtime,
- or turn public `L2` into a mature multi-domain physics encyclopedia,
- modify the JSON schema for `research_question.contract.json` (enrichment is
  construction-time only),
- add new `research_mode` enum values (lane awareness is derived from existing
  fields).

Those remain valid later directions, but they are not required to make the
current public kernel much more usable to a working theorist.

## Approaches considered

### Approach A: protocol semantics first, then minimal content lift

Start by fixing what the user sees and what the contract means:

- make `research_question.contract` lane-aware and physics-specific,
- remove runtime-maintenance language from the human-facing next-action path,
- then add the smallest honest `L0`/`L4`/`L2` improvements that support those
  stronger surfaces.

Pros:

- fastest user-visible improvement,
- directly addresses the biggest current pain,
- preserves current architecture while improving meaning,
- keeps implementation bounded.

Cons:

- still touches several central files,
- some internal architectural debt remains for a later phase.

### Approach B: infrastructure refactor first

Extract new builder/synthesizer helpers first, then migrate contract and
dashboard behavior after the internals are cleaner.

Pros:

- cleaner architecture,
- easier long-term maintenance.

Cons:

- delays research-facing improvement,
- first round looks like refactoring rather than product progress.

### Approach C: content-first expansion

Expand sources, validators, and seed memory first, while leaving the current
contract and next-action behavior mostly intact.

Pros:

- increases physics substance quickly.

Cons:

- the main human-facing experience remains runtime-shaped,
- new content still gets filtered through weaker contract semantics.

## Chosen approach

Choose **Approach A**.

The current bottleneck is not merely lack of content.
It is that the public system does not always make the active contract and next
step read like the actual physics work that is underway.

Therefore this wave should first make the protocol surfaces semantically worthy
of the science, then lift public `L0`/`L4`/`L2` just enough to support that
stronger interface honestly.

## Lane taxonomy and runtime mapping

The spec uses a three-lane taxonomy:

| Lane                | `template_mode`        | `research_mode`            |
|---------------------|------------------------|----------------------------|
| `formal_derivation` | `formal_theory`        | `formal_derivation`        |
| `toy_model`         | `code_method`          | `exploratory_general` (*)  |
| `first_principles`  | `code_method`          | `exploratory_general` (*)  |

(*) The `toy_model` and `first_principles` lanes currently share the same
`research_mode` value (`exploratory_general`). Lane differentiation within this
mode is done by inspecting topic content (source types, observable targets,
model families) rather than by a distinct enum value.

This mapping means:
- lane-aware defaults must be derived at construction time from a combination
  of `template_mode`, `research_mode`, and topic content, not from a single
  field,
- no new `research_mode` enum values are introduced in this wave,
- if a topic cannot be confidently assigned to one lane, the generic fallback
  applies.

## Design decisions

### 1. The active research contract must preserve topic-specific physics intent

`research_question.contract` should remain the main bounded statement of the
scientific problem for ordinary topic work.

That implies three changes.

First, the contract builder must prefer the strongest available research-facing
question source in this order:

1. an already human-curated question in the existing contract,
2. a real natural-language topic statement or persisted steering request,
3. source distillation from `L0`/`L1`,
4. only then a generic fallback sentence.

Second, the contract must stop using runtime-only placeholders for high-rigor
fields when a stronger topic-specific statement is available.
In particular:

- `observables` should describe actual quantities, signals, or review targets,
  not "Declared candidate ids, bounded claims, and validation outcomes,"
- `target_claims` should summarize bounded scientific claims rather than only
  action ids like `action:{topic-slug}:01`,
- `deliverables` should mention concrete research outputs for the lane,
  not "Persist the active research question, validation route, and bounded
  next action as durable runtime artifacts,"
- `context_intake` should preserve the real language that shaped the route.

Third, lane-specific defaults should be introduced so that the contract reads
like the lane it belongs to.

### 2. High-rigor contract fields become lane-aware obligations at construction time

The current schema requires only the minimal cross-lane fields.
That is appropriate for base compatibility, but too weak for a public system
that aims to preserve actual research meaning.

This design keeps the root schema unchanged.
Lane-aware enrichment is applied at contract **construction time** inside the
runtime builder, not at the schema level.

For `formal_derivation`, the active contract builder should populate:

- bounded theorem or closure target,
- source theorem dependencies,
- notation/definition lock,
- proof or closure obligations,
- non-claims about broader formalization.

For `toy_model`, the active contract builder should populate:

- model family,
- observable family,
- finite-size or parameter regime,
- benchmark/comparator route,
- negative-comparator or non-transfer clauses.

For `first_principles` / code-method style lanes, the active contract builder
should populate:

- code/method family,
- bounded workflow or validator basis,
- observable or convergence target,
- benchmark-first route,
- explicit non-claims about whole-stack maturity.

The central design rule is:

- generic protocol prose is acceptable as supporting guardrails,
- but the lane-specific fields must carry concrete scientific content whenever
  the topic already contains that content.

### 3. Human-facing next actions must always be research-shaped

`inspect_resume_state` and similar actions remain useful as internal runtime
fallbacks, but they should no longer be the main human-facing action whenever a
research-shaped synthesis can be produced.

This design introduces a distinction between:

- **runtime fallback action types** for internal queue safety,
- **research-facing action summaries** for operator-facing surfaces.

The `inspect_resume_state` fallback has two distinct root causes that require
different fixes:

**Root cause A — structural (queue is empty):** The topic was never bootstrapped
or its action queue was consumed without producing new actions.
Fix: the next-action synthesizer should detect this case and propose a
structural bootstrap action phrased in research terms, such as
"Register the source basis for [topic question]" or "Bootstrap the topic
workflow for [topic question]."

**Root cause B — presentational (queue has entries but summary is generic):**
The queue contains research-meaningful actions but the summary string was
generated from generic templates.
Fix: the next-action synthesizer should rephrase using lane-specific evidence
from the contract and source index.

In both cases, the synthesis must:

- draw only from existing durable evidence,
- prefer "recover X" over "conclude Y" phrasing,
- keep evidence refs on the decision surface.

Example:

- bad current phrasing: "Inspect the runtime resume state."
- desired phrasing (root cause A): "Register the source basis for the bounded
  OTOC shoulder question before continuing interpretation."
- desired phrasing (root cause B): "Recover the missing literature basis for
  the bounded OTOC shoulder question before continuing interpretation."

The runtime may still keep the underlying action type as a fallback-compatible
value if needed, but the dashboard, operator console, and next-action note must
show a research-facing summary first.

### 4. Dashboard and operator console must converge on the same main story

The public documentation already says `topic_dashboard.md` is the main human
runtime surface and `operator_console.md` is a compatibility surface.

This wave should make them converge further around one rule:

- both surfaces must tell the same bounded scientific story,
- neither surface should force the user to reason about queue internals before
  they understand the scientific next step.

That means:

- keep detailed queue/debug information in supporting sections,
- keep the top sections focused on current question, bounded action, blockers,
  and what scientific artifact is missing next.

### 5. `L0` should recognize more real theory-research source shapes

The public `L0` layer should remain thin and auditable.
It should not become an opaque web-research engine.

But it does need a wider first-class source taxonomy.

This wave extends the public source surface toward four source families:

1. paper/preprint,
2. book chapter or lecture note,
3. code repository / implementation reference,
4. local derivation note or technical note.

The immediate goal is not full acquisition automation for each family.
The goal is:

- better source typing,
- better distillation defaults,
- and better route suggestions when the source basis is incomplete.

This is enough to make `L0` look more like real theoretical-physics work and
less like an arXiv-only stub.

### 6. `L4` should expose validator families, not only one example script

The current TFIM exact-diagonalization starter is useful but too narrow to
stand alone as the public face of `L4`.

This design adds the concept of **starter validation packs**:

- `toy_numeric` starter pack,
- `code_method` starter pack,
- `formal_theory` starter pack.

In this first wave, these packs can still be lightweight and partly
template-driven.
What matters is that the public kernel now communicates that validation is a
family of bounded workflows rather than one lone tool.

The code change can remain modest:

- create `validation/tools/README.md` describing the pack taxonomy,
- add minimal helper/config templates under `validation/templates/`,
- surface these packs in runtime-facing guidance and contracts.

### 7. `L2` should grow a small number of high-signal public seeds

This wave should not attempt a large public `L2` corpus.
Instead it should add a small number of carefully chosen seed units that line up
with the improved lane semantics.

Target shape:

- at least one bounded formal-theory seed unit that compiles through
  `cli_l2_compiler_handler.py` without errors,
- at least one bounded toy-model seed unit that compiles through the same path,
- at least one bounded code-method seed unit that compiles through the same
  path.

Each seed must include:

- topic question shape,
- source basis,
- validation logic,
- promoted reusable outcome,
- and non-claims.

The criterion is not raw count. It is whether each seed passes the existing
L2 acceptance test suite (`test_l2_backend_contracts.py`,
`test_l2_hygiene.py`).

### 8. Real-topic acceptance must become the primary safeguard

The repository already has acceptance coverage for real natural-language topic
dialogue.
This wave extends that philosophy.

The most important new acceptance guarantees are:

1. real topic text remains visible in the active research contract,
2. lane-specific contract fields contain lane-specific scientific content,
3. dashboard/operator-console next steps are research-shaped,
4. `inspect_resume_state` no longer appears as the first human-facing action in
   cases where the runtime can synthesize a more specific scientific next step.

## Workstream design

### W1. Lane-aware research-contract semantics [code change]

**Primary files**

- `research/knowledge-hub/runtime/scripts/orchestrate_topic.py` — main
  contract builder entry point
- `research/knowledge-hub/runtime/scripts/sync_topic_state_support.py` —
  state sync that triggers contract regeneration
- `research/knowledge-hub/runtime/scripts/orchestrator_contract_support.py` —
  contract template construction helpers
- `research/knowledge-hub/knowledge_hub/theory_context_injection.py` —
  theory context extraction for contract fields
- `research/knowledge-hub/knowledge_hub/semantic_routing.py` —
  template_mode / research_mode resolution
- `research/knowledge-hub/topics/*/runtime/research_question.contract.md` —
  existing generated contracts for regression comparison

**Files to create**

- `research/knowledge-hub/knowledge_hub/lane_contract_defaults.py` — new
  helper: lane-aware default population for `observables`, `target_claims`,
  `deliverables` fields

**Changes**

- add a runtime-side helper for lane-aware contract defaults,
- preserve stronger natural-language topic text whenever present,
- generate lane-specific `observables`, `target_claims`, and `deliverables`,
- tighten documentation around high-rigor fields,
- keep the JSON schema unchanged; enrichment is construction-time only.

**Success condition**

Reading `research_question.contract.md` should let a physicist answer:

- what exact bounded scientific question is active,
- what quantity or claim is under study,
- what the lane-specific success standard is,
- what this topic is explicitly **not** claiming.

Mechanically, the acceptance test must assert:

- for any topic with `research_mode == formal_derivation`, the `observables`
  field contains at least one physics-specific term not present in the generic
  template string,
- the `target_claims` field does not match the pattern `action:*:NN`,
- the `deliverables` field is not identical to the generic template string.

### W2. Research-facing next-action synthesis [code change]

**Primary files**

- `research/knowledge-hub/runtime/scripts/decide_next_action.py` —
  next-action decision logic, fallback to `inspect_resume_state`
- `research/knowledge-hub/runtime/scripts/orchestrate_topic.py` —
  orchestrator that calls the decision logic
- `research/knowledge-hub/runtime/scripts/interaction_surface_support.py` —
  surface rendering for dashboard/console

**Files to create**

- `research/knowledge-hub/knowledge_hub/next_action_synthesis.py` — new
  helper: research-facing summary generation from topic state

**Changes**

- introduce a synthesis helper that distinguishes root cause A (queue-empty /
  never-bootstrapped) from root cause B (queue-has-entries but generic summary),
- for root cause A: synthesize a structural bootstrap action phrased in
  research terms using the topic's `research_question` text and L0 source
  index,
- for root cause B: rephrase the queue head action using lane-specific
  evidence from the contract,
- keep `inspect_resume_state` available internally but not as the preferred
  top-level human action,
- phrase queue mismatch remediation as scientific next work when possible,
- align dashboard and operator console top sections on that result.

**Success condition**

For the operator-facing path, the top next action must not be
`inspect_resume_state` when any of the following are true:

- the topic has a non-empty L0 source index,
- the topic has a non-empty `research_question.contract` question field,
- the topic has been bootstrapped at least once (has a run directory).

When none of the above are true (topic is truly empty), the action may remain
`inspect_resume_state` but must be labelled as a bootstrap action.

### W3. `L0` source-intake expansion [content lift]

**Primary files**

- `research/knowledge-hub/L0_SOURCE_LAYER.md` — source layer documentation
- `research/knowledge-hub/source-layer/scripts/register_arxiv_source.py` —
  current arXiv source registration
- `research/knowledge-hub/source-layer/scripts/register_local_note_source.py` —
  current local-note registration
- `research/knowledge-hub/source-layer/scripts/backfill_topic_sources.py` —
  source backfill logic
- `research/knowledge-hub/source-layer/scripts/enrich_with_deepxiv.py` —
  enrichment logic
- `research/knowledge-hub/tests/test_source_layer_registration.py` —
  existing source tests
- `research/knowledge-hub/schemas/source-item.schema.json` — source schema

**Changes**

- broaden public source-family vocabulary in `L0_SOURCE_LAYER.md` to cover
  all four families (paper, book/lecture, code repo, local note),
- improve source distillation heuristics so book/lecture/code/local-note inputs
  contribute better lane-specific topic text,
- keep the acquisition path explicit and auditable.

**Success condition**

- `L0_SOURCE_LAYER.md` documents all four source families with examples,
- at least two source types beyond `paper` are registered in at least one
  existing topic's source index,
- the new source types pass `test_source_layer_registration.py`.

### W4. `L4` validation starter packs [content lift]

**Primary files**

- `research/knowledge-hub/validation/tools/tfim_exact_diagonalization.py` —
  existing TFIM starter
- `research/knowledge-hub/knowledge_hub/_bundle/validation/tools/tfim_exact_diagonalization.py` —
  bundled copy

**Files to create**

- `research/knowledge-hub/validation/tools/README.md` — pack taxonomy and
  usage guide
- `research/knowledge-hub/validation/templates/README.md` — template index
- `research/knowledge-hub/validation/templates/formal_theory_pack.md` —
  formal-theory starter guidance
- `research/knowledge-hub/validation/templates/toy_numeric_pack.md` —
  toy-numeric starter guidance

**Changes**

- define starter validation pack categories in README,
- expose bounded starter guidance for toy-model, code-method, and
  formal-theory lanes,
- keep the current TFIM starter as one pack member rather than the whole story,
- surface validator-family expectations in contracts and notes.

**Success condition**

- `validation/tools/README.md` exists and documents three pack categories,
- each pack template references at least one concrete example or workflow,
- existing TFIM acceptance test (`run_tfim_benchmark_code_method_acceptance.py`)
  continues to pass.

### W5. `L2` seed enrichment [content lift]

**Primary files**

- `research/knowledge-hub/knowledge_hub/cli_l2_compiler_handler.py` —
  L2 compilation entry point
- `research/knowledge-hub/knowledge_hub/cli_l2_graph_handler.py` —
  L2 graph handler
- `research/knowledge-hub/knowledge_hub/l2_staging.py` — L2 staging logic
- `research/knowledge-hub/schemas/candidate-seed.schema.json` — seed schema
- `research/knowledge-hub/knowledge_hub/_bundle/canonical/canonical-unit.schema.json` —
  canonical unit schema
- `research/knowledge-hub/tests/test_l2_backend_contracts.py` — L2 acceptance
- `research/knowledge-hub/tests/test_l2_hygiene.py` — L2 hygiene tests

**Changes**

- add one bounded formal-theory seed unit,
- add one bounded toy-model seed unit,
- add one bounded code-method seed unit,
- ensure each compiles through `cli_l2_compiler_handler.py` without errors,
- ensure each passes `test_l2_backend_contracts.py` and `test_l2_hygiene.py`.

**Success condition**

- three new seed units exist, one per lane,
- each seed compiles and passes the existing L2 acceptance suite,
- each seed contains: question shape, source basis, validation logic, promoted
  outcome, non-claims.

### W6. Acceptance and regression [cross-cutting integration gate]

W6 is not an independent workstream. It is a cross-cutting integration gate:

- each of W1–W5 must land with its own focused tests,
- W6 defines the integration-level acceptance that runs after all workstreams
  are complete.

**Primary files**

- `research/knowledge-hub/runtime/scripts/run_formal_real_topic_dialogue_acceptance.py`
- `research/knowledge-hub/runtime/scripts/run_toy_model_real_topic_dialogue_acceptance.py`
- `research/knowledge-hub/runtime/scripts/run_first_principles_real_topic_dialogue_acceptance.py`
- `research/knowledge-hub/runtime/scripts/run_hs_toy_model_target_contract_acceptance.py`
- `research/knowledge-hub/runtime/scripts/run_librpa_qsgw_target_contract_acceptance.py`

**Changes**

- add failing tests for contract semantic preservation,
- add failing tests for research-facing next-action rendering,
- extend real-topic acceptance to assert lane-aware contract semantics and
  removal of human-facing runtime-self-inspection wording.

**Success condition**

All three real-topic dialogue acceptance scripts pass, each asserting:

- the research contract preserves domain-specific language in the `question`
  field,
- the `observables` field contains lane-specific content,
- the `target_claims` field does not contain bare action ids,
- the top human-facing next action is not `inspect_resume_state` when the
  topic has non-empty source index and contract question.

## Architecture impact

This wave is intentionally **behavioral before architectural**.

It does not require a full refactor of the runtime.
But it should still move the codebase one step toward better separation by
introducing focused helpers where new semantics would otherwise bloat existing
hotspot files further.

The expected shape is:

- keep `mcp_server.py`, `orchestrate_topic.py`, `decide_next_action.py`, and
  the runtime scripts as orchestrators,
- extract new lane-aware contract defaulting into
  `lane_contract_defaults.py`,
- extract research-facing next-action synthesis into
  `next_action_synthesis.py`,
- keep the public behavior change concentrated and testable.

This balances two needs:

- immediate user-facing improvement now,
- no new giant service-function growth in order to get it.

## Risks

### 1. Over-tightening contract semantics

If lane-aware defaults become too rigid, early exploratory topics may feel
forced into fake precision.

Mitigation:

- keep fallback fields honest,
- preserve uncertainty markers,
- allow generic fallback only when stronger topic-specific material truly is
  absent.

### 2. Human-facing next actions become too clever

If next-action synthesis invents scientific specificity not grounded in topic
state, the system becomes more fluent but less honest.

Mitigation:

- synthesize only from existing durable evidence,
- prefer "recover X" over "conclude Y" phrasing,
- keep evidence refs on the decision surface.

### 3. Public content additions become shallow marketing

If new `L0`/`L4`/`L2` entries are added just to improve counts, this wave would
increase apparent richness without increasing actual reuse.

Mitigation:

- add only bounded, lane-aligned, test-backed seeds,
- prefer a few strong examples over broad coverage,
- each new L2 seed must pass the existing L2 acceptance test suite.

### 4. Content-lift workstreams expand beyond scope

W3–W5 involve editorial judgment and could expand if the boundary is not clear.

Mitigation:

- W3 adds documentation and registration for existing source types; it does not
  build new acquisition pipelines,
- W4 adds README and templates; it does not build new validation backends,
- W5 adds exactly three seed units; it does not build a corpus.

## Testing strategy

Testing should follow three layers.

### Unit / focused behavior tests

- lane-specific research-contract default generation,
- next-action synthesis behavior for root cause A (queue-empty) and root cause B
  (generic summary),
- source-family distillation classification,
- starter-pack surfacing logic.

### Integration tests

- `orchestrate_topic.py` producing stronger contract payloads,
- dashboard/operator-console convergence on research-facing next action,
- `cli_l2_compiler_handler.py` still functioning with new seed units.

### Acceptance tests

- real natural-language formal topic,
- real natural-language toy-model topic,
- real natural-language first-principles/code-method topic.

Each should verify:

- the research contract preserves domain-specific language,
- lane-specific scientific fields are present and non-generic,
- the top human-facing next action is not runtime self-inspection when a
  stronger scientific next step can be synthesized.

## Delivery order

Implement this wave in four phases.

### Phase 1: contract semantics (W1)

- land lane-aware contract helper (`lane_contract_defaults.py`),
- wire it into `orchestrate_topic.py` via `orchestrator_contract_support.py`,
- add real-topic regression tests for preserved physics semantics.

### Phase 2: next-action and surface convergence (W2)

- land research-facing next-action synthesis (`next_action_synthesis.py`),
- wire it into `decide_next_action.py`,
- update dashboard/operator-console rendering via `interaction_surface_support.py`,
- add regression coverage for root cause A and root cause B fallback cases.

### Phase 3: public content lift (W3 + W4 + W5)

- expand `L0` source-family handling in documentation and registration,
- add validation starter-pack README and templates,
- add three lane-specific L2 seed units.

W3–W5 may be done in parallel since they are independent content additions.

### Phase 4: acceptance closure (W6)

- run the targeted real-topic acceptances,
- confirm no regression in current first-run/public paths,
- update docs that describe the public kernel readiness surface.

## Acceptance criteria

This design is successful when **all** of the following are mechanically true.

1. **Contract question preservation**: for every topic whose natural-language
   request contains a domain-specific physics term (e.g. "OTOC", "von Neumann
   algebra", "Green-function topological invariant"), that term appears in the
   `research_question.contract.md` `## Question` section. Verified by string
   match in acceptance tests.

2. **Contract field lane-specificity**: for topics with
   `research_mode == formal_derivation`, the `observables` field must not equal
   the generic template string "Declared candidate ids, bounded claims, and
   validation outcomes." For topics with `template_mode == code_method`, the
   `deliverables` field must not equal the generic template string. Verified by
   exact string inequality in acceptance tests.

3. **Next-action research shaping**: for topics where the L0 source index is
   non-empty and the contract question field is non-empty, the top human-facing
   next action must not be `inspect_resume_state`. Verified by action type
   check in `next_action_decision.json`.

4. **Content lift completeness**:
   - `L0_SOURCE_LAYER.md` documents four source families,
   - `validation/tools/README.md` documents three starter packs,
   - three new L2 seed units compile through `cli_l2_compiler_handler.py` and
     pass `test_l2_backend_contracts.py`.

5. **No regression**: all existing acceptance tests that passed before this
   wave continue to pass after.

## Recommended next step

After review, write an implementation plan that splits this design into a small
number of TDD-first tasks with explicit file ownership.

The first implementation slice should target `W1` and `W2` before the content
lift, because those two workstreams unlock the largest user-visible improvement
with the least scientific ambiguity.
