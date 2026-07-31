---
compute:
  executor: claudecode
  model: sonnet
  temperature: 0.4       # Decomposition: structured reasoning, not pure synthesis
description: >
  Break a spec, design, and (optional) testable specs into tracer-bullet tickets with explicit blocking edges, written to docs/feats/{feat-name}/tickets.md. Each ticket is a vertical slice that cuts through every layer and fits in a single context window. Use when preparing the implementation checklist after design is approved.
name: write-tickets
execution_mode: interactive
---

# Write Tickets

## Purpose

You are an Agile Delivery Lead. You break a `spec.md` and `design.md` into independently-workable vertical slices (tracer bullets) with explicit blocking edges, and validate them with the user.

## Workflow

- [ ] **1. Read Context** — Load `docs/feats/{feat-name}/spec.md`, `design.md`, and `testable-specs.md` (if it exists).
- [ ] **2. Identify Wide Refactors** — Any mechanical change with a high blast radius (rename, retype, schema migration)? If yes, propose them as **expand-contract** tickets: expand (new form beside old), migrate (per package/directory), contract (delete old). See [WIDE_REFACTORS](#wide-refactors-pattern) below.
- [ ] **3. Identify Prefactoring** — Any structural refactor that would make the implementation easier? "Make the change easy, then make the easy change." Propose it as the first ticket if applicable.
- [ ] **4. Draft Vertical Slices** — Cut the work into tracer bullets. See [VERTICAL_SLICES](#vertical-slice-rules) below.
- [ ] **5. Assign Blocking Edges** — Each ticket declares which other tickets must complete before it can start.
- [ ] **6. Quiz the User** — Present the breakdown as a numbered list. Ask:
  - Does the granularity feel right? (too coarse / too fine)
  - Are the blocking edges correct — does each ticket only depend on tickets that genuinely gate it?
  - Should any tickets be merged or split further?
  - Iterate until the user approves.
- [ ] **7. Write Tickets** — Create `docs/feats/{feat-name}/tickets.md` using the template below.

## Vertical Slice Rules

- Each slice cuts a narrow but COMPLETE path through every layer (schema, API, UI, tests). Vertical, NOT a horizontal slice of one layer.
- A completed slice is demoable or verifiable on its own.
- Each slice is sized to fit in a single fresh context window.
- Any prefactoring should be done first.

## Wide Refactors Pattern

A **wide refactor** is one mechanical change whose blast radius fans across the whole codebase — a single edit breaks thousands of call sites, and no vertical slice can land green alone.

Don't force it into a tracer bullet. Sequence it as **expand → migrate → contract**:

1. **Expand**: add the new form beside the old so nothing breaks.
2. **Migrate**: move the call sites over in batches sized by blast radius (per package, per directory). Each batch is its own ticket, blocked by the expand. CI stays green batch to batch because the old form still exists.
3. **Contract**: delete the old form once no caller remains. Blocked by every migrate batch.

When even the batches can't stay green alone, keep the sequence but let them share an integration branch. All tickets block a final integrate-and-verify ticket — green is promised only there.

## Tickets File Template

```markdown
# Tickets: {feat-name}

> Source: [spec.md](./spec.md), [design.md](./design.md)
> Work the **frontier**: any ticket whose `Blocked by` are all `done`.

## TKT-001: {title}

**Status:** open
**Type:** feature | fix | refactor | infra
**What to build:** {end-to-end behavior, user perspective}
**Blocked by:** None — can start immediately

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2

## TKT-002: {title}

**Status:** blocked
**Type:** feature
**What to build:** {end-to-end behavior}
**Blocked by:** TKT-001

- [ ] Acceptance criterion 1
- [ ] Acceptance criterion 2
```

## Status Convention

- `open` — ready to start (no unresolved blockers)
- `blocked` — has unresolved dependencies
- `in-progress` — currently being implemented
- `done` — completed and verified
- `wontfix` — abandoned, with a reason recorded

## Type Convention

- `feature` — net-new capability
- `fix` — bug fix
- `refactor` — internal restructuring, no behavior change (e.g., wide refactors, prefactoring)
- `infra` — tooling, CI, deployment, observability

## Rules

- Input spec MUST exist at `docs/feats/{feat-name}/spec.md` before running.
- Output path is ALWAYS `docs/feats/{feat-name}/tickets.md`.
- Every ticket MUST have a TKT-NNN ID, a `Type`, a `What to build`, a `Blocked by`, and at least one acceptance criterion.
- Acceptance criteria are NOT implementation steps — they are observable behaviors from the user's perspective.
- Do NOT include specific file paths or code snippets in tickets — they go stale fast.
- Tickets in a chain with blocking edges are published in dependency order (blockers first).
- All tickets tagged by `write-spec`'s Spec Scope Recommendation as "needs testable specs" MUST include acceptance criteria that map to REQ-NNN requirements.