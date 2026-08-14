# Phase 4 — Design direction (per surface)

The missing piece. Without this, brisar would end without concrete direction to start designing. The builder opens the editor, sees an empty App.tsx, and now what?

This phase produces the visual direction for each confirmed surface, with enough brief for the builder (or the Develop phase) to start designing. Each file has 5 fixed sections: Visual hierarchy, DS components, States, First sketch direction, Notes.

**Where it lands:** inside the task's folder, next to the spec — the plugin-level `references/spec-state.md` owns that contract. One surface writes `.bb/<slug>/design.md`; two or more write `.bb/<slug>/design/<surface>.md` plus an index. The project folder scaffolded in Phase 3 holds code and design-context, not design direction.

## Step 1 — Confirm surfaces

Phase 1 inferred provisional surfaces from the initial prompt (e.g.: `[busca, resultados, vazio]`). Confirm before generating files:

```json
{
  "questions": [
    {
      "question": "Identifiquei estas surfaces a partir da sua descrição: [<surfaces_provisional>]. Confirma essa lista, quer ajustar, ou tem outras?",
      "header": "Surfaces",
      "options": [
        {
          "label": "Confirma a lista",
          "description": "Vou gerar a direção visual de cada uma em .bb/<slug>/"
        },
        { "label": "Ajustar / adicionar", "description": "Texto livre — separe por vírgula" },
        {
          "label": "Só uma surface principal",
          "description": "Texto livre — só a que importa agora"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

If the builder answers "adjust" or "only one", parse the response. Limit to 5 surfaces per session (more than that turns into noise — additional surfaces enter in re-runs).

Slugify each surface: lowercase, kebab-case, ASCII (`Tela de busca` → `busca`, `Resultado vazio` → `vazio`, etc).

## Step 2 — Resolve the task folder, then the index

Resolve `.bb/` per the spec-state contract (nearest ancestor with one, else create it in the cwd) and use `.bb/<slug>/` — the same `<slug>` as the project. If a spec already sits there (`spec.md`, from `/bb:discover`), the folder exists; otherwise `mkdir -p` it.

With **one** confirmed surface, write `.bb/<slug>/design.md` with the Step 3 template and skip the index — an index of one is ceremony.

With **two or more**, write `.bb/<slug>/design/<surface>.md` for each plus `.bb/<slug>/design/README.md`:

```markdown
# Design — <slug>

> Gerado por /bb:brisar em <data>. Marca: <brand>.

Surfaces nesta sessão (ordem sugerida — desenhe de cima para baixo):

1. [<surface-1>](./<surface-1>.md) — <breve descrição inferida>
2. [<surface-2>](./<surface-2>.md) — ...
3. ...

## Por que essa ordem

A regra geral:

1. **Começo pelas surfaces de "default state"** — telas que o usuário vê na maior parte do tempo.
2. **Depois empty/loading** — estados frequentes mas não-default.
3. **Depois error/edge** — críticos mas raros.
4. **Por último, transições e overlays** (modais, drawers, sheets).

Se sua estrutura é diferente, edite este README à vontade — é seu projeto.

## Como construir

Rode `/bb:brisar` de novo na pasta do projeto — ele detecta o projeto e oferece a fase Develop. A fase lê `design-context/` para tokens/componentes, e o arquivo desta pasta para o brief da surface específica. Recomendo desenhar uma surface por vez.
```

## Step 3 — Generate one file per surface

Template:

```markdown
# <Surface name title-cased>

> Surface de <slug> — gerado por /bb:brisar.
> Marca: <brand> · Fidelidade: <fidelity>

## Hierarquia visual

[Infer from the surface name + context of the original prompt. Always name:

- The anchor element (what dominates the frame visually)
- The secondary element (what supports the anchor)
- The tertiary (metadata, secondary actions)

Examples:

- "busca" → anchor: search input · secondary: filters · tertiary: recent history
- "vazio" → anchor: illustration + heading · secondary: primary CTA · tertiary: docs link
- "resultados" → anchor: results list · secondary: side filters · tertiary: pagination

Each bullet in one sentence. Do not write more than 5 bullets — if you need to, rethink the surface.]

## Componentes do DS a usar

[List 3-7 components from `design-context/components.md` that fit here. For each, say "for X" or "for Y" — do not blindly copy the list.

Examples:

- `Text Input` — for the main search field
- `Button (Primary)` — "Search" CTA
- `Tag / Pill` — for the recent searches history
- `Feedback Banner (info)` — for tip of the day (optional)

If any component that fits is NOT in scope (see `components.md`), list it in "Notes → DS gaps" below, not here.]

## Estados a desenhar

[Always 4 minimum states — adapt to the context. Each on a single line:

- **Default** — [what appears when the surface is healthy and has data]
- **Loading** — [what appears while loading; skeleton or spinner]
- **Empty** — [what appears when there's no data; "how to start" CTA]
- **Error** — [what appears when it fails; clear message + recovery path]

For critical surfaces, also consider: focused, hover, disabled, selected.]

## Primeira sketch direction (3 bullets)

[Three concrete sentences that the builder can start drawing WITHOUT needing to think more. Don't be vague. Don't philosophize.

Examples:

- Place the search input centered, taking 60% of the width, with a pt-BR placeholder.
- Below the input, 3 chips with recent searches (use Tag / Pill), max-width 320px.
- When focusing the input, expand height by 8px and show a tip line ("Try searching for...").

These 3 bullets are enough to break the blank page. The Develop phase and the builder iterate from here.]

## Notas

### Gaps de DS

[List any required component that does NOT exist in the current DS. It will become a seed for future DS feedback. If there are no gaps, write "Nenhum identificado nesta surface."]

### Decisões a tomar antes de desenhar

[Things you need to decide but brisar cannot decide for you. E.g.:

- How many results per page?
- Are filters single-select or multi-select?
- Does the empty state have an illustration or only text?

Max 3 items. If the list grows, it's a sign that this surface needs more shaping.]
```

## Step 4 — Update .brisar/config.yaml and session.yaml

### config.yaml — fill in `design_path` and `surfaces`

`design_path` is the absolute path of the task folder; each `file` is relative to it. Three surfaces:

```yaml
design_path: "<absolute path of .bb/<slug>/>"

surfaces:
  - name: busca
    file: design/busca.md
    state: drafted
    last_updated: <ISO>
  - name: resultados
    file: design/resultados.md
    state: drafted
    last_updated: <ISO>
  - name: vazio
    file: design/vazio.md
    state: drafted
    last_updated: <ISO>
```

One surface:

```yaml
design_path: "<absolute path of .bb/<slug>/>"

surfaces:
  - name: busca
    file: design.md
    state: drafted
    last_updated: <ISO>
```

### session.yaml — mark final phase

```yaml
current_phase: done
status: completed
completed_at: <ISO>

# Adds the record of what was generated:
surfaces_confirmed:
  - busca
  - resultados
  - vazio
```

## Inference — how to make decent surfaces.md without being robotic

The difference between a useful design.md and a generic one is the **specificity of the original prompt**. Use `intent.raw_prompt` from Phase 1 and `brand.design_md_path` to enrich:

- For Lexflow: remember it is dark theme. Visual hierarchy should mention gradient cards when relevant (composer hero), JetBrains Mono for technical chips, etc.
- For Inspira: remember it is light theme + Rich Black for primary CTAs.
- For custom: cite the base and say explicitly "adjust from here".

If the builder asked for "search screen" and the brand is Lexflow, the busca file MUST reflect the composer dark gradient as reference (not Inspira's white input).

When you're lost about what to write in "Visual hierarchy" or "First sketch direction" for a surface, read the brand's entire DESIGN.md once — there will be a concept (DarkGradientCard, HeroTitle two-line accent-split, etc.) that serves as an anchor.

## When a surface does not fit the template

If a surface is fundamentally different (e.g.: API debug surface, command palette, login splash), don't force the template. Adapt design.md to what makes sense. But keep the 5 sections (Hierarchy / Components / States / Sketch / Notes) — they work for 95% of cases and giving them as a backbone avoids a totally improvised design.md.
