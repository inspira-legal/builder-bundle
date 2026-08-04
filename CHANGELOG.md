# Changelog

## 2.1.0 — 2026-07-31

O `/bb:brisar` passa a cobrir o **duplo diamante inteiro**. Antes ele começava no
scaffold: o builder chegava com uma ideia e saía com uma tela, sem nenhuma etapa
entre as duas além do próprio repertório dele. O primeiro diamante — pesquisar o
espaço antes de desenhar dentro dele — não existia em skill nenhuma do bundle.

Nada foi removido e nenhuma fase existente mudou de contrato. As fases 0–3
(calibração, intake, maturity gate, scaffold) seguem iguais.

### Novo — o primeiro diamante

- **`references/phase-research.md`** — pesquisa antes do pixel, em subagentes
  paralelos. **Piso que roda em qualquer modo:** bench de mercado (Mobbin),
  o design system **lido da fonte** (não da memória, não de cópia congelada), e
  a resposta explícita pra "precisa de componente novo?". **Discricionário, e
  declarado:** vieses comportamentais com proveniência (fonte primária ou
  `[não verificado]`), heurísticas, modelos mentais, e "o que o produto já tem
  pra mostrar" (assets no repo, dado que existe de fato, copy viva no i18n,
  locales). O modo (`pocket`/`full`) é julgado, não perguntado — e o que foi
  pulado é dito em voz alta. Corte silencioso se lê como cobertura completa.
- **`references/brief.md`** — o design brief como **contrato vivo** em
  `.bb/tasks/<slug>/brief-design.md`, registrado em `gate.design_brief`.
  Atualizado a cada rodada sem ser pedido, e no fim vira delta pro spec.
  Traz a **reconciliação obrigatória** contra o enquadramento do
  `/bb:discover` — _confirma · contradiz · não alcança_ — e a **leitura em
  chat** como parte da entrega, não cortesia.
- **`references/phase-diverge.md`** — direções **em pé de igualdade**. Cada uma
  com cinco partes obrigatórias (aposta · composição · copy prevista · racional
  ancorado na pesquisa · risco e custo), depois de declarar a base comum a
  todas. Recomendar é permitido; descrever uma em detalhe e as outras num
  parágrafo, não — o check de tratamento igual **bloqueia o gate**.
- **`references/phase-medium.md`** — o meio virou **pergunta**: código, Claude
  design, Figma, Paper ou Pencil, oferecendo só o que o preflight detecta e
  **nomeando** o que falta. O brief serve os cinco; só o build muda. Meio de
  canvas pula o scaffold, e canvas-primeiro-código-depois é caminho normal, não
  reinício.

### Mudou — o segundo diamante ficou medium-aware e a review, sênior

- **Develop** lê `medium.chosen` e constrói no meio escolhido. Passa a gravar um
  **locator preciso** por surface × variante (arquivo, ou arquivo + página +
  pranchas) e as **deviations** conscientes — sem isso o Deliver não consegue
  abrir nem julgar o que foi feito.
- **Deliver** ganhou o que faltava:
  - **lê o artefato de qualquer meio** (arquivos, preview, MCP do Paper/Figma/
    Pencil). Antes o input era literalmente "HTML/React em `src/`": quem
    desenhou num canvas não tinha o que ele abrisse;
  - **a unidade de review é surface × variante**, não surface. É nos deltas
    entre variantes que o contrato é violado;
  - **sete lentes** em vez de quatro. As três novas: **copy lida palavra por
    palavra** (rótulo que nomeia processo inexistente, claim que a fonte não
    sustenta, erro de português no herói), **contraste calculado como número**
    contra o mínimo da WCAG, e a **triangulação**;
  - **triangulação problema × pesquisa × construído.** O `gate.design_brief`
    **soma** ao `gate.discover_brief`, nunca substitui. Três perguntas: o
    construído honra a pesquisa? a pesquisa honra o problema? onde discordam,
    quem está errado? A resposta pode ser **o enquadramento**;
  - **severidade `divergência`** — o build está fiel e a review discorda de uma
    decisão do brief ou do spec. Nunca bloqueia; abre decisão, e exige o
    argumento (sem ele é preferência, e preferência não entra em review);
  - **delta pro spec** no handoff: o contrato alcança o que o design aprendeu.
- **`preflight-tooling.md`** — detecta `paper`/`figma`/`pencil`/`mobbin`, e passa
  a ler os **dois escopos** de `mcpServers` (global e de projeto). Servidor
  configurado só pro diretório atual não aparecia no topo e era reportado como
  ausente — o que removia silenciosamente um meio que o builder tinha.
- **Retomada** — um `brief-design.md` no disco é sinal de retomada por si só, com
  ou sem sessão. O brisar continua de onde o brief parou e **nunca re-roda a
  pesquisa por cima de um brief existente**.

### Postura preservada de propósito

A editorial stance do Deliver não mudou: só sinaliza o que importa, todo issue vem
com solução, **um elogio específico** ("não é torcida, é informação"),
não-bloqueante quando falta contexto, review e a11y em arquivos separados. O que
mudou foi o alcance das lentes, não o tom.

E uma regra nova que atravessa tudo: **legibilidade é requisito do artefato.** O
público não é só designer. Ponteiro interno carrega o significado no primeiro uso,
conceito de design ganha glosa de 5–10 palavras. Denso é bom; precisar de
decodificador não.

## 2.0.0 — 2026-07-23

O plugin `ofc` (Oficina) virou o **Builder Bundle** (`bb`): 28 skills de 4 fontes
(ofc, bundle brisar, cópias da loja inspira-skills, inspira-code-review)
consolidadas em **16 skills** organizadas em 6 trilhas. Repo renomeado de
`inspira-legal/ofc-skills` pra `inspira-legal/builder-bundle` (o GitHub
redireciona o nome antigo).

### Migrando do ofc

O marketplace deste repo agora lista **só o plugin `bb`** — a entrada `ofc` foi
removida de propósito (quebra de major). Consequências:

- **`claude plugin update` do ofc antigo falha.** É o comportamento esperado:
  não existe mais `ofc` pra atualizar. Migre assim:

  ```bash
  claude plugin uninstall ofc@inspira-legal
  claude plugin marketplace add inspira-legal/builder-bundle
  claude plugin install bb@inspira-legal
  ```

- **Coexistência ofc + bb funciona, mas não fique nela.** Os prefixos são
  distintos (`/ofc:` e `/bb:`), então nada quebra — porém os dois plugins têm
  hook `SessionStart`, e você passa a injetar contexto operacional **em dobro**
  em toda sessão. Desinstale o ofc primeiro.
- **Briefs antigos precisam ser movidos.** O único caminho lido agora é
  `.bb/tasks/<slug>/spec.md` — não há fallback pro `.ofc/`. Migre com:

  ```bash
  git mv .ofc/tasks .bb/tasks
  find .bb/tasks -name shape.md -execdir git mv shape.md spec.md \;
  ```

- **Env var da routine: `BB_UNATTENDED`** — a antiga `OFC_UNATTENDED` não é mais
  lida. Atualize a Cloud Routine pra definir a nova e rodar `/bb:delegate`.
- **Marcador do sticky comment do maintain-repo mudou de `ofc:` pra `bb:`** —
  o `/bb:maintain-repo` não reconhece o comment antigo e cria um novo; apague o
  sticky antigo do `/ofc:maintain-repo` no repo triado.
- **Skill customizada gerada pelo code-review-setup antigo** continua
  funcionando isolada no repo dela, mas recomendamos remover e usar
  `/bb:review` + `/bb:review-setup` (que agora gera só o `CODE_REVIEW_GUIDE.md`,
  sem skill por repo).

### De-para: 28 skills → 16

| origem              | skill antiga            | destino no bb                                                 |
| ------------------- | ----------------------- | ------------------------------------------------------------- |
| ofc                 | `frame-problem`         | `/bb:discover` (fase de enquadramento)                        |
| ofc                 | `assess-fit`            | `/bb:discover` (fase de fit)                                  |
| brisar              | `nise`                  | `/bb:discover` (material de descoberta)                       |
| brisar              | `esperanca`             | `/bb:discover` (material de hipótese)                         |
| loja                | `desafio`               | `/bb:challenge` (renomeada)                                   |
| loja                | `think`                 | `/bb:think` (base do método)                                  |
| ofc                 | `answer-yourself`       | `/bb:think` (modo take: veredito direto)                      |
| ofc                 | `legal-lens`            | `/bb:legal-lens`                                              |
| ofc                 | `shape`                 | `/bb:spec` (o método veio daqui)                              |
| loja                | `spec`                  | `/bb:spec` (formato de export em `references/export-spec.md`) |
| ofc                 | `implement`             | `/bb:implement`                                               |
| ofc                 | `ship`                  | `/bb:ship`                                                    |
| ofc                 | `delegate`              | `/bb:delegate`                                                |
| ofc                 | `gather-branch-context` | `/bb:gather-branch-context`                                   |
| ofc                 | `review-changes`        | `/bb:review` (fonte diff)                                     |
| ofc                 | `tidy`                  | `/bb:review` (passada de qualidade)                           |
| ofc                 | `tidy-pr`               | `/bb:review` (fonte threads)                                  |
| loja                | `pr-review`             | `/bb:review`                                                  |
| loja                | `fix-ci`                | `/bb:review` (fonte CI, absorvida)                            |
| ofc                 | `maintain-repo`         | `/bb:maintain-repo`                                           |
| inspira-code-review | `code-review-setup`     | `/bb:review-setup`                                            |
| inspira-code-review | `code-review-update`    | `/bb:review-setup` (update absorvido)                         |
| brisar              | `brisar`                | `/bb:brisar`                                                  |
| brisar              | `tarsila`               | `/bb:brisar` (fase Develop)                                   |
| brisar              | `clarisse`              | `/bb:brisar` (fase Deliver)                                   |
| loja                | `ui-accessibility`      | `/bb:ui-accessibility`                                        |
| ofc                 | `code-deep-research`    | `/bb:code-deep-research`                                      |
| ofc                 | `write-readme`          | `/bb:write-readme`                                            |

### Arquitetura do bundle

- **Progressive disclosure** em toda skill fundida: `SKILL.md` enxuto que
  roteia; o material de cada fase/modo vive em `references/` e carrega só
  quando a fase roda.
- **Handoff gates**: skill com próximo passo natural termina num
  `AskUserQuestion` que sugere a próxima trilha — sugere, nunca auto-invoca
  (exceção: `delegate` e o auto-chain implement→ship quando pré-autorizado).
  Convenção única em `plugins/bb/references/handoff-gate.md`.
- **Manifesto em runtime**: `implement`, `ship`, `review` e `review-setup`
  consultam `inspira-legal/manifesto` pra decisões de stack; sem acesso, seguem
  os padrões do repo atual e avisam.
- **Motor de review compartilhado** entre `ship` e `review` em
  `plugins/bb/references/` + `scripts/` — papéis distintos, motor único.

O histórico anterior a 2.0.0 (plugin `ofc` até a 1.16.0) vive no git log deste
repo.
