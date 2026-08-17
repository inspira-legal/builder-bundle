<div align="center">

# builder-bundle

[![github](https://img.shields.io/badge/github-inspira--legal%2Fbuilder--bundle-111111?style=flat-square&logo=github)](https://github.com/inspira-legal/builder-bundle)

_Builder Bundle (`bb`) — o plugin unificado de skills pra builders da Inspira: 15 skills em 6 trilhas, do problema ao PR._

</div>

adicione o marketplace e instale o plugin único:

```bash
claude plugin marketplace add inspira-legal/builder-bundle
claude plugin install bb@inspira-legal
```

traz um hook `SessionStart` de contexto operacional, auto-ativo na instalação, e dois agentes de só leitura (`bb-finder`, `bb-verifier`) que o review despacha em paralelo — papéis internos do pipeline, não portas de entrada. as skills são invocadas como `/bb:<skill>` — ex. `/bb:discover`, `/bb:spec`, `/bb:ship`. toda skill com próximo passo natural termina num gate que **sugere** a próxima trilha, nunca auto-invoca.

## o que tem dentro

um plugin, `bb`; 15 skills organizadas em 6 trilhas.

### pensar — enquadrar & decidir antes de construir

| skill            | descrição                                                                                                                                     |
| ---------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:discover`   | do incômodo à aposta que dá pra especificar — enquadra o problema, pressiona o fit (vale construir? o que cortar?) e fecha hipótese + apetite |
| `/bb:challenge`  | pre-mortem adversarial de uma tese — tenta derrubar antes que a realidade derrube                                                             |
| `/bb:think`      | pensa junto e se posiciona — recomendação honesta e decisiva, nomeia a tensão não vista, sem bajulação                                        |
| `/bb:legal-lens` | passada jurídica sobre ideia, fluxo ou documento — risco legal & compliance, fundamentado em normas citadas (brasil por padrão)               |

### desenhar — alinhar a forma do que vai ser construído

| skill      | descrição                                                                                                                             |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:spec` | alinhe a ideia antes do código — desenvolve o draft, itera nas zonas cinzentas via perguntas, valida uma spec em `.bb/<slug>/spec.md` |

### construir — escrever & entregar código

| skill                       | descrição                                                                                                                                                                                                                                    |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:implement`             | implementa uma spec validada — constrói as tarefas, roda o gate, depois oferece entregar                                                                                                                                                     |
| `/bb:ship`                  | leva a branch ao fim do seu jeito — roda a engine de review do `/bb:review` (todas as frentes que se aplicam, sem perguntar) + deixa os checks verdes, então push, prepara pra main, abre um PR e cuida dele, ou prepara o deploy no LexFlow |
| `/bb:delegate`              | roda uma spec de ponta a ponta — seleciona, constrói todas as tarefas e entrega (implement → ship), trilhando o `status`                                                                                                                     |
| `/bb:gather-branch-context` | resume todas as mudanças da branch vs main                                                                                                                                                                                                   |

### revisar — qualidade & manutenção

| skill               | descrição                                                                                                                                                                                                                                                                                                                      |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `/bb:review`        | você escolhe as frentes (correção, qualidade, regras do projeto, contrato da spec, acessibilidade da UI, threads do PR, CI), ela roda em paralelo e verifica cada achado; corrige, responde e resolve o que você aprovar. a frente de acessibilidade também roda sozinha como auditoria WCAG AA de uma pasta ou página rodando |
| `/bb:maintain-repo` | tria PRs + dependabot/desatualizados, reporta o que dá pra mergear (nunca faz merge)                                                                                                                                                                                                                                           |
| `/bb:review-setup`  | configura o workflow de code-review da Inspira no repo e escreve o `CODE_REVIEW_GUIDE.md`                                                                                                                                                                                                                                      |

### design — da ideia à surface em alta fidelidade

| skill        | descrição                                                                                                                                                                                   |
| ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:brisar` | jornada de design de ponta a ponta — calibra o perfil, scaffolda com o DS da marca, escreve direção visual por surface, e constrói (Develop) e revisa/entrega (Deliver) como fases internas |

### pesquisar & documentar

| skill                    | descrição                                                                                      |
| ------------------------ | ---------------------------------------------------------------------------------------------- |
| `/bb:code-deep-research` | acha, clona & explora repos, depois verifica adversarialmente os achados contra o código-fonte |
| `/bb:write-readme`       | gera um README mínimo de cabeçalho centralizado a partir dos fatos do repo                     |

## migrando do ofc?

veja o [CHANGELOG](CHANGELOG.md) — de-para completo das 28 skills antigas pras novas, aviso de coexistência e como trocar o plugin.

desenvolva localmente:

```bash
git clone git@github.com:inspira-legal/builder-bundle.git
claude --plugin-dir ./builder-bundle/plugins/bb    # carrega o plugin do disco pra testar
```

<sub>a passada de qualidade do `/bb:review` é adaptada do `/simplify` do Claude Code, a arquitetura de ângulos/verificação, do `/code-review` (Anthropic, Apache-2.0), e a frente de acessibilidade absorve a skill de rafael na loja inspira-skills. `/bb:brisar` incorpora as skills do bundle brisa-ds. componentes individuais mantêm suas licenças originais.</sub>
