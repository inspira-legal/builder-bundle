---
status: done
created: 2026-07-23
slug: builder-bundle
---

# Builder Bundle — unificação das skills de builder num plugin só

Transformar este repo (ex-`ofc-skills`, já renomeado no GitHub pra
`inspira-legal/builder-bundle`) no **Builder Bundle**: o plugin unificado de skills pra
builders da Inspira, aprovado em reunião de 23/07/2026. Consolida 28 skills (ofc 15 +
brisar bundle + cópias soltas da loja `inspira-skills` + inspira-code-review) em **16
skills** organizadas em 6 trilhas, invocadas como `/bb:<skill>`.

Hoje há 4 lugares com skills sobrepostas (ofc, brisar, loja, inspira-code-review), com
duplicação, coisas quebradas (codenavi) e desatualizadas. Quem está aprendendo não sabe o
que usar. Um plugin só, opinativo, com uma skill por verbo e modos por variação, dá
localização ("onde estou na jornada?") e faz qualquer extensão futura acontecer _dentro_
do bundle em vez de virar mais um plugin.

Sucesso: o time instala um plugin e sabe qual verbo usar em cada ponto da jornada.

## As 6 trilhas

- **Pensar**: `discover`, `challenge`, `think`, `legal-lens`
- **Desenhar**: `spec`
- **Construir**: `implement`, `ship`, `delegate`, `gather-branch-context`
- **Revisar**: `review`, `maintain-repo`, `review-setup`
- **Design**: `brisar`, `ui-accessibility`
- **Pesquisar/Doc**: `code-deep-research`, `write-readme`

## Como o bundle se organiza

- **Layout**: `plugins/bb/{skills/<16>/,references/,scripts/,hooks/}`. References
  compartilhadas no nível do plugin (handoff-gate.md, quality/review checklists, motor de
  review); references por skill dentro de cada `skills/<name>/references/` (fases do
  brisar, modos do discover, export-spec).
- **Fluxo da jornada** (o que os gates encadeiam): dor/ideia → `discover` (apoios:
  challenge, think, legal-lens) → _é código_ → `spec` → `implement` → `ship` → `review` da
  PR; _é design_ → `brisar` → volta pro `spec`. `think` só oferece gate quando convergiu;
  `challenge` devolve pro dono da tese.
- **Contrato do estado**: `.bb/tasks/<slug>/spec.md` com frontmatter `status/created/slug`.
  Documentado num único lugar (reference compartilhada) e usado por **spec, implement e
  delegate** (a Cloud Routine passa pelo delegate, então herda).
- **Manifesto**: um reference compartilhado ("consult-manifesto") incluído pela lista
  canônica (implement, ship, review, review-setup) — busca
  `gh api repos/inspira-legal/manifesto/...`, aplica níveis
  Obrigatório/Padrão/Alternativa/Proibido, fallback com aviso.

## Decisões

- **Prefixo de invocação: `bb`** (`/bb:spec`, `/bb:brisar`). Plugin name no `plugin.json` =
  `bb`; dir `plugins/ofc` → `plugins/bb`; marketplace continua `inspira-legal`; versão
  **2.0.0**. O marketplace.json passa a listar **só `bb`** — a entrada `ofc` é removida
  (quebra intencional de major; quem tem ofc instalado migra via nota no CHANGELOG, sem
  entrada dupla de transição).
- **Estado em disco: `.bb/tasks/<slug>/spec.md`** — caminho único, sem fallback legado.
  Briefs antigos são migrados na mão (documentado no CHANGELOG).
- **Idioma híbrido**: corpo das instruções em inglês (padrão ofc, base do método);
  descriptions, triggers e todo texto visto pelo usuário (perguntas de gates, relatórios)
  em PT-BR.
- **Manifesto em runtime**: `implement`, `ship`, `review` e `review-setup` (lista canônica;
  `delegate` herda via implement→ship) consultam `inspira-legal/manifesto` via `gh api`
  quando precisam decidir stack. Fallback gracioso: sem acesso, segue padrões do repo atual
  e **avisa** que não consultou o manifesto.
- **6 fusões** (regra geral de conflito: método do ofc vence, conteúdo das outras fontes
  vira reference):
  1. `discover` ← frame-problem + assess-fit (ofc) + nise + esperanca (brisar). Primeiro
     diamante inteiro. Contrato de saída: escreve as seções upstream
     (`## problem`/`## hypothesis`/`## fit`/`## cuts`) em `.bb/tasks/<slug>/spec.md`, que o
     `spec` lê como intenção.
  2. `think` ← think (loja) + answer-yourself (ofc). Exceção nomeada à regra geral: a base
     do método é o think da loja (parceiro de raciocínio); answer-yourself entra como modo
     "take" (veredito direto quando pedem julgamento).
  3. `review` ← review-changes + tidy + tidy-pr (ofc) + pr-review (loja) + fix-ci (loja,
     `skills/github-management/fix-ci`). 3 fontes: diff + threads da PR + CI; lê
     `CODE_REVIEW_GUIDE.md`; **modo interativo**: reporta, pergunta o que aplicar, aplica
     os fixes escolhidos, responde/resolve threads e re-reporta.
  4. `spec` ← shape (ofc) + spec (loja). Método do shape (mapa de comportamento, revisor
     adversarial, gate 3-vias); nome do spec; formato de export do spec original vira
     `references/export-spec.md`.
  5. `brisar` ← brisar + tarsila + clarisse (fases Develop/Deliver internas via references;
     nise/esperanca foram pro discover). Mantém `references/ds/` da marca.
  6. `review-setup` ← code-review-setup + code-review-update (inspira-code-review). Output
     só o guia `CODE_REVIEW_GUIDE.md` — **não** gera mais skill customizada por repo.
- **2 renames**: desafio → `challenge`; shape → `spec`.
- **Progressive disclosure obrigatório em skill fundida**: SKILL.md enxuto que roteia;
  material de cada fase/modo em `references/`, carregado só quando a fase roda.
- **Handoff-gate**: toda skill com próximo passo natural termina com `AskUserQuestion`
  oferecendo a próxima; "encerrar aqui" sempre é opção; **sugere, nunca auto-invoca**
  (exceção única: `delegate`, e o auto-chain implement→ship quando o ship já foi
  autorizado). Formato único em `references/handoff-gate.md`. Sem gate: legal-lens,
  maintain-repo, review-setup, write-readme, code-deep-research, gather-branch-context,
  ui-accessibility.
- **Motor de review compartilhado** entre `ship` e `review` em `references/` + `scripts/`
  (2 passadas, régua de severidade, CI/threads) — papéis distintos (ship automático landa;
  review interativo reporta), motor único pra evitar drift. Scripts existentes
  (`fetch_comments.py`, `reply_resolve_thread.py`, `gather_context.py`) reutilizados.
- **Reuso**: skills do ofc que seguem quase intactas — implement, ship, delegate,
  gather-branch-context, legal-lens, maintain-repo, code-deep-research, write-readme
  (ajustes: paths `.bb/`, referências shape→spec, manifesto, gates, identidade bb). Hooks
  do ofc (SessionStart operating-context etc.) mantidos com textos atualizados.
- **Fontes de importação**: repo `inspira-skills` local em
  `C:\Users\PC\development\inspira-skills` (`skills/brisar/*`, skills/desafio, skills/think,
  skills/spec, skills/pr-review, skills/ui-accessibility, `skills/inspira-code-review/*`,
  skills/github-management/fix-ci).
- **Validação só via CI/PR** (`gh pr checks --watch`) — nunca rodar checks localmente.
  Lefthook/bun existentes mantidos.
- **Migração documentada**: README + CHANGELOG com nota ofc→bb (desinstalar
  `ofc@inspira-legal`, instalar `bb@inspira-legal`; GitHub redireciona o nome antigo do
  repo).

## Comportamento

1. Time roda `claude plugin marketplace add inspira-legal/builder-bundle` e
   `claude plugin install bb@inspira-legal` → instala, `/bb:` lista as 16 skills.
2. `/bb:discover` roda o primeiro diamante (frame + fit, com material nise/esperanca por
   fase) → gate oferece spec / brisar / challenge / encerrar.
3. `/bb:spec <ideia>` roda o método, escreve `.bb/tasks/<slug>/spec.md`, gate 3-vias
   implement/delegate/parar.
4. `/bb:implement` lê o brief, constrói por slices, oferece ship.
5. `/bb:ship` quality pass (motor compartilhado), gate verde, landa, vigia CI e threads;
   nunca merge.
6. `/bb:review <PR|branch>` junta diff + threads + CI + CODE_REVIEW_GUIDE.md, reporta e
   pergunta o que aplicar.
7. `/bb:brisar` roteia fases Develop (tarsila) / Deliver (clarisse), carregando o reference
   da fase; ao entregar, gate oferece ui-accessibility / spec.
8. `implement`/`ship`/`review`/`review-setup` consultam o manifesto em runtime pra decisões
   de stack.

| WHEN                                           | THEN                                                                     |
| ---------------------------------------------- | ------------------------------------------------------------------------ |
| só há briefs no caminho antigo                 | `/bb:delegate` não acha nada; a migração manual está no CHANGELOG        |
| manifesto inacessível (offline, sem `gh`)      | segue os padrões do repo atual e avisa que não consultou                 |
| o usuário responde "encerrar aqui" num gate    | nada é auto-invocado                                                     |
| `/bb:review` roda numa branch sem PR           | funciona só com a fonte diff, e reporta que só analisou o diff           |
| `CODE_REVIEW_GUIDE.md` não existe              | review roda genérico e sugere `/bb:review-setup`; se existe, atualiza    |
| o repo tem a skill customizada do setup antigo | ela segue funcionando isolada; a nota de migração recomenda remover      |
| delegate roda sob `BB_UNATTENDED`              | nunca merge (capability scoping) e o auto-chain implement→ship se aplica |
| o usuário tenta `/ofc:<skill>` após migrar     | não existe; README/CHANGELOG têm o de-para completo (15 ofc → bb)        |
| uma skill fundida roda uma fase                | só o reference daquela fase é carregado                                  |
| instala bb sem desinstalar ofc                 | os dois convivem, mas os hooks injetam contexto em dobro                 |
| quem tem ofc roda `claude plugin update`       | falha — o marketplace lista só `bb`; esperado no major 2.0.0             |

## Tarefas

- [x] **1. Scaffold** — `plugins/ofc`→`plugins/bb`, plugin.json (name bb, 2.0.0, descrição
      PT-BR), marketplace.json só com `bb`, README raiz, hooks com textos atualizados, env
      var `BB_UNATTENDED` → behavior 1 · depende: — · verifica: CI
- [x] **2. Convenções compartilhadas** — `references/handoff-gate.md`, contrato de estado
      `.bb/`, consult-manifesto, guideline de progressive disclosure
      → behaviors 2, 7 · depende: 1 · verifica: CI
- [x] **3. Trilha Desenhar** — `spec` (shape renomeado + `references/export-spec.md` +
      escrita em `.bb/`) → behavior 3 · depende: 2 · verifica: CI
- [x] **4. Trilha Construir** — `implement`, `delegate`, `ship`, `gather-branch-context` com
      paths/identidade/manifesto/gates → behaviors 4, 5, 8 · depende: 2 · verifica: CI
- [x] **5. Trilha Revisar** — `review` (fusão, 3 fontes, interativo), `review-setup` (fusão,
      guia-only), `maintain-repo`; motor compartilhado extraído
      → behaviors 5, 6 · depende: 2 · verifica: CI
- [x] **6. Trilha Pensar** — `discover` (fusão 4 fontes), `challenge`, `think` (fusão
      answer-yourself), `legal-lens` → behavior 2 · depende: 2 · verifica: CI
- [x] **7. Trilha Design** — `brisar` (tarsila/clarisse como fases, mantém `references/ds/`),
      `ui-accessibility` → behavior 7 · depende: 2 · verifica: CI
- [x] **8. Pesquisar/Doc + docs finais** — `code-deep-research`, `write-readme`; CHANGELOG +
      nota de migração ofc→bb com o de-para 28→16 → behavior 1 · depende: 3-7 · verifica: CI
- [x] **9. PR única** — branch → PR → CI verde; conteúdo das fusões validado contra
      `analise-skills-ofc-brisar.md` e `mapa-casos-de-uso-skills.md`
      → behaviors 1-8 · depende: 8 · verifica: CI verde

## Fora de escopo

- Despublicar/deprecar as cópias da loja `inspira-skills` (spec, think, desafio, pr-review,
  ui-accessibility, brisar bundle, inspira-code-review, tlc-spec-driven, codenavi) —
  _revisit_: PR separado no repo inspira-skills depois que o bb publicar.
- Gerenciador de tarefas / backlog compartilhado / session log→git — _revisit_ (v2).
- Memória organizacional OKF (elephant) — _revisit_ (plugin irmão).
- Mobbin MCP como modo do brisar — _revisit_ (Matheus explora).
- Design system / monorepo — fórum separado do Léo.
- Distribuição org-level (admin instala pra todos) — decidir depois; v1 via marketplace.

## Em aberto

- Sigla/branding "BB" no README (Léo quer explorar) — não bloqueia; o nome do plugin já é
  `bb`.
- Distribuição org-level — decidir fora deste trabalho.
