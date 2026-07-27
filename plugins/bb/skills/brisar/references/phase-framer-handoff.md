# Phase Framer-handoff — bypass scaffold, generate handoff to HARPA

Replaces Phase 2 (gate) + Phase 3 (scaffold) + Phase 4 (design-direction) **only when** `brand.workflow == framer-harpa`. The builder is building on the Site Institucional, which lives in Framer + `harpa-lpbuilder`, not in Vite + React.

## Why this phase exists

The standard brisar flow (Vite + Tailwind + design-context/) is incompatible with Framer:

- Framer doesn't accept Tailwind nor CSS modules — code components use inline styles only.
- Tokens live as Framer color styles (`/Rich Black`, `/Centaurea`, `/Cornflower`), not as CSS vars.
- The `harpa-lpbuilder` bundle already has rules equivalent to tokens.md/components.md (in `.claude/rules/`), plus the `mcp-unframer-co` MCP to sync with live Framer.

The wrong thing would be to scaffold a React app here. The right thing is **to capture the intent from the lightning intake and deliver it as context for the builder to use inside harpa-lpbuilder**.

## What this phase does

Just one thing: writes `harpa-handoff-<slug>-<YYYY-MM-DD>.md` in the cwd with what the builder will paste (or reference) in the Claude session inside `harpa-lpbuilder/`. Doesn't create a folder, doesn't scaffold, doesn't touch Framer files.

## Step 1 — Check if the harpa-lpbuilder repo exists locally

```bash
test -d ~/Desktop/harpa-lpbuilder && echo "found-desktop" \
  || test -d ./harpa-lpbuilder && echo "found-cwd" \
  || find ~ -maxdepth 4 -type d -name "harpa-lpbuilder" -not -path "*/node_modules/*" 2>/dev/null | head -3
```

Three outcomes:

- **Found**: record the path. Will cite it in the terminal handoff.
- **Not found**: record `harpa_repo_path: null`. The handoff will include the `git clone` in Step 5.

## Step 2 — Write harpa-handoff-<slug>-<date>.md

Use Write to create the file in the cwd. Template:

```markdown
# HARPA handoff — <slug>

> Gerado por /bb:brisar em <data>.
> Use este arquivo dentro de `harpa-lpbuilder/` quando você abrir Claude Code lá.

## Contexto rápido

- **Slug:** <slug>
- **Escopo Framer:** <new-page | section-in-existing | edit-existing | exploration>
- **Apetite:** <appetite>
- **Brand:** Site institucional (Inspira)
- **Stack:** Framer canvas + code components React/TS com inline styles only

## O que estou construindo (intent original)

<intent.raw_prompt da Phase 1>

## Como começar a sessão (cole isto na primeira mensagem do Claude Code dentro de harpa-lpbuilder)
```

Quero <intent.raw_prompt>.

Escopo: <framer.scope>.
Apetite: <appetite>.

Antes de qualquer ação:

1. Roda `mcp__mcp-unframer-co__getProjectXml` para confirmar que o Harpa está em foco no Framer desktop. Se vier projeto errado (Modo B), me avisa antes de seguir.
2. Lê `.claude/rules/design-tokens.md` e `.claude/rules/components.md` (Modo A — fonte de verdade live; Modo C — fallback em `references/`).
3. Para `<framer.scope == new-page>`: scan a Building Blocks page via `getNodeXml` e me proponha 2-3 composições antes de criar a página.
   Para `<framer.scope == section-in-existing>`: me pergunte qual página alvo, depois `getNodeXml` da página e proponha onde a seção entra.
   Para `<framer.scope == edit-existing>`: me pergunte qual elemento alvo (rota + nome do bloco), depois `getNodeXml` desse nó específico.
   Para `<framer.scope == exploration>`: comece em Modo C (rascunho code-only) — vou colar no Framer manualmente depois.
4. Reuse-first: nunca crie componente novo sem antes confirmar comigo que nenhum existente serve.
5. Responsive-first: desktop → tablet (810px) → mobile (390px) overrides.
6. Inline styles only. WCAG AA. Português pt-BR.

```

## Direção visual (rascunho — refine na sessão)

<Se framer.scope ∈ {new-page, section-in-existing}, gere 3-5 bullets de direção visual em idiom Framer:>

- **Composição:** [como organizar Stacks/Frames — ex: "hero full-bleed com Stack vertical centralizado: Eyebrow + H1 (Instrument Serif se for hero, senão Poppins Semibold) + sub + CTA primário"]
- **Componentes a reutilizar:** [liste blocos que existem no Building Blocks — ex: "Hero/Centered, CTA/Primary, Section/SplitWithImage"]
- **Tokens-chave:** [`/Rich Black 100%` para headlines, `/Cornflower 100%` para CTA, `/Cool Gray 60%` para body — sempre comentar nos code components com a Framer style name]
- **Responsive notes:** ["em mobile, o split vira stack vertical; CTA full-width abaixo de 600px"]
- **Estados:** [se aplica — hover de CTA, foco de input, estado vazio de CMS list, etc.]

<Se framer.scope == edit-existing: pular essa seção. Ajuste fino é melhor decidido na sessão com o XML em mão.>

## Open questions (decidir na sessão Framer, não aqui)

- Conteúdo (copy, imagens) — quem fornece, quando.
- CMS — vai usar coleção existente ou precisa criar?
- Animações — Framer Motion variants ou só hover states?
- Métrica — vai trackear conversão? Onde?

## Riscos / heads-up

<Inclua se relevante:>
- Se `framer.scope == edit-existing` E `appetite == hoje`: alerte que mudanças no ar precisam de Modo A (MCP live), não Modo C — caso contrário, dois caminhos divergentes vão sair.
- Se `framer.scope == new-page` E `appetite == hoje`: produção de página completa em horas é viável só reutilizando blocos. Não é momento para componente novo.
- Se `framer.scope == exploration`: fica em Modo C; o Framer só recebe o resultado depois de validação visual local.

---

Próximo passo: vide o terminal do /bb:brisar (variante Framer em phase-5-handoff.md).
```

## Step 3 — Update .brisar/session.yaml (in cwd, without creating a new folder)

Since this path does NOT scaffold, `.brisar/session.yaml` stays in the cwd where /brisar was run, not inside `<slug>/`.

```yaml
status: completed
current_phase: done
completed_at: <ISO>

intent: <from Phase 1>
brand:
  name: site-institucional
  workflow: framer-harpa
  source: external-bundle
  design_md_path: null
artifact:
  fidelity: framer-canvas
  hosting: framer-harpa
shaping:
  appetite: <appetite>
framer:
  scope: <framer.scope>
  handoff_file: "harpa-handoff-<slug>-<YYYY-MM-DD>.md"
  harpa_repo_path: <path detected in Step 1, or null>

# Phase 2 (gate) and Phase 3 (Vite scaffold) were NOT executed — Framer path does not use them.
gate:
  fired: false
  resolution: not-applicable-framer-path
```

## Step 4 — Call phase-5-handoff.md in "framer terminal" mode

Phase 5 already has conditional variants (production override, custom brand, etc.). Add/use the "framer terminal" variant there — it prints the instructions for how to enter the `harpa-lpbuilder` session and the path of the generated handoff file.

## One sharp caution

Never scaffold or generate design-context on the Framer path. The single handoff file in the cwd is the whole output: `harpa-lpbuilder/.claude/rules/` already carries the token/component equivalents (duplicating creates drift), the Develop phase is not used (the Claude session inside `harpa-lpbuilder` does that work), and the `mcp-unframer-co` MCP belongs to that session, not this one. If the builder doesn't have the MCP configured, the markdown handoff still works — mention they can add the MCP to their Claude config (`~/.claude.json`, `mcpServers` block) for the live-canvas path next time.
