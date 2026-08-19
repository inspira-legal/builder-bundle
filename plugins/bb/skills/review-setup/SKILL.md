---
name: review-setup
description: Generates or updates the repository's CODE_REVIEW_GUIDE.md. Runs automatic discovery with parallel subagents, interviews the maintainer to validate every rule, and writes the guide at the root as the source of truth /bb:review consumes. Generates from scratch when there is no guide; when one exists, it updates surgically, only what changed. Use when the user says "set up code review", "generate the review guide", "create the CODE_REVIEW_GUIDE", "update the review guide", "the review guide is stale", or when /bb:review reports drift. Don't use it to review code (use /bb:review).
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
- Remind: "The guide takes effect on the next `/bb:review`. It reads
  CODE_REVIEW_GUIDE.md fresh on every run."
- If a legacy generated skill exists at `.claude/skills/code-review/SKILL.md`,
  flag it as superseded by `/bb:review` and suggest the user delete it (their
  action, not yours).
- Suggest committing the guide so CI-side and teammates' reviews see it.

## Edge cases

| WHEN                                             | THEN                                                                  |
| ------------------------------------------------ | --------------------------------------------------------------------- |
| update mode, no changes detected by any subagent | report "no significant changes since the last update", stop           |
| repo > 1000 files                                | sample representative files per directory instead of exhaustive scans |
| maintainer rejects every candidate               | guide ships with confirmed rules only; thin is fine, invented is not  |
| legacy `.claude/skills/code-review/` present     | flag as superseded; never regenerate it                               |
| not a git repo                                   | report the error, stop                                                |

## Bundled resources

- `references/discovery.md`: the 5 discovery subagent prompts + rule extraction format.
- `references/interview.md`: the `AskUserQuestion` validation protocol (setup and update variants).
- `references/guide-template.md`: the CODE_REVIEW_GUIDE.md template and generation rules.
- `references/update-delta.md`: delta discovery, incremental interview, surgical edits.
