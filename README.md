# AITP Research Protocol

**AI-assisted Theoretical Physics.** Protocol v4.0.

> 追求真理而非沽名钓誉。 *Pursue truth, not fame.*

AITP is a protocol layer that gives your AI agent the discipline of a good research collaborator: show your sources, justify your claims, don't skip steps, and only call something "known" after it passes gates.

## Quick start

```bash
git clone git@github.com:bhjia-phys/AITP-Research-Protocol.git
cd AITP-Research-Protocol
pip install -e .
```

Then connect it to your AI agent. The MCP server is at `brain/mcp_server.py`.

### Claude Code

Add to `~/.claude/mcp.json` or project `.claude/mcp.json`:

```json
{
  "mcpServers": {
    "aitp": {
      "command": "python",
      "args": ["-m", "brain.mcp_server"],
      "cwd": "/path/to/AITP-Research-Protocol"
    }
  }
}
```

Then `/reload-plugins` in Claude Code.

### Other agents

AITP is agent-agnostic. Any MCP-compatible agent can use it. See `adapters/` for specific setups.

## How to use

### Starting a research topic

1. Tell your AI agent what you want to study. It will call `aitp_bootstrap_topic` to create the topic structure.
2. **L0 — Discover sources.** Register papers, datasets, code. Fill `source_registry.md`.
3. **L1 — Read and frame.** Parse the table of contents for every source. Skim all sections. Deep-extract the relevant ones. Define a bounded question.
4. **L3 — Derive.** Research mode for original work. Study mode for learning from literature.
5. **L4 — Validate.** Submit candidates to adversarial review. Counterargument required.
6. **L2 — Knowledge persists.** Promoted results enter the global L2 knowledge graph. The endpoint of every topic. The starting point of the next.

### Checking progress

```
Ask your AI: "What's the status of this topic?"
```
The AI calls `aitp_get_execution_brief` which returns the gate status, any missing requirements, and a physics-contentful next action.

### Resuming after a break

Just open the topic again. State is stored in plain Markdown files. No database. No session dependency.

### Best practices

- **Push after every feature.** See `skills/aitp-push-after-feature.md` — this exists because we learned the hard way.
- **Start from L2.** Every new topic should check `aitp_query_l2_index` first to discover what's already known.
- **Source everything.** Every L2 node and edge requires a `source_ref`. Provenance is mandatory.

## Protocol stages (v4.0)

```
L0 (discover) → L1 (read → frame) → L3 (derive) ⇄ L4 (validate) → L2 (knowledge)
```

| Stage | What happens | Key artifacts |
|-------|-------------|--------------|
| **L0** | Find and register sources | `source_registry.md`, `L0/sources/*.md` |
| **L1** | TOC-first reading, bounded question, section intake | `source_toc_map.md`, `question_contract.md`, `L1/intake/` |
| **L3** | Derivation (research) or literature study | Subplane artifacts, candidates |
| **L4** | Adversarial validation with mandatory counterargument | Validation contracts, reviews |
| **L2** | Persistent, cross-topic knowledge graph | Nodes, edges, EFT towers |

**L5 (writing/publication) is removed in v4.0.** L2 is the endpoint. The knowledge graph itself is the output. Paper writing is the human's work.

## Two paths to L2

- **Path A (Lightweight):** L0 → L2 directly. For well-understood concepts with clear sources. Use `aitp_quick_l2_concept` to create concept nodes and edges in one call.
- **Path B (Deep):** L0 → L1 → L3 → L4 → L2. For novel or uncertain claims requiring derivation and adversarial review.

## L2 Knowledge Graph

The L2 knowledge graph is the protocol's persistent memory. It stores:

| Node type | Example |
|-----------|---------|
| `concept` | Density Functional Theory, Green's Function |
| `theorem` | Kohn-Sham Equation, Dyson Equation |
| `technique` | GW Approximation, RPA |
| `approximation` | LDA, GGA |
| `result` | AdS/CFT Correspondence |
| `regime_boundary` | DFT validity limits |
| `derivation_chain` | GW self-consistency proof |
| `open_question` | Band gap problem |

Current coverage: 21 nodes across 7 physics domains, 17 typed edges, 1 EFT tower.

## Install / Update / Uninstall

### Install

```bash
git clone git@github.com:bhjia-phys/AITP-Research-Protocol.git
cd AITP-Research-Protocol
pip install -e .
python scripts/aitp-pm.py install
```

The installer detects your environment and deploys hooks, skills, and MCP configs.

### Update

```bash
cd AITP-Research-Protocol
git pull origin main
pip install -e . --upgrade
python scripts/aitp-pm.py update
```

### Uninstall

```bash
cd AITP-Research-Protocol
python scripts/aitp-pm.py uninstall
pip uninstall aitp-kernel
```

This removes hooks, skills, and MCP configs from all detected agents.

### Verify

```bash
aitp doctor
```

Checks: Python version, dependencies, MCP connectivity, topics root, git status.

## Architecture

```
AITP-Research-Protocol/
├── brain/
│   ├── mcp_server.py         # FastMCP server (~3500 lines, 35+ tools)
│   ├── state_model.py        # Gate logic, stage machine, domain taxonomy
│   ├── sympy_verify.py       # Symbolic verification (dimensions, algebra, limits)
│   └── PROTOCOL.md           # Protocol operating manual v4.0
├── skills/                   # Per-stage instructions
│   ├── skill-discover.md     # L0: source discovery
│   ├── skill-read.md         # L1: TOC-first reading workflow
│   ├── skill-l3-*.md         # L3 subplanes (research + study)
│   └── aitp-push-after-feature.md  # Push discipline
├── tests/                    # Test suite (12 files)
├── docs/                     # Specs, guides, design documents
├── adapters/                 # Agent-specific integrations
├── contracts/                # Artifact templates
├── schemas/                  # JSON Schema definitions
└── templates/                # LaTeX templates
```

## Design principles

- **Evidence before confidence.** No claim without provenance.
- **Bounded questions, not open-ended exploration.** Every topic has a contract.
- **Humans own trust.** The promotion gate exists because "the AI seems confident" is not a valid reason.
- **Durable by default.** Research state lives in your filesystem (plain Markdown), not in chat sessions.
- **Agent-agnostic.** Any MCP-speaking agent can drive the protocol.
- **Compiled, not raw.** L2 stores distilled knowledge. Source provenance is stored for auditing but hidden from default queries to prevent context bloat.

## Documentation

| Document | Description |
|----------|-------------|
| [brain/PROTOCOL.md](brain/PROTOCOL.md) | Protocol operating manual (the AI reads this) |
| [docs/superpowers/specs/](docs/superpowers/specs/) | Feature specs |
| [research/knowledge-hub/](research/knowledge-hub/) | Protocol playbooks and contracts |

## License

MIT. See [LICENSE](LICENSE).
