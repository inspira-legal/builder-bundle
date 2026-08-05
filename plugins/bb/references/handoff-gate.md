# Handoff gate — the one convention for "what's next"

Every skill whose outcome has a natural next step ends with a **handoff gate**: a
single `AskUserQuestion` that offers the next skill(s) in the journey. The gate is
how the bundle gives the user a sense of place — "here's where you are, here's
what usually comes next" — without ever deciding for them.

## Why the tool (applies to any question, not just gates)

Anything expecting an answer goes through `AskUserQuestion` — a question printed
as plain text has no response path, so the flow stalls. The tool auto-provides
an "Other" free-text option; a manual "Outro"/"Modificar" option is redundant.

## The rule

- **Suggest, never auto-invoke.** A gate offers; the user picks. The only
  exceptions: `/bb:delegate` (the explicit "run everything" verb — chaining is its
  job), and the `implement → ship` auto-chain when shipping was already authorized
  up front (a delegate run, or the unattended frame).
- **"Encerrar aqui" is always an option.** Picking it ends the turn — nothing is
  invoked, no follow-up question. The user is never trapped in the flow.
- **One gate per skill, at the end.** Mid-skill questions are the skill's own
  business (gray areas, confirmations); the handoff gate is the last interaction.
- **Skills without a natural next step have no gate** — they just report and stop:
  `legal-lens`, `maintain-repo`, `review-setup`, `write-readme`,
  `code-deep-research`, `gather-branch-context`.
- **Unattended runs never gate.** Under `BB_UNATTENDED` the skill takes its
  documented lean, records the choice, and proceeds (see the unattended addendum).

## The format

Ask one question, in PT-BR (all gate text the user sees is PT-BR):

- `question`: one sentence naming what just finished and asking how to follow.
- `options`: 2–4, each a next skill (or action) with a one-line description of
  what invoking it will do **now**. Lead with the recommended pick and suffix its
  label with `(Recomendado)`.
- Last option: **"Encerrar aqui"** — description says what stays saved and how to
  pick the flow back up later (the exact `/bb:<skill>` command).

Example (spec's exit gate, 3-way):

```
question: "Brief validado e salvo em .bb/tasks/<slug>/spec.md. Como seguimos?"
options:
  - "Implementar (Recomendado)" — Rodo /bb:implement agora: construo os slices e paro pronto pra ship.
  - "Delegar" — Rodo /bb:delegate <slug>: implement + ship de ponta a ponta.
  - "Encerrar aqui" — Brief fica salvo; retome depois com /bb:implement ou /bb:delegate <slug>.
```

## Journey map (what gates typically offer)

- `discover` → spec (é código) / brisar (é design) / challenge (testar a tese) / encerrar
- `spec` → implement / delegate / encerrar
- `implement` → ship / encerrar
- `ship` → review (da PR aberta) / encerrar
- `review` → aplicar mais itens / rodar as frentes que faltaram / auditar a UI rodando / review-setup / ship (quando não há PR) — no máximo três, por prioridade, + encerrar
- `brisar` (ao entregar) → review (auditoria de acessibilidade) / spec / encerrar
- `think` (quando convergiu) → spec / discover / encerrar
- `challenge` → devolve a tese ao dono; oferece spec quando a tese sobreviveu e é construível
