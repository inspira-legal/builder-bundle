# Phase 5 — Handoff + gate

After Phase 4 writes the visual direction of each surface into `.bb/tasks/<slug>/`, the journey-map part of brisar is done. This phase prints the handoff summary (persona-shaped) and ends with the **handoff gate** — a single `AskUserQuestion` offering the natural next steps. The gate suggests, never auto-invokes (per `plugins/bb/references/handoff-gate.md`).

## Output shape (default — senior/standard)

Plain text, in pt-BR. Structure:

```
✓ /bb:brisar terminou o scaffold. Projeto em ./<slug>/

Estrutura criada:
  <slug>/
  ├── package.json, vite.config.ts, tsconfig.json
  ├── src/{main.tsx, App.tsx, index.css, tokens-brand.css}
  ├── design-context/{tokens.md, components.md}     ← a fase Develop lê isto
  └── .brisar/{config.yaml, session.yaml}

  .bb/tasks/<slug>/                                  ← junto do brief
  └── design/                                        ← brief de cada surface
      ├── README.md (ordem sugerida)
      ├── <surface-1>.md
      ├── <surface-2>.md
      └── <surface-3>.md

Para rodar:

  cd <slug>
  pnpm install
  pnpm dev
```

With a single surface, that last block is one line — `.bb/tasks/<slug>/design.md`.

Then the gate:

```json
{
  "questions": [
    {
      "question": "Scaffold pronto. Próximo passo?",
      "header": "Próximo",
      "options": [
        {
          "label": "Construir as surfaces agora (fase Develop)",
          "description": "Continuo nesta sessão: leio design-context/ + a direção visual em .bb/tasks/<slug>/ e construo tela a tela"
        },
        {
          "label": "Rodar /bb:discover antes",
          "description": "Aprofundar o enquadramento (problema, fit, hipótese, apetite) antes de desenhar"
        },
        {
          "label": "Parar por aqui",
          "description": "Projeto fica pronto; rode /bb:brisar de novo nesta pasta quando quiser construir"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

- **Develop:** load `references/phase-develop.md` and continue in this same session. Update `current_phase: develop`.
- **/bb:discover:** suggest the command (`/bb:discover <ideia em 1 frase>`) and STOP — never invoke it.
- **Stop:** print one line saying the re-entry works (`/bb:brisar` in this folder resumes) and end.

## Conditional variants

### If persona = executive (path prototype-hosted)

**Replaces the whole default terminal** — executive doesn't run `pnpm dev` and the Develop phase doesn't apply (design goes straight to HTML in Phase 4).

```
✓ /bb:brisar terminou. Protótipo HTML criado em ./<slug>/

O que tem aqui:
  <slug>/
  ├── index.html              ← abra esse arquivo no navegador (dois cliques)
  ├── <surface-1>.html        ← uma página por tela
  ├── <surface-2>.html
  ├── styles.css              ← visual da marca <brand>
  ├── README.md               ← como mostrar pro time
  └── HANDOFF-DEV.md          ← pacote pro time técnico continuar

  .bb/tasks/<slug>/           ← o brief escrito de cada tela fica aqui

Como abrir:
  1. Vá na pasta <slug>/ no Finder
  2. Dê dois cliques em index.html
  3. Vai abrir no navegador. Os links na página levam pra cada tela.

Não precisa instalar nada. Funciona offline.

Como mostrar pro time:
  - Compartilhe a pasta zipada (cada pessoa abre o index.html)
  - Ou peça pro time de eng hospedar (Vercel/Netlify) — vira um link

Pra virar produto de verdade:
  Passe a pasta + HANDOFF-DEV.md pro time técnico. Eles re-escrevem
  no stack real (Vite + React + Tailwind v4 com os tokens da marca).
  HANDOFF-DEV.md tem todas as instruções.
```

If the builder marked `intent.scale_signal == will-scale`, add at the end:

```
⚠ Você marcou que esse protótipo VAI virar produto. Antes do time técnico
pegar, considere rodar /bb:discover — deixa problema, hipótese e métrica
claros, e economiza retrabalho depois.
```

No Develop gate here — end with a simple report. Mention `/bb:discover` as the optional next step (as above) and stop.

### If persona = junior (explicit narration)

Same default terminal, but with narration before the gate:

```
✓ /bb:brisar terminou o scaffold. Vou te guiar pelos próximos passos:

1. Abra um terminal nessa pasta. Comando:
       cd <slug>

2. Instale as dependências (vai demorar 1-2 minutos):
       pnpm install
   Se você não tem pnpm: instale com `npm install -g pnpm` antes.

3. Rode o servidor de desenvolvimento:
       pnpm dev
   Vai aparecer um link tipo http://localhost:5173 — abra no navegador.

Se algo der errado em qualquer passo, me avise — eu ajudo a debugar.
```

Then the same gate as the default variant (Develop / /bb:discover / stop). In the Develop option description, add that each step will be narrated.

### If path Framer (`brand.workflow == framer-harpa`)

**Replaces the whole default terminal** — the builder doesn't have a `<slug>/` to cd into. The path is to open Claude Code inside `harpa-lpbuilder/`. See `phase-framer-handoff.md` for the terminal it prints. No Develop gate — the Develop phase is not used on the Framer path.

### If Phase 2 fired and the builder chose override

Add before the gate:

```
⚠ Heads up: você marcou "<scale_signal>" mas pulou o gate de maturidade.
Override registrado em .brisar/session.yaml com a razão "<override_reason>".
Se em algum momento sentir que faltou fundamentação, rode /bb:discover —
é onde isso resolve.
```

### If brand: deferred

Add:

```
⚠ Marca: ainda não decidida. Usei tokens da Inspira como fallback.
Quando decidir, edite <slug>/design-context/tokens.md ou rode /bb:brisar de novo.
```

### If brand.source ∈ {custom-from-inspira, custom-from-lexflow, from-scratch, external-tokens}

Add:

```
⚠ Marca custom (<source>): tokens iniciais herdados de <base>.
Edite <slug>/design-context/tokens.md conforme a identidade evoluir.
Quando estabilizar, considere promover para um DESIGN.md próprio em <DS_PATH>/brand/<nome>/.
```

### If DS not-found

Add:

```
⚠ Design system não foi encontrado neste ambiente. Tokens do scaffold são
Tailwind defaults com placeholders. Aponte BRISAR_DS_PATH ou configure
ds_path em .brisar/config.yaml — o bundle também traz uma cópia em
references/ds/ dentro da própria skill.
```

### If DS gaps were detected in Phase 4

Add:

```
🌱 Gaps de DS detectados nas surfaces:
  - <surface>: <componente faltando>
  - ...

Esses ficaram registrados em .brisar/session.yaml como ds_feedback_seeds.
Revise/promova quando quiser — são candidatos a componentes novos do DS.
```

## Critical behavior

- **Do not execute `cd`, `pnpm install`, or the dev server.** The user runs them. Auto-execution violates the builder's expectation and creates side effects without confirmation.
- **Surface errors explicitly.** If any file from Phase 3/4 failed to be written, mention it instead of simulating success.
- **Always include the path on the first line** (`./<slug>/` is relative — good; `<slug>` alone is ambiguous). The builder may be following logs; ambiguity here costs time.

## When to run /bb:brisar again in the same project

If the builder returns to the same `<slug>/` and runs /bb:brisar:

- Step 0 detects `.brisar/session.yaml` with `status: completed` + existing `.brisar/config.yaml`.
- Asks:
  ```
  Já existe um projeto Brisa aqui (<slug>, marca <brand>, <N> surfaces). O que fazer?
  - Construir/iterar surfaces (fase Develop)
  - Revisar/handoff do que existe (fase Deliver)
  - Adicionar surface nova (vai pra Phase 4)
  - Trocar marca (regrava design-context/, mantém src/)
  - Re-enquadrar (sugiro /bb:discover)
  - Recomeçar do zero (arquiva .brisar/session.archived-<ISO>.yaml antes)
  ```
- Routes accordingly. "Re-enquadrar" suggests `/bb:discover` and stops; "Recomeçar" always archives the old session first.

This is the re-entry contract. Not used on the first invocation, but keeps the skill useful in subsequent sessions.
