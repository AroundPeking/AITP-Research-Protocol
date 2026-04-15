# Phase 165.2: Mode Envelope Runtime Enforcement + Literature Intake Fast Path

## Goal

Make the 4 AITP operating modes (discussion, explore, verify, promote) actually
control runtime behavior, and add a lightweight literature-intake fast path so
papers can deposit reusable knowledge into L2 without the full formal-theory
audit pipeline.

## Current State

### What exists
- `mode_envelope_support.py`: 4 mode specs defined, `_select_runtime_mode()`
  auto-selects mode from runtime state, `build_runtime_mode_contract()` builds
  a mode contract dict, `runtime_mode_markdown_lines()` renders to markdown.
- `runtime_bundle_support.py`: imports from mode_envelope_support but does not
  use the selected mode to vary `must_read_now` / `may_defer_until_trigger`.
- `L1_VAULT_PROTOCOL.md`: raw/wiki/output vault exists for intake.
- `L2_STAGING_PROTOCOL.md`: staging exists for provisional L2-adjacent material.
- `ARXIV_FIRST_SOURCE_INTAKE.md`: arXiv-first source acquisition policy exists.

### What is missing
1. Runtime bundle generation does not vary context loading by mode.
2. Runtime protocol markdown buries mode info instead of surfacing it early.
3. No lightweight path from "read a paper" to "deposit knowledge into L2 staging."
4. Escalation triggers fire uniformly regardless of mode.
5. No acceptance test for mode-aware behavior.
6. Front-door agents still do not surface H-plane / human-control posture clearly enough in chat.
7. Verify-mode iterative loops still feel too bounded when no real human checkpoint is active.

## Plan 165.2-01: Mode-Aware Runtime Bundle + Escalation Sensitivity

### Scope
- `runtime_bundle_support.py`: mode-aware `must_read_now` / `may_defer_until_trigger`
- `mode_envelope_support.py`: mode-specific escalation trigger profiles
- Runtime protocol markdown: promote mode section to top-level
- Acceptance test scaffolding

### Tasks

1. **Define mode-specific context-loading profiles in `mode_envelope_support.py`:**
   ```
   DISCUSSION_PROFILE = {
     must_include: [topic_synopsis, research_question, control_note],
     must_exclude: [validation_bundles, promotion_surfaces, broad_l2_retrieval]
   }
   EXPLORE_PROFILE = {
     must_include: [research_question, active_candidate, relevant_l1_l3],
     must_exclude: [promotion_package, unrelated_history, broad_l2]
   }
   VERIFY_PROFILE = {
     must_include: [validation_contract, selected_candidate, execution_surface],
     must_exclude: [unrelated_l2, unrelated_topic_history]
   }
   PROMOTE_PROFILE = {
     must_include: [gate_state, candidate, target_backend, supporting_artifacts],
     must_exclude: [unrelated_history, future_publication_surfaces]
   }
   ```

2. **Wire `build_runtime_bundle()` in `runtime_bundle_support.py` to use the
   selected mode profile when building `must_read_now` and `may_defer_until_trigger`:**
   - After `_select_runtime_mode()` returns a mode, use the corresponding
     profile to filter/expand the surface lists.
   - Surfaces that match `must_include` patterns go to `must_read_now`.
   - Surfaces that match `must_exclude` patterns go to `may_defer_until_trigger`.
   - Surfaces that don't match either stay in their current category.

3. **Add mode-specific escalation trigger profiles in `mode_envelope_support.py`:**
   ```python
   _MODE_ESCALATION_TRIGGERS = {
     "discussion": {"direction_ambiguity", "scope_change"},
     "explore": {"candidate_ready", "route_change", "source_gap"},
     "verify": {"validation_complete", "contradiction_detected", "proof_obligation_resolved"},
     "promote": {"gate_passed", "gate_rejected", "human_override"},
   }
   ```
   - When the runtime bundle checks escalation triggers, it should only fire
     triggers that belong to the current mode's set.
   - Out-of-mode triggers should be logged but not escalated.

4. **Promote mode section in `runtime_protocol.generated.md`:**
   - Move the `## Mode envelope` and `## Transition posture` sections to appear
     immediately after the topic header, before any detailed action queues.
   - Add a one-line summary: "Operating in `{mode}` mode. {local_task}"

5. **Acceptance test: `run_mode_enforcement_acceptance.py` (part 1):**
   - Bootstrap a topic, force discussion mode, verify must_read_now is minimal.
   - Force explore mode, verify expanded context.
   - Force verify mode, verify L4-foreground loading.
   - Force promote mode, verify gate-state loading.
   - Verify escalation triggers fire only for the active mode's trigger set.

6. **Front-door visible H-plane + autonomy contract:**
   - `session_start.generated.md` and `runtime_protocol.generated.md` must publish a plain-language human-control summary.
   - The summary must tell the agent whether AITP is waiting on the human now, or whether bounded work should continue autonomously.
   - Codex / Claude Code / OpenCode skill text must explicitly tell the agent to surface that posture before deeper work.

7. **Iterative verify continuation budget:**
   - `run_topic_loop()` must expand bounded auto-step budget for `verify + iterative_verify` when no active checkpoint or clarification gate is present.
   - Do not expand when the human explicitly disabled auto steps or when a real checkpoint / approval / clarification gate is active.
   - Treat this as a foreground agent-loop contract, not as a hidden daemon.

### Out of scope
- Literature-intake fast path (Plan 165.2-02).
- New CLI commands.
- Changes to the layer model or promotion policy.

### Verification
- `run_mode_enforcement_acceptance.py --json` passes on isolated temp kernel root.
- Existing acceptance tests still pass.
- `aitp doctor --json` reports mode_envelope surface as present.
- Session-start / runtime markdown and Codex prompt tests all assert the same human-control + autonomy contract.

---

## Plan 165.2-02: Literature-Intake Fast Path + L2 Staging Bridge

### Scope
- New `literature` submode under `explore` in `mode_envelope_support.py`.
- L1 vault → L2 staging bridge in a new helper module or extension of
  `staging` support.
- Acceptance test for the fast path.

### Tasks

1. **Define `literature` submode in `mode_envelope_support.py`:**
   ```python
   "literature": {
     "parent_mode": "explore",
     "local_task": "Read a source, extract reusable knowledge units, and stage them into L2 without full formal-theory audit.",
     "entry_conditions": [
       "Action involves source intake, reading, or note extraction.",
       "No active benchmark or proof obligation.",
       "Topic lane is formal_theory or mixed.",
     ],
     "exit_conditions": [
       "All extractable units from the current source are staged.",
       "Human redirects to a different task.",
     ],
     "allowed_unit_types": [
       "concept", "physical_picture", "method", "warning_note",
       "claim_card", "workflow",
     ],
     "forbidden_unit_types": [
       "theorem_card", "proof_fragment", "derivation_object",
     ],
     "required_writeback": [
       "L2 staging entries with literature_intake_fast_path provenance tag.",
       "L1 vault wiki pages for the source.",
     ],
   }
   ```
   - Entry: detected automatically when explore-mode actions involve source
     intake keywords, or manually via `--skill-query "literature intake"`.
   - Exit: when all extractable units are staged or human redirects.

2. **Implement L1 vault → L2 staging bridge:**
   - New function `stage_literature_units()` in a new module
     `literature_intake_support.py` (or extend `staging` support).
   - Input: topic slug, source slug, list of candidate knowledge units
     extracted from L1 vault wiki pages.
   - For each unit:
     - Validate it is in `allowed_unit_types`.
     - Create a canonical-format JSON with `provenance.literature_intake_fast_path: true`.
     - Write to `canonical/staging/entries/` following `L2_STAGING_PROTOCOL.md`.
     - Update `staging_index.jsonl` and `workspace_staging_manifest.json`.
   - Staged items are immediately searchable via `aitp consult-l2` but are not
     in canonical L2 until a later full audit promotes them.

3. **Wire the fast path into the topic loop:**
   - When `_select_runtime_mode()` returns "explore" and the action summary
     contains source-intake keywords, set `active_submode = "literature"`.
   - The runtime bundle for literature submode should include:
     - The L1 vault wiki pages for the current source.
     - The L2 staging manifest (to check for duplicates).
     - The canonical index (to check for existing units).
   - The runtime bundle should NOT include:
     - Validation bundles.
     - Promotion gates.
     - Full coverage audit surfaces.

4. **Acceptance test: `run_mode_enforcement_acceptance.py` (part 2):**
   - Register an arXiv source (existing `register_arxiv_source.py`).
   - Run a literature-intake loop on the topic.
   - Verify that:
     - The runtime bundle is in literature submode.
     - Extracted concept/physical_picture/method units appear in L2 staging.
     - Staged units carry `literature_intake_fast_path: true` provenance.
     - Staged units are NOT in canonical L2 (no premature promotion).
     - `aitp consult-l2` returns the staged units with a staging indicator.
   - All checks on isolated temp kernel root.

### Out of scope
- Automatic promotion from staging to canonical (requires later full audit).
- New `aitp intake-literature` CLI command (convenience wrapper, defer to
  Phase 165.3 if needed).
- Changes to existing promotion or validation surfaces.

### Verification
- `run_mode_enforcement_acceptance.py --json` passes both parts on isolated
  temp kernel root.
- Staged literature units are visible via `aitp consult-l2 --retrieval-profile
  l1_provisional_understanding` but not in `index.jsonl`.
- Existing acceptance tests still pass.

---

## Dependencies

- Plan 165.2-01 must complete before Plan 165.2-02 (literature submode builds
  on mode-aware runtime bundle).
- Phase 165 should ideally complete first (real-topic E2E validates that mode
  design addresses real friction), but 165.2-01 can start in parallel since
  mode-aware context loading is self-contained.

## Key Files

| File | Change |
|---|---|
| `knowledge_hub/mode_envelope_support.py` | Add mode profiles, escalation triggers, literature submode |
| `knowledge_hub/runtime_bundle_support.py` | Wire mode profiles into context loading |
| `knowledge_hub/literature_intake_support.py` | New: L1→L2 staging bridge |
| `runtime/scripts/run_mode_enforcement_acceptance.py` | New: acceptance test |
| `knowledge_hub/kernel_markdown_renderers.py` | Promote mode section in runtime protocol md |

## Risk Notes

- The literature fast path deliberately bypasses formal coverage/theory audit.
  The `literature_intake_fast_path: true` provenance tag ensures these units
  are always identifiable as "not yet fully audited" in L2 consultation results.
- Staged literature units should be treated as "probably correct but not yet
  verified" by agents consulting L2. The retrieval profile should surface the
  provenance tag.
- Mode-specific escalation trigger profiles may need iteration once tested
  against real topics. Start conservative (fewer triggers per mode) and expand.
