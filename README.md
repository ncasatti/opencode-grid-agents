# The Grid: OpenCode Agent System

![The Grid](docs/assets/the-grid.png)

**Version:** 1.4
**Status:** System Online (Master Control Program Active)
**Interactive Docs:** [The Grid Agents](https://ncasatti.github.io/opencode-grid-agents/)

## Overview

Welcome to **The Grid**, User. This is a modular agent system created for OpenCode. 
Unlike traditional assistants, The Grid operates under a strict orchestration architecture inspired by the Tron universe (1982). 

You interact with a single central program—the **Master Control Program (MCP)**—which analyzes, reasons, and delegates execution to specialized programs (sub-agents) operating in the shadows synchronously or asynchronously. The MCP is cold, technical, and direct. It speaks in terms of cycles, sectors, I/O processes, and data streams. Zero corporate filter.

---

## The Programs (Active Roster)

The following programs are currently in active service:

| Archivo | Alias (Lore) | Rol | Responsabilidad |
|---------|--------------|------|----------------|
| `clu` | Clu | System Administrator | Technical Planner, SDD generation, and task orchestration. |
| `dumont` | Dumont | Technical Writer | Documentation generation, READMEs, and architecture reports. |
| `tron` | Tron | Heavy Builder | Complex code, business logic, and architectural refactors. |
| `quorra` | Quorra | Archivist | Skill creation, prompt engineering, and knowledge standardization. |

### Legacy / Review Programs
The following programs are currently in legacy mode or reserved for review purposes:
`librarian`, `planner`, `researcher`, `reviewer`, `sysadmin`, `tron-lite`, `version-control`.

---

## Skills Directory (Active)

The passive abilities (pure knowledge) loaded into the system as of version 1.4:

### SDD Pipeline (Workflow)

The current workflow is documented in [docs/sdd-workflow.md](docs/sdd-workflow.md). Quick index:

- `flow-router`: User-invoked router. Recommends which skill to invoke and routes code-intel queries between gbrain and codebase-memory-mcp. See [SKILLS.md](skill/flow-router/SKILLS.md), [TOOLS.md](skill/flow-router/TOOLS.md), [SYNC.md](skill/flow-router/SYNC.md).
- `write-spec`: Synthesizes a spec from an ongoing conversation. Output: `docs/feats/{feat-name}/spec.md`. Interactive.
- `write-testable-specs`: Reads `spec.md` and produces `testable-specs.md` (RFC 2119 + delta specs). Conditional — recommended by a 4-dimension heuristic in `write-spec`. Headless.
- `write-design`: Produces `design.md` + ADRs in `docs/adr/`. Publishes ADRs to `codebase-memory-mcp`. Interactive.

**In progress** (not yet migrated): tickets, implement, code-review, archive.

### General Skills
- `agent-authoring`: Guide for creating and maintaining Claude Code agents.
- `changelog-format`: Keep a Changelog v1.1 standard.
- `clingy`: Context-aware CLI framework expert.
- `conventional-commits`: Strict standard for commit messages.
- `mcp-builder`: Guide for creating high-quality MCP servers.
- `nextjs-15`: Next.js 15 App Router patterns.
- `pytest`: Pytest testing patterns for Python.
- `skill-authoring`: Strict structural rules for new skills.

---
> "End of line."
