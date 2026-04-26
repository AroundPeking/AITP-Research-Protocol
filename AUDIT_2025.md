# AITP Codebase Audit Report

**Auditor perspective**: Theoretical physicist (rigorous, systematic, first-principles)
**Date**: 2026-04-26
**Scope**: Full codebase — brain/, skills/, hooks/, deploy/, tests/, schemas/

---

## 0. Executive Summary

The AITP protocol is a sophisticated multi-layer research governance system. Its design philosophy — layered gates, trust evolution, adversarial validation — is sound and well-motivated. However, the implementation contains **3 critical defects** (any one of which could silently corrupt research state), **7 systematic inconsistencies** (skill-trigger vs code mismatches that break the dispatch contract), and **numerous engineering quality issues** (duplicate code, dead code, O(n^2) I/O, thread-unsafe globals). These are categorized and analyzed below with the same taxonomy one would use to classify pathologies in a physical theory: gauge anomalies, UV divergences, and IR redundancies.

---

## 1. Critical Defects (Anomalies)

### 1.1 Duplicate `_get_l3_config()` — state_model.py:961 and :983

**What**: The function `_get_l3_config()` is defined twice, with `L3_ARTIFACT_TEMPLATES = L3_ACTIVITY_TEMPLATES` also assigned twice (lines 959 and 981).

**Nature**: This is a gauge anomaly — two conflicting definitions of the same quantity. In Python, the second definition silently shadows the first. If the two definitions ever diverge (one is edited, the other is not), the bug becomes latent and undetectable until a specific code path hits the wrong one.

**Impact**: High. Every L3 gate evaluation depends on this config. Currently the second definition wins, but if someone fixes "the duplicate" by removing the wrong one, the L3 gate logic changes silently.

**Fix**: Delete one definition. Search for any callers that might depend on the first.

### 1.2 `json.JSONDecodeError` used without importing `json` — state_model.py:1280

**What**: `_load_manifest()` catches `json.JSONDecodeError` at line 1280, but `json` is never imported at module scope (only `re`, `dataclasses`, `Path`, `typing` are imported at lines 10-13).

**Nature**: A bare coupling constant — the exception handler references a name that doesn't exist in the local scope. If this exception is ever raised, Python will raise `NameError: name 'json' is not defined` *instead* of catching the JSON error, which would then propagate up and potentially crash the L4 gate evaluation.

**Impact**: Medium-High. The `_load_manifest` function is used in domain skill resolution. If a malformed manifest is encountered, the NameError would bypass the catch and crash the evaluation.

**Fix**: Either `import json` at module scope (it's already used in mcp_server.py) or catch `Exception` if the intent was generic error handling.

### 1.3 `aitp_fast_track_claim` bypasses all validation — mcp_server.py

**What**: The `aitp_fast_track_claim` tool creates a candidate with `status: "approved_for_promotion"` and immediately promotes it to L2, skipping L4 entirely. There is no check that the claim actually appears in peer-reviewed literature.

**Nature**: This is a symmetry violation in the trust model. The trust evolution is designed as:

```
source_grounded -> multi_source_confirmed -> validated -> independently_verified
```

Fast-track claims enter at `independently_verified` without passing through any intermediate trust levels. The skill documentation says this is for "results already validated in peer-reviewed literature," but the *code* never verifies this condition. Any agent can call `aitp_fast_track_claim` with any claim.

**Impact**: Critical. A misconfigured or hallucinating agent can inject arbitrary claims into the global L2 knowledge graph, poisoning all future topics that query it.

**Fix**: At minimum, require a `source_ref` parameter and verify the source exists in L0. Ideally, require human approval via a popup gate (like the promotion gate).

---

## 2. Systematic Inconsistencies (Broken Symmetries)

### 2.1 Skill triggers vs L3 activity names — 3-way mismatch

| Skill file | Declared trigger | Actual L3 activity in code |
|---|---|---|
| `skill-l3-analyze.md` | `l3_activity == "analysis"` | `"derive"` |
| `skill-l3-integrate.md` | `l3_activity == "result_integration"` | `"integrate"` |
| `skill-l3-distill.md` | `l3_activity == "distillation"` | `"distill"` |

**Nature**: The state_model.py `L3_ACTIVITIES` list (line 852-855) defines: `["ideate", "plan", "derive", "trace-derivation", "gap-audit", "connect", "integrate", "distill"]`. The skills use *different* names. The trigger mechanism is skill-frontend matching (the agent reads the skill based on stage/posture recommendation from the execution brief), not programmatic dispatch. So this doesn't cause a runtime crash — but it means the skill documentation is wrong about its own trigger condition, and any programmatic trigger system built on these declared triggers would fail.

**Impact**: Medium. The session_start hook recommends skills by name, so the agent loads the right file. But the trigger metadata in the frontmatter is misleading and would break any automated skill dispatch system.

**Fix**: Align the skill trigger values with the actual `L3_ACTIVITIES` entries, or change the activity names to match the skills.

### 2.2 Skill references non-existent activities

Several skills reference activities that don't exist in `L3_ACTIVITIES`:

- `skill-l3-analyze.md:51`: `aitp_switch_l3_activity(target="planning")` — actual activity is `"plan"`
- `skill-l3-analyze.md:53`: `aitp_switch_l3_activity(target="ideation")` — actual activity is `"ideate"`
- `skill-l3-integrate.md:46`: `aitp_switch_l3_activity(target="analysis")` — actual activity is `"derive"`
- `skill-l3-distill.md:47`: `aitp_switch_l3_activity(target="analysis")` — actual activity is `"derive"`
- `skill-l3-plan.md:95`: exit to `"analysis"` — actual activity is `"derive"`

**Nature**: The skill documents tell agents to call `aitp_switch_l3_activity` with invalid target names. Since `aitp_switch_l3_activity` validates against `L3_ACTIVITIES` (state_model.py:1008), these calls would return an error like "unknown activity 'analysis'. Valid: [...]".

**Impact**: High. An agent following the skill instructions literally would be unable to switch activities and would get stuck.

### 2.3 L3 subplane directory names vs activity names

The test code (`test_l3_subplanes.py:41-43`) uses subplane directory names like `"ideation"`, `"planning"`, `"analysis"`, `"result_integration"`, `"distillation"` for writing artifacts. But `L3_ACTIVITIES` has `"ideate"`, `"plan"`, `"derive"`, `"integrate"`, `"distill"`. The tests pass because they write to the directory path directly, but the gate evaluation in state_model.py looks up the active artifact path based on the activity name from `state.md` frontmatter.

**Nature**: There are two parallel naming systems. If an agent uses `"ideate"` as the activity but the artifact directory is `"ideation"`, the gate won't find the artifact. The current code works because `aitp_advance_l3_subplane` creates directories using a *mapping* from the activity name — but this mapping is implicit and fragile.

### 2.4 `aitp_get_status` always evaluates L1 gate — mcp_server.py:385

**What**: Regardless of the actual stage in `state.md`, `aitp_get_status` calls `evaluate_l1_stage`. This means L3, L4, and L5 topics get L1 gate evaluation, which checks for L1-specific artifacts (question_contract, source_basis, etc.) that may not be relevant.

**Nature**: Measuring the wrong observable. The function returns L1 gate status for topics that have long since passed L1. This produces misleading status information.

**Impact**: Medium. Agents relying on `aitp_get_status` for current-stage gate evaluation get incorrect information.

### 2.5 `aitp_health_check` only handles L0/L1/L3 — mcp_server.py:319-324

**What**: The health check dispatch table has entries for L0, L1, and L3, but not L4 or L5. Topics in L4 or L5 stages fall through to the default case, which may return incomplete health information.

### 2.6 `aitp_advance_l3_subplane` has double `@mcp.tool()` decorator — mcp_server.py:2511-2512

**What**: Two consecutive `@mcp.tool()` decorators on the same function. FastMCP may register the tool twice or behave unpredictably.

**Impact**: Low-Medium. Depends on FastMCP's duplicate registration handling.

### 2.7 `aitp_return_to_l3_from_l4` not decorated with `@mcp.tool()` — mcp_server.py:2528

**What**: The function is documented as an MCP tool and called by agents, but lacks the `@mcp.tool()` decorator. It's inaccessible via the MCP protocol.

**Impact**: Critical for L4→L3 return flow. Agents cannot invoke this tool, breaking the validation feedback loop.

---

## 3. Physical Verification Defects (Observables Mismeasured)

### 3.1 Dimensional analysis — wrong dimensions for wavefunction

In `sympy_verify.py`, the `PHYSICAL_DIMENSIONS` table assigns both `wavefunction` and `probability_density` the same dimensional tuple `(0, -1, 0, 0, 0)` (in some length-mass-time-charge-temperature basis). This is physically wrong:

- In d spatial dimensions: $[\psi] = L^{-d/2}$ and $[\psi^2] = L^{-d}$
- In 3D: $[\psi] = L^{-3/2}$ and $[\psi^2] = L^{-3}$

Having the same dimension for both means `aitp_verify_dimensions` would pass a check like $|\psi|^2 = \psi$, which is dimensionally inconsistent.

**Impact**: High for any quantum mechanics topic. The dimensional verifier gives false passes on wavefunction-related expressions.

### 3.2 Heuristic commutator evaluation — sympy_verify.py

The `_v_commutator_eval` function uses a heuristic: if an expression has "length <= 2 or contains _", it treats operators as non-commutative. This is fragile and unphysical — whether operators commute is a property of the algebra, not of the symbol name.

**Impact**: Medium. False commutativity decisions lead to incorrect algebraic verification results.

### 3.3 SymPy verification is advisory, not blocking

The L4 validation protocol (`skill-validate.md`) marks SymPy verification as "MANDATORY for pass" for `formal_theory` lanes. However, `aitp_submit_l4_review` in mcp_server.py only checks that `check_results` or `verification_evidence` is non-empty — it doesn't verify that SymPy was actually invoked. An agent can fabricate `check_results` strings without running any computation.

**Nature**: The verification protocol has a soft wall — it looks like a hard constraint but can be trivially bypassed.

---

## 4. Engineering Quality Issues (UV Divergences and IR Redundancies)

### 4.1 Massive code duplication

| Duplication | Files | Lines |
|---|---|---|
| `_parse_frontmatter()` | hooks/session_start.py:89, hooks/stop.py:18 | Identical 12-line function |
| `_parse_md()` | hooks/session_start.py:105, hooks/stop.py:34, brain/mcp_server.py | Three copies |
| `_find_workspace_root()` | hooks/session_start.py:41, hooks/stop.py:67 | Identical |
| `_find_topics_root()` | hooks/session_start.py:56, hooks/stop.py:92 | Identical |
| `_read_aitp_config()` | hooks/session_start.py:21, hooks/stop.py:81 | Identical |
| `_find_active_topic()` | hooks/session_start.py:118, hooks/stop.py:115 | Identical |
| `_hooks_disabled()` | hooks/session_start.py:33, hooks/stop.py:183 | Identical |
| `_load_manifest()` | brain/state_model.py:1264 (one implementation) | Not duplicated, but earlier summary said it was — verified it's only in state_model.py |
| L3_ARTIFACT_TEMPLATES assignment | state_model.py:959 and :981 | Same value, twice |

The hooks should import from a shared utility module. The current structure means any fix must be applied in multiple places.

### 4.2 O(n^2) I/O in `_suggest_related_concepts` — mcp_server.py

**What**: Inside a list comprehension over all L2 nodes, the function re-reads each node file from disk. For N nodes, this is N file reads inside an N-iteration loop — O(N^2) disk I/O.

**Impact**: Performance degrades quadratically as L2 grows. With 100 nodes, 10,000 file reads. With 1000 nodes, 1,000,000.

### 4.3 Thread-unsafe global state in l2_embedding.py

**What**: `_FITTED_VOCAB` is a module-level mutable dict. If two MCP tool calls run concurrently (e.g., in async context), they race on this shared state.

**Impact**: Low in single-threaded MCP usage, but latent bug for any concurrent deployment.

### 4.4 Dead code: L5 writing

**What**: `aitp_get_execution_brief` states "L5 writing removed in v4.0" (deploy templates). But:
- `evaluate_l5_stage` still exists in state_model.py
- `aitp_advance_to_l5` still exists in mcp_server.py
- Bootstrap creates `L5_writing/` directories
- `test_e2e_scenario_a.py` tests L5 advancement and verifies L5_writing scaffold creation
- `skill-promote.md` mentions "start writing (L5, skill-write)"

**Nature**: The theory says L5 is removed; the code still creates and evaluates it. This is a Schrodinger's feature — simultaneously present and absent depending on which file you read.

**Impact**: Confusing for maintainers. Tests verify behavior that the documentation says doesn't exist.

### 4.5 Compact hook missing L4/L5 evaluation — hooks/compact.py:47-52

**What**: The compact hook only evaluates L0, L1, L3 stages. L4 and L5 fall through to `evaluate_l1_stage` as default, while session_start.py correctly handles all five stages. After compaction, the agent gets wrong stage information for L4/L5 topics.

### 4.6 Deleted schemas still referenced

Six schema files were deleted:
- `benchmark-report.schema.json`
- `calculation-debug.schema.json`
- `computation-workflow.schema.json`
- `compute-resource.schema.json`
- `development-task.schema.json`

But references persist in:
- `contracts/` directory (5 files with matching names)
- `research/knowledge-hub/` documentation
- `AUDIT_REPORT.md` and `DEEPSEEK_PROMPTS.md`

### 4.7 Flow TeX section is empty — mcp_server.py

The `_auto_refresh_flow_notebook` function is called in multiple places but the TeX generation section (lines 2682-2686) is empty — it generates a file with headers but no physics content.

---

## 5. Test Coverage Gaps (Unmeasured Observables)

The test suite covers:
- L0/L1 bootstrap and gates (test_state_model, test_io_contracts)
- L3 subplane traversal (test_l3_subplanes)
- L4 review outcomes (test_l4_l2_memory)
- Promotion gate lifecycle (test_foundation_safety)
- E2E scenario A (test_e2e_scenario_a)
- Conflict resolution, order estimation, LaTeX search (test_io_contracts)

Not tested:
- **SymPy verification**: No tests for `sympy_verify.py` at all. The dimensional analysis, algebraic verification, limit checking, and derivation step validation are completely untested.
- **Semantic search**: Only a minimal test for LaTeX alias existence and a single query. The full search pipeline (tokenization, embedding, scoring) is untested.
- **L2 embedding**: The TF-IDF-like vector system in l2_embedding.py has no tests.
- **Domain skill resolution**: `_load_manifest` and domain skill detection paths are untested.
- **Hooks edge cases**: No tests for session_start with malformed state.md, missing config, or concurrent access.
- **Fast-track claim bypass**: No test verifying that fast-track actually requires evidence.
- **Error paths**: Most MCP tool error paths (invalid slugs, missing files, corrupted YAML) are untested.

---

## 6. Deploy Template Issues

### 6.1 Template rendering of `{{TOPICS_ROOT}}` — using-aitp.md and aitp-runtime.md

The deploy templates use `{{TOPICS_ROOT}}` as a placeholder, but there's no template engine in the codebase that substitutes these values. The `aitp-routing-guard.py` and `aitp-keyword-router.py` also hardcode `{{TOPICS_ROOT}}`. If these files are deployed without template rendering, the placeholder string is used as a literal path.

### 6.2 Keyword router has overly broad triggers — aitp-keyword-router.py

The AITP_KEYWORDS list includes very common words like "research", "topic", and single Chinese characters like "拓扑" (topology). This means nearly any physics-related conversation triggers AITP routing, even for casual questions that don't need the full protocol.

---

## 7. Architectural Observations (Renormalization Concerns)

### 7.1 Monolithic mcp_server.py

At ~3800+ lines, `mcp_server.py` is the largest file and contains 40+ tool functions, file I/O utilities, gate evaluation helpers, flow notebook generation, and configuration management. This is beyond the maintainability threshold for a single file. Consider splitting into:
- `brain/tools/` — one module per tool group (source tools, candidate tools, L2 tools, etc.)
- `brain/io.py` — `_parse_md`, `_write_md`, `_atomic_write_text`
- `brain/gates.py` — gate evaluation helpers

### 7.2 No transaction semantics across artifact writes

When advancing stages, multiple files are written (state.md, artifact files, log entries). If the process crashes mid-write, the topic can be left in an inconsistent state (e.g., state.md says L3 but the L3 directories don't exist). The atomic write function protects individual files but not multi-file transactions.

### 7.3 Popup gates returned as dicts, not enforced

Popup gates (user decision points) are returned as Python dicts in the tool response. The agent is expected to check for `popup_gate` keys and call `AskUserQuestion`. But there's no enforcement — an agent can ignore the popup gate and proceed. The gate is a social convention, not a technical constraint.

---

## 8. Priority Ranking for Fixes

| Priority | Issue | Effort | Risk |
|---|---|---|---|
| P0 | 1.3 fast_track bypasses validation | S | Trust poisoning |
| P0 | 2.7 return_to_l3_from_l4 undecorated | S | L4 feedback loop broken |
| P0 | 1.1 duplicate _get_l3_config | S | Silent L3 gate corruption |
| P1 | 2.1-2.3 skill trigger / activity name mismatches | M | Agent stuck in L3 |
| P1 | 3.1 wavefunction dimensions | S | False dimensional passes |
| P1 | 1.2 missing json import | S | NameError on malformed manifest |
| P1 | 4.5 compact hook missing L4/L5 | S | Wrong state after compaction |
| P2 | 2.4 get_status wrong gate evaluation | S | Misleading status |
| P2 | 2.6 double decorator | S | Potential double registration |
| P2 | 4.2 O(n^2) related concepts | M | Performance at scale |
| P2 | 4.1 code duplication in hooks | M | Maintenance burden |
| P2 | 4.4 dead L5 code | M | Confusion |
| P3 | 5.x test coverage gaps | L | Regressions |
| P3 | 7.1 monolithic mcp_server | L | Maintainability |

**S** = small (hours), **M** = medium (days), **L** = large (week+)

---

## 9. Conclusion

The AITP protocol's *design* — layered gates, trust evolution, adversarial validation, source-grounded derivation — is well-conceived and reflects genuine understanding of how theoretical physics research should be structured. The *implementation* has the character of a rapidly-evolved research code: the core state machine works, but it has accumulated inconsistencies at the interfaces between modules (skill triggers, activity names, gate evaluations) and has several latent bugs in error paths. The three P0 issues (fast-track bypass, undecorated tool, duplicate definition) should be fixed immediately as they represent actual failure modes. The naming mismatches (Section 2) are the most pervasive class of bug and suggest a refactoring where the L3 activity names were changed without updating all references — a systematic sweep would resolve most of them at once.
