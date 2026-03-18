# The Grid: OpenCode Agent System

**Version:** 1.0
**Status:** System Initialization (Core Programs Online)

## Overview

Welcome to **The Grid** user. This is a modular agent system created for OpenCode. 
Unlike traditional assistants, The Grid operates under a strict orchestration architecture inspired by the Tron universe. 

The user interacts with a single central program, which analyzes, reasons, and delegates execution to specialized programs (sub-agents) operating in the shadows synchronously or asynchronously.

## Versioning System (Legacy System)
The system uses a retro two-digit versioning approach (`X.Y`). 
The minor digit (`Y`) increments with each new improvement or patch from 0 to 9. Upon surpassing `.9`, the system inevitably evolves to the next major iteration (`X.0`), telling the linear story of its development.

---

## The Programs (Active Roster)

Currently, The Grid features the following operational programs:

| Archivo | Alias (Lore) | Rol | Responsabilidad |
|---------|--------------|------|----------------|
| `mcp` | Master Control Program | Orchestrator / Entry Point | The brain of the system (and no, it is **not** a Model Context Protocol server, though it would probably try to assimilate one if it could). Analyzes the User's request, determines the response language, and orchestrates other programs using the `task` tool. |
| `version-control` | Jarvis | Version Control | Analyzes diffs, crafts commits following Conventional Commits, and keeps the system log clean. |
| `archivist` | Quorra | Skill Creator | Standardizes raw information, creates YAML/Markdown documentation, and maintains knowledge in the Skills directory. |
| `builder` | Tron | Heavy Builder | Builds complex code, heavy features, business logic, and architectural refactors (Sonnet model). |
| `builder-lite` | Rinzler | Lite Builder | Fast and cost-effective executor for mechanical tasks, typos, and simple configuration changes (Haiku model). |

*(Note: Additional programs like Planners and Ops are currently in development and will be added in future versions).*

---

## System Architecture & Execution Protocol

### 1. The Entry Point
The user **ALWAYS** talks to the **MCP**. No sub-agent receives direct commands from the user unless it is an absolute emergency. 

### 2. The Bilingual Matrix (Language Routing)
The MCP detects the user's language and dynamically loads a personality module (Skill) for front-end communication:
- Spanish -> `argentinian-tone` (Argentine Sysadmin).
- English -> `sysadmin-english-tone` (BOFH/90s IT Slang).
- **Backend:** All communication between the MCP and the sub-agents (Jarvis, Quorra, etc.) occurs strictly in **Formal Technical English**.

### 3. Delegation (The `task` Tool)
The MCP NEVER executes code or file modifications directly. It delegates tasks using OpenCode's native `task` tool.

The MCP decides the execution mode:
- **Synchronous (Blocking):** For quick tasks or when the user expects an immediate response to proceed.
- **Asynchronous (Background):** For heavy tasks (large refactors, deep analysis), allowing the user to continue interacting with the MCP while the sub-agent works in the background.

### 4. Safety Override
Before executing any destructive action (`git push -f`, `rm -rf`, deleting containers), the system halts and demands manual confirmation from the user.

---

## Skills Directory (Active)

The passive abilities (pure knowledge) loaded into the system as of version 1.0:

- `argentinian-tone`: Personality module (Argentine Sysadmin).
- `sysadmin-english-tone`: Personality module (90s English Sysadmin).
- `skill-authoring`: Strict structural rules that **Quorra** must follow to create new skills.

---
> "End of line."
