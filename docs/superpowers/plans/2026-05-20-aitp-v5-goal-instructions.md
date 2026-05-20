# AITP v5 Goal Instructions

Use this file as the long-form instruction source for a Codex `/goal`.

## Objective

Complete AITP v5 according to the existing architecture and implementation plans.
The end state should be a practical theoretical-physicist workflow harness that is
tested, documented, pushed to the remote AITP repository, and easy for another AI
or human reviewer to audit step by step.

## Repository

Preferred worktree:

```text
C:\Users\samur\.config\superpowers\worktrees\AITP-Research-Protocol\aitp-v5-kernel-mvp
```

Branch:

```text
codex/aitp-v5-kernel-mvp
```

If the preferred worktree is unavailable, use the active AITP checkout only after
checking branch, git status, and recent commits.

## Planning Sources

Read these before choosing the next task:

- `PROJECT_MEMORY.md`
- `docs/superpowers/specs/2026-05-17-aitp-v5-physicist-workflow-architecture-plan.md`
- `docs/superpowers/plans/2026-05-20-aitp-v5-next-agent-implementation-plan.md`
- `docs/superpowers/plans/2026-05-18-aitp-v5-hooks-plan.md`
- Any newer AITP v5 progress, implementation, migration, or review documents.

## Core Invariants

- Typed v5 kernel records are authoritative.
- Summaries, README text, generated plans, external notes, IMA/Zotero/Obsidian
  pointers, and adapter packets are orientation-only unless converted into typed
  kernel records.
- Public surfaces exposing derived context must keep `summary_inputs_trusted=false`.
- Reference locations are not evidence by themselves.
- Trust-changing actions must go through kernel records, preflight, validation, or
  explicit human checkpoint records.
- Keep modules small and focused. Do not recreate the old monolithic AITP style.
- Prefer kernel/CLI/MCP/runtime/hook symmetry for public capabilities.
- Migrate old topic content into v5 typed records. Do not make legacy format the
  long-term compatibility truth source.

## Execution Loop

Work in small coherent subfeatures.

For each subfeature:

1. Check git status, branch, and recent commits.
2. Read only the minimal relevant planning and source files.
3. Select exactly one coherent task from the plan.
4. Write or update the focused test first.
5. Run that test and confirm it fails for the expected reason.
6. Implement the smallest correct change.
7. Update CLI/MCP/runtime/hook surfaces when the capability is public.
8. Update docs, README, or planning status when user-facing behavior changes.
9. Run focused verification.
10. Run the full v5 focused suite:

```powershell
$files = Get-ChildItem tests -Filter 'test_v5_*.py' | ForEach-Object { $_.FullName }
pytest $files -q
```

11. Run:

```powershell
python -m compileall -q brain\v5
git diff --check -- .
```

12. Commit the coherent subfeature.
13. Push `origin codex/aitp-v5-kernel-mvp`.
14. Push `origin HEAD:main` only when fast-forward safe and consistent with the repo workflow.
15. Continue to the next planned subfeature.

## Reviewability Ledger

Maintain or update a durable implementation ledger so a reviewer can inspect every
step. Each completed subfeature should record:

- commit hash
- task name
- planning source or requirement
- changed files
- public API/CLI/MCP/runtime/hook changes
- tests added or changed
- verification commands and results
- residual risks or deferred items
- next recommended task

If no ledger exists, create one under `docs/superpowers/progress/`.

## Documentation Requirements

Before the goal is complete, update:

- `README.md` for the implemented AITP v5 architecture and user workflow
- `PROJECT_MEMORY.md` for durable repository memory
- relevant specs and plans under `docs/superpowers/`
- hook, MCP, CLI, runtime adapter usage docs
- migration docs explaining old topic content to v5 typed records

Documentation must describe what is implemented, what is intentionally deferred,
and how a user or agent should operate the system.

## Verification Requirements

The goal is not complete until:

- all planned AITP v5 tasks are implemented or explicitly deferred with reasons
- all v5 focused tests pass
- `python -m compileall -q brain\v5` passes
- `git diff --check -- .` passes
- README and core docs match the implemented system
- old topic migration path is implemented and tested
- hook/MCP/CLI/runtime surfaces are documented and tested
- the reviewability ledger is complete enough for GPT/Codex review
- final commits are pushed to the remote repository

Do not treat historical legacy full-suite failures as blockers unless the task
modifies legacy code. Mention them clearly when relevant.

## Blocker Policy

Do not stop for ordinary uncertainty. Investigate, narrow the issue, and continue.
Only mark blocked when the same concrete blocker repeats after multiple attempts
and cannot be resolved without user input or an external-state change.

When blocked, record:

- exact blocker
- attempted fixes
- affected files
- smallest user decision needed
