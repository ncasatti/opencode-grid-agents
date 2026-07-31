# SDD Workflow

This document describes the Spec-Driven Development (SDD) workflow used in The Grid. It covers the seven phases of the pipeline, the memory model, and the sync protocol.

**Status:** Phases 1–3 (`write-spec`, `write-testable-specs`, `write-design`) are implemented. Phases 4–7 (tickets, implement, code-review, archive) are in progress. The memory model and sync protocol are functional for the implemented phases.

## Overview

The workflow is a **seven-phase pipeline** that takes a feature from raw idea to closed-out documentation. It is intermediate between two reference models:

- **`sdd-*` (original The Grid pipeline):** seven phases, granular, with a dedicated archive step.
- **Matt Pocock's `engineering` skills:** five phases, highly consolidated, tracker-first.

The current workflow keeps the granularity of the original (especially the archive step) while borrowing naming, philosophy, and structural patterns from Matt Pocock (the `to-*` / `write-*` prefix family, the distinction between narrative spec and testable specs, ADRs as durable artifacts, the router pattern).

Each phase has a single skill that owns a single artifact. Skills are linked by their inputs and outputs — no skill is allowed to consume artifacts that do not yet exist from a prior phase.

## The 7 Phases

| # | Skill | Mode | Input | Output | Status |
|---|-------|------|-------|--------|--------|
| 1 | `write-spec` | interactive | ongoing conversation | `docs/feats/{feat-name}/spec.md` | implemented |
| 2 | `write-testable-specs` | headless | `spec.md` | `docs/feats/{feat-name}/testable-specs.md` | implemented (conditional) |
| 3 | `write-design` | interactive | `spec.md` (+ optional `testable-specs.md`) | `docs/feats/{feat-name}/design.md` + `docs/adr/NNN-slug.md` | implemented |
| 4 | `write-tickets` | headless | `design.md` | `docs/feats/{feat-name}/tickets.md` or issue tracker | **in progress** |
| 5 | `implement` | TDD loop | tickets | code + tests | **in progress** |
| 6 | `code-review` | model-invoked | PR diff + origin spec | review comments | **in progress** |
| 7 | `archive` | headless | feature artifacts | `docs/feats/{feat-name}/archive.md` | **in progress** |

The `flow-router` skill ([skill/flow-router/SKILL.md](../skill/flow-router/SKILL.md)) maps user intent to a recommended sequence of these skills.

## Memory Model

Data lives in three layers. Each layer has a single responsibility; no data is duplicated across layers.

| Layer | Tool | Single source of truth for… |
|-------|------|------------------------------|
| **Files** | the repository itself (`docs/feats/`, `docs/adr/`) | all feature artifacts and ADRs |
| **codebase-memory-mcp** | structural knowledge graph + ADR index | cross-file code structure + ADR discovery |
| **Engram** | `engram_mem_save` (project scope) | cross-session workflow decisions + session state |

**Why three layers and not one:**

- **Files** are versioned, committable, discoverable by any agent or human reading the repo.
- **codebase-memory-mcp** answers "where is X used across the codebase" and "what ADRs exist about topic T" without scanning the filesystem.
- **Engram** survives session boundaries so that tomorrow's agent knows what today's agent decided.

**What goes where:**

| Information | File | MCP | Engram |
|-------------|------|-----|--------|
| Spec content | yes (`spec.md`) | no | no |
| ADR content | yes (`docs/adr/NNN.md`) | indexed | no |
| ADR reference inside a design | yes (`design.md`) | yes | no |
| Architectural decision rationale (project-level) | no | no | yes |
| Session state ("working on X") | no | no | yes |
| Code structure (functions, modules) | n/a | yes | no |

## Sync Protocol

**Sync 4C** — hybrid, file-first.

| Layer | When | How |
|-------|------|-----|
| Files | every step | the skill writes directly; no sync needed |
| Engram | end of every step | `engram_mem_save` with a 4–5 line structured observation |
| codebase-memory-mcp | end of the whole feature, not per step | `manage_adr` for each ADR + `index_repository` if significant code changed |

**Why deferred MCP sync:** indexing a draft spec is wasted work if it gets rewritten. Wait until the feature is consolidated.

**Exception — write-design:** ADRs are published to MCP as a sub-step of `write-design` itself, not deferred. ADRs are durable decisions of the project, not draft artifacts, and they need to be discoverable the moment they are written.

**When to force an out-of-band sync:**

- User explicitly asks: "sync to MCP" or "save what we did."
- Starting a new session on an old feature: run `index_repository` if the MCP is stale.
- Closing a feature: full sync per the archive skill.

## Quick Start

You have an idea for a feature and want to drive it through the pipeline.

1. **Start a conversation** with the agent. Describe the problem, the proposed solution, any constraints. Discuss until both sides agree.
2. **Invoke `flow-router`** if you are unsure where you are. Otherwise, invoke **`write-spec`** directly.
3. **`write-spec`** will mine the conversation, ask only the gaps, recommend a `feat-name` for confirmation, and write `docs/feats/{feat-name}/spec.md`. It will also score a 4-dimension heuristic and recommend whether `write-testable-specs` is also justified.
4. If testable specs are recommended, run **`write-testable-specs`**. It is headless; you do not need to be present.
5. Run **`write-design`**. It will ask you to confirm tradeoffs (Option A vs Option B) for every major architectural decision. ADRs are written to `docs/adr/` and published to MCP automatically.
6. (In progress) `write-tickets` decomposes the design into vertical slices.
7. (In progress) `implement` runs the TDD loop on each ticket.
8. (In progress) `code-review` reviews the PR against both the spec and the codebase standards.
9. (In progress) `archive` closes the feature, writes a summary, and updates project-level documentation.

## Routing: gbrain vs codebase-memory-mcp

Two code-intel systems are available. Pick based on the question shape.

| Question shape | Use |
|----------------|-----|
| Who calls function X / what does X call | **gbrain** `code_callers` / `code_callees` |
| Where is X defined / all references to X | **gbrain** `code_def` / `code_refs` |
| Cross-file graph, multi-hop | **codebase-memory-mcp** `trace_path` |
| Architecture of a package | **codebase-memory-mcp** `get_architecture` |
| Source of function Z | **codebase-memory-mcp** `get_code_snippet` |
| Find functions by pattern or semantic query | **codebase-memory-mcp** `search_graph` |
| ADRs about topic T | **codebase-memory-mcp** `manage_adr` |

**Default to gbrain** for single-hop file-local questions (callers, callees, defs, refs). **Default to codebase-memory-mcp** for multi-hop, cross-file, or architectural questions. If both could work, prefer gbrain first (cheaper, resolver-grade) and fall back to MCP if gbrain returns nothing.

gbrain has no awareness of codebase-memory-mcp. The two systems are decoupled; only the agent (and `flow-router`) sees both tool sets. The `flow-router/TOOLS.md` file is the canonical routing table.

## File Layout

Per-feature artifacts live under `docs/feats/{feat-name}/`:

```
docs/feats/{feat-name}/
├── spec.md                  # from write-spec (phase 1)
├── testable-specs.md        # from write-testable-specs (phase 2, optional)
├── design.md                # from write-design (phase 3)
├── tickets.md               # from write-tickets (phase 4, in progress)
├── archive.md               # from archive (phase 7, in progress)
└── .archive/                # moved here on archive
```

ADRs are **global** to the project, not per-feature:

```
docs/adr/
├── 001-use-bcrypt-for-passwords.md
├── 002-adopt-grill-with-docs-pattern.md
└── NNN-{slug}.md
```

ADR numbering continues from the highest existing ADR. The `write-design` skill checks before assigning numbers.

## Migration History

The current workflow is the result of consolidating two earlier skill families:

- **The `sdd-*` family** (`sdd-propose`, `sdd-specs`, `sdd-design`, `sdd-tasks`, `sdd-apply`, `sdd-verify`, `sdd-archive`) — the original seven-phase pipeline.
- **The `write-a-prd` / `write-prd` family** — interview-driven PRD creation, later renamed.

The consolidation is tracked in [CHANGELOG.md](../CHANGELOG.md) under `[Unreleased]`. Archived skills are kept under `skill/_legacy/` for reference and rollback during validation.