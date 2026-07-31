# Changelog

All notable changes to The Grid will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added

- **`flow-router` skill** — user-invoked router with four files (`SKILL.md`, `SKILLS.md`, `TOOLS.md`, `SYNC.md`). Maps user intent to skill sequences and routes code-intel queries between gbrain and codebase-memory-mcp.
- **`write-spec` skill** — synthesizes a spec from an ongoing conversation. Interactive mode. Output: `docs/feats/{feat-name}/spec.md`. Includes a 4-dimension heuristic that recommends whether testable specs are also needed.
- **`write-testable-specs` skill** — headless skill that reads `spec.md` and produces `testable-specs.md` with delta specs (ADDED/MODIFIED/REMOVED), RFC 2119 keywords, and REQ-NNN traceability IDs.
- **`write-design` skill** — interactive skill that produces `design.md` and ADRs in `docs/adr/`. Tradeoff rationale (Option A vs Option B) is mandatory for every major decision. ADRs are published to `codebase-memory-mcp` via `manage_adr`.
- **`docs/sdd-workflow.md`** — documentation of the full workflow, memory model, and sync protocol.
- **Sync 4C protocol** — hybrid sync: files written directly per step, Engram auto-save at end of every step, MCP sync deferred to end of feature. ADRs are an exception (published to MCP as a sub-step of `write-design`).

### Changed

- **SDD Pipeline consolidated** — the original `sdd-propose` + `sdd-specs` + `sdd-design` family has been replaced by the new `write-*` workflow.
- **`sdd-design` migrated** — renamed to `write-design`, with new responsibilities: ADR generation in `docs/adr/`, MCP publishing, and Engram sync. Execution mode changed from `headless` to `interactive` because architecture decisions require user input on tradeoffs.
- **`sdd-archive`, `sdd-apply`, `sdd-tasks`, `sdd-verify`** — still in their original form, pending migration. Will be addressed in a follow-up to align with the new `write-*` naming.

### Deprecated

- **`sdd-propose`** — interview-driven PRD creation, replaced by `write-spec` (synthesis from conversation).
- **`sdd-specs`** — replaced by the two-layer model: `write-spec` (narrative) + `write-testable-specs` (RFC 2119 formalism).
- **`write-a-prd`** — the user's original PRD skill, superseded by `write-spec`.

### Removed

- **Stale `write-prd` (named `write-a-prd` in its frontmatter)** — moved to `_legacy/write-a-prd/`. Its replacement is `write-spec`.

### Archived

- `sdd-propose/` → `_legacy/sdd-propose/`
- `sdd-design/` → `_legacy/sdd-design/` (after migration to `write-design/`)
- `write-a-prd/` (formerly `write-prd/`) → `_legacy/write-a-prd/`