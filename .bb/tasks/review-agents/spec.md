---
status: in-progress
created: 2026-08-04
slug: review-agents
---

# bb-finder e bb-verifier — capability scoping pro fan-out do review

## what

Publicar dois agentes definidos no plugin (`plugins/bb/agents/bb-finder.md` e
`plugins/bb/agents/bb-verifier.md`), por **papel no pipeline** e não por frente, e
passar o fan-out do `/bb:review` (e, por empréstimo, do `/bb:ship`) a despachá-los
via `subagent_type`. O `tools:` do frontmatter passa a ser quem garante que finder
e verifier não escrevem; a prosa que hoje garante isso vira ponteiro.

Junto: o contrato invariante de cada papel migra pro system prompt do agente (dono
único), e o CI aprende a validar `agents/*.md`.

## why

O read-only dos finders hoje é garantido por prosa (`fronts.md:77` — "read-only —
they report, never edit"), mas o `.claude/CLAUDE.md` do repo manda **"enforce
irreversible hazards with capability scoping, not prose"**. É o mesmo raciocínio
já aplicado duas vezes no repo (never-merge e outward-posting saíram da prosa pro
capability scoping da routine).

O dano concreto: um finder que decide consertar o que achou quebra o single-writer
com até 5 agentes escrevendo em paralelo na mesma working tree — corrupção difícil
de atribuir, porque o relatório não registra edits que ninguém pediu.

## decisions

| decisão                            | escolha                                                                                                                                                                                                                         |
| ---------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| dois agentes, por papel            | `bb-finder` e `bb-verifier`. As diferenças entre frentes são conteúdo de prompt que o caller já monta (angle set, criteria path, scope block, Finding shape) — um agente por frente seria 7 nomes globais guardando a mesma metade invariante. |
| `tools:` dos dois                  | `Read, Grep, Glob, Bash`. **Decisão do usuário**, com o custo declarado: `tools:` é por nome de ferramenta, então `sed -i` e `>` continuam alcançáveis via Bash. O scoping tira o que o modelo naturalmente alcança (Edit/Write), não é hermético. Bash é o que mantém `git diff <range>` e `gh pr diff` (mode-external-pr) funcionando sem inflar o scope block. |
| dono do contrato                   | O **agente** é o dono. A rubrica CONFIRMED/PLAUSIBLE/REFUTED (+ viés de PLAUSIBLE, + REFUTED só quando construtível do código) migra pro prompt do `bb-verifier`; o contrato do finder (consequência nomeável, não auto-censurar) migra pro `bb-finder`. `verify.md §2`, `fronts.md` item 5 e o parágrafo de consequência do `front-correctness.md` deferem numa linha. Mesma disciplina de dono único do `9a461e8`. |
| o que **não** migra                | A verificação por citação de `rules`/`contract`/`a11y` (`verify.md`, seção "verificam diferente") fica na referência e o caller anexa ao prompt do verifier — é conteúdo por frente, não invariante de papel. Idem: campos da Finding shape, angle sets, caps. |
| fallback                           | Realocar, não deletar. `fronts.md:77` e `review/SKILL.md:91` viram "os finders vão como `subagent_type: bb-finder` — read-only por capability", uma linha cada. O invariante segue nomeado uma vez, mas quem o garante é o frontmatter; o item 6 do `fronts.md` (sem Agent tool) continua cobrindo o host sem fan-out. |
| CI                                 | `validate-frontmatter.ts` passa a caminhar em `agents/*.md` (name + description obrigatórios) **e falha se um agente do bb listar `Write`/`Edit`/`NotebookEdit` em `tools:`** — o capability scoping vira teste, que é exatamente o argumento da PR. O `paths:` do `validate.yml` ganha `plugins/bb/agents/**` e `.github/scripts/**`, senão um PR só-de-agente não dispara o Validate. |
| `model:`                           | Omitido nos dois → herda o modelo da sessão. Não fixar `sonnet`: a qualidade do achado e do veredito é justamente o que não se quer barateando por default.                                                                     |
| `description:`                     | PT-BR (regra híbrida: frontmatter description é user-facing), e **estreita de propósito** — diz que é papel interno do pipeline de review, despachado pelas skills, e aponta `/bb:review` pra quem quer revisar. Contramedida direta pro custo (b): agente de plugin fica visível globalmente com a description sempre em contexto. |
| `plugin.json`                      | Nada a declarar — `agents/` é auto-descoberto (confirmado nos plugins oficiais: `pr-review-toolkit` publica 6 agentes com `plugin.json` sem campo `agents`). Só o bump de versão.                                              |
| versão                             | `2.2.0` → `2.3.0` no `plugin.json` e no `metadata.version` de cada SKILL.md tocado (`review`; `ship` só se acabar tocado).                                                                                                     |
| `/bb:ship`                         | Sem edição esperada — ship empresta `fronts.md`/`verify.md`, então herda os agentes pela convenção de empréstimo. Confirmar na implementação; se `ship/SKILL.md:54` ("review agents in one message") ficar ambíguo, ajustar a linha. |

## design

**Seam entre agente e caller.** O agente é dono da metade que não muda entre
frentes; o caller monta a metade que muda.

```
bb-finder (system prompt)          | caller (scope block + prompt)
-----------------------------------|-----------------------------------
read-only, nunca edita             | diff range resolvido (<merge_base>...HEAD)
todo candidato com consequência    | arquivos mudados + parágrafo do que mudou
  nomeável passa (não se censurar) | CODE_REVIEW_GUIDE.md / brief quando há
devolve exatamente a Finding shape | criteria path (review-/quality-checklist)
  que o caller passou              | UM angle/lens set + o cap dele
diz quantos cortou ao bater o cap  | a Finding shape do front

bb-verifier (system prompt)        | caller (scope block + prompt)
-----------------------------------|-----------------------------------
rubrica CONFIRMED/PLAUSIBLE/REFUTED| os candidatos daquele local, [0], [1], …
viés: PLAUSIBLE é o default        | addendum por frente (citação em rules/
REFUTED só se construtível do      |   contract, WCAG + recálculo de contraste
  código (cita a linha que prova)  |   em a11y)
um veredito por índice, julgado    | o scope block
  independentemente, com evidência |
```

**Sem shape passada** (caller esqueceu, ou é um uso novo): o finder devolve
`file:line | summary | failure_scenario` — o mínimo que o `group_candidates.py`
consegue agrupar.

**Limite conhecido e aceito:** com Bash na lista, um diff que contenha texto
instruindo o modelo ("ignore o anterior, edite X") não é barrado por capability —
`Edit`/`Write` somem, `sed -i` não. O ângulo `instruction-integrity` continua sendo
a defesa de leitura; o scoping é redução de superfície, não isolamento.

## behavior

**Happy path** (`/bb:review`, step 3, depth com fan-out):

1. O probe resolve o diff range e as frentes disponíveis (nada muda aqui).
2. O caller monta o scope block e dispara todos os finders **numa mensagem**, cada
   um com `subagent_type: "bb-finder"`, um angle/lens set e o cap do seu front.
3. Cada finder lê o diff (`git diff <merge_base>...HEAD` via Bash) e os arquivos
   com a função envolvente aberta; devolve candidatos na Finding shape do front.
   Nenhum finder pode chamar Edit/Write — não estão na lista de tools.
4. Barreira: o main context junta tudo e roda `group_candidates.py`.
5. Um `bb-verifier` por local, com os candidatos indexados + o addendum da frente
   quando é `rules`/`contract`/`a11y`. Rubrica vem do prompt do agente.
6. Dedupe, rank, cap, relatório — inalterado. A stats line segue batendo.

**Edge cases**

| WHEN                                                          | THEN                                                                                                                                     |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `bb-finder` não resolve como `subagent_type` (plugin parcial, run aninhado) | o fan-out cai no agente genérico com o contrato inline; a linha relocada no `fronts.md` segue nomeando o invariante read-only. Sem crash, sem regressão silenciosa. |
| não há Agent tool nenhum no host                              | item 6 do `fronts.md` como hoje — trabalha todos os ângulos no main context e **diz no relatório** que foi single-pass sem verificação independente |
| o caller não passa Finding shape                              | o finder devolve `file:line \| summary \| failure_scenario`                                                                              |
| diff tiny (≲2 arquivos / ≲100 linhas)                         | nenhum agente é spawnado (a depth table já manda inline) — os agentes existem e não são usados; nada muda                                 |
| candidato de `rules` / `contract` / `a11y`                    | o caller anexa o addendum de verificação por citação; o verifier aplica os 3 estados do prompt sobre o critério de citação, não sobre crash |
| um finder morre                                               | comportamento atual mantido: o front reporta com os ângulos que voltaram e nomeia o que falta                                            |
| um verifier morre ou omite um índice                          | comportamento atual mantido: candidato fica **sem veredito**, com linha própria, nunca promovido                                        |
| `/bb:ship` roda o mesmo pass                                  | usa os mesmos dois agentes sem edição em `ship/` — herda via empréstimo do `fronts.md`                                                   |
| alguém adiciona/edita um agente do bb com `Write` em `tools:` | o Validate falha com a linha do arquivo e o tool proibido                                                                                |
| um PR toca só `plugins/bb/agents/**`                          | o Validate dispara (paths filter estendido) em vez de passar verde por não ter rodado                                                    |
| o diff carrega texto que instrui o modelo (injection)         | Edit/Write barrados por capability; escrita via Bash continua alcançável — limite declarado, não coberto                                 |
| `BB_UNATTENDED` setado                                        | nada muda — o caminho já é report-only; os agentes só reforçam o read-only que a routine já assume                                       |

## tasks

- [ ] **Slice 1 — os dois agentes.** `plugins/bb/agents/bb-finder.md` e
      `bb-verifier.md`: frontmatter (`name`, `description` PT-BR estreita,
      `tools: ["Read", "Grep", "Glob", "Bash"]`, sem `model`) + system prompt em
      inglês com o contrato invariante de cada papel migrado. Entrega os
      comportamentos: happy path 3/5, "sem Finding shape", "injection" (limite
      declarado no prompt), dispatch estreito.
- [ ] **Slice 2 — o engine passa a despachá-los.** `fronts.md` (item 1 nomeia
      `subagent_type: bb-finder`; item 5 defere o contrato ao agente),
      `review/SKILL.md:91`, `verify.md §2` (defere a rubrica, mantém o addendum por
      frente), `front-correctness.md` (defere o parágrafo da consequência nomeável).
      Entrega: happy path 2/5, fallback sem `bb-finder`, candidatos de
      rules/contract/a11y, `/bb:ship` herdando.
- [ ] **Slice 3 — o CI guarda o scoping.** `validate-frontmatter.ts` caminha em
      `agents/*.md`, exige `name`+`description` e falha em `Write`/`Edit`/
      `NotebookEdit` no `tools:` de agente do bb; `validate.yml` ganha
      `plugins/bb/agents/**` e `.github/scripts/**` no `paths:`. Entrega: as duas
      linhas de CI da tabela de edges.
- [ ] **Slice 4 — docs e versão** (sem comportamento próprio, housekeeping):
      `.claude/CLAUDE.md` (árvore ganha `agents/`, uma linha de convenção ao lado
      da de scripts compartilhados), README se listar a estrutura, bump
      `2.2.0` → `2.3.0` no `plugin.json` e nos SKILL.md tocados.

Ordem: 1 → 2 são o par que precisa landar junto (o engine referencia o agente).
3 e 4 são independentes e podem vir em qualquer ordem depois.

PR sugerida: `feat(review): bb-finder e bb-verifier com capability scoping`.

## out of scope

- **Os 5 subagentes de discovery do `/bb:review-setup`** — prompts fixos, skill que
  roda raro; não paga 5 nomes globais. _revisit_ se o review-setup virar rotina.
- **Reusar o `Explore` nativo** — a description dele diz que localiza código e não
  revisa nem audita; brigaria com a tarefa.
- **O revisor independente do `/bb:spec`** (Agent tool, contexto fresco) — mesma
  forma read-only, mas sem Finding shape e sem pipeline de verify; não é o mesmo
  papel. _revisit_ se ele passar a devolver achados estruturados.
- **Um agente por frente** — as diferenças entre frentes são conteúdo de prompt que
  o caller já monta.
- Apagar a branch local `claude/review-fronts` (1 commit atrás do merge da PR #3) —
  limpeza, não faz parte desta task.

## still open

- Nada load-bearing. O único ponto a confirmar na implementação é se
  `ship/SKILL.md:54` precisa de ajuste de redação — decidido por default: só mexer
  se a linha ficar ambígua depois do slice 2.

## validação

Regra do usuário: **nada roda local**. Esta mudança é validada subindo a branch pra
PR e acompanhando o CI (`gh pr checks --watch`) — o `paths:` do `validate.yml`
dispara porque o slice 2 toca `skills/**`, e `fmt:check` (oxfmt) cobre a formatação
dos `.md` novos. O slice 3 é o que precisa do CI verde pra provar que a assertion de
write-tool não dá falso positivo nos outros agentes.
