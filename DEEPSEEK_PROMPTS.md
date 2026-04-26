# DeepSeek Execution Prompts

These are self-contained prompts for DeepSeek to execute each batch of modifications.
Each prompt includes full context and exact file references so DeepSeek can work independently.

---

## Prompt 1: Fix Harness Chain (Batch 1 — URGENT)

```
You are modifying the AITP Research Protocol repository at D:\BaiduSyncdisk\repos\AITP-Research-Protocol.
The repo is a FastMCP-based MCP server for structured theoretical physics research.

## Context

We recently added a domain skill system. The core detection logic is in `brain/state_model.py`:
- `resolve_domain_prerequisites(topic_root_path: Path, topic_slug: str = "") -> list[str]`
  Detects domains via 3 tiers: contracts manifest files -> state.md frontmatter `domains` field -> slug pattern fallback.
  Returns a list of skill filenames like `["skill-librpa"]`.

- `DOMAIN_ID_TO_SKILL: dict[str, str] = {"abacus-librpa": "skill-librpa"}`
- `_detect_domains_from_contracts(topic_root_path: Path) -> list[str]` — supports both `.md` and `.json` manifests

The main MCP server is `brain/mcp_server.py`. The function `aitp_get_execution_brief` already calls
`resolve_domain_prerequisites(root, topic_slug)` and includes `domain_prerequisites` in all 5 return branches.

However, there are critical gaps in the harness chain where domain skills are never loaded by agents.

## Task 1.1: Update deploy templates to include domain skill loading

File: `deploy/templates/claude-code/using-aitp.md`
File: `deploy/templates/kimi-code/using-aitp.md`

Both files have an "Entry procedure" section with Steps 1-5. Between Step 3 ("Get execution brief")
and Step 5 ("Follow the brief"), insert a new step:

```
### Step 3.5: Load domain prerequisites

If the execution brief's `domain_prerequisites` field is non-empty, load each listed skill file
from `skills/` BEFORE loading the stage skill. Domain skills provide domain-specific knowledge
(workflow lanes, invariants, validation criteria) that must be understood before stage work begins.

Example: if `domain_prerequisites: ["skill-librpa"]`, read `skills/skill-librpa.md` first.
```

Also update the "Skill activation" section. It currently says:
```
1. Check `domain_prerequisites` — if non-empty, load those skills FIRST.
```
Keep this text, but make sure it's prominent (not just a bullet point).

File: `deploy/templates/claude-code/aitp-runtime.md`
File: `deploy/templates/kimi-code/aitp-runtime.md`

In the decision loop that matches on `brief.stage` and loads the stage skill, add BEFORE the stage
matching:

```
# Domain prerequisites (load before stage skill)
if brief.get("domain_prerequisites"):
    for skill_name in brief["domain_prerequisites"]:
        read_file(f"skills/{skill_name}.md")
```

## Task 1.2: Add domain_prerequisites to aitp_session_resume

File: `brain/mcp_server.py`

Find the function `aitp_session_resume` (around line 1858-1920). It currently returns a dict with
stage, posture, lane, l3_mode, l3_subplane, gate_status, skill, required_artifact_path,
missing_requirements, instruction — but NO domain_prerequisites.

Changes needed:
1. At the top of the function, after computing `root = _topic_root(topics_root, topic_slug)`:
   ```python
   domain_prereqs = resolve_domain_prerequisites(root, topic_slug)
   ```
2. Add `"domain_prerequisites": domain_prereqs` to the return dict.
3. Add `_agent_behavior_reminder` to the return dict (it's missing here but present in
   `aitp_get_execution_brief`).
4. Update the `instruction` field to mention: "If domain_prerequisites is non-empty, load those
   skills from skills/ before the stage skill."

Make sure `resolve_domain_prerequisites` is imported at the top of mcp_server.py (it should already be).

## Task 1.3: Consolidate manifest loaders

Currently there are THREE manifest-loading functions:

1. `_detect_domains_from_contracts(topic_root_path: Path) -> list[str]` in `state_model.py` (~line 48)
   Supports both `.md` and `.json` formats. Returns domain_id strings.

2. `_load_manifest(topic_root_path: Path) -> dict` in `state_model.py` (~line 1096)
   Only reads `.md`. Used by `evaluate_l4_stage` for invariant checking.

3. `_load_domain_manifest(topic_root_path: Path) -> dict` in `mcp_server.py` (~line 200)
   Only reads `.md`. Used by `aitp_get_status` and `aitp_load_domain_manifest`.

Changes needed:

In `state_model.py`:
- Create a new function `load_domain_manifest(topic_root_path: Path) -> dict | None` that:
  1. First tries `contracts/domain-manifest.md` (parse YAML frontmatter, return as dict)
  2. If not found, tries `contracts/domain-manifest.*.json` (glob, parse first match as JSON)
  3. Returns None if neither exists
- Keep `_detect_domains_from_contracts()` as-is (it extracts domain_ids, not full manifest data)
- Replace `_load_manifest()` body with a call to the new `load_domain_manifest()`

In `mcp_server.py`:
- Import `load_domain_manifest` from state_model
- Replace `_load_domain_manifest()` body with a call to the imported `load_domain_manifest()`
- Update all call sites that used `_load_domain_manifest()` to use the imported version

This ensures ALL code paths (execution brief, session resume, get_status, L4 invariant check,
load_domain_manifest tool) support both `.md` and `.json` manifest formats.

## Task 1.4: Update aitp_get_status

File: `brain/mcp_server.py`

Find `aitp_get_status` (around line 380-410). Currently it does:
```python
manifest = _load_domain_manifest(root)
...
"domain_skill": manifest.get("domain_id", "") if manifest else "",
```

Change to:
```python
domain_prereqs = resolve_domain_prerequisites(root, topic_slug)
manifest = load_domain_manifest(root)
...
"domain_prerequisites": domain_prereqs,
"domain_skill": manifest.get("domain_id", "") if manifest else "",
```

Keep both fields for backward compatibility. `domain_prerequisites` is the actionable field
(list of skill filenames). `domain_skill` is informational (the domain_id string).

## Task 1.5: Add domain section to PROTOCOL.md

File: `brain/PROTOCOL.md`

After the section that defines Stage, Posture, and Lane, add a new section:

```markdown
### Domain Skills

Domain skills inject domain-specific knowledge (workflow lanes, invariants, validation criteria)
into the research process. They are orthogonal to lanes:

- **Lane** determines HOW research is conducted (formal_theory, toy_numeric, code_method).
- **Domain skill** determines WHAT domain-specific knowledge is needed (abacus-librpa, vasp, qe, etc.).
- Domain skills are currently only relevant for `code_method` lane topics. This is a design choice,
  not a fundamental limitation.

#### Detection (priority order)

1. `contracts/domain-manifest.md` or `contracts/domain-manifest.<id>.json` in the topic directory
2. `domains: [<id>]` in `state.md` frontmatter
3. Legacy slug-pattern fallback

The execution brief's `domain_prerequisites` field lists skill filenames to load. Agents must
load these BEFORE the stage skill.

#### Disambiguation

"L2 domain" in the knowledge graph refers to physics subject areas (electronic-structure,
quantum-many-body, etc.). "Domain skill" refers to code/workflow specializations (abacus-librpa,
etc.). These are different concepts.
```

## Verification

After making all changes:
1. Run `python -c "from brain.state_model import resolve_domain_prerequisites, load_domain_manifest; print('imports OK')"`
2. Run `python -c "from brain.mcp_server import *; print('mcp_server imports OK')"`
3. Run `pytest tests/ -x --tb=short` and report results

Do NOT modify any test files. Report any test failures.
```

---

## Prompt 2: Generalize Contract Schemas (Batch 2.1 — HIGH)

```
You are modifying the AITP Research Protocol repository at D:\BaiduSyncdisk\repos\AITP-Research-Protocol.

## Context

AITP has JSON Schema files in `schemas/` that define contract structures. Several of these schemas
are hardcoded to ABACUS+LibRPA specifics, which blocks adding new first-principles code domains
(VASP, Quantum ESPRESSO, ABINIT, GPAW, etc.).

The domain skill system uses `contracts/domain-manifest.<domain_id>.json` files to declare domain-
specific operations, invariants, and stage definitions. Contract schemas should accept values from
any domain, not just ABACUS+LibRPA.

## Task: Generalize 4 contract schemas

### 2.1a: `schemas/computation-workflow.schema.json`

Changes:
1. `description`: Change from "GW or RPA with ABACUS and LibRPA" to "Computational workflow for first-principles calculations"
2. `computation_type` enum: Change from `["gw", "rpa"]` to open string (remove enum, keep type: string). Add a comment that valid values are defined by the domain manifest.
3. `stages[].name` enum: Change from `["scf", "df", "nscf", "librpa", "postprocess"]` to open string. Stage names are domain-specific.
4. `basis_integrity`: Remove `shrink_invariant` (ABACUS-NAO specific) and `nao_orbitals` (ABACUS-NAO specific). Replace with a generic `domain_integrity` object: `{"type": "object", "description": "Domain-specific integrity checks, defined by domain manifest"}`
5. Keep all other fields as-is.

### 2.1b: `schemas/compute-resource.schema.json`

Changes:
1. Remove hardcoded code paths: `abacus_path`, `librpa_path`, `libri_path`.
2. Replace with: `executable_paths: {"type": "object", "additionalProperties": {"type": "string"}, "description": "Map of code name to executable path, e.g. {\"abacus\": \"/path/to/abacus\"}"}`
3. Keep `conda_env` but remove pyatb reference from description.
4. Keep all other fields as-is.

### 2.1c: `schemas/development-task.schema.json`

Changes:
1. `target` enum: Change from `["abacus", "librpa", "libri", "libcomm", "pyatb", "other"]` to open string. Target codes are defined by the domain.
2. `build_config.toolchain` enum: Expand to `["gnu", "intel", "intel-oneapi", "llvm", "nvhpc", "cray", "other"]`
3. `description`: Remove "for ABACUS, LibRPA, LibRI, or related" reference.

### 2.1d: `schemas/calculation-debug.schema.json`

Changes:
1. `failure_stage` enum: Change from `["scf", "df", "nscf", "librpa", "postprocess"]` to open string. Stage names are domain-specific.

### 2.1e: `schemas/benchmark-report.schema.json` (minor)

Changes:
1. `system_type` enum: Expand from `["molecule", "solid", "2D"]` to include `"surface"`, `"nanotube"`, `"cluster"`, `"liquid"`, `"interface"`, `"other"`.

## Verification

After changes, validate each schema:
```bash
python -c "
import json
for name in ['computation-workflow', 'compute-resource', 'development-task', 'calculation-debug', 'benchmark-report']:
    with open(f'schemas/{name}.schema.json') as f:
        s = json.load(f)
    print(f'{name}: OK ({len(s.get(\"properties\", {}))} properties)')
"
```

Check that existing test fixtures in tests/ still pass. Run `pytest tests/ -x --tb=short`.
```

---

## Prompt 3: Split Playbook and Lane Protocol (Batch 2.2-2.3 — HIGH)

```
You are modifying the AITP Research Protocol repository at D:\BaiduSyncdisk\repos\AITP-Research-Protocol.

## Context

Two documents are currently LibRPA-specific but should have their generic patterns extracted:

1. `research/knowledge-hub/FEATURE_DEVELOPMENT_PLAYBOOK.md` — A 9-phase feature development playbook
   that is structurally universal but has LibRPA-specific walkthrough examples mixed in.

2. `research/knowledge-hub/FIRST_PRINCIPLES_LANE_PROTOCOL.md` — An entire document specific to
   ABACUS+LibRPA that contains universal patterns (interaction loops, routing strategies, invariant
   frameworks, validation standards).

## Task 3.1: Refactor FEATURE_DEVELOPMENT_PLAYBOOK.md

Read the file carefully. Identify:

**Universal content (keep in playbook):**
- 9-phase structure (P, 0-7)
- Gate definitions (G0-G5)
- Derive-first discipline (Phase 1)
- Human interaction protocol
- Development planning structure (Phase 2)
- Debug loop structure (Phase 6)
- Production readiness structure (Phase 7)
- Error classification taxonomy (the categories like convergence_failure, input_mismatch,
  resource_exhaustion, numerical_instability, basis_incompatibility, toolchain_error are universal)
- Contract usage table (mapping phases to contracts)

**LibRPA-specific content (move to domain appendix):**
- Title and description referencing "ABACUS, LibRPA, LibRI, LibComm, pyatb"
- All walkthrough examples with specific file paths (STRU, KPT, INPUT_scf, librpa.in, OUT.ABACUS/)
- Quick Reference: Failure Recovery table (keep the structure but replace specifics with placeholders)
- Any ABACUS/LibRPA-specific step details

Restructure the file as:
1. Main body: universal playbook template with generic placeholders for domain-specific details
2. Appendix A: ABACUS+LibRPA domain specialization (the extracted LibRPA-specific content)

At the top of the file, add a note:
```
This playbook defines the generic feature development lifecycle for first-principles code in the
`code_method` lane. Domain-specific details are provided by domain skills (loaded via
`domain_prerequisites` in the execution brief) and documented in the appendix.
```

## Task 3.2: Create generic FIRST_PRINCIPLES_LANE_PROTOCOL template

Read `research/knowledge-hub/FIRST_PRINCIPLES_LANE_PROTOCOL.md`.

Create a new file `research/knowledge-hub/FIRST_PRINCIPLES_LANE_PROTOCOL.md` (overwrite) with:

1. Generic template containing:
   - Sub-domain concept (computation vs. development) — universal
   - Interaction loop (development -> build -> benchmark -> computation -> debug) — universal
   - L0 knowledge classification taxonomy structure — universal concept
   - Routing strategy (intent-based, input-based, mode-based) — universal
   - Invariant checking framework structure — universal pattern
   - Validation standards structure — universal
   - Rules for future changes — universal meta-protocol

2. Appendix: "ABACUS+LibRPA Domain Instantiation" containing:
   - Section 1 (domain identity table) — LibRPA-specific
   - Section 4.1 (specific operation families) — LibRPA-specific
   - Section 5 (specific file patterns: STRU, librpa.in, *.upf) — LibRPA-specific
   - Section 7 (specific invariant definitions) — LibRPA-specific
   - Section 12 (SOC and symmetry constraints) — LibRPA-specific

At the top, add:
```
This protocol defines the generic first-principles code development lane within `code_method`.
It is not an independent lane. It is a domain-specific protocol layer whose concrete instantiation
is provided by domain skills (loaded via `domain_prerequisites` in the execution brief).
```

## Task 3.3: Fix AITP_SPEC.md

File: Find `AITP_SPEC.md` in the repository.

Find line ~474 where it says:
```
| lane | Research domain | formal_theory, model_numeric, code_and_materials |
```

Change to:
```
| lane | Research methodology | formal_theory, toy_numeric, code_method |
```

Also search for any other occurrences of `model_numeric` or `code_and_materials` in the file and
update them to `toy_numeric` and `code_method` respectively.

## Verification

1. Check all modified files are valid Markdown (no broken formatting)
2. Run `pytest tests/ -x --tb=short` and report results
3. Do NOT modify test files
```

---

## Prompt 4: Promote Universal Patterns (Batch 3 — MEDIUM)

```
You are modifying the AITP Research Protocol repository at D:\BaiduSyncdisk\repos\AITP-Research-Protocol.

## Context

The domain skill `skills/skill-librpa.md` contains patterns that are universal for ANY first-
principles code, not just LibRPA. These should be promoted to the protocol level so all domains
inherit them automatically.

## Task 4.1: Add smoke test framework to skill-l3-plan.md

File: `skills/skill-l3-plan.md`

This file already has a "Computational Environment (MANDATORY for toy_numeric and code_method lanes)"
section. Add after it:

```markdown
### Smoke Test Gate (MANDATORY for code_method lane)

Before any expensive validation run, define and pass a smoke test:

1. **Define minimal test system**: smallest possible system that exercises the full pipeline
2. **Pass criteria**: all stages complete without NaN, expected output files exist
3. **Mandatory order**: smoke test MUST pass before full calculation begins

The specific test system and pass criteria are defined by the domain skill.
Example: for LibRPA, bulk Si 2×2×2 with low ecutwfc; for VASP, a simple bulk calculation.
```

## Task 4.2: Add invariant checking framework to skill-validate.md

File: `skills/skill-validate.md`

Find the section about validation evidence requirements. Add:

```markdown
### Domain Invariant Verification

For topics with domain skills (domain_prerequisites non-empty), verify ALL domain invariants
before submitting `outcome="pass"`:

1. Load the domain manifest from the topic's `contracts/` directory
2. Check each invariant in the manifest's `invariants` list
3. Record pass/fail for each invariant explicitly
4. If ANY invariant fails, the validation outcome must be `fail` or `partial_pass`

Invariant definitions and check methods are provided by the domain skill.
```

## Task 4.3: Add escape hatch patterns to skill-validate.md

In the same file, add to the escape hatches section:

```markdown
### Domain Skill Escape Hatches

Common escape hatches for domain-specific validation:

1. **Domain manifest missing**: Clone from upstream, copy into topic's `contracts/`, register via
   `aitp_register_source`. Record the resolution.
2. **formal_theory lane**: Domain invariant checks are advisory, not blocking.
3. **User override ("skip domain checks")**: Record the skip, mark validation as `partial_pass`
   rather than `pass`.
```

## Task 4.4: Update skill-librpa.md to reference promoted patterns

File: `skills/skill-librpa.md`

In the "This skill is additive" section, add to the list of protocol-level concerns:

```
- Smoke test framework -> skill-l3-plan.md
- Invariant checking framework -> skill-validate.md
- Escape hatch patterns -> skill-validate.md
```

And update the specific sections to note they are instantiations of the protocol-level patterns:

- Smoke Test Criteria: add "This is the LibRPA instantiation of the protocol-level smoke test framework."
- Domain Invariants: add "These are the LibRPA instances of the protocol-level invariant checking framework."
- Escape Hatches: add "These extend the protocol-level escape hatch patterns."

## Verification

1. Read all modified files to confirm no formatting issues
2. Run `pytest tests/ -x --tb=short`
3. Do NOT modify test files
```

---

## Execution Order

| Prompt | Batch | Priority | Estimated Complexity |
|--------|-------|----------|---------------------|
| 1 | Batch 1: Fix Harness | URGENT | High (5 files, mcp_server.py has ~4700 lines) |
| 2 | Batch 2.1: Schemas | HIGH | Medium (5 JSON files) |
| 3 | Batch 2.2-2.3: Docs | HIGH | High (2 large markdown files + SPEC) |
| 4 | Batch 3: Patterns | MEDIUM | Low (3 skill files) |

**Recommended execution**: Run Prompt 1 first (fixes the non-functional harness), then Prompts 2-4 can run in any order or in parallel.
