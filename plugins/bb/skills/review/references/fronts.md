# Fronts — the catalog, the availability probe, and the fan-out budget

A review is a set of **fronts**. Each front is an independent source of findings
with its own method reference and its own agent budget. The user picks which
fronts run; nothing else in the skill changes.

`/bb:review` is the only caller: it probes, asks which fronts to run, and
orchestrates the fan-out. **`/bb:ship` does not review** — it greens the project's
checks, lands, and then offers `/bb:review`, which arrives here through the same
door as any other run.

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
- UI in the diff, decided by **what the hunks contain** — never by the file's
  extension. Grep the added/removed lines (`git diff <range> -U0`) for one of:
  - rendered markup — a JSX/HTML element, a tagged template with tags,
    `createElement`, `innerHTML`, server-side HTML in `.erb`/`.hbs`/`.blade.php`
    or a Django/Jinja template;
  - an attribute that decides semantics or interaction — `role`, `aria-*`, `alt`,
    `label`, `tabIndex`, `autoFocus`, `.focus()`, or a keyboard/pointer handler
    added to an element (`onClick`, `onKeyDown`) as part of new markup;
  - a stylesheet hunk that decides focus, contrast or visibility (`outline`,
    `:focus`, `color`, `background`, `display: none`).

  **A touched `.tsx` is not a UI change.** A component file whose diff only moves
  handler bodies, wires analytics, adds hooks, types or imports leaves the markup
  as it was, and an a11y finder sent at it burns an agent to report nothing — the
  front is unavailable and the report doesn't mention it. A `.js` that builds a
  dialog does activate it. When the grep is ambiguous, read the hunks before
  offering the front, not after.
- `gh pr view --json number,url` — is there an open PR.
- failing checks: `gh pr checks <n>` when a PR exists, otherwise
  `gh run list --branch <branch> --limit 1` — the branch's last run is evidence
  enough for `ci` without a PR.

A front whose probe comes back empty is **not offered** and not reported as a
failure. Only `threads` needs an open PR; `ci` falls back to the branch's last
run. `gh` unauthenticated makes both unavailable — say so once, with
`gh auth login` as the remedy, and offer the rest. No `CODE_REVIEW_GUIDE.md` makes
`rules` unavailable — one line, with `/bb:review-setup` as the remedy.

## Depth — two tiers by default, a third only when asked

| Diff                                | Correctness angles                                | Quality | Rules      | Contract | A11y    | Verify                           | Sweep   | Report cap |
| ----------------------------------- | ------------------------------------------------- | ------- | ---------- | -------- | ------- | -------------------------------- | ------- | ---------- |
| ≲2 arquivos / ≲100 linhas           | os 2 primeiros do angle set, inline (sem fan-out) | inline  | inline     | inline   | inline  | self-check no contexto principal | —       | 6          |
| **qualquer diff maior — o padrão**  | os 3 primeiros do angle set (3 agents)            | 1 agent | 1 agent    | 1 agent  | 1 agent | 1-vote agrupado por local        | —       | 10         |
| **profundo — só sob pedido**        | o angle set inteiro (até 5 agents)                | 1 agent | 1–2 agents | 1 agent  | 1 agent | 1-vote agrupado por local        | 1 agent | 15         |

**Size alone never reaches the third row.** A big diff runs the middle tier — the
same three angles a medium one gets, no sweep — because a review that silently
triples its own cost on a big branch is the review nobody can afford to run twice.
The deep tier is opt-in and the router is what sets it (`SKILL.md`, step 1: the
`profundo` argument, "revisa a fundo", or the deep option at the fronts question).
This engine only reads the flag it was handed. The verify pass has a ceiling of its
own — 8 verifier agents, 12 deep — so a finder pool that returns many locations
batches them instead of dispatching one agent apiece (`verify.md`, §1).

The table sizes the fan-out. **Which** angles fill it comes from what the diff is
made of (`front-correctness.md`) — a diff of prompts or manifests swaps the
language-pitfalls angle for one that grips there and drops the wrapper angle, so an
agent is never spent on a lens with nothing to read. The sets there are written in
priority order, which is what "os 2 primeiros" resolves against: a tier that funds
fewer angles than the set has takes them from the left and names the ones it
dropped.

## Model — Sonnet by default, Opus only when deep

Finders and verifiers declare `model: sonnet` in their own definitions
(`agents/bb-review-finder.md`, `agents/bb-review-verifier.md`), so every dispatch is Sonnet unless
the call says otherwise. **Deep mode passes `model: "opus"` on every Agent call it
sends** — finders and verifiers alike. That's the whole difference in cost between
the tiers, alongside the angle count.

Nothing about the main context changes: it stays on the session's model, it stays
the single writer, and it is what applies fixes. What the fan-out is for is reading
in parallel, and a finder that names a consequence with a line number does that well
below the session's tier. The reason this is written down: with no `model:` at all,
ten finders on a routine review inherit Opus, and the review costs more than the
change it reviewed.

## Fan-out shape

1. **One message, all finder agents.** Every picked front's finders go out
   concurrently via the Agent tool as `subagent_type: "bb-review-finder"`, whose prompt
   carries the finder contract and whose `tools:` has no editing tool
   (`plugins/bb/agents/bb-review-finder.md`). Pass `model: "opus"` on every call when the
   run is deep, and nothing when it isn't — the agent's own `model: sonnet` is the
   default. `Bash` is on that list for reading, so the
   read-only rule still rests on the prompt at the margin. Single writer: the main
   context — hold that line when you dispatch.
2. **Each finder gets the same scope block** — the resolved diff range
   (`<merge_base>...HEAD`, the sha the probe returned, not a `<base>` the finder
   has to guess), changed files, one paragraph of what changed, the repo's
   `CODE_REVIEW_GUIDE.md` when there is one, the criteria path its front points at (plugin-root
   `review-checklist.md` or `quality-checklist.md`), and the
   spec when there is one — plus ONE angle/lens set and its candidate cap.
3. **Barrier before verify.** Pool every finder's candidates first: verification
   groups them by `file:line`, which needs all of them (`verify.md`).
4. **`threads` and `ci` don't fan out** — they're script/`gh` reads followed by
   judgment in the main context.
5. The finder's own contract — name a consequence, pass through every candidate
   that clears that bar, return the shape it was given — belongs to the `bb-review-finder`
   prompt. What the fan-out owes each finder is the scope block above, one angle
   set and its cap.
6. **No Agent tool in this context** (some hosts, some nested runs): work every
   angle of every picked front yourself, in sequence, in the main context — skip
   no angle for lack of fan-out — and self-check each candidate against the file
   before keeping it. Then **say in the report that this was a single-pass review
   without independent verification**, so nobody reads it as the full fan-out.
