# AITP Acceptance Test Baseline

Date: 2026-04-17
Authoring session: S10
Scope: Read-only baseline capture for unit tests and acceptance scripts. No production or test code was modified.

## Summary

- Unit test files discovered: 88
- Acceptance scripts discovered: 74
- Short-path unit baseline: `775 passed, 0 failed, 19 subtests passed` from `python -m pytest tests/ -v --tb=line` with `TMP/TEMP=C:\t`
- Long-TMP control run: `741 passed, 34 failed, 19 subtests passed`; every observed failure was `INFRA`, caused by Windows path-length pressure while copying runtime bundles into deep temporary roots
- Acceptance scripts impacted by mode migration: 5
- Acceptance scripts with confirmed long-TMP path failures: 24
- Acceptance scripts with potential long-path risk by static inspection: 48
- Acceptance scripts with no observed long-path issue from static inspection: 2
- Short-path sampling of 5 mode-related acceptance scripts did not reveal Windows path failures; instead, all 5 were blocked by current shared-worktree import inconsistencies introduced during parallel editing

## Method

1. Enumerated all unit tests with `rg --files research/knowledge-hub/tests -g 'test_*.py'`.
2. Enumerated all acceptance scripts with `rg --files research/knowledge-hub/runtime/scripts -g 'run_*_acceptance.py'`.
3. Ran the full unit suite twice:
   - First with a long Windows temp root under `%LOCALAPPDATA%\Temp\aitp_acceptance_baseline`
   - Then with a short temp root `C:\t`
4. Classified acceptance scripts statically by:
   - Presence of old mode assertions or old CLI mode commands (`discussion`, `verify`, `promote`)
   - Presence of long-path-sensitive setup patterns such as `copytree`, `prepare_first_run_kernel`, `tempfile.mkdtemp`, or explicit `--work-root` handling
5. Sampled 5 mode-related acceptance scripts using a short work root under `C:\t`.

## Unit Test Final Baseline

| Run | Temp root | Result | Classification |
| --- | --- | --- | --- |
| Full pytest baseline | `C:\t` | `775 passed, 0 failed, 19 subtests passed in 532.61s` | PASS |
| Full pytest control | `%LOCALAPPDATA%\Temp\aitp_acceptance_baseline` | `741 passed, 34 failed, 19 subtests passed in 293.84s` | FAIL_INFRA |

### Long-TMP Failures

All 34 long-TMP failures were infrastructure failures, not code regressions. Representative stack traces showed `shutil.copytree(...)` failing with Windows path resolution errors while materializing `canonical/staging/entries/*` into deep temporary work roots.

| Test family | Count | Representative failures | Category | Root cause |
| --- | --- | --- | --- | --- |
| `tests/test_aitp_cli_e2e.py` | 1 | `test_first_run_acceptance_can_continue_into_source_registration` | INFRA | Long temp root caused `run_first_run_topic_acceptance.py` bundle copy failure |
| `tests/test_brain_lifecycle_contracts.py` | 8 | Bootstrap / chronicle / scheduler scenarios | INFRA | Shared first-run kernel copy exceeded comfortable Windows path margin |
| `tests/test_runtime_scripts.py` | 24 | Acceptance-script isolation tests listed below in the confirmed long-TMP set | INFRA | Acceptance scripts copied large runtime bundles into deep isolated work roots |
| `tests/test_theory_context_injection.py` | 1 | `test_build_prerequisite_fragment_handles_long_fresh_topic_names` | INFRA | Combined long temp root plus long generated topic name exceeded path comfort margin |

### Confirmed Long-TMP Acceptance Script Failures

These 24 acceptance scripts were directly implicated by the long-TMP pytest control run:

- `run_consultation_followup_selection_acceptance.py`
- `run_first_principles_real_topic_dialogue_acceptance.py`
- `run_first_run_topic_acceptance.py`
- `run_first_source_followthrough_acceptance.py`
- `run_formal_real_topic_dialogue_acceptance.py`
- `run_hs_positive_l2_acceptance.py`
- `run_hs_positive_negative_coexistence_acceptance.py`
- `run_hs_toy_model_target_contract_acceptance.py`
- `run_l1_graph_analysis_staging_acceptance.py`
- `run_l1_graph_community_bridge_acceptance.py`
- `run_l1_graph_diff_runtime_acceptance.py`
- `run_l1_graph_diff_staging_acceptance.py`
- `run_l1_graph_hyperedge_pattern_acceptance.py`
- `run_l2_knowledge_report_acceptance.py`
- `run_librpa_qsgw_positive_l2_acceptance.py`
- `run_librpa_qsgw_target_contract_acceptance.py`
- `run_mode_enforcement_acceptance.py`
- `run_multi_paper_l2_relevance_acceptance.py`
- `run_positive_negative_l2_coexistence_acceptance.py`
- `run_promotion_review_gate_acceptance.py`
- `run_selected_candidate_route_choice_acceptance.py`
- `run_staged_l2_advancement_acceptance.py`
- `run_staged_l2_reentry_acceptance.py`
- `run_toy_model_real_topic_dialogue_acceptance.py`

## Mode Migration Impact

The acceptance classification distinguishes true mode-migration coverage from unrelated uses of words like “promoted” or `promote_candidate`. Only scripts that still assert old runtime modes or invoke old CLI mode commands are counted as mode-migration impacted.

### Mode-Migration-Impacted Scripts

| Script | Why it is mode-related | Short-path sample result |
| --- | --- | --- |
| `run_analytical_cross_check_surface_acceptance.py` | Calls old CLI command `verify` | ERROR: downstream `python -m knowledge_hub.aitp_cli analytical-review ...` import chain failed |
| `run_analytical_judgment_surface_acceptance.py` | Calls old CLI command `verify` and asserts `verify --mode analytical` behavior | ERROR: downstream `python -m knowledge_hub.aitp_cli analytical-review ...` import chain failed |
| `run_l1_progressive_reading_acceptance.py` | Seeds and asserts `runtime_mode: verify` | ERROR: downstream `python -m knowledge_hub.aitp_cli status ...` import chain failed |
| `run_mode_enforcement_acceptance.py` | Explicitly asserts `discussion`, `verify`, and `promote` runtime modes | ERROR: import failed on `l1_notation_alignment_lines` |
| `run_selected_candidate_promotion_writeback_acceptance.py` | Invokes old CLI command `promote` | ERROR: `ModuleNotFoundError: knowledge_hub.collaborator_profile_support` |

### Notes

- Not counted as mode-migration scripts:
  - Scripts that merely call `service.promote_candidate(...)`
  - Scripts that check `promoted` status fields
  - Scripts that use `promote-exploration` as a dedicated workflow command
- Those are promotion-pipeline semantics, not old runtime-mode assertions.

## Sampled Short-Path Acceptance Runs

All sample runs used short work roots under `C:\t` and therefore were not blocked by Windows path length. Every failure instead came from the current shared worktree import state after concurrent edits from other sessions.

| Script | Command shape | Result | Category |
| --- | --- | --- | --- |
| `run_mode_enforcement_acceptance.py` | `python runtime/scripts/run_mode_enforcement_acceptance.py --json --work-root C:\t\...` | ImportError: `l1_notation_alignment_lines` missing from `knowledge_hub.l1_source_intake_support` | ERROR / shared-worktree conflict |
| `run_l1_progressive_reading_acceptance.py` | `python runtime/scripts/run_l1_progressive_reading_acceptance.py --json --work-root C:\t\...` | Downstream `python -m knowledge_hub.aitp_cli status ...` import chain failed | ERROR / shared-worktree conflict |
| `run_analytical_cross_check_surface_acceptance.py` | `python runtime/scripts/run_analytical_cross_check_surface_acceptance.py --json --work-root C:\t\...` | Downstream `python -m knowledge_hub.aitp_cli analytical-review ...` import chain failed | ERROR / shared-worktree conflict |
| `run_analytical_judgment_surface_acceptance.py` | `python runtime/scripts/run_analytical_judgment_surface_acceptance.py --json --work-root C:\t\...` | Downstream `python -m knowledge_hub.aitp_cli analytical-review ...` import chain failed | ERROR / shared-worktree conflict |
| `run_selected_candidate_promotion_writeback_acceptance.py` | `python runtime/scripts/run_selected_candidate_promotion_writeback_acceptance.py --json --work-root C:\t\... --register-arxiv-id 2401.12345` | `ModuleNotFoundError: knowledge_hub.collaborator_profile_support` | ERROR / shared-worktree conflict |

## Current Import Integrity Check

At the time of finalizing this report, the live shared worktree no longer imported cleanly:

```text
python -c "import knowledge_hub"
ModuleNotFoundError: No module named 'knowledge_hub.research_trajectory_support'
```

This means:

- The `775 passed` unit-test baseline is a valid historical snapshot for the short-path run completed earlier in this session.
- The current repository state has changed underneath S10 because of concurrent sessions.
- Short-path acceptance sampling now reflects shared-worktree conflicts rather than Windows path problems.

## Complete Acceptance Script Classification

Legend:

- `Mode signal`:
  - `Old CLI verify/promote` or `Old runtime_mode ...` means the script is impacted by the 4-mode -> 3-mode migration.
  - `No old mode assertion detected` means no direct migration assertion was found in the script body.
- `Path status`:
  - `Confirmed long-TMP INFRA` means the script was implicated by the long-temp pytest control failure.
  - `Potential long-path risk` means static inspection found bundle-copy or temp-root patterns that could become path-sensitive on Windows.
  - `No long-path issue observed` means neither signal was found.

| Script | Mode signal | Path status | Short-path sample |
| --- | --- | --- | --- |
| `run_analytical_cross_check_surface_acceptance.py` | Old CLI `verify` command | Potential long-path risk | ERROR on short path; downstream `knowledge_hub.aitp_cli analytical-review` import chain failed |
| `run_analytical_judgment_surface_acceptance.py` | Old CLI `verify` command + assertion text | Potential long-path risk | ERROR on short path; downstream `knowledge_hub.aitp_cli analytical-review` import chain failed |
| `run_collaborator_continuity_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_competing_hypotheses_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_consultation_followup_selection_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_dependency_contract_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_first_principles_real_topic_dialogue_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_first_run_topic_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_first_source_followthrough_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_formal_positive_l2_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_formal_real_topic_dialogue_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_hs_positive_l2_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_hs_positive_negative_coexistence_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_hs_toy_model_target_contract_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_human_modification_record_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_branch_routing_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_activation_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_choice_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_handoff_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_reentry_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_transition_authority_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_transition_clearance_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_transition_commitment_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_transition_discrepancy_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_transition_escalation_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_transition_followthrough_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_transition_gate_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_transition_intent_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_transition_receipt_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_transition_repair_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_transition_resolution_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_hypothesis_route_transition_resumption_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_jones_chapter4_finite_product_formal_closure_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_l0_source_concept_graph_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_l0_source_discovery_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_l0_source_enrichment_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_l1_assumption_depth_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_l1_concept_graph_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_l1_contradiction_surface_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_l1_graph_analysis_staging_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_l1_graph_community_bridge_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_l1_graph_diff_runtime_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_l1_graph_diff_staging_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_l1_graph_hyperedge_pattern_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_l1_graph_obsidian_brain_bridge_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_l1_graph_obsidian_export_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_l1_graph_obsidian_multicommunity_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_l1_method_specificity_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_l1_progressive_reading_acceptance.py` | Old runtime_mode `verify` assertions | Potential long-path risk | ERROR on short path; downstream `knowledge_hub.aitp_cli status` import chain failed |
| `run_l1_vault_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_l2_knowledge_report_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_l2_mvp_direction_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_librpa_qsgw_positive_l2_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_librpa_qsgw_target_contract_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_mode_enforcement_acceptance.py` | Old runtime_mode assertions for `discussion`/`verify`/`promote` | Confirmed long-TMP INFRA | ERROR on short path; ImportError `l1_notation_alignment_lines` from shared worktree |
| `run_multi_paper_l2_relevance_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_positive_negative_l2_coexistence_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_promotion_review_gate_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_quick_exploration_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_real_direction_corpus_growth_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_real_lean_bridge_export_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_runtime_parity_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_scrpa_control_plane_acceptance.py` | No old mode assertion detected | No long-path issue observed | Not sampled |
| `run_scrpa_thesis_topic_acceptance.py` | No old mode assertion detected | No long-path issue observed | Not sampled |
| `run_selected_candidate_promotion_writeback_acceptance.py` | Old CLI `promote` command | Potential long-path risk | ERROR on short path; ModuleNotFoundError `knowledge_hub.collaborator_profile_support` |
| `run_selected_candidate_route_choice_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_source_catalog_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_staged_l2_advancement_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_staged_l2_reentry_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_statement_compilation_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_tfim_benchmark_code_method_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_toy_model_real_topic_dialogue_acceptance.py` | No old mode assertion detected | Confirmed long-TMP INFRA | Not sampled |
| `run_transition_history_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |
| `run_witten_topological_phases_formal_closure_acceptance.py` | No old mode assertion detected | Potential long-path risk | Not sampled |

## Recommendations

1. Keep Windows acceptance runs on a short work root such as `C:\t` until the kernel-copy logic is hardened against long paths.
2. Before trusting any new acceptance result, restore shared-worktree import integrity; current blockers include missing `knowledge_hub.research_trajectory_support`, missing `knowledge_hub.collaborator_profile_support`, and missing exported symbol `l1_notation_alignment_lines`.
3. After import integrity is restored, rerun the 5 mode-migration-impacted scripts first. They are the fastest signal for whether the 4-mode -> 3-mode transition is coherent.
4. After those 5 scripts pass on short paths, rerun the full 74-script acceptance set under a short work root to establish a clean post-merge baseline.
