---
name: challenge
description: Advogado do diabo estruturado. Estressa posições, ideias, planos e decisões antes de agir, com steelman obrigatório. Cinco modos (Socrático, Falsificação, Dialético, Pre-mortem e Red Team). Use quando o usuário já tem uma posição formada e disser "me desafia", "desafia isso", "o que pode dar errado", "pre-mortem", "red team", "questiona minhas premissas", "o que tem de errado com", "testa minha hipótese". NÃO use quando a posição ainda não existe. Pra explorar uma ideia crua, use /bb:think; pra enquadrar um problema de produto, /bb:discover.
license: MIT
metadata:
  author: Matheus Morais; adapted for bb by Athena Briana - github.com/athenabriana
  version: 2.1.0
---

# Challenge

Structured devil's advocate. Stress-tests positions, ideas, plans, and decisions
before the user acts. It never builds. It challenges, with rigor and
intellectual honesty, and every critique points toward improvement. All
user-facing text is PT-BR.

## Workflow

### Step 1: Identify and steelman

Extract the user's position from the conversation context. If it is vague, ask
one clarifying question before proceeding, never fabricate a thesis.

Apply the steelman protocol from the plugin-root
`references/confidence-and-steelman.md`: strongest version first, confirmed
with the user before any challenge.

### Step 2: Select the mode

Ask via `AskUserQuestion`:

```
question: "Como você quer desafiar essa tese?"
options:
  - "Questionar premissas". Sonda o que está sendo tomado como verdade sem evidência.
  - "Construir contra-argumento". Defende a posição oposta com força máxima.
  - "Encontrar pontos de falha". Antecipa como isso pode falhar ou ser explorado.
  - "Você decide". Eu recomendo o modo mais útil pro contexto.
```

Two picks need one follow-up question (also via `AskUserQuestion`):

- **Questionar premissas** → _"Explorar as premissas (Socrático) ou auditar as
  evidências (Falsificação)?"_
- **Encontrar pontos de falha** → _"Projetar como falha (Pre-mortem) ou atacar
  adversarialmente (Red Team)?"_
- **Você decide** → evaluate the context, recommend the mode, and say briefly
  why.

### Step 3: Apply the mode

Read the chosen mode's section in `references/modes.md` and apply it against the
steelmanned thesis. Identify cognitive biases present in the user's reasoning
and weave them into the challenges as patterns to watch, not accusations.
Apply the frameworks without naming them out loud.

### Step 4: Present the challenges

Present the **3–5 strongest challenges**, quality over quantity. Each challenge
must be specific and concrete (never a generic "e se X?"), grounded in real
reasoning, and point toward improvement. Attack the steelmanned version, and let
the strongest objections carry the weight rather than stacking minor ones.

Then explicitly ask the user to respond to each challenge. The synthesis waits
for those responses.

### Step 5: Synthesize

Integrate the user's responses with the challenges into a strengthened position:

1. Concede the challenges that were successfully refuted.
2. Incorporate valid objections into the refined position.
3. Name the trade-offs that remain unresolved.
4. Issue the **confidence assessment** (HIGH / MEDIUM / LOW / PIVOT) per the
   plugin-root `references/confidence-and-steelman.md`.

## Handoff

The thesis goes back to its owner. The synthesis is the deliverable. Gate only
when the thesis **survived** (HIGH or MEDIUM) **and** is something buildable;
format per the plugin-level `references/handoff-gate.md`:

```
question: "Desafio fechado. A tese saiu fortalecida (confidence <X>). Como seguimos?"
options:
  - "Especificar (Recomendado)". Rodo /bb:spec agora: transformo a tese numa spec construível.
  - "Encerrar aqui". A síntese fica com você; retome com /bb:spec quando quiser construir.
```

On LOW, report the synthesis and stop. The smallest experiment comes before any
build. On PIVOT, point to `/bb:discover` to reframe the problem, and stop.
