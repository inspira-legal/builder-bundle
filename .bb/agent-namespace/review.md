# Review de fix/agent-namespace, achados a aplicar

Estado quando isto foi escrito: branch `fix/agent-namespace`, 8 commits, árvore limpa,
`bun run validate` e `bun run fmt:check` verdes, spec `in-progress` com 6/6 tarefas ticadas.
Sem PR aberto. Escopo autorizado: build, review e ship.

Review standard: 4 fronts, 6 finders, 4 verificadores, 14 candidatos, 13 CONFIRMED,
1 PLAUSIBLE, 0 refutados, 0 sem veredito.

Regra de aplicação (vem de `/bb:implement` passo 11): aplicar todo CONFIRMED, apenas
reportar o PLAUSIBLE. Sem curadoria item a item.

## A aplicar (CONFIRMED)

1. **Bloqueante. `.github/scripts/validate-agent-names.ts:54`.** `FRONTMATTER_REGEX` fecha a
   captura no primeiro `---` sem exigir que ele esteja sozinho na linha (falta âncora de
   início de linha e a flag `m`). Um agente cujo frontmatter traga um `---` dentro de um
   bloco escalar tem o `name:` lido como null, some de `known.names`, e todo despacho
   correto `bb:<esse-agente>` passa a ser reprovado como "names an agent this plugin does
   not ship", na árvore inteira. Reproduzido pelo verificador.

2. **Bloqueante. Commit `eafd6d5`.** Assunto `repo(versão): 3.6.1 com entrada no CHANGELOG`
   inverte tipo e escopo da regra BB025 (`CODE_REVIEW_GUIDE.md:245-250`, tabela HIGH):
   `repo` é valor de escopo, não de tipo. Os outros cinco commits da branch seguem a regra.
   **É o único conserto que reescreve histórico** (amend/rebase). A branch não foi pushada,
   então é seguro. Sugestão: `chore(repo): 3.6.1 com entrada no CHANGELOG`.

3. **Sugestão. `plugins/bb/workflows/build-tasks.js:86-88` e
   `plugins/bb/references/build-tasks-workflow.md:202-203`.** A exclusão da promessa falsa
   levou junto a cláusula verdadeira "plus one line of that protocol": o corpo de
   `reusePrompt()` ainda injeta `Confirm each one against the repo before you judge it, with
\`Grep\` on the symbol it names.`, que duplica o protocolo do `bb-reuse-check.md`. O
   comentário atual é desmentido pelo código duas linhas abaixo. Uma causa, dois locais.

4. **Sugestão. `plugins/bb/references/build-tasks-workflow.md:203`.** A frase ficou
   "carries what only the caller has, the numbered notes and the schema carries the return
   shape": sem a vírgula, "the numbered notes and the schema" lê como objeto composto do
   primeiro "carries", e a leitura literal diz que o schema viaja dentro do prompt, quando
   ele é `opts.schema` e `reusePrompt()` nunca o toca. Mesma frase do item 3, defeito
   distinto.

5. **Sugestão. `CHANGELOG.md:5` e `:7`.** Três citações de linha erradas na entrada 3.6.1:
   cita `build-tasks.js:319` quando o dispatch ficou na `:330` (o próprio commit inseriu 13
   linhas acima dele); cita `build-tasks.js:86-89` como apagado quando 86-87 não mudaram; e
   cita `build-tasks-workflow.md:202-206` quando a 202 não mudou.

6. **Sugestão. `CHANGELOG.md`, entrada 3.6.1 contra a 3.6.0.** A nova diz que o mecanismo de
   degradação "does not exist"; a 3.6.0, logo abaixo e intocada, o afirma como fato ("That is
   the fallback the review fan-out already sets for its finder"). Contradição sem hedge.
   Em escopo pela metade nova: cabe à 3.6.1 reconciliar, não à 3.6.0 mudar.

7. **Sugestão. `.github/scripts/validate-agent-names.ts:100-101` e `:169-172`.** BB019
   (`CODE_REVIEW_GUIDE.md:325`, tabela LOW, escopo alcança `.github/scripts/*.ts`): dois
   `console.error` + `process.exit` para pré-condições esperadas (manifesto sem `name`,
   conjunto derivado vazio). O exemplo canônico que a própria regra cita,
   `plugins/bb/scripts/gather_context.py:113-115`, trata o caso análogo imprimindo JSON no
   stdout. Os dois validadores irmãos não chamam `console.error`/`process.exit` no corpo.

8. **Sugestão (quality). `.github/scripts/validate-agent-names.ts:54,78-92`.** Parsing de
   frontmatter duplicado: o regex é byte a byte o do `validate-frontmatter.ts:27` e
   `frontmatterName()` repete a sequência de `parseFrontmatter()` (:34-56). É o mesmo regex
   do item 1, então sem extrair o conserto tem que ser feito duas vezes.

9. **Sugestão (quality). `.github/scripts/validate-agent-names.ts:175`.** `resolveTargets`
   sem argumento parte de `process.cwd()` e varre o repo todo antes de filtrar por
   `PLUGIN_DIR` no `keep()`, embora o script já calcule `PLUGIN_DIR` e varra `AGENTS_DIR`
   direto duas linhas antes. Acontece a cada commit (lefthook roda `bun run validate`, que
   encadeia o guard) e a cada CI.

10. **Sugestão (quality), acima do teto do relatório mas a aplicar.**
    `.github/scripts/validate-agent-names.ts:106`, o predicado
    `p.endsWith(".md") && basename(dirname(p)) === "agents"` duplica a condição do
    `classify()` em `validate-frontmatter.ts:62`.

11. **Sugestão (quality), acima do teto mas a aplicar.**
    `.github/scripts/validate-agent-names.ts:70-76`, `lineOf()` reimplementa com outro
    algoritmo o utilitário já existente em `validate-workflow-script.ts:257-259`.

Os itens 8, 10 e 11 saem juntos: extrair `parseFrontmatter`, `isAgentFile` e `lineOf` para
`.github/scripts/lib/validate-common.ts` e fazer os três validadores consumirem de lá.
O item 1 se resolve dentro do `parseFrontmatter` compartilhado, corrigindo os dois de uma vez.

## Apenas reportado (PLAUSIBLE, não aplicar)

12. `plugins/bb/workflows/build-tasks.js:207-215`. `messageOf()` devolve `err.message` sem
    corte e isso cai inteiro no `log()` e no `stopped.blocker`, que `/bb:implement` reporta
    à pessoa. Nada trunca em lugar nenhum da cadeia. O que mantém isto em PLAUSIBLE é que
    depende do formato das rejeições da plataforma, que este repo não documenta e o código
    não responde. O verificador também derrubou o argumento do finder de que `NOTE_CEILING`
    seria precedente: aquilo é convenção pedida ao agente no prompt, não teto aplicado pelo
    script.

## Limpo

- **Contract**: as 19 linhas do `## Behavior` e o `## Out of scope` fecham, verificado
  rodando o guard em três estados (em `ff1975e` acusa os cinco pontos; no HEAD, zero sobre
  90 arquivos; apontado à raiz, continua em 90, com `.bb/` e `CHANGELOG.md` fora).
- **Correctness**: rodou `diff-scan`, `removed-behavior` e `instruction-integrity`.
  `cross-file` e `wrapper-boundary` não são financiados no tier standard.
- **Threads**: não rodou, não há PR.

## Deriva do guia, separada dos desvios

- O `CODE_REVIEW_GUIDE.md` descreve `bun run validate` como conferência de frontmatter, e
  agora ele roda um terceiro validador com outro assunto.
- Descreve o glob do lefthook como `*.{json,md}`; ele é `*.{json,md,js,ts}`.
- O guia dá entrada própria a cada uma das cinco regras aplicadas por programa. Esta branch
  acrescenta a sexta sem entrada. Nenhuma regra escrita exige isso, então é lacuna e não
  desvio, e é a origem das duas linhas acima. Fecha com `/bb:review-setup`, fora do escopo
  desta branch.

## Depois de aplicar

Rodar `bun run validate`, `bun run fmt:check` e
`python3 plugins/bb/skills/spec/scripts/lint_spec.py .bb/*/spec.md`, commitar, e seguir para
o ship (`/bb:ship`), que é o resto do escopo autorizado. Nada é mergeado sem a pessoa.
