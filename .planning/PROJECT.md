# AITP Runtime And Knowledge Foundations

## What This Is

This is the brownfield GSD planning layer for the canonical
`AITP-Research-Protocol` repository.

It tracks repo implementation work without replacing the protocol itself:
GSD organizes execution, while AITP runtime artifacts remain the source of
truth for research state.

## Core Value

AITP must turn vague but meaningful research starts into bounded, durable, and
explainable runtime state without pretending uncertainty is already resolved.

## Current State

`v1.27 Capability-Audit And Runtime-Sync Boundary Extraction And Closure`
shipped on 2026-04-07.

It delivered:

- capability-audit assembly, recommendation synthesis, and capability report
  persistence now live behind `knowledge_hub/capability_audit_support.py`
- resume-stage inference, evidence-return explainability, and resume-note
  rendering now live behind `runtime/scripts/sync_topic_state_support.py`
- `aitp_service.py` dropped again to `6459` lines while
  `sync_topic_state.py` now keeps its explainability/render boundary outside
  the CLI shell, and targeted regressions plus maintainability budgets stayed
  green

`v1.26` remains the latest shipped milestone immediately underneath this work:

- interaction-surface plus chat-routing boundary extraction and closure

## Future Horizon

After `v1.27`, the next likely work splits into two tracks:

- keep turning doctrine into the next runtime hotspot such as
  `closed_loop_v1.py`
- keep extracting the next remaining service hotspot out of `aitp_service.py`,
  especially steering payloads or innovation-direction helpers

After that stabilization, keep `L5 Publication Factory` as the final
output-layer expansion.

Its intended meaning remains:

- `L0-L4` do the research honestly
- `L2` preserves reusable knowledge
- `L5` turns completed work into publication-grade outputs

`L5` stays downstream of evidence and may not invent new scientific truth.

Detailed parking-lot candidates now live in `.planning/BACKLOG.md` with any
accumulated phase context under `.planning/backlog/`.

## Completed Milestones

### v1.27 Capability-Audit And Runtime-Sync Boundary Extraction And Closure (shipped 2026-04-07)

- `capability_audit_support.py` now owns capability-audit assembly,
  recommendation synthesis, and capability report persistence
- `sync_topic_state_support.py` now owns resume-stage inference,
  evidence-return explainability, and resume-note rendering
- `AITPService.capability_audit()` now acts as a thin stable façade
- targeted runtime-script/service regressions and maintainability budgets
  stayed green

### v1.26 Interaction-Surface And Chat-Routing Boundary Extraction And Closure (shipped 2026-04-07)

- `runtime/scripts/interaction_surface_support.py` now owns interaction-state
  assembly plus operator-console and agent-brief rendering support
- `AITPService.route_codex_chat_request()` and
  `AITPService.start_chat_session()` now act as thin stable façades over
  `chat_session_support.py`
- targeted runtime-script/service regressions and maintainability budgets
  stayed green

### v1.25 Contract-Aware Checkpoint/Append Closure And Loop-Execution Boundary Extraction (shipped 2026-04-07)

- `runtime/scripts/orchestrator_contract_support.py` now owns contract-aware
  queue shaping, checkpoint append gating, and runtime-appended action assembly
- active `operator_checkpoint.active.json` now acts as an explicit append gate
  even before a refreshed runtime bundle catches up
- `AITPService.run_topic_loop()` now acts as a thin stable façade over
  `topic_loop_support.py`
- targeted runtime-script/service regressions and maintainability budgets
  stayed green

### v1.24 Source Distillation Boundary Extraction And Closure (shipped 2026-04-07)

- `source_distillation_support.py` now owns source-backed idea distillation,
  preview fallback recovery, novelty extraction, and lane/first-route inference
- `AITPService._distill_from_sources()` now acts as a thin stable façade
- targeted source-backed topic-start regressions and maintainability budgets
  stayed green

### v1.23 Topic-Skill Projection Boundary Extraction And Closure (shipped 2026-04-07)

- `topic_skill_projection_support.py` now owns topic-skill projection context
  derivation, route/read guidance assembly, and lane-specific availability gating
- `AITPService._derive_topic_skill_projection()` now acts as a thin stable façade
- targeted topic-skill projection regressions and maintainability budgets stayed green

### v1.22 Theory-Coverage Audit Boundary Extraction And Closure (shipped 2026-04-07)

- `theory_coverage_audit_support.py` now owns theory-coverage normalization,
  packet artifact construction, regression-gate assembly, and candidate ledger updates
- `AITPService.audit_theory_coverage()` now acts as a thin stable façade
- targeted theory-coverage regressions and maintainability budgets stayed green

### v1.21 Lean-Bridge Materialization Boundary Extraction And Closure (shipped 2026-04-07)

- `lean_bridge_support.py` now owns Lean-bridge packet construction,
  proof-obligation materialization, and active index synthesis
- `AITPService._materialize_lean_bridge()` now acts as a thin stable façade
- targeted lean-bridge regressions and maintainability budgets stayed green

### v1.20 Candidate Promotion Boundary Extraction And Closure (shipped 2026-04-07)

- `candidate_promotion_support.py` now owns candidate-promotion preparation,
  TPKN writeback materialization, consultation logging, and promotion-state
  finalization
- `AITPService.promote_candidate()` now acts as a thin stable façade
- targeted promotion regressions and maintainability budgets stayed green

### v1.19 Formal-Theory Audit Boundary Extraction And Closure (shipped 2026-04-07)

- `formal_theory_audit_support.py` now owns formal-theory audit normalization,
  blocker evaluation, artifact writing, and candidate ledger updates
- `AITPService.audit_formal_theory()` now acts as a thin stable façade
- targeted formal-theory regressions and maintainability budgets stayed green

### v1.18 Declarative Append Policy Closure And Promotion-Gate Boundary Seed (shipped 2026-04-07)

- declared append policy now suppresses helper-produced runtime-appended
  system actions instead of only the closed-loop branch
- active operator checkpoints now suppress those helper-produced
  runtime-appended actions too, while capability-gap skill append stays under
  its own explicit flag
- `promotion_gate_support.py` now owns shared promotion-gate markdown,
  persistence, logging, and human approval lifecycle support

### v1.17 Checkpoint-Aware Queue Shaping And Auto-Promotion Extraction (shipped 2026-04-07)

- queue shaping now respects explicit human-checkpoint posture for narrow
  runtime-appended suppression cases
- `auto_promote_candidate` now lives in
  `knowledge_hub/auto_promotion_support.py`
- `aitp_service.py` dropped to `8836` lines with regression and
  maintainability guards still green

### v1.16 Contract-Aware Queue Shaping Seed (shipped 2026-04-07)

- queue materialization now suppresses mismatched runtime-appended actions in
  first explicit contract-aware cases
- runtime-script regression locks promotion and consultation shaping cases
- maintainability budgets stayed green

### v1.15 Queue Materialization And Auto-Action Boundary Extraction (shipped 2026-04-07)

- queue materialization now starts honoring the explicit runtime contract
- auto-action execution left `aitp_service.py`
- regression and maintainability guards stayed green

### v1.14 Mode-Aware Queue And Decision Routing Seed (shipped 2026-04-06)

- decision surfaces now read runtime contract hints for queue ordering and
  selected-action choice
- `decide_next_action.py` is now watchlisted explicitly
- runtime-script and service regressions lock the first queue/decision hookup

### v1.13 Transition-Aware Auto-Handler Routing Seed (shipped 2026-04-06)

- auto-handler execution now reads the explicit runtime contract
- backedge transitions now gate the wrong auto handlers
- capability-gap skill discovery remains allowed as a recovery lane

### v1.12 Runtime Mode And Transition Contract Seed (shipped 2026-04-06)

- runtime mode/transition policy extracted into a dedicated support module
- mode and transition posture now exposed explicitly in the bundle contract
- schema/docs/tests updated to lock the new runtime contract

### v1.11 Ontology, Mode, And Context-Policy Formalization (shipped 2026-04-06)

- transition/backedge doctrine added and cross-linked
- light-profile mandatory context reduced to the true primary surfaces
- runtime docs/tests updated to lock the new progressive-disclosure contract

### v1.10 Followup And Closed-Loop Decomposition (shipped 2026-04-05)

- follow-up orchestration extracted from `aitp_service.py`
- deferred-buffer and reintegration/writeback flows extracted from
  `aitp_service.py`
- tighter service budget plus docs/test closure

### v1.9 Topic Shell Assembly Decomposition (shipped 2026-04-05)

- topic-shell assembly extracted from `aitp_service.py`
- topic dashboard and shell-surface derivation extracted from
  `aitp_service.py`
- tighter service budget plus docs/test closure

### v1.8 Continued Kernel Decomposition (shipped 2026-04-05)

- template/session-start rendering extracted from `aitp_service.py`
- pure contract/note markdown rendering extracted from `aitp_service.py`
- runtime bundle and session-start materialization extracted from
  `aitp_service.py`
- tighter service budget plus docs/test closure

### v1.7 Kernel Decomposition And Maintainability Guard (shipped 2026-04-05)

- front-door support extracted from `aitp_service.py`
- agent-install/bootstrap support extracted from `aitp_service.py`
- front-door command family extracted from `aitp_cli.py`
- tighter maintainability budgets plus docs/test closure

### v1.6 Runtime Front-Door Parity Hardening (shipped 2026-04-05)

- explicit runtime/front-door support matrix through `aitp doctor`
- Codex baseline plus Claude/OpenCode parity-target diagnostics
- migration before/after convergence reporting
- docs and regression closure for runtime maturity language

### v1.5 L2 Knowledge Compiler And Hygiene (shipped 2026-04-05)

- compiled `L2`, replay, hygiene, staging, and closure docs/tests

### v1.4 Runtime Simplification And Reuse Foundations (shipped 2026-04-04)

- runtime simplification, boundary extraction, checkpoints, routing, reuse

### v1.3 Multi-Topic Parallel Execution (shipped 2026-04-04)

- authoritative multi-topic runtime control

### v1.2 Projection-First Formal-Theory Seed (shipped 2026-04-01)

- bounded `formal_theory` projection seed

### v1.1 L2 Topic-Skill Projection (shipped 2026-04-01)

- first-class `topic_skill_projection`

### v1.0 Runtime Hardening (shipped 2026-03-31)

- source-grounded topic starts and explicit AITP x GSD workflow contract

## Requirements

### Validated

- [x] `L0 -> L1 -> L3 -> L4 -> L2` remains the stable protocol kernel.
- [x] Multi-topic runtime control is authoritative and scheduler-based.
- [x] `L2` now has compiled, replay, hygiene, and staging support.
- [x] Runtime/front-door support is now diagnosable through `aitp doctor`.
- [x] Topic-shell assembly now lives outside `aitp_service.py`.
- [x] Follow-up / deferred-buffer / reintegration flows now live outside
  `aitp_service.py`.
- [x] Maintainability budgets tightened again after the new extractions.
- [x] Docs and regression coverage now lock the newly extracted boundaries.
- [x] Transition/backedge doctrine is now explicit and cross-linked.
- [x] Light-profile runtime bundles now keep machine/control surfaces deferred
  unless the relevant trigger fires.
- [x] Runtime docs and acceptance expectations now reflect the new
  progressive-disclosure contract.
- [x] Runtime bundles now expose explicit mode and transition contract fields.
- [x] Mode/transition policy now lives outside the bundle materializer.
- [x] Auto-handler execution now obeys the first transition-aware contract
  gate.
- [x] Queue ordering and selected-action choice now obey the first
  contract-aware routing hints.
- [x] Queue materialization now obeys the first contract-aware routing hints.
- [x] Auto-action execution boundary now lives outside `aitp_service.py`.
- [x] Queue materialization now performs the first narrow contract-aware
  shaping step, not only reordering.
- [x] Declared `append_runtime_actions=false` now suppresses helper-produced
  runtime-appended system actions while leaving capability-gap skill append
  under its own explicit contract flag.
- [x] Shared promotion-gate lifecycle helpers now live outside
  `aitp_service.py`.
- [x] Shared formal-theory audit helpers now live outside
  `aitp_service.py`.
- [x] Shared candidate promotion helpers now live outside
  `aitp_service.py`.
- [x] Shared lean-bridge materialization helpers now live outside
  `aitp_service.py`.
- [x] Shared theory-coverage audit helpers now live outside
  `aitp_service.py`.
- [x] Shared topic-skill projection helpers now live outside
  `aitp_service.py`.
- [x] Shared source-distillation helpers now live outside `aitp_service.py`.
- [x] Shared topic-loop helpers now live outside `aitp_service.py`.
- [x] Shared chat-routing and session-start helpers now live outside
  `aitp_service.py`.
- [x] Shared capability-audit helpers now live outside `aitp_service.py`.
- [x] Contract-aware queue policy helpers now live outside `orchestrate_topic.py`.
- [x] Shared interaction-surface helpers now live outside `orchestrate_topic.py`.
- [x] Shared runtime-sync explainability/resume helpers now live outside
  `sync_topic_state.py`.

### Active

No post-`v1.27` milestone is active yet.

Choose the next milestone from `.planning/BACKLOG.md`, then create a fresh
`.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md`.

### Out of Scope

- `L5 Publication Factory`
- new major protocol features
- marketplace packaging
- broad OpenClaw redesign

## Context

- `v1.17` left helper-produced `runtime_appended` actions partially outside
  the declared append-policy switch, even though those helpers already mark
  themselves as `runtime_appended`.
- `v1.24` extracted the shared source-distillation boundary into a dedicated
  support module without changing the public service method.
- `v1.27` extracted the shared capability-audit boundary and the shared
  runtime-sync explainability/resume boundary.
- The main service façade is now `6459` lines with a `140`-line longest
  function, while `sync_topic_state.py` keeps only the CLI shell and remaining
  sync orchestration around a new support boundary, so maintainability work
  remains real and the next bounded targets are steering payloads or
  `closed_loop_v1.py`.
- The detailed backlog parking lot now lives in `.planning/BACKLOG.md` instead
  of the active milestone roadmap surface.

## Constraints

- **Protocol:** Do not change the research-layer kernel while decomposing code.
- **Behavior:** Preserve CLI/runtime behavior during extraction.
- **Brownfield:** Work with the existing dirty tree carefully and avoid
  overwriting unrelated changes.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Keep doing maintainability work before `L5` | A fragile kernel would make the final writing layer harder to trust and evolve | ✓ Locked |
| Use doctrine and runtime behavior changes together | The user wants real harness behavior, not standalone concept notes | ✓ Locked |
| Reduce light-profile mandatory context instead of adding more bundle prose | Too much mandatory context would suppress model intelligence and violate progressive disclosure | ✓ Locked |
| Extract runtime mode policy into its own helper boundary | Explicit runtime contracts should not come at the cost of re-centralizing bundle logic | ✓ Locked |
| Let backedge transitions gate handler execution before rewriting the full orchestrator | The safest first hookup is to stop clearly wrong auto execution before reworking queue generation | ✓ Locked |
| Let decision selection consume the explicit contract before rewriting full queue materialization | This keeps the next hookup bounded while still moving control authority downward from the bundle into real routing logic | ✓ Locked |
| Combine queue-materialization work with one real service extraction in the same milestone | The user explicitly wants both tracks to keep moving, so the roadmap should not force a false serial choice | ✓ Locked |
| Keep queue shaping narrow and explicit | The user does not want Python to become a hidden research brain, so shaping should only suppress mismatched runtime-appended actions that the explicit contract already rules out | ✓ Locked |
| Extract the source-grounded distillation boundary before deeper orchestrator work | `_distill_from_sources` was the next narrow, high-leverage service hotspot with stable topic-start regressions already surrounding it | ✓ Locked |
| Treat active `operator_checkpoint.active.json` as an explicit append gate | The durable checkpoint surface should govern queue expansion even before the derived bundle refresh catches up | ✓ Locked |
| Extract `run_topic_loop` before broader chat-routing decomposition | The loop/execution cluster was the next stable public service façade that could shrink without widening the API | ✓ Locked |
| Extract operator-facing interaction surfaces before deeper runtime rewrites | `build_interaction_state`, `build_operator_console`, and `build_agent_brief` were the next stable orchestrator hotspot cluster with narrow rendering-oriented behavior | ✓ Locked |
| Extract chat routing together with session-start orchestration | `route_codex_chat_request` and `start_chat_session` form one public entry surface and should stay behaviorally aligned behind one helper boundary | ✓ Locked |
| Extract capability audit as one bounded surface | `capability_audit()` was the next stable service hotspot with focused tests and a clear report boundary | ✓ Locked |
| Extract runtime-sync explainability together with resume rendering | `infer_resume_state`, `derive_status_explainability`, and `build_resume_markdown` form one coherent operator-facing sync slice | ✓ Locked |
| Keep maintainability budgets green instead of loosening them for doctrine work | Guardrails should resist regression even when the milestone focus shifts | ✓ Locked |
| Keep `L5 Publication Factory` as a future final layer | Writing stays downstream of evidence and validation | ✓ Locked |

---
*Last updated: 2026-04-07 after shipping v1.27*
