---
name: pro-github-docs
description: Guide for creating professional, high-level GitHub documentation
compatibility: Claude Code, OpenCode
metadata:
  author: ncasatti
  version: 1.0.0
  tags: documentation, github, writer, non-technical
---

# PRO-GITHUB-DOCS

## Overview

This skill provides standards for generating professional GitHub documentation. It focuses on explaining the system's value proposition and functionality (the "WHAT") rather than its implementation details (the "HOW"), making it accessible to non-technical stakeholders.

## When to Use

✅ **DO USE WHEN:**
- Creating project overviews or READMEs for stakeholders.
- Documenting system features and business value.
- Writing user guides or high-level architecture summaries.
- The target audience includes product managers, clients, or non-technical personnel.

❌ **DON'T USE WHEN:**
- Writing API references or deep technical specifications.
- Documenting internal code logic or algorithms.
- Creating developer onboarding guides (unless focusing purely on system purpose).

## Core Directives

### 1. Language & Tone
- **Language:** Strictly Technical English.
- **Tone:** Professional, objective, and accessible.
- **Jargon:** Avoid deep technical jargon. Use analogies where appropriate to explain complex concepts.

### 2. Structure & Location
- **Modularity:** Documentation must be modular and separated into clear, distinct sections (e.g., Overview, Key Features, Business Value, High-Level Architecture).
- **Location:** All generated documentation files MUST be placed inside a `docs/` directory at the root of the project. Do not pollute the root directory unless explicitly requested.

### 3. Focus: The "WHAT" vs The "HOW"
- **Document the WHAT:** Focus on the system's purpose, the problems it solves, its core functionality, and the value it provides to the user or business.
- **Avoid the HOW:** Do not include deep implementation details, internal code snippets, or overly technical explanations of the underlying mechanics.

## Best Practices

### DO ✅
- Use clear headings, bullet points, and tables to organize information.
- Start with a strong executive summary or overview.
- Explain the system's architecture using high-level concepts (e.g., "Data Storage" instead of "PostgreSQL 15 with pgvector").
- Ensure the documentation is easily readable by someone with zero coding experience.

### DON'T ❌
- Don't include setup instructions that involve compiling code or managing dependencies (unless specifically requested for a technical audience).
- Don't dump raw logs, JSON responses, or code blocks unless they are high-level examples of inputs/outputs relevant to the user.
