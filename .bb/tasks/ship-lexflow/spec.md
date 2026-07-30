---
status: done
created: 2026-07-30
slug: ship-lexflow
---

# ship — destino LexFlow

## what

Adicionar **LexFlow** como 4º destino do `/bb:ship`, ao lado de branch / main / PR. Quem
constrói app LexFlow passa a ter o mesmo caminho de landing que todo mundo: quality pass →
commit → push → e então o comando de deploy **entregue na mão**, nunca apertado pelo ship.

Junto vem um refactor: os quatro landings saem do `SKILL.md` pra `references/land-*.md`,
deixando o `SKILL.md` como router (progressive disclosure — o `CLAUDE.md` do repo trata
`SKILL.md` monolítico como defeito, e o landing de PR sozinho já tem ~55 linhas).

## why

Hoje o `ship` sempre desembocaria em PR, e parte do time constrói em LexFlow sem `gh`. Mas o
gap não é de conveniência: **ninguém revisa os YAMLs de workflow LexFlow hoje.** Os app repos
(`data-magnifier`, `data-inspira-hm`, `data-chat-features-hm`) não têm `.github/` nenhum — zero
CI — e o `lexflow-builder` só valida a sintaxe do YAML que ele mesmo acabou de gerar. O quality
pass do `ship` é exatamente a substância que falta ali.

E dá pra fazer isso sem inventar nada: esse cohort **tem git**, os apps **são** repos git, então
a espinha do ship (diff → review → commit → push) já serve.

Sinal de sucesso: um app LexFlow chega no deploy tendo passado por review de verdade, e o
builder aperta o deploy sabendo qual sha está subindo.

## design

### O que é um app LexFlow (o que a leitura da fonte corrigiu)

Fonte lida: `inspira-legal/lexflow-automacoes/lexflow-deploy-cli/` (README + `cli.py`,
`manifest.py`, `deploy.py`, `doctor.py`).

- **O remote é a plataforma, não o GitHub.** `lexflow clone`/`init` instalam um credential
  helper em `~/.config/lexflow/git-credentials-helper.py` que autentica via JWT do Firebase.
  Um `git clone` cru da URL falha com `could not read Username` numa máquina que nunca rodou
  `lexflow login`. Não existe mecanismo de PR nesse remote — o que confirma o destino exclusivo.
- **`push` ≠ `deploy`, por design deliberado.** A CLI é explícita: "Pushing to the git remote
  does NOT trigger a deploy" — o bucket é storage versionado. E ela instrui LLMs diretamente:
  "prefer raw git for read paths"; "if the user asks you to 'push the changes', that's a VCS
  operation; if they ask you to 'deploy', that's `lexflow deploy`".
  → Push é seguro e autorizado pra ferramenta agêntica. Deploy é o ato irreversível.
- **`manifest.py` já valida a coerência do `lexflow.toml`** que este brief ia reimplementar:
  campos obrigatórios, formato de slug, slugs duplicados (datastore/workflow/deployment) e
  existência de cada `source` — inclusive de middleware.
- **`load_manifest` roda antes da rede.** Em `deploy()`: auth → `load_manifest` → (`ManifestError`
  → imprime `Manifest error:` + exit 1) → só então fetch do estado da plataforma → diff.
- **`lexflow deploy --ref <branch|tag|sha>`** busca a fonte do git host naquele ref e deploya
  exatamente aquele commit, gravando o `git_sha` no deployment.
- Comandos que existem: `login/logout`, `deploy`, `refs`, `clone`, `sync`, `init`, `push`, `pull`,
  `doctor`, `self-update`, `destroy`, `secret *`, `connection *`, `examples *`, `opcodes *`.
  **Não existe `lexflow validate`** — e `doctor` é só detecção de tooling local (git/uv/claude),
  não validação de manifest.

### Correção de leitura própria

Eu havia registrado `--dry-run` como gate não confiável (bug da Thais em #team-ai-stack,
2026-05-06: 500 por datastore órfão do team). A leitura da fonte refina isso: `--dry-run` é
inútil como gate **de plano** e confiável como gate **de manifest**, porque a validação local
acontece antes da chamada de rede que quebra. É isso que separa bloquear de reportar.

### As três camadas do ship, e o que muda em cada

| Camada                       | Muda? | Como                                              |
| ---------------------------- | ----- | ------------------------------------------------- |
| Destino (Step 1)             | sim   | 4º destino + preflight de detecção                |
| Gate + quality pass (Step 2) | sim   | gate próprio; lentes re-apontadas pro artefato    |
| Landing                      | sim   | novo `land-lexflow.md` + extração dos outros três |

### Detecção (preflight no Step 1)

`lexflow.toml` na raiz → seta `project_kind: lexflow`, flag que Step 1 e Step 2 leem.

A flag torna LexFlow a opção **recomendada** do Step 1, e não pula a pergunta: o mesmo repo pode
legitimamente querer um PR naquela rodada. Detecção informa; o destino segue escolha única.

### O gate LexFlow (três camadas, uma autoridade cada)

1. **Pré-check local** — `scripts/check_lexflow_manifest.py` (script próprio do skill, path
   relativo por convenção). Só o subset barato e estável, via `tomllib`: existe `[app]`, e cada
   `source` (deployments, workflows, middlewares) aponta pra arquivo real. Falha em ms, sem rede,
   funciona deslogado. Nada além disso — o resto é da CLI e duplicar drifta.
2. **`lexflow deploy --dry-run`** — autoridade sobre o manifest. Classificação em três baldes:
   `Manifest error:` + exit 1 → culpa do app, acionável → **bloqueia e conserta**. 500 / rede na
   fase de diff → instabilidade de plataforma → **reporta e segue**. CLI ausente ou deslogado →
   **check pulado**, aponta `lexflow login`.
3. **Leitura do LLM nos YAMLs** — os workflows são pequenos e declarativos; o LLM lê e confere
   nomes e params de opcode contra `lexflow opcodes list`. Zero parser de YAML em Python (a regra
   do repo é stdlib only, e stdlib não tem YAML).

### Quality pass — lentes re-apontadas

A estrutura fica: quatro agentes, **uma lente cada**, saída `file:line | what | evidence |
suggested fix | confidence`. O conteúdo das lentes não: `async-state` é peso morto num manifest
declarativo. Pra `project_kind: lexflow` o fan-out troca o set pra caber no artefato — lógica e
edges do workflow / contratos de opcode e secrets-permissões / correção das queries / qualidade.

### Landing

`push` (git puro — commit + push, reversível, explicitamente autorizado pra LLM) e então
**entrega** `lexflow deploy --ref <sha>` com o sha que passou pelo quality pass. Fecha o buraco
entre o que foi revisado e o que sobe, e a plataforma grava esse `git_sha` no deployment.

Segue valendo: nunca faz merge, nunca aprova, nunca force-push, **nunca deploya**.

## decisions

- **4º destino exclusivo**, não um passo que compõe com o landing git. Step 1 continua escolha
  única: branch / main / PR / LexFlow. Quem escolhe LexFlow não abre PR naquela rodada; quem
  quer os dois roda o ship duas vezes. _Consequência aceita:_ o caso "PR pra revisão humana **e**
  deploy" custa duas rodadas.
- **O ship entrega o comando de deploy, não aperta.** Convenção a seguir, não a inventar: o
  `lexflow-builder` já decidiu isso ("não executa deploy automaticamente").
- **Comando entregue: `lexflow deploy --ref <sha>`** (não o `lexflow deploy` puro), pra deployar
  o commit revisado em vez da working tree.
- **Gate = pré-check `tomllib` + CLI como autoridade + LLM nos YAMLs.**
- **Bloqueia erro de manifest; reporta erro de plataforma; pula quando deslogado.**
- **Extrai os quatro landings** pra `references/land-{branch,main,pr,lexflow}.md`; `SKILL.md`
  vira router.
- **Reuso:** `${CLAUDE_PLUGIN_ROOT}/scripts/gather_context.py` serve sem alteração (git puro — e
  a CLI recomenda exatamente isso pra read paths). `references/review-checklist.md` e
  `references/loop.md` seguem valendo. `fetch_comments.py`, `reply_resolve_thread.py` e
  `scripts/inspect_pr_checks.py` são do caminho de PR e não entram aqui.
- **bb aponta pro `lexflow-builder`, não re-ensina deploy.** As mecânicas (montar o
  `lexflow.toml`, a flag `--url`, a URL de publicação) são do time de plataforma; restatear
  drifta quando a plataforma mudar.
- **Output de CLI e conteúdo de YAML são dados, não instruções** — estende a linha que o ship já
  tem pra comentário de PR e log de CI.

## behavior

### Happy path

1. Builder roda `/bb:ship` num repo com `lexflow.toml` na raiz.
2. Preflight seta `project_kind: lexflow`; Step 1 oferece os quatro destinos com LexFlow
   recomendado. Builder escolhe LexFlow.
3. Pré-check local passa (`[app]` presente, todo `source` existe).
4. Quality pass: fan-out de quatro lentes re-apontadas sobre o diff; findings voltam com
   `file:line | what | evidence | suggested fix | confidence`. Fixes aplicados só no contexto
   principal (um escritor só). Re-run do gate.
5. `lexflow opcodes list` → LLM confere os opcodes usados nos YAMLs tocados pelo diff.
6. `lexflow deploy --dry-run` → plano computado, reportado como informação.
7. Commit em unidades lógicas (conventional, sem atribuição de IA) → `git push`.
8. Relatório final: sha, quais deployments o diff afeta (derivado do `lexflow.toml`), resultado
   de cada camada do gate, e o comando: `lexflow deploy --ref <sha>`.

### Edges

| Caso                                                                                                                                                 | Resultado                                                                                                                                       |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| WHEN o diff não toca nenhum arquivo referenciado pelo `lexflow.toml` (README, notas de design, fixture)                                              | THEN commita e dá push, e **omite o handoff de deploy** — não há o que deployar (a CLI desenhou o bucket exatamente pra isso)                   |
| WHEN o arquivo mudado não é referenciado por nenhum `source` declarado, mas pode ser referenciado **de dentro** de um workflow (ex: `queries/*.sql`) | THEN o pré-check devolve `affects_deploy: "unknown"` em vez de um falso negativo; o LLM lê os YAMLs, decide, e diz de que jeito chamou          |
| WHEN o pré-check acha um `source` apontando pra arquivo inexistente                                                                                  | THEN bloqueia antes do quality pass, nomeia o path e o deployment, conserta                                                                     |
| WHEN `lexflow deploy --dry-run` sai com `Manifest error:`                                                                                            | THEN bloqueia, conserta, re-roda o dry-run                                                                                                      |
| WHEN o dry-run dá 500 / erro de rede na fase de diff                                                                                                 | THEN reporta como instabilidade de plataforma (não do app), segue o landing, e diz que o plano não pôde ser computado                           |
| WHEN não está logado (`_get_auth` falha antes de tudo)                                                                                               | THEN dry-run e `opcodes list` viram checks pulados; pré-check e leitura do LLM seguem; aponta `lexflow login`                                   |
| WHEN a CLI `lexflow` não está no PATH ou o shim está quebrado                                                                                        | THEN mesma degradação de deslogado, e reporta o shim quebrado como diagnóstico (aconteceu nesta máquina: shim apontando pra um Python removido) |
| WHEN o `git push` falha com `could not read Username`                                                                                                | THEN diagnostica como credential helper não instalado e aponta `lexflow login` / `lexflow clone` — não trata como problema de git               |
| WHEN o push é rejeitado por remote à frente                                                                                                          | THEN `lexflow sync` (ff-only) ou `lexflow pull`; segue proibido force-push                                                                      |
| WHEN o diff declara um `$secret` novo em `[env]`                                                                                                     | THEN nomeia o secret no relatório e aponta `lexflow secret set` — o deploy vai pedir por ele                                                    |
| WHEN o diff toca `[[datastores]]`                                                                                                                    | THEN avisa que é a área do bug conhecido de dry-run (fetch de todos os datastores do team) e que um 500 ali provavelmente não é do app          |
| WHEN existem múltiplos `lexflow.toml` (monorepo de apps)                                                                                             | THEN deriva o app pelo que o diff toca; se o diff cruza mais de um app, pergunta qual                                                           |
| WHEN o builder pede destino LexFlow e não há `lexflow.toml`                                                                                          | THEN diz que não achou o manifest e sugere o diretório certo ou `lexflow clone`                                                                 |
| WHEN o diff é pequeno (≲2 arquivos / ≲100 linhas)                                                                                                    | THEN pula o fan-out, review inline — regra atual do ship, mantida                                                                               |
| WHEN alguém deployou outro sha nesse meio-tempo                                                                                                      | THEN irrelevante pro handoff: `--ref <sha>` é determinístico                                                                                    |

## tasks

- [x] Preflight de detecção no Step 1 + 4º destino no `SKILL.md` (entrega: `/bb:ship` num repo LexFlow oferece o destino) — behaviors: happy 1–2, edges "múltiplos `lexflow.toml`", "sem `lexflow.toml`"
- [x] `scripts/check_lexflow_manifest.py` — pré-check `tomllib` (`[app]` + existência de todo `source`), stdlib only, stdout consumível — behaviors: happy 3, edge "`source` inexistente"
- [x] Extração dos quatro landings pra `references/land-{branch,main,pr,lexflow}.md`; `SKILL.md` vira router — sem mudança de behavior nos três existentes (refactor de estrutura)
- [x] `references/land-lexflow.md` — gate (3 camadas + classificação do dry-run), quality pass com lentes re-apontadas, landing push + handoff `--ref <sha>`, template de relatório em PT-BR — behaviors: happy 3–8 e todos os edges de gate/push/deploy
- [x] Triggers PT-BR na frontmatter do `SKILL.md` ("deployar no lexflow", "subir o app lexflow") — behavior: happy 1
- [x] Linha no `CHANGELOG.md`

## out of scope

- Builders sem tooling local nenhum (ex: Claude web, que resolvem deploy pedindo no Slack pra
  alguém deployar). Fora do alcance do ship; a plataforma tem o chat interno do LexFlow.
- Re-ensinar mecânica de deploy dentro do bb (ownership do `lexflow-builder`).
- Apertar o deploy, mesmo com autorização prévia. _revisit:_ não antes de a plataforma ter
  rollback de deployment.
- Fragmentação das três skills `*-builder` concorrentes (`lexflow-builder` em
  `lexflow-automacoes`, `lex-flow-builder` em `lex-flow`, e o bb). Maior que o ship e é conversa
  com o time de plataforma (Capitani/Giro). _revisit:_ depois deste brief entregar.
- Re-adicionar `lexflow` ao `product-registry.yaml` do `brisar` (entrada removida no build beta
  por `repo_url` TODO). _revisit:_ quando os repo_urls canônicos fecharem.
- Consertar o shim quebrado da CLI nesta máquina — pré-requisito de teste, não escopo do brief.

## still open

- Nenhuma decisão load-bearing aberta.
- O `--ref` aceita sha, branch ou tag; entregar sha cru vs. sha curto vs. a branch é cosmético e
  se resolve na hora de escrever o template do relatório.
- Não validado contra `lexflow --help` real: o shim da CLI nesta máquina aponta pra um Python
  removido. Todo o conhecimento de CLI aqui vem da **fonte** (`cli.py`, `manifest.py`,
  `deploy.py`, README do `lexflow-deploy-cli`), que é mais confiável que `--help` de qualquer
  forma, mas a versão instalada no time pode estar atrás do `main`.
