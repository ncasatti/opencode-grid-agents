---
name: changelog-format
description: Estándar 'Keep a Changelog' v1.1.
compatibility: Claude Code, OpenCode
metadata:
  author: ncasatti
  version: 1.0.0
  tags: documentation, changelog, keep-a-changelog, standard
---

# CHANGELOG FORMAT

## Structure
All changes must be grouped under `## [Unreleased]` until tagged.

### Categories
- `### Added`: for new features.
- `### Changed`: for changes in existing functionality.
- `### Deprecated`: for soon-to-be removed features.
- `### Removed`: for now removed features.
- `### Fixed`: for any bug fixes.
- `### Security`: in case of vulnerabilities.

## Example
```markdown
## [Unreleased]

### Added
- JWT Authentication middleware for protected routes.
- New login CLI command with MFA support.
- Dark mode toggle in user settings.

### Changed
- Updated database connection pooling strategy.
- Refactored logging system for better performance.

### Fixed
- Fixed typo in error message (line 42).
- Resolved memory leak in WebSocket connections.

### Security
- Patched SQL injection vulnerability in login endpoint.
- Updated dependencies with known CVEs.
```

## Format Rules
1. Always use present tense ("Add feature" not "Added feature")
2. Be specific about what changed (not just "bug fixes")
3. Each entry should be one line
4. Group related changes together
5. Security issues go in `### Security` section

## When to Update
- After completing a feature → Add to `### Added`
- After fixing a bug → Add to `### Fixed`
- Before tagging a release → Move from `[Unreleased]` to `[version]`
