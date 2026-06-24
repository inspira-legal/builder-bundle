<div align="center">

# ofc-skills

[![github](https://img.shields.io/badge/github-inspira--legal%2Fofc--skills-111111?style=flat-square&logo=github)](https://github.com/inspira-legal/ofc-skills)

_Oficina (`ofc`) — a claude code plugin of agent skills grouped by use, with an operating-context hook shipped alongside them._

</div>

add the marketplace, then install the one plugin:

```bash
claude plugin marketplace add inspira-legal/ofc-skills
claude plugin install ofc@inspira-legal
```

it ships a `SessionStart` operating-context hook, auto-active on install. skills are invoked as `/ofc:<skill>` — e.g. `/ofc:shape`, `/ofc:ship`, `/ofc:answer-yourself`.

## what's inside

one plugin, `ofc`; the skills are organized by use.

### shape & ship — write & ship code, you-driven

| skill                        | description                                                                                                                                                              |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `/ofc:shape`                 | align on the idea before building — develop, loop on gray areas via questions, validate                                                                                  |
| `/ofc:implement`             | implement a validated shape brief — build the slices, run the gate, then offer to ship (or chain straight to it)                                                         |
| `/ofc:ship`                  | land the branch your way — review + green the checks, then push to a branch, prep a push to main, or open a PR & auto-tend it (handle comments, green CI, keep watching) |
| `/ofc:address-comments`      | address review comments on github PRs                                                                                                                                    |
| `/ofc:gather-branch-context` | summarize all changes on the branch vs main                                                                                                                              |
| `/ofc:improve-code`          | improve a diff's quality with a hard regression guard (no bugs)                                                                                                          |

### loops — run across time (scheduled / event-driven)

there's no dedicated overnight skill — the unattended path **is** the trio: a [Cloud Routine](plugins/ofc/references/routines.md) sets `OFC_UNATTENDED` and runs `/ofc:implement` → `/ofc:ship` against a committed brief, building the whole backlog and leaving a draft PR. for that path, never-merge is enforced by **capability scoping** — the routine runs with a token that has no merge/branch-push permission and no merge-capable connector — backed by GitHub branch protection. server-side controls, not a local hook.

| skill                  | description                                                              |
| ---------------------- | ------------------------------------------------------------------------ |
| `/ofc:maintain-repo`   | triage PRs + dependabot/outdated, report what's mergeable (never merges) |
| `/ofc:digest-research` | scheduled, read-only research/monitoring digest to slack or a branch     |

### helpers — standalone

| skill                  | description                                                                      |
| ---------------------- | -------------------------------------------------------------------------------- |
| `/ofc:research-topic`  | deep research using parallel agents                                              |
| `/ofc:research-code`   | find, clone, and explore relevant repos                                          |
| `/ofc:write-readme`    | generate a minimal centered-header README from repo facts                        |
| `/ofc:answer-yourself` | honest, decisive recommendation — commit, name the unseen tension, no sycophancy |

develop locally:

```bash
git clone git@github.com:inspira-legal/ofc-skills.git
claude --plugin-dir ./ofc-skills/plugins/ofc    # load the plugin from disk to test
```

<sub>`/ofc:improve-code` is adapted from Claude Code's `/simplify` (Anthropic, Apache-2.0). individual components retain their original licenses.</sub>
