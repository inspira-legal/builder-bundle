---
status: in-progress
created: 2026-08-06
slug: build-via-workflow
---

# construir as slices via dynamic workflow

Um caminho novo no `/bb:implement` e no `/bb:delegate`: em vez de construir todas as slices
no contexto principal, despachar um dynamic workflow que roda um agente por slice. O `dep:`
e o `verifica:` que cada slice já carrega são o DAG que esse orquestrador consome sem
reinterpretar prosa.

O problema que ele resolve não é velocidade. Um brief de oito slices construído num
contexto só bate compactação no meio do build, e é exatamente ali que o implement degrada:
esquece o `## behavior`, deriva das `## decisions`. Um agente por slice começa com
orçamento limpo e carrega só o brief mais a sua fatia. A perda de contexto tácito entre
slices é paga por uma nota de convenções que atravessa os estágios — compactação também é
lossy, com a diferença de que ela é automática e a nota é projetada.

Sucesso: um brief grande roda até o fim sem compactar, e o que a slice 3 construiu usa os
nomes que a slice 1 estabeleceu.

## O que a plataforma decide por nós

**Sem input no meio da run.** Só prompt de permissão pausa um workflow; a doc manda rodar
cada estágio como um workflow separado quando se quer sign-off entre eles. Isso tira a
válvula de segurança conversacional do implement de dentro da run — o agente de slice só
consegue _retornar_ "o brief está subespecificado", e quem decide é o script.

**O script não tem shell nem filesystem.** Só agentes leem, escrevem e rodam comando. Todo
gate, todo commit, todo `verifica:` acontece dentro de um agente; o script só coordena e lê
retornos estruturados.

**Comando fora da allowlist não pede permissão numa routine.** Em `claude -p` e no SDK não
há a quem perguntar, então a chamada segue as regras configuradas sem confirmação — na
prática, falha. Um gate que a routine não tem permissão de rodar não vira pergunta, vira
slice vermelha.

## Sequencial, e por quê

As slices rodam num `for` com `await`, não em `pipeline()`. O `pipeline` roda cada item por
todos os estágios de forma independente e concorrente — primitivo errado aqui, porque as
slices compartilham a working tree e o `dep:` existe justamente para dizer que a 2 se apoia
no que a 1 criou. Paralelizar daria conflito de árvore, ou exigiria worktree isolada e um
merge que o script não tem como executar.

O único ponto genuinamente paralelo é o estágio zero, read-only por natureza. Ali
`parallel()` é barreira legítima — nada começa antes de todos os veredictos chegarem.

## decisions

- **A escolha é uma pergunta, em toda run** — `/bb:implement` e `/bb:delegate`
  supervisionados abrem perguntando entre construir via workflow ou em contexto, qualquer
  que seja o tamanho do brief. Unattended não pergunta: sempre workflow.
- **O script é gerado por run** — a skill autora o JS e passa em `script`; o runtime
  persiste no diretório da sessão e devolve o path. Não vai pra `workflows/` do plugin,
  então não vira comando `/bb:build-slices` nem aparece no autocomplete.
- **A forma do script é um reference, não um executável** — `build-slices-workflow.md` fixa
  o contrato que o script gerado tem que cumprir, e a skill confere antes de invocar.
- **`for` sequencial, `parallel()` só no estágio zero.**
- **O estágio zero roda o gate inteiro uma vez** — não só localiza os comandos pela cadeia
  de autoridade do implement: executa todos. Prova a permissão e estabelece a linha de base
  verde, então árvore já vermelha vira blocker antes da slice 1 em vez de slice falha.
- **Quem constrói a slice roda o gate** — o mesmo agente constrói, cumpre o `verifica:`,
  roda o gate, conserta o que quebrou (cap de 3 retries só em assinatura de flake, como o
  implement já define) e commita. Sem agente de gate dedicado: quem quebrou tem o contexto
  pra consertar, e é um agente a menos por slice.
- **`verifica:` não-executável vira auto-inspeção** — `leitura`: o agente confere o que
  produziu contra os behaviors que a slice cita e devolve evidência curta. `CI`: fora do
  alcance da run, volta pendente pro ship. Nenhum `verifica:` é silenciosamente pulado.
- **A nota de convenções acumula, com teto** — a slice N recebe as convenções de todas as
  anteriores, não só da imediatamente anterior. Passando de ~1500 caracteres, o próprio
  agente condensa as mais antigas e devolve a versão que a próxima recebe; sem agente de
  resumo dedicado.
- **O commit é o checkpoint** — cada agente commita só os arquivos que tocou, com o `- [x]`
  da sua slice no mesmo commit. O resume do workflow é só na mesma sessão e re-roda tudo
  que começou depois do primeiro agente não-terminado; os commits sobrevivem a qualquer
  coisa, então é neles que o progresso mora.
- **Idempotência pelo checkbox** — o agente relê o `## tasks` em disco antes de construir e
  retorna na hora se a sua slice já está ticada. Re-rodar um brief meio construído não
  refaz o que já landou.
- **Slice vermelha não commita e não reverte** — a árvore fica como está, pro diagnóstico.
  Quem trata é o caller, pelo contrato que já existe: o implement para no passo 7, o
  delegate flipa `blocked` e não segue pro ship.
- **Reuse note morta para a run** — é a válvula de segurança do implement disparando pelo
  preço mais barato possível. `moved` segue e entra na nota de convenções; `gone` para.
- **O delegate não pergunta duas vezes** — ele já suprime o passo 8 do implement; passa a
  suprimir também a pergunta de modo, e repassa a decisão que tomou.
- **`routines.md` perde a proibição de fan-out** — a regra "single-agent only until you've
  measured cost" sai e vira a descrição do modo workflow como default da routine, com a
  allowlist dos comandos de gate na lista de provisionamento.
- **Effort baixo no estágio zero, modelo herdado nas slices** — os agentes de pre-flight são
  lookup read-only; os de slice constroem e ficam no modelo da sessão.
- **Versão** — `plugin.json` `2.6.0` → `2.7.0`; `implement` `2.1.0` → `2.2.0`; `delegate`
  `2.2.0` → `2.3.0`.

## behavior

1. Supervisionado, `/bb:implement` e `/bb:delegate` abrem perguntando entre workflow e
   contexto; unattended não pergunta e vai de workflow.
2. Escolhido o workflow, a skill autora o script conforme o reference e invoca `Workflow`
   passando em `args` o slug, o caminho do brief e a lista das slices ainda não ticadas,
   cada uma com o seu `dep:` e o seu `verifica:`.
3. O estágio zero roda em paralelo: um agente por reuse note do brief, mais um que resolve
   os comandos do gate e roda todos eles uma vez.
4. Estágio zero com reuse note `gone`, gate inexecutável ou árvore já vermelha para o script
   antes da slice 1 e devolve o blocker.
5. As slices rodam num `for` sequencial, uma por agente, na ordem que o `dep:` implica, na
   mesma working tree.
6. Cada agente relê o checkbox da sua slice em disco antes de construir; já ticado, retorna
   sem tocar em nada.
7. Constrói, cumpre o `verifica:`, roda o gate, commita os arquivos que tocou junto com o
   `- [x]`, e retorna veredito, evidência e as convenções que estabeleceu.
8. A nota de convenções acumula: cada agente recebe a das anteriores e devolve ela mais a
   sua, condensada por ele mesmo quando passa do teto.
9. Gate vermelho irrecuperável, `verifica:` reprovado, agente perdido ou brief
   subespecificado param o loop sem commitar a slice; o que ficou verde já está commitado.
10. Todas verdes, o workflow retorna e quem chamou segue — o implement no passo 8, o
    delegate no ship. Loop parado, o caller recebe o blocker e não segue pro ship.
11. Sem workflow disponível, os dois caminhos constroem em contexto e dizem por quê.

| WHEN                                        | THEN                                                             |
| ------------------------------------------- | ---------------------------------------------------------------- |
| workflows desligados por config ou org      | não oferece a escolha; constrói em contexto nomeando o motivo    |
| unattended e workflows desligados           | constrói em contexto; o motivo entra no relatório do delegate    |
| reuse note aponta código que sumiu          | para antes da slice 1; caller flipa `blocked` e aponta o spec    |
| reuse note aponta código que mudou de sítio | segue; o caminho novo entra na nota de convenções                |
| brief sem nenhuma reuse note                | o estágio zero roda só o agente de gate                          |
| o estágio zero não acha gate nenhum         | segue e reporta que não havia gate; não bloqueia                 |
| comando de gate fora da allowlist           | falha no estágio zero; para com blocker de permissão             |
| a árvore já está vermelha antes da slice 1  | para; o gate quebrado não é do build e volta como blocker        |
| o `verifica:` da slice é `leitura`          | o agente confere contra os behaviors citados e devolve evidência |
| o `verifica:` da slice é `CI`               | volta pendente no retorno; quem confere é o ship                 |
| gate vermelho depois dos 3 retries          | a slice não commita, o loop para, a árvore fica pro diagnóstico  |
| o agente acha o brief subespecificado       | retorna o blocker em vez de improvisar; o loop para              |
| um agente de slice volta `null`             | trata como slice falha, para o loop, preserva o que está verde   |
| a run é parada no meio                      | commits e checkboxes seguram o progresso; re-rodar retoma        |
| re-rodada com slices já ticadas             | os agentes delas retornam na hora; o estágio zero roda de novo   |
| você sai do Claude Code com a run viva      | a sessão seguinte não retoma a run; retoma pelos checkboxes      |
| o delegate dirige o build                   | pergunta uma vez só; o implement não re-pergunta                 |
| o brief não tem `## tasks`                  | não entra no modo workflow                                       |
| o brief tem uma slice só                    | pergunta mesmo assim; a escolha é do usuário, não do limiar      |

## tasks

- [x] **1. Reference da forma do script** — `references/build-slices-workflow.md`: `for`
      sequencial, `parallel()` no estágio zero, os schemas de retorno, a nota acumulada com
      teto, a idempotência pelo checkbox, o escopo do commit, o tratamento de gate e
      allowlist, e o checklist que a skill confere antes de invocar
      → behaviors 2, 3, 5, 6, 7, 8, 9 · dep: — · verifica: leitura
- [x] **2. O gate da escolha** — reference compartilhado com a pergunta em PT-BR, quando
      aparece e a regra unattended, no formato do `handoff-gate.md`
      → behavior 1 · dep: — · verifica: leitura
- [x] **3. delegate** — passo novo entre o 2 e o 3, repassa a decisão pro build, suprime a
      pergunta do implement e trata o blocker de volta flipando `blocked`
      → behaviors 1, 4, 10 · dep: 1, 2 · verifica: leitura
- [x] **4. implement** — a mesma escolha quando invocado direto, suprimida quando o delegate
      dirige; blocker de volta cai na válvula do passo 7
      → behaviors 1, 4, 10 · dep: 1, 2 · verifica: leitura
- [x] **5. Fallback sem workflow** — detecção e caminho em contexto nos dois, com o motivo
      dito → behavior 11 · dep: 3, 4 · verifica: leitura
- [x] **6. routines.md** — tira a proibição de fan-out, descreve o modo workflow como default
      da routine e põe a allowlist do gate no provisionamento
      → behaviors 1, 3 · dep: 2 · verifica: leitura
- [x] **7. Versão e docs** — `plugin.json` `2.7.0`, versões de `implement` e `delegate`,
      CHANGELOG, o reference novo no `.claude/CLAUDE.md`
      → behavior 1 · dep: 1-6 · verifica: CI

## out of scope

- Paralelizar slices entre si — o `dep:` e a árvore compartilhada impedem. Se um dia houver
  brief largo com várias slices `dep: —` e arquivos disjuntos, é brief próprio (_revisit_).
- Pre-flight no caminho em contexto — só o modo workflow ganha o estágio zero (_revisit_).
- Script versionado em `workflows/` e comando `/bb:build-slices` — decidido contra.
- Medir custo por run automaticamente — o `/workflows` já mostra tokens por agente.
- Qualquer mudança no `/bb:ship`; o workflow devolve o controle antes do landing.

## open

- Nada.
