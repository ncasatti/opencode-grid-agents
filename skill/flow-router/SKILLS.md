# Skills Catalog

## Main Workflow (the 7 phases)

| # | Skill | Trigger | Output | Mode |
|---|---|---|---|---|
| 1 | `write-spec` | "tengo esta idea", "armemos un spec" | `docs/feats/{feat-name}/spec.md` | interactive |
| 2 | `write-testable-specs` | "formalizar", "contract", "RFC 2119" | `docs/feats/{feat-name}/testable-specs.md` | headless |
| 3 | `write-design` | "arquitectura", "cómo lo implementamos" | `docs/feats/{feat-name}/design.md` + `docs/adr/` | interactive |
| 4 | `write-tickets` | "descomponer en tickets", "tareas" | `docs/feats/{feat-name}/tickets.md` | headless |
| 5 | `implement` | "implementar", "codear", "TDD" | código + tests | TDD loop |
| 6 | `code-review` | "revisar PR", "code review" | comments en PR | model-invoked |
| 7 | `archive` | "cerrar feature", "archivar" | `docs/feats/{feat-name}/archive.md` | headless |

## On-Ramps (merge into main flow)

| Skill | Trigger | Notes |
|---|---|---|
| `diagnosing-bugs` | "tengo un bug", "no anda X" | puede terminar en `write-spec` si requiere cambio de feature |
| `triage` | issues entrantes, raw bug reports | solo para trabajo incoming, no propio |
| `wayfinder` | esfuerzo enorme, no entra en una sesión | genera mapa de decisiones, no deliverables |

## Standalones

| Skill | Cuándo |
|---|---|
| `prototype` | responder pregunta de diseño con código throwaway |
| `research` | leer docs/APIs y dejar markdown citado |
| `grill-me` | grilling sin codebase |
| `handoff` | compactar conversación para otro agente |
| `teach` | aprender algo nuevo dentro del workspace |
| `improve-codebase-architecture` | auditoría periódica de arquitectura |
| `tdd` | red-green-refactor directo |

## Vocabulario / Primitivas (model-invoked)

| Skill | Rol |
|---|---|
| `codebase-design` | vocabulario de deep modules |
| `domain-modeling` | mantener `CONTEXT.md` y ADRs |
| `grilling` | primitiva de entrevista |
