# Tool Routing: gbrain vs codebase-memory-mcp

Two code-intel systems coexist in the user's setup. Pick based on the question shape.

## Decision rule

| Question shape | Use | Why |
|---|---|---|
| "Who calls function X?" / "What does X call?" | **gbrain** `code_callers` / `code_callees` | resolver-grade, single-hop, fast |
| "Where is X defined?" / "All references to X" | **gbrain** `code_def` / `code_refs` | resolver-grade for renames / impact analysis |
| "Cross-file graph: who calls what across the codebase?" | **codebase-memory-mcp** `trace_path` | structural graph, multi-hop |
| "What's the architecture of package Y?" | **codebase-memory-mcp** `get_architecture` | Leiden clusters, package overview |
| "Show me the source of function Z" | **codebase-memory-mcp** `get_code_snippet` | full source, post-resolution |
| "Find functions matching pattern / semantic query" | **codebase-memory-mcp** `search_graph` | BM25 + semantic |
| "ADRs about topic T" | **codebase-memory-mcp** `manage_adr` | ADR-specific tool |

## Practical guidance

- **Default to gbrain** for single-hop, file-local questions (callers, callees, defs, refs).
- **Default to codebase-memory-mcp** for multi-hop, cross-file, or architectural questions.
- **For ADRs**: use `manage_adr` in codebase-memory-mcp. Source of truth lives in `docs/adr/` files; the MCP indexes them.
- **If both could work**: prefer gbrain first (cheaper, resolver-grade), fall back to MCP if gbrain returns nothing.

## Context from the project

- gbrain is a TypeScript RAG system at `/home/flyn/.the-grid/systems/opensource/gbrain`.
- gbrain has NO awareness of codebase-memory-mcp. The two systems are decoupled — only the agent (and this router) sees both tool sets.
- For dual setups, the practical pattern is: "for cross-file structural graph → codebase-memory-mcp `trace_path`; for semantic/sinks → gbrain `code_*`".