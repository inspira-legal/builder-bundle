---
status: done
created: 2026-08-04
slug: review-agents
---

# bb-finder e bb-verifier — capability scoping pro fan-out do review

Dois agentes definidos no plugin — `plugins/bb/agents/bb-finder.md` e
`plugins/bb/agents/bb-verifier.md` — nomeados por **papel no pipeline**, não por frente. O
fan-out do `/bb:review` (e, por empréstimo, do `/bb:ship`) passa a despachá-los via
`subagent_type`, e o `tools:` do frontmatter vira quem garante que finder e verifier não
escrevem. Junto: o contrato invariante de cada papel migra pro system prompt do agente, e o
CI aprende a validar `agents/*.md`.

O read-only dos finders hoje é garantido por prosa (`fronts.md:77` — "read-only — they
report, never edit"), mas o `.claude/CLAUDE.md` do repo manda **"enforce irreversible
hazards with capability scoping, not prose"**. É o mesmo raciocínio já aplicado duas vezes
no repo: never-merge e outward-posting saíram da prosa pro capability scoping da routine.

O dano concreto: um finder que decide consertar o que achou quebra o single-writer com até
5 agentes escrevendo em paralelo na mesma working tree — corrupção difícil de atribuir,
porque o relatório não registra edits que ninguém pediu.

Sucesso: o invariante read-only está no frontmatter e no CI, e nenhuma skill precisa
repeti-lo pra que valha.

## O seam entre agente e caller

O agente é dono da metade que não muda entre frentes; o caller monta a metade que muda.

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

**Sem Finding shape passada** (caller esqueceu, ou é um uso novo): o finder devolve
`file:line | summary | failure_scenario` — o mínimo que o `group_candidates.py` consegue
agrupar.

**Limite conhecido e aceito:** com Bash na lista, um diff que contenha texto instruindo o
modelo ("ignore o anterior, edite X") não é barrado por capability — `Edit`/`Write` somem,
`sed -i` não. O ângulo `instruction-integrity` continua sendo a defesa de leitura; o scoping
é redução de superfície, não isolamento.

## Decisões

- **Dois agentes, por papel** — `bb-finder` e `bb-verifier`. O que difere entre frentes é
  conteúdo de prompt que o caller já monta (angle set, criteria path, scope block, Finding
  shape); um agente por frente seriam 7 nomes globais guardando a mesma metade invariante.
- **`tools: Read, Grep, Glob, Bash` nos dois**, com o custo declarado: `tools:` é por nome
  de ferramenta, então `sed -i` e `>` continuam alcançáveis via Bash. O scoping tira o que o
  modelo naturalmente alcança (Edit/Write); não é hermético. Bash é o que mantém
  `git diff <range>` e `gh pr diff` (mode-external-pr) funcionando sem inflar o scope block.
- **O agente é dono do contrato.** A rubrica CONFIRMED/PLAUSIBLE/REFUTED (+ viés de
  PLAUSIBLE, + REFUTED só quando construtível do código) mora no prompt do `bb-verifier`; o
  contrato do finder (consequência nomeável, não se auto-censurar) mora no `bb-finder`.
  `verify.md §2`, `fronts.md` item 5 e o parágrafo de consequência do `front-correctness.md`
  deferem numa linha cada.
- **O que não migra:** a verificação por citação de `rules`/`contract`/`a11y` fica na
  referência e o caller anexa ao prompt do verifier — é conteúdo por frente, não invariante
  de papel. Idem campos da Finding shape, angle sets e caps.
- **Fallback é realocar, não deletar** — `fronts.md:77` e `review/SKILL.md:91` viram "os
  finders vão como `subagent_type: bb-finder` — read-only por capability", uma linha cada. O
  invariante segue nomeado uma vez, mas quem garante é o frontmatter; o item 6 do
  `fronts.md` continua cobrindo o host sem fan-out.
- **O CI guarda o scoping** — `validate-frontmatter.ts` caminha em `agents/*.md` (name +
  description obrigatórios) e **falha se um agente do bb listar `Write`/`Edit`/`NotebookEdit`
  em `tools:`**, que é exatamente o argumento da PR virado teste. O `paths:` do
  `validate.yml` ganha `plugins/bb/agents/**` e `.github/scripts/**`, senão um PR
  só-de-agente não dispara o Validate.
- **`model:` omitido nos dois** → herda o modelo da sessão. A qualidade do achado e do
  veredito é justamente o que não se quer barateando por default.
- **`description:` em PT-BR e estreita de propósito** — diz que é papel interno do pipeline
  de review, despachado pelas skills, e aponta `/bb:review` pra quem quer revisar. Agente de
  plugin fica visível globalmente com a description sempre em contexto.
- **`plugin.json` não declara nada** — `agents/` é auto-descoberto (confirmado no
  `pr-review-toolkit` oficial: 6 agentes, `plugin.json` sem campo `agents`). Só o bump.
- **Versão** — `2.2.0` → `2.3.0` no `plugin.json` e no `metadata.version` de cada SKILL.md
  tocado (`review`; `ship` só se acabar tocado).
- **`/bb:ship` sem edição esperada** — empresta `fronts.md`/`verify.md`, então herda os
  agentes pela convenção de empréstimo. Ajustar `ship/SKILL.md:54` só se a linha ficar
  ambígua depois do slice 2.

## Comportamento

Happy path (`/bb:review`, step 3, depth com fan-out):

1. O probe resolve o diff range e as frentes disponíveis — nada muda aqui.
2. O caller monta o scope block e dispara todos os finders **numa mensagem**, cada um com
   `subagent_type: "bb-finder"`, um angle/lens set e o cap do seu front.
3. Cada finder lê o diff (`git diff <merge_base>...HEAD` via Bash) e os arquivos com a
   função envolvente aberta; devolve candidatos na Finding shape do front. Nenhum finder
   pode chamar Edit/Write — não estão na lista de tools.
4. Barreira: o main context junta tudo e roda `group_candidates.py`.
5. Um `bb-verifier` por local, com os candidatos indexados + o addendum da frente quando é
   `rules`/`contract`/`a11y`. A rubrica vem do prompt do agente.
6. Dedupe, rank, cap, relatório — inalterado. A stats line segue batendo.

| WHEN                                         | THEN                                                                                     |
| -------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `bb-finder` não resolve como `subagent_type` | cai no agente genérico com o contrato inline; sem crash nem regressão silenciosa         |
| não há Agent tool nenhum no host             | item 6 do `fronts.md` — tudo no main context, e o relatório diz que foi single-pass      |
| o caller não passa Finding shape             | o finder devolve `file:line \| summary \| failure_scenario`                              |
| diff tiny (≲2 arquivos / ≲100 linhas)        | nenhum agente é spawnado — a depth table já manda inline                                 |
| candidato de `rules` / `contract` / `a11y`   | o caller anexa o addendum; o verifier aplica os 3 estados sobre citação, não sobre crash |
| um finder morre                              | o front reporta com os ângulos que voltaram e nomeia o que falta                         |
| um verifier morre ou omite um índice         | o candidato fica sem veredito, com linha própria, nunca promovido                        |
| `/bb:ship` roda o mesmo pass                 | usa os mesmos dois agentes sem edição em `ship/`                                         |
| alguém adiciona um agente do bb com `Write`  | o Validate falha nomeando o arquivo e o tool proibido                                    |
| um PR toca só `plugins/bb/agents/**`         | o Validate dispara — o paths filter foi estendido                                        |
| o diff carrega texto que instrui o modelo    | Edit/Write barrados; escrita via Bash segue alcançável — limite declarado                |
| `BB_UNATTENDED` setado                       | nada muda — o caminho já é report-only                                                   |

## Tarefas

- [x] **1. Os dois agentes** — `bb-finder.md` e `bb-verifier.md`: frontmatter (`name`,
      `description` PT-BR estreita, `tools: ["Read", "Grep", "Glob", "Bash"]`, sem
      `model`) e system prompt em inglês com o contrato invariante de cada papel
      → behaviors 3, 5 e as linhas de Finding shape e injection · depende: — · verifica: CI
- [x] **2. O engine despacha os agentes** — `fronts.md` (item 1 nomeia o `subagent_type`,
      item 5 defere o contrato), `review/SKILL.md:91`, `verify.md §2` (defere a rubrica,
      mantém o addendum por frente), `front-correctness.md`
      → behaviors 2, 5 e as linhas de fallback e de ship · depende: 1 · verifica: CI
- [x] **3. O CI guarda o scoping** — `validate-frontmatter.ts` caminha em `agents/*.md`,
      exige `name`+`description` e falha em `Write`/`Edit`/`NotebookEdit`; `validate.yml`
      ganha `plugins/bb/agents/**` e `.github/scripts/**` no `paths:`
      → as duas linhas de CI da tabela · depende: — · verifica: CI verde (prova que a assertion
      não dá falso positivo nos outros agentes)
- [x] **4. Docs e versão** — `.claude/CLAUDE.md` (árvore ganha `agents/`, uma linha de
      convenção), README se listar a estrutura, bump `2.2.0` → `2.3.0`
      → nenhum comportamento próprio · depende: 1-3 · verifica: CI

PR sugerida: `feat(review): bb-finder e bb-verifier com capability scoping`.

## Fora de escopo

- **Os 5 subagentes de discovery do `/bb:review-setup`** — prompts fixos, skill que roda
  raro; não paga 5 nomes globais. _revisit_ se o review-setup virar rotina.
- **Reusar o `Explore` nativo** — a description dele diz que localiza código e não revisa
  nem audita; brigaria com a tarefa.
- **O revisor independente do `/bb:spec`** (Agent tool, contexto fresco) — mesma forma
  read-only, mas sem Finding shape e sem pipeline de verify; não é o mesmo papel. _revisit_
  se ele passar a devolver achados estruturados.
- **Um agente por frente** — as diferenças entre frentes são conteúdo de prompt que o caller
  já monta.
- Apagar a branch local `claude/review-fronts` — limpeza, não faz parte desta task.

## Em aberto

- Nada load-bearing. O único ponto a confirmar na implementação é se `ship/SKILL.md:54`
  precisa de ajuste de redação — decidido por default: só mexer se a linha ficar ambígua
  depois do slice 2.
