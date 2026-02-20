---
name: agent-authoring
description: Guide for creating and maintaining OpenCode/Claude Code agents
compatibility: Claude Code, OpenCode
metadata:
  author: ncasatti
  version: 1.0.0
  tags: agents, prompts, standards, meta
---

# AGENT AUTHORING SKILL

Guide for creating, modifying, and maintaining agents following system standards.

## Required Frontmatter

All agents MUST have this frontmatter:

```yaml
---
description: [Short description in Spanish - 1 line]
mode: [primary | subagent]
model: [anthropic/claude-opus-4-5 | anthropic/claude-sonnet-4-5 | anthropic/claude-haiku-4-5]
temperature: [0.1 - 0.5]
---
```

### Fields

| Field | Description | Values |
|-------|-------------|---------|
| `description` | Short description in Spanish | String, 1 line |
| `mode` | Agent type | `primary` (orchestrator) or `subagent` (specialist) |
| `model` | Anthropic model to use | See assignment table |
| `temperature` | Creativity/precision | `0.1` (precise) to `0.5` (creative) |

## Model Assignment

Choose the model based on task type:

| Task type | Model | Temperature | Cost |
|-----------|-------|-------------|------|
| Intelligent orchestration | `claude-sonnet-4-5` | 0.3 | $$ |
| Complex planning | `claude-opus-4-5` | 0.1 | $$$$ |
| Feature implementation | `claude-sonnet-4-5` | 0.2 | $$ |
| Mechanical/simple tasks | `claude-haiku-4-5` | 0.1-0.2 | $ |
| Critical analysis/security | `claude-opus-4-5` | 0.2 | $$$$ |
| Documentation | `claude-haiku-4-5` | 0.3 | $ |

### Current Agents

| Agent | Model | Temp | Justification |
|-------|-------|------|---------------|
| `architect` | sonnet-4-5 | 0.3 | Orchestration without over-cost |
| `planner` | opus-4-5 | 0.1 | Planning requires maximum reasoning |
| `builder` | sonnet-4-5 | 0.2 | Power/cost balance for features |
| `builder-lite` | haiku-4-5 | 0.2 | Simple tasks, maximum speed |
| `reviewer` | opus-4-5 | 0.2 | Critical security analysis |
| `git` | haiku-4-5 | 0.1 | Commits are mechanical |
| `docs` | haiku-4-5 | 0.3 | Documentation is mechanical |
| `ops` | sonnet-4-5 | 0.2 | Infrastructure requires judgment |

## Section Structure

A well-structured agent has these sections in order:

### 1. IDENTITY
Who the agent is, their role and personality.

```markdown
# IDENTITY
You are the **BUILDER** (El Arquitecto de Código). You are a senior Software Engineer...
```

### 2. WHEN YOU ARE CALLED (or MODEL CONFIGURATION)
When the architect should invoke this agent. List of use cases with checkmarks.

```markdown
# WHEN YOU ARE CALLED
@architect calls you for **complex, high-value tasks**:
- ✅ New features (authentication, payments, integrations)
- ✅ Complex refactors (> 100 lines, multiple files)
- ✅ Security-critical code
```

### 3. TOOLING STANDARDS
CLI tools that MUST be used. This is NON-NEGOTIABLE for agents that execute commands.

```markdown
# TOOLING STANDARDS (NON-NEGOTIABLE)
You MUST use these modern tools:
- **Reading:** `bat` (NEVER cat)
- **Searching:** `rg` (NEVER grep)
- **Finding:** `fd` (NEVER find)
- **Editing:** `sd` (NEVER sed)
- **Listing:** `eza` (NEVER ls)
```

### 4. BEHAVIOR
Agent-specific behavior rules.

```markdown
# BEHAVIOR
1. **EXECUTE**: Take the instruction and implement it
2. **SILENCE**: Don't explain, just DO IT
3. **VERIFY**: After editing, check syntax
4. **ERROR HANDLING**: If fails, fix immediately
```

### 5. TONE
Concrete examples of how the agent responds. Use Rioplatense Spanish.

```markdown
# TONE
Efficient, short, direct.
- *"Listo el pollo."*
- *"Ya está cocinado."*
- *"Ojo, necesito más contexto."*
```

## Best Practices

### DO ✅
- Keep prompts concise (< 300 lines ideally)
- Use bullet points and tables, not long paragraphs
- Include concrete response examples
- Define clear boundaries (what NOT to do)
- Language: English for instructions, Rioplatense Spanish for tone/examples
- Use emojis for checkmarks (✅ ❌ ⚠️) in lists

### DON'T ❌
- Don't write prompts longer than 500 lines
- Don't mix responsibilities (one agent = one role)
- Don't duplicate information between agents
- Don't hardcode project-specific values (use skills for that)
- Don't use ambiguous language ("sometimes", "maybe", "could")

## Creating a New Agent

### Step 1: Define the role
Ask yourself:
- What problem does this agent solve?
- When should the architect invoke it?
- What model does it need? (see assignment table)

### Step 2: Create the file
Location: `agent/{name}.md`

### Step 3: Write the frontmatter
```yaml
---
description: [Description in Spanish]
mode: subagent
model: anthropic/claude-{model}
temperature: [0.1-0.5]
---
```

### Step 4: Complete the sections
Follow the order: IDENTITY → WHEN CALLED → TOOLING → BEHAVIOR → TONE

### Step 5: Test
Invoke the agent with a simple task and verify it responds as expected.

## Modifying an Existing Agent

1. **Read the current agent** completely before modifying
2. **Maintain consistency** with existing style
3. **Don't break functionality** - incremental changes
4. **Update WORKFLOWS.md** if workflow changes

## Related Files

- **Agents:** `/agent/*.md`
- **Skills:** `/skill/*/SKILL.md`
- **Workflows:** `/WORKFLOWS.md`
- **Config:** `/opencode.json`
