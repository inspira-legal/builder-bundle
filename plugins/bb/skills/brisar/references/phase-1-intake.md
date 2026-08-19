# Phase 1: lightning intake (depth adapts to persona_id)

The previous version asked 6-10 questions just to reach "now I'll frame it." This phase cuts that, but the number and language of the questions vary by the `profile.persona_id` captured in Phase 0. When the trade-off of skipping the framing isn't worth it (serious artifact, persona = senior/junior), Phase 2 (maturity gate) pulls /bb:discover into the flow.

## Step 0a: shortcut router (pre-persona)

Before branching by persona, brisar checks whether the builder mentioned **specific intent for a later stage of the trilha**. When there's a clear signal, it shortens the pipeline: jumps to the right phase (or suggests /bb:discover) instead of running the full intake + scaffold.

It reads `intent.raw_prompt` (what the builder typed) + `preflight.product.detected` + the presence of `.brisar/session.yaml` in the cwd.

### Shortcut matrix

| Signal in raw_prompt                                                                                                          | Cwd                                                 | Shortcut          | Target                   | What brisar does                                                                                                                         |
| ----------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- | ----------------- | ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| "uma tela", "só design", "protótipo rápido", "desenhar X", "construir tela Y"                                                 | already-scaffolded repo (has `.brisar/config.yaml`) | `develop-direct`  | Develop phase (internal) | Skips intake. Writes `intent.shortcut: develop-direct` to session.yaml. After confirmation, jumps to `references/phase-develop.md`.      |
| "revisa esse design", "preciso de doc pra dev", "antes de mergear", "fechar deliver", "preparar PR"                           | repo with surfaces in `src/` or `<surface>.html`    | `deliver-direct`  | Deliver phase (internal) | Skips intake. Writes `intent.shortcut: deliver-direct`. After confirmation, jumps to `references/phase-deliver.md`.                      |
| "shapear", "maturar problema", "vale a pena", "validar mercado", "tem demanda", "preciso cortar escopo", "priorizar features" | any                                                 | `discover-direct` | `/bb:discover`           | Skips intake. Writes `intent.shortcut: discover-direct`. Suggests `/bb:discover` (it runs its own intake) and STOPS, never auto-invokes. |
| "quero começar", "novo projeto", "scaffolda", "tela X em marca Y" (default)                                                   | any                                                 | none              | (follows normal flow)    | Persona branch below.                                                                                                                    |

### When the shortcut fires

1. Print a short confirmation, example for `develop-direct`:

   > **/bb:brisar**: detectei que você quer construir direto. Vou pular o intake e entrar na fase Develop. Confirma?

2. `AskUserQuestion` requesting confirmation:

   ```json
   {
     "questions": [
       {
         "question": "Atalho detectado: <alvo>. Pular intake?",
         "header": "Atalho",
         "options": [
           {
             "label": "Sim, pular pra <alvo>",
             "description": "A fase/skill alvo roda seu próprio intake. Vai puxar contexto direto."
           },
           {
             "label": "Não, fluxo completo",
             "description": "Roda o intake normal (calibração + 3 perguntas + scaffold)."
           }
         ],
         "multiSelect": false
       }
     ]
   }
   ```

3. If "Sim" → writes `intent.shortcut` and a minimal session.yaml. For `develop-direct`/`deliver-direct`, load the target phase file and continue there. For `discover-direct`, suggest `/bb:discover <ideia>` and STOP.
4. If "Não" → continues normally to Step 0b (persona branch).

### Why confirmation is mandatory

A heuristic-detected shortcut may be wrong. Asking for confirmation costs 1 turn and avoids skipping context the builder wanted to build (for example: "preciso de doc pra dev" might be part of a larger intake, not necessarily a jump to Deliver).

### When NOT to fire the shortcut (even with a signal)

- No `.brisar/config.yaml` in cwd AND signal is `develop-direct`: scaffold is a prerequisite for the Develop phase. Falls into the normal flow; the Phase 5 gate offers Develop at the end.
- Persona `executive` or `content` detected in Phase 0: skip shortcuts. These paths have operational/brand-first intake that doesn't combine well with short-circuit.

---

## Step 0b: branch by persona

Read `.brisar/session.yaml` field `profile.persona_id`. Route:

| `persona_id`     | Goes to                                                                             | How many questions                                         |
| ---------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `builder-senior` | [Senior variant](#variante-senior-2-perguntas)                                      | 2 (intent + brand, with brand skipped if product detected) |
| `builder-junior` | [Standard flow](#pergunta-1--o-que-você-está-construindo) below + narration         | 3                                                          |
| `executive`      | [Executive variant](#variante-executive-linguagem-operacional)                      | 5-6 in operational language                                |
| `content`        | **Does NOT enter Phase 1.** Jumps straight to `references/phase-framer-handoff.md`. | 0 (intake-Framer-variant)                                  |

If `persona_id` is missing: assumes `builder-junior` (Phase 0 fallback) and follows the standard flow.

If `preflight.product.detected != unknown`: brand, hosting, and (sometimes) artifact are already derived from the product, skip those questions regardless of persona. Use [Shortcuts with product detected](#atalhos-com-produto-detectado).

---

## Senior variant (2 questions)

Senior dev, technical vocabulary OK, no narration of every `cd`. Path optimized for minimum friction.

Print a short intro:

> **/bb:brisar**: perfil senior detectado. 2 perguntas e te jogo no editor.

### Senior question #1: intent

```json
{
  "questions": [
    {
      "question": "O que você está construindo? Uma frase.",
      "header": "Intent",
      "options": [
        {
          "label": "Resposta livre",
          "description": "Ex: 'tela de busca semântica em LexFlow' ou 'componente Chat novo no DS'"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

Derives slug + surface inference, same as the standard flow.

### Senior question #2: brand/product (CONDITIONAL)

- If `preflight.product.detected != unknown`: SKIP. Brand + hosting are already known.
- Otherwise: use the standard Question 2 (brand registry).

Question 3 (artifact/hosting/appetite) **does not run for senior** when product is detected. The product's `mode_default` defines this. Senior in greenfield (product = `greenfield-vite`) gets the standard question 3.

Short echo + proceed to Phase 2 (gate runs as usual).

---

## Junior variant (standard flow + narration)

Junior uses the 3 questions below (Question 1, 2, 3), exactly like senior in greenfield, but with **explicit narration** in each echo. Each echo needs to explain:

- What's going to happen in the next step
- How long it takes
- What file/command to look at

Example of junior echo (vs senior):

| Senior                                    | Junior                                                                                                                    |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| "Slug: `lexflow-busca`. Indo para marca." | "Slug derivado: `lexflow-busca`. Vou usar como nome da pasta. Próximo: pergunta de marca pra eu saber que tokens copiar." |

When in Phase 5 (handoff), junior receives narrated instructions for each command (see `phase-5-handoff.md`).

---

## Executive variant (operational language)

Executive doesn't have technical vocabulary. **NEVER use**: scaffold, embed, MCP, repo, branch, slug, hosting, fidelity, Shaping appetite, surface. **Use**: folder, project, install, environment, page, area.

Print a short intro:

> **/bb:brisar**: vou te ajudar a sair de "ideia" pra "protótipo clicável que dá pra mostrar pro time". Vou fazer 5 perguntas rápidas em linguagem do dia-a-dia.

### Exec question #1: what

```json
{
  "questions": [
    {
      "question": "O que você quer construir? Em uma frase, do jeito que explicaria pra um colega.",
      "header": "Ideia",
      "options": [
        {
          "label": "Resposta livre",
          "description": "Ex: 'plataforma pra gestão financeira do setor', 'ferramenta pra acompanhar contratos do time jurídico'"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

### Exec question #2: who uses it

```json
{
  "questions": [
    {
      "question": "Quem vai usar essa ferramenta?",
      "header": "Usuários",
      "options": [
        {
          "label": "Time interno (operações, financeiro, RH, etc)",
          "description": "Ferramenta interna, não tem cliente externo"
        },
        {
          "label": "Advogados internos da Inspira",
          "description": "Ferramenta pra advogados da casa"
        },
        {
          "label": "Cliente da Inspira",
          "description": "Ferramenta voltada pra fora, cliente final"
        },
        {
          "label": "Misto / não sei ainda",
          "description": "Tem mais de um público, ou ainda em definição"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

### Exec question #3: what problem it solves

```json
{
  "questions": [
    {
      "question": "Qual problema essa ferramenta resolve hoje?",
      "header": "Problema",
      "options": [
        {
          "label": "Resposta livre",
          "description": "Em uma frase. Ex: 'gente perde tempo achando contrato em pasta', 'não tem visibilidade do orçamento por área'"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

### Exec question #4: visual

```json
{
  "questions": [
    {
      "question": "Como você quer que pareça visualmente?",
      "header": "Visual",
      "options": [
        {
          "label": "Cara da Inspira (azul/preto, claro)",
          "description": "Marca-mãe. O jeito padrão da Inspira"
        },
        {
          "label": "Cara do LexFlow (escuro, dev-tool)",
          "description": "Visual escuro, tipo ferramenta de programador"
        },
        {
          "label": "Outra marca interna (Stillare, etc)",
          "description": "Tem identidade própria, me fala qual"
        },
        {
          "label": "Não sei / decida por mim",
          "description": "Uso Inspira como base. Você ajusta depois"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

### Exec question #5: when

```json
{
  "questions": [
    {
      "question": "Quando você quer ter algo pronto pra mostrar?",
      "header": "Prazo",
      "options": [
        {
          "label": "Pra essa semana",
          "description": "Urgência. Protótipo simples vai ter que servir"
        },
        { "label": "Em ~2 semanas", "description": "Tempo razoável pra explorar" },
        { "label": "Sem prazo definido", "description": "Quero fazer direito" }
      ],
      "multiSelect": false
    }
  ]
}
```

### Exec question #6: next step (CONDITIONAL, only if answer to #1 implies a serious product)

```json
{
  "questions": [
    {
      "question": "Depois do protótipo: alguém da engenharia vai pegar pra virar produto de verdade?",
      "header": "Continuação",
      "options": [
        {
          "label": "Sim, vou passar pro time técnico",
          "description": "Protótipo é pra validar; alguém constrói depois"
        },
        {
          "label": "Não, só preciso pra mostrar/validar",
          "description": "Pode ficar como demo mesmo"
        },
        { "label": "Ainda não sei", "description": "Depende do feedback que receber" }
      ],
      "multiSelect": false
    }
  ]
}
```

### How to read (executive)

Map to the session.yaml schema:

- Question #1 → `intent.raw_prompt` + derived `slug`
- Question #2 → `intent.audience` (new field: `internal-team | internal-lawyers | client | mixed`)
- Question #3 → `intent.problem_statement`
- Question #4 → `brand.name` (or `deferred` if "não sei")
- Question #5 → `shaping.appetite` mapped: "essa semana" → `1 week`, "~2 semanas" → `2 weeks`, "sem prazo" → `undefined`
- Question #6 → `intent.scale_signal`: "sim, eng pega" → `will-scale`, "não, só demo" → `exploration`, "não sei" → `exploration`

**Always force:**

- `artifact.fidelity: prototype-hosted` (HTML variant, not local Vite)
- `artifact.hosting: prototype-hosted`
- `intent.persona: executive`

Short echo in operational language. E.g.: _"Recebido, projeto: 'plataforma de gestão financeira'. Pra time interno. Pra essa semana. Vou montar um protótipo HTML clicável que você pode abrir no navegador e mostrar pro time. Vai gerar uma pasta `<slug>/` com arquivos prontos + um `HANDOFF-DEV.md` que o time técnico usa pra continuar."_

**Phase 2 (gate) does NOT run for executive.** Goes straight to Phase 3 prototype-hosted variant.

---

## Shortcuts with product detected

When `preflight.product.detected` is a known product (inspira-saas, portal-cliente, stillare, lexflow, ds-inspira), several fields are already derivable. Skip the corresponding questions:

| Field                  | Source                                    |
| ---------------------- | ----------------------------------------- |
| `brand.name`           | `product.brand`                           |
| `brand.design_md_path` | derived from `product.ds_source`          |
| `artifact.hosting`     | `embedded` (always, for detected product) |
| `mode`                 | `product.mode_default` (usually `embed`)  |

What still needs to be asked:

- **Question #1 (intent)**: always, without this there's nothing to build
- **Appetite/scale_signal**: only for senior/junior (executive on detected product is rare; if it happens, force `will-scale` and continue)

Echo when product is detected: _"Detectei que você tá em [Stillare/LexFlow/etc]. Pulei marca e hospedagem, já sei. Próximo: [pergunta intent]."_

---

## Question 1: what are you building?

Print a short intro:

> **/bb:brisar**: trilha de design. Vou fazer 3 perguntas rápidas e em poucos minutos você tem um projeto scaffoldado e direção visual para começar a desenhar. Use "Other" para texto livre em qualquer momento.

Then `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "O que você está construindo? Descreva em uma frase, vou usar para nomear a pasta do projeto.",
      "header": "Projeto",
      "options": [
        {
          "label": "Resposta livre",
          "description": "Em uma frase, ex: 'tela de busca semântica para Lexflow' ou 'landing page nova institucional'"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

### How to read

The answer serves two purposes:

1. **Project slug**: derive in sanitized kebab-case (lowercase, ASCII, no stopwords). E.g.: "tela de busca semântica para Lexflow" → `lexflow-busca-semantica`. E.g.: "landing page nova institucional" → `landing-institucional`. Cap at 50 characters.
2. **Surface inference (provisional)**: suggest main surfaces. E.g.: "busca" → `[busca, resultados, vazio]`. "landing" → `[hero, beneficios, cta]`. Will be confirmed/adjusted in Phase 4.

If the phrase is vague ("um app", "alguma coisa nova"), ask ONCE for specificity: _"Pode ser mais concreto? Ex: 'painel de filtros para advogados', 'editor de petições', 'tela de onboarding'."_ If still vague, accept with `intent.confidence: low` and continue.

Short echo: _"Recebido, slug: `<slug>`. Indo para marca."_

## Question 2: brand

Use the registry built in Step 0.3. Construct the options dynamically:

**Always inject `Site institucional (Framer)` as a fixed option, before "Sem marca / custom"**: it's a different surface (Framer + harpa-lpbuilder), not a registry brand. It's a forked path, not a brand.

```json
{
  "questions": [
    {
      "question": "Qual marca?",
      "header": "Marca",
      "options": [
        {
          "label": "Inspira",
          "description": "Marca-base, light theme, Cornflower Blue + Rich Black"
        },
        { "label": "Lexflow", "description": "Sub-marca dev-tool: dark theme, GitHub Primer" },
        {
          "label": "Site institucional (Framer)",
          "description": "Não é Vite, usa Framer + harpa-lpbuilder. Vou redirecionar para esse fluxo."
        },
        {
          "label": "Sem marca / custom",
          "description": "Vou criar identidade própria, white-label ou nova marca"
        },
        { "label": "Ainda não sei", "description": "Decidir depois, registre como pendente" }
      ],
      "multiSelect": false
    }
  ]
}
```

### How to read

- **Site institucional (Framer)**: register `brand.name: site-institucional`, `brand.workflow: framer-harpa`, `brand.design_md_path: null`. **SKIP the entire Question 3 (the artifact/hosting/appetite question in the original format) and use the [Question 3 Framer-variant](#pergunta-3-framer-variant-só-quando-brandworkflow--framer-harpa) below.** The flow continues differently from here. Phase 2 (gate) is skipped and Phase 3 becomes `references/phase-framer-handoff.md` instead of the normal scaffold.
- **Known brand (Inspira, Lexflow, etc.)**: register `brand.name`, `brand.source: registry`, `brand.design_md_path: <path>`. Echo: _"Marca [X], vou copiar tokens de `<path>` no scaffold."_
- **No brand / custom**: do a follow-up:
  ```json
  {
    "questions": [
      {
        "question": "Como começar a identidade?",
        "header": "Custom",
        "options": [
          { "label": "Partir da Inspira", "description": "Clone tokens da Inspira, ajusto depois" },
          { "label": "Partir da Lexflow", "description": "Clone tokens da Lexflow, ajusto depois" },
          { "label": "Começar do zero", "description": "Só Tailwind primitives, sem brand layer" },
          {
            "label": "Tenho tokens externos",
            "description": "Vou colocar em design-context manualmente"
          }
        ],
        "multiSelect": false
      }
    ]
  }
  ```
  Register `brand.source: custom-from-inspira | custom-from-lexflow | from-scratch | external-tokens`. For custom-from-X, copy the tokens of the base brand but register `brand.name: custom`, `brand.design_md_path: null`.
- **Don't know yet**: register `brand: deferred`. Use Inspira as fallback in the scaffold but warn: _"Vou usar Inspira como base; quando decidir, edita `<slug>/design-context/tokens.md` ou roda `/bb:brisar` de novo."_
- **Empty brand registry (DS not-found)**: fall back to free-text mode. Ask which brand, register `brand.source: free-text`, use Tailwind primitives in the scaffold.

Short echo.

## Question 3 Framer-variant (only when `brand.workflow == framer-harpa`)

When the builder chose "Site institucional (Framer)", the fidelity/hosting questions from the Vite path don't make sense (Framer is hi-fi by definition; hosting is always the existing Framer project). Replace with:

```json
{
  "questions": [
    {
      "question": "O que você está construindo no site? (página nova, seção em página existente, ou edit em conteúdo já no ar)",
      "header": "Escopo Framer",
      "options": [
        {
          "label": "Página nova",
          "description": "Criar uma página inédita no Harpa. Vai ter rota nova"
        },
        {
          "label": "Seção em página existente",
          "description": "Adicionar/redesenhar bloco em página que já existe"
        },
        {
          "label": "Edit em conteúdo já no ar",
          "description": "Mexer em copy, imagens, ou ajuste fino sem mudança estrutural"
        },
        { "label": "Ainda não sei o escopo", "description": "Vou explorar, começa rascunhando" }
      ],
      "multiSelect": false
    },
    {
      "question": "Apetite + prioridade",
      "header": "Apetite",
      "options": [
        { "label": "Hoje: urgência", "description": "Precisa ir pro ar essa semana" },
        { "label": "Esta semana: normal", "description": "Iteração padrão de marketing" },
        {
          "label": "2 semanas, campanha",
          "description": "Lançamento de feature, anúncio, ou marco"
        },
        { "label": "Sem prazo: exploração", "description": "Estudo de redesign, experimento" }
      ],
      "multiSelect": false
    }
  ]
}
```

### How to read (Framer-variant)

Capture:

- `framer.scope` ∈ `{new-page, section-in-existing, edit-existing, exploration}`
- `shaping.appetite` (mapped to "1 day" / "1 week" / "2 weeks" / "undefined")
- `artifact.fidelity: framer-canvas` (constant for this path)
- `artifact.hosting: framer-harpa` (constant)
- `intent.scale_signal: commitment` (constant. Institutional site is always production)

**Important:** `intent.scale_signal: commitment` AND the normal Phase 2 gate does not fire here. Framer + harpa-lpbuilder is already the production path, there's no scaffold to gate. Jump directly to `references/phase-framer-handoff.md`.

Short echo: _"Site institucional / Framer, escopo: [X], apetite: [Y]. Vou montar handoff para o fluxo HARPA."_

---

## Question 3: artifact + hosting + appetite + scale (standard variant, NON-Framer)

> Use only when `brand.workflow != framer-harpa` (Inspira, Lexflow, custom, deferred. Anything that will become a Vite scaffold).

Combined question (a single `AskUserQuestion` with 2 questions, both structured):

```json
{
  "questions": [
    {
      "question": "O que você quer no final + onde isso vai viver?",
      "header": "Artefato",
      "options": [
        {
          "label": "Protótipo low-fi (standalone)",
          "description": "Wireframe clicável, repo novo"
        },
        {
          "label": "Protótipo mid-fi (standalone)",
          "description": "Visual aplicado, mockado, repo novo"
        },
        {
          "label": "Protótipo hi-fi (standalone)",
          "description": "Visual final, dados mock, repo novo"
        },
        {
          "label": "Protótipo hi-fi (embedded)",
          "description": "Visual final dentro de app existente"
        },
        {
          "label": "Produto no ar (standalone)",
          "description": "Deploy real, repo novo, dados reais"
        },
        {
          "label": "Produto no ar (embedded)",
          "description": "Deploy real, app existente, dados reais"
        },
        { "label": "Storybook só", "description": "Componente isolado para review" }
      ],
      "multiSelect": false
    },
    {
      "question": "Apetite + intent de escala",
      "header": "Apetite",
      "options": [
        { "label": "1 dia: exploração", "description": "Sprint relâmpago, descartável" },
        { "label": "1 semana: exploração", "description": "Pequeno e focado, ainda exploração" },
        { "label": "2 semanas: exploração", "description": "Médio porte, ainda testando" },
        {
          "label": "2 semanas, vai escalar",
          "description": "Médio porte, mas o protótipo vai virar produto"
        },
        {
          "label": "6 semanas, commitment",
          "description": "Ciclo Shaping clássico, comprometido com o resultado"
        },
        { "label": "Sem prazo definido: vai escalar", "description": "Open-ended, mas sério" }
      ],
      "multiSelect": false
    }
  ]
}
```

### How to read

Capture:

- `artifact.fidelity` ∈ `{low-fi, mid-fi, hi-fi, production, storybook-only}` (mapped from the 7 labels)
- `artifact.hosting` ∈ `{standalone, embedded, storybook-only}` (mapped)
- `shaping.appetite` (string)
- `intent.scale_signal` ∈ `{exploration, will-scale, commitment}`, derived from the second question

The combination `artifact.fidelity` + `intent.scale_signal` feeds Phase 2 (maturity gate). Don't cross-check here, just capture and continue.

Brief echo with the 3 pieces of data together: _"Recebido, protótipo hi-fi standalone, 1 semana de exploração. Indo para o gate."_

## State to persist

At the end of Phase 1, write a partial `.brisar/session.yaml`:

```yaml
version: 1
status: in-progress
created_at: <ISO>
current_phase: phase-2

intent:
  type: new
  confidence: high
  scale_signal: exploration # exploration | will-scale | commitment
  raw_prompt: "<what the builder typed in P1>"
  slug: "<derived slug>"

brand:
  name: Lexflow
  source: registry
  design_md_path: brand/lexflow/DESIGN.md

artifact:
  fidelity: hi-fi
  hosting: embedded

shaping:
  appetite: "1 week"

surfaces_provisional:
  - busca
  - resultados
  - vazio
```

`surfaces_provisional` is a list inferred from the prompt, not confirmed. Phase 4 will refine it. Useful for the gate to decide context.
