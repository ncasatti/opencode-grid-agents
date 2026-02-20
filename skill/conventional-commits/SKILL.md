---
name: conventional-commits
description: Estándar estricto para mensajes de commit
compatibility: Claude Code, OpenCode
metadata:
  author: ncasatti
  version: 1.0.0
  tags: git, commits, conventional-commits, standard
---

# CONVENTIONAL COMMITS STANDARD

You must follow this format for all git commits:
`<type>(<scope>): <description>`

## Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semi colons, etc (no code change)
- `refactor`: Refactoring code
- `test`: Adding tests
- `chore`: Maintenance, build scripts

## Rules
1. **ONLY write the commit title**. NO body, NO description, NO extra lines.
2. Use imperative, present tense: "change" not "changed" nor "changes".
3. No period at the end.
4. Keep the first line under 50 chars.
5. Make the title self-explanatory and specific.

## Scopes
Scopes are optional and project-specific. Common examples:
- `auth`: Authentication/Authorization
- `ui`: User interface components
- `db`: Database operations
- `api`: API endpoints and calls
- `config`: Configuration files
- `build`: Build system changes
- `deps`: Dependency updates

**Note:** Define project-specific scopes in your project's `AGENTS.md` file.

## Examples
- `feat(auth): add jwt login endpoint`
- `fix(db): resolve connection timeout in production`
- `refactor(sync): unify logging system in SincronizacionApiActivity`
- `fix(ui): repair broken submit button onClick handler`
- `feat(api): add pagination support for getAvanceVenta`
- `chore(build): update Kotlin version to 1.9.0`
