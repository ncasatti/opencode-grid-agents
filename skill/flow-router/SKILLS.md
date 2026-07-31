# Skills Catalog

Four layers, modeled on Matt Pocock's `ask-matt` but condensed for our size.

## Triggers (user-invoked, `disable-model-invocation: true`)

Reach for these when the human explicitly opts in.

| Skill | Trigger | Output |
|---|---|---|
| `flow-router` | "no sé qué skill usar", "¿qué hago?" | recommendation |
| `improve-codebase-architecture` | "revisar la arquitectura", "hay deuda" | HTML report in `$TMPDIR` |
| `grill-with-docs` | "afilá esta idea", "sharpen el plan" | sharpened idea + `docs/CONTEXT.md` / `docs/adr/` updates |

## Vocabulary underneath (model-invoked lenses)

Pulled in automatically when relevant. They supply the **words**, not the process.

| Skill | Provides | When pulled in |
|---|---|---|
| `codebase-design` | module / interface / seam / depth / adapter / leverage / locality vocabulary | any skill designing or auditing modules |
| `domain-modeling` | `docs/CONTEXT.md` (glossary) + `docs/adr/` (decisions) maintenance | any skill that names a term or makes an irreversible decision |

## Main flow (idea → ship, model-invoked)

The route most work travels. Steps 1–4 are live; 5–7 are roadmap.

| # | Skill | Status | Output |
|---|---|---|---|
| 1 | `write-spec` | live | `docs/feats/{feat-name}/spec.md` |
| 2 | `write-testable-specs` | live (conditional) | `docs/feats/{feat-name}/testable-specs.md` |
| 3 | `write-design` | live | `docs/feats/{feat-name}/design.md` + `docs/adr/NNNN-*.md` |
| 4 | `write-tickets` | live | `docs/feats/{feat-name}/tickets.md` |
| 5 | `sdd-apply` | legacy | code + tests (TDD loop) |
| 6 | `sdd-verify` | legacy | test report |
| 7 | `sdd-archive` | legacy | `docs/feats/{feat-name}/archive.md` |

## Standalones (off the main flow)

| Skill | When |
|---|---|
| `tdd` | red-green-refactor on a concrete behaviour, no spec needed |
| `teach` | learn a new concept across multiple sessions, workspace as state |
| `system-auditor` | audit multi-agent consistency, architecture, memory continuity (read-only) |
| `html-generator` | mirror repo markdown to `docs/html/` (static docs site) |
| `changelog-format` | write/update `CHANGELOG.md` per Keep a Changelog v1.1 |
| `pro-docs` | write/update repo docs per our two-tier convention |
| `nextjs-15` | Next.js App Router patterns |
| `pytest` | Python test patterns |
| `nix` | NixOS / flakes |
| `clingy` | build interactive CLIs with fzf menus |
| `mcp-builder` | author MCP servers |
| `skill-authoring` / `agent-authoring` | meta: write skills or agents |
| `codebase-memory` | graph query patterns for `codebase-memory-mcp` |
| `conversation-formatter` | standard for chat messages and transcripts |
| `conventional-commits` | commit message format |
| `prd-to-issues` | break a PRD into issues |

## Roadmap (not yet adopted)

These exist in `to-review/mattpocock-skills/` but aren't part of The Grid yet. Adopt when the gap appears.

| Skill | Would fill the gap |
|---|---|
| `implement` | replaces `sdd-apply` with sub-agent-per-ticket pattern |
| `code-review` | replaces `sdd-verify` with two-axis (Standards + Spec) review |
| `triage` | incoming issues / bug reports |
| `diagnosing-bugs` | hard bugs that resist a first glance |
| `wayfinder` | huge foggy efforts that don't fit one session |
| `prototype` | throwaway code to settle a design question |
| `research` | delegate reading legwork to a background agent |
| `handoff` | compact a conversation into a markdown file for a fresh session |
| `grill-me` | grilling without a codebase (stateless) |
| `ask-matt` reference | the "navigable encyclopedia" pattern; future migration target |

## Migration target

`flow-router` currently routes by **trigger / lens / phase / standalone**. The end state is the `ask-matt` pattern: **main flow + on-ramps + vocabulary + crossing sessions + precondition**. Out of scope for now.
