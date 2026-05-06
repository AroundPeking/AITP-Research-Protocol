# L4 Harness Hardening — 2026-05-07

## Changes Applied

### Harness (4 files)

| File | Change |
|------|--------|
| `brain/state.py` | `_LANE_PHYSICS_CHECK_FIELDS`: added `code_method` and `toy_numeric` → `PHYSICS_CHECK_FIELDS[:6]` (includes `approximation_validity_check`) |
| `brain/mcp_server.py:aitp_l4_background_submit` | GUARD: block new submit if previous job completed but no review filed; new params `source_commit_hash`, `source_repo_url`; increment `l4_job_attempt_count`; set `l4_first_entered_at` |
| `brain/mcp_server.py:aitp_submit_l4_review` | GUARD: validate evidence_scripts have actual content (≥200 bytes, contains exec command); validate evidence_outputs files exist on disk |
| `brain/mcp_server.py:aitp_return_to_l3_from_l4` | GUARD: popup warning if background job still running |
| `brain/gates.py:evaluate_l4_stage` | 5 new gate checks: `blocked_no_reviews` (dead-state detection after 3+ attempts), `blocked_repeated_failure` (3+ consecutive failures → L1), `blocked_job_running` (don't declare ready while jobs run), evidence file existence verification, background job status awareness |
| `hooks/aitp_l4_watchdog.py:record_completion` | Consecutive failure counter: increment on fail/timeout/oom/cancelled, reset to 0 on success |

### Test fixes (3 files)

| File | Before | After |
|------|--------|-------|
| `tests/test_l4_l2_memory.py` | 2/9 | **9/9** |
| `tests/test_study_l2_graph.py` | ~14/44 | 27/30 |
| `tests/test_visualization.py` | ~0/18 | 11/18 |

**Root cause of test failures**: `@mcp.tool()` decorator from FastMCP transforms function signatures. Tests called decorated functions with positional arguments, which the wrapper rejects. Fix: use `.__wrapped__` for `@mcp.tool()` functions, keyword arguments for `@require_stage`-only functions.

### Pre-existing test failures (not addressed)

These 12 failures exist on clean `main` branch and are functional, not signature-related:

- `test_l3_activities_are_defined` — assertion on activity count
- `test_edge_rejects_dangling_nodes` — edge creation logic
- `test_query_by_type` — AttributeError in L2 query
- 7x visualization tests — node counts, correspondence detection, type icons
- 2x `HookOutputTests` — subprocess environment-dependent

### Additional pre-existing MCP signature issues (not addressed)

The following test files also have `@mcp.tool()` positional arg issues but were not fixed:
- `tests/test_e2e_scenario_a.py`
- `tests/test_e2e_study_l2.py`
- `tests/test_foundation_safety.py`
- `tests/test_io_contracts.py`
- `tests/test_l3_subplanes.py`

Fix approach is the same: use `.__wrapped__` for `@mcp.tool()` functions, keyword args for others.
