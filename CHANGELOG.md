# Changelog

## 2.1.0 — 2026-08-05

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

### Quando a ferramenta não está lá — degradar sem mentir

O piso da pesquisa é inegociável, o que significa que ele precisa de um caminho
quando a ferramenta falta. Antes esse caminho era uma frase ("degrada e diz qual
frente"), então o piso rodava e o resultado piorava sem que ninguém soubesse
quanto.

- **Front A sem Mobbin** — escada explícita, e o primeiro degrau é decidir se a
  tela é **pública ou atrás de login**, porque isso define quais degraus existem.
  **Atrás de login — que é a maior parte de um produto** (paywall, expiração,
  modal de upgrade, empty state, onboarding pós-signup): o app do concorrente
  **não é fonte**, e a skill não planeja em cima de entrar nele — brisar não cria
  conta nem faz login. Sobram **galerias públicas por `site:`** (Land-book, SaaS
  Landing Page, Refero, Pageflows, Nicelydone — algumas indexam fluxo gravado em
  vez de frame solto, o que é o substituto mais próximo de tela logada),
  **os prints que o builder já tem** (maior sinal por token, e o degrau mais
  pulado por educação), **o precedente do próprio produto**, e só então busca
  genérica. **Público — landing, preço, site institucional:** aí o
  navegador ganha o lugar dele, com a ressalva de que lê a superfície de
  _marketing_ e não diz nada sobre como a plataforma se comporta por dentro.
  E uma obrigação **aperta**: achado negativo agora vai com **o tamanho e a
  origem do corpus**, ou não vai. "Nenhuma das 18 telas usa urgência" só pesa se
  as 18 não foram entregues por um ranqueamento.
- **Front B: "não está no cwd" não é "não está no disco".** Degrau novo **antes**
  do remoto — procurar o repo no resto da máquina (`mdfind` no macOS, `find` como
  portátil, sempre excluindo `node_modules`), buscando **o artefato e não o nome
  do repo**, porque a pasta pode se chamar qualquer coisa. Era o buraco mais bobo
  e mais caro: brisar rodado de uma pasta vizinha declarava o repo ausente com o
  arquivo ali do lado, degradando três frentes sem motivo. E este degrau vale
  **mais** que o remoto — lê source de verdade, então recupera o inventário de
  componentes e o "quantos lugares usam isso" que o remoto não dá. Com duas
  ressalvas: confirmar que o hit é o checkout certo (worktree velho ou cópia
  vendorizada responde com confiança e errado) e mais de um hit plausível é
  pergunta pro builder, não moeda ao ar.
- **E quando o `gh` não está disponível** — que não é caso de borda: pode não
  estar instalado, não estar autenticado, ou estar numa conta sem acesso ao repo
  privado. Esse caminho ficou desenhado em vez de encolhido: procurar no disco
  **antes** de oferecer autenticação · oferecer `gh auth login` (nunca rodar
  sozinho — é autenticação, e é do builder) · **perguntar ao builder onde está**,
  que é a resposta mais barata e a mais pulada por reflexo de autossuficiência ·
  pedir **o arquivo de regras do próprio repo** em vez dos tokens, que é melhor
  porque é orientação autoral e **continua certa quando os caminhos mudam** · e só
  então o pacote de marca, com o gap declarado.
- **Onde os caminhos devem morar — e não é dentro da skill.** Cravar o caminho de
  token de um produto no plugin deixa o plugin errado no dia do refactor. Dois
  lares melhores, nessa ordem: **o arquivo de regras do repo do produto** (é a
  única coisa capaz de manter aquilo verdadeiro) e o `ds_source` do
  `product-registry.yaml`, ou um `.brisar/config.yaml`/`BRISAR_DS_PATH` pra
  override por máquina. Quando a busca dá trabalho, a skill **sugere registrar**
  — a próxima rodada não deve repetir a procura.
- **Front B sem o repo em lugar nenhum** — degrau remoto: **ler o repo
  via `gh`**, sem clonar. Duas chamadas: a **árvore inteira** de
  caminhos (`git/trees/HEAD?recursive=1`) como mapa, e `contents` pra ler os
  arquivos que o mapa apontou. Resolve o caso comum — `gh` autenticado, repo não
  está aqui — e cobre **token e copy viva no i18n**. O que **não** cobre: o
  inventário de componentes com as armadilhas (a semântica real de um componente
  exige varredura de source, não duas leituras) e "quantos lugares usam isso".
  **Não use `gh search code`:** ele tem orçamento de **10 requisições por minuto**,
  um fan-out de subagentes esgota numa rodada, o 403 volta vazio — igualzinho a
  "não achei" — e o qualificador `path:` não aceita glob, então query razoável
  retorna zero e se lê como ausência. A árvore fica no orçamento normal de
  5.000/hora, vem completa numa chamada e é grepável localmente; quando
  `truncated: false`, **ausência de caminho é conclusiva**. brisar **não clona por
  conta própria** — repo privado da empresa no computador de alguém é decisão do
  builder.
- **O fallback empacotado parou de se passar por design system.** O
  `references/ds/brand/` é **pacote de marca** — voz, princípios, significado de
  cor, uso de logo. O `tokens.json` dele é artefato de marca e **não** é o
  vocabulário de token de produção. Continua servindo pra intenção visual;
  parou de ser apresentado como token lido da fonte, o que gerava classe que a
  codebase não tem.
- **A linha de modo ganhou uma quarta parte: o que a degradação invalida.**
  Nomear a ferramenta que faltou não informa nada. "Não li o token da fonte,
  então os valores são de segunda mão, o inventário de componentes não existe, e
  não verifiquei se essa página já está em produção" informa o que não confiar.

### Não designer — o contrato da calibração passou a valer nas fases novas

A Phase 0 define um vocabulário proibido pro perfil `executive` (`scaffold`,
`embed`, `npm`, `MCP`, `repo`, `branch`, `slug`) e as quatro fases novas do
primeiro diamante não o honravam — nenhuma delas lia `profile.persona_id`.

- **As fases se nomeiam pelo resultado, não pelo método.** "Monto 2 ou 3 caminhos
  diferentes e você escolhe" no lugar de "divergir em direções". Quem não é
  designer não tem por que saber o que é divergência — e o gate pedia justamente
  que ele escolhesse isso.
- **A pergunta do meio vende a consequência, não a ferramenta.** Ninguém sem
  repertório escolhe entre Paper e Figma; escolhe entre "ver rápido", "mostrar e
  receber comentário" e "isso vai pra produção". `MCP` saiu do texto de usuário.
- **A recomendação virou obrigatória** pros perfis `executive` e `content`. N
  caminhos no mesmo nível de detalhe e nenhum critério não é neutralidade: é
  entregar o julgamento mais difícil do fluxo pra quem tem menos repertório, e o
  resultado costuma ser escolher o primeiro. Não afrouxa o tratamento igual — a
  regra proíbe **descrição assimétrica**, nunca recomendação declarada.
- **E o contrato de vocabulário ganhou verificação mecânica.** A regra de perfil
  era aspiracional — dois lugares diziam "escreva pra quem não é designer" e nada
  checava. Agora o self-check antes de apresentar tem **duas passadas com alvo
  zero**: ponteiro pelado (já existia) e, quando o perfil é `executive`/`content`,
  o vocabulário proibido **mais os nomes do próprio método** (`divergência`,
  `reconciliação`, `piso`, `pocket`/`full`) — cada ocorrência **substituída** pelo
  que significa, nunca anotada. Regra com check é seguida; regra com adjetivo
  deriva, e foi exatamente assim que o contrato passou batido por quatro fases.

### A leitura em chat ficou mais curta sem ficar mais pobre

Legibilidade tinha self-check mecânico e concisão tinha só adjetivo, então o texto
tinha viés estrutural pra inflar — glosar, expandir ponteiro e citar evidência
todos empurram pra cima. Três testes de necessidade, mais um self-check simétrico:
cada bloco existe pra habilitar **uma decisão ou uma opinião**; o achado viaja com
**a consequência, não com o percurso**; e a **evidência mora no documento, o chat
carrega a conclusão**. E **o chat apresenta o delta quando quem lê já leu** —
"assuma que ninguém leu" é verdade pro stakeholder e falso pro builder na quarta
rodada do brief que ele ajudou a escrever. O discriminador é **o leitor, não o
número da rodada**: apresentar pra alguém novo é rodada 1 pra essa pessoa, e a
leitura inteira volta.

E o empate entre as duas regras ficou resolvido em vez de implícito:
**legibilidade ganha.** Frase que o leitor não decodifica custa a ele o ponto
inteiro; frase dez palavras mais longa custa dez palavras. Então a glosa fica e o
ponteiro fica expandido, sempre — e a concisão passa a mirar outro lugar: **corta
itens inteiros, não as palavras dentro deles.** Concisão decide **o que** entra na
leitura, legibilidade decide **como** cada coisa sobrevivente é escrita. Encurtar
raspando glosa é o único movimento que falha nas duas ao mesmo tempo.

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
