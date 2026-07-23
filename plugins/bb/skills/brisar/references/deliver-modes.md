# Deliver modes — templates for the 3 modes

Lazy load: read only the section of the mode chosen in Step 1 of `phase-deliver.md`.

---

## Mode 1: Design review (`design-review`)

**Why it exists:** confronts the prototype with the *intent* (hypothesis + cuts from the discover brief). Without this confrontation, design becomes opinion.

### Inputs

- `.brisar/session.yaml` — read `gate.discover_brief` (→ `.bb/tasks/<slug>/spec.md`: hypothesis, cuts, appetite) and `tarsila.surfaces[]`
- Surfaces built by the Develop phase: HTML/React in `<project>/src/...` or `<project>/<surface>.html`
- Design context: `<design_context_path>/tokens.md` + `components.md` (path in `.brisar/config.yaml`)

### Walkthrough (sequential — 1 surface at a time)

For each surface in `tarsila.surfaces[]`:

**1. Hypothesis fit** (the key question)
- Read the hypothesis from the discover brief.
- Mental question: "If a user enters this screen, does their path lead to the behavior this hypothesis predicts?"
- Flag if: primary CTA is below the fold, the primary action isn't visually dominant, there's unnecessary friction in the critical path.

**2. Visual hierarchy + CTA**
- Where does the eye land? (mental F-pattern / Z-pattern)
- Is the primary CTA the most salient element?
- Are there more than 1 "primary" CTA competing? (frequency: high)

**3. Consistency with design system**
- Do the tokens used match `tokens.md`? (colors, spacing, type-scale)
- Do the components used exist in `components.md`?
- If there's inline custom, is the why documented?

**4. Obvious edge cases**
- Does a loading state exist?
- Does an empty state exist?
- Does an error state exist?
- "No permission" state (if Inspira context)?

### Severity

Each issue receives **one** severity:
- `blocker` — blocks merge. E.g.: violates WCAG AA, contradicts hypothesis, breaks DS.
- `significant` — doesn't block, but worth resolving before PR. E.g.: missing state, ambiguous CTA.
- `minor` — goes in "neighborhood". **Don't use for nitpicking** — only for real things worth noting.

### At least 1 specific piece of praise

Not cheerleading. Information. Identify 1 decision that worked and say *why* — so the builder maintains that pattern.

### Output: `.brisar/clarisse/design-review.md`

```markdown
# Design review — <projeto>

> Gerado pela fase Deliver do /bb:brisar em <ISO date>
> Confrontado contra: hipótese e problema do brief (.bb/tasks/<slug>/spec.md)
> Apetite: <small|medium|large> — rigor do review proporcional

## Resumo

- Surfaces revisadas: <lista>
- Blockers: <N>
- Significants: <N>
- Fit com hypothesis: aligned | partial | misaligned | unknown
- Pronto pra merge: sim | não | só após blockers

## Por surface

### <surface_name>

#### Hypothesis fit
<frase: aligned/partial/misaligned + razão em 1 linha>

#### Issues

##### [blocker] <título curto>
- **Onde:** <componente/seção/arquivo:linha se aplicável>
- **Problema:** <1-2 frases>
- **Por que importa:** <impacto observável>
- **Sugestão:** <ação concreta>

##### [significant] <título curto>
- **Onde:** ...
- **Problema:** ...
- **Sugestão:** ...

##### [minor] <título curto>
- <breve, em 1 linha>

#### O que ficou bem
- <decisão específica> — por que: <razão de manter esse padrão>

## Neighborhood (issues minor agrupados — não bloqueantes)

- <item>
- <item>

## Decisão final

<ready-to-merge | fix-blockers-first | re-prototype | run-/bb:challenge-se-hipotese-fragil>
```

---

## Mode 2: Accessibility audit (`accessibility`)

**Why it exists:** WCAG AA isn't optional for an Inspira product. Accessibility is part of the Deliver contract.

### Decision: inline or delegate?

| Signal | Action |
|---|---|
| Builder asked for "deep audit" or "before merging to prod" | **Suggest `/bb:ui-accessibility`** (specialized skill). Flag in handoff: "Rode `/bb:ui-accessibility` na pasta `<projeto>` antes de mergear." |
| Quick sanity check during design review | **Inline** (5 checks below) |
| Small appetite + hosted prototype | **Inline** is sufficient |

### Inline checks (only if decision = inline)

**1. Color contrast (WCAG AA = 4.5:1 for normal text, 3:1 for large text)**
- For each foreground/background pair used in the prototype, validate.
- If in doubt, suggest /bb:ui-accessibility — don't guess values.

**2. Keyboard navigation (mental walkthrough)**
- Does Tab traverse all interactive elements?
- Does the tab order make sense (top-to-bottom, left-to-right)?
- Is focus visible (not removed with `outline: none` without replacement)?
- Does Esc close modals? Does Enter submit forms?

**3. ARIA + semantics**
- Do buttons use `<button>`, not `<div onClick>`?
- Do icon-only buttons have `aria-label`?
- Do form fields have `<label>` or `aria-labelledby`?
- Are headings in order (h1 → h2 → h3, without skipping)?

**4. Screen reader (mental)**
- Does what's announced in DOM order make sense?
- Do informative images have `alt`? Do decorative ones have `alt=""`?
- Do dynamic states (loading, error) use `aria-live`?

**5. Motion and timing**
- Is there no autoplay of video/animation causing distraction?
- Is `prefers-reduced-motion` respected?
- Are timeouts extensible (if any)?

### Output: `.brisar/clarisse/accessibility-checklist.md`

```markdown
# Accessibility checklist — <projeto>

> Gerado pela fase Deliver do /bb:brisar em <ISO date>
> Modo: inline | delegated (sugerido /bb:ui-accessibility)
> WCAG target: AA

## Status

- WCAG AA: pass | fail | partial | not-fully-assessed
- Blockers: <N>

## Resultados

### Contraste
- [pass | fail | not-assessed] <par cor X sobre Y> — ratio: <N:1> — target: <N:1>

### Teclado
- [pass | fail | not-assessed] Tab order coerente
- [pass | fail | not-assessed] Foco visível
- [pass | fail | not-assessed] Esc/Enter funcionam

### ARIA + semântica
- [pass | fail | not-assessed] Botões são `<button>`
- [pass | fail | not-assessed] Ícones-only têm aria-label
- [pass | fail | not-assessed] Form fields têm label
- [pass | fail | not-assessed] Headings em ordem

### Leitor de tela
- [pass | fail | not-assessed] Ordem do DOM coerente
- [pass | fail | not-assessed] Alt texts presentes
- [pass | fail | not-assessed] aria-live em estados dinâmicos

### Movimento
- [pass | fail | not-assessed] Sem autoplay disruptivo
- [pass | fail | not-assessed] prefers-reduced-motion respeitado

## Blockers a resolver antes do merge

- <item> — fix sugerido: <ação>
- <item> — fix sugerido: <ação>

## Para session.yaml

```yaml
clarisse:
  accessibility:
    wcag_aa_status: <pass|fail|partial|not-assessed>
    mode: inline | delegated
    blockers: [<id1>, <id2>]
```
```

---

## Mode 3: Handoff doc (`handoff`)

**Why it exists:** the developer/agent who will implement needs a structured doc. Without it, design decisions are lost and implementation becomes free interpretation.

### Inputs

- `<design_context_path>/tokens.md` + `components.md`
- `<design_context_path>/<surface>.md` (visual direction written by brisar Phase 4)
- Surfaces in `<project>/src/...` (React structure) or `<project>/<surface>.html`
- `.brisar/session.yaml` (all sections — uses recorded decisions)

### Output structure

For each surface, generate a section. Don't invent — only map what exists in the prototype + design-context.

### Output: `.brisar/clarisse/handoff.md`

```markdown
# Handoff — <projeto>

> Gerado pela fase Deliver do /bb:brisar em <ISO date>
> Audiência: developer ou agente que vai implementar
> Confrontado contra: hipótese e cortes do brief

## Contexto rápido

- **Hipótese (do brief em .bb/tasks/<slug>/spec.md):** <statement>
- **Apetite (do brief):** <small|medium|large>
- **Surfaces no escopo:** <lista>
- **Cortes registrados:** <lista de cortes do brief — pra evitar implementar o que foi cortado>

## Design tokens (referência)

Path: `<design_context_path>/tokens.md`

Resumo (auto-extraído):
- Cores: <lista de tokens principais>
- Spacing scale: <referência>
- Type scale: <referência>

## Componentes do DS usados

| Componente | Onde | Variant |
|---|---|---|
| Button | <surface>.header, <surface>.footer | primary, secondary |
| Card | <surface>.list | default |
| ... | | |

## Componentes custom (fora do DS)

- **<nome>** — em `<surface>:<location>` — razão: <breve> — sugestão futura: <add ao DS | manter custom>

## Por surface

### <surface_name>

**Intent:** <1 frase do que essa surface faz>

**Hierarchy (top-to-bottom):**
1. <elemento> — token: <ref> — state: <default|hover|active|disabled>
2. <elemento>
3. <CTA primário> — destination/action: <onde leva>

**States:**
- Default — descrição
- Loading — descrição
- Empty — descrição
- Error — descrição
- (outros relevantes)

**Edge cases tratados:**
- <caso 1>
- <caso 2>

**Edge cases NÃO tratados (decidido cortar — ver cortes do brief):**
- <caso> — razão: <cut_reason>

**Decisões registradas:**
- <decisão 1> — razão: <breve, do design review ou do brief>

## Acessibilidade

- WCAG AA status: <pass|fail|partial>
- Itens a garantir no merge: <lista de blockers da accessibility-checklist.md>
- Doc de referência: `.brisar/clarisse/accessibility-checklist.md`

## CI / code-review

- Workflow `inspira-legal/code-review` presente: <sim|não>
- Se não: sugerimos rodar `/bb:review-setup` antes de mergear PRs deste repo.

## Para session.yaml

```yaml
clarisse:
  handoff:
    completeness: <high|med|low>
    surfaces_documented: <N>
    ci_code_review_present: <bool>
```
```

---

**Mental recap before closing the phase:**
- Each mode generated its artifact.
- session.yaml has `clarisse:` complete with `status`, `ran_modes`, `next_action`.
- End at the Step 3 gate of `phase-deliver.md` (ui-accessibility / spec / encerrar) — suggest, never invoke.
