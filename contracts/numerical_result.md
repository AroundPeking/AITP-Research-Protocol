---
artifact_kind: numerical_result
required_fields:
  - observable
  - computed_value
  - units
  - execution_environment
  - benchmark_comparison
observable: ''
computed_value: ''
uncertainty: ''
units: ''
conditions:
  system: ''
  method: ''
  pseudopotential: ''
  ecutwfc: ''
  k_grid: ''
  nbands: ''
  convergence_criterion: ''
  iterations_completed: ''
  iterations_max: ''
execution_environment:
  host: ''
  binary_commit: ''
  mpi_processes: ''
  wall_time: ''
  job_id: ''
benchmark_comparison:
  literature_value: ''
  literature_source: ''
  literature_method: ''
  agreement_status: ''
  deviation_percent: ''
---

# Numerical Result: {{observable}}

## Computed Value

- **Value**: {{computed_value}} ± {{uncertainty}} {{units}}
- **Conditions**: {{system}}, {{method}}, {{pseudopotential}}, ecutwfc={{ecutwfc}} Ry, k-grid={{k_grid}}, nbands={{nbands}}
- **Convergence**: {{convergence_criterion}}, iterations {{iterations_completed}}/{{iterations_max}}

## Execution Environment

| Field | Value |
|-------|-------|
| Host | {{host}} |
| Binary commit | {{binary_commit}} |
| MPI processes | {{mpi_processes}} |
| Wall time | {{wall_time}} |
| Job ID | {{job_id}} |

## Benchmark Comparison

| Field | Value |
|-------|-------|
| Literature value | {{literature_value}} {{units}} |
| Literature source | {{literature_source}} |
| Literature method | {{literature_method}} |
| Agreement | {{agreement_status}} |
| Deviation | {{deviation_percent}}% |

### Agreement Assessment

[EXPLAIN: does computed value agree with literature within expected error? If not, why?]

## Data Provenance

- Input files: [list paths to librpa.in, INPUT_scf, KPT, etc.]
- Output files: [list paths to gw_band.dat, librpa.out, etc.]
- Raw data archived at: [path on HPC]

## Evidence

[Link to L4 outputs or attach key plots/data]
