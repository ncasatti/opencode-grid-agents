# Sync Protocol — The 3 Layers

After every workflow step, data lives in one of three layers. Apply these rules strictly.

## The 3 layers

1. **Files in repo** (`docs/feats/{feat-name}/*`, `docs/adr/*`) — single source of truth for all artifacts
2. **codebase-memory-mcp** — indexes ADRs + structural code knowledge
3. **Engram** (project scope) — cross-session memory of workflow decisions + session state

## Sync rules (Sync 4C — hybrid)

| Layer | When | How |
|---|---|---|
| **Files** | At every step | The skill writes directly. No sync needed. |
| **Engram** | At end of every step | `engram_mem_save` with the step summary (4–5 lines, structured format) |
| **MCP** | At end of the **whole feature**, not per step | `codebase-memory-mcp manage_adr` for each ADR + `codebase-memory-mcp index_repository` if significant code changed |

## Rationale

- **Files first**: everything is derived from files. Files are versioned, committable, discoverable.
- **Engram always**: cheap, doesn't add friction, gives cross-session memory.
- **MCP deferred**: indexing a draft spec is wasted work if it gets rewritten. Wait until feature is consolidated.

## What goes where (no duplication)

| Type of info | File | MCP | Engram |
|---|---|---|---|
| Spec content | ✅ `spec.md` | ❌ | ❌ |
| ADR content | ✅ `docs/adr/NNN.md` | ✅ indexed | ❌ |
| ADR reference in feature | ✅ `design.md` | ✅ | ❌ |
| Workflow decision (e.g. "we use bcrypt") | ❌ | ❌ | ✅ |
| Session state ("working on X") | ❌ | ❌ | ✅ (session_start) |
| Code structure (functions, modules) | n/a | ✅ | ❌ |

## When to force a sync outside the protocol

- User explicitly asks: "sync to MCP" or "save what we did"
- Starting a new session on an old feature: `index_repository` if MCP is stale
- Closing a feature: full sync per archive skill
- After `write-design` step: ADRs MUST be published to MCP (sub-step of that skill, not deferred)