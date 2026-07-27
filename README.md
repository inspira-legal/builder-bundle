<div align="center">

# builder-bundle

[![github](https://img.shields.io/badge/github-inspira--legal%2Fbuilder--bundle-111111?style=flat-square&logo=github)](https://github.com/inspira-legal/builder-bundle)

_Builder Bundle (`bb`) — o plugin unificado de skills pra builders da Inspira: 16 skills em 6 trilhas, do problema ao PR._

</div>

adicione o marketplace e instale o plugin único:

```bash
claude plugin marketplace add inspira-legal/builder-bundle
claude plugin install bb@inspira-legal
```

traz um hook `SessionStart` de contexto operacional, auto-ativo na instalação. as skills são invocadas como `/bb:<skill>` — ex. `/bb:discover`, `/bb:spec`, `/bb:ship`. toda skill com próximo passo natural termina num gate que **sugere** a próxima trilha, nunca auto-invoca.

## o que tem dentro

um plugin, `bb`; 16 skills organizadas em 6 trilhas.

### pensar — enquadrar & decidir antes de construir

| skill            | descrição                                                                                                                        |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:discover`   | do incômodo à aposta shapeável — enquadra o problema, pressiona o fit (vale construir? o que cortar?) e fecha hipótese + apetite |
| `/bb:challenge`  | pre-mortem adversarial de uma tese — tenta derrubar antes que a realidade derrube                                                |
| `/bb:think`      | pensa junto e se posiciona — recomendação honesta e decisiva, nomeia a tensão não vista, sem bajulação                           |
| `/bb:legal-lens` | passada jurídica sobre ideia, fluxo ou documento — risco legal & compliance, fundamentado em normas citadas (brasil por padrão)  |

### desenhar — alinhar a forma do que vai ser construído

| skill      | descrição                                                                                                                                   |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:spec` | alinhe a ideia antes do código — desenvolve o draft, itera nas zonas cinzentas via perguntas, valida um brief em `.bb/tasks/<slug>/spec.md` |

### construir — escrever & entregar código

| skill                       | descrição                                                                                                                                                          |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `/bb:implement`             | implementa um brief validado — constrói as fatias, roda o gate, depois oferece entregar                                                                            |
| `/bb:ship`                  | leva a branch ao fim do seu jeito — revisa + deixa os checks verdes, então push, prepara pra main, ou abre um PR e cuida dele                                      |
| `/bb:delegate`              | roda uma task shapeada de ponta a ponta — escolhe o brief, constrói e entrega (implement → ship), trilhando o `status`. o mesmo verbo no desk e na routine noturna |
| `/bb:gather-branch-context` | resume todas as mudanças da branch vs main                                                                                                                         |

### revisar — qualidade & manutenção

| skill               | descrição                                                                                                                                |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:review`        | revisa contra 3 fontes — diff da branch, threads do PR e CI — com gate interativo pra escolher o que tratar; corrige, responde e resolve |
| `/bb:maintain-repo` | tria PRs + dependabot/desatualizados, reporta o que dá pra mergear (nunca faz merge)                                                     |
| `/bb:review-setup`  | configura o workflow de code-review da Inspira no repo e escreve o `CODE_REVIEW_GUIDE.md`                                                |

### design — da ideia à surface em alta fidelidade

| skill                  | descrição                                                                                                                                                                                   |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:brisar`           | jornada de design de ponta a ponta — calibra o perfil, scaffolda com o DS da marca, escreve direção visual por surface, e constrói (Develop) e revisa/entrega (Deliver) como fases internas |
| `/bb:ui-accessibility` | audita interfaces web pra WCAG AA — contraste, teclado, leitor de tela — com relatório priorizado por impacto                                                                               |

### pesquisar & documentar

| skill                    | descrição                                                                                      |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| `/bb:code-deep-research` | acha, clona & explora repos, depois verifica adversarialmente os achados contra o código-fonte |
| `/bb:write-readme`       | gera um README mínimo de cabeçalho centralizado a partir dos fatos do repo                     |

## rodar sem supervisão

não há skill dedicada de madrugada — o caminho não-supervisionado **é** a tríade: uma [Cloud Routine](plugins/bb/references/routines.md) define `BB_UNATTENDED` e roda `/bb:delegate <slug>` contra um brief commitado, que encadeia `/bb:implement` → `/bb:ship`, construindo todo o backlog e deixando um PR em rascunho. nesse caminho, o never-merge é garantido por **capability scoping** — a routine roda com um token sem permissão de merge/push em branch protegida e sem connector capaz de merge — apoiado pela branch protection do GitHub. controles do lado do servidor, não um hook local.

## migrando do ofc?

veja o [CHANGELOG](CHANGELOG.md) — de-para completo das 28 skills antigas pras 16 novas, aviso de coexistência e como trocar o plugin.

desenvolva localmente:

```bash
git clone git@github.com:inspira-legal/builder-bundle.git
claude --plugin-dir ./builder-bundle/plugins/bb    # carrega o plugin do disco pra testar
```

<sub>a passada de qualidade do `/bb:review` é adaptada do `/simplify` do Claude Code (Anthropic, Apache-2.0). `/bb:brisar` incorpora as skills do bundle brisa-ds; `/bb:ui-accessibility` é baseada na skill de rafael na loja inspira-skills. componentes individuais mantêm suas licenças originais.</sub>
