# AITP Research Protocol

**AI-assisted Theoretical Physics.** Protocol v4.1.

> 追求真理而非沽名钓誉。 *Pursue truth, not fame.*

AITP is a protocol layer that gives your AI agent the discipline of a good research collaborator: show your sources, justify your claims, don't skip steps, and only call something "known" after it passes gates.

## Architecture: Four-Layer Harness

```
CLI 强制、MCP 便利、Skill 指导、Hook 监视
```

| Layer | Role | Can block? |
|-------|------|:---:|
| **CLI** (`brain/cli/`) | Enforcement engine. Preflight + state validator + Pydantic contracts. Sole path that can change topic state. | Hard block |
| **MCP** (`brain/mcp_server.py`) | Convenience layer. Parameter parsing + dispatch. ~55 tools (from 76), 26 with `@require_stage`. | Forwards to CLI |
| **Skill** (`skills/*.md`, `deploy/skills/`) | Guidance. Pure text injection. Red flags, CLI command mappings, domain constraints. | Advisory only |
| **Hook** (`hooks/`) | Surveillance. SessionStart: injects gateway skill. Stop: writes HUD state + logs. | Post-hoc detection |

### Harness components

| Component | Location | Purpose |
|-----------|----------|---------|
| Preflight engine | `brain/cli/preflight.py` | 10 registered checks. Stage/gate/activity validation. Conditional preflight (`when` dict matching). |
| State manager | `brain/cli/state.py` | Authoritative source for stage/lane/activity/gate. Atomic writes (tempfile + os.replace). Validated transitions (L0→L1→L3→L4⇄L3→promotion→L2). |
| Pydantic contracts | `brain/cli/contracts.py` | `CandidateContract` (extra="forbid", chain validation). `ReviewContract` (5 required physics checks for pass). |
| Stage decorators | `brain/cli/decorators.py` | `@require_stage` (STAGE_PERMISSIONS + LANE_OVERRIDES). `@with_preflight` (command policy enforcement). |
| Command policies | `brain/commands/*.md` (21 files) | YAML frontmatter: stage, gate, preflight checks, allowed tools, blocking conditions. |
| Agent templates | `brain/agents/*.md` (4 files) | Algebraic/Physical/Numerical Verifier + Skeptic. YAML frontmatter with tool allowlists. |
| HUD | `~/.aitp/hud_state.json` | Written by Stop hook. Real-time status panel. |
| Observability | `brain/cli/observability.py` | JSONL event logging per session. |

## Quick start

**One-liner (Claude Code):**

```bash
git clone git@github.com:bhjia-phys/AITP-Research-Protocol.git && cd AITP-Research-Protocol && AITP_TOPICS_ROOT=~/research/aitp-topics python scripts/aitp-pm.py install
```

This auto-detects your AI agents, deploys all hooks/skills/config, and registers a global `aitp` CLI command.

Step by step:

```bash
git clone git@github.com:bhjia-phys/AITP-Research-Protocol.git
cd AITP-Research-Protocol

# Non-interactive (recommended for CI/scripts):
AITP_TOPICS_ROOT=~/research/aitp-topics python scripts/aitp-pm.py install

# Interactive (prompts for topics root):
python scripts/aitp-pm.py install

# Single agent only:
python scripts/aitp-pm.py install --agent claude-code
```

After install, use `aitp` from anywhere:

```bash
aitp doctor     # Full health check
aitp status     # Show what's installed
aitp update     # Re-sync deployed files
aitp upgrade    # Git pull + re-deploy
aitp uninstall  # Remove everything
```

### Manual MCP setup

If you prefer to wire the MCP server yourself, add to `~/.claude/mcp.json` or project `.mcp.json`:

```json
{
  "mcpServers": {
    "aitp": {
      "command": "python",
      "args": ["/path/to/AITP-Research-Protocol/brain/mcp_server.py"]
    }
  }
}
```

Then run `/reload-plugins` in Claude Code.

## Protocol stages (v4.1)

```
L0 (discover) → L1 (read → frame) → L3 (derive) ⇄ L4 (validate) → L2 (knowledge)
```

| Stage | What happens | Key artifacts |
|-------|-------------|--------------|
| **L0** | Find and register sources | `source_registry.md`, `L0/sources/*.md` |
| **L1** | TOC-first reading, bounded question, section intake | `source_toc_map.md`, `question_contract.md`, `L1/intake/` |
| **L3** | Derivation (research) or literature study. 8 activities: ideate, plan, derive, trace-derivation, gap-audit, connect, integrate, distill | Subplane artifacts, candidates |
| **L4** | Adversarial validation (3 Verifiers + Skeptic) + independent execution | Reviews, computational reports |
| **L2** | Persistent, cross-topic knowledge graph | Nodes, edges, EFT towers |

**L5 (writing/publication) is removed in v4.1.** L2 is the endpoint. The knowledge graph itself is the output.

## Two-speed design

| | Lightweight | Heavyweight |
|---|:---:|:---:|
| **Preflight** | None (advisory only) | Hard block (stage + gate + checks) |
| **Commands** | `sympy check`, `l2 ask`, `source discover`, `quick compute`, `session resume` | `source registry`, `question frame`, `derive pack`, `candidate submit`, `verify run/results`, `promote` |
| **Use case** | Exploration, quick checks, reading | Stage boundaries, claims, promotion |

## Lane differentiation

| | code_method | formal_theory |
|---|:---:|:---:|
| **Bash:remote (SSH/HPC)** | Yes | No |
| **Domain invariants** | Mandatory | Skipped |
| **SymPy verification** | N/A | Core |
| **L4 execution** | compute prepare→submit→check→validate→report | sympy execute + l2 cross-check |
| **Compute target** | local / fisher / dongfang / kouxiang | local / fisher |

## Study vs Research mode

Set via `candidate_type` on `aitp candidate submit`:

| | Study Mode | Research Mode |
|---|---|---|
| **candidate_type** | `atomic_concept` / `derivation_chain` | `research_claim` |
| **L4 verification** | 1 adversarial reader + source anchoring + coverage | 3 Verifiers + Skeptic |
| **Use case** | Understanding known results | Producing new claims |

## Agent Team (L4 Verification)

Four specialized agents with worktree isolation:

| Agent | Role | Strategy |
|-------|------|----------|
| **Algebraic Verifier** | Step-by-step algebra, dimensional consistency, source anchoring | Derivation chain audit |
| **Physical Verifier** | Limits, symmetries, conservation laws, L2 cross-reference | Physics sanity checks |
| **Numerical Verifier** | Tier-1 (param consistency) + Tier-2 (HPC output) | Computational audit |
| **Skeptic** | Claim-only blind review, L2 access only, contradiction-first | Adversarial: find what's wrong |

Disagreement matrix: `unanimous_pass` → promote. `divergent` → human decides. `incomplete` → retry. Non-pass returns to L3 with structured feedback (≤3 cycles).

## Research loop (L3⇄L4)

```
L3: derive → candidate submit
    ↓
L4: execute + verify (3 Verifiers + Skeptic)
    ↓
    ├── pass → promotion → L2
    ├── fail → structured feedback → L3 (gap-audit), cycle++
    └── ≤3 cycles → human escalation
```

## CLI commands (21)

```bash
# Topic lifecycle
aitp topic init <slug> --lane code_method|formal_theory --intensity quick|standard|full
aitp topic lane <slug> <lane>         # Switch research lane mid-project

# Session management
aitp session resume <slug>            # Restore topic context + recent log events
aitp session list                     # All active topics
aitp session status                   # Current topic binding

# State management
aitp state show <topic>               # Full topic state
aitp state advance <topic> <stage>    # L0→L1→L3→L4→promotion
aitp state retreat <topic> <stage>    # Retreat preserving all artifacts
aitp gate check <topic>               # Gate readiness
aitp gate override <topic> --reason "..." --scope current_gate|this_session|permanent

# L0 — Source discovery
aitp source add --id <id> --title <title> --type paper|code|data
aitp source discover --query "..." --max 10   # arXiv API search
aitp source registry                  # Coverage assessment
aitp source read --source <id>        # Quick-read a source

# L1 — Reading & framing
aitp source parse-toc --source <id> --sections "..."
aitp source extract --source <id> --section <name> --content "..." --confidence high
aitp source extract-all --source <id> # List pending sections
aitp question frame --question "..." --scope "..." --targets "..."
aitp convention lock --add "convention: ..."
aitp anchor map --source <id> --equation "Eq.X" --note "..."
aitp contradiction register --source-a <id1> --source-b <id2> --conflict "..."
aitp source cross-map

# L3 — Derivation workspace
aitp derive record --step D1 --input "..." --output "..." --source "ref:Eq" --justification approximation
aitp derive pack --candidate-id <id> --chain default
aitp candidate submit --candidate-id <id> --type research_claim|atomic_concept --claim "..."
aitp sympy check dim|algebra|limit "<expr>"
aitp sympy execute --candidate <id>  # Batch formal verification (L4)
aitp switch-activity ideate|plan|derive|trace-derivation|gap-audit|connect|integrate|distill
aitp quick compute --expr "<python code>"  # Sandboxed execution
aitp memory steer|decide|pitfall --text "..."

# L4 — Verification
aitp verify run --candidate <id>      # Spawn Verifier + Skeptic agents (JSON)
aitp verify results --candidate <id>  # Build disagreement matrix
aitp promote --candidate <id>         # Promote to L2 (requires Skeptic pass)

# L4 — Computation (code_method lane)
aitp compute prepare --candidate-id <id>  # Generate Slurm script + audit
aitp compute submit --candidate-id <id>   # Local run or HPC handoff
aitp compute check --candidate-id <id>    # Check output files
aitp compute validate --candidate-id <id> # Parse outputs, compare to claim
aitp compute report --candidate-id <id>   # Aggregate computational report

# L2 — Knowledge graph
aitp l2 ask "<query>"                # Search knowledge base
aitp l2 node-create --node-id <id> --title "..." --node-type concept
aitp l2 edge-create --edge-id <id> --from-node <id> --to-node <id> --edge-type derives_from
aitp l2 merge <topic>                # Merge topic subgraph to global L2
aitp l2 query "<substring>"          # Raw graph search

# Maintenance
aitp migrate <topic>                  # v0.6 → v1.0 protocol migration
aitp notebook generate <topic>        # Generate flow notebook
```

## Repository structure

```
AITP-Research-Protocol/
├── brain/
│   ├── cli/                     # CLI enforcement engine (Phase 0-5)
│   │   ├── __init__.py          # argparse router, 20+ commands
│   │   ├── state.py             # Stage transitions, atomic writes
│   │   ├── preflight.py         # Preflight engine, 10 registered checks
│   │   ├── contracts.py         # Pydantic CandidateContract, ReviewContract
│   │   ├── decorators.py        # @require_stage, @with_preflight
│   │   ├── observability.py     # JSONL event logging
│   │   ├── _dispatch_helpers.py # MCP→CLI dispatch
│   │   ├── migrate.py           # v0.6→v1.0 protocol migration
│   │   └── commands/            # 9 command modules (source, reading, framing, l3_workflow, sympy, memory, verify, compute, l2)
│   ├── commands/                # 23 command policy files (YAML frontmatter + intensity_override)
│   ├── agents/                  # 4 verifier agent templates
│   ├── mcp_server.py            # MCP server — ~55 tools (from 76), HTTP transport
│   ├── state_model.py           # Backward-compatible re-export layer
│   ├── gates.py                 # Stage gate evaluation (L0/L1/L3/L4)
│   ├── contracts.py             # Artifact templates, required headings (legacy)
│   ├── PROTOCOL.md              # Protocol operating manual v4.1
│   └── L2_ARCHITECTURE_v5.md    # L2 v5 faceted knowledge base design
├── hooks/                       # Agent hook scripts
│   ├── session_start.py         # Injects gateway skill + topic context
│   ├── stop.py                  # Writes hud_state.json + session logs
│   ├── compact.py               # Context compaction handler
│   ├── aitp_event.py            # Offline event recording (no MCP dependency)
│   └── hook_utils.py            # Shared hook utilities
├── skills/                      # Protocol skills (auto-discovered + deployed)
│   ├── skill-discover.md        # L0: source discovery
│   ├── skill-read.md            # L1: TOC-first reading workflow
│   ├── skill-frame.md           # L1: framing — conventions and contradictions
│   ├── skill-l3-*.md            # L3 activities (ideate, plan, analyze, gap-audit, integrate, distill)
│   ├── skill-validate.md        # L4: adversarial validation
│   ├── skill-promote.md         # L2 promotion gate
│   ├── skill-l2-entry.md        # L2 knowledge entry and retrieval
│   ├── skill-librpa.md          # Domain skill: ABACUS+LibRPA
│   └── skill-continuous.md      # Resume after session break
├── deploy/                      # Unified deployment source
│   ├── skills/                  # Gateway skills: using-aitp, aitp-runtime
│   ├── hooks/                   # Generated hooks
│   ├── runners/                 # Shell/batch runners
│   ├── config/                  # Hook configuration (hooks.json)
│   └── templates/               # Agent-specific template overrides
├── scripts/
│   ├── aitp-pm.py               # Package manager (install/update/upgrade/uninstall)
│   ├── aitp / aitp.cmd          # CLI entry wrappers
│   └── generate_l2_viz.py       # L2 graph visualization
├── docs/                        # Specs, guides, design documents
├── tests/                       # Test suite (141 passing)
└── schemas/                     # JSON Schema definitions
```

## Design principles

- **Evidence before confidence.** No claim without provenance.
- **Bounded questions, not open-ended exploration.** Every topic has a contract.
- **Humans own trust.** The promotion gate exists because "the AI seems confident" is not a valid reason.
- **Durable by default.** Research state lives in your filesystem (plain Markdown), not in chat sessions.
- **Agent-agnostic.** Any MCP-speaking agent can drive the protocol.
- **Compiled, not raw.** L2 stores distilled knowledge. Source provenance is stored for auditing but hidden from default queries.

## Implementation status

| Phase | Status | Key deliverables |
|:---:|:---:|------|
| Phase 0 | 🟢 97% | CLI engine + gate_override + preflight + session + topic init/lane + migrate + @require_stage×26 + @with_preflight×3 |
| Phase 1 | 🟢 97% | 11 L0-L1 commands + arXiv source discover + 23 policy files + intensity_override + nested source extract |
| Phase 2 | 🟢 98% | 6 L3 commands + HUD stop hook + sandboxed quick compute + log events in session resume |
| Phase 3 | 🟢 100% | 4 agent templates + verify-run/results + promote + Skeptic gate + Study/Research mode |
| Phase 4 | 🟢 70% | Two-speed wired + unified path resolution + MCP dispatch 7/11 + L4 compute 5 commands + observability |
| Phase 5 | 🟢 85% | L2 graph + notebook + compute pipeline + sympy execute + source_refs propagation |

**Last audited**: 2026-05-05 by 5 review agents + 3 E2E test agents. 28/28 audit findings resolved. 11/11 E2E tests passed.
| Phase 3 | 🟡 95% | 4 agent templates (complete) + verify-run/results/promote |
| Phase 4 | 🟡 40% | `@require_stage` on 29 tools. MCP thinning not done (76 tools). MCP/CLI are independent implementations. |
| Phase 5 | 🟡 60% | L2 node/edge/merge/query + notebook scaffold. Compute commands are all stubs. |

**Last audited**: 2026-05-05 by 5 independent review agents (architecture consistency, protocol correctness, implementation completeness, physics workflow realism, code quality & integration). 28 findings: 9 critical, 9 high, 7 medium, 3 low.

Full audit details in [aitp-harness-final.md](D:/BaiduSyncdisk/Theoretical-Physics/obsidian-markdown/07 Share_work/aitp-harness-final.md).

## Known issues (from 5-agent audit)

All 28 audit findings resolved. See [aitp-harness-final.md](D:/BaiduSyncdisk/Theoretical-Physics/obsidian-markdown/07 Share_work/aitp-harness-final.md) for full details.

## Documentation

| Document | Description |
|----------|-------------|
| [brain/PROTOCOL.md](brain/PROTOCOL.md) | Protocol operating manual |
| [aitp-harness-final.md](D:/BaiduSyncdisk/Theoretical-Physics/obsidian-markdown/07 Share_work/aitp-harness-final.md) | Complete architecture plan + audit findings |
| [docs/](docs/) | Feature specs, design documents |

## License

MIT. See [LICENSE](LICENSE).
