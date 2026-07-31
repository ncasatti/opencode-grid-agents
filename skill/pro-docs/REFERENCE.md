# Documentation Guidelines: Professional Software Documentation

## 1. Core Architectural Principles

When creating documentation, you must adhere strictly to these principles:

- **Minimum Viable Documentation:** Write short, useful documents. It is better to have a small set of highly accurate, fresh documentation than a massive repository of outdated text. Cut out redundant information.
- **Separation of Concerns:** Categorize content based on user needs into four distinct forms: *Tutorials* (learning-oriented), *How-to guides* (problem-oriented), *Technical reference* (information-oriented), and *Explanation* (understanding-oriented). Do not mix these modes within the same section.
- **Write for Humans First:** Use clear, plain language and avoid unnecessary jargon. Always list the simplest, most common use case first before diving into advanced configurations.
- **Duplication is Evil:** Never repeat information. If a concept or process is explained in another file or section, use a hyperlink to point the user to the original source.
- **Verify Against the Source:** Documentation drifts from code. Never document from memory or assumption — verify each claim against the codebase. When a doc and the code disagree, the code wins: fix the doc and cite `file:line`.

## 2. File Naming Convention

Apply a strict two-tier convention so every doc in the repo is named consistently:

- **Root sentinel files → `UPPERCASE`.** `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, and agent files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`). Rationale: (1) uppercase sorts first in ASCII, so they float to the top of a file listing; (2) hosts like GitHub recognize and render them specially; (3) they visually "shout" *read me first*.
- **Everything under `docs/` → `lowercase-kebab-case.md`.** e.g. `docs/getting-started.md`, `docs/api-reference.md`, `docs/architecture.md`. Rationale: URL-safe slugs, and it avoids case-sensitivity bugs between case-insensitive (macOS/Windows) and case-sensitive (Linux) filesystems that silently break links.

Never mix tiers: a file inside `docs/` is never `UPPERCASE`; a recognized sentinel is never lowercase.

## 3. Core Repository Structure

Do not create monolithic files. Break the documentation into logical, modular files that serve specific purposes:

- **`README.md` (The Entry Point):**
  - *Purpose:* Orients the new user to the project and acts as a central dispatcher.
  - *Contents:* A self-explaining project name, a concise description of what the project does, badges (e.g., build status), prerequisites, the fastest installation method, basic usage examples, and support/contact information.
  - *Navigation:* Must include a quick navigation table or list linking to all other documentation files.
- **`docs/getting-started.md` (or `docs/installation.md`):**
  - *Purpose:* Step-by-step onboarding.
  - *Contents:* Detailed setup instructions separated by platform/environment, environment variable configuration, and dependency requirements.
- **`docs/reference.md` (or `docs/api.md`):**
  - *Purpose:* The comprehensive technical reference.
  - *Contents:* API endpoints, CLI command flags, database schemas, or code contracts. This defines *what* the software does, listing parameters, expected outputs, and errors.
- **`docs/architecture.md` (or `docs/design.md`):**
  - *Purpose:* System design and theoretical models (Explanation).
  - *Contents:* High-level overviews of how the system works under the hood, data flow, and directory structure.
- **`docs/troubleshooting.md`:**
  - *Purpose:* Problem-solving (How-to guides).
  - *Contents:* Common error messages, what they mean, and specific steps or commands to resolve them.
- **`CONTRIBUTING.md`:**
  - *Purpose:* Guidelines for collaborators.
  - *Contents:* How to set up a development environment, run tests, lint code, and submit changes.

## 4. Navigation and Linking

To ensure users can easily navigate the documentation ecosystem:

- **Back-links:** Every sub-document must contain a clear link back to the main `README.md` at the very top.
- **Cross-referencing:** Link directly to related documents instead of recreating context.
- **Tables of Contents:** For longer documents, always include a Table of Contents right after the introduction to help users scan.
- **Index all artifacts:** The README index links every `docs/` page, plus `CHANGELOG.md` (if present) and the interactive HTML mirror at `docs/html/index.html` (if present). These are produced by sibling skills (`changelog-format`, `html-generator`) but indexed here.

## 5. Markdown Styling & Formatting Rules

- **Consistent Headings:** Use `#` for the document title, `##` for major sections, and `###` for sub-sections. Do not skip hierarchy levels.
- **Emphasis for Readability:** **Bold** the most critical paths, parameters, requirements, or warnings so they stand out to users scanning the page.
- **Code Blocks:** Always use constrained monospace blocks with the correct syntax highlighting language tag (e.g., `bash`, `json`, `python`) for all terminal commands, API responses, and code snippets.
- **Data Presentation:** Always use Markdown tables when listing environment variables, comparing features, or defining API parameters.
- **Visual Structure:** Use bulleted or numbered lists for sequential steps to break up large walls of text.