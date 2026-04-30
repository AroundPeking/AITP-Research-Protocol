---
name: L2 Architecture v5
version: "5.0"
description: Three-dimensional knowledge architecture for L2.
  Formal concepts (graph) + Physical systems (catalog) + Computational methods (catalog).
  Three orthogonal retrieval dimensions serving three distinct use cases.
created: "2026-04-30"
status: spec
---

# L2 Architecture v5 — Three-Dimensional Knowledge

## Problem

L2 v4 is a single graph database (node/edge/tower). This works for formal_theory
topics where knowledge is concepts and their relationships. But for code_method
and toy_numeric topics, the critical cross-topic knowledge is:

- "What's the verified status of Si QSGW on ABACUS+LibRPA?"
- "What INPUT template should I use?"
- "What known pitfalls exist for this toolchain?"
- "Has anyone validated this formula numerically?"

A graph of "concept", "theorem", "technique" nodes cannot answer these questions
efficiently. The knowledge exists but is buried in node physical_meaning fields.

## Architecture

```
L2/
├── formal/                    # Dimension 1: Theoretical concepts (existing graph)
│   ├── nodes/                 # Per-node .md files (aitp_create_l2_node)
│   ├── edges/                 # Per-edge metadata
│   ├── towers/                # EFT towers
│   └── index.md               # Domain taxonomy (aitp_query_l2_index)
│
├── systems/                   # Dimension 2: Physical systems
│   ├── si-bulk.md             # All Si-related knowledge
│   ├── bn-bulk.md             # BN, etc.
│   └── INDEX.md               # Searchable index by element/structure
│
├── methods/                   # Dimension 3: Computational methods
│   ├── abacus-librpa-qsgw.md  # ABACUS+LibRPA QSGW workflow
│   ├── fhi-aims-librpa-qsgw.md
│   └── INDEX.md               # Searchable index by toolchain
│
└── crosswalks/                # Links between dimensions
    └── head-wing.md            # "Head-wing concept → implementations → systems"
```

## Dimension 1: formal/ (existing, unchanged)

Purpose: Store theoretical concepts, theorems, derivation results.
Data model: Graph (node, edge, tower).
Query pattern: "What is the head-wing formula?" "What derives_from what?"
Tools: aitp_query_l2_index, aitp_query_l2_graph, existing node/edge tools.

## Dimension 2: systems/ (new)

Purpose: Store everything about a physical system — calculation results,
verification status, benchmark values, templates.

### File schema

```yaml
---
system_id: si-bulk
name: Si Bulk (Cubic, Diamond)
formula: Si
structure: diamond
properties: [semiconductor, indirect-gap, cubic]
reference_gap_experiment: 1.17  # eV
reference_gap_lda: 0.45          # eV (typical)
reference_gap_g0w0: 1.1-1.3      # eV (converged)
---

# Si Bulk

## Calculation Records

### ABACUS+LibRPA QSGW band0
- **Status**: failed
- **Server**: dongfang, kouxiang
- **Date**: 2025-09 to 2026-04
- **Details**:
  - kouxiang: ran ~8.5h, no completion, no GW_band output
  - dongfang: SCF OK, pyatb blocked (get_velocity_matrix API mismatch)
  - dongfang: LibRPA shrink_sinvS divide-by-zero with use_shrink_abfs=t
- **Input template**: [methods/abacus-librpa-qsgw.md]
- **Pitfalls**: pyatb API version, shrink_sinvS crash, nbands too small
```

### Query tools

```
aitp_query_systems(system_id="si-bulk")  → full system record
aitp_query_systems(formula="Si")          → Si records
aitp_query_systems(status="verified")     → only verified systems
aitp_list_systems()                       → system index
```

## Dimension 3: methods/ (new)

Purpose: Store everything about a computational method — workflow steps,
input templates, compatibility matrix, known pitfalls.

### File schema

```yaml
---
method_id: abacus-librpa-qsgw
name: ABACUS + LibRPA QSGW
toolchain: [abacus, pyatb, librpa, libri]
lane: code_method
status: unverified  # verified | consistent | unverified | broken
---

# ABACUS + LibRPA QSGW

## Verified Systems
- (none — no system has a successful QSGW band0 run verified)

## Unverified Systems
- [Si Bulk](../systems/si-bulk.md): kouxiang incomplete, dongfang blocked

## Workflow
1. ABACUS SCF (INPUT_scf, KPT_scf, STRU)
2. pyatb get_diel.py → band_out, KS_eigenvector_*.dat, velocity_matrix
3. mv OUT.ABACUS/sks*_nao.txt . ; mv OUT.ABACUS/vxcs*_nao.txt .
4. ABACUS NSCF (INPUT_nscf, KPT_nscf)
5. preprocess_abacus_for_librpa_band.py
6. rename_copy.sh → band_vxcs*, band_sks*
7. LibRPA chi0_main.exe

## Input Templates
### SCF
\`\`\`
rpa = 1
out_mat_xc = 1
out_mat_xc2 = 1      # QSGW: NAO full Vxc matrix
out_mat_hs2 = 1
out_mat_r = 1
exx_pca_threshold = 10
...
\`\`\`

## Known Pitfalls
### pyatb API mismatch
- Symptom: `ValueError: not enough values to unpack (expected 3, got 2)`
- Cause: pyatb version returns (eigenvalues, eigenvectors) without velocity_matrix
- Fix: Use pyatb >= version X, or use get_velocity_matrix separately

### shrink_sinvS divide-by-zero
- Symptom: `Floating point exception at handle_sinvS_file()`
- Cause: use_shrink_abfs=t but shrink_sinvS files malformed or missing
- Fix: Use use_shrink_abfs=f, or regenerate shrink_sinvS with correct ABACUS
```

### Query tools

```
aitp_query_methods(method_id="abacus-librpa-qsgw")  → full method record
aitp_query_methods(toolchain=["abacus", "librpa"])   → matching methods
aitp_query_methods(status="verified")                 → only verified methods
aitp_query_methods(pitfall="pyatb")                   → methods with pyatb issues
aitp_list_methods()                                    → method index
```

## Crosswalks

Crosswalk files link concepts, systems, and methods. They are the "join table"
between dimensions.

```yaml
---
crosswalk_id: head-wing
concepts: [headwing-algorithm-trace]
systems: [si-bulk]
methods: [abacus-librpa-qsgw, fhi-aims-librpa-qsgw]
status: partially-verified  # formula verified from code, numerical validation pending
---
```

## MCP Tools to Add

### System Catalog
- `aitp_query_systems(system_id, formula, status)` → list or query
- `aitp_record_system(system_id, ...)` → create or update

### Method Catalog
- `aitp_query_methods(method_id, toolchain, status, pitfall)` → list or query
- `aitp_record_method(method_id, ...)` → create or update

### Crosswalk
- `aitp_query_crosswalks(concept_id, system_id, method_id)` → find connections

## Migration from v4

Existing L2 node/edge/tower data moves to `L2/formal/`.
System and method knowledge currently embedded in node physical_meaning fields
should be extracted into new catalog files.
Topics continue to use existing L0-L4 stages unchanged.
The promotion workflow gains a new step: successful L4 validation → record
in both formal/ and systems/ + methods/.
