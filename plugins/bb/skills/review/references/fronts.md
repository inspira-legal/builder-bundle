# Fronts — the catalog, the availability probe, and the fan-out budget

A review is a set of **fronts**. Each front is an independent source of findings
with its own method reference and its own agent budget. The user picks which
fronts run; nothing else in the skill changes.

Two callers read this engine. `/bb:review` probes and **asks** which fronts to
run. `/bb:ship` probes and takes **every available front except `threads` and
`ci`** — no question, no gate, because it handles comments and red checks itself.
The method below is identical either way.

## The catalog

| id            | Rótulo (PT-BR)    | O que cobre                                                                                         | Disponível quando                                  | Referência             |
| ------------- | ----------------- | --------------------------------------------------------------------------------------------------- | -------------------------------------------------- | ---------------------- |
| `correctness` | Correção          | bugs no diff — lógica, edges, contratos, concorrência, segurança                                    | o diff não está vazio                              | `front-correctness.md` |
| `quality`     | Qualidade         | limpeza behavior-preserving — reuso, simplificação, eficiência, dead weight, altitude, consistência | o diff não está vazio                              | `front-quality.md`     |
| `rules`       | Regras do projeto | desvios do `CODE_REVIEW_GUIDE.md` do repo                                                           | existe `CODE_REVIEW_GUIDE.md` no root              | `front-rules.md`       |
| `contract`    | Contrato da spec  | o diff construiu o que foi combinado — e só isso                                                    | existe spec da branch (`.bb/<slug>/spec.md`)       | `front-contract.md`    |
| `a11y`        | Acessibilidade    | WCAG AA no que o diff mexeu na UI — semântica, nome acessível, teclado, foco, contraste             | o diff toca arquivo de UI                          | `front-a11y.md`        |
| `threads`     | Threads da PR     | comentários de review não resolvidos                                                                | há PR aberta pra branch                            | `front-threads.md`     |
| `ci`          | CI                | checks vermelhos — evidência, diagnóstico, causa raiz                                               | há check falhando na PR ou no último run da branch | `front-ci.md`          |

## Probe availability before asking

Ask only about fronts that can actually produce findings. Run the probe as one
batch of cheap read-only calls (parallel background where possible):

- `${CLAUDE_PLUGIN_ROOT}/scripts/gather_context.py` — one call returns
  `base_branch`, `merge_base`, `diff_stat`, `files_changed` and
  `uncommitted_changes`. **`<merge_base>...HEAD` is the review's diff range for
  the whole run** — carry the resolved sha into the scope block so every finder,
  every front reference and the shared checklists read the same range instead of
  each resolving a base of its own. Uncommitted changes enter scope, flagged
  separately.
- `CODE_REVIEW_GUIDE.md` at the repo root — the `rules` front's only rule source
  (`front-rules.md`), so its absence is what makes the front unavailable.
- spec lookup for this branch (plugin-root `references/spec-state.md`).
- UI in the diff, decided by **content** and not by extension: markup or
  component files (`*.{jsx,tsx,vue,svelte,astro,html,htm}`, `*.erb`, `*.hbs`,
  `*.blade.php`, Django/Jinja templates), a `.js`/`.ts`/`.py` file whose diff
  renders markup (JSX, tagged template strings, `createElement`, `innerHTML`,
  server-side HTML), or a stylesheet hunk that decides focus, contrast or
  visibility (`outline`, `:focus`, `color`, `background`, `display: none`). Grep
  the diff for those; a `.tsx` of pure types doesn't activate the front and a
  `.js` that builds a dialog does.
- `gh pr view --json number,url` — is there an open PR.
- failing checks: `gh pr checks <n>` when a PR exists, otherwise
  `gh run list --branch <branch> --limit 1` — the branch's last run is evidence
  enough for `ci` without a PR.

A front whose probe comes back empty is **not offered** and not reported as a
failure. Only `threads` needs an open PR; `ci` falls back to the branch's last
run. `gh` unauthenticated makes both unavailable — say so once, with
`gh auth login` as the remedy, and offer the rest. No `CODE_REVIEW_GUIDE.md` makes
`rules` unavailable — one line, with `/bb:review-setup` as the remedy.

## Depth — auto-scaled from the diff, not asked

| Diff                             | Correctness angles                                | Quality | Rules      | Contract | A11y    | Verify                           | Sweep   | Report cap |
| -------------------------------- | ------------------------------------------------- | ------- | ---------- | -------- | ------- | -------------------------------- | ------- | ---------- |
| ≲2 arquivos / ≲100 linhas        | os 2 primeiros do angle set, inline (sem fan-out) | inline  | inline     | inline   | inline  | self-check no contexto principal | —       | 6          |
| até ~10 arquivos / ~500 linhas   | os 3 primeiros do angle set (3 agents)            | 1 agent | 1 agent    | 1 agent  | 1 agent | 1-vote agrupado por local        | —       | 10         |
| acima disso, ou "revisa a fundo" | o angle set inteiro (até 5 agents)                | 1 agent | 1–2 agents | 1 agent  | 1 agent | 1-vote agrupado por local        | 1 agent | 15         |

The table sizes the fan-out. **Which** angles fill it comes from what the diff is
made of (`front-correctness.md`) — a diff of prompts or manifests swaps the
language-pitfalls angle for one that grips there and drops the wrapper angle, so an
agent is never spent on a lens with nothing to read. The sets there are written in
priority order, which is what "os 2 primeiros" resolves against: a tier that funds
fewer angles than the set has takes them from the left and names the ones it
dropped.

## Fan-out shape

1. **One message, all finder agents.** Every picked front's finders go out
   concurrently via the Agent tool as `subagent_type: "bb-finder"`, whose prompt
   carries the finder contract and whose `tools:` has no editing tool
   (`plugins/bb/agents/bb-finder.md`). `Bash` is on that list for reading, so the
   read-only rule still rests on the prompt at the margin. Single writer: the main
   context — hold that line when you dispatch.
2. **Each finder gets the same scope block** — the resolved diff range
   (`<merge_base>...HEAD`, the sha the probe returned, not a `<base>` the finder
   has to guess), changed files, one paragraph of what changed, the repo's
   `CODE_REVIEW_GUIDE.md` when there is one, the criteria path its front points at (plugin-root
   `references/review-checklist.md` or `references/quality-checklist.md`), and the
   spec when there is one — plus ONE angle/lens set and its candidate cap.
3. **Barrier before verify.** Pool every finder's candidates first: verification
   groups them by `file:line`, which needs all of them (`verify.md`).
4. **`threads` and `ci` don't fan out** — they're script/`gh` reads followed by
   judgment in the main context.
5. The finder's own contract — name a consequence, pass through every candidate
   that clears that bar, return the shape it was given — belongs to the `bb-finder`
   prompt. What the fan-out owes each finder is the scope block above, one angle
   set and its cap.
6. **No Agent tool in this context** (some hosts, some nested runs): work every
   angle of every picked front yourself, in sequence, in the main context — skip
   no angle for lack of fan-out — and self-check each candidate against the file
   before keeping it. Then **say in the report that this was a single-pass review
   without independent verification**, so nobody reads it as the full fan-out.
