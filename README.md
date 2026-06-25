<div align="center">

# ofc-skills

[![github](https://img.shields.io/badge/github-inspira--legal%2Fofc--skills-111111?style=flat-square&logo=github)](https://github.com/inspira-legal/ofc-skills)

_Oficina (`ofc`) — um plugin do claude code com skills de agente agrupadas por uso, e um hook de contexto operacional junto._

</div>

adicione o marketplace e instale o plugin único:

```bash
claude plugin marketplace add inspira-legal/ofc-skills
claude plugin install ofc@inspira-legal
```

traz um hook `SessionStart` de contexto operacional, auto-ativo na instalação. as skills são invocadas como `/ofc:<skill>` — ex. `/ofc:shape`, `/ofc:ship`, `/ofc:answer-yourself`.

## o que tem dentro

um plugin, `ofc`; as skills são organizadas por uso.

### shape & ship — escrever & entregar código, conduzido por você

| skill                        | descrição                                                                                                                                                                      |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `/ofc:shape`                 | alinhe a ideia antes de construir — desenvolve, itera nas zonas cinzentas via perguntas, valida                                                                                |
| `/ofc:implement`             | implementa um brief de shape validado — constrói as fatias, roda o gate, depois oferece entregar (ou emenda direto)                                                            |
| `/ofc:ship`                  | leve a branch ao fim do seu jeito — revisa + deixa os checks verdes, então push numa branch, prepara push pra main, ou abre um PR e cuida dele (comentários, CI, fica de olho) |
| `/ofc:review-changes`        | revisa o diff da branch — bugs de correção + qualidade — só reporta e sugere o próximo passo, nunca edita                                                                      |
| `/ofc:tidy-pr`               | passada leve e curada nos threads de review do PR aberto — você escolhe quais tratar; corrige/responde, resolve, e pode ajustar título/corpo                                   |
| `/ofc:gather-branch-context` | resume todas as mudanças da branch vs main                                                                                                                                     |
| `/ofc:tidy`                  | passada de qualidade behavior-preserving num diff, com guarda dura contra regressão (sem caça a bug)                                                                           |
| `/ofc:write-readme`          | gera um README mínimo de cabeçalho centralizado a partir dos fatos do repo                                                                                                     |

### think & research — entender & decidir, antes de construir

| skill                     | descrição                                                                                                                                  |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `/ofc:frame-problem`      | enquadra o problema antes de qualquer solução — a aposta, quem sente a dor, o sinal de sucesso & o apetite                                 |
| `/ofc:assess-fit`         | pressiona um problema enquadrado — vale construir? o que cortar, em que ordem, a única hipótese testável                                   |
| `/ofc:code-deep-research` | acha, clona & explora repos, depois verifica adversarialmente os achados contra o código-fonte                                             |
| `/ofc:legal-lens`         | uma passada jurídica sobre uma ideia, fluxo ou documento — risco legal & de compliance, fundamentado em normas citadas (brasil por padrão) |
| `/ofc:answer-yourself`    | recomendação honesta e decisiva — se posiciona, nomeia a tensão não vista, sem bajulação                                                   |

### loops — rodar ao longo do tempo (agendado / orientado a evento)

não há skill dedicada de madrugada — o caminho não-supervisionado **é** a tríade: uma [Cloud Routine](plugins/ofc/references/routines.md) define `OFC_UNATTENDED` e roda `/ofc:implement` → `/ofc:ship` contra um brief commitado, construindo todo o backlog e deixando um PR em rascunho. nesse caminho, o never-merge é garantido por **capability scoping** — a routine roda com um token sem permissão de merge/push em branch e sem connector capaz de merge — apoiado pela branch protection do GitHub. controles do lado do servidor, não um hook local.

| skill                | descrição                                                                            |
| -------------------- | ------------------------------------------------------------------------------------ |
| `/ofc:maintain-repo` | tria PRs + dependabot/desatualizados, reporta o que dá pra mergear (nunca faz merge) |

desenvolva localmente:

```bash
git clone git@github.com:inspira-legal/ofc-skills.git
claude --plugin-dir ./ofc-skills/plugins/ofc    # carrega o plugin do disco pra testar
```

<sub>`/ofc:tidy` é adaptada do `/simplify` do Claude Code (Anthropic, Apache-2.0). componentes individuais mantêm suas licenças originais.</sub>
