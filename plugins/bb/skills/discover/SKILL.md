---
name: discover
description: Roda o primeiro diamante inteiro antes de qualquer design — enquadra o problema (problema, quem sente, hipótese, sinal de sucesso, apetite) e pressure-testa o encaixe (vale construir?, o que cortar, em que ordem, qual aposta testável). Escreve o enquadramento na spec que o /bb:spec lê como intenção. Use quando o usuário disser "qual problema estamos resolvendo", "enquadra o problema", "vale a pena construir", "valida o mercado", "o que cortar pra caber", "prioriza essas features", "roda o trio", "shapeia essa ideia", "pivot ou persevere", ou chegar com uma dor difusa em vez de uma feature pronta. NÃO use pra desenhar a solução (use /bb:spec), pra estressar uma tese já formada (use /bb:challenge), nem pra uma mudança mecânica pequena.
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 2.3.0
---

# Discover

Run the whole first diamond: get the **problem** sharp, then decide **what
survives to design**. Framing the wrong problem crisply still ships the wrong
thing — this is the lowest-cost moment to catch that. The output is a spec
seeded with framing and fit that `/bb:spec` reads as upstream intent.

Two phases, each with its own reference — load only the one that's running:

| Phase                         | What it settles                                                                      | Reference             |
| ----------------------------- | ------------------------------------------------------------------------------------ | --------------------- |
| **1 — Frame** (o problema)    | problem, who & impact, hypothesis, success signal, appetite — each confidence-tagged | `references/frame.md` |
| **2 — Fit** (o que sobrevive) | worth building? what to cut, in what order, the one testable hypothesis              | `references/fit.md`   |

## Entry decision

Read the invocation and any existing spec before asking anything:

- **Fresh pain or idea** → full pipeline, Phase 1 then Phase 2.
- **Spec already carries `## Problema` / `## Hipótese`** (an earlier discover
  run, or written by hand — the English `## problem` / `## hypothesis` counts the
  same) → echo the trio in one line and go straight to Phase 2.
- **A specific fit ask** ("o que cortar", "prioriza", "vale a pena construir")
  → Phase 2, that mode only; if no framed problem exists, suggest Phase 1 once
  (non-blocking) and note `ran without a framed problem` in `## Encaixe` if declined.
- **Spec already complete** (all four sections) → confirm whether this is an
  audit/re-run before re-asking anything.

## Interview discipline (both phases)

- **Draft-first, never an interrogation.** Develop best-guess values from the
  one-liner and the codebase/context, mark them as guesses, and bring something
  to react to.
- **Anything expecting an answer goes through `AskUserQuestion`** (rationale in
  the plugin-root `references/handoff-gate.md`). **At most 2 questions per turn** (more turns it
  into a form, and forms get form-shaped answers), each with concrete options
  and your lean. Decide the obvious yourself.
- **Echo before advancing.** One line after each turn ("Recebido — problema: X,
  hipótese: Y.") so a misread surfaces in seconds, not in sprint three.
- **Confidence-tag everything** `[low | med | high]`; **skip with a reason,
  never a silent blank** (`skipped — <reason>` is information; a blank is debt).
- **Vagueness is data.** Clarify once; if still fuzzy, accept at `low`
  confidence and move on. Where you'd be guessing at a fact (market size,
  competitors, prior art), check — codebase, then docs, then web — and tag what
  you find.

All user-facing text — echoes, question labels, reports — is PT-BR.

## Capture (on disk)

Both phases accrete the same spec, resolved per the spec-state contract
(plugin-level `references/spec-state.md`): `.bb/<slug>/spec.md`. Generate
`<slug>` as a short kebab name for the
problem area; if the file exists for a _different_ idea, suffix it (`-2`) or ask
— never overwrite another spec. Section formats live in each phase's reference.
Keep deferred ideas as plain bullets marked _revisit_ — never checkboxes, so the
task selector never mistakes them for work.

## Handoff gate

End with one `AskUserQuestion` per the plugin-level `references/handoff-gate.md`.
Lead with the pick the fit verdict supports: `next_action: build-mvp` → spec;
`validate-first` or low confidence → challenge; design-led work → brisar.

```
question: "Primeiro diamante fechado — problema enquadrado e fit decidido em .bb/<slug>/spec.md. Como seguimos?"
options:
  - "Especificar (Recomendado)" — Rodo /bb:spec agora: desenho a solução em cima do problema e do fit.
  - "Design" — Rodo /bb:brisar: direção visual e prototipagem pra trabalho design-led.
  - "Desafiar" — Rodo /bb:challenge: estresso a tese antes de investir na construção.
  - "Encerrar aqui" — A spec fica salva; retome depois com /bb:spec ou /bb:discover.
```

When the fit verdict is `shelve` or `pivot`, there is nothing to hand off —
report the verdict with its evidence and stop (a pivot points back to
`/bb:discover` with the reframed problem).

## Edge cases

| WHEN                                       | THEN                                                                               |
| ------------------------------------------ | ---------------------------------------------------------------------------------- |
| slug exists for a different idea           | suffix `-2` or ask — never overwrite                                               |
| answer still vague after one clarification | accept at `low` confidence and move on                                             |
| a field can't be answered                  | record `skipped — <reason>`                                                        |
| fit asked with no framed problem           | suggest Phase 1 once; if declined, proceed and note `ran without a framed problem` |
