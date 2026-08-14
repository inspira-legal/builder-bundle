---
name: review
description: Revisa a mudança de ponta a ponta — você escolhe as frentes, ela roda em paralelo. Detecta quais frentes fazem sentido (correção, qualidade, regras do projeto, contrato da spec, acessibilidade da UI, threads da PR, CI), pergunta quais rodar, faz fan-out de agentes read-only por ângulo, verifica cada achado com um agente independente (CONFIRMED/PLAUSIBLE/REFUTED) e reporta ranqueado. Desvios de regra vêm com a regra citada ao lado da linha que a quebra, direto do CODE_REVIEW_GUIDE.md do repo. Fecha dizendo o que checou e passou, não só o que falhou — a frente de regras entrega checklist PASS/FAIL/SKIP por regra. Depois você escolhe item por item entre corrigir e comentar na PR — ela corrige com guarda de regressão, posta os achados que você preferiu deixar registrados, responde/resolve threads e re-reporta. Também revisa uma PR externa por número e posta o review. Use quando o usuário disser "revisa minhas mudanças", "revisa a PR", "revisa esse diff", "tem bug nisso?", "responde os comentários da PR", "o CI quebrou", "conserta o CI", "limpa esse código", "simplifica o diff", "checa se seguiu as regras do projeto", "revisa a acessibilidade do que eu mudei", "auditoria de acessibilidade", "checa acessibilidade dessa pasta/página", "WCAG", "a11y", "contraste", "leitor de tela", ou "revisa a PR #42 do repo X". A frente de acessibilidade também roda sozinha em escopo de superfície — pasta, arquivos ou página rodando, sem diff. NÃO use pra abrir/finalizar uma PR e acompanhar até o fim (use /bb:ship), nem pra triagem de todas as PRs abertas do repo (use /bb:maintain-repo).
license: Apache-2.0
metadata:
  author: Athena Briana - github.com/athenabriana; quality-pass material adapted from Claude Code's /simplify, angle/verify architecture adapted from Claude Code's /code-review (Anthropic, Apache-2.0), a11y front absorbed from rafael's ui-accessibility skill (loja inspira-skills, MIT)
  version: 2.4.0
---

# Review

One review skill, seven **fronts** of findings. The skill detects which fronts can
produce anything on this branch, asks which ones you want, runs them as a parallel
fan-out of read-only agents, and puts every candidate through an independent
verifier before it reaches the report. Then the flow is interactive — report → you
pick → apply → reply/resolve → re-report — and repeats until you close it. It fixes
what you approve; it never merges, never approves, never force-pushes.

This SKILL.md is the router. Each front's method lives in its own reference and is
loaded **only when that front was picked**; each action likewise.

## Prerequisites

Inside a git repository. `gh` authenticated (`gh auth status`) for anything
PR/CI-related; the diff fronts need no `gh`. The accessibility audit in surface
scope is the one path that needs neither a repo nor a diff.

## Step 0 — Load the review context

- **Repo guide:** if `CODE_REVIEW_GUIDE.md` exists at the repo root, read it fresh
  (never cached) — it's the `rules` front's whole rule source, and its severities
  rank the whole report. No guide → the front is unavailable and the report carries
  one line, "Sem CODE_REVIEW_GUIDE.md — regras específicas do repo via
  /bb:review-setup". Why the guide alone is the source: `references/front-rules.md`.
- **Legacy custom skill:** if `.claude/skills/code-review/SKILL.md` exists (an old
  generated per-repo review skill), note in the report that `/bb:review` +
  `CODE_REVIEW_GUIDE.md` supersede it and the user can delete it.
- **Stack judgment:** when a finding turns on a stack choice (library, pattern,
  architecture), consult the manifesto per the plugin-root
  `references/consult-manifesto.md` before calling it wrong.

## Step 1 — Resolve the mode

- **External PR** (user names a repo and/or PR number that isn't the current
  branch's): follow `references/mode-external-pr.md`, then stop. Read-only over
  that PR; posting the review requires explicit confirmation.
- **Direct front ask** — the user already named the front ("o CI quebrou",
  "responde os comentários", "checa se seguiu as regras"): that front is the
  scope. Skip step 2's question and go straight to it.
- **Accessibility audit** — the user named a **surface** instead of the branch: a
  folder, a set of files, a URL or a running page ("auditoria de acessibilidade",
  "checa a acessibilidade dessa pasta/página"). The named target is what routes
  here; an a11y ask with no target is the `a11y` front over the diff, picked at
  step 2. Run `references/front-a11y.md` in surface scope — no diff, no other
  fronts, no git repository required — and stop at its own gate.
- **Otherwise**: current branch, all fronts on the table.

## Step 2 — Probe the fronts, then ask which ones

Load `references/fronts.md`: it carries the front catalog, the availability probe
(one batch of cheap read-only calls), and the depth table that sizes the fan-out
from the diff.

Run the probe, then ask with one `AskUserQuestion` (PT-BR, `multiSelect`) —
offering **only the available fronts**, each option saying in one line what that
front will look for and roughly what it costs:

```
question: "Achei <N> frentes possíveis nessa branch. Quais eu reviso?"
options:
  - "Tudo que se aplica (Recomendado)" — roda as N frentes disponíveis em paralelo.
  - "Correção + Regras" — bugs no diff e desvios do CODE_REVIEW_GUIDE.md.
  - "Só <frente específica>" — <o que ela cobre>.
  - "Nenhuma — encerrar" — nada roda.
```

Say the depth the diff resolved to in one line, with the numbers the resolution
actually produced — how many angles are in the diff's set, how many the tier funds,
which ones were dropped and why, and whether the sweep runs (`markdown: 4 ângulos
no set, 3 rodam, wrapper-boundary fora — sem sweep`). Every number in that line comes
from the resolution that just ran, which is what makes it match the stats line at the
end; on a small diff it's also why no agent shows up.

## Step 3 — Run the picked fronts in parallel

The catalog in `fronts.md` maps each picked front to its `references/front-*.md` —
that mapping is the list, so a front added to the engine reaches this router with no
edit here. Load only the picked fronts' references, build the shared scope block
(the resolved diff range included), and send every finder agent in **one message**
(Agent tool, `subagent_type: bb-finder`, which carries the finder contract in its
own prompt; the main context is the only writer). `threads` and `ci` don't fan out: script/`gh` reads plus
judgment here.

Then `references/verify.md`: pool everything at the barrier, group by `file:line`,
one independent verifier per location (CONFIRMED / PLAUSIBLE / REFUTED), sweep on
large diffs, then dedupe, rank and cap.

## Step 4 — Report

One unified report, numbered items across all fronts, most severe first. Each item
carries its front, its verdict, and the columns of **its own front's Finding
shape** — the row format lives in each `front-*.md` next to the method that
produces it, so a front that changes its columns doesn't leave a stale template
here. Group the items by front under PT-BR headings (Correção, Qualidade, Regras,
Contrato, Acessibilidade, Threads, CI) and keep one numbering across the whole
report.

Close with what didn't make it and what actually ran:

- **what came back clean** — one line per front naming what it covered and found
  nothing on, with the count the depth resolution actually produced ("Correção:
  3 dos 4 ângulos do set, nada fora dos itens 1–3"). The `rules` front
  closes with its own PASS/FAIL/SKIP checklist per rule (`front-rules.md`), which is
  what makes a silent rule readable as checked instead of forgotten;
- refuted candidates, one line each;
- candidates left **sem veredito** (dropped — a verifier died or skipped the index),
  one line each with the location;
- the count cut by the cap ("+4 de qualidade fora do cap");
- one stats line — frentes rodadas, agentes finder, candidatos, verificados,
  refutados, sem veredito, reportados. It's how the reader knows the depth that ran
  matches the depth that was announced, and `candidatos` has to add up.

Clean everywhere → say so and jump to the gate (step 7).

## Step 5 — Curate (the user picks)

One `AskUserQuestion` (PT-BR, `multiSelect`): which numbered items to handle now,
and **how** — fixing is one outcome, leaving the finding on the PR is another.
Options group naturally ("Todas as correções", "Correção + regras HIGH", "Só os
threads", specific numbers via "Other"). "Comentar os itens na PR em vez de corrigir"
is offered when the probe found an open PR, and fix and comment can both be picked:
fix 1–3, comment 4–6. "Nenhum — encerrar" is always an option.

## Step 6 — Apply what was picked

Follow `references/act-apply-fixes.md` — one change at a time, justified, with the
regression guard; quality edits are strictly behavior-preserving. Then:

- **fix-threads**: commit (conventional style, no AI attribution), push to the PR
  branch, reply with the sha and resolve (`references/front-threads.md`, handling
  table).
- **answer-threads**: reply, do NOT resolve — the reviewer closes it.
- **CI fixes**: push and re-check the failing workflow; cap at 3 diagnose→fix
  cycles, then report what's still red instead of thrashing.
- **comment-on-PR**: `references/act-comment-findings.md` — body shown before
  anything is posted, anchored inline where the location is in the diff and folded
  into one summary comment where it isn't. On a PR that already carries a review
  comment, each point lands once: still-open prior points as status lines, first-time
  findings in full, fixed ones as a count.

Re-report as a table: `# | item | action taken | commit/status` — `corrigido`,
`comentado (link)` and `deixado no relatório` are all valid outcomes.

## Step 7 — Gate

Per the plugin-root `references/handoff-gate.md`, one PT-BR question with **2–4
options**. Five states can qualify, so take the first three that apply in this
priority order — unfinished work on this report outranks the next skill:

1. items still open → **"Aplicar mais"** (loops to step 5)
2. fronts left unrun → **"Rodar as frentes que faltaram"** (loops to step 3)
3. a11y findings that need a rendered page (runtime colors, real focus order, live
   regions) → **"Auditar a UI rodando"** (loops to `front-a11y.md`, surface scope)
4. guide drift or missing guide reported → **"Gerar/atualizar o guia — rodo
   /bb:review-setup"**
5. no open PR and everything clean/handled → **"Abrir a PR — rodo /bb:ship"**

Lead with the highest-priority one and suffix its label `(Recomendado)`. The states
that didn't fit go in one line of prose above the question, so nothing is hidden —
the user can still ask for them via "Other". Last option is always **"Encerrar
aqui"** (what stays saved: the report; how to resume: `/bb:review`).

## Edge cases

Front availability is `fronts.md`'s probe — an empty probe means the front isn't
offered, which needs no row here. What this table covers is everything else:

| WHEN                                         | THEN                                                                                                                  |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| diff vs base empty and no PR                 | report "nada pra revisar", stop                                                                                       |
| no front available (empty probe)             | say what was probed and why each came back empty, stop                                                                |
| no open PR (review-sem-PR)                   | `threads` and the comment-on-PR option not offered; `ci` still runs off the branch's last run; gate offers `/bb:ship` |
| `gh` unauthenticated                         | `threads`/`ci` unavailable — say so once with `gh auth login` as the remedy, offer the diff fronts                    |
| a11y finding needs a rendered page           | report it as out of static reach; the gate offers the surface-scope audit                                             |
| accessibility audit asked outside a git repo | surface scope needs no diff and no repo — audit what was pointed at                                                   |
| legacy `.claude/skills/code-review/` present | flag as superseded; the user deletes it                                                                               |
| uncommitted changes present                  | include in diff scope, flagged separately                                                                             |
| a finder agent dies                          | its front reports with the angles that returned, and says which angle is missing                                      |
| user picks nothing at curation               | no edits; go to the gate                                                                                              |
| a verifier dies or omits an index            | that candidate is `sem veredito`, reported as its own line, never promoted                                            |
| CI still red after 3 diagnose→fix cycles     | stop editing, report the remaining failure and the evidence                                                           |

## Bundled Resources

Router support:

- `references/fronts.md` — the front catalog, the availability probe, the depth table and the fan-out shape.
- `references/verify.md` — pool, group by location, 3-state verdict, sweep, rank and cap.

Per-front method (loaded only when that front is picked):

- `references/front-correctness.md` — the correctness angles over the diff, and how the diff's content picks which of them run.
- `references/front-quality.md` — the cleanup lenses, one finder, behavior-preserving.
- `references/front-rules.md` — `CODE_REVIEW_GUIDE.md` deviations, with the citation discipline.
- `references/front-contract.md` — the spec's `## behavior` map as the acceptance contract.
- `references/front-a11y.md` — WCAG AA: diff scope (static) and surface scope (folder, files or a rendered page).
- `references/front-threads.md` — PR review threads: fetch, triage, fix/answer, reply/resolve.
- `references/front-ci.md` — CI failures: evidence → diagnosis → fix → verify.

Skill-owned script:

- `scripts/group_candidates.py` — canonicalizes finder paths against the scope file list and groups candidates by location for the verify pass. Reads/writes JSON.

Actions and modes:

- `references/act-apply-fixes.md` — applying findings: the regression guard and the order of operations.
- `references/act-comment-findings.md` — leaving findings on the PR instead of fixing: anchoring and approval.
- `references/mode-external-pr.md` — reviewing a PR in another repo and posting the review.

Pipeline agents (plugin root, dispatched by the fan-out — same two for `/bb:ship`):

- `${CLAUDE_PLUGIN_ROOT}/agents/bb-finder.md` — the finder's contract, and the narrowed `tools:` list.
- `${CLAUDE_PLUGIN_ROOT}/agents/bb-verifier.md` — the CONFIRMED / PLAUSIBLE / REFUTED rubric.

Shared engine (plugin root, same criteria as `/bb:ship`):

- `${CLAUDE_PLUGIN_ROOT}/references/review-checklist.md`, `${CLAUDE_PLUGIN_ROOT}/references/quality-checklist.md` — the correctness and quality criteria.
- `${CLAUDE_PLUGIN_ROOT}/scripts/gather_context.py` — branch, base + merge-base, diff stat, changed files, full diff, uncommitted changes. Resolves the review's diff range for the probe.
- `${CLAUDE_PLUGIN_ROOT}/scripts/fetch_comments.py`, `${CLAUDE_PLUGIN_ROOT}/scripts/reply_resolve_thread.py` — thread I/O via `gh api graphql`.
