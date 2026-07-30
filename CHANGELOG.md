# Changelog

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
