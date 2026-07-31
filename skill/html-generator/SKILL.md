---
name: html-generator
description: Renders an interactive HTML mirror of the project's Markdown documentation (the pro-docs README + docs/ tree) into docs/html/, styled with the "Brutalist Command" terminal aesthetic. Self-contained pages, no build step. The Markdown is the source of truth; this skill only mirrors it. Use when rendering or publishing docs as an interactive web site, mirroring the README and docs to HTML, generating a GitHub Pages doc site, or producing a styled documentation portal.
version: 2.0.0
---

# Static HTML Generator

This skill is a **rendering layer**, not a standalone doc system. It produces an interactive HTML **mirror** of the Markdown documentation authored with `pro-docs` — the Markdown (`README.md` + `docs/**/*.md`) is the single source of truth; the HTML is derived from it, never the reverse. The agent is the builder: it writes self-contained `.html` files directly using the patterns defined in `theme/`. There is no script, no `npm install`, no runtime — every output loads its CSS via the Tailwind CDN.

## Theme Path (Reference Only)

The theme lives at a fixed absolute path. The agent reads from it; it never copies the files into the project.

- Design bible: `~/.the-grid/programs/skill/html-generator/theme/DESIGN.md`
- Snippet library: `~/.the-grid/programs/skill/html-generator/theme/COMPONENTS.md`
- Full-page examples: `~/.the-grid/programs/skill/html-generator/theme/examples/{readme,reference,architecture}.html`
- Visual references: `~/.the-grid/programs/skill/html-generator/theme/assets/*.png`

## Standard Project Layout (Mandatory)

The HTML mirror lives entirely under `docs/html/`, mirroring the Markdown tree one-to-one — same slug, same position, `.html` instead of `.md`:

```
README.md              →  docs/html/index.html          (landing)
docs/<slug>.md         →  docs/html/<slug>.html          (archetype by Diátaxis mode)
docs/<dir>/<slug>.md   →  docs/html/<dir>/<slug>.html    (tree preserved)
```

The Markdown under `docs/` is the source and is **never touched** by this skill. The HTML under `docs/html/` is the derived mirror — regenerate it when the Markdown changes (the Markdown wins). Commit the `docs/html/` tree to the repo. For GitHub Pages, set `Settings → Pages → Source: /docs/html`.

## Quick Start

| Content type | Archetype | Hero variant | CRT overlay |
|---|---|---|---|
| Project README / landing | `landing` | Solid cyan headline | No |
| API reference / CLI docs | `reference` | Side-bordered with crumb | No |
| Architecture / ADR / system spec | `architecture` | White headline + cyan period | Yes |

## Discovery Protocol (Agent-First)

The agent gathers requirements before producing any file. It generates content dynamically from the conversation; pre-existing HTML files are honored when present.

### Phase 1 — Mirror Audit

Discover the source structure, then mirror it. Resolve before writing any file:

1. **Read the source.** Enumerate the `pro-docs` Markdown: `README.md` (the index) and every `docs/**/*.md`. This set defines the pages to render — do not invent pages the Markdown doesn't have.
2. **Check the mirror.** Does `docs/html/` already hold rendered `.html`? If yes → offer to regenerate (re-sync with the Markdown) or extend.
3. **Map each source file to an archetype** via its Diátaxis mode (see the Archetype Selection Map). `README.md` → `index.html` (`landing`).
4. **Note constraints.** Any pages to exclude from the mirror, or extra interactive sections to add.

If no `pro-docs` Markdown exists yet, say so and recommend authoring it first (with the `pro-docs` skill) — the mirror has nothing to reflect without a source.

### Phase 2 — Execution

1. Create `docs/html/` (mirroring any subdirectories of `docs/`) if missing.
2. For each source page (from Phase 1):
   - Open the matching `theme/examples/<archetype>.html` as a structural reference.
   - Open `theme/COMPONENTS.md` to copy the exact snippet patterns needed.
   - Open `theme/DESIGN.md` for any color, typography, or spacing decision not covered by a snippet.
   - Render the Markdown content into the complete `.html` file at its mirror path (`docs/html/<slug>.html`). No external CSS, no JS bundles, no build step. Tailwind and Space Grotesk are loaded inline via CDN inside the file.
3. **Mirror the links:** `index.html` reproduces the README's navigation index (one entry per page); every other page links back to `index.html` ("Return to Entry Point"); cross-links between pages match the Markdown's cross-links.
4. **Register in the index:** ensure the source `README.md` links to `docs/html/index.html` as the interactive docs (per the `pro-docs` skill).
5. Report output paths to the User.

### Sample Discovery Dialogue

> **Agent:** I see the source docs: `README.md`, `docs/installation.md`, and `docs/reference.md`. I'll mirror them into `docs/html/`. Confirm, or tell me which to skip.
> **User:** All three. Go.
> **Agent:** Writing `docs/html/index.html` (mirror of `README.md`, `landing` archetype) with the cyan-headline hero and navigation tiles; `docs/html/installation.html` (mirror of `docs/installation.md`, `landing`); and `docs/html/reference.html` (mirror of `docs/reference.md`, `reference` archetype) with the side-bordered hero and flag list. Each secondary page links back to `index.html`, and I'll add the `docs/html/index.html` link to the README. Standalone HTML, no build step.

## Archetype Selection Map

Pick each page's archetype from the Diátaxis mode of its source Markdown:

| Source doc (Diátaxis mode) | Archetype |
|---|---|
| `README.md` / index / overview | `landing` |
| Reference (`docs/reference.md`, `docs/api.md`, `docs/keys/*`) | `reference` |
| Explanation (`docs/architecture.md`, `docs/design.md`) | `architecture` |
| How-to / Tutorial (`docs/getting-started.md`, `docs/troubleshooting.md`) | `landing` |

Layout signatures per archetype:

| Archetype | Use for | Layout signature | Reference file |
|---|---|---|---|
| `landing` | Landing pages, project entrypoints, general docs | TopNavBar + SideNavBar + cyan-headline hero + bento card grid + footer | `theme/examples/readme.html` |
| `reference` | API docs, technical references, CLI docs | TopNavBar + SideNavBar + side-bordered hero + bento (endpoints, flags, contracts) | `theme/examples/reference.html` |
| `architecture` | System specs, ADRs, design docs | SideNavBar + TopNavBar + cyan-period hero + bento (overview, directory map, data flow) + CRT overlay + vignette | `theme/examples/architecture.html` |

## Build Recipe (per page)

For every `.html` file the agent produces, follow this sequence:

1. **Boilerplate.** Start from the matching `theme/examples/<archetype>.html`. Replace placeholder titles, copy, and links with the User's content.
2. **Hero.** Pick the hero variant from `COMPONENTS.md §4` that matches the archetype. Do not mix variants.
3. **Body.** Drop in the prose paragraphs, then assemble the bento grid using snippets from `COMPONENTS.md §5`. Keep the 12-column rhythm; vary column spans to create asymmetry.
4. **Specialty blocks.** Add reference-specific (endpoints, flag list, contracts) or architecture-specific (directory tree, data flow, CRT overlay) blocks from `COMPONENTS.md §7–§11`.
5. **Footer.** Pick `§10a` for landing pages or `§10b` for versioned reference / architecture pages.
6. **Cross-links.** Confirm every internal link resolves to a real sibling file.

## Theme Contract — "The Brutalist Command"

The User will see:
- Background `#050505`, surface panels `#0A0A0A`, accent cyan `#00FFFF`.
- Strict monospace-feeling typography (Space Grotesk family), uppercase headers, cyan period accents.
- Zero rounded corners, no easing curves — `transition-duration: 0ms` everywhere; `transition-none` is the default Tailwind class.
- `architecture` archetype adds a global CRT scanline overlay and corner vignette.
- Tonal stacking instead of shadows. The "No-Line" rule: layout boundaries are background shifts, not 1px lines. The only sanctioned hairline is `border-[#4B5563]/15` for ghost borders inside panels.

Reference: `theme/DESIGN.md` for the full design system; `theme/COMPONENTS.md §1` for the color token table.

## Operational Constraints

- **Mirror only.** Never create, edit, or delete the Markdown source (`README.md`, `docs/**/*.md`); this skill writes only under `docs/html/`. The Markdown is owned by `pro-docs`.
- **Self-contained output.** Every `.html` file must work when opened directly in a browser with no companion files. CSS is loaded via the Tailwind CDN inside the file; fonts via Google Fonts; no local JS bundles.
- **No build step.** Do not introduce `package.json`, `node_modules`, build scripts, or watchers.
- **No frameworks.** No React, no Vue, no static-site generators. Plain HTML and Tailwind utility classes only.
- **Version control.** Never staged or committed by this skill. All `git` actions remain manual.
- **Idempotency.** Re-running the agent for the same page must produce equivalent output for equivalent input. Do not add timestamps or random IDs to the markup unless the User asks.

## Theme Files Reference

| File | Role |
|---|---|
| `theme/DESIGN.md` | The design bible — palette, typography, elevation, do/don't. |
| `theme/COMPONENTS.md` | The snippet library — copy-ready HTML fragments with usage notes. |
| `theme/examples/readme.html` | A complete rendered landing page. Open it side-by-side while building. |
| `theme/examples/reference.html` | A complete rendered reference page. |
| `theme/examples/architecture.html` | A complete rendered architecture page. |
| `theme/assets/*.png` | Screenshots of the rendered examples. |

End of line.
