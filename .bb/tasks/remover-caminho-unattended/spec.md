---
status: in-progress
created: 2026-08-11
slug: remover-caminho-unattended
---

# remover o caminho unattended do bb

Tirar do plugin `bb` o caminho não-supervisionado inteiro: a env var `BB_UNATTENDED`, o
addendum que ela injeta, o guia de Cloud Routines, o scaffold de routine, as duas rotinas
próprias do `maintain-repo`, e todo ramo condicional "unattended" espalhado pelas skills.
Depois disso o bundle tem um modo só — supervisionado, com um humano na sessão.

O caminho **nunca rodou**. Não existe Cloud Routine configurada do lado do
GitHub/Anthropic, nem nunca existiu. Isso muda o que está sendo deletado: não é código que
funciona, é design especulativo. Cada afirmação em `hooks/unattended-context.md`, no watch
unattended do `land-pr.md` e nos caps de retry do implement é comportamento que nenhuma run
jamais exerceu — escrito, revisado, versionado, nunca verificado por nada.

O que ele cobra em troca é caro e visível: o debate de onde o blocker aparece (descrição da
PR vs `## open` numa branch pushada), o ship rodando sobre uma árvore incompleta, uma régua
paralela no `build-mode.md`, uma seção de provisionamento de segurança no `routines.md`, e
uma frase "Unattended:" em quase todo passo do trio.

## A superfície medida

`rg -i 'BB_UNATTENDED|unattended|routine|AFK'` em `plugins/bb/` casa **142 linhas em 22
arquivos**. Elas se partem em dois grupos desiguais:

- **4 arquivos morrem inteiros** — `hooks/unattended-context.md` (5), `references/routines.md`
  (25), `references/scripts/scaffold_routine.py` (13) e
  `skills/maintain-repo/references/routines-setup.md` (22). São 65 das 142.
- **18 arquivos são editados** — as 77 restantes. A contagem por arquivo está em cada slice;
  ela é o inventário que o build consome, porque número de linha muda durante a edição e
  contagem não.

Fora de `plugins/bb/` sobram `README.md` (2) e `.claude/CLAUDE.md` (8). `CHANGELOG.md` e os
briefs antigos em `.bb/tasks/` também casam, e ficam: são histórico.

**O `-i` não é detalhe.** `rg` é case-sensitive por default, e boa parte das ocorrências é
capitalizada — `## Unattended`, `**Unattended:**`, `Cloud Routine`, `Routine A`. Uma
varredura sem `-i` volta verde sobre um plugin ainda sujo. Todo `verifica:` deste brief usa
`-i`, e o critério de sucesso também.

Sucesso: `rg -i 'BB_UNATTENDED|unattended|routine|AFK'` volta zero em `plugins/bb/`,
`README.md` e `.claude/CLAUDE.md`, e nenhuma skill referencia arquivo deletado.

## decisions

- **Reuse:** nada novo é escrito. A remoção é subtrativa; onde sobra frase incompleta, ela é
  encurtada, não substituída por prosa nova. Segue a régua do `CLAUDE.md` do usuário:
  remover > negar — em lugar nenhum entra "não existe modo unattended".
- **A garantia never-merge por capability scoping morre junto.** Sem routine não há token
  pra escopar. O never-merge que fica é o da skill ("ship nunca mergeia, nunca aprova, nunca
  força push") mais a branch protection do repo, que é fato do repo e não do bb. Toda
  cláusula "enforced by capability scoping on the unattended path" vira só a linha dura.
- **`hooks/enter_worktree.py` fica, e são três pontos, não dois.** Ele é isolamento de
  worktree pra run local e task paralela — a própria docstring diz que uma routine *não*
  precisa dele. Mas essa nota é uma comparação com uma coisa que deixa de existir: o
  parágrafo `NOTE:` inteiro sai (ele também aponta pra linha da tabela que a slice 1
  deleta), e `unattended` sai de mais dois comentários. Nada de lógica muda.
- **O fato `claude -p` / Agent SDK sobrevive no `build-slices-workflow.md`.** O bullet hoje
  se chama "Out-of-allowlist commands don't prompt **in a routine**", mas a condição que a
  própria frase seguinte declara é `claude -p` e o Agent SDK — que é como os slice agents
  rodam mesmo numa sessão supervisionada. Some a moldura de routine do título do bullet; o
  fato e o estágio zero que ele justifica ficam de pé.
- **`hooks/scheduling-decision.md` fica, sem a linha Cloud Routine — e sem uma coluna.**
  A tabela segue útil pros cinco mecanismos restantes (`/loop`, Desktop task, Channels,
  `/goal`, Monitor). Saem: a linha, os dois bullets de "How to pick" que apontam pra ela, e
  a frase de abertura que promete resolver o job AFK de madrugada. Some também a coluna
  **`Survives laptop closed?`**, que sem a Cloud Routine tem `No` nas cinco linhas — coluna
  de valor único não informa nada.
- **A inconsistência do passo 4 do implement fecha por deleção, não por texto novo.** O
  trecho que manda encadear `/bb:ship` num build incompleto está inteiro dentro do prefixo
  "**Unattended:**". Deletado o prefixo, some a contradição com o passo 4 do delegate, e a
  regra que sobra já é a certa — passo 8, "not clean → don't offer ship".
- **O estágio zero e o modo workflow ficam.** Nenhum dos dois depende de routine: o baseline
  verde é independente, e a allowlist é questão de SDK (acima).
- **CHANGELOG e briefs antigos em `.bb/tasks/` não são reescritos** — são histórico, e ficam
  fora do escopo de toda varredura. Entra só uma entrada nova no CHANGELOG.
- **`references/scripts/` some junto com `scaffold_routine.py`** — é o único arquivo lá.
- **Versão:** `plugin.json` vai a `2.8.0` e as **9 skills tocadas** levam bump de
  `metadata.version` (delegate, implement, ship, review, review-setup, discover, spec,
  maintain-repo — e nenhuma outra). Remover comportamento documentado é mudança de
  comportamento, inclusive quando é só uma linha de edge case.
- **O gate roda só no CI.** `bun run fmt:check`, `validate-frontmatter.ts` e `lint_spec.py`
  rodam na PR. O `verifica:` de cada slice é `rg -i -c` no próprio escopo voltando zero —
  busca, não build.

## behavior

1. Sessão qualquer num repo com o plugin ligado: o `inject_operating_context.py` lê
   `operating-context.md` e injeta, sem ramo condicional. `BB_UNATTENDED=1` no ambiente não
   produz efeito nenhum — a var não é mais lida.
2. `enter_worktree.py` segue criando worktree isolada pra run local/autônoma e recusando
   branch protegida; nenhum comentário dele cita routine.
3. `/bb:delegate <slug>`: resolve o brief, flipa `in-progress`, pergunta o modo de build
   (sempre), constrói, roda o ship, landa, flipa `done`. Nenhum passo e nenhuma linha de
   edge case tem variante unattended.
4. `/bb:implement` invocado direto: pergunta o modo de build, e com gate quebrando de forma
   irrecuperável commita o que está verde, reporta done/skipped/blocked e **não oferece
   ship**.
5. `/bb:ship`: o Step 1 sempre resolve o destino por sinal ou pergunta. Não existe destino
   fixo, nem draft PR automática, nem cap de rodada de comentário, nem watch AFK.
6. Toda skill com próximo passo natural termina no handoff gate. Não sobra exceção que pule
   a pergunta e tome a lean documentada sozinha.
7. `/bb:maintain-repo`: roda supervisionado de ponta a ponta — fases 1 a 4, digest no Slack
   pelas MCP tools da sessão, merge na mão do humano. Sem pré-requisito de provisionamento.
8. Quem procura como rodar de madrugada abre o `scheduling-decision.md`, encontra cinco
   mecanismos comparados, e nenhum sobrevive ao laptop fechado.
9. `review`, `review-setup`, `discover` e `spec` perdem as menções que tinham; o
   comportamento supervisionado delas não muda em nada.
10. README, `.claude/CLAUDE.md` e a `description` do `plugin.json` descrevem o bundle sem o
    caminho; `2.8.0`, os bumps de skill e uma entrada de CHANGELOG registram a remoção.
11. `rg -i` do conjunto volta zero em `plugins/`, `README.md` e `.claude/CLAUDE.md`, e
    nenhuma referência aponta pra arquivo deletado.

| WHEN                                                | THEN                                                                             |
| --------------------------------------------------- | ---------------------------------------------------------------------------------- |
| `BB_UNATTENDED=1` setado depois da remoção          | nada acontece; a sessão roda supervisionada normal                               |
| a varredura roda sem `-i`                           | passa verde sobre plugin sujo: `Unattended:` e `Cloud Routine` escapam           |
| `unattended-context.md` some mas o `if` fica        | o hook injeta bloco vazio; por isso o `if` e o helper saem no mesmo commit       |
| alguma skill ainda aponta pra arquivo deletado      | o CI não pega; quem pega é a varredura da slice 7                                |
| a coluna "Survives laptop closed?" fica só com `No` | some a coluna; valor único não informa                                           |
| o bullet de allowlist perde a moldura de routine    | o fato `claude -p` / SDK fica; o estágio zero segue justificado                  |
| o `NOTE:` do `enter_worktree.py` compara com routine | o parágrafo sai inteiro; a lógica do arquivo não muda                            |
| passo 4 do implement, gate irrecuperável            | o parágrafo unattended some; a regra do passo 8 já cobre, sem texto novo         |
| `plugin.json` perde a cláusula de capability scoping | never-merge segue afirmado como linha dura em ship e delegate                    |
| `maintain-repo` perde as duas rotinas próprias      | sobra o supervisionado inteiro; some o pré-requisito de provisionar antes        |
| CHANGELOG e `.bb/tasks/` antigos citam unattended   | ficam; estão fora do escopo de toda varredura                                    |
| CI não dispara em PR que só toca `references/`      | esta PR toca 9 `SKILL.md`, então dispara; o gatilho não muda                     |
| sobra frase pela metade depois de tirar a cláusula  | encurta a frase; não entra prosa nova explicando a ausência                      |

## tasks

- [ ] **1. hooks** — deleta `unattended-context.md` (5); tira o `if`, o helper e a constante
      do `inject_operating_context.py` (7); a cláusula de capability scoping do
      `operating-context.md` (1); o parágrafo `NOTE:` e dois comentários do
      `enter_worktree.py` (3); a linha Cloud Routine, a coluna "Survives laptop closed?", os
      dois bullets AFK e a frase de abertura do `scheduling-decision.md` (5)
      → behaviors 1, 2, 8 · dep: — · verifica: `rg -i -c` em `hooks/` volta zero
- [ ] **2. references de plugin-root** — deleta `routines.md` (25) e `scripts/` inteiro (13);
      no `build-mode.md` (6) a seção `## Unattended`, a frase "won't survive an unattended
      run either" e a linha do relatório; no `build-slices-workflow.md` (4) a moldura de
      routine no bullet de allowlist, o ponteiro do topo, o cap de retry e a branch; no
      `handoff-gate.md` (3) a regra "unattended runs never gate" e a cláusula do auto-chain
      → behaviors 4, 6 · dep: — · verifica: `rg -i -c` em `references/` volta zero
- [ ] **3. o trio** — `delegate` (15: description, abertura, passos 1 a 6, três linhas de edge
      case, fecho), `implement` (7: description, abertura, passos 3/4/6/7/8 — o 4 fecha por
      deleção e o 7 aponta pro `routines.md`), `ship` (2: parágrafo do Step 1 e a linha de
      bundled resource) e `land-pr.md` (6: `--draft`, thread sem pausa, cap de rodada, "not
      an AFK agent", o ponteiro de Channel/routine e o watch unattended)
      → behaviors 3, 4, 5 · dep: 1, 2 · verifica: `rg -i -c` nas três skills volta zero
- [ ] **4. skills periféricas** — `review` (3: fan-out, curadoria, linha de edge case),
      `mode-external-pr.md` (1: parágrafo report-only), `review-setup` (1) e `discover` (1),
      linha de edge case cada; `spec` (3: a menção de reload, o "mesmo verbo da routine" no
      Delegar e o ponteiro pro guia no "Encerrar aqui")
      → behavior 9 · dep: — · verifica: `rg -i -c` nas cinco skills volta zero
- [ ] **5. maintain-repo** — deleta `references/routines-setup.md` (22); no `SKILL.md` (8) a
      moldura "roda de dois jeitos", o pré-requisito de provisionar, o bullet never-merge por
      capability, a entrega via connector Slack, a entrada de bundled resource e a seção
      `### Safety model`
      → behavior 7 · dep: — · verifica: `rg -i -c` na skill volta zero
- [ ] **6. docs do repo e versão** — `README.md` (2: linha do `/bb:delegate` na tabela e a
      seção "rodar sem supervisão"); `.claude/CLAUDE.md` (8: a claim do topo, quatro linhas
      da árvore — inclusive o comentário do `scheduling-decision.md`, que fica — e a nota de
      hooks); `description` do `plugin.json` e `2.8.0`; `metadata.version` das 9 skills;
      entrada no CHANGELOG
      → behavior 10 · dep: 3, 4, 5 · verifica: `rg -i -c` em `README.md` e `.claude/` zero
- [ ] **7. varredura** — `rg -i` do conjunto em `plugins/`, `README.md` e `.claude/` volta
      zero, e `rg -i 'routines(-setup)?\.md|scaffold_routine|unattended-context'` no repo
      inteiro só casa em `CHANGELOG.md` e `.bb/`; PR verde
      → behavior 11 · dep: 1-6 · verifica: CI

## out of scope

- **Guard de CI contra regressão.** Um job que falha se `BB_UNATTENDED` reaparecer é peso
  permanente pra uma remoção única.
- **Reescrever CHANGELOG e briefs antigos.** Histórico fica.
- **Mexer no estágio zero, no modo workflow ou na lógica do `enter_worktree.py`.**
- **Reavaliar se `/bb:delegate` ainda se justifica como verbo.** Ele sobrevive: é o "sim" ao
  gate do implement dado de antemão. Só a description e a abertura são reescritas.
- **A nota de convenções não sobreviver a um resume** — achado real do build-via-workflow,
  brief próprio.

## open

Nada aberto.
