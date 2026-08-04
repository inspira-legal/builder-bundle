# Changelog

## 2.2.0 — 2026-08-03

### `/bb:review` virou sete frentes que você escolhe

O `review` fazia muita coisa de uma vez: rodava diff, threads e CI em sequência
sem perguntar, e o que era "regra do projeto" ficava diluído dentro das lentes de
correção e qualidade. Agora ele **detecta o que dá pra revisar nessa branch e
pergunta quais frentes rodar**:

| frente        | o que procura                                                           |
| ------------- | ----------------------------------------------------------------------- |
| `correctness` | bugs no diff, em 2–5 ângulos nomeados                                   |
| `quality`     | reuso, simplificação, peso morto, eficiência, altitude, consistência    |
| `rules`       | desvios do `CODE_REVIEW_GUIDE.md` e dos `CLAUDE.md` que governam o diff |
| `contract`    | o mapa `## behavior` do brief como contrato de aceite                   |
| `a11y`        | WCAG AA no que o diff mexeu na UI — estático, sem browser               |
| `threads`     | comentários de review não resolvidos da PR                              |
| `ci`          | checks vermelhos — evidência antes de editar                            |

A pergunta oferece só as frentes disponíveis (sem PR aberta não existe `threads`
nem `ci`; sem brief não existe `contract`; sem arquivo de UI no diff não existe
`a11y`), e diz a profundidade que o diff resolveu antes de gastar agente.

### Execução em paralelo, com verificação independente

As frentes escolhidas viram um fan-out de agentes read-only numa mensagem só —
eles reportam candidatos, nunca editam; o contexto principal é o único que
escreve. Depois vem a barreira: os candidatos são agrupados por `file:line` e
cada grupo passa por um verificador independente que devolve **CONFIRMED /
PLAUSIBLE / REFUTED**. Candidato não verificado é descartado, nunca promovido.
Todo candidato que saiu de um finder termina num de quatro lugares, e a linha de
stats fecha a conta: reportado, **refutado** (uma linha cada), **sem veredito** (o
descartado, com o local e o motivo do veredito faltar) ou contado no cap.

O tamanho do diff dimensiona o fan-out; **o conteúdo** decide quais ângulos entram
nele. Diff de código roda os cinco. Diff de prompt/skill/markdown troca o ângulo de
footguns de linguagem — que não tem onde morder ali — por `instruction-integrity`:
duas seções que se contradizem, ponteiro que não resolve de onde é citado, regra no
negativo que escreve no prompt o comportamento que ela proíbe, instrução que sobrou
de um guard deletado, saída sem cap num doc que capa as outras, e ação oferecida sem
o probe da precondição. Diff de config/manifest ganha um ângulo de validade contra o
schema do formato. O ângulo derrubado é nomeado no relatório com o motivo — a
profundidade reportada é a que rodou.

Arquitetura de ângulos e verificação adaptada do `/code-review` do Claude Code
(Anthropic, Apache-2.0).

### Desvio de regra agora vem com a regra citada

A frente `rules` é a que responde "seguiu as regras do projeto?". Cada achado
carrega **o texto exato da regra** (com ID ou `path§seção`) ao lado da **linha que
a quebra** — é o que mata regra alucinada, porque o verificador confere a citação,
não um crash. Três fontes em ordem de precedência: o `CODE_REVIEW_GUIDE.md` (lido
fresh), o conjunto de `CLAUDE.md` que governa os arquivos tocados (escopo por
diretório ancestral), e comentários de guidance no próprio código. Divergência
entre guia e código vira item separado apontando pro `/bb:review-setup` — tanto
regra citando caminho que não existe mais quanto **regra desviada em 40%+ dos
arquivos que ela alcança**, que nessa densidade fala mais do guia desatualizado que
do diff (o achado continua, o veredito não muda, e o relatório oferece regenerar a
regra em vez de pedir sete edições).

### O relatório diz o que passou, e você escolhe corrigir ou comentar

Duas coisas que a skill gerada do plugin antigo fazia bem voltaram. O relatório
fecha com **o que veio limpo** — uma linha por frente dizendo o que cobriu sem
achar nada, e na frente `rules` um checklist PASS/FAIL/SKIP regra por regra, com os
SKIP colapsados numa linha. Regra silenciosa agora se lê como checada, não como
esquecida.

E na curadoria, corrigir não é o único desfecho: item por item você escolhe entre
**corrigir** e **comentar na PR**, e pode misturar (corrige 1–3, comenta 4–6). O
comentário sai ancorado na linha do diff, com a citação da regra ou o critério WCAG
junto, e só depois de você ver o corpo exato e aprovar — comentário de PR é
voltado pra fora. Achado cujo local está fora do diff (bug em linha não-alterada de
função que a branch mexeu) não tem onde ancorar: vai num comentário-resumo com o
`file:line` escrito no texto, e o re-report diz quais foram assim. A opção só
aparece quando existe PR aberta. O re-report passou a ter três desfechos:
`corrigido`, `comentado` e `deixado no relatório`.

### Acessibilidade entrou como frente — e o `/bb:ui-accessibility` saiu

Quando o diff toca UI, a frente `a11y` roda o que dá pra provar do código: papel
semântico, nome acessível, label de campo, alcance por teclado, foco visível,
região live, e contraste quando as duas cores estão no diff ou resolvem pelos
tokens. Cada achado diz **quem fica bloqueado** — é o `failure_scenario` dessa
frente — e leva prioridade Critical/Major/Minor/Enhancement.

A mesma frente roda em **escopo de superfície**: aponta pra uma pasta, um conjunto
de arquivos ou uma página rodando e ela audita tudo, sem diff e sem repo git, com
o browser resolvendo o que o código não fecha (contraste computado, ordem real de
foco, o que o leitor de tela anuncia, reflow em 320px). Relatório agrupado por
prioridade e veredito `WCAG AA: pass | fail | partial`.

Com isso o **`/bb:ui-accessibility` foi removido** — eram duas skills pedindo o
mesmo checklist. `/bb:review` responde aos mesmos gatilhos ("auditoria de
acessibilidade", "WCAG", "contraste", "leitor de tela"), e o gate do Deliver do
`/bb:brisar` passou a oferecer essa auditoria. São **15 skills** agora.

### O `/bb:ship` passou a usar a mesma engine

O ship tinha a própria passada de review — quatro lentes fixas, sem probe, sem
verificação independente — e era ela que rodava no `/bb:delegate` e na routine
noturna. Ou seja: no caminho que de fato encosta código na main, o
`CODE_REVIEW_GUIDE.md` do repo não era checado e acessibilidade não existia.

Agora o Step 2 do ship **lê as referências do `/bb:review`**
(`${CLAUDE_PLUGIN_ROOT}/skills/review/references/{fronts,verify,front-*,act-apply-fixes}.md`) e
roda todas as frentes disponíveis menos `threads` e `ci` — essas duas continuam
sendo trabalho do próprio ship. Sem pergunta e sem gate: ship é caminho de
entrega. Ler reference não é invocar skill, então o ship segue self-contained; o
que morreu foi a segunda definição de "como se revisa". Consequência direta:
`/bb:delegate` agora checa regra de projeto, contrato do brief e acessibilidade, e
cada achado passa pelo verificador antes de virar fix.

### SKILL.md virou router

Cada frente e cada ação viraram reference própria, carregada só quando aquela
frente foi escolhida: `references/front-{correctness,quality,rules,contract,a11y,threads,ci}.md`,
`references/fronts.md` (catálogo + probe + profundidade), `references/verify.md`,
`references/act-apply-fixes.md`, `references/act-comment-findings.md`,
`references/mode-external-pr.md`.

No `/bb:review-setup`, o campo `Lens` das regras virou `Categoria` — ele não roteia
mais nada (a frente `rules` lê todas as regras), só diz que tipo de preocupação a
regra é. Guias já gerados com `Lens` continuam válidos.

## 2.1.0 — 2026-07-30

### `/bb:ship` ganhou o destino **LexFlow**

Quem constrói app LexFlow tinha o `ship` desembocando sempre em PR — e parte do
time não tem `gh`. Agora o LexFlow é um **4º destino**, ao lado de branch / main
/ PR. Os destinos são exclusivos: quem quer PR **e** deploy roda o `ship` duas
vezes.

O que o caminho faz: detecta `lexflow.toml` na raiz, roda um gate próprio,
revisa os workflows YAML com lentes que cabem num app declarativo, commita,
pusha o repo do app — e **entrega** `lexflow deploy --ref <sha>` com o sha que
passou pelo review. O `ship` nunca deploya; a mecânica de deploy continua sendo
do `lexflow-builder`, a skill do time de plataforma.

O gate tem três camadas, cada uma com uma autoridade:

- `scripts/check_lexflow_manifest.py` — parse do `lexflow.toml` via `tomllib`,
  exige `[app]`, confere que todo `source` declarado (deployments, workflows,
  middlewares) aponta pra arquivo real. Roda em ms, sem rede, e funciona
  deslogado. Com `--changed`, mapeia os arquivos do diff nos deployments que eles
  afetam — direto ou por referência de dentro de um YAML.
- `lexflow deploy --dry-run` — a autoridade sobre o manifest. `Manifest error:`
  **bloqueia** (é erro do app, e acontece antes de qualquer chamada de rede); 5xx
  na fase de diff **reporta** como instabilidade de plataforma; CLI ausente ou
  deslogado **pula** o check e aponta `lexflow login`.
- conferência de opcodes — `lexflow opcodes list` cruzado com os YAMLs tocados.

### `/bb:delegate` acompanhou o destino novo

O passo de landing do `delegate` afirmava draft PR pro caminho unattended — que não
existe em repo LexFlow. Agora bifurca por destino, e o blocker de um run travado
aterrissa no `## still open` do brief quando não há PR pra escrever nele.

### Landings extraídos pra `references/`

O `SKILL.md` do `ship` virou router: os quatro landings agora vivem em
`references/land-{branch,main,pr,lexflow}.md`, carregados só quando aquele
destino é o escolhido. O `SKILL.md` foi de 170 pra 135 linhas carregando um
destino a mais.

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
| loja                | `ui-accessibility`      | `/bb:review` (frente `a11y`, desde 2.2.0)                     |
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
