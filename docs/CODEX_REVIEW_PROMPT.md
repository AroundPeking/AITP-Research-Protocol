# AITP v2 Architecture Review — Full Context Prompt

Copy everything below the line and paste into Codex.

---

You are reviewing the AITP v2 architecture — a research protocol for AI-assisted theoretical physics. It was recently rewritten from a Python-heavy v1 to a minimal, skill-driven v2. Your job: find bugs, gaps, design problems, and suggest improvements. Be specific. Cite line numbers when relevant.

## Authority Hierarchy

```
CHARTER.md > AITP_SPEC.md > sub-protocols > implementation
```

## Architecture Overview

**Core idea**: Brain (MCP server) provides tools. Skills (Markdown) provide wisdom. Agent provides execution. All storage is Markdown with YAML frontmatter. No JSON, no JSONL.

**Layer model**: L0 (source) → L1 (intake) → L3 (derive/candidate) → L4 (validate) → L2 (promote) → L5 (write PDF)

**Status → Skill mapping**:
```
new                → skill-explore
sources_registered → skill-intake
intake_done        → skill-derive
candidate_ready    → skill-validate
validated          → skill-promote
promoted           → skill-write
complete           → (done)
blocked            → read state.md
any (after break)  → skill-continuous
```

**Topic directory structure** (created by aitp_bootstrap_topic):
```
topics/<slug>/
  state.md              # YAML frontmatter: status, mode, layer, timestamps
  L0/sources/*.md       # source metadata
  L1/intake/*.md        # per-source analysis
  L2/canonical/*.md     # promoted knowledge
  L3/derivations.md     # append-only derivation log
  L3/candidates/*.md    # formal candidates
  L4/reviews/*.md       # validation reviews
  L5_writing/           # paper output
    draft.tex, references.bib, figures/, tables/, outline.md
  runtime/              # internal state
```

## Known Issues (already identified, not yet fixed)

1. **L2 is per-topic, should be global**: Physics knowledge accumulates across topics. Currently each topic has its own L2/. Should be a shared global L2 at topics_root level, with subdirs: canonical/, notation/, conventions/, methods/, lessons/
2. **No notation lock before derivation**: Intake records notation but doesn't lock conventions before L3 begins
3. **No physics-specific validation**: skill-validate lacks conservation law checks, correspondence principle, thermodynamic consistency, symmetry constraints
4. **No approximation discipline in derive**: Derivation steps don't track approximation type, validity regime, or dimensional consistency
5. **skill-continuous still references aitp_get_popup** which was removed

---

## FILE: brain/mcp_server.py (full content)

```python
"""AITP Brain MCP Server v2 — Minimal skill-driven research protocol.

Provides ~10 tools for the agent to read/write topic state.
All storage is Markdown with YAML frontmatter. No JSON, no JSONL.

Dependencies: fastmcp, pyyaml
Install: pip install fastmcp pyyaml
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from fastmcp import FastMCP

mcp = FastMCP("aitp-brain")


# ---------------------------------------------------------------------------
# Helpers — Markdown + YAML frontmatter I/O
# ---------------------------------------------------------------------------

_FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)


def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _topic_root(topics_root: str, topic_slug: str) -> Path:
    root = Path(topics_root) / topic_slug
    if not root.is_dir():
        raise FileNotFoundError(f"Topic not found: {topic_slug}")
    return root


def _parse_md(path: Path) -> tuple[dict[str, Any], str]:
    if not path.exists():
        return {}, ""
    text = path.read_text(encoding="utf-8")
    m = _FM_RE.match(text)
    if not m:
        return {}, text
    import yaml
    fm = yaml.safe_load(m.group(1)) or {}
    return fm, m.group(2)


def _write_md(path: Path, fm: dict[str, Any], body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    import yaml
    frontmatter = yaml.dump(fm, default_flow_style=False, allow_unicode=True).strip()
    path.write_text(f"---\n{frontmatter}\n---\n{body}\n", encoding="utf-8")


def _append_section(path: Path, section: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if existing and not existing.endswith("\n"):
        existing += "\n"
    path.write_text(existing + section + "\n", encoding="utf-8")


def _slugify(text: str) -> str:
    s = text.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-") or "untitled"


# ---------------------------------------------------------------------------
# Skill injection logic
# ---------------------------------------------------------------------------

_SKILL_MAP = {
    "new": "skill-explore",
    "sources_registered": "skill-intake",
    "intake_done": "skill-derive",
    "candidate_ready": "skill-validate",
    "validated": "skill-promote",
    "promoted": "skill-write",
}

_VALID_STATUSES = set(_SKILL_MAP.keys()) | {"complete", "blocked"}


def _infer_status(fm: dict[str, Any], topic_root: Path) -> str:
    explicit = str(fm.get("status") or "").strip()
    if explicit and explicit in _VALID_STATUSES:
        return explicit
    # Infer from filesystem state
    src_dir = topic_root / "L0" / "sources"
    intake_dir = topic_root / "L1" / "intake"
    cand_dir = topic_root / "L3" / "candidates"
    l2_dir = topic_root / "L2" / "canonical"
    if src_dir.is_dir() and list(src_dir.glob("*.md")):
        if intake_dir.is_dir() and list(intake_dir.glob("*.md")):
            if cand_dir.is_dir() and list(cand_dir.glob("*.md")):
                return "candidate_ready"
            return "intake_done"
        return "sources_registered"
    return "new"


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------


@mcp.tool()
def aitp_get_status(topics_root: str, topic_slug: str) -> dict[str, Any]:
    """Read topic state and return current status, mode, layer, and counts."""
    root = _topic_root(topics_root, topic_slug)
    fm, body = _parse_md(root / "state.md")
    status = _infer_status(fm, root)
    src_dir = root / "L0" / "sources"
    intake_dir = root / "L1" / "intake"
    cand_dir = root / "L3" / "candidates"
    l2_dir = root / "L2" / "canonical"
    return {
        "topic_slug": topic_slug,
        "status": status,
        "mode": fm.get("mode", "explore"),
        "layer": fm.get("layer", "L0"),
        "title": fm.get("title", topic_slug),
        "sources_count": len(list(src_dir.glob("*.md"))) if src_dir.is_dir() else 0,
        "intake_count": len(list(intake_dir.glob("*.md"))) if intake_dir.is_dir() else 0,
        "candidates_count": len(list(cand_dir.glob("*.md"))) if cand_dir.is_dir() else 0,
        "l2_count": len(list(l2_dir.glob("*.md"))) if l2_dir.is_dir() else 0,
        "updated_at": fm.get("updated_at", ""),
    }


@mcp.tool()
def aitp_update_status(
    topics_root: str,
    topic_slug: str,
    status: str | None = None,
    mode: str | None = None,
    layer: str | None = None,
) -> str:
    """Update topic state.md frontmatter fields."""
    root = _topic_root(topics_root, topic_slug)
    state_path = root / "state.md"
    fm, body = _parse_md(state_path)
    if status:
        fm["status"] = status
    if mode:
        fm["mode"] = mode
    if layer:
        fm["layer"] = layer
    fm["updated_at"] = _now()
    _write_md(state_path, fm, body)
    return f"Updated {topic_slug}: status={fm.get('status')}, mode={fm.get('mode')}, layer={fm.get('layer')}"


@mcp.tool()
def aitp_bootstrap_topic(
    topics_root: str,
    topic_slug: str,
    title: str,
    question: str,
) -> str:
    """Create a new topic directory structure with state.md."""
    root = Path(topics_root) / topic_slug
    if root.exists():
        return f"Topic {topic_slug} already exists."
    root.mkdir(parents=True)
    for sub in ["L0/sources", "L1/intake", "L2/canonical", "L3/candidates", "L4/reviews", "L5_writing/figures", "L5_writing/tables", "runtime"]:
        (root / sub).mkdir(parents=True)
    fm = {
        "topic_slug": topic_slug,
        "title": title,
        "status": "new",
        "mode": "explore",
        "layer": "L0",
        "created_at": _now(),
        "updated_at": _now(),
        "sources_count": 0,
        "candidates_count": 0,
    }
    body = f"# {title}\n\n## Research Question\n{question}\n"
    _write_md(root / "state.md", fm, body)
    return f"Bootstrapped topic {topic_slug} at {root}"


@mcp.tool()
def aitp_register_source(
    topics_root: str,
    topic_slug: str,
    source_id: str,
    source_type: str = "paper",
    title: str = "",
    arxiv_id: str = "",
    fidelity: str = "arxiv_preprint",
    notes: str = "",
) -> str:
    """Register a source in L0. Creates a Markdown file with frontmatter."""
    root = _topic_root(topics_root, topic_slug)
    slug = _slugify(source_id)
    path = root / "L0" / "sources" / f"{slug}.md"
    if path.exists():
        return f"Source {slug} already registered."
    fm = {
        "source_id": slug,
        "type": source_type,
        "title": title or source_id,
        "arxiv_id": arxiv_id,
        "fidelity": fidelity,
        "registered": _now(),
    }
    body = f"# {title or source_id}\n\n{notes}\n" if notes else f"# {title or source_id}\n"
    _write_md(path, fm, body)
    return f"Registered source {slug}"


@mcp.tool()
def aitp_list_sources(topics_root: str, topic_slug: str) -> list[dict[str, Any]]:
    """List all registered sources for a topic."""
    root = _topic_root(topics_root, topic_slug)
    src_dir = root / "L0" / "sources"
    if not src_dir.is_dir():
        return []
    results = []
    for path in sorted(src_dir.glob("*.md")):
        fm, _ = _parse_md(path)
        results.append({"source_id": fm.get("source_id", path.stem), "title": fm.get("title", ""), "type": fm.get("type", ""), "arxiv_id": fm.get("arxiv_id", "")})
    return results


@mcp.tool()
def aitp_record_derivation(
    topics_root: str,
    topic_slug: str,
    derivation_id: str,
    kind: str,
    title: str,
    status: str = "in_progress",
    source: str = "",
    content: str = "",
) -> str:
    """Append a derivation record to L3/derivations.md."""
    root = _topic_root(topics_root, topic_slug)
    deriv_path = root / "L3" / "derivations.md"
    section = (
        f"\n## {title}\n\n"
        f"- id: {derivation_id}\n"
        f"- kind: {kind}\n"
        f"- status: {status}\n"
        f"- source: {source}\n"
        f"- recorded: {_now()}\n\n"
        f"{content}\n"
    )
    _append_section(deriv_path, section)
    return f"Recorded derivation {derivation_id}"


@mcp.tool()
def aitp_submit_candidate(
    topics_root: str,
    topic_slug: str,
    candidate_id: str,
    title: str,
    claim: str,
    evidence: str = "",
    assumptions: str = "",
    validation_criteria: str = "",
) -> str:
    """Submit a candidate finding. Creates L3/candidates/<id>.md."""
    root = _topic_root(topics_root, topic_slug)
    slug = _slugify(candidate_id)
    path = root / "L3" / "candidates" / f"{slug}.md"
    fm = {
        "candidate_id": slug,
        "title": title,
        "status": "submitted",
        "mode": "candidate",
        "created_at": _now(),
        "updated_at": _now(),
    }
    body = (
        f"# {title}\n\n"
        f"## Claim\n{claim}\n\n"
        f"## Evidence\n{evidence}\n\n"
        f"## Assumptions\n{assumptions}\n\n"
        f"## Validation Criteria\n{validation_criteria}\n"
    )
    _write_md(path, fm, body)
    return f"Submitted candidate {slug}"


@mcp.tool()
def aitp_promote_candidate(
    topics_root: str,
    topic_slug: str,
    candidate_id: str,
    comment: str = "",
) -> str:
    """Promote a validated candidate to L2. Called AFTER human approval via AskUserQuestion."""
    root = _topic_root(topics_root, topic_slug)
    slug = _slugify(candidate_id)
    cand_path = root / "L3" / "candidates" / f"{slug}.md"
    if not cand_path.exists():
        return f"Candidate {slug} not found."
    fm, body = _parse_md(cand_path)
    if fm.get("status") != "validated":
        return f"Candidate {slug} status is '{fm.get('status')}', not 'validated'. Validate first."
    fm["status"] = "promoted"
    fm["promoted_at"] = _now()
    fm["promotion_comment"] = comment
    _write_md(cand_path, fm, body)
    l2_path = root / "L2" / "canonical" / f"{slug}.md"
    _write_md(l2_path, fm, body)
    return f"Promoted {slug} to L2/canonical/."


@mcp.tool()
def aitp_list_candidates(topics_root: str, topic_slug: str) -> list[dict[str, Any]]:
    """List all candidates for a topic."""
    root = _topic_root(topics_root, topic_slug)
    cand_dir = root / "L3" / "candidates"
    if not cand_dir.is_dir():
        return []
    results = []
    for path in sorted(cand_dir.glob("*.md")):
        fm, _ = _parse_md(path)
        results.append({"candidate_id": fm.get("candidate_id", path.stem), "title": fm.get("title", ""), "status": fm.get("status", "")})
    return results


@mcp.tool()
def aitp_get_skill_context(topics_root: str, topic_slug: str) -> dict[str, Any]:
    """Determine which skill to inject based on current topic status."""
    root = _topic_root(topics_root, topic_slug)
    fm, _ = _parse_md(root / "state.md")
    status = _infer_status(fm, root)
    skill_name = _SKILL_MAP.get(status, "skill-continuous")
    return {
        "topic_slug": topic_slug,
        "status": status,
        "mode": fm.get("mode", "explore"),
        "skill": skill_name,
        "message": f"Topic is in '{status}' state. Inject '{skill_name}'.",
    }


if __name__ == "__main__":
    mcp.run()
```

## FILE: skills/skill-explore.md

```markdown
---
name: skill-explore
description: Explore mode — discover literature, register sources, record initial ideas.
trigger: status == "new"
---

# Explore Mode

You are in **explore** mode. Your job: discover relevant literature and register sources.

## What to Do

1. **Search for literature** related to the research question in `state.md`.
   - Use arXiv search, Google Scholar, or references the human provides.
   - For each relevant paper, note the arXiv ID.

2. **Register each source** by calling:
   ```
   aitp_register_source(
     topics_root, topic_slug,
     source_id="author-keyword-year",
     source_type="paper",
     title="Full Paper Title",
     arxiv_id="2401.12345",
     fidelity="arxiv_preprint",
     notes="Why this paper is relevant"
   )
   ```

3. **Read key papers** to identify:
   - Core claims and results
   - Methods used
   - Open questions
   - Connections to other work

4. **Record initial ideas** in `L3/derivations.md` using:
   ```
   aitp_record_derivation(
     topics_root, topic_slug,
     derivation_id="idea-1",
     kind="ideation",
     title="Brief idea description",
     status="speculative",
     content="What you noticed and why it might matter"
   )
   ```

5. **When you have registered at least one source**, update status:
   ```
   aitp_update_status(topics_root, topic_slug, status="sources_registered")
   ```

## Rules

- Do NOT form formal candidates yet. Ideas in explore mode are speculative.
- Do NOT skip reading the source. Registering without reading is a protocol violation.
- Mark every idea as speculative. Do not merge speculation with source-grounded claims.
- If the human provides a direction, follow it. If not, search broadly first.

## When to Transition

Transition to **intake** (skill-intake) when:
- At least one source is registered AND
- You have a basic understanding of what the topic is about.

Ask the human: "I've found [N] sources. Should I start analyzing them in depth?"
```

## FILE: skills/skill-intake.md

```markdown
---
name: skill-intake
description: Intake mode — analyze each source in depth, extract assumptions and methods.
trigger: status == "sources_registered"
---

# Intake Mode

You are in **intake** mode. Your job: analyze each registered source in depth.

## What to Do

1. **Read each source** in `L0/sources/`. For each source:

2. **Create an intake note** by writing a Markdown file at `L1/intake/<source-id>.md`:

   ```markdown
   ---
   source_id: hs-1988
   reading_depth: close_read
   analyzed: 2026-04-19
   ---

   # Intake: Haldane & Shastry (1988)

   ## Core Claims
   - [List main results with evidence sentences]

   ## Key Assumptions
   - [Structural assumptions, not keywords]

   ## Methods
   - [Mathematical/computational methods used]

   ## Notation
   - $S_i$ = spin operator at site i
   - [All symbols defined]

   ## Open Questions
   - [What the source leaves unresolved]

   ## Connections
   - [Links to other sources in L0]
   ```

3. **Detect contradictions** between sources. If found, note them in the intake.

4. **Extract derivation anchors** — specific equations, theorems, or results that
   could serve as starting points for later L3 work.

5. **When all sources have intake notes**, update status:
   ```
   aitp_update_status(topics_root, topic_slug, status="intake_done")
   ```

## Rules

- Every claim in L1 is **provisional**. Mark it as such.
- Do not skip assumption extraction. "Obvious" assumptions are often the most important.
- Record notation precisely. Notation conflicts between sources must be noted.
- Reading depth: aim for `close_read` for core sources, `scan` for peripheral ones.

## When to Transition

Transition to **derive** (skill-derive) when:
- All registered sources have intake notes AND
- You understand the key assumptions and methods AND
- You have at least one idea for what to investigate.
```

## FILE: skills/skill-derive.md

```markdown
---
name: skill-derive
description: Derive mode — perform derivations, form candidates, iterate.
trigger: status == "intake_done"
---

# Derive Mode

You are in **derive** mode. Your job: perform structured derivations and form
candidate findings.

## What to Do

1. **Start a derivation** by calling:
   ```
   aitp_record_derivation(
     topics_root, topic_slug,
     derivation_id="d1-reconstruct-hamiltonian",
     kind="source_reconstruction",
     title="Reconstruct H-S Hamiltonian from source",
     source="hs-1988",
     content="Step-by-step reconstruction..."
   )
   ```

2. **Derivation types** (use the appropriate `kind`):
   - `source_reconstruction` — reproduce a result from a source
   - `cross_source_reconstruction` — combine results from multiple sources
   - `candidate_derivation` — derive a new or novel result
   - `failed_attempt` — record a failed approach (do not hide failures)
   - `notation_resolution` — resolve notation conflicts between sources

3. **Record every step**. Each derivation step should include:
   - What you started from (source, previous step)
   - What transformation you applied
   - What you obtained
   - Any assumptions made

4. **When a derivation produces a finding**, form a candidate:
   ```
   aitp_submit_candidate(
     topics_root, topic_slug,
     candidate_id="level-spacing-wigner",
     title="Level spacing follows Wigner-Dyson distribution",
     claim="In the chaotic window, the level spacing distribution...",
     evidence="Numerical data from derivation d3, analytical argument from d2",
     assumptions="Thermalization assumption, finite-size extrapolation",
     validation_criteria="Compare with GOE prediction, check convergence"
   )
   ```

5. **When a candidate is submitted**, update status:
   ```
   aitp_update_status(topics_root, topic_slug, status="candidate_ready")
   ```

## Rules

- Record **failed attempts**. A negative result is still a result.
- Do not skip steps. If you jump from step 3 to step 7, record why.
- Each candidate must state its claim, evidence, assumptions, and validation criteria.
- Do not claim more than the evidence supports.
- If you need more sources, go back to explore mode (record why in derivations).

## Mode Awareness

- In `learn` mode: focus on `source_reconstruction` and `cross_source_reconstruction`.
  Verify known results before pursuing new ideas.
- In `implement` mode: focus on `candidate_derivation`. Pursue new ideas with
  full L3-I → L3-P → L3-A pipeline.

## When to Transition

Transition to **validate** (skill-validate) when:
- At least one candidate is submitted with clear validation criteria.

Ask the human: "I have a candidate: [title]. Should I proceed to validate it?"
```

## FILE: skills/skill-validate.md

```markdown
---
name: skill-validate
description: Validate mode — check candidates against evidence and known results.
trigger: status == "candidate_ready"
---

# Validate Mode

You are in **validate** mode. Your job: verify candidates against their declared
validation criteria.

## What to Do

1. **Read the candidate** from `L3/candidates/<id>.md`. Note its:
   - Claim
   - Evidence provided
   - Assumptions
   - Validation criteria

2. **Run validation checks** appropriate to the candidate:

   ### Numerical Validation
   - Run benchmark comparisons if applicable
   - Check convergence (parameter sweeps, finite-size scaling)
   - Verify error budgets are within tolerance
   - Record results in a Python script or notebook

   For numerical work, use the **Jupyter MCP server** tools:
   - `jupyter-mcp-server__connect_to_jupyter` — connect to running Jupyter
   - `jupyter-mcp-server__use_notebook` — open a notebook for the validation
   - `jupyter-mcp-server__insert_execute_code_cell` — run Python code inline
   - `jupyter-mcp-server__read_cell` — read output for results
   - Save generated plots to `L4/reviews/figures/` for L5 inclusion

   ### Analytical Validation
   - Check limiting cases: do formulas reduce correctly?
   - Dimensional analysis: do equations have correct dimensions?
   - Symmetry checks: do results respect declared symmetries?
   - Self-consistency: are different parts of the derivation compatible?

   For formal verification, use the **Lean MCP server** tools:
   - `lean-lsp-mcp__lean_goal` — check proof state at a position
   - `lean-lsp-mcp__lean_diagnostic_messages` — find errors in formalization
   - `lean-lsp-mcp__lean_leansearch` — search mathlib for relevant lemmas
   - `lean-lsp-mcp__lean_multi_attempt` — test tactics without editing
   - `lean-lsp-mcp__lean_verify` — verify a theorem with axiom check

   ### Comparison Validation
   - Compare candidate against known L2 results
   - If contradiction found, record it explicitly

3. **Write a validation review** at `L4/reviews/<candidate-id>.md`:

   ```markdown
   ---
   candidate_id: level-spacing-wigner
   reviewer: ai_agent
   status: pass
   reviewed: 2026-04-19
   ---

   # Validation Review: Level Spacing Distribution

   ## Checks Performed
   - [x] Limiting case: reduces to Poisson in integrable limit
   - [x] Dimensional analysis: dimensionless ratio
   - [x] Numerical comparison: chi-squared test vs GOE

   ## Results
   [Detailed findings]

   ## Gaps Remaining
   - [Any unresolved issues]
   ```

4. **Update candidate status** based on results:
   - If passed: read the candidate .md, update frontmatter `status: validated`
   - If failed: update `status: revision_needed`, explain what needs fixing
   - If stuck: update `status: blocked`, explain what is missing

5. **If candidate passes**, update topic status:
   ```
   aitp_update_status(topics_root, topic_slug, status="validated")
   ```

## Rules

- **L4 does NOT write to L2 directly.** All results return through L3-R.
- Do not weaken validation criteria to make a candidate pass.
- Record what was checked, how, and what passed/failed.
- If you cannot complete validation (missing capability/source), record it honestly.
  Do not fake closure.

## Validation Outcomes

| Outcome | Meaning | Next Step |
|---------|---------|-----------|
| `pass` | All criteria met | Route to promotion |
| `partial_pass` | Some criteria met | Determine if partial result is useful |
| `fail` | Criteria not met | Return to L3 for revision |
| `contradiction` | Contradicts known results | Open gap, investigate |
| `blocked` | Cannot complete | Record blocker, escalate if needed |
```

## FILE: skills/skill-promote.md

```markdown
---
name: skill-promote
description: Promote mode — guide validated candidates through L2 promotion gate.
trigger: status == "validated"
---

# Promote Mode

You are in **promote** mode. Your job: present validated candidates to the human
for L2 promotion approval.

## What to Do

1. **List validated candidates** by calling:
   ```
   aitp_list_candidates(topics_root, topic_slug)
   ```
   Filter for `status == "validated"`.

2. **For each validated candidate**, read its file at `L3/candidates/<id>.md`
   and present the evidence to the human using AskUserQuestion:

   ```
   AskUserQuestion(questions=[{
     "header": "Promote",
     "question": "Candidate '[title]' has passed validation. It claims [brief claim]. Evidence: [summary]. Should I promote it to reusable knowledge (L2)?",
     "options": [
       {"label": "Approve promotion", "description": "Promote to L2/canonical/ as trusted knowledge"},
       {"label": "Needs revision", "description": "Return to derive mode for corrections"},
       {"label": "Reject", "description": "Mark as rejected, do not promote"}
     ],
     "multiSelect": false
   }])
   ```

3. **On human approval**, call:
   ```
   aitp_promote_candidate(topics_root, topic_slug, candidate_id="...", comment="Human approved")
   ```

4. **On revision request**, update the candidate:
   - Read `L3/candidates/<id>.md`
   - Change frontmatter `status: revision_needed`
   - Add the human's feedback to the body
   - Return to derive mode (skill-derive)

5. **After all candidates are resolved**, update topic status:
   ```
   aitp_update_status(topics_root, topic_slug, status="promoted")
   ```

## Rules

- **L2 promotion ALWAYS requires human approval via AskUserQuestion.** No exceptions.
- Do not auto-promote without asking the human.
- Present evidence honestly, including gaps and assumptions.
- If a candidate is too wide (mixes multiple claims), split it before promoting.

## After Promotion

After promoting all candidates:
- Ask the human if they want to continue with another candidate
- Or start writing (L5, skill-write)
- Or explore new directions
```

## FILE: skills/skill-write.md

```markdown
---
name: skill-write
description: Write mode — assemble L2+L3 knowledge into publication-grade TeX and compile to PDF.
trigger: status == "promoted"
---

# Write Mode

You are in **write** mode. Your job: assemble validated knowledge from L2 and L3
into a publication-ready LaTeX manuscript, then compile it to PDF.

## What to Do

### 1. Gather Material

Read all available content layers:

- `L2/canonical/*.md` — validated knowledge (cite as established results)
- `L3/candidates/*.md` — candidates with `status: promoted` (now in L2 as well)
- `L3/derivations.md` — derivation trail for method sections
- `L4/reviews/*.md` — validation evidence for results sections
- `L1/intake/*.md` — source analysis for introduction and background
- `L0/sources/*.md` — bibliography metadata

### 2. Create Outline

Write `L5_writing/outline.md` with paper structure. Ask human to approve.

### 3. Write TeX Draft

Create `L5_writing/draft.tex` with revtex4-2 document class. Sections: Introduction, Background, Results, Discussion, Conclusion.

### 4. Handle Figures and Tables

Copy plots from L4 to `L5_writing/figures/`. Generate tables to `L5_writing/tables/`.

### 5. Build Bibliography

Create `L5_writing/references.bib` from L0 source metadata.

### 6. Compile to PDF

Run pdflatex + bibtex + pdflatex x2. Or latexmk -pdf.

### 7. Present to Human

Tell human where PDF is, what was included, any gaps.

## Rules

- Every claim must trace to L2 (trusted) or L3 (preliminary).
- L3 content must be marked as preliminary.
- Do NOT invent results not backed by L2 or L3.
- Figures/tables must trace to L4 validation or L2 canonical data.
- Do not modify L0-L4 artifacts during writing.

## After Writing

- Ask human to review the PDF
- Iterate on revisions
- When satisfied, mark topic as `complete`
```

## FILE: skills/skill-continuous.md

```markdown
---
name: skill-continuous
description: Resume mode — restore workflow after session break or context compaction.
trigger: any status after session break
---

# Resume Mode

Your session was interrupted. This skill helps you pick up where you left off.

## What to Do

1. **Read topic state**: `aitp_get_status(topics_root, topic_slug)`

2. **Check for popups** (blockers requiring human input):
   ```
   aitp_get_popup(topics_root, topic_slug)
   ```
   If there is a popup, resolve it FIRST before continuing.

3. **Determine where you are** based on status:

   | Status | Next Skill |
   |--------|------------|
   | `new` | skill-explore |
   | `sources_registered` | skill-intake |
   | `intake_done` | skill-derive |
   | `candidate_ready` | skill-validate |
   | `validated` | skill-promote |
   | `promoted` | skill-write |
   | `complete` | Ask human for new direction |
   | `blocked` | Read state.md to understand blocker |

4. **Read relevant files** to rebuild context

5. **Inject the appropriate skill** and continue

## Rules

- Do NOT start from scratch. Read what already exists.
- Do NOT assume the status is correct. Verify by checking actual files.
- Fix status mismatches.
```

## FILE: hooks/session_start.py

```python
"""AITP SessionStart hook — inject skill based on topic status."""

from __future__ import annotations
import json
import os
import re
import sys

def _find_topics_root() -> str | None:
    cwd = os.getcwd()
    for _ in range(5):
        candidate = os.path.join(cwd, "topics")
        if os.path.isdir(candidate):
            return os.path.dirname(candidate)
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent
    return os.environ.get("AITP_TOPICS_ROOT")

def _parse_frontmatter(path: str) -> dict:
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm

def _find_active_topic(topics_root: str) -> str | None:
    topics_dir = os.path.join(topics_root, "topics")
    if not os.path.isdir(topics_dir):
        return None
    best_slug = None
    best_time = ""
    for entry in os.listdir(topics_dir):
        state_path = os.path.join(topics_dir, entry, "state.md")
        if os.path.isfile(state_path):
            fm = _parse_frontmatter(state_path)
            updated = fm.get("updated_at", "")
            if updated > best_time:
                best_time = updated
                best_slug = entry
    return best_slug

_SKILL_MAP = {
    "new": "skill-explore",
    "sources_registered": "skill-intake",
    "intake_done": "skill-derive",
    "candidate_ready": "skill-validate",
    "validated": "skill-promote",
    "promoted": "skill-write",
}

def main():
    topics_root = _find_topics_root()
    if not topics_root:
        print("AITP: No topics root found. Skipping skill injection.")
        return
    topic_slug = _find_active_topic(topics_root)
    if not topic_slug:
        print("AITP: No active topic found. Start one with aitp_bootstrap_topic.")
        return
    state_path = os.path.join(topics_root, "topics", topic_slug, "state.md")
    fm = _parse_frontmatter(state_path)
    status = fm.get("status", "new")
    skill = _SKILL_MAP.get(status, "skill-continuous")
    print(f"AITP: Active topic '{topic_slug}' (status: {status}).")
    print(f"AITP: Read and follow skills/{skill}.md before continuing.")

if __name__ == "__main__":
    main()
```

## FILE: hooks/compact.py

```python
"""AITP Compact hook — re-inject skill after context compaction."""

from __future__ import annotations
import os
import sys
from session_start import _find_topics_root, _find_active_topic, _parse_frontmatter, _SKILL_MAP

def main():
    topics_root = _find_topics_root()
    if not topics_root:
        return
    topic_slug = _find_active_topic(topics_root)
    if not topic_slug:
        return
    state_path = os.path.join(topics_root, "topics", topic_slug, "state.md")
    fm = _parse_frontmatter(state_path)
    status = fm.get("status", "new")
    skill = _SKILL_MAP.get(status, "skill-continuous")
    print(f"AITP: Context was compacted. Resuming topic '{topic_slug}' (status: {status}).")
    print(f"AITP: Read skills/{skill}.md to restore your workflow context.")
    print(f"AITP: Also read topics/{topic_slug}/state.md for the full picture.")

if __name__ == "__main__":
    main()
```

## FILE: hooks/stop.py

```python
"""AITP Stop hook — save progress summary at session end."""

from __future__ import annotations
import os
import re
from datetime import datetime

def _parse_frontmatter(path: str) -> dict:
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not m:
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm

def _find_topics_root() -> str | None:
    cwd = os.getcwd()
    for _ in range(5):
        candidate = os.path.join(cwd, "topics")
        if os.path.isdir(candidate):
            return os.path.dirname(candidate)
        parent = os.path.dirname(cwd)
        if parent == cwd:
            break
        cwd = parent
    return os.environ.get("AITP_TOPICS_ROOT")

def main():
    topics_root = _find_topics_root()
    if not topics_root:
        return
    topics_dir = os.path.join(topics_root, "topics")
    if not os.path.isdir(topics_dir):
        return
    for entry in os.listdir(topics_dir):
        state_path = os.path.join(topics_dir, entry, "state.md")
        if os.path.isfile(state_path):
            now = datetime.now().astimezone().isoformat(timespec="seconds")
            with open(state_path, "a", encoding="utf-8") as f:
                f.write(f"\n## Session ended {now}\n\n")

if __name__ == "__main__":
    main()
```

## FILE: docs/CHARTER.md (constitutional, highest authority)

```markdown
# AITP Research Charter

## Preamble — Three-Phase Evolution

1. **Phase 1 — Research Workflow Tool**: human-in-the-loop, human directs, AITP executes.
2. **Phase 2 — Learning Collaborator**: reuses past results, anticipates needs, genuine partner.
3. **Phase 3 — Autonomous Physicist**: independently explores, tests, proposes, creates.

## Articles

1. The goal is truth, not fluency.
2. Distinguish source-grounded / derived / conjectured / speculative. Never merge silently.
3. Preserve distinction: source traces / provisional / reusable / exploratory / validation.
4. If a step matters, it's a durable artifact.
5. Reusable knowledge is earned through validation, not assumed.
6. Tool trust is conditional until gates are satisfied.
7. Preserve anomalies, failures, unresolved gaps.
8. Human checkpoints are legitimate.
9. Conformance is enforceable (protocol artifacts must exist).
10. Adapters execute AITP but do not redefine it.
```

---

## PLANNED CHANGES (not yet in code)

### 1. L2 Global Knowledge Base

Move L2 from per-topic to global. Add subdirs: notation/, conventions/, methods/, lessons/.

**Evolution mechanism**: bootstrap_topic reads L2 global, creates local snapshot. Promote writes back to L2 global with conflict detection. Creates positive feedback loop: more topics → richer L2 → better new topics.

**Notation atlas** (`L2/notation/`): accumulates symbol definitions across topics. New topics inherit. Conflicts flagged for resolution.

**Conventions** (`L2/conventions/`): locked high-level decisions (metric, units). Inherited by default.

**Methods** (`L2/methods/`): validated method descriptions + applicability. Not code, structured descriptions.

**Lessons** (`L2/lessons/`): negative knowledge from failures. Warnings for future topics.

### 2. Physics-Specific Enhancements

- **Notation lock** (L1): before derivation, lock conventions in `L1/convention_snapshot.md`
- **Approximation discipline** (L3): every step records approximation type, validity regime, dimensional check
- **Physical consistency checks** (L4): conservation laws, correspondence principle, thermodynamic consistency, symmetry constraints, positivity, limit behavior — all mandatory, not optional
- **Trust levels** (L2): confidence field: exact/rigorous/established/conjectured/phenomenological
- **Equation provenance** (L5): every numbered equation has source annotation

### 3. Bug: skill-continuous still references aitp_get_popup (removed tool)

---

## REVIEW QUESTIONS

Please evaluate on these dimensions:

### A. Completeness
1. Can the current v2 run full E2E? (literature → intake → derivation → validation → promotion → TeX → PDF)
2. Are there missing tools/skills/hooks that block E2E?
3. Is the L2 global design complete enough to implement? Edge cases?

### B. Correctness
1. Are all status transitions valid? Any unreachable or unmapped statuses?
2. Is `_infer_status` correct? Can it produce wrong status?
3. Race conditions or consistency issues in Markdown file I/O?
4. Is AskUserQuestion-based promotion gate safe from bypass?

### C. Design Quality
1. Is 11 tools the right number? Which are unnecessary?
2. Are skills the right granularity? Split or merge?
3. Is the hook design sufficient for session continuity?
4. Is L2 global evolution sound? Better alternatives?

### D. Physics-Specific Fitness
1. Do planned enhancements cover main failure modes in theoretical physics?
2. Other physics patterns not captured?
3. Is trust level taxonomy appropriate?

### E. Scalability
1. Will global L2 grow unmanageably?
2. Are append-only files (L3/derivations.md) sustainable?
3. Topic-state query performance with many topics?

### F. Security & Safety
1. Can agent silently promote unvalidated content to L2?
2. Can agent modify L0-L4 during L5 writing?
3. Prompt injection risks in skill files?

## EXPECTED OUTPUT

1. List of issues (bugs, gaps, design problems) with priority (P0/P1/P2)
2. Specific suggestions for each issue
3. Overall assessment: is v2 ready for E2E testing on a real physics topic?
