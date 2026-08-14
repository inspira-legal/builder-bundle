---
status: in-progress
created: 2026-08-12
slug: vocabulario-pt
---

# vocabulário — uma palavra por coisa, em português

O bb escreve `slice` 125 vezes. O usuário nunca escreveu essa palavra, e o plugin também
nunca escreveu "fatia" — mesmo assim "fatia" aparece nas sessões, porque o modelo traduziu
por conta própria. É o retrato do problema: o plugin batiza um conceito em inglês, o Claude
repete o batismo em português inventando a tradução, e sai uma palavra que não existe nem
no código nem na conversa. O gênero oscila na mesma sessão ("o slice 6", "a slice 15") e
oscila dentro do próprio plugin ("construo os slices", "Construo as slices").

Esta spec faz duas coisas que se sustentam: renomeia os conceitos que o bb inventou e
escreve a regra que impede o próximo. Junto vão a espinha da spec em português e a pasta
em disco, que perde um nível.

Sucesso: uma pessoa não-técnica lê a saída de qualquer skill do bb e não encontra palavra
que precise de tradução.

## Duas causas, dois remédios

O levantamento separou os termos por onde eles moram, e a divisão decide o remédio:

| termo        | ocorrências | em linha PT | onde mora                |
| ------------ | ----------- | ----------- | ------------------------ |
| brief        | 423         | 18          | prosa em inglês          |
| scope        | 146         | 5           | prosa em inglês          |
| slice        | 125         | 4           | prosa em inglês          |
| shape        | 64          | 3           | prosa em inglês          |
| blocker      | 42          | 1           | prosa em inglês          |
| load-bearing | 25          | 1           | prosa em inglês          |
| fan-out      | 24          | 2           | prosa em inglês          |
| veredito     | 12          | 5           | `description:` de agente |
| gray area    | 10          | 0           | prosa em inglês          |
| seam         | 3           | 0           | prosa em inglês          |
| lente        | 3           | 2           | `description:` de agente |
| landar       | 2           | 2           | `description:` de skill  |

Quase tudo vive na documentação **em inglês**, e isso divide os termos em dois grupos com
tratamentos diferentes.

**Nome próprio do bb** — `slice` e `brief` nomeiam coisas que só existem aqui dentro. O
nome é o conceito, então trocar o nome mata o vazamento na origem, e a troca vale também
na prosa em inglês, porque é lá que as outras 121 ocorrências estão. Substituição resolve.

**Palavra inglesa em documento inglês** — `blocker`, `load-bearing`, `fan-out`, `scope`,
`gray area`, `seam`. Um documento em inglês escrever "load-bearing decision" é inglês
normal; trocar por "decisão estruturante" no meio da frase produz texto quebrado. Elas
vazam por outro caminho: o Claude lê inglês e fala português, e na hora de falar não tem
palavra pronta. O remédio é a tabela de tradução, não a substituição — o documento fica
como está, e a tabela diz o que dizer quando o texto é português.

## A capitalização já está certa

O pedido era padronizar a capitalização do texto em português, e a varredura devolveu o
contrário do esperado: fora do design system, o português do plugin tem duas linhas em
Title Case, e as duas se defendem — "Fase Deliver" nomeia a fase do duplo diamante, "Não é
o produto final" abre frase. Os rótulos de opção dos gates já são caixa de sentença
consistente, com `(Recomendado)` como sufixo.

O que falta não é limpeza, é a regra: não existe uma linha escrita sobre capitalização em
lugar nenhum do plugin, e foi por isso que a espinha da spec ficou toda em caixa baixa. A
entrega aqui é a regra escrita mais a espinha capitalizada — não um passe de correção.

## A regra, e onde ela mora

O `references/vocabulario.md` novo carrega três coisas: o princípio (chamar cada coisa pelo
nome que ela tem no código ou no repo), a tabela EN→PT acima resolvida, e a capitalização.
Ele é escrito em instrução positiva — diz qual palavra usar, não qual evitar. Listar a
palavra errada ao lado da certa a escreve no prompt e prima o modelo pra ela; é o mesmo
motivo pelo qual o `## design` sobreviveu no `spec/SKILL.md` sendo proibido na linha 55 e
pedido na linha 83.

O ponteiro pra ele vai no `hooks/operating-context.md` porque esse arquivo é injetado no
início da sessão **e depois de cada compactação** — vale pra toda skill e pra conversa
solta, que é o alcance pedido. O `spec-format.md` ganha uma linha própria: a spec é
artefato escrito e o vocabulário dela é o que o builder vai repetir depois.

## decisions

- **`slice` morre.** O item do `## Tarefas` é **tarefa** em português e **task** em inglês.
  São cognatos, então o conceito tem um nome só e nenhuma terceira palavra entra. A troca
  vale na prosa em inglês também — 12 arquivos, incluindo a mensagem `W002` do
  `lint_spec.py`.
- **`fase` é agrupamento de tarefas**, não sinônimo de tarefa. O `/bb:brisar` já usa assim
  ("Fase Develop", "Fase Deliver") — nada a corrigir lá, só a definição a fixar.
- **O nível de cima é `spec`** nas duas línguas: o arquivo é `spec.md`, o comando é
  `/bb:spec`. "a task pendente" vira "a spec pendente"; "the brief" vira "the spec". O
  `references/task-state.md` passa a se chamar `spec-state.md`.
- **Dentro do `skills/brisar/**` a palavra "brief" fica**, porque lá ela é o
  `brief-design.md` — outro artefato, com arquivo e nome próprios. São 207 das 423
  ocorrências. A exceção é onde o texto aponta explicitamente pro `spec.md` ou pro brief do
  `/bb:discover`: essas viram "spec".
- **A pasta perde um nível: `.bb/<slug>/`.** O `.bb/` não guarda nada além de `tasks/`
  hoje, então o nível intermediário só existia pra repetir a palavra que está sendo
  aposentada. O glob de varredura vira `.bb/*/spec.md`.
- **O caminho antigo continua achável.** Os leitores varrem `.bb/*/spec.md` e
  `.bb/tasks/*/spec.md`; spec em outro repo (app, reasoning-bench) não some. O slug da
  pasta é a chave, então a mesma spec nos dois lugares conta uma vez.
- **A espinha é traduzida e capitalizada:** `## Decisões`, `## Comportamento`,
  `## Tarefas`, `## Fora de escopo`, `## Em aberto`. As seções semeadas pelo `/bb:discover`
  vão junto — `## Problema`, `## Hipótese`, `## Encaixe`, `## Cortes` — e a do
  `/bb:legal-lens` também: `## Jurídico`.
- **`dep:` vira `depende:`**; `verifica:` já está em português e fica.
- **O nome inglês continua válido como aviso.** O `lint_spec.py` ganha `W003` — a seção em
  inglês é aceita, com a tradução ao lado; os leitores de seção aceitam os dois nomes. Spec
  antiga em qualquer repo continua construível.
- **O frontmatter fica em inglês** (`status`, `created`, `slug`, `pending|blocked|done`).
  São chaves de dado validadas pelo `E001` e escritas pelo `/bb:delegate`.
- **Os outros termos entram por tabela, não por substituição.** O `vocabulario.md` traz o
  par EN→PT; o documento em inglês fica em inglês.
- **`shape` tem dois sentidos.** No sentido de dar forma a uma ideia é **spec** (rename já
  feito no `spec-legivel`); no sentido de formato de dado (`Finding shape`) é **formato**.
- **As frases-gatilho das `description:` ficam intactas.** "landa essa branch", "esverdeia
  a PR", "shapeia essa ideia" são como o usuário fala e são o que roteia a skill. A tabela
  governa a prosa da `description:`, não a lista de gatilhos.
- **A `description:` em português dos agentes é reescrita.** `bb-finder` e `bb-verifier`
  concentram "veredito", "lente", "fan-out", "read-only" e "Finding shape" em duas frases
  portuguesas — é texto PT, então segue a tabela.
- **Capitalização:** português em caixa de sentença — só a primeira letra sobe. Nome
  próprio e identificador mantêm o caso exato. `(Recomendado)` é sufixo do rótulo.
- **A regra não lista palavra proibida.** Instrução positiva; a tabela tem a coluna
  "escreva", e o termo em inglês aparece só como chave de busca.

## behavior

Caminho principal:

1. A sessão abre (ou compacta) → o hook injeta o ponteiro pro `vocabulario.md` → o Claude
   nomeia as coisas pelo nome que elas têm no repo, escreve "tarefa" e "spec", e usa a
   coluna "escreva" da tabela quando o documento traz o termo em inglês.
2. `/bb:spec` roda → escreve `.bb/<slug>/spec.md` com a espinha em português capitalizada.
3. `lint_spec.py` na spec nova → sem achado.
4. `/bb:implement` lê a spec → acha `## Tarefas`, lê `depende:` e `verifica:`, constrói
   tarefa por tarefa.
5. `/bb:review` caminha `## Comportamento` row a row; o gate do `/bb:spec` bloqueia em
   `## Em aberto`.
6. `/bb:delegate` sem argumento varre `.bb/*/spec.md`, acha as specs migradas e pega a
   pendente mais antiga.
7. O CI roda `validate.yml` → lint em `.bb/*/spec.md` → verde nas 7.
8. `/bb:review` despacha os agentes → a `description:` e o relatório saem em português sem
   termo que precise de tradução.

| #   | WHEN                                                | THEN                                                              |
| --- | --------------------------------------------------- | ------------------------------------------------------------------ |
| 9   | spec antiga com `## decisions`/`## open`            | lint emite `W003` com a tradução; sem erro, arquivo continua válido |
| 10  | spec antiga chega no `/bb:implement`                | acha `## tasks` pelo nome antigo e constrói igual                  |
| 11  | spec mistura `## Tarefas` e `## tasks`              | lint emite `W003` na seção em inglês; as duas são lidas             |
| 12  | spec sem `## Decisões` nem `## decisions`           | `E002` como hoje, agora citando o nome português                   |
| 13  | spec com `## design` ou `## still open`             | `E003` como hoje — nome morto continua morto                       |
| 14  | linha de tarefa ainda escrita com `dep:`            | lida normalmente; `depende:` e `dep:` valem os dois                 |
| 15  | spec mora em `.bb/tasks/<slug>/` de outro repo      | encontrada e construída — o glob antigo continua na varredura       |
| 16  | repo tem `.bb/<slug>/` e `.bb/tasks/<slug>/` iguais | conta uma vez; o slug da pasta é a chave                            |
| 17  | texto em inglês do plugin usa "load-bearing"        | fica como está — a tabela governa o que se escreve em português     |
| 18  | usuário diz "landa essa branch" ou "esverdeia a PR" | roteia pro `/bb:ship` como hoje — os gatilhos não mudam             |
| 19  | `/bb:legal-lens` roda sobre uma spec                | anexa `## Jurídico`; `## legal` existente é lido e avisado          |
| 20  | falta na tabela o termo que o Claude precisa        | descreve em três palavras o que acontece, em vez de batizar         |

## tasks

- [x] **1. `references/vocabulario.md`** — o princípio, a tabela EN→PT e a regra de
      capitalização, em instrução positiva → behaviors 1, 17, 20 · dep: — · verifica: leitura
- [ ] **2. Ponteiro no hook e no formato** — bullet curto no `hooks/operating-context.md`
      e linha no `spec/references/spec-format.md` → behavior 1 · dep: 1 · verifica: leitura
- [ ] **3. Rename `slice` → task/tarefa** — 12 arquivos, incluindo o `W002` do
      `lint_spec.py`; `build-slices-workflow.md` vira `build-tasks-workflow.md` e os 4
      ponteiros pra ele acompanham → behaviors 4, 10 · dep: 1 · verifica: grep zerado
- [ ] **4. Rename do nível de cima → spec** — as 216 ocorrências fora do `skills/brisar/**`,
      mais as do brisar que apontam pro `spec.md`; `task-state.md` vira `spec-state.md`
      → behaviors 2, 4 · dep: 1 · verifica: grep + leitura
- [ ] **5. Pasta `.bb/<slug>/`** — `spec-state.md`, os 33 arquivos que citam o caminho, o
      glob do `delegate` e o `validate.yml`, com o caminho antigo mantido na varredura
      → behaviors 2, 6, 7, 15, 16 · dep: 4 · verifica: CI
- [ ] **6. Espinha em português no formato e no lint** — `spec-format.md` e `lint_spec.py`
      com `W003` e os nomes duplos → behaviors 2, 3, 9, 11, 12, 13 · dep: 3, 4 · verifica: CI
- [ ] **7. Leitores de seção aceitam os dois nomes** — `implement`, `review`, `delegate`,
      `discover`, `brisar`, `legal-lens`, `build-mode`, `spec-state`, mais `depende:`/`dep:`
      → behaviors 4, 5, 10, 14, 19 · dep: 6 · verifica: leitura
- [ ] **8. `description:` dos agentes em português** — `bb-finder` e `bb-verifier` pela
      tabela, gatilhos preservados → behaviors 8, 18 · dep: 1 · verifica: leitura
- [ ] **9. Migrar as 7 specs em disco** — move pra `.bb/<slug>/`, espinha traduzida e
      `depende:`, inclusive as `done` e esta → behaviors 6, 7 · dep: 5, 6 · verifica: CI verde
- [ ] **10. Versão e docs** — `plugin.json` `2.9.0`, CHANGELOG, README e
      `.claude/CLAUDE.md` → behavior 7 · dep: 1-9 · verifica: CI

## out of scope

- Traduzir a prosa em inglês do plugin. Os documentos de referência são escritos em inglês
  e continuam assim.
- `references/ds/brand/**` — "Rich Black", "Cornflower Blue", "Four Entities" são nome de
  cor e de princípio de marca, não texto derivado.
- Passe de correção de capitalização no texto em português: a varredura não achou defeito
  que justifique um.
- Frontmatter e valores de `status`.
- Check de capitalização no CI — detectar caixa por regex em texto misto PT/EN gera falso
  positivo. _revisit_ se a regra escrita não segurar.
- Remover o nome inglês das seções e o glob `.bb/tasks/*/spec.md`. Ficam como aviso; a data
  de remoção é decisão de outro momento, com as specs dos outros repos já migradas.
- Re-medir as sessões pra confirmar que os termos caíram em vez de se deslocarem pra um
  vizinho. _revisit_ — mede-se depois de algumas semanas de uso, não no PR.

## open

- Nada.
