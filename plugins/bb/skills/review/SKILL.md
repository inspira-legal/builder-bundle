---
name: review
description: Revisa a mudança de ponta a ponta — diff, threads da PR e CI — num fluxo interativo. Reporta os achados das três fontes (diff da branch em 2 passes correção + qualidade; comentários de review da PR aberta; checks de CI falhando, com diagnóstico antes de editar), você escolhe o que aplicar, ele corrige com guarda de regressão, responde/resolve threads e re-reporta. Lê o CODE_REVIEW_GUIDE.md do repo quando existir. Também revisa uma PR externa por número e posta o review. Use quando o usuário disser "revisa minhas mudanças", "revisa a PR", "revisa esse diff", "tem bug nisso?", "responde os comentários da PR", "o CI quebrou", "conserta o CI", "limpa esse código", "simplifica o diff", ou "revisa a PR #42 do repo X". NÃO use pra abrir/finalizar uma PR e acompanhar até o fim (use /bb:ship), nem pra triagem de todas as PRs abertas do repo (use /bb:maintain-repo).
license: Apache-2.0
metadata:
  author: Athena Briana - github.com/athenabriana; quality-pass material adapted from Claude Code's /simplify (Anthropic, Apache-2.0)
  version: 2.0.0
---

# Review

One review skill, three sources of findings: the **branch diff** (correctness +
quality), the open PR's **review threads**, and failing **CI checks**. The flow is
interactive — report → you pick → apply → reply/resolve → re-report — and repeats
until you close it. It fixes what you approve; it never merges, never approves,
never force-pushes.

This SKILL.md is the router. Each source's method lives in its own reference and
is loaded **only when that source is in scope**.

## Prerequisites

Inside a git repository. `gh` authenticated (`gh auth status`) for anything
PR/CI-related; diff-only review needs no `gh`.

## Step 0 — Load the review context

- **Repo guide:** if `CODE_REVIEW_GUIDE.md` exists at the repo root, read it fresh
  (never cached). Its rules extend the bundle checklists: findings that match a
  guide rule cite its ID, and rule severities (HIGH/MEDIUM/LOW) rank the report.
  No guide → use the bundle checklists alone and add one line to the report:
  "Sem CODE_REVIEW_GUIDE.md — regras específicas do repo via /bb:review-setup."
- **Legacy custom skill:** if `.claude/skills/code-review/SKILL.md` exists (an old
  generated per-repo review skill), note in the report that `/bb:review` +
  `CODE_REVIEW_GUIDE.md` supersede it and the user can delete it.
- **Stack judgment:** when a finding turns on a stack choice (library, pattern,
  architecture), consult the manifesto per the plugin-root
  `references/consult-manifesto.md` before calling it wrong.

## Step 1 — Resolve what's being reviewed

- **External PR** (user names a repo and/or PR number that isn't the current
  branch's): external mode — follow `references/external-pr.md`, then stop
  (the other sources don't apply). Read-only over that PR; posting the review
  requires explicit confirmation.
- **Current branch with an open PR** (`gh pr view`): full scope — diff + threads
  - CI, all three sources.
- **No open PR**: diff-only scope. Threads and CI are skipped, not failed.

## Step 2 — Gather findings per source in scope

- **Diff** → `references/diff-review.md` — the two-pass engine (correctness +
  quality) shared with `/bb:ship`, lens fan-out for non-tiny diffs, the task
  brief as intended scope when one matches.
- **Threads** → `references/threads.md` — fetch unresolved review threads, one
  line each with what handling it would take (fix vs. answer).
- **CI** → `references/ci-diagnosis.md` — evidence first: collect failing-check
  logs and produce a diagnosis before any edit.

## Step 3 — Report

One unified report, numbered items grouped by source:

- **Correctness** — `# | file:line | what breaks | trigger | suggested fix | confidence` (+ rule ID when a guide rule matches)
- **Quality** — same shape, smells only
- **Threads** — `# | file:line | thread summary | fix or answer`
- **CI** — `# | failing check | root cause | evidence | proposed fix`

Clean everywhere → say so and jump to the gate (step 6).

## Step 4 — Curate (the user picks)

One `AskUserQuestion` (PT-BR, `multiSelect`): which numbered items to handle now.
Options group naturally (e.g. "Todas as correções", "Só os threads", specific
numbers via "Other"). "Nenhum — encerrar" is always an option. Under
`BB_UNATTENDED` there is no curation: report-only, no edits, stop.

## Step 5 — Apply what was picked

Follow `references/apply-fixes.md` — one change at a time, justified, with the
regression guard; quality edits are strictly behavior-preserving. Then:

- **fix-threads**: commit (conventional style, no AI attribution), push to the PR
  branch, reply with the sha and resolve (`references/threads.md`, handling table).
- **answer-threads**: reply, do NOT resolve — the reviewer closes it.
- **CI fixes**: push and re-check the failing workflow; cap at 3 diagnose→fix
  cycles, then report what's still red instead of thrashing.

Re-report as a table: `# | item | action taken | commit/status`.

## Step 6 — Gate

Per the plugin-root `references/handoff-gate.md`, one PT-BR question. Options by
state: more items still open → "Aplicar mais" (loops to step 4); diff-only scope
and clean/handled → "Abrir a PR — rodo /bb:ship"; always "Encerrar aqui" (what
stays saved: the report; how to resume: `/bb:review`).

## Edge cases

| WHEN                                         | THEN                                                           |
| -------------------------------------------- | -------------------------------------------------------------- |
| diff vs base empty and no PR                 | report "nada pra revisar", stop                                |
| no open PR (review-sem-PR)                   | diff-only scope; gate offers `/bb:ship` to open one            |
| `CODE_REVIEW_GUIDE.md` absent                | bundle checklists only; one-line pointer to `/bb:review-setup` |
| legacy `.claude/skills/code-review/` present | flag as superseded; the user deletes it                        |
| uncommitted changes present                  | include in diff scope, flagged separately                      |
| user picks nothing at curation               | no edits; go to the gate                                       |
| CI still red after 3 diagnose→fix cycles     | stop editing, report the remaining failure and the evidence    |
| `gh` unauthenticated with PR/CI in scope     | prompt `gh auth login`; continue diff-only meanwhile           |
| `BB_UNATTENDED` set                          | report-only: no curation, no edits, no gate                    |

## Bundled Resources

Per-source method (loaded only when that source is in scope):

- `references/diff-review.md` — two-pass diff review: scope, lens fan-out, brief-as-contract.
- `references/apply-fixes.md` — applying findings: the regression guard and the order of operations.
- `references/threads.md` — PR review threads: fetch, curate, fix/answer, reply/resolve.
- `references/ci-diagnosis.md` — CI failures: evidence → diagnosis → fix → verify.
- `references/external-pr.md` — reviewing a PR in another repo and posting the review.

Shared engine (plugin root, same criteria as `/bb:ship`):

- `references/review-checklist.md`, `references/quality-checklist.md` — the two passes.
- `${CLAUDE_PLUGIN_ROOT}/scripts/fetch_comments.py`, `${CLAUDE_PLUGIN_ROOT}/scripts/reply_resolve_thread.py` — thread I/O via `gh api graphql`.
