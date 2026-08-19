---
status: in-progress
created: 2026-08-18
slug: doc-style-google
---

# estilo de documentação: o guia do Google no bb

O bb escreve prosa em inglês em dois lugares. Nos documentos que ele gera pra fora, o README
do `/bb:write-readme` e o CODE_REVIEW_GUIDE do `/bb:review-setup`, e na instrução que os
agentes leem: os `SKILL.md`, as `references/`, o `README.md` do repo, o `.claude/CLAUDE.md`.
Nenhuma das duas tem régua hoje. `## How It Works` fica ao lado de `## Style contract`,
`# Quality Checklist` ao lado de `## Bundled Resources`, e o travessão aparece 1737 vezes em
84 arquivos, mesmo com o `/bb:write-readme` proibindo o dele desde a primeira versão.

O guia em https://developers.google.com/style preenche exatamente esse vazio: é o guia de
documentação técnica mais testado que existe, escrito pra quem lê em segunda língua, e o bb
já concorda com metade dele por instinto (segunda pessoa, voz ativa, condição antes da
instrução). Esta spec destila o guia numa reference, registra as duas exceções que o bb
mantém, e passa a régua no que já está escrito.

Sucesso: um agente que vai escrever prosa em inglês abre um arquivo e sabe o que fazer, e a
prosa que ele lê em volta não contradiz esse arquivo.

## A fronteira entre as duas línguas

O guia é inglês: American spelling, word list, tom. Vale na prosa em inglês, que é a
instrução do método e o que o bb gera pra fora. A camada em português (`description:`,
pergunta de gate, rótulo de opção, relatório) continua governada pelo `vocabulario.md`, que
já pede sentence case e já tem a tabela de termos.

A regra do travessão é a única que atravessa as duas línguas, porque é pontuação e não
vocabulário: os 22 travessões que moram em `description:` são linha em português e caem
junto.

## As duas exceções

O guia entra inteiro, com duas divergências decididas que a reference registra na abertura,
pra quem lê saber que não é esquecimento:

1. **Travessão nunca.** Mais forte que a Google, que permite o travessão sem espaço. Onde ele
   iria, vai vírgula, dois-pontos, ponto, ou a frase reescrita. É o contrato que o
   `/bb:write-readme` já tem, promovido ao plugin inteiro.
2. **Voz figurativa fica.** A Google proíbe metáfora porque ela atravessa mal a tradução. No
   bb a metáfora é carga útil: é o que faz a instrução colar no agente que lê o `SKILL.md`. O
   resto do capítulo de tom entra normalmente.

## O tamanho da migração

O escopo é tudo fora de `references/ds/**`, do `CHANGELOG.md` e das specs em `.bb/`. Cada
remoção é julgamento por frase, não `sed`, e por isso a coluna de arquivos importa tanto
quanto a de ocorrências: o fatiamento por área existe pra que cada commit caiba numa leitura.

| área                                          | arquivos | travessões |
| --------------------------------------------- | -------- | ---------- |
| `skills/brisar/**`, sem `ds/`                 | 18       | 784        |
| `skills/review/**` e `skills/review-setup/**` | 21       | 331        |
| `skills/spec/**` e `skills/ship/**`           | 13       | 234        |
| as outras 9 skills                            | 15       | 220        |
| `plugins/bb/references/`, `hooks/`, `agents/` | 12       | 127        |
| `README.md`, `CLAUDE.md`, CI e os 2 `.json`   | 5        | 41         |
| total                                         | 84       | 1737       |

Fora do travessão, a varredura achou 33 meia-riscas, 54 travessões sem espaço e 37 headings
em title case declarado (`### Naming Conventions`, `## Bundled Resources`,
`# Quality Checklist`). Os 259 headings que contêm travessão são reescritos pela regra do
travessão, não por uma tarefa de caixa.

## Decisões

- A reference nova é `plugins/bb/references/doc-style.md`, nível plugin e não escopo de
  skill, porque governa a prosa de todas as skills e a do repo. O `hooks/operating-context.md`
  aponta pra ela junto com o `vocabulario.md`, que é como a régua alcança uma sessão em
  qualquer repo, não só neste. Sem skill nova e sem lente de
  docs no `/bb:review`: a régua é leitura de quem escreve, não passo de revisão.
- Dentro dela, só forma positiva. Sem par recommended/not recommended e sem catálogo de
  errado: escrever o errado ao lado do certo prima o errado, que é a regra de prompt do
  `CLAUDE.md` global.
- Precedência: regra da casa primeiro, guia depois. É a hierarquia que a própria Google
  publica. Onde o `/bb:write-readme` já tem contrato (tudo minúsculo, quatro blocos, badge
  por fato verificável), o contrato ganha, e o `SKILL.md` dele aponta pra reference em vez de
  repetir a regra do travessão.
- Travessão nunca, nas duas línguas. A meia-risca sai pelo mesmo caminho, e o travessão sem
  espaço entra na mesma varredura.
- Um travessão que é token funcional fica: quando o caractere está dentro de comando, regex,
  path ou string comparada em código, tirar não é estilo, é mudança de comportamento.
- Citação verbatim de fonte externa mantém a pontuação da fonte. É a única exceção à regra do
  travessão.
- Template gerado segue a regra. O bloco cercado que é modelo de saída, o
  `review-setup/references/guide-template.md` e os templates de relatório, é prosa que o bb
  escreve pra fora.
- Heading em sentence case fora de `ds/`. Nome próprio e identificador mantêm a caixa:
  `# Builder Bundle (bb)`, `Mobbin`, `Framer`, `LexFlow`, `Phase Framer`.
- `references/ds/**` fica intocado. É o brand package da Inspira, conteúdo de marca com voz
  própria.
- No `CHANGELOG.md`, as entradas antigas ficam. A entrada nova troca o heading pra
  `## 2.12.0 (2026-08-18)`, porque o formato atual separa versão e data com travessão.
- As 7 specs em `.bb/` ficam como estão. São registro landado; só esta segue a regra nova.
- O enforcement é a reference ser lida. Sem check no CI e sem script: um detector de
  travessão em prosa mista PT/EN acusa token funcional e citação, e o falso positivo custa
  mais que o desvio.
- Landa numa PR só, com um commit por área.
- Versão `2.12.0`.

## Comportamento

Caminho principal:

1. Um agente vai escrever prosa em inglês → o `.claude/CLAUDE.md` aponta pro `doc-style.md` →
   ele lê a reference antes de escrever.
2. Ele escreve heading em sentence case, segunda pessoa, voz ativa, condição antes da
   instrução, code font em filename, classe, método, status HTTP e placeholder, e nenhum
   travessão.
3. `/bb:write-readme` roda → mantém tudo minúsculo, os quatro blocos e a badge por fato
   verificável → o README sai sem travessão e sem meia-risca.
4. `/bb:review-setup` roda → o `guide-template.md` gera o CODE_REVIEW_GUIDE com heading em
   sentence case e sem travessão.
5. `/bb:spec` escreve uma spec → prosa em português pelo `vocabulario.md`, e sem travessão.
6. O CI roda no PR → frontmatter, lint de spec e `fmt:check` verdes.

| #   | WHEN                                                     | THEN                                             |
| --- | -------------------------------------------------------- | ------------------------------------------------ |
| 7   | grep de travessão fora de `ds/`, `CHANGELOG.md` e `.bb/` | zero ocorrências                                 |
| 8   | grep de meia-risca no mesmo escopo                       | zero, fora de token funcional                    |
| 9   | a prosa cita verbatim uma fonte que usa travessão        | a citação mantém a pontuação da fonte            |
| 10  | o caractere está em comando, regex, path ou string       | fica; remover mudaria comportamento              |
| 11  | o heading tem nome próprio ou identificador              | a caixa original fica                            |
| 12  | o heading combina rótulo e frase com travessão           | vira `## Phase 2: maturity gate`                 |
| 13  | regra do guia bate com contrato do `/bb:write-readme`    | o contrato da casa ganha                         |
| 14  | entrada nova no `CHANGELOG.md`                           | heading `## 2.12.0 (2026-08-18)`                 |
| 15  | entrada antiga do CHANGELOG ou spec em `.bb/`            | intocada                                         |
| 16  | arquivo dentro de `references/ds/**`                     | nada muda                                        |
| 17  | linha em português: `description:`, gate, relatório      | `vocabulario.md` manda; daqui vem só o travessão |
| 18  | a prosa em inglês usa metáfora                           | fica; a exceção está escrita na reference        |

## Tarefas

- [x] **1. `references/doc-style.md`**: o guia destilado em forma positiva, cobrindo tom e
      voz, heading, formatação de texto, lista e tabela, link, data e número, mais as duas
      exceções e a precedência → behaviors 1, 2, 11, 13, 17, 18 · depende: nada · verifica: leitura
- [x] **2. Os quatro leitores**: ponteiro no `.claude/CLAUDE.md`, no `hooks/operating-context.md`,
      no `write-readme/SKILL.md` e no `review-setup/references/guide-template.md`; o
      write-readme fica só com as regras da casa
      → behaviors 1, 3, 4, 5, 13 · depende: 1 · verifica: leitura
- [x] **3. Triagem dos headings**: os 37 em title case declarado fora de `ds/`, mais os
      candidatos onde a caixa depende de nome próprio ou de template → behaviors 2, 11 ·
      depende: 1 · verifica: leitura
- [x] **4. Travessão no `brisar`**: 784 em 18 arquivos, com `ds/` fora
      → behaviors 7, 12, 16 · depende: 1 · verifica: grep zerado
- [x] **5. Travessão no `review` e no `review-setup`**: 331 em 21 arquivos, incluindo os
      templates de relatório e o `guide-template.md`
      → behaviors 7, 9, 10, 12 · depende: 1 · verifica: grep zerado
- [x] **6. Travessão no `spec` e no `ship`**: 234 em 13 arquivos, incluindo os templates de
      relatório e a espinha que o `/bb:spec` escreve
      → behaviors 5, 7, 12 · depende: 1 · verifica: grep zerado
- [x] **7. Travessão nas outras 9 skills**: 220 em 15 arquivos: `discover` 44, `challenge`
      32, `code-deep-research` 27, `maintain-repo` 24, `implement` 23, `legal-lens` 23,
      `delegate` 19, `think` 19, `gather-branch-context` 9; os 22 de `description:` moram
      nesses arquivos → behaviors 7, 17 · depende: 1 · verifica: grep zerado
- [x] **8. Travessão nas references do plugin, nos hooks e nos agents**: 127 em 12 arquivos,
      incluindo o `vocabulario.md` e o `operating-context.md`
      → behavior 7 · depende: 1 · verifica: grep zerado
- [ ] **9. Travessão na doc do repo**: 41 em 5 arquivos: `README.md` 18, `.claude/CLAUDE.md`
      20, a mensagem de echo do `validate.yml` e os 2 `.json` de plugin
      → behavior 7 · depende: 2 · verifica: grep zerado
- [ ] **10. Meia-risca e travessão sem espaço**: as 33 e os 54 em escopo, com o token
      funcional preservado → behaviors 8, 10 · depende: 4, 5, 6, 7, 8, 9 · verifica: grep
- [ ] **11. Versão e CHANGELOG**: `plugin.json` em `2.12.0` e a entrada nova com heading
      `## 2.12.0 (2026-08-18)`, em prosa sem travessão
      → behaviors 6, 14, 15 · depende: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 · verifica: CI verde

## Fora de escopo

- `references/ds/**`: 383 travessões, 74 headings com travessão e 70 em title case. É o brand
  package da Inspira, conteúdo de marca com voz própria.
- Entradas antigas do `CHANGELOG.md`, 122 travessões. Registro histórico: reescrever muda o
  que já foi publicado.
- As 7 specs em `.bb/`, 231 travessões. Estão landadas.
- Check no CI ou script de detecção. _revisit_ se a régua escrita não segurar; a medida é um
  grep novo depois de algumas semanas de uso.
- Lente de docs no `/bb:review`, e uma skill `/bb:docs`.
- American spelling e a word list na prosa em português. O `vocabulario.md` continua sozinho
  ali.
- Reescrever a voz figurativa do plugin.
- Traduzir a prosa em inglês, inclusive a reference nova: ela é instrução de método, logo fica
  em inglês.

## Em aberto

- O `verifica: grep zerado` das tarefas 4 a 9 prova que o caractere saiu, não que a frase
  ficou boa. A vírgula mecânica no lugar do travessão às vezes precisa virar dois-pontos ou
  frase nova, e isso só a leitura pega. O commit por área existe pra que essa leitura caiba.
- O `fmt:check` reformata tabela: uma reescrita que muda a largura de uma célula muda o
  padding da coluna inteira. É ruído esperado no diff das tarefas 4 a 9, não defeito.
