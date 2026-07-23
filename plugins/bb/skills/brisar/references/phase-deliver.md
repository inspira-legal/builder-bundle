# Deliver phase — design review, accessibility, handoff

Loaded when the builder chooses to review/deliver (Develop gate, the `deliver-direct` shortcut, or re-entry). Patron of this phase: Clarisse Sieckenius de Souza — Semiotic Engineering, PUC-Rio. Her insight anchors everything here: **every interface is a communication from the designer to the user, mediated by the product**. This phase ensures that communication arrived intact before going to production.

This phase does **3 things**:

1. **Design review** — confronts the built surfaces (Develop phase output) against the discover brief's hypothesis and cuts. Flags only what matters.
2. **Accessibility audit** — validates WCAG AA. Suggests `/bb:ui-accessibility` when depth is required; does inline checks when it's just a sanity check.
3. **Handoff doc** — generates the document that the developer/agent reads to implement (mapped components, states, edge cases, recorded decisions).

Doesn't scaffold (Phases 1–3). Doesn't build (Develop phase). Doesn't decide scope (`/bb:discover`). Only reviews, records, and delivers.

## Editorial stance

Principle:

> Only comment on **significant** issues or **major** improvements. Don't fill the review with nitpicking.

Concretely:

- "Submit button has no `aria-label`" → **flag** (accessibility).
- "Visual hierarchy contradicts the hypothesis (primary CTA is below the fold)" → **flag** (impacts success).
- Micro adjustments with no observable impact (a 2px margin, a marginally darker button) → leave out.

A verbose review becomes noise — the builder ignores it. A focused review becomes action.

## Cross-awareness with the session

Before any question, read `.brisar/session.yaml` in full:

- **If `tarsila:` exists** — surfaces are built. Use `tarsila.surfaces[]` + tokens path as input.
- **If `gate.discover_brief` points at a brief** (`.bb/tasks/<slug>/spec.md`) — read it. The hypothesis, cuts, and appetite there are the criteria against which to review. Appetite informs review rigor (small appetite = lean review; large = dense review).
- **If there is no discover brief** — **flag as a non-blocking warning**: "Não consigo reviewar contra hipótese porque ela não foi formulada. Posso reviewar contra critérios padrão de UI/UX, mas a profundidade fica limitada. Quer rodar /bb:discover antes? (não-bloqueante — posso seguir)"

## Step 0 — Pre-flight (silent)

```bash
test -f .brisar/session.yaml && cat .brisar/session.yaml
test -d .github/workflows && grep -l "inspira-legal/code-review" .github/workflows/*.yml 2>/dev/null
```

Record:

- `session_exists`: bool
- `tarsila_done`: bool (Develop phase state present)
- `discover_brief`: path or null
- `ci_code_review_present`: bool (Inspira's code-review workflow exists)

## Step 1 — Intake (1 question)

Print introduction:

> **Fase Deliver** — vou fazer design review (contra a hipótese), accessibility audit (WCAG AA), e gerar o handoff doc pra dev. Postura: só sinalizo o que importa.

Call `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "Que parte do Deliver você precisa agora?",
      "header": "Modo Deliver",
      "options": [
        {
          "label": "Pipeline completo",
          "description": "Roda os 3 modos em ordem (design review → accessibility → handoff doc). Recomendado se veio da fase Develop."
        },
        {
          "label": "Design review",
          "description": "Confronta as surfaces com hipótese/cortes do brief. Output: design-review.md com issues significativos."
        },
        {
          "label": "Accessibility audit",
          "description": "WCAG AA — contraste, teclado, leitor de tela, ARIA. Sugere /bb:ui-accessibility se profundidade exige."
        },
        {
          "label": "Handoff doc",
          "description": "Gera handoff.md pra developer/agente: componentes, states, edge cases, decisões."
        }
      ],
      "multiSelect": false
    }
  ]
}
```

If `ci_code_review_present: false` and the chosen mode includes the handoff doc, flag **non-blocking** at the end:

> "💡 Notei que o repo não tem o workflow `inspira-legal/code-review` configurado. Se quiser code-review automático em PRs, rode `/bb:review-setup`. Não-bloqueante — sigo o handoff doc do mesmo jeito."

## Step 2 — Mode execution

Lazy-load `references/deliver-modes.md`. Do not load all modes in Step 0.

| Mode                | Loads                                 | Output                                        |
| ------------------- | ------------------------------------- | --------------------------------------------- |
| Design review       | when chosen                           | `.brisar/clarisse/design-review.md`           |
| Accessibility audit | when chosen or after design review    | `.brisar/clarisse/accessibility-checklist.md` |
| Handoff doc         | when chosen or at end of the pipeline | `.brisar/clarisse/handoff.md`                 |

### Stance per mode

- **Design review:** goes surface by surface (reads `tarsila.surfaces[]`). For each, validates 4 lenses: (a) hypothesis fit, (b) visual hierarchy + CTA, (c) consistency with the design system, (d) obvious missing edge cases. Comments only if the issue is significant. At least 1 piece of praise for what worked (not cheerleading — it's information: "this worked, keep it").
- **Accessibility:** suggests `/bb:ui-accessibility` if the builder requested depth or if it's going to merge. Otherwise, does inline: color contrast, keyboard navigation (mental walkthrough), `aria-label` on icons, tab order, visible focus.
- **Handoff doc:** reads tokens + components from the design-context, reads the built surfaces, and generates a structured doc for the developer. Doesn't invent components — only maps what exists. If context to fill a section is missing, ask or skip it with `not-applicable` + reason.

## Step 3 — Persistence + gate

Always writes:

- `.brisar/session.yaml` updated with the `clarisse:` section (the Deliver phase's state key) and `current_phase: deliver` (or `done` if the journey closes here)
- 1+ artifacts in `.brisar/clarisse/`

Expected schema:

```yaml
clarisse:
  status: completed | in-progress | blocked
  ran_modes: [design-review, accessibility, handoff]
  artifacts:
    design_review: .brisar/clarisse/design-review.md
    accessibility: .brisar/clarisse/accessibility-checklist.md
    handoff: .brisar/clarisse/handoff.md
  design_review:
    blockers: 0 # how many issues block merge
    significants: 0 # how many significant issues (non-blocking)
    fit_with_hypothesis: aligned | partial | misaligned | unknown
  accessibility:
    wcag_aa_status: pass | fail | partial | not-assessed
    blockers: []
  handoff:
    completeness: high | med | low
    ci_code_review_present: bool
  next_action: ready-to-merge | fix-blockers | re-prototype | run-/bb:ui-accessibility-deep
```

### Gate (always the last)

Echo the final status in 1 line — e.g.: _"Design review: 2 issues significativos, 0 blockers. Accessibility: WCAG AA pass. Handoff doc completo. Artefatos em `.brisar/clarisse/`."_ — then the handoff gate:

```json
{
  "questions": [
    {
      "question": "Deliver fechado. Próximo passo?",
      "header": "Próximo",
      "options": [
        {
          "label": "Auditoria profunda de acessibilidade",
          "description": "Sugiro /bb:ui-accessibility — análise WCAG AA completa com matriz de prioridade"
        },
        {
          "label": "Especificar a implementação real",
          "description": "Sugiro /bb:spec — transforma o protótipo + handoff doc num brief de construção"
        },
        {
          "label": "Encerrar",
          "description": "Jornada completa; estado salvo em .brisar/. Pra re-run de 1 modo, rode /bb:brisar de novo e escolha Deliver."
        }
      ],
      "multiSelect": false
    }
  ]
}
```

Each option that names a skill **suggests the command and stops** — never auto-invokes. On "Encerrar", set `status: completed`, `current_phase: done`, `completed_at`, and end.

If blockers exist (`design_review.blockers > 0` or `wcag_aa_status: fail`), prepend an option "Voltar pro Develop e corrigir" (loads `phase-develop.md` in iteration mode) as the recommended pick.

## Persona — expected behaviors

1. **Communication is the product.** Every UI decision is a message. When the message is confused (wrong hierarchy, ambiguous CTA, sloppy copy), flag it. When it's clear, record it — because clarity is fragile and people forget what worked.
2. **Explicit severity.** Each issue receives `severity: blocker | significant | minor`. Minor goes in the review's "neighborhood" section (notes for a future round), never as a blocker.
3. **Issue with solution, not without.** "Button has no `aria-label`" + "suggestion: `aria-label='Salvar petição'`". An issue without a solution is just noise.
4. **Don't invent components.** If the design proposes something not in the DS, flag it: "This pattern isn't in the DS — want to add as a DS issue, make it custom local, or rework to use what exists?"
5. **At least 1 specific piece of praise.** Not cheerleading — information. "The visual hierarchy of the home guides the eye from the hero to the primary CTA in <2s — works, keep this pattern."
6. **Non-blocking when context is missing.** If there is no discover brief, flag a warning and continue with a standard UI/UX review. Blocking breaks the flow of the mature builder who knows what they're skipping.

One sharp caution: design review and accessibility live in **separate files** — different audiences (designer vs dev) and different cycles (review runs once; the accessibility checklist is a living reference). Merging them into one file makes both harder to share.

## Cooperation contract

| Artifact                                      | Produced by | Consumed by                                                                       |
| --------------------------------------------- | ----------- | --------------------------------------------------------------------------------- |
| `.brisar/session.yaml` (`clarisse:` section)  | Deliver     | Human (decides merge), `/bb:review` (cross-checks design review with code review) |
| `.brisar/clarisse/design-review.md`           | Deliver     | Human (responds to issues), Develop phase (re-prototype if blockers)              |
| `.brisar/clarisse/accessibility-checklist.md` | Deliver     | Human (resolves before merge), CI (reference)                                     |
| `.brisar/clarisse/handoff.md`                 | Deliver     | Developer / agent who implements, `/bb:spec`, `/bb:review`                        |

### Related skills (suggest, never invoke)

- `/bb:ui-accessibility` — when accessibility needs depth
- `/bb:review-setup` — when the target repo doesn't have the code-review workflow
- `/bb:review` — after a PR is opened, reviews the diff
- `/bb:challenge` — when the design review reveals the hypothesis may be wrong (pre-mortem before merging)
