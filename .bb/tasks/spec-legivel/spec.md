---
status: in-progress
created: 2026-08-05
slug: spec-legivel
---

# spec — um documento pra ser lido

O `/bb:spec` produz briefs que ninguém reabre. As três specs em disco somam 485 linhas
e o custo aparece na ponta: quem vai construir prefere reler a conversa. A mudança é
tratar a spec como **documento**, não como formulário — abertura e corpo livres, escritos
pra serem lidos, apoiados numa espinha fixa que as outras skills consomem.

Junto vêm quatro coisas que a mesma mudança resolve: o revisor independente vira passo
estrutural, a justificativa de mudança sai do arquivo e vai pro commit, o `## tasks`
passa a carregar o que um workflow precisa, e `shape` some do vocabulário.

Sucesso: o builder abre a spec e sabe o que construir sem reabrir a conversa.

## O que quebrou nas três specs

Nenhum dos defeitos é "tem prosa demais". São quatro, e todos têm causa no prompt:

**Prosa que reconta a conversa.** O `ship-lexflow` tem uma seção inteira chamada
_"Correção de leitura própria"_ — "eu havia registrado X, a leitura da fonte refina
isso". O `review-agents` grava "Decisão do usuário, com o custo declarado" e cita o sha
`9a461e8`. Isso é histórico, e histórico tem lugar próprio: a mensagem de commit.

**Tabela usada como prosa.** O `## decisions` do `review-agents` é uma tabela de duas
colunas cuja coluna direita tem parágrafos de 300+ caracteres; o oxfmt então alinha
tudo pela célula mais larga. Uma row inclusive quebrou — um `|` não escapado dentro de
`file:line | summary` destruiu a linha 103. Prosa em célula de tabela é ilegível de um
jeito que prosa em parágrafo não é.

**Seis seções dizendo a mesma coisa.** `what`, `why`, `decisions`, `design`, `behavior` e
`tasks` repetem o mesmo fato três ou quatro vezes — o `tools: Read, Grep, Glob, Bash` do
`review-agents` aparece em quatro lugares. A causa são dois índices concorrentes: o
`draft-first.md:13-25` lista 7 coisas que o draft deve cobrir e o "Capture the alignment"
do `SKILL.md` lista outras. O modelo escreve as duas.

**E o prompt pede o que a gente não quer.** `SKILL.md:55` diz "Don't write a design
document"; vinte e oito linhas depois, `:83` manda escrever `## design` com "components
and their boundaries, the data model, key data flows". Entre proibição e instrução
positiva, a positiva ganha sempre — e o `## design` é justamente a seção que ninguém lê
depois (`implement` lê `tasks` e `behavior`, o review caminha `behavior`, `delegate` lê o
frontmatter). Seção sem consumidor deriva.

## A forma nova

A spec passa a ter duas metades, com regras diferentes.

```
---  frontmatter  ---                    contrato (task-state.md)

# título
abertura, 1–3 parágrafos                 ┐
                                         │  metade de cima: livre
## <seção que o problema pedir>          │  quantas seções quiser, com os nomes
## <outra>                               ┘  que o problema pedir. prosa, diagrama,
                                            tabela curta, código.
## decisions                             ┐
## behavior                              │  espinha: fixa, nesta ordem
## tasks                                 │  cada uma tem consumidor
## out of scope                          │
## open                                  ┘
```

A espinha é fixa porque tem quem leia. A metade de cima não tem consumidor de máquina —
tem leitor humano, e por isso a forma dela é do autor.

`## design` não volta em nenhuma das metades: no bb a palavra já significa desenho de
tela (`/bb:brisar` escreve `design/<surface>.md`). Arquitetura, quando o caso pede, mora
na metade de cima com o nome que ela tem naquele problema — "o seam entre agente e
caller" diz mais que "design".

## decisions

- **Espinha fixa, topo livre** — `decisions`, `behavior`, `tasks`, `out of scope` e
  `open` nesta ordem no fim; acima delas, abertura e quantas seções o problema pedir.
- **A prosa descreve, não reconta** — o que a coisa é e como se comporta fica na spec;
  como chegamos até ela vai pro corpo do commit. É o critério que separa as duas.
- **Célula de tabela é para dado curto** — passou de 100 chars, vira prosa ou bullet. O
  número vem do oxfmt: `fmt:check` roda `oxfmt --check .` sem ignore, então ele já
  formata `.bb/` e alinha a coluna inteira pela célula mais larga. Uma célula de 300
  chars empurra a tabela toda pra fora da tela.
- **Espinha obrigatória vs. recomendada** — o lint erra na falta de `## decisions` ou
  `## open`; avisa na falta de `## behavior` e `## tasks`, que spec Medium não precisa ter.
- **`## design` é nome morto** — o lint barra. Arquitetura vai pro topo, com nome próprio.
- **`## still open` → `## open`** — nome único, e só decisão de fato aberta.
- **`## cuts` do discover permanece** — é escopo cortado *na fase de problema*, com o
  porquê; `## out of scope` é o que esta spec não faz. O lint aceita as duas.
- **Remover > negar** — saem do prompt: o parágrafo do `## design` (`SKILL.md:83`),
  "map them meticulously" (`:68`), "Don't abbreviate" (`:70`) e a lista de 7 itens do
  `draft-first.md:13-25`, que é o índice concorrente.
- **Slice carrega dep e verificação** — `- [ ] **N. nome** — entrega → behaviors 1,3 ·
  dep: N-1 · verifica: <como>`. É o DAG que um workflow consome sem reinterpretar prosa.
- **Revisor é passo próprio** — obrigatório em Medium+, antes do gate, veredito de uma
  linha no gate. Hoje é sub-bullet de um passo condicional.
- **Lint só no mecânico** — erro: `## design`, `## still open`, row com contagem de células
  errada, célula > 100 chars, frontmatter inválido, seção obrigatória ausente. Sem teto de
  linhas: tamanho é julgamento, e julgamento é do revisor independente, que ganha
  duplicação e arqueologia no mandato.
- **CI: um passo `python3` no `validate.yml`** — `python3 plugins/bb/skills/spec/scripts/lint_spec.py .bb/tasks/*/spec.md`,
  sem `setup-python` (o `ubuntu-latest` já traz), mais `.bb/tasks/**` nos `paths:` pra o
  job disparar quando só a spec muda. O `fmt:check` já cobre esses arquivos hoje.
- **Rename só no processo** — `shape`/`shaped`/`shapear`/`re-shape` → spec/especificar.
  `Finding shape` e `return shape` ficam: são formato de dado, outro sentido.
- **Versão** — `plugin.json` `2.3.0` → `2.4.0`. Cada SKILL.md tocado incrementa a versão
  **dele** (`spec` vai de `2.0.0` a `2.1.0`); os dois números são independentes.

## behavior

1. `/bb:spec <ideia>` roda draft-first — fork de maior aposta primeiro, zonas cinzentas
   em batch pelo question tool — e o draft já nasce na forma nova.
2. O brief tem topo livre e espinha; o que é histórico não entra, vai pro commit.
3. Cada slice cita os behaviors que entrega, `dep:` e `verifica:` — é daí que sai o
   rastreio de cobertura e o DAG que um workflow consome.
4. O revisor independente roda em todo brief Medium+, em contexto fresco, só com o brief.
5. `lint_spec.py` roda antes do gate; o que ele apontar é corrigido ali.
6. O gate mostra happy path, edges, cobertura e o veredito do revisor, finaliza
   `.bb/tasks/<slug>/spec.md` e oferece implement / delegate / parar.
7. Toda skill que fala do brief diz "spec"; "shape" só sobrevive como formato de dado.

| WHEN                                     | THEN                                                             |
| ---------------------------------------- | ---------------------------------------------------------------- |
| a spec é reescrita depois de landada     | o porquê mudou vai no commit; o arquivo só ganha a decisão nova  |
| aparece uma seção `## design`            | o lint falha nomeando a linha e aponta a metade de cima          |
| célula de tabela passa de 100 chars      | o lint falha; o conteúdo vira prosa ou bullet                    |
| uma row tem `\|` não escapado            | o lint pega pela contagem de células — o bug de `review-agents:103` |
| falta `## behavior` ou `## tasks`        | o lint avisa; spec Medium pode não ter as duas                   |
| o autor cria seções próprias no topo     | passa — é o ponto; o lint só checa a espinha                     |
| spec antiga de outro repo tem `## design`| o lint só roda no que o `/bb:spec` acabou de escrever            |
| não há Agent tool no host                | o revisor não roda e o gate diz isso, em vez de omitir           |
| o revisor acha buraco load-bearing       | volta pro passo de perguntas; o gate não abre com decisão aberta |
| o trabalho é Tiny                        | nada de spec — segue a regra de auto-size que já existe          |
| o brief foi seedado pelo `/bb:discover`  | as seções upstream ficam no topo, que é livre                    |

## tasks

- [x] **1. Formato e lint** — `references/spec-format.md` (as duas metades, a espinha, o
      critério descreve-vs-reconta) e `scripts/lint_spec.py` (stdlib, `path:line CODE msg`,
      exit 1 no erro) → behaviors 2, 3, 5 · dep: — · verifica: CI
- [x] **2. Poda do prompt** — deleta do `SKILL.md` o parágrafo do `## design`,
      "meticulously" e "Don't abbreviate"; mata a lista de 7 do `draft-first.md`; os dois
      passam a apontar pro `spec-format.md` → behaviors 1, 2 · dep: 1 · verifica: CI
- [x] **3. Revisor como passo próprio** — passo dedicado no `SKILL.md`, obrigatório em
      Medium+, com duplicação e arqueologia no mandato; veredito de uma linha no gate
      → behaviors 4, 6 · dep: 2 · verifica: leitura
- [x] **4. Slice pronta pra workflow** — `dep:` e `verifica:` no `spec-format.md`;
      `implement` e `delegate` leem os dois → behavior 3 · dep: 1 · verifica: leitura
- [x] **5. Justificativa no commit** — linha no `SKILL.md` e na seção Commits do
      `.claude/CLAUDE.md` → behavior 2 · dep: — · verifica: leitura
- [x] **6. Rename shape→spec** — `task-state.md`, `delegate`, `implement`, `discover`,
      `brisar`, `operating-context.md`, `routines.md`, `spec/SKILL.md`, README
      → behavior 7 · dep: — · verifica: CI
- [x] **7. Migrar as 3 specs e ligar o CI** — reescreve `builder-bundle`, `ship-lexflow` e
      `review-agents` na forma nova; passo `python3` e `.bb/tasks/**` no `validate.yml`
      → behavior 5 · dep: 1, 6 · verifica: CI verde
- [ ] **8. Versão e docs** — `plugin.json` `2.4.0`, `spec/SKILL.md` `2.1.0`, CHANGELOG,
      `.claude/CLAUDE.md` → behavior 7 · dep: 1-7 · verifica: CI

## out of scope

- Workflow no `implement`/`delegate` pra construir as slices — brief próprio, logo depois
  deste. Aqui entra só o que a spec precisa entregar pra ele.
- `Finding shape` e `return shape` no review — outro sentido da palavra.
- Modo export (`references/export-spec.md`) — documento externo, não é o brief.

## open

- Nada.
