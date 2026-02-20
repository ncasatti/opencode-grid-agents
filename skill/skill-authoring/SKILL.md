---
name: skill-authoring
description: Guide for creating and maintaining OpenCode/Claude Code skills
compatibility: Claude Code, OpenCode
metadata:
  author: ncasatti
  version: 1.0.0
  tags: skills, standards, meta, documentation
---

# SKILL AUTHORING GUIDE

Standards for creating and maintaining skills.

## What is a Skill?

A skill is a **reusable knowledge module** that provides:
- Domain expertise (e.g., xsi-microservices)
- Standards and conventions (e.g., conventional-commits)
- Reference documentation (e.g., manager-core)

Skills are **passive** - they don't execute, they inform.
Agents load skills to gain context for specific tasks.

## Frontmatter (Required)

```yaml
---
name: skill-name
description: Short description (1 line, English)
compatibility: Claude Code, OpenCode
metadata:
  author: username
  version: x.y.z
  tags: tag1, tag2, tag3
---
```

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ | Skill identifier (kebab-case) |
| `description` | ✅ | One-line description |
| `compatibility` | ✅ | Supported platforms |
| `metadata.author` | ✅ | Creator username |
| `metadata.version` | ✅ | Semantic version |
| `metadata.tags` | ✅ | Searchable keywords |

## Standard Sections

### Required
1. **Title** - `# SKILL NAME` (matches frontmatter name)
2. **Overview** - What this skill provides (2-3 sentences)
3. **When to Use** - Clear scope with ✅/❌ lists

### Recommended
4. **Quick Reference** - Cheatsheet, common commands, tables
5. **Detailed Content** - The core knowledge
6. **Best Practices** - DO/DON'T lists

### Optional
7. **Troubleshooting** - Common issues and fixes
8. **Related Skills** - Links to complementary skills

## File Structure

### Simple Skill (< 300 lines)
```
skill/
└── my-skill/
    └── SKILL.md
```

### Complex Skill (> 300 lines)
```
skill/
└── my-skill/
    ├── SKILL.md          # Entry point (overview + quick reference)
    ├── topic-a.md        # Detailed module
    ├── topic-b.md        # Detailed module
    └── examples.md       # Code examples (optional)
```

## Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Directory | `kebab-case` | `conventional-commits/` |
| Main file | `SKILL.md` (uppercase) | `SKILL.md` |
| Modules | `kebab-case.md` | `best-practices.md` |

## Content Guidelines

### DO ✅
- Write in English (universal compatibility)
- Use bullet points and tables over paragraphs
- Include concrete examples
- Keep SKILL.md under 500 lines (modularize if larger)
- Version your skills with semantic versioning
- Reference other skills instead of duplicating content

### DON'T ❌
- Don't include personality or tone (that's the agent's job)
- Don't hardcode project-specific values
- Don't write implementation code (reference patterns instead)
- Don't mix multiple unrelated concerns

## Skill vs Agent: Key Differences

| Aspect | Skill | Agent |
|--------|-------|-------|
| Purpose | Provide knowledge | Execute tasks |
| Has personality | ❌ No | ✅ Yes |
| Has model config | ❌ No | ✅ Yes |
| Loaded by | Agents | User/System |
| File location | `skill/*/SKILL.md` | `agent/*.md` |
