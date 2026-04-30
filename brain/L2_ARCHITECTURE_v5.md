---
name: L2 Architecture v5
version: "5.0"
status: design
created: "2026-04-30"
replaces: PROTOCOL.md §L2 Knowledge Graph
---

# L2 Architecture v5 — Faceted Knowledge Base

## 1. The Physicist's Mental Model

When approaching a new research problem, a physicist asks questions across
five axes that form a natural query hypergraph:

```
              ┌─────────────────┐
              │  What am I      │
              │  studying?      │  ← System
              └────────┬────────┘
                       │
     ┌─────────────────┼─────────────────┐
     │                 │                 │
┌────▼────┐     ┌──────▼──────┐    ┌─────▼──────┐
│  What   │     │  How do I   │    │  What has  │
│  theory │     │  compute/   │    │  been      │
│  governs│     │  derive it? │    │  done?     │
│  this?  │     │             │    │            │
│ Framework    │  Method     │    │  Prior     │
└────┬────┘     └──────┬──────┘    └─────┬──────┘
     │                 │                 │
     └─────────────────┼─────────────────┘
                       │
              ┌────────▼────────┐
              │  What claim or  │
              │  observable am  │
              │  I targeting?   │  ← Claim/Observable
              └─────────────────┘
```

Examples across lanes:

| Lane | System | Framework | Method | Claim |
|------|--------|-----------|--------|-------|
| code_method | Si bulk, diamond, a=5.43Å | GW approximation, k·p theory | ABACUS+LibRPA QSGW band0 | "Head-wing correction at Gamma improves k-point convergence" |
| formal_theory | 4D Maxwell theory with θ-term | Generalized symmetries, higher-form gauge theory | Anomaly inflow, descent equations | "1-form magnetic symmetry has mixed anomaly with 0-form electric symmetry" |
| toy_numeric | LR Heisenberg chain H = Σ J_ij S_i·S_j, J_ij ∝ 1/r^α | Random matrix theory, ETH | Exact diagonalization + level statistics | "Spectral form factor shows linear ramp for α < 2D" |
| formal_theory | FQHE at filling ν = 1/3 | Chern-Simons theory, anyon condensation | Edge mode counting, modular tensor category | "Ground state degeneracy on torus is 3^g" |

The L2 must make ALL five axes queryable, and their intersections navigable.

## 2. Core Data Model: Faceted Entries

The atomic unit of L2 is an **Entry**. Every entry has a **role** that determines
which structured **facets** it carries. Entries are connected by typed **relationships**.

### 2.1 Entry Roles

Five roles cover all lanes:

| Role | Description | Examples |
|------|-------------|----------|
| **Claim** | A statement about nature, a formula, a numerical result, a definition | "Si G0W0 gap = 1.15 eV", "ε_head = 1 − Σ v·v/(Eg(Eg²+ω²))", "out_mat_xc2 outputs Vxc full matrix" |
| **System** | A physical system, model, or spacetime | Si bulk, 2+1D Chern-Simons at level k, Heisenberg chain J∝1/r^α |
| **Method** | A technique, workflow, or code path | ABACUS+LibRPA QSGW, conformal bootstrap, exact diagonalization |
| **Pitfall** | A known failure mode, bug, or subtle issue | pyatb API mismatch, shrink_sinvS crash |
| **Question** | An open research question | "Does iterative head-wing improve k-point convergence?" |

Why five, not sixteen: The current 16 node types (concept, theorem, technique,
result, approximation, open_question, regime_boundary, negative_result, definition,
equation, assumption_card, notation, proof_fragment, example, caveat, diagram)
are subtypes of these five. The canonical type is stored as a facet:

```
role: claim
claim_type: theorem | result | approximation | negative_result | definition | equation | ...
```

### 2.2 Common Facets (all entries)

| Facet | Type | Required | Description |
|-------|------|----------|-------------|
| `entry_id` | slug | yes | Unique ID |
| `role` | enum | yes | claim / system / method / pitfall / question |
| `title` | str | yes | Human-readable summary |
| `lane` | list[enum] | yes | Which lanes this applies to: formal_theory, toy_numeric, code_method |
| `status` | enum | yes | verified / consistent / unverified / failed / conjectured |
| `regime` | str | no | Where this holds: "weak coupling, T=0, 3D" |
| `source_ref` | str | **yes** | Provenance: topic slug + file |
| `updated` | date | yes | Last modification |

### 2.3 Role-Specific Facets

**Claim** adds:

| Facet | Type | Description |
|-------|------|-------------|
| `claim_type` | enum | theorem / result / approximation / negative_result / definition / equation / assumption / proof |
| `statement` | str | The claim itself (one sentence) |
| `mathematical_expression` | str | LaTeX formula |
| `observable` | str | What quantity this claim is about: "band gap", "entanglement entropy", "anomaly coefficient" |
| `evidence_type` | enum | analytic_proof / numerical / experimental / code_derived |
| `depends_on_claims` | list[slug] | Claims this depends on |
| `counterargument` | str | Known weaknesses or counter-arguments |

**System** adds:

| Facet | Type | Description |
|-------|------|-------------|
| `system_type` | enum | material / hamiltonian / field_theory / lattice_model / phase / spacetime |
| `formula_or_identifier` | str | Chemical formula, Hamiltonian, Lagrangian |
| `parameters` | str | Key parameters: lattice constant, coupling, filling, dimension |
| `energy_scale` | str | Characteristic energy: eV, meV, GeV |
| `reference_values` | dict | Known experimental or theoretical benchmarks |

**Method** adds:

| Facet | Type | Description |
|-------|------|-------------|
| `method_type` | enum | numerics / analytics / experiment / code |
| `toolchain` | list[str] | Software stack |
| `steps` | list[str] | Workflow steps |
| `templates` | dict | File contents or paths to templates |
| `compatibility` | dict | Known-good version combinations |
| `resource_estimate` | str | Typical CPU, memory, wall time |

**Pitfall** adds:

| Facet | Type | Description |
|-------|------|-------------|
| `symptom` | str | What the user sees: "ValueError: not enough values to unpack" |
| `cause` | str | Root cause |
| `fix` | str | How to resolve |
| `affects_methods` | list[slug] | Methods this pitfall applies to |

**Question** adds:

| Facet | Type | Description |
|-------|------|-------------|
| `question_statement` | str | The research question |
| `competing_hypotheses` | list[str] | Possible answers |
| `suggested_approach` | str | How one might investigate |

### 2.4 Relationships

Entries are connected by typed, directed relationships. Simplified from 20 types to 8:

**Logical** (cross-lane):
- `derives_from`: A logically follows from B
- `implies`: A ⇒ B
- `contradicts`: A and B cannot both be true
- `equivalent_to`: A ⇔ B

**Hierarchical** (generalization/specialization):
- `limits_to`: A reduces to B in some limit
- `generalizes` / `specializes`: A is broader/narrower than B
- `component_of`: A is part of B

**Methodological** (connecting across roles):
- `computed_by`: Claim was produced by Method
- `verified_by`: Claim was verified by Method
- `blocked_by`: Claim cannot be verified because of Pitfall
- `applies_to`: Method is applicable to System
- `governs`: Framework governs System

## 3. Storage Layout

```
L2/
├── entries/            # All entries as individual .md files
│   ├── claim-si-g0w0-gap.md
│   ├── claim-headwing-formula.md
│   ├── claim-out-mat-xc2.md
│   ├── system-si-bulk.md
│   ├── system-heisenberg-chain.md
│   ├── method-abacus-librpa-qsgw.md
│   ├── pitfall-pyatb-api-mismatch.md
│   ├── question-iterative-headwing.md
│   └── ...
│
├── INDEX.md            # Auto-generated: all entries by role + lane + status
├── INDEX_status.md     # Only verified entries (for quick bootstrap)
├── INDEX_pitfalls.md   # All pitfalls with symptoms (for debugging)
│
├── formal/             # Existing graph (node/edge/tower) — unchanged
│   └── ...
│
└── templates/           # Reusable input files
    └── si-qsgw-abacus/
        ├── INPUT_scf
        ├── INPUT_nscf
        ├── KPT_scf
        ├── KPT_nscf
        └── librpa.in
```

Each entry file:

```markdown
---
entry_id: claim-si-g0w0-gap
role: claim
claim_type: result
title: "Si G0W0 band gap is 1.1-1.3 eV"
lane: [code_method, formal_theory]
status: verified
regime: "diamond structure, converged basis"
mathematical_expression: "E_gap = 1.15 ± 0.05 eV"
observable: "band gap"
evidence_type: numerical
source_ref: "topic:qsgw-headwing-update-librpa/kouxiang-runs"
updated: "2026-04-30"
---

# Si G0W0 Band Gap

Verified by multiple FHI-aims+LibRPA G0W0 calculations.
ABACUS+LibRPA path not independently verified.

## Relationships
- computed_by: method-fhi-aims-librpa-qsgw
- governs: system-si-bulk
```

## 4. Query Patterns

Agents query the L2 through these access patterns (MCP tools to implement):

```
# Bootstrap: what do we know?
aitp_query_entries(role="claim", status="verified")
  → all verified claims across all systems

# By system: what about Si?
aitp_query_entries(role="claim", system="system-si-bulk")
  → all claims about Si

# By method: how do I run QSGW?
aitp_query_entries(role="method", entry_id="method-abacus-librpa-qsgw")
  → full method entry with templates and pitfalls

# Debug: why is this failing?
aitp_query_entries(role="pitfall", affects_methods__contains="method-abacus-librpa-qsgw")
  → all known pitfalls for this method

# Open questions: what's left to do?
aitp_query_entries(role="question", status="unverified")
  → open questions, grouped by system

# Follow relationships: what depends on this?
aitp_query_entries(relationships__from="claim-headwing-formula")
  → all entries that reference this claim
```

Key: file-based implementation means agents can also just grep/glob the entries/ directory.

## 5. Integration with Topic Lifecycle

**L0 → L2 (Path A, lightweight):**
Well-understood facts: create entries directly without derivation.
```
aitp_record_entry(role="claim", claim_type="definition", status="verified", source_ref="...")
```

**L1 → L2:**
Each extracted source concept becomes a Claim entry (status: source_grounded).

**L3 → L2:**
Derivation produces Claim entries (status: unverified).
Pitfalls discovered during work become Pitfall entries.
Systems studied become System entries.
Methods used become Method entries.

**L4 → L2:**
Validated claims: status updated to verified.
Failed approaches: recorded as Pitfalls with symptom/cause/fix.
Negative results: recorded as Claims with claim_type="negative_result".

**Promotion gate (human):**
Before promoting, human reviews the entries and confirms status.

## 6. Migration from v4

1. v4 graph nodes → migrate to entries/, choosing the appropriate role
2. v4 node types → map to claim_type under role: claim
3. v4 edge types → map to the 8 relationship types
4. v4 towers → preserved in formal/ directory
5. Existing topics: not affected; promotion step gains ability to create entries
