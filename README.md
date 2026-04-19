<div align="center">
  <img src="./.github/assets/aitp-mark.svg" width="116" alt="AITP AI monogram" />
  <h1>AITP Research Charter and Kernel</h1>
  <p><strong>A research protocol that turns your AI coding agent into a disciplined theoretical-physics collaborator — one that keeps evidence separate from conjecture, remembers your topics across sessions, and only promotes results to trusted memory after you approve them.</strong></p>
  <p>
    <a href="#how-it-works">How it works</a> ·
    <a href="#protocol-and-current-implementation">Protocol & Implementation</a> ·
    <a href="#installation">Installation</a> ·
    <a href="#current-use-paths">Using AITP</a> ·
    <a href="#the-basic-workflow">Workflow</a> ·
    <a href="#research-model">Research Model</a> ·
    <a href="#whats-inside">What's Inside</a> ·
    <a href="#philosophy">Philosophy</a> ·
    <a href="#read-next">Docs</a>
  </p>
</div>

<p align="center">
  <img src="./.github/assets/aitp-hero.svg" width="100%" alt="AITP protocol-first research kernel hero with AI monogram" />
</p>

<p align="center">
  <a href="https://github.com/bhjia-phys/AITP-Research-Protocol/stargazers"><img src="https://img.shields.io/github/stars/bhjia-phys/AITP-Research-Protocol?style=flat-square&labelColor=0B1220&color=FFC857" alt="GitHub stars" /></a>
  <a href="https://github.com/bhjia-phys/AITP-Research-Protocol/network/members"><img src="https://img.shields.io/github/forks/bhjia-phys/AITP-Research-Protocol?style=flat-square&labelColor=0B1220&color=7EE8F2" alt="GitHub forks" /></a>
  <a href="https://github.com/bhjia-phys/AITP-Research-Protocol/issues"><img src="https://img.shields.io/github/issues/bhjia-phys/AITP-Research-Protocol?style=flat-square&labelColor=0B1220&color=FF9B71" alt="GitHub issues" /></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/license-MIT-EAF4FF?style=flat-square&labelColor=0B1220" alt="MIT License" /></a>
  <img src="https://img.shields.io/badge/kernel-L0--L4-9CF6EC?style=flat-square&labelColor=0B1220" alt="L0 to L4 kernel" />
  <img src="https://img.shields.io/badge/research-protocol--first-8BEFF7?style=flat-square&labelColor=0B1220" alt="Protocol-first" />
</p>

## How it works

It starts when you describe what you want to study — in plain language, the way you would explain it to a colleague. AITP takes that description and turns it into a bounded research topic with a clear question, scope, and validation plan. You don't need to learn any special commands; just talk.

Once the topic is set up, your AI agent does the actual research work — gathering sources, reading papers, sketching derivations, or running benchmarks — inside a layered protocol that keeps every piece of evidence traceable. Exploratory notes and tentative claims stay clearly labeled as such. Nothing gets promoted to "trusted" status just because the agent sounds confident.

When the work reaches a natural checkpoint, AITP presents what it found, what gaps remain, and whether the results are ready for your review. You decide what gets promoted to reusable memory. This is the human gate — the agent executes, but you own the trust decisions.

Everything is durable. You can close your laptop, come back days later, say "continue this topic," and the agent picks up exactly where it left off — with full context of what was done, what was decided, and what is still open. For the full experience, see [`docs/USER_TOPIC_JOURNEY.md`](docs/USER_TOPIC_JOURNEY.md).

## Protocol and Current Implementation

This repository contains both:

1. the **AITP research protocol**
2. the **current public reference implementation** of that protocol

The protocol is the durable contract: layers, trust boundaries, promotion
rules, runtime artifacts, and the rule that evidence stays separate from
conjecture.

The implementation is what you actually run today:

- the installable kernel under [`research/knowledge-hub/`](research/knowledge-hub/)
- the `aitp` and `aitp-mcp` entrypoints
- the runtime scripts and topic-shell materialization
- the current Codex / OpenCode / Claude Code / OpenClaw front doors

The important boundary is:

- the protocol is the durable model
- the current Python kernel and front-door integrations are one implementation
  of that model

Another implementation would still count as AITP only if it preserves the same
layer semantics, durable artifact model, evidence boundaries, and governed
promotion into trusted memory.

## Installation

### Kernel Install

```bash
python -m pip install aitp-kernel
aitp --version
aitp doctor
```

Optional PaperQA-backed topic consultation is available on Python 3.11+:

```bash
python -m pip install "aitp-kernel[paperqa]"
aitp consult-paperqa --topic-slug <topic_slug> --query-text "<question>" --llm anthropic/claude-3-5-sonnet-20240620
```

Then install the platform adapter you use:

### Codex (recommended)

```bash
aitp install-agent --agent codex --scope user
```

See [`.codex/INSTALL.md`](.codex/INSTALL.md) for details.

### OpenCode

Add to your `opencode.json`:

```json
{ "plugin": ["aitp@git+https://github.com/bhjia-phys/AITP-Research-Protocol.git"] }
```

See [`.opencode/INSTALL.md`](.opencode/INSTALL.md) for details.

### Claude Code

```bash
aitp install-agent --agent claude-code --scope user
```

This path now installs both the SessionStart bootstrap and the native Claude
Code AITP MCP registration.

See [`docs/INSTALL_CLAUDE_CODE.md`](docs/INSTALL_CLAUDE_CODE.md) for details.

### OpenClaw

```bash
aitp install-agent --agent openclaw --scope user
```

See [`docs/INSTALL_OPENCLAW.md`](docs/INSTALL_OPENCLAW.md) for details.

For contributor/local-dev editable installs, Windows-specific instructions,
migration from older installs, and troubleshooting, see
[`docs/INSTALL.md`](docs/INSTALL.md).

### What `aitp doctor` Means

`aitp doctor` is the current install/bootstrap truth surface.

Use it to confirm:

- the kernel is installed correctly
- the fixed protocol roots are present
- your selected front door is wired correctly
- the current machine has enough structure to run the bounded first-use path

Important boundary:

- `aitp doctor` proves **front-door readiness**
- it does **not** by itself prove deep-execution parity across every runtime

For machine-readable inspection, run:

```bash
aitp doctor --json
```

## Current Use Paths

The current implementation supports three honest entry styles.

### 1. Agent-front-door usage

After installing the adapter for Codex, OpenCode, Claude Code, or OpenClaw,
you can start from a natural-language request inside that agent surface.

That is the most protocol-native experience:

- describe the idea
- let AITP route it into a bounded topic
- continue through the topic shell and runtime protocol artifacts

### 2. Explicit topic bootstrap

If you want the most direct CLI path from idea to topic:

```bash
aitp bootstrap --topic "<topic>" --statement "<initial idea or question>"
aitp loop --topic-slug <topic_slug> --human-request "Continue with the next bounded step."
aitp status --topic-slug <topic_slug>
```

This is the current verified first-run path for the public kernel.

Useful follow-up reads:

- `aitp replay-topic --topic-slug <topic_slug>`
- `aitp capability-audit --topic-slug <topic_slug>`
- `aitp paired-backend-audit --topic-slug <topic_slug>`
- `aitp h-plane-audit --topic-slug <topic_slug>`
- `aitp compile-source-catalog`
- `aitp trace-source-citations --canonical-source-id <canonical_source_id>`
- `aitp compile-source-family --source-type paper`
- `aitp export-source-bibtex --canonical-source-id <canonical_source_id>`
- `aitp import-bibtex-sources --topic-slug <topic_slug> --bibtex-path <path-to-bib-file>`
- `aitp consult-paperqa --topic-slug <topic_slug> --query-text "<question>" --llm anthropic/<model>`

### 3. Lightweight idea-first exploration

If the idea is still too loose for full topic bootstrap:

```bash
aitp explore "Sketch the idea before opening a full topic loop."
```

That writes a lightweight exploration carrier instead of the full topic shell.
When the idea becomes specific enough, promote it into normal topic work with
`promote-exploration` or start a full topic explicitly.

## The Basic Workflow

1. **Topic bootstrap** — You describe what you want to study. AITP sets up a research topic with a bounded question, scope, and validation contract. No special commands needed.

2. **Source acquisition (L0)** — AITP gathers papers, notes, and upstream references. Everything is traceable back to its origin.

3. **Analysis and exploration (L1, L3)** — The agent reads, annotates, sketches derivations, or runs benchmarks. Exploratory outputs are clearly labeled as candidates, not conclusions.

4. **Validation and trust audit (L4)** — When results look promising, AITP runs explicit checks — consistency, convergence, reproduction — before asking whether the work is ready.

5. **Promotion to reusable memory (L2)** — Only after your explicit approval does material move into long-term trusted memory. The agent cannot promote on its own.

## Research Model

AITP keeps research state in layers instead of flattening everything into one chat transcript.

| Layer | Purpose | What goes here |
| --- | --- | --- |
| **L0** | Source acquisition | papers, notes, upstream code references |
| **L1** | Provisional understanding | analysis notes, derivation sketches |
| **L3** | Exploratory outputs | candidate claims, tentative material |
| **L4** | Validation and trust audit | checks, benchmarks, human decisions |
| **L2** | Long-term trusted memory | promoted knowledge, reusable workflows |

The default route is `L0 → L1 → L3 → L4 → L2`. Layer 2 is intentionally last — exploratory work does not become reusable memory just because the agent sounds confident.

```mermaid
flowchart LR
    A[Research question] --> B[aitp bootstrap]
    B --> C[L0 source traces]
    C --> D[L1 provisional analysis]
    D --> E[L3 candidate outputs]
    E --> F[L4 validation and trust audit]
    F --> G{Human approval gate}
    G -->|approved| H[L2 reusable memory]
    G -->|not yet| E
```

## What's Inside

### Three Research Lanes

The same protocol kernel drives different categories of theoretical-physics work.

| Lane | Typical inputs | Validation | Trusted output |
| --- | --- | --- | --- |
| **Formal theory and derivation** | papers, definitions, prior claims | proof-gap analysis, consistency checks | semi-formal theory objects, Lean-ready packets |
| **Toy-model numerics** | model specs, observables, scripts | convergence checks, benchmarks | validated workflows, reusable operations |
| **Code-backed algorithm development** | upstream codebases, existing methods | reproduction, trust audit | trusted methods, backend writeback |

### Capabilities

- **Multi-topic runtime** — Work on several research topics in one workspace. Switch between them with natural language.
- **Cross-session memory** — Every topic survives session resets. Resume days later with full context.
- **Lean-ready export** — Bridge validated theory results into Lean 4 declaration packets with proof-obligation sidecars.
- **Bounded autonomous execution** — Run multi-step research loops with explicit human gates at decision points (OpenClaw).
- **L1 three-layer vault** — Materialize raw/wiki/output intake vaults with explicit flowback receipts on the existing topic-shell path.
- **Statement compilation before proof repair** — Compile bounded theory statements into declaration skeletons and explicit proof-repair plans before Lean-facing export.
- **L2 compiler helpers** — Seed and inspect reusable knowledge views with commands like `aitp seed-l2-direction --direction tfim-benchmark-first`, `aitp consult-l2 --query-text "TFIM exact diagonalization benchmark workflow" --retrieval-profile l3_candidate_formation`, `aitp compile-l2-graph-report`, and `aitp compile-l2-knowledge-report`.
- **Domain skill interface** — Plug domain-specific physics skills (GW workflows, transport calculations) into AITP through a structured contract interface.

### Domain Skills

AITP separates research lifecycle management from domain knowledge. Domain skills provide physics-specific contracts, operations, and invariants.

| Skill | Domain | Link |
| --- | --- | --- |
| **oh-my-LibRPA** | ABACUS + LibRPA GW/RPA workflows | [GitHub →](https://github.com/AroundPeking/oh-my-LibRPA) |

The domain skill interface protocol is documented in [`research/knowledge-hub/DOMAIN_SKILL_INTERFACE_PROTOCOL.md`](research/knowledge-hub/DOMAIN_SKILL_INTERFACE_PROTOCOL.md).

### Runtime Support

| Runtime | Install path | Role |
| --- | --- | --- |
| **Codex** | [`.codex/INSTALL.md`](.codex/INSTALL.md) | Baseline — cleanest end-to-end experience |
| **OpenCode** | [`.opencode/INSTALL.md`](.opencode/INSTALL.md) | Plugin-based natural-language routing |
| **Claude Code** | [`docs/INSTALL_CLAUDE_CODE.md`](docs/INSTALL_CLAUDE_CODE.md) | SessionStart bootstrap |
| **OpenClaw** | [`docs/INSTALL_OPENCLAW.md`](docs/INSTALL_OPENCLAW.md) | Bounded autonomous research loops |

Run `aitp doctor --json` to check what is converged on your machine.

Current baseline: Codex.
Parity target: Claude Code and OpenCode.
Specialized lane: OpenClaw.
`aitp doctor` reports front-door readiness only. Deep-execution parity is a
separate surface.
Across Codex, Claude Code, and OpenCode, the front door now publishes the same
plain-language human-control posture and autonomous-continuation posture in
`session_start.generated.md` and `runtime_protocol.generated.md`.
When no real checkpoint is active, AITP should continue bounded work without
ritual reconfirmation; in `verify + iterative_verify`, the bounded L3-L4 loop
is allowed to keep cycling until success, a real blocker, or a real human
checkpoint appears.
The current bounded parity probes are available for Claude Code and OpenCode
via `python research/knowledge-hub/runtime/scripts/run_runtime_parity_acceptance.py --runtime <runtime> --json`.
The cross-runtime closure report is available via
`python research/knowledge-hub/runtime/scripts/run_runtime_parity_audit.py --json`.
The bounded L1 raw/wiki/output vault acceptance is available via
`python research/knowledge-hub/runtime/scripts/run_l1_vault_acceptance.py --json`.
The bounded L1 assumption/reading-depth acceptance is available via
`python research/knowledge-hub/runtime/scripts/run_l1_assumption_depth_acceptance.py --json`.
The bounded L1 method-specificity acceptance is available via
`python research/knowledge-hub/runtime/scripts/run_l1_method_specificity_acceptance.py --json`.
The bounded L1 concept-graph intake acceptance is available via
`python research/knowledge-hub/runtime/scripts/run_l1_concept_graph_acceptance.py --json`.
The bounded Layer 0 source-catalog acceptance is available via
`python research/knowledge-hub/runtime/scripts/run_source_catalog_acceptance.py --json`.
The bounded runtime transition/demotion acceptance is available via
`python research/knowledge-hub/runtime/scripts/run_transition_history_acceptance.py --json`.
The bounded promotion-gate human-modification acceptance is available via
`python research/knowledge-hub/runtime/scripts/run_human_modification_record_acceptance.py --json`.
The bounded competing-hypotheses acceptance is available via
`python research/knowledge-hub/runtime/scripts/run_competing_hypotheses_acceptance.py --json`.
The bounded statement-compilation acceptance is available via
`python research/knowledge-hub/runtime/scripts/run_statement_compilation_acceptance.py --json`.

The machine-readable install view exposes:

- `runtime_convergence`
- `deep_execution_parity`
- `full_convergence_repair`
- `runtime_support_matrix.runtimes.<runtime>.remediation`
- `runtime_support_matrix.deep_execution_parity.runtimes.<runtime>.status`

Windows local-checkout note:

- `scripts\aitp-local.cmd doctor`
- `scripts\aitp-local.cmd bootstrap --topic "<topic>" --statement "<statement>"`

Useful runtime audit entrypoints once a topic exists:

- `aitp capability-audit --topic-slug <topic_slug>`
- `aitp paired-backend-audit --topic-slug <topic_slug>`
- `aitp h-plane-audit --topic-slug <topic_slug>`

## Philosophy

- **Evidence before confidence** — sources stay separate from speculation at every layer
- **Bounded steps, not freestyle** — every unit of work has a clear question and scope
- **Humans own trust** — nothing becomes reusable memory without explicit approval
- **Durable by default** — research state survives session resets and machine changes
- **Light until it matters** — ordinary work stays minimal; the runtime only expands when something important happens
- **Externalized knowledge** — implementation-critical knowledge that papers leave implicit gets written into spec artifacts before code
- **Absolutely reproducible** — every conversation, every spec, every code version is preserved with structured naming

## Current Status

- Ships one public reference implementation of the AITP protocol under `research/knowledge-hub`
- Supports Codex, OpenCode, Claude Code, and OpenClaw front doors over the same kernel
- Has a verified first-run path: `bootstrap -> loop -> status`
- Has a verified lightweight idea-first path: `explore -> promote-exploration`
- Has an explicit human approval gate before `L2` promotion
- Bridges into the [Theoretical-Physics-Knowledge-Network](https://github.com/bhjia-phys/Theoretical-Physics-Knowledge-Network) formal-theory backend

What is mostly done:

- protocol surface coverage for the current `L0-L4` kernel
- install/bootstrap/front-door adoption surface
- runtime control plane, `H-plane`, layer graph, and route-transition visibility

What is not yet fully proven:

- real-topic end-to-end research utility across `L0 -> L1 -> L3 -> L4 -> L2`
- deep-execution parity on every non-Codex runtime
- full maturity of the `L2` knowledge surface and statement-compilation pipeline

## Contributing

AITP stabilizes the research protocol, not one frozen implementation. Contributions that preserve the layer model, durable artifacts, evidence boundaries, and governed promotion gates are welcome.

See [`docs/CHARTER.md`](docs/CHARTER.md) for what counts as disciplined AI-assisted theoretical-physics work.
See [`docs/AITP_GSD_WORKFLOW_CONTRACT.md`](docs/AITP_GSD_WORKFLOW_CONTRACT.md)
for the boundary between research-topic work in AITP and implementation work
in GSD.

## License

MIT License — see [`LICENSE`](LICENSE) file for details.

## Read Next

- [`docs/QUICKSTART.md`](docs/QUICKSTART.md) — detailed walkthrough with a real topic
- [`docs/USER_TOPIC_JOURNEY.md`](docs/USER_TOPIC_JOURNEY.md) — what AITP feels like in practice
- [`docs/INSTALL.md`](docs/INSTALL.md) — all installation details and troubleshooting
- [`docs/PUBLISH_PYPI.md`](docs/PUBLISH_PYPI.md) — public package build and release workflow
- [`docs/CHARTER.md`](docs/CHARTER.md) — the full research charter
- [`docs/architecture.md`](docs/architecture.md) — technical architecture
- [`docs/MULTI_TOPIC_RUNTIME.md`](docs/MULTI_TOPIC_RUNTIME.md) — multi-topic runtime behavior
- [`docs/MIGRATE_MULTI_TOPIC.md`](docs/MIGRATE_MULTI_TOPIC.md) — migration notes for multi-topic state
- [`research/knowledge-hub/L5_PUBLICATION_FACTORY_PROTOCOL.md`](research/knowledge-hub/L5_PUBLICATION_FACTORY_PROTOCOL.md) — publication/output layer contract
- [`docs/AITP_GSD_WORKFLOW_CONTRACT.md`](docs/AITP_GSD_WORKFLOW_CONTRACT.md) — when to use AITP vs GSD
- [`docs/AITP_WORKFLOW_SHELL_AND_PROTOCOL_KERNEL.md`](docs/AITP_WORKFLOW_SHELL_AND_PROTOCOL_KERNEL.md) — why the UX converges on Superpowers' install shape
- [`docs/roadmap.md`](docs/roadmap.md) — development roadmap
- [`research/knowledge-hub/DOMAIN_SKILL_INTERFACE_PROTOCOL.md`](research/knowledge-hub/DOMAIN_SKILL_INTERFACE_PROTOCOL.md) — domain skill interface specification
- [`research/knowledge-hub/EXTERNALIZED_SPEC_PROTOCOL.md`](research/knowledge-hub/EXTERNALIZED_SPEC_PROTOCOL.md) — externalized specification and reproducibility protocol
- [`research/knowledge-hub/FIRST_PRINCIPLES_LANE_PROTOCOL.md`](research/knowledge-hub/FIRST_PRINCIPLES_LANE_PROTOCOL.md) — ABACUS+LibRPA domain protocol
- [`research/knowledge-hub/FEATURE_DEVELOPMENT_PLAYBOOK.md`](research/knowledge-hub/FEATURE_DEVELOPMENT_PLAYBOOK.md) — 9-phase feature development playbook
- [**oh-my-LibRPA**](https://github.com/AroundPeking/oh-my-LibRPA) — ABACUS+LibRPA domain skill with chat-native workflow orchestration
