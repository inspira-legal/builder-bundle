---
status: in-progress
created: 2026-07-23
slug: builder-bundle
---

# Builder Bundle — unificação das skills de builder num plugin só

## what

Transformar este repo (ex-`ofc-skills`, já renomeado no GitHub pra `inspira-legal/builder-bundle`) no **Builder Bundle**: o plugin unificado de skills pra builders da Inspira, aprovado em reunião de 23/07/2026. Consolida 28 skills (ofc 15 + brisar bundle + cópias soltas da loja `inspira-skills` + inspira-code-review) em **16 skills** organizadas em 6 trilhas, invocadas como `/bb:<skill>`.

Trilhas e skills finais:

- **Pensar**: `discover`, `challenge`, `think`, `legal-lens`
- **Desenhar**: `spec`
- **Construir**: `implement`, `ship`, `delegate`, `gather-branch-context`
- **Revisar**: `review`, `maintain-repo`, `review-setup`
- **Design**: `brisar`, `ui-accessibility`
- **Pesquisar/Doc**: `code-deep-research`, `write-readme`

## why

Hoje há 4 lugares com skills sobrepostas (ofc, brisar, loja, inspira-code-review), com duplicação, coisas quebradas (codenavi) e desatualizadas. Quem está aprendendo não sabe o que usar. Um plugin só, opinativo, com uma skill por verbo e modos por variação, dá localização ("onde estou na jornada?") e faz qualquer extensão futura acontecer _dentro_ do bundle em vez de virar mais um plugin. Decisões validadas pelo time na reunião (nome Builder Bundle, fusões, renames, manifesto como fonte).

## decisions

- **Prefixo de invocação: `bb`** (`/bb:spec`, `/bb:brisar`). Plugin name no `plugin.json` = `bb`; dir `plugins/ofc` → `plugins/bb`; marketplace continua `inspira-legal`; versão **2.0.0**. O marketplace.json passa a listar **só `bb`** — a entrada `ofc` é removida (quebra intencional de major; quem tem ofc instalado migra via nota no CHANGELOG, sem entrada dupla de transição).
- **Estado em disco: `.bb/tasks/<slug>/spec.md`** (novo padrão). `delegate`/`implement` leem `.ofc/tasks/<slug>/shape.md` como **fallback legado** (só leitura/atualização in-place quando não existe `.bb/` pro mesmo slug; escrita nova sempre em `.bb/`). Se o mesmo slug existir nos dois, `.bb/` vence.
- **Idioma híbrido**: corpo das instruções em inglês (padrão ofc, base do método); descriptions, triggers e todo texto visto pelo usuário (perguntas de gates, relatórios) em PT-BR.
- **Manifesto em runtime**: `implement`, `ship`, `review` e `review-setup` (lista canônica; `delegate` herda via implement→ship) consultam `inspira-legal/manifesto` via `gh api` quando precisam decidir stack. Fallback gracioso: sem acesso, segue padrões do repo atual e **avisa** que não consultou o manifesto (nunca inventa stack).
- **6 fusões** (regra geral de conflito: método do ofc vence, conteúdo das outras fontes vira reference):
  1. `discover` ← frame-problem + assess-fit (ofc) + nise + esperanca (brisar). Primeiro diamante inteiro. Contrato de saída: escreve as seções upstream (`## problem`/`## hypothesis`/`## fit`/`## cuts`) em `.bb/tasks/<slug>/spec.md`, que o `spec` lê como intenção — mesmo contrato do frame-problem/assess-fit hoje, só mudando o path.
  2. `think` ← think (loja) + answer-yourself (ofc). Exceção nomeada à regra geral: a base do método é o think da loja (parceiro de raciocínio); answer-yourself entra como modo "take" (veredito direto quando pedem julgamento).
  3. `review` ← review-changes + tidy + tidy-pr (ofc) + pr-review (loja) + fix-ci (loja, `skills/github-management/fix-ci`). 3 fontes: diff + threads da PR + CI; lê `CODE_REVIEW_GUIDE.md`; **modo interativo**: reporta, pergunta o que aplicar, aplica os fixes escolhidos, responde/resolve threads (comportamento tidy-pr absorvido) e re-reporta.
  4. `spec` ← shape (ofc) + spec (loja). Método do shape (mapa de comportamento, revisor adversarial, gate 3-vias); nome do spec; formato de export do spec original vira `references/export-spec.md`.
  5. `brisar` ← brisar + tarsila + clarisse (fases Develop/Deliver internas via references; nise/esperanca foram pro discover). Mantém `references/ds/` da marca.
  6. `review-setup` ← code-review-setup + code-review-update (inspira-code-review). Output só o guia `CODE_REVIEW_GUIDE.md` — **não** gera mais skill customizada por repo.
- **2 renames**: desafio → `challenge`; shape → `spec`.
- **Regras de arquitetura do bundle**:
  - **Progressive disclosure obrigatório em skill fundida**: SKILL.md enxuto que roteia; material de cada fase/modo em `references/`, carregado só quando a fase roda. Nunca SKILL.md monolítico.
  - **Handoff-gate**: toda skill com próximo passo natural termina com `AskUserQuestion` oferecendo a próxima; "encerrar aqui" sempre é opção; **sugere, nunca auto-invoca** (exceção única: `delegate`, e o auto-chain implement→ship quando o ship já foi autorizado). Formato único em `references/handoff-gate.md`. Sem gate: legal-lens, maintain-repo, review-setup, write-readme, code-deep-research, gather-branch-context, ui-accessibility.
  - **Motor de review compartilhado** entre `ship` e `review` em `references/` + `scripts/` (2 passadas, régua de severidade, CI/threads) — papéis distintos (ship automático landa; review interativo reporta), motor único pra evitar drift. Scripts existentes (`fetch_comments.py`, `reply_resolve_thread.py`, `gather_context.py`) reutilizados.
- **Reuso**: skills do ofc que seguem quase intactas — implement, ship, delegate, gather-branch-context, legal-lens, maintain-repo, code-deep-research, write-readme (ajustes: paths `.bb/`, referências shape→spec, manifesto, gates, identidade bb). Hooks do ofc (SessionStart operating-context etc.) mantidos com textos atualizados.
- **Fontes de importação**: repo `inspira-skills` local em `C:\Users\PC\development\inspira-skills` (skills/brisar/_, skills/desafio, skills/think, skills/spec, skills/pr-review, skills/ui-accessibility, skills/inspira-code-review/_, skills/github-management/fix-ci).
- **Validação só via CI/PR** (`gh pr checks --watch`) — nunca rodar checks localmente. Lefthook/bun existentes mantidos.
- **Migração documentada**: README + CHANGELOG com nota ofc→bb (desinstalar `ofc@inspira-legal`, instalar `bb@inspira-legal`; GitHub redireciona o nome antigo do repo).

## out of scope

- Despublicar/deprecar as cópias da loja `inspira-skills` (spec, think, desafio, pr-review, ui-accessibility, brisar bundle, inspira-code-review, tlc-spec-driven, codenavi) — _revisit_: PR separado no repo inspira-skills depois que o bb publicar.
- Gerenciador de tarefas / backlog compartilhado / session log→git — _revisit_ (v2, "arredores do plugin").
- Memória organizacional OKF (elephant) — _revisit_ (plugin irmão).
- Mobbin MCP como modo do brisar — _revisit_ (Matheus explora).
- Design system / monorepo — fórum separado do Léo.
- Distribuição org-level (admin instala pra todos) — decidir depois; v1 via marketplace.

## design

- **Layout**: `plugins/bb/{skills/<16>/,references/,scripts/,hooks/}`. References compartilhadas no nível do plugin (handoff-gate.md, quality/review checklists, motor de review); references por skill dentro de cada `skills/<name>/references/` (fases do brisar, modos do discover, export-spec).
- **Fluxo da jornada** (o que os gates encadeiam): dor/ideia → `discover` (apoios: challenge, think, legal-lens) → _é código_ → `spec` → `implement` → `ship` → `review` da PR; _é design_ → `brisar` → volta pro `spec`. `think` só oferece gate quando convergiu; `challenge` devolve pro dono da tese.
- **Contrato do estado**: `.bb/tasks/<slug>/spec.md` com o mesmo frontmatter de hoje (`status/created/slug`). Fallback de leitura documentado num único lugar (reference compartilhada) e usado por **spec, implement e delegate** (a Cloud Routine passa pelo delegate, então herda).
- **Manifesto**: um snippet/reference compartilhado ("consult-manifesto") incluído pela lista canônica acima (implement, ship, review, review-setup) — busca `gh api repos/inspira-legal/manifesto/...`, aplica níveis Obrigatório/Padrão/Alternativa/Proibido, fallback com aviso.

## behavior

Happy path:

1. Time roda `claude plugin marketplace add inspira-legal/builder-bundle` e `claude plugin install bb@inspira-legal` → instala, `/bb:` lista as 16 skills.
2. `/bb:discover` roda o primeiro diamante (frame + fit, com material nise/esperanca por fase) → gate oferece spec / brisar / challenge / encerrar.
3. `/bb:spec <ideia>` roda o método do shape, escreve `.bb/tasks/<slug>/spec.md`, gate 3-vias implement/delegate/parar.
4. `/bb:implement` lê o spec, constrói por slices, oferece ship.
5. `/bb:ship` quality pass (motor compartilhado), gate verde, landa, vigia CI e threads; nunca merge.
6. `/bb:review <PR|branch>` junta diff + threads + CI + CODE_REVIEW_GUIDE.md, reporta e pergunta o que aplicar.
7. `/bb:brisar` roteia fases Develop (tarsila) / Deliver (clarisse), carregando o reference da fase; ao entregar, gate oferece ui-accessibility / spec.
8. `implement`/`ship`/`review`/`review-setup` consultam o manifesto em runtime pra decisões de stack.

Edges (WHEN → THEN):

- WHEN projeto tem `.ofc/tasks/x/shape.md` pendente e roda `/bb:delegate` THEN o brief legado é encontrado (fallback), executado e atualizado in-place; nada é movido.
- WHEN o mesmo slug existe em `.bb/` e `.ofc/` THEN `.bb/` vence; o legado é ignorado com aviso.
- WHEN manifesto inacessível (offline, sem `gh` auth) THEN a skill segue os padrões do repo atual e avisa que não consultou o manifesto — nunca inventa stack.
- WHEN usuário responde "encerrar aqui" num handoff-gate THEN nada é auto-invocado.
- WHEN `/bb:review` roda numa branch sem PR THEN funciona só com a fonte diff (threads/CI ausentes não quebram, reporta que só analisou o diff).
- WHEN `CODE_REVIEW_GUIDE.md` não existe THEN `review` roda com o motor genérico e sugere `/bb:review-setup`; review-setup num repo que já tem guia atualiza (comportamento do code-review-update absorvido).
- WHEN repo tem a skill customizada gerada pelo code-review-setup antigo THEN ela continua funcionando isolada; nota de migração recomenda remover e usar `/bb:review`.
- WHEN delegate roda unattended (`OFC_UNATTENDED`→renomear env var pra `BB_UNATTENDED` com fallback) THEN nunca merge (capability scoping mantido) e o auto-chain implement→ship se aplica.
- WHEN usuário tenta `/ofc:<skill>` após migrar THEN não existe; README/CHANGELOG documentam o de-para completo (15 ofc → destino no bb).
- WHEN skill fundida roda uma fase THEN só o reference daquela fase é carregado (progressive disclosure verificável no SKILL.md).
- WHEN usuário instala bb sem desinstalar ofc THEN os dois convivem (prefixos distintos) mas os hooks SessionStart injetam contexto em dobro; nota de migração manda desinstalar ofc primeiro.
- WHEN quem tem ofc instalado roda `claude plugin update` THEN falha (marketplace.json lista só `bb`) — comportamento esperado do major 2.0.0, documentado no CHANGELOG; sem entrada dupla de transição.

## tasks

- [x] 1. Scaffold: `plugins/ofc`→`plugins/bb`, plugin.json (name bb, 2.0.0, descrição PT-BR), marketplace.json só com `bb`, README raiz, hooks com textos atualizados, env var `BB_UNATTENDED` (fallback `OFC_UNATTENDED`) — comportamentos: instalação/listagem (1); edges de migração (coexistência, update)
- [x] 2. Convenções compartilhadas: `references/handoff-gate.md`, reference do contrato de estado `.bb/`+fallback, reference consult-manifesto, guideline de progressive disclosure no CONTRIBUTING — comportamentos: gates (2, 7); edges: encerrar-aqui, legado, slug-duplicado, manifesto-inacessível, disclosure
- [x] 3. Trilha Desenhar: `spec` (shape renomeado + `references/export-spec.md` + escrita em `.bb/`) — comportamento 3
- [x] 4. Trilha Construir: `implement`, `delegate` (fallback legado), `ship`, `gather-branch-context` com paths/identidade/manifesto/gates — comportamentos 4, 5, 8; edges: legado, slug-duplicado, unattended
- [x] 5. Trilha Revisar: `review` (fusão, 3 fontes, interativo), `review-setup` (fusão, guia-only), `maintain-repo`; motor compartilhado extraído pra references/scripts — comportamentos 5, 6; edges: review-sem-PR, guia-ausente, skill-customizada-antiga
- [x] 6. Trilha Pensar: `discover` (fusão 4 fontes), `challenge` (desafio importado + renomeado), `think` (fusão answer-yourself), `legal-lens` — comportamento 2
- [x] 7. Trilha Design: `brisar` (tarsila/clarisse como fases em references, mantém `references/ds/`), `ui-accessibility` importada — comportamento 7
- [x] 8. Pesquisar/Doc + docs finais: `code-deep-research`, `write-readme` (identidade bb); CHANGELOG + nota de migração ofc→bb com de-para das 28→16, aviso de coexistência ofc+bb e quebra do `plugin update` — comportamento 1, edges de migração (de-para, coexistência, update)
- [ ] 9. PR única (branch → PR → CI verde via `gh pr checks --watch`); validação de conteúdo das fusões contra `analise-skills-ofc-brisar.md` e `mapa-casos-de-uso-skills.md` como checklist

## open

- Sigla/branding "BB" no README (Léo quer explorar) — não bloqueia; nome do plugin já é `bb`.
- Distribuição org-level — decidir fora deste trabalho.
