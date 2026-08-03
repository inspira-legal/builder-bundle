---
name: review
description: Revisa a mudança de ponta a ponta — você escolhe as frentes, ela roda em paralelo. Detecta quais frentes fazem sentido (correção, qualidade, regras do projeto, contrato do brief, acessibilidade da UI, threads da PR, CI), pergunta quais rodar, faz fan-out de agentes read-only por ângulo, verifica cada achado com um agente independente (CONFIRMED/PLAUSIBLE/REFUTED) e reporta ranqueado. Desvios de regra vêm com a regra citada ao lado da linha que a quebra — CODE_REVIEW_GUIDE.md do repo e os CLAUDE.md que governam o diff. Depois você escolhe o que aplicar, ela corrige com guarda de regressão, responde/resolve threads e re-reporta. Também revisa uma PR externa por número e posta o review. Use quando o usuário disser "revisa minhas mudanças", "revisa a PR", "revisa esse diff", "tem bug nisso?", "responde os comentários da PR", "o CI quebrou", "conserta o CI", "limpa esse código", "simplifica o diff", "checa se seguiu as regras do projeto", "revisa a acessibilidade do que eu mudei", ou "revisa a PR #42 do repo X". NÃO use pra abrir/finalizar uma PR e acompanhar até o fim (use /bb:ship), nem pra auditar acessibilidade de uma página rodando (use /bb:ui-accessibility), nem pra triagem de todas as PRs abertas do repo (use /bb:maintain-repo).
license: Apache-2.0
metadata:
  author: Athena Briana - github.com/athenabriana; quality-pass material adapted from Claude Code's /simplify, angle/verify architecture adapted from Claude Code's /code-review (Anthropic, Apache-2.0)
  version: 2.2.0
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
PR/CI-related; the diff fronts need no `gh`.

## Step 0 — Load the review context

- **Repo guide:** if `CODE_REVIEW_GUIDE.md` exists at the repo root, read it fresh
  (never cached) — it powers the `rules` front and its severities rank the whole
  report. No guide and no applicable CLAUDE.md → add one line to the report: "Sem
  CODE_REVIEW_GUIDE.md — regras específicas do repo via /bb:review-setup."
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
  - "Correção + Regras" — bugs no diff e desvios do CODE_REVIEW_GUIDE/CLAUDE.md.
  - "Só <frente específica>" — <o que ela cobre>.
  - "Nenhuma — encerrar" — nada roda.
```

Say the depth the diff resolved to (`3 angles` vs `5 angles + sweep`) in one line
so the size of what's about to run isn't a surprise. Under `BB_UNATTENDED` there is
no question: every available front runs, report-only.

## Step 3 — Run the picked fronts in parallel

Load only the picked fronts' references, build the shared scope block, and send
every finder agent in **one message** (Agent tool, read-only — they report, never
edit; the main context is the only writer):

- **Correção** → `references/front-correctness.md` — 2–5 angles over the diff.
- **Qualidade** → `references/front-quality.md` — one finder, all cleanup lenses.
- **Regras do projeto** → `references/front-rules.md` — guide + CLAUDE.md
  deviations, each with the rule quoted next to the line that breaks it.
- **Contrato do brief** → `references/front-contract.md` — the `## behavior` map
  as the acceptance contract.
- **Acessibilidade** → `references/front-a11y.md` — one finder, static, WCAG AA
  over the UI the diff changed.
- **Threads da PR** → `references/front-threads.md` — no fan-out; script read plus
  triage (fix vs. answer).
- **CI** → `references/front-ci.md` — no fan-out; evidence first, diagnosis before
  any edit.

Then `references/verify.md`: pool everything at the barrier, group by `file:line`,
one independent verifier per location (CONFIRMED / PLAUSIBLE / REFUTED), sweep on
large diffs, then dedupe, rank and cap.

## Step 4 — Report

One unified report, numbered items across all fronts, most severe first, each item
carrying its front and its verdict:

- **Correção** — `# | file:line | what breaks | trigger | suggested fix | verdict`
- **Regras** — `# | rule ID / path§seção | "regra" | file:line | linha que desvia | severidade`
- **Contrato** — `# | linha do brief | file:line ou "ausente" | o que falta ou sobra`
- **Acessibilidade** — `# | file:line | critério WCAG | o que falha | quem é bloqueado | prioridade | fix`
- **Qualidade** — `# | file:line | smell | custo concreto | suggested edit`
- **Threads** — `# | file:line | thread summary | fix or answer`
- **CI** — `# | failing check | root cause | evidence | proposed fix`

Close with what didn't make it and what actually ran:

- refuted candidates, one line each;
- the count cut by the cap ("+4 de qualidade fora do cap");
- one stats line — frentes rodadas, agentes finder, candidatos, verificados,
  refutados, reportados. It's how the reader knows the depth that ran matches the
  depth that was announced.

Clean everywhere → say so and jump to the gate (step 7).

## Step 5 — Curate (the user picks)

One `AskUserQuestion` (PT-BR, `multiSelect`): which numbered items to handle now.
Options group naturally ("Todas as correções", "Correção + regras HIGH", "Só os
threads", specific numbers via "Other"). "Nenhum — encerrar" is always an option.
Under `BB_UNATTENDED` there is no curation: report-only, no edits, stop.

## Step 6 — Apply what was picked

Follow `references/act-apply-fixes.md` — one change at a time, justified, with the
regression guard; quality edits are strictly behavior-preserving. Then:

- **fix-threads**: commit (conventional style, no AI attribution), push to the PR
  branch, reply with the sha and resolve (`references/front-threads.md`, handling
  table).
- **answer-threads**: reply, do NOT resolve — the reviewer closes it.
- **CI fixes**: push and re-check the failing workflow; cap at 3 diagnose→fix
  cycles, then report what's still red instead of thrashing.

Re-report as a table: `# | item | action taken | commit/status`.

## Step 7 — Gate

Per the plugin-root `references/handoff-gate.md`, one PT-BR question. Options by
state: fronts left unrun → "Rodar as frentes que faltaram" (loops to step 3); more
items still open → "Aplicar mais" (loops to step 5); no open PR and clean/handled →
"Abrir a PR — rodo /bb:ship"; guide drift or missing guide reported → "Gerar/atualizar
o guia — rodo /bb:review-setup"; a11y findings that need a rendered page (runtime
colors, real focus order, live regions) → "Auditar a UI rodando — rodo
/bb:ui-accessibility"; always "Encerrar aqui" (what stays saved: the
report; how to resume: `/bb:review`).

## Edge cases

| WHEN                                             | THEN                                                                                  |
| ------------------------------------------------ | ------------------------------------------------------------------------------------- |
| diff vs base empty and no PR                     | report "nada pra revisar", stop                                                       |
| no front available (empty probe)                 | say what was probed and why each came back empty, stop                                |
| no open PR (review-sem-PR)                       | `threads`/`ci` not offered; gate offers `/bb:ship` to open one                        |
| `CODE_REVIEW_GUIDE.md` absent, CLAUDE.md present | `rules` front runs on the CLAUDE.md set alone, with the pointer to `/bb:review-setup` |
| neither guide nor applicable CLAUDE.md           | `rules` front not offered; one-line pointer to `/bb:review-setup`                     |
| no brief for this branch                         | `contract` front not offered                                                          |
| diff touches no UI file                          | `a11y` front not offered                                                              |
| a11y finding needs a rendered page               | report it as out of static reach; the gate offers `/bb:ui-accessibility`              |
| legacy `.claude/skills/code-review/` present     | flag as superseded; the user deletes it                                               |
| uncommitted changes present                      | include in diff scope, flagged separately                                             |
| a finder agent dies                              | its front reports with the angles that returned, and says which angle is missing      |
| user picks nothing at curation                   | no edits; go to the gate                                                              |
| CI still red after 3 diagnose→fix cycles         | stop editing, report the remaining failure and the evidence                           |
| `gh` unauthenticated                             | `threads`/`ci` unavailable — say so once, offer the diff fronts                       |
| `BB_UNATTENDED` set                              | every available front runs; report-only: no curation, no edits, no gate               |

## Bundled Resources

Router support:

- `references/fronts.md` — the front catalog, the availability probe, the depth table and the fan-out shape.
- `references/verify.md` — pool, group by location, 3-state verdict, sweep, rank and cap.

Per-front method (loaded only when that front is picked):

- `references/front-correctness.md` — the five correctness angles over the diff.
- `references/front-quality.md` — the cleanup lenses, one finder, behavior-preserving.
- `references/front-rules.md` — `CODE_REVIEW_GUIDE.md` + CLAUDE.md deviations, with the citation discipline.
- `references/front-contract.md` — the brief's `## behavior` map as the acceptance contract.
- `references/front-a11y.md` — WCAG AA over the changed UI, static and diff-scoped.
- `references/front-threads.md` — PR review threads: fetch, triage, fix/answer, reply/resolve.
- `references/front-ci.md` — CI failures: evidence → diagnosis → fix → verify.

Actions and modes:

- `references/act-apply-fixes.md` — applying findings: the regression guard and the order of operations.
- `references/mode-external-pr.md` — reviewing a PR in another repo and posting the review.

Shared engine (plugin root, same criteria as `/bb:ship`):

- `references/review-checklist.md`, `references/quality-checklist.md` — the correctness and quality criteria.
- `${CLAUDE_PLUGIN_ROOT}/scripts/fetch_comments.py`, `${CLAUDE_PLUGIN_ROOT}/scripts/reply_resolve_thread.py` — thread I/O via `gh api graphql`.
