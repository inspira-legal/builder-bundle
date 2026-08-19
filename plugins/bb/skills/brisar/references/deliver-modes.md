# Deliver modes: templates for the 3 modes

Lazy load: read only the section of the mode chosen in Step 1 of `phase-deliver.md`.

---

## Mode 1: design review (`design-review`)

**Why it exists:** confronts what was built with **the problem and the research**. Without that
confrontation design becomes opinion, and with only half of it, design becomes a faithful
execution of the wrong question.

### Inputs

- `.brisar/session.yaml`: `gate.discover_brief` (→ `.bb/<slug>/spec.md`: hypothesis, cuts, appetite), `gate.design_brief` (→ `.bb/<slug>/brief-design.md`: research, chosen direction with its five parts, base block, token limits read from source, open tension), `tarsila.surfaces[]` (locator + `variants[]` + `states_covered[]` + `deviations[]`), `medium.chosen`
- `.brisar/config.yaml`: `design_path` + `surfaces[].file`, the visual direction in the same task folder. **Only on medium `código`**: on a canvas or `claude-design` medium there is no config, and the direction comes from `gate.design_brief` instead. That is the normal path there, not a degradation.
- **The artifact, opened through the reader for its medium**: files, preview, or Paper/Figma/Pencil MCP. Resolved in Step 0.1 of `phase-deliver.md`. On a canvas, read structure and computed values through the MCP; a screenshot judges composition and **never** supplies numbers.
- Design context: `<design_context_path>/tokens.md` + `components.md` when the medium is `código`; otherwise the DS section of the design brief, which read the same source.

### The unit of review is surface × variant

Not surface. A surface with four variants is **four sweeps**. The deltas between them are where the
contract gets violated, because each variant hides or swaps blocks, and the swap is where a string
stops making sense.

Concretely: a coupon labelled for people coming back, shown in the variant for someone who never had
access. A headline asserting the customer's size, in the variant reached by a fallback that does not
know the size. A variant that dropped its only action, and with it the only thing that could be
measured. **None of those are visible in the default variant, and all of them ship.**

Anything you could not reach goes in `variants_unreviewed`, never silently omitted.

### Walkthrough: seven lenses per surface × variant

Lenses 1–4 are structural; 5–7 are what a senior designer adds. Comment only when the issue is
significant.

**1. Fidelity to the chosen direction**

- The direction's five parts (bet, composition, copy, rationale, risk) are the contract.
- Flag when the composition drifted, when a block the direction excluded reappeared, or when the base
  block common to all directions was broken **without a declared exception**.
- Check `tarsila.deviations[]`: a recorded deviation gets judged, not rediscovered. An **unrecorded**
  one is itself the finding.

**2. Hypothesis fit**

- Read the hypothesis from the spec.
- "If a user enters this screen, does their path lead to the behavior this hypothesis predicts?"
- Flag if: primary CTA below the fold, primary action not visually dominant, unnecessary friction in
  the critical path.
- **And check the measurement**, which nobody checks: can this surface actually emit the success
  signal? A variant that cannot, by construction, is not a bug in the screen; it is a hole in the
  contract. That is a `divergência`, not a design fix.

**3. Visual hierarchy + CTA**

- Where does the eye land? (mental F-pattern / Z-pattern)
- Is the primary CTA the most salient element?
- More than one "primary" CTA competing? (frequency: high)
- **Does the most important message get the weakest treatment?** The line that explains why the user
  is here, set in the smallest type on the page, is a real and common failure.

**4. Consistency with the design system + edge cases**

- Do the tokens used match the source? Do the components used exist? Is inline custom documented?
- States present: `loading`, `empty`, `error`, and "no permission" where it applies.
- **Empty containers**: a reserved frame with nothing in it becomes an empty `div` in code, or a
  question for the dev. Fill it or remove it.

**5. Copy, read word by word**

Read every string in every variant. Not scanned, read.

- **Grammar and typos** in what the user actually reads, especially the headline and the primary
  action. A duplicated preposition in the hero is not a nitpick.
- **Labels naming a process that does not exist.** "Continuar contratação" where no contracting
  started. The word promises a state the system is not in.
- **Claims against their source.** When the brief cites a number or a fact, check the string against
  it. "Junte-se a 14 mil advogados" where the source says "14.000 usuários ativos" is a _different
  claim_, and on a commercial surface an unsupported claim is a liability, not a rounding error.
- **Terms the product does not use with customers**: internal vocabulary leaking into the interface.
- **Trailing/leading whitespace** in labels: invisible on the canvas, real in the string.
- **Per-variant semantics**: the same string can be correct in one variant and nonsense in another.

**6. Contrast, computed as a number**

Not "looks low". Compute the ratio for every text-on-background pair you can resolve and compare
against the threshold for that size and weight (4.5:1 normal text, 3:1 large text and UI components).
Report `<ratio> contra o mínimo de <minimum>` and name the token that fixes it.

Give the smallest text particular attention, failures cluster there, and it is often the text
carrying state information. When the same failure repeats across every variant, say it once and mark
it **systemic** (a token choice) instead of filing it N times.

If values are unreadable in this medium, put `contrast` in `lenses_skipped` with the reason. **Never
guess a ratio.**

**7. Triangulation, and where the contract itself is wrong**

The three questions from `phase-deliver.md`, answered explicitly:

- Does the built thing honor the research?
- Does the research honor the problem?
- Where they disagree, **who is wrong**. The design, or the framing?

When the answer is the framing, produce a `divergência`. Look specifically for: a cut the research
disproved; a success metric a variant cannot emit; two constraints in the contract that contradict
each other; a dependency the design needs and the system never promised.

The brief ran this reconciliation when it closed. **Run it again**, against the built thing, which
did not exist then.

### Severity

Each issue receives **one** severity:

- `blocker`: blocks merge. E.g.: violates WCAG AA, contradicts hypothesis, breaks DS.
- `significant`: doesn't block, but worth resolving before PR. E.g.: missing state, ambiguous CTA, a
  claim the source does not support.
- **`divergência`**: the build is faithful and you think **a decision in the brief or the spec is
  wrong**. Never blocks. Carries three things: what the contract decided, what you would do instead,
  and the argument. Without the argument it is a preference. Leave it out.
- `minor`: goes in "neighborhood". **Don't use for nitpicking**, only for real things worth noting.

Order the report **by gravity**, and mark which items change **contract or data** versus which are
corrections to the artifact. Those are different conversations with different people, and mixing them
buries the expensive ones.

### At least 1 specific piece of praise

Not cheerleading. Information. Identify 1 decision that worked and say _why_, so the builder maintains that pattern.

### Output: `.brisar/clarisse/design-review.md`

Escreva pra quem **não** é designer também: expanda ponteiro interno no primeiro uso, glose
conceito de design em 5–10 palavras. Um review que ninguém consegue ler não muda nada.

```markdown
# Design review: <projeto>

> Gerado pela fase Deliver do /bb:brisar em <ISO date>
> Confrontado contra: **problema** (.bb/<slug>/spec.md) × **pesquisa**
> (.bb/<slug>/brief-design.md) × **construído** (<meio>)
> Apetite: <small|medium|large>. Rigor do review proporcional
> Lido via: <arquivos | preview | MCP do Paper/Figma/Pencil>

## Resumo

- Surface × variante revisadas: <N>, <lista>
- Não alcançadas: <lista, ou "nenhuma">
- Blockers: <N> · Significants: <N> · **Divergências: <N>** · Minors: <N>
- Lentes puladas: <lista com razão, ou "nenhuma">
- Pronto pra merge: sim | não | só após blockers

## Triangulação

| Pergunta                          | Veredito                           | Em uma linha |
| --------------------------------- | ---------------------------------- | ------------ |
| O construído honra a pesquisa?    | aligned/partial/misaligned         | <razão>      |
| A pesquisa honra o problema?      | aligned/partial/misaligned         | <razão>      |
| Onde discordam, quem está errado? | nada/desenho/enquadramento/os dois | <razão>      |

## O que muda contrato ou dado (leia primeiro)

Itens que **não** se resolvem editando a tela: precisam de decisão de produto, dado novo, ou
mudança no spec. Em ordem de gravidade.

| #   | Onde | O que está errado | Severidade |
| --- | ---- | ----------------- | ---------- |

## Divergências: onde eu discordo do contrato

Não bloqueiam. Cada uma é uma decisão tua.

### [divergência] <título curto>

- **O contrato decidiu:** <o que o brief ou o spec definiu, em palavras próprias>
- **Eu faria:** <a alternativa, concreta>
- **Por quê:** <o argumento: evidência da pesquisa, consequência observável, ou conflito interno
  do contrato. Sem isto, é preferência e não entra.>
- **Se procede:** <o que muda, spec primeiro, depois a tela>

## Por surface × variante

### <surface_name> · <variante>

#### Fidelidade à direção escolhida

<frase: honra/desviou + o quê, em 1 linha>

#### Issues

##### [blocker] <título curto>

- **Onde:** <componente/seção · arquivo:linha, ou prancha/frame>
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

- <decisão específica>, por que: <razão de manter esse padrão>

## Copy: achados de texto

| Variante | String | Problema | Sugestão |
| -------- | ------ | -------- | -------- |

## Contraste: calculado

| Elemento | Cor / fundo | Contraste | Mínimo | Correção |
| -------- | ----------- | --------- | ------ | -------- |

Falha que repete em todas as variantes entra **uma vez**, marcada como **sistêmica**, é escolha
de token, não erro de prancha.

## Neighborhood (issues minor agrupados: não bloqueantes)

- <item>
- <item>

## Decisão final

<ready-to-merge | fix-blockers-first | re-prototype | run-/bb:challenge-se-hipotese-fragil>
```

---

## Mode 2: accessibility audit (`accessibility`)

**Why it exists:** WCAG AA isn't optional for an Inspira product. Accessibility is part of the Deliver contract.

### Decision: inline or delegate?

| Signal                                                     | Action                                                                                                                                                                    |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Builder asked for "deep audit" or "before merging to prod" | **Suggest `/bb:review`'s accessibility audit** (surface scope). Flag in handoff: "Rode `/bb:review`, auditoria de acessibilidade na pasta `<projeto>`, antes de mergear." |
| Quick sanity check during design review                    | **Inline** (5 checks below)                                                                                                                                               |
| Small appetite + hosted prototype                          | **Inline** is sufficient                                                                                                                                                  |

### Inline checks (only if decision = inline)

**1. Color contrast (WCAG AA = 4.5:1 for normal text, 3:1 for large text)**

- For each foreground/background pair used in the prototype, validate.
- If in doubt, suggest the /bb:review accessibility audit. Don't guess values.

> **Don't file this twice.** The design review's lens 6 already computes contrast, and when both
> modes run in the pipeline the numbers are the same. Division of labour: the **design review**
> reports it as a design decision (the token choice is wrong, and here is the token that fixes it);
> the **accessibility checklist** carries it as the compliance record, referencing the review
> instead of restating each row. When only one mode runs, that one carries it in full.

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

````markdown
# Accessibility checklist: <projeto>

> Gerado pela fase Deliver do /bb:brisar em <ISO date>
> Modo: inline | delegated (sugerido /bb:review, auditoria de acessibilidade)
> WCAG target: AA

## Status

- WCAG AA: pass | fail | partial | not-fully-assessed
- Blockers: <N>

## Resultados

### Contraste

- [pass | fail | not-assessed] <par cor X sobre Y>, ratio: <N:1>, target: <N:1>

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

- <item>, fix sugerido: <ação>
- <item>, fix sugerido: <ação>

## Para session.yaml

```yaml
clarisse:
  accessibility:
    wcag_aa_status: <pass|fail|partial|not-assessed>
    mode: inline | delegated
    blockers: [<id1>, <id2>]
```
````

````

---

## Mode 3: Handoff doc (`handoff`)

**Why it exists:** the developer/agent who will implement needs a structured doc. Without it, design decisions are lost and implementation becomes free interpretation.

### Inputs

- `<design_context_path>/tokens.md` + `components.md`, or, on a canvas medium, the DS section of the design brief (same source, read one step earlier)
- `<design_path>/<surfaces[].file>` (visual direction written by brisar Phase 4, in `.bb/<slug>/`) and/or the chosen direction in `gate.design_brief`. **The brief is the richer input when both exist**
- The artifact, via the reader for `medium.chosen`
- `.brisar/session.yaml` (all sections, uses recorded decisions and `tarsila.deviations[]`)

### Output structure

For each surface, generate a section. Don't invent, only map what exists in the artifact + the design context.

### Three things the handoff must say that are easy to forget

1. **Which artifact is the source of truth, and how to read its values.** On a canvas medium, name
   the file, the page and the boards, and say explicitly that exact values (spacing, tokens, copy)
   come **through the MCP, not from a screenshot**. Numbers taken off an image survive all the way
   into production as wrong.
2. **The order of authority when artifacts disagree.** State it once: *where the spec and the design
   disagree, the spec wins. It records the conscious deviations and why. Where the brief and the
   spec disagree, the spec wins: the brief is the research record, the spec is the contract.*
3. **The traps.** Breakpoints that don't match framework defaults, framework defaults reset to
   `initial`, a component whose name misleads, a required prop that makes a component semantically
   wrong here. These came out of the research (Front B). Carry them forward instead of letting the
   implementer rediscover them.

### The spec delta: the contract catching up with the design

Exploration changes decisions. The brief recorded them round by round (living-contract rule); the
handoff is where they **go back into the contract**.

Produce a `## Delta para o spec` section listing what the contract does not yet carry: decisions
taken during design, decisions **revoked**, new constraints discovered while drawing, and any
`divergência` the builder accepted. Each item: what the spec says today, what it should say, and why.

**An empty delta is a valid outcome**: say "nenhum" rather than inventing changes. But an empty
delta after eight rounds of exploration is a signal you did not look: the brief's round history is
the checklist.

The delta is a **proposal**, not an edit. Writing the spec is `/bb:spec`'s job, and the gate offers
it.

### Output: `.brisar/clarisse/handoff.md`

```markdown
# Handoff: <projeto>

> Gerado pela fase Deliver do /bb:brisar em <ISO date>
> Audiência: developer ou agente que vai implementar
> Confrontado contra: hipótese e cortes do brief

## Contexto rápido

- **Hipótese (da spec em .bb/<slug>/spec.md):** <statement>
- **Apetite (do brief):** <small|medium|large>
- **Surfaces no escopo:** <lista>
- **Cortes registrados:** <lista de cortes do brief, pra evitar implementar o que foi cortado>

## Design tokens (referência)

Path: `<design_context_path>/tokens.md`

Resumo (auto-extraído):
- Cores: <lista de tokens principais>
- Spacing scale: <referência>
- Type scale: <referência>

## Componentes do DS usados

| Componente | Onde                               | Variant            |
| ---------- | ---------------------------------- | ------------------ |
| Button     | <surface>.header, <surface>.footer | primary, secondary |
| Card       | <surface>.list                     | default            |
| ...        |                                    |                    |

## Componentes custom (fora do DS)

- **<nome>**: em `<surface>:<location>`, razão: <breve>, sugestão futura: <add ao DS | manter custom>

## Por surface

### <surface_name>

**Intent:** <1 frase do que essa surface faz>

**Hierarchy (top-to-bottom):**
1. <elemento>, token: <ref>, state: <default|hover|active|disabled>
2. <elemento>
3. <CTA primário>, destination/action: <onde leva>

**States:**
- Default: descrição
- Loading: descrição
- Empty: descrição
- Error: descrição
- (outros relevantes)

**Edge cases tratados:**
- <caso 1>
- <caso 2>

**Edge cases NÃO tratados (decidido cortar. Ver cortes do brief):**
- <caso>, razão: <cut_reason>

**Decisões registradas:**
- <decisão 1>, razão: <breve, do design review ou do brief>

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
````

```

---

**Mental recap before closing the phase:**
- Each mode generated its artifact.
- session.yaml has `clarisse:` complete with `status`, `ran_modes`, `next_action`.
- End at the Step 3 gate of `phase-deliver.md` (auditoria de acessibilidade / spec / encerrar), suggest, never invoke.
```
