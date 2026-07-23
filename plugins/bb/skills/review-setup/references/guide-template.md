# CODE_REVIEW_GUIDE.md — template and generation rules

Write the guide at the repo root with the Write tool, filled from the validated
rules. The guide is self-contained — anyone reading it understands every rule
without external context. Guide prose in PT-BR; rule IDs, code examples, and
technical terms in English.

Required content:

1. **Propósito** — reference before opening PRs + the rule source `/bb:review`
   reads fresh on every run.
2. **Severidades** — the HIGH/MEDIUM/LOW ladder and its verdict impact.
3. **Pre-PR checklist** — numbered, actionable, derived from the HIGH and MEDIUM
   rules (concrete commands: the repo's own test/lint invocations).
4. **Rules by severity** — every rule with ID, título, lens, descrição,
   evidência (real paths), and Do/Don't examples from the repo.
5. **Categorização de arquivos** — file patterns → categories, so a reviewer
   knows which rules apply to which files.
6. **Padrões do repositório** — sections only for what was actually discovered
   (commits, organização, testes, error handling, observabilidade, segurança,
   domínios custom).
7. **Arquivos de referência** — canonical examples of each major pattern.
8. **Histórico de alterações** — one row per generation/update.

## Template

```markdown
# Code Review Guide — {{PROJECT_NAME}}

> **Última atualização**: {{DATE}}
> **Gerado por**: /bb:review-setup
> **Stack**: {{STACK_SUMMARY}}

## Propósito

Regras de code review do **{{PROJECT_NAME}}**: referência pré-PR pros devs e
fonte de regras do `/bb:review` (lido fresh a cada run). Toda convenção do repo
está documentada aqui com evidência.

## Severidades

| Nível      | Significado                                                          | Impacto no review                                  |
| ---------- | -------------------------------------------------------------------- | --------------------------------------------------- |
| **HIGH**   | Não negociável — quebra de contrato, teste ausente, vulnerabilidade  | Veredito: CHANGES REQUESTED                         |
| **MEDIUM** | Requer julgamento; 3+ num PR indica degradação                       | 1–2: NEEDS DISCUSSION / 3+: CHANGES REQUESTED       |
| **LOW**    | Informativo, nit                                                     | Nunca afeta o veredito                              |

## Pre-PR Checklist

{{PRE_PR_CHECKLIST}}

## Regras

### HIGH

| ID | Título | Lens |
| -- | ------ | ---- |
{{HIGH_RULES_TABLE}}

{{HIGH_RULES_DETAIL}}

### MEDIUM

{{MEDIUM_RULES_TABLE_AND_DETAIL}}

### LOW

{{LOW_RULES_TABLE_AND_DETAIL}}

## Categorização de Arquivos

| Categoria | Patterns | Exemplos |
| --------- | -------- | -------- |
{{FILE_CATEGORIES_TABLE}}

## Padrões do Repositório

{{REPO_PATTERNS_SECTIONS}}

## Arquivos de Referência

| Padrão | Arquivo | Descrição |
| ------ | ------- | --------- |
{{REFERENCE_FILES_TABLE}}

## Histórico de Alterações

| Data     | Tipo    | Descrição                          |
| -------- | ------- | ----------------------------------- |
| {{DATE}} | Criação | Guia gerado pelo /bb:review-setup   |
```

Rule detail block, one per rule:

```markdown
#### {{ID}} — {{TITLE}}

- **Lens**: logic-edges | async-state | contracts-security | quality
- **Severidade**: HIGH | MEDIUM | LOW
- **Descrição**: o que a regra garante e por quê
- **Evidência**: paths do repo que mostram o padrão
- **Faça**:
  ```{{lang}}
  {{good example from the repo}}
  ```
- **Evite**:
  ```{{lang}}
  {{bad example}}
  ```
```

## Generation rules

- The **Lens** field maps each rule to the `/bb:review` lens that enforces it
  (`logic-edges`, `async-state`, `contracts-security`, `quality`) — that's how
  the engine routes guide rules to its fan-out agents.
- Every example is real (from the repo) — never invent code to illustrate a
  rule; a rule without a real example gets evidence paths only.
- Only rules the maintainer accepted in the interview enter the guide.
- Sections with nothing discovered are omitted, not filled with boilerplate.
