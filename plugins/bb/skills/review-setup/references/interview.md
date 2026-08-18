# Interview: the maintainer validates every rule

Every interaction goes through `AskUserQuestion` (question text and option
labels in PT-BR): rationale and the "Other" convention in the plugin-root
`references/handoff-gate.md`.

Processing each answer, always in this order:

1. Read the selected option from the tool result.
2. Confirm it in one printed line, `"Regra {ID}: você escolheu [{opção}]."`,
   so the user sees it registered.
3. Apply the decision **before** presenting the next item. "Confirmar como
   MEDIUM" means the rule enters the guide as MEDIUM; "Ignorar" means it's gone.
4. Free-text via "Other" gets interpreted and applied (severity change,
   rewording, merge, skip).

## Setup mode

### Confirmed rules: one batch

Print the confirmed rules as an informational table (ID, título, severidade,
categoria), context only, no questions in the text. Then immediately ask:

```
question: "Revisou as regras confirmadas acima. Sigo com todas ou ajusta alguma?"
header: "Confirmadas"
options:
  - "Confirmar todas": entram no guia como listadas.
  - "Ajustar algumas": quero mudar severidade, remover ou reformular alguma.
```

"Ajustar algumas" (or free text) → interpret and apply; ask a follow-up
`AskUserQuestion` if the request is vague.

### Candidate rules: one at a time, never grouped

For EACH candidate: print ID, título, o que foi observado no repo (com paths),
a inferência proposta, evidência, severidade sugerida, then immediately ask:

```
question: "Regra {ID}, {Title} (sugestão: {SEVERITY}). Confirma, ajusta ou ignora?"
header: "{ID}"
options:
  - "Confirmar {SEVERITY}": aceitar com a severidade sugerida.
  - "Confirmar como HIGH": não negociável, sempre seguida.
  - "Confirmar como MEDIUM": importante, mas com julgamento.
  - "Ignorar": não é uma regra válida pra este repo.
```

Only after confirming the answer does the next candidate appear.

## Update mode (incremental: only what changed)

Never re-ask about rules that didn't change. Three question shapes:

- **New pattern detected:** "Novo padrão detectado: {descrição}. Criar regra?", options: "Sim, HIGH" / "Sim, MEDIUM" / "Sim, LOW" / "Não, ignorar".
- **Drifted rule:** "A regra {ID} parece desatualizada: {evidência}. O que
  fazer?", options: "Atualizar com o novo padrão" / "Remover do guia" /
  "Manter como está".
- **Obsolete pattern:** "O padrão da regra {ID} não aparece mais no codebase.
  Remover?", options: "Remover" / "Manter (pode voltar)".

## Priorities

Validation order when time/attention is short: functional delivery > repo
patterns > best practices > security-hardening nits. Each question's
informational text must carry the repo evidence. The maintainer decides on
facts, not on trust.
