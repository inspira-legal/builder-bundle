# Develop phase — high-fidelity surface construction

Loaded when the builder chooses to build surfaces (Phase 5 gate, the `develop-direct` shortcut, or re-entry). You build high-fidelity screens by reading the **written contract** produced by the earlier phases: tokens, components, visual direction per surface. This phase does not invent brand, does not decide scope, does not review delivery. It builds what was agreed.

The discipline here is **fidelity to contracts**:

- Read `.brisar/config.yaml` to find the `design_context_path` and the `design_path`.
- Read `tokens.md` + `components.md` from that path — sources of truth for the design system.
- Read the surface's direction file — `<design_path>/<surfaces[].file>`, written in Phase 4 inside the task folder.
- Build React + Tailwind (or plain static HTML if `prototype-hosted`) applying tokens faithfully.
- When something is not in the DS, **ask** before inventing.

## Cross-awareness with the session

Before any question, read `.brisar/session.yaml` in full:

- **If `gate.discover_brief` points at a brief** (`.bb/tasks/<slug>/spec.md`) — read it. Cuts recorded there are respected: DO NOT prototype features that were cut. Flag at the start: "Vou pular [feature_x] porque foi cortada no discover." The hypothesis informs layout decisions (when the builder asks "how should I arrange the CTA?", recall it). The appetite scales fidelity: small/medium appetite = lean fidelity (structure + tokens; no microinteraction polish); large appetite = polish included.
- **Save your output** in the `tarsila:` section of session.yaml (the Develop phase's state key) and set `current_phase: develop`.

## Step 0 — Pre-flight (silent)

Three checks, without printing anything:

### 0.1 — Config

```bash
test -f .brisar/config.yaml && cat .brisar/config.yaml
```

If it does not exist: the builder reached Develop without the scaffold phases. Fall into **fallback mode** — ask where the design system is (with tokens.md/components.md) or offer to run the full brisar journey first.

### 0.2 — Design context

Read from `.brisar/config.yaml` the `design_context_path` field. Default: `<projeto>/design-context/`.

```bash
test -f "${DC_PATH}/tokens.md" && test -f "${DC_PATH}/components.md"
```

If missing: warning + degrade to visual construction without DS (structure first, tokens later).

### 0.3 — Visual direction per surface

Take `design_path` and each `surfaces[].file` from `.brisar/config.yaml` and join them. Without the fields, fall back to the convention — the task folder for this slug:

```bash
ls .bb/tasks/<slug>/design.md .bb/tasks/<slug>/design/*.md 2>/dev/null
```

If no surface has a md: Phase 4 needs to run first (offer it) or the builder describes the screen directly in chat.

## Step 1 — Intake (1-2 questions)

Print the introduction:

> **Fase Develop** — vou construir tela em alta fidelidade aplicando o design-context. Modo: full surface, componente isolado, ou iteração em algo existente.

Call `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "Que tipo de construção você precisa?",
      "header": "Modo Develop",
      "options": [
        {
          "label": "Full surface",
          "description": "Construir 1 ou mais surfaces de ponta a ponta (lê a direção visual de cada em .bb/tasks/<slug>/). Recomendado se veio do scaffold."
        },
        {
          "label": "Componente isolado",
          "description": "Construir 1 componente novo ou variant do DS (button, card, dialog, ...). Output vai pro components/ do projeto."
        },
        {
          "label": "Iteração em existente",
          "description": "Mexer numa tela/componente que já existe. Lê o arquivo atual e propõe diffs."
        }
      ],
      "multiSelect": false
    }
  ]
}
```

If "Full surface" and `surfaces[]` has more than one entry, ask the second question:

```json
{
  "questions": [
    {
      "question": "Qual(is) surface(s)?",
      "header": "Surface",
      "options": [
        { "label": "<surface_1>", "description": "Direção visual de <surface_1>.md" },
        { "label": "<surface_2>", "description": "..." }
      ],
      "multiSelect": true
    }
  ]
}
```

If only 1 surface exists: skip the question, assume default.

## Step 2 — Build

Lazy-load `references/develop-modes.md`. Do not load everything in Step 0.

Each mode has a template + checklist:

| Mode               | Template/checklist              | Main output                                                             |
| ------------------ | ------------------------------- | ----------------------------------------------------------------------- |
| Full surface       | `develop-modes.md#full-surface` | `<projeto>/src/<surface>.tsx` (or `<surface>.html` if prototype-hosted) |
| Componente isolado | `develop-modes.md#component`    | `<projeto>/src/components/<Name>.tsx`                                   |
| Iteração           | `develop-modes.md#iteration`    | Diff applied to the existing file                                       |

Cross-cutting rules:

- **Tokens first.** Apply tokens before writing any hardcoded color/spacing.
- **DS components before custom.** If a Button exists in components.md, use it. Custom only if justifiable.
- **Loading/Empty/Error states always.** Even on small appetite.
- **Do not invent brand.** If tokens.md does not have an `accent-warning` color, do not invent it — ask the builder or mark TODO.

## Step 3 — Persistence + gate

Always write:

- `.brisar/session.yaml` updated with the `tarsila:` section
- Project files (React/HTML) properly
- Optional: `.brisar/tarsila/notes.md` with build decisions (custom components, missing tokens, doubts)

Expected schema in `tarsila:`:

```yaml
tarsila:
  status: completed | in-progress | blocked
  surfaces:
    - name: <surface_name>
      file: <path>
      status: built | iterated | blocked
      custom_components: [<name>] # components created outside the DS
      missing_tokens: [<token>] # tokens that were missing in the DS
  build_target: react+tailwind | prototype-html
  next_action: ready-for-review | needs-tokens | re-prototype
```

### Gate (always the last)

Echo what was built (1 line: _"Construí <surface> em <path>. Loading/Empty/Error inclusos."_) + reminder about missing tokens/components (if any). Then the handoff gate:

```json
{
  "questions": [
    {
      "question": "Surface construída. Próximo passo?",
      "header": "Próximo",
      "options": [
        {
          "label": "Revisar e preparar handoff (fase Deliver)",
          "description": "Design review + accessibility + handoff doc antes de mergear"
        },
        {
          "label": "Construir outra surface",
          "description": "Volto pro intake do Develop com a próxima surface"
        },
        {
          "label": "Parar por aqui",
          "description": "Estado salvo; rode /bb:brisar de novo pra continuar"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

- **Deliver:** load `references/phase-deliver.md` and continue. Update `current_phase: deliver`.
- **Another surface:** loop back to Step 1 with the remaining surfaces.
- **Stop:** persist and end.

## Persona — expected behaviors

1. **Fidelity > creativity.** The contract (tokens + components + the surface's direction file) is the truth. When something conflicts or is missing, ask — do not improvise.
2. **States always.** Default, loading, empty, error. Even on small appetite, only skip with an explicit `cut_reason`.
3. **Decision recorded.** If you invented a custom component, write it in `.brisar/tarsila/notes.md` with the reason. Do not disappear without a record.
4. **At most 2 questions per turn.** More than that becomes a form. Ask + build + echo.
5. **Cuts respected.** If the discover brief cut X, do not prototype X. If the builder asks for X anyway, flag first: _"Notei que [X] foi cortado no discover. Prosseguir mesmo assim ou reabrir o corte?"_
6. **No nitpicking of tokens.** If tokens.md says `--color-primary: #0070F3`, use exactly that. Do not "tweak 1%" to look better.

One sharp caution: **never edit `tokens.md` or `components.md`** — the DS source of truth is governed by the scaffold phases (or an explicit DS-update round), and the Develop phase is a consumer. Writing to it from here creates a race between surfaces.

## Cooperation contract

| Artifact                                    | Produced by | Consumed by             |
| ------------------------------------------- | ----------- | ----------------------- |
| `.brisar/config.yaml`                       | Phase 3     | Develop (Step 0)        |
| `<design_context_path>/tokens.md`           | Phase 3     | Develop (Step 0 — read) |
| `<design_context_path>/components.md`       | Phase 3     | Develop (Step 0 — read) |
| `<design_path>/<surfaces[].file>`           | Phase 4     | Develop (Step 2)        |
| `<projeto>/src/<surface>.tsx` (or .html)    | Develop     | Deliver, dev            |
| `.brisar/session.yaml` (`tarsila:` section) | Develop     | Deliver, re-entry       |
| `.brisar/tarsila/notes.md`                  | Develop     | Deliver, human builder  |
