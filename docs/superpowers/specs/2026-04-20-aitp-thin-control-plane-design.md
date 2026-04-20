# AITP Thin Control Plane Design

Status: working design

Date: 2026-04-20

## Goal

Add a thin project-level control plane around AITP's existing topic kernel so
that multiple active topics can be monitored, dispatched, resumed, and
remediated without weakening AITP's epistemic model.

The target outcome is:

- AITP remains protocol-first and topic-truth-root-first;
- single-topic `L0/L1/L2/L3/L4` semantics stay authoritative;
- cross-topic operator visibility and execution follow-up become materially
  stronger;
- notebook and validation gaps can become explicit actionable work instead of
  staying buried inside topic-local reports.

This is a control-plane addition, not a research-model rewrite.

## Problem Statement

AITP already has strong single-topic protocol surfaces:

- topic truth roots,
- topic dashboards,
- research reports,
- unfinished work,
- pending decisions,
- decision ledgers,
- action queues,
- notebook-facing obligation closure,
- and explicit promotion / validation doctrine.

But the current public shape is still weak in three operator-facing ways.

### 1. Cross-topic visibility is too thin

AITP can explain one topic well, but it does not yet offer a compact
project-level view across several active topics:

- what is blocked,
- what is waiting on the human,
- what has actionable next work,
- what has gone stale,
- and which topics are close to a meaningful evidence return.

### 2. Dispatch semantics are still fragmented

AITP can already decide next actions and dispatch bounded execution, but the
surfaces for:

- automation,
- external execution,
- future channel delivery,
- reminders,
- and resumable follow-up

are not yet unified under one thin dispatch contract.

### 3. Obligation gaps are visible but not operational enough

The new notebook-facing protocols make missing scientific blocks explicit, but
many of those gaps still terminate as passive report content rather than as
durable remediation work.

Short form:

- AITP is already strong as a topic kernel;
- it is not yet strong enough as a multi-topic operating surface.

## Design Objectives

### 1. Preserve AITP semantics

The control plane must not flatten:

- `L0/L1/L2/L3/L4`,
- promotion gates,
- validation routes,
- topic truth roots,
- or notebook-facing obligation doctrine

into generic workflow states.

### 2. Reuse existing topic artifacts

The new layer should derive from current topic-local truth surfaces rather than
requiring parallel manual data entry.

### 3. Make blockers actionable

A scientifically meaningful missing block should be able to become a durable,
dispatchable remediation task with status and replay pointers.

### 4. Support gradual runtime expansion

The first version should stay local, file-backed, and compatible with current
CLI/runtime patterns.

### 5. Avoid a generic research OS rewrite

AITP should not attempt to become a full `project -> workflow -> task` system
in the ResearchClaw sense. The new control plane should stay thin and topic-led.

## Non-Goals

This design does not aim to:

- replace topic-local truth with a project database;
- replace layer semantics with generic workflow stages;
- introduce a new top-level memory model for conversations or notes;
- add a heavy web app or channel platform in this phase;
- claim autonomous remediation execution before the task contracts are robust.

## Current Judgment

### What AITP already does better than a generic research OS

- evidence and conjecture are explicitly separated;
- promotion is gated rather than implicit;
- notebook/report surfaces are increasingly scientist-readable;
- topic-local derivation, validation, and obligation closure are protocolized.

### What a thin control plane can add without semantic damage

- cross-topic status compression,
- dispatch normalization,
- remediation task surfacing,
- staleness and blocker tracking,
- and better operator follow-through.

### What should not be copied from ResearchClaw

- generic workflow stages such as `paper_reading` or `result_analysis` as a new
  outer truth model;
- conversation-centric memory as a substitute for AITP epistemic artifacts;
- a large independent runtime boundary before AITP has matured the smaller
  control-plane contracts.

## Proposed Architecture

The thin control plane consists of three additions.

### A. Cross-topic control index

Add a derived cross-topic index that summarizes each active topic using existing
topic-owned runtime artifacts.

Suggested surfaces:

- `runtime/control_plane/topic_control_index.json`
- `runtime/control_plane/topic_control_index.md`
- `runtime/control_plane/blocker_queue.json`
- `runtime/control_plane/blocker_queue.md`

Each topic entry should derive from existing surfaces such as:

- `topic_state.json`
- `topic_dashboard.md`
- `research_report.active.md`
- `unfinished_work.json`
- `pending_decisions.json`
- `failure_classification.json`

The control index should expose, at minimum:

- topic slug,
- current bounded objective,
- current layer / route status,
- most recent evidence return,
- open decision count,
- open unfinished-work count,
- blocked or stale status,
- remediation count,
- and primary next action pointer.

This is a derived operator view, not a new source of truth.

### B. Unified dispatch contract

Add a thin dispatch target contract for any execution or follow-up path that
needs to hand work to an agent, automation run, or future channel surface.

Suggested machine surface:

- `runtime/control_plane/dispatch_targets.json`

Suggested contract fields:

- `target_kind`
- `topic_slug`
- `action_ref`
- `task_ref`
- `dispatch_surface`
- `session_ref`
- `writeback_paths`
- `reply_required`
- `retry_policy`
- `cooldown_policy`

The purpose is not to invent a large runner framework. The purpose is to let:

- `dispatch_execution_task.py`,
- future automation,
- future reminder or heartbeat surfaces,
- and later channel delivery

share one minimal routing language.

### C. Notebook-obligation remediation bridge

Turn notebook-facing missing blocks into explicit remediation tasks when the
missing block is operationally actionable.

Examples:

- missing source anchors in a `source_restoration_round`,
- missing derivation spine in a `derivation_round`,
- missing observable definition or anomaly analysis in a
  `numerical_or_benchmark_round`,
- synthesis prose that lacks supporting rounds or excluded-route accounting.

Suggested surfaces:

- `topics/<slug>/runtime/remediation_tasks.json`
- `topics/<slug>/runtime/remediation_tasks.md`
- derived entries in the cross-topic blocker queue

Each remediation task should carry:

- originating round or artifact,
- missing block,
- why it matters,
- whether it blocks claim use,
- recommended next round type,
- bounded task statement,
- execution eligibility,
- and expected writeback artifact(s).

The bridge should only materialize tasks for actionable missing blocks.
Purely interpretive or high-level scientific uncertainty should remain visible
as an obligation, not be converted into fake taskability.

## Data Model Principles

### 1. Topic truth remains local

All scientific truth remains under `topics/<slug>/`.

### 2. Control-plane state is mostly derived

The cross-topic control plane should be regenerated from topic artifacts
wherever possible.

### 3. New writable state stays thin

The main new writable surfaces should be limited to:

- remediation task ledgers,
- dispatch receipts,
- and control-plane index materializations.

### 4. No parallel claim or evidence graph

AITP should continue to treat its own candidate, validation, and promotion
artifacts as the authority. The control plane should point at them rather than
mirror them into a new graph store.

## Runtime Behavior

### Cross-topic status update

On bootstrap, resume, and significant topic writeback, AITP should refresh the
cross-topic control index.

### Remediation materialization

When notebook/report compilation or obligation closure detects an actionable
blocking gap, AITP should:

1. preserve the normal topic-local report statement,
2. create or refresh a remediation task entry,
3. add or update the blocker queue projection,
4. avoid duplicate task explosion for the same unresolved gap.

### Dispatch and writeback

When a remediation task or next action is dispatched, AITP should record:

- what was sent,
- where it was sent,
- what artifacts are expected back,
- and how completion or failure should be written into topic-local truth.

## Error Handling And Guardrails

### 1. No silent task inflation

The system must not create new remediation tasks on every render pass for the
same unresolved gap.

### 2. No semantic demotion

The control plane must not replace scientific statuses such as blocked,
qualified, or promotion-ineligible with flatter generic task states.

### 3. No ghost completion

A remediation task should not close merely because a dispatch occurred. It
closes only when its expected writeback artifacts or status conditions are met.

### 4. No cross-topic truth leakage

The cross-topic dashboard may summarize a topic, but it must not become the
place where scientific details are maintained or corrected.

## Testing Strategy

The first implementation pass should prove:

- cross-topic index materialization from multiple topics with different states;
- blocker queue generation from unfinished work, pending decisions, and
  notebook-facing obligations;
- remediation deduplication across repeated renders;
- dispatch receipt recording and replay pointers;
- writeback-driven task closure;
- and compatibility with current topic-local runtime artifacts.

The strongest early tests should be fixture-driven runtime tests rather than UI
tests.

## Phased Implementation Shape

### Phase 1. Read-only cross-topic index

- derive multi-topic summary surfaces;
- no new dispatch logic yet;
- no remediation execution yet.

### Phase 2. Remediation task bridge

- generate topic-local remediation ledgers from actionable notebook/report gaps;
- project them into the blocker queue.

### Phase 3. Unified dispatch receipts

- normalize dispatch target contracts and writeback expectations for bounded
  execution tasks and remediation tasks.

## Decision

AITP should evolve as:

- a strong topic kernel,
- plus a thin derived control plane.

It should not evolve as:

- a generic research OS that replaces its own epistemic doctrine.

## Open Questions

1. Which existing topic-local artifact should be treated as the canonical
   source for "last meaningful evidence return"?
2. Should remediation task generation happen during notebook/report build,
   during orchestration, or in a dedicated post-pass?
3. How much dispatch normalization is needed before a real channel surface is
   worth adding?
