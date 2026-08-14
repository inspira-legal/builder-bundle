# Export mode — the shareable product/UX spec

Load this only when exporting. The converged spec in `.bb/tasks/<slug>/spec.md`
stays the source of truth; the export is a **rendering** of it for an audience
without the spec's context — a designer picking it up in Figma, a dev team, a
stakeholder deck. Everything below comes from the alignment already reached in
the loop; the export never introduces new decisions.

## The trio rule (hypothesis · OKR · metric)

The export carries the minimum shaping of the product team's modus operandi. The
hypothesis, OKR, and metric fields are **inseparable** — they come together or
not at all.

**Test:** "Will the user change any behavior because of this?"

- **Yes** → `Hypothesis` required → trio (`Connected OKR` + `Expected Impact` +
  `Metric`) required. If the spec's `## hypothesis` (from `/bb:discover`)
  exists, render it here; if the trio can't be filled from the spec, ask —
  don't invent.
- **No** (internal feature, design pattern, compliance) → trio omitted entirely
  — no placeholder, no "N/A".

## Auto-sizing the export

| Scope      | Signals                                                            | Documents                             |
| ---------- | ------------------------------------------------------------------ | ------------------------------------- |
| **Small**  | Single flow, no UI content, scope clear in 1 sentence              | `spec.md`                             |
| **Medium** | Feature with screens, UI content, 1–2 flows                        | `spec.md` + `content.md`              |
| **Large**  | Multiple flows, technical dependencies, non-trivial implementation | `spec.md` + `content.md` + `tasks.md` |

When in doubt, export the smallest set and expand on request. Name the files
`spec-<feature>.md`, `content-<feature>.md`, `tasks-<feature>.md` and write them
where the user wants them (default: alongside the spec in
`.bb/tasks/<slug>/`).

## spec.md — the definition document

Map from the spec: the opening and the free top half → context and framing;
`## decisions` → Decision rationale; `## out of scope` → Out of scope; `## behavior` → Behaviors;
the behavior map's `WHEN … THEN …` rows → Definition of done criteria.

```markdown
# Spec: [Feature Name]

> Status: draft | under review | approved
> Last updated: [date]

## Shaping

**Problem:** [what pain, for whom, how often]

<!-- Trio below: only if the feature changes user behavior (see trio rule). -->

**Hypothesis:** If we deliver X, we expect to see Y in metric Z
**Connected OKR:** [metric name] — [how this initiative moves that indicator]
**Expected Impact:** [baseline → target]
**Metric:** [how to measure]

## Product

- **User:** [who experiences this problem — be specific]
- **Business objective:** [what the product gains beyond the metric]

## Scope

### Included

- [behavior / flow / screen]

### Out of scope (explicit)

- [what is consciously not here and why]

## Behaviors

### Main flow

[step by step of the normal journey — from the spec's happy path]

### States and variations

[loading, empty, error, relevant edge cases — from the edge→outcome table]

### Constraints

[technical, product, deadline]

## Definition of done

- [ ] [verifiable criterion — each maps to a WHEN/THEN row]

## Decision rationale

[non-obvious decisions made during shaping and why]

## Next steps

[who needs what, in what order]
```

## content.md — canonical UI texts

Generate when UI content is involved. Drafts to guide visual exploration; final
copy is validated in the visual stage. Follow the product's voice guide when one
exists; the voice rules below are the fallback. UI copy is written in the
product's language (PT-BR for Inspira products).

```markdown
# Content: [Feature Name]

> Draft to guide visual exploration. Final copy is validated in the visual stage.

## [Section / Screen Name]

- **Title:**
- **Subtitle:**
- **Primary CTA:**
- **Secondary CTA:**
- **Body:**
- **Empty state:**
- **Error message:**
```

## tasks.md — implementation breakdown

Generate for Large scope or non-trivial technical dependencies. Render from the
spec's `## tasks` items — same work, table form with explicit dependencies and
verification criteria.

```markdown
# Tasks: [Feature Name]

> Implementation owner: [name]
> Critical dependency: [what needs to be ready first]

## Tasks

| #   | Task          | Dependency | Verification criterion  | Status  |
| --- | ------------- | ---------- | ----------------------- | ------- |
| 1   | [atomic task] | —          | [how to know it's done] | pending |
| 2   | [atomic task] | 1          | [how to know it's done] | pending |

## Technical decisions to confirm

- [question / validation point]
```

## Voice — copy rules (for `content.md`)

Apply the product's established voice and tone; these are the defaults when no
brand guide exists:

- **Buttons and CTAs:** verbs in the imperative present, maximum 3 words, always
  specific to the action.
- **Labels and navigation:** direct nouns, no articles, only first letter
  capitalized.
- **Empty states:** guide with a CTA — tell the user what to do next, not just
  that nothing is there.
- **Errors:** explain what happened + what to do, empathetic tone.
- **Loading:** contextual to the operation ("Buscando…", "Gerando relatório…").
- **Language:** active voice, present tense, numbers written out in body text.

## Handoff (PT-BR, shown to the user)

After exporting, emit:

```
Spec exportada. O que levar para cada destino:

→ Exploração visual: use spec.md + content.md como insumo (Figma / /bb:brisar)
→ Implementação: compartilhe spec.md [+ tasks.md se houver] com o time — ou rode /bb:implement direto da spec
→ Próximo passo: [ação específica mais importante agora]
```

## Don't invent

Every field renders from the spec or from an answer the user gave. A field the
spec doesn't settle gets asked (one round, batched) or left blank — blank beats
invented.
