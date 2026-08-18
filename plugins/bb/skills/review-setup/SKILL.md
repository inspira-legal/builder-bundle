---
name: review-setup
description: Gera ou atualiza o CODE_REVIEW_GUIDE.md do repositório: descoberta automática com subagentes paralelos, entrevista com o mantenedor pra validar cada regra, e o guia escrito na raiz como fonte de verdade que o /bb:review consome. Gera do zero quando não há guia; quando já existe, atualiza cirurgicamente só o que mudou. Use quando o usuário disser "configura o code review", "gera o guia de review", "cria o CODE_REVIEW_GUIDE", "atualiza o guia de review", "o guia de review tá desatualizado", ou quando /bb:review apontar drift. NÃO use pra revisar código (use /bb:review).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 2.3.0
---

# Review setup

Produce the repo's `CODE_REVIEW_GUIDE.md`, the single source of truth for what
"good" means in this codebase: rules with IDs, severities, and evidence, validated
by the maintainer in an interview. `/bb:review` reads it fresh on every run;
developers read it before opening PRs. **The guide is the only output**, no
per-repo skill is generated; the review engine is `/bb:review` itself.

This SKILL.md is the router: it picks the mode, and each phase's method lives in
its own reference, loaded only when that phase runs.

## Mode selection

- `CODE_REVIEW_GUIDE.md` absent at the repo root → **setup** (full generation).
- Present → **update** (delta only: never re-interview what didn't change).

If `$ARGUMENTS` names a focus area, constrain discovery (either mode) to that
domain.

## Setup mode

1. **Discovery** → `references/discovery.md`: 5 parallel read-only subagents
   (stack & structure, patterns & conventions, git history & PRs, CI/CD &
   quality, security & contracts), then rule extraction into
   Confirmed/Candidate tables with IDs, severities, and evidence.
2. **Interview** → `references/interview.md`: the maintainer validates via
   `AskUserQuestion` (PT-BR): confirmed rules in one batch, candidates one at a
   time. Every rule in the guide was accepted by a human, none slipped in.
3. **Generate** → `references/guide-template.md`: write `CODE_REVIEW_GUIDE.md`
   at the repo root from the validated rules.

## Update mode

Follow `references/update-delta.md`: read the existing guide, run 3 delta
subagents (new patterns, drifted rules, git history since the guide's last
change), interview **only** on what changed, then edit the guide surgically:
preserve rule IDs, never renumber, never rewrite untouched sections.

## Closing

No handoff gate, report and stop:

- Name what was written/changed: rule counts per severity, new/updated/removed
  IDs (update mode).
- Remind: "O guia entra em vigor no próximo `/bb:review`. Ele lê o
  CODE_REVIEW_GUIDE.md fresh a cada run."
- If a legacy generated skill exists at `.claude/skills/code-review/SKILL.md`,
  flag it as superseded by `/bb:review` and suggest the user delete it (their
  action, not yours).
- Suggest committing the guide so CI-side and teammates' reviews see it.

## Edge cases

| WHEN                                             | THEN                                                                  |
| ------------------------------------------------ | --------------------------------------------------------------------- |
| update mode, no changes detected by any subagent | report "sem mudanças significativas desde a última atualização", stop |
| repo > 1000 files                                | sample representative files per directory instead of exhaustive scans |
| maintainer rejects every candidate               | guide ships with confirmed rules only; thin is fine, invented is not  |
| legacy `.claude/skills/code-review/` present     | flag as superseded; never regenerate it                               |
| not a git repo                                   | report the error, stop                                                |

## Bundled resources

- `references/discovery.md`: the 5 discovery subagent prompts + rule extraction format.
- `references/interview.md`: the `AskUserQuestion` validation protocol (setup and update variants).
- `references/guide-template.md`: the CODE_REVIEW_GUIDE.md template and generation rules.
- `references/update-delta.md`: delta discovery, incremental interview, surgical edits.
