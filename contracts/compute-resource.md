# Compute Resource Contract

## Purpose

Declare where and how a computation runs — local machine or remote server with
specific module and MPI configurations.

## Minimum fields

- `resource_id`
- `location`: `local` or `server`
- For server:
  - `alias`: server shorthand (e.g., `df`, `ks`, `66`)
  - `host`
  - `modules`: list of environment modules to load
  - `abacus_path`
  - `librpa_path`
  - `slurm_defaults`: partition, cpus_per_task, omp_num_threads
- For local:
  - `abacus_path`
  - `librpa_path`

## Constraints

Server constraints that must be declared:

- `batch_no_bashrc`: Slurm batch must not use `source ~/.bashrc` as entrypoint
- `full_node_threads`: Default cpus_per_task to full node core count for 1 MPI
  rank/node
- `explicit_modules`: Prefer explicit `module load` over shell profile injection

## Why it matters

Server environment differences are the single largest source of silent failures
in computational physics. Explicit resource declarations prevent profile
injection issues, conda path conflicts, and mismatched toolchains.
