# Fronts — the catalog, the availability probe, and the fan-out budget

A review is a set of **fronts**. Each front is an independent source of findings
with its own method reference and its own agent budget. The user picks which
fronts run; nothing else in the skill changes.

## The catalog

| id            | Rótulo (PT-BR)         | O que cobre                                                            | Disponível quando                                      | Referência             |
| ------------- | ---------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------ | ---------------------- |
| `correctness` | Correção               | bugs no diff — lógica, edges, contratos, concorrência, segurança       | o diff não está vazio                                   | `front-correctness.md` |
| `quality`     | Qualidade              | limpeza behavior-preserving — reuso, simplificação, eficiência, dead weight, altitude, consistência | o diff não está vazio                | `front-quality.md`     |
| `rules`       | Regras do projeto      | desvios do `CODE_REVIEW_GUIDE.md` e dos CLAUDE.md que governam o diff  | existe guia no root **ou** um CLAUDE.md aplicável       | `front-rules.md`       |
| `contract`    | Contrato do brief      | o diff construiu o que foi combinado — e só isso                        | existe brief da branch (`.bb/tasks/<slug>/spec.md`)     | `front-contract.md`    |
| `threads`     | Threads da PR          | comentários de review não resolvidos                                    | há PR aberta pra branch                                 | `front-threads.md`     |
| `ci`          | CI                     | checks vermelhos — evidência, diagnóstico, causa raiz                   | há check falhando na PR ou no último run da branch      | `front-ci.md`          |

## Probe availability before asking

Ask only about fronts that can actually produce findings. Run the probe as one
batch of cheap read-only calls (parallel background where possible):

- `git diff --stat <base>...HEAD` + `git diff --stat` — diff size and whether
  there are uncommitted changes (they enter scope, flagged separately).
- `test -f CODE_REVIEW_GUIDE.md` and the CLAUDE.md set (per `front-rules.md`).
- brief lookup for this branch (plugin-root `references/task-state.md`).
- `gh pr view --json number,url` — is there an open PR.
- `gh pr checks <n>` (only when a PR exists) — any failing check.

A front whose probe comes back empty is **not offered** and not reported as a
failure. `gh` unauthenticated makes `threads`/`ci` unavailable — say so once and
offer the rest.

## Depth — auto-scaled from the diff, not asked

| Diff                             | Correctness angles              | Quality | Rules | Contract | Verify              | Sweep | Report cap |
| -------------------------------- | ------------------------------- | ------- | ----- | -------- | ------------------- | ----- | ---------- |
| ≲2 arquivos / ≲100 linhas        | `diff-scan` + `removed-behavior`, inline (sem fan-out) | inline | inline | inline | self-check no contexto principal | —     | 6          |
| até ~10 arquivos / ~500 linhas   | `diff-scan`, `removed-behavior`, `cross-file` (3 agents) | 1 agent | 1 agent | 1 agent | 1-vote agrupado por local | —     | 10         |
| acima disso, ou "revisa a fundo" | os 5 angles (5 agents)          | 1 agent | 1–2 agents | 1 agent | 1-vote agrupado por local | 1 agent | 15         |

## Fan-out shape

1. **One message, all finder agents.** Every picked front's finders go out
   concurrently via the Agent tool, read-only — they report, never edit. Single
   writer: the main context.
2. **Each finder gets the same scope block** — diff command, changed files, one
   paragraph of what changed, the applicable rule sources, and the brief when
   there is one — plus ONE angle/lens set and a candidate cap.
3. **Barrier before verify.** Pool every finder's candidates first: verification
   groups them by `file:line`, which needs all of them (`verify.md`).
4. **`threads` and `ci` don't fan out** — they're script/`gh` reads followed by
   judgment in the main context.
5. Finders pass through every candidate with a nameable failure scenario. A
   finder that self-censors half-believed candidates bypasses the verifier, which
   is the main way real bugs get missed.
