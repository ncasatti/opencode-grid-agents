---
name: pro-docs
description: Standard for creating, editing, and standardizing professional software documentation (READMEs, references, architecture docs, guides). Defines a two-tier file-naming convention, Diátaxis structure, and verifying docs against the codebase. Use when writing, updating, refactoring, auditing, fixing stale docs, renaming doc files, or standardizing any Markdown documentation.
---

# Professional Software Documentation

## Quick start

This skill governs the full doc lifecycle — creating, editing, standardizing, and verifying documentation. Adhere to the **Minimum Viable Documentation** principle: write short, useful, accurate documents. Structure content with the **Diátaxis** framework — separate Tutorials (learning), How-to guides (problem), Technical reference (information), and Explanation (understanding); never mix modes in one section.

## File naming

Two tiers — apply consistently, never mix:

- **Root sentinel files → `UPPERCASE`:** `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`, `SECURITY.md`, and agent files (`CLAUDE.md`, `AGENTS.md`). Tooling recognizes them and they sort to the top.
- **Everything under `docs/` → `lowercase-kebab-case.md`:** e.g. `docs/architecture.md`, `docs/getting-started.md`, `docs/api-reference.md`. URL-safe; avoids cross-filesystem case bugs.

A doc inside `docs/` is never `UPPERCASE`; a sentinel file is never lowercase. See [REFERENCE.md](REFERENCE.md) for the rationale.

## Verify against the source

Docs drift from code over time. When a doc and the code disagree, **the code wins** — fix the doc and cite `file:line`. Verify claims against the codebase before documenting them as fact.

## Workflows

### 1. Planning Documentation
- [ ] **Identify the Audience:** Determine if the user needs a tutorial, how-to, reference, or explanation (Diátaxis).
- [ ] **Choose the Right File:** Don't create monolithic files. Use `README.md` (sentinel) plus `docs/installation.md`, `docs/reference.md`, `docs/architecture.md`, etc. (lowercase-kebab).
- [ ] **Avoid Duplication:** Never repeat information. Link to existing docs.

### 2. Writing Content
- [ ] **Write for Humans:** Use clear, plain language. List the simplest use case first.
- [ ] **Format Consistently:** Use proper Markdown headings (`#`, `##`, `###`), bolding for critical paths, and syntax-highlighted code blocks.
- [ ] **Use Tables:** Present environment variables, API parameters, or feature comparisons in Markdown tables.

### 3. Structuring the Repository
- [ ] **README.md:** The entry point. Include description, badges, prerequisites, fast install, basic usage, and navigation links.
- [ ] **Navigation:** Include back-links to `README.md` in all sub-documents. Add a Table of Contents for long files.
- [ ] **Index everything:** The README navigation links every `docs/` page. If a `CHANGELOG.md` exists, link it. If an interactive HTML mirror exists (`docs/html/index.html`), link it too.

## Advanced features

For detailed architectural principles, repository structure, and formatting rules, see [REFERENCE.md](REFERENCE.md).