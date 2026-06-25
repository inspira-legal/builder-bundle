---
name: review-changes
description: Review the changes on the current branch for correctness bugs and quality smells, then suggest the next step — report-only, never edits. Runs ship's two-pass review engine (correctness + quality) over the branch diff without heading toward landing. Use when the user says "review my changes", "review this diff", "review the branch", "any bugs in my diff", "check my changes before I ship", or "is this diff good?". Do NOT use to apply fixes or finalize a PR (use /ofc:ship), to apply quality cleanups (use /ofc:tidy), or to just summarize what changed without judging it (use /ofc:gather-branch-context).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.0.0
---

# Review Changes

A standalone correctness + quality review of the branch diff — the same engine
`/ofc:ship` runs in its quality pass, but **report-only**: it surfaces findings
and points you at the next step, and lands nothing. The door to the review engine
when you want a read on the diff without committing to ship.

**Report-only — it never edits code.** Findings are surfaced for you to act on;
applying them is `/ofc:tidy` (quality) or `/ofc:ship` (correctness + landing).

## Prerequisites

Inside a git repository with a resolvable base branch. No `gh` needed — this reads
the local diff, not a PR.

## Workflow

1. **Get the change scope.** Resolve the base (the repo's default branch unless the
   user names one) and read the diff inline — `git diff <base>...HEAD` plus any
   uncommitted changes (`git diff`). Read each hunk **with its surrounding file
   context** (open the file, not just the diff) before judging it.

2. **Fan out one read-only agent per checklist area.** Each gets the diff scope, the
   path to the plugin-root `references/review-checklist.md`, and ONE lens:
   - `logic-edges` — logic errors, edge cases, error handling
   - `async-state` — async/concurrency, state & lifecycle
   - `contracts-security` — contract breaks, security, type safety
   - `quality` — the entire Pass 2 (reuse, simplification, dead weight, efficiency, altitude, consistency)

   Each verifies every finding against the actual file (not just the diff) and returns
   `file:line | what | evidence | suggested fix | confidence`. For tiny diffs (≲2 files
   / ≲100 lines), skip the fan-out and apply the checklist in the main context. If a
   `.ofc/tasks/*/shape.md` brief matches this branch, pass it to the agents as the
   intended scope — review the diff against what was agreed (did it build the shaped
   thing, and only that?). Its `## behavior` map is the acceptance contract: a mapped
   `WHEN … THEN …` row with no corresponding code or test is a finding.

3. **Dedupe and print a grouped report — no edits.** Merge overlapping findings, then
   print two groups:
   - **Correctness** (Pass 1) — bugs, each `file:line | what | evidence | suggested fix | confidence`
   - **Quality** (Pass 2) — smells, same shape

4. **Suggest the next step** from what surfaced:
   - clean (no findings) → `/ofc:ship`
   - only quality smells → `/ofc:tidy`
   - correctness bugs → offer to fix them now, or hand to `/ofc:ship` (which applies high-confidence fixes and lands)

## Edge cases

| WHEN | THEN |
| --- | --- |
| diff vs base is empty | report "no changes to review", stop |
| no findings | report "clean", suggest `/ofc:ship` |
| only quality smells | report them, suggest `/ofc:tidy` |
| correctness bugs found | report them, offer to fix or hand to `/ofc:ship` |
| uncommitted changes present | include them in scope, flag them separately in the report |
| not a git repo / no base resolvable | report the error, stop |

## Bundled Resources

The review criteria live at the plugin root, shared with `/ofc:ship` so a diff is
judged identically wherever it's reviewed:

- `references/review-checklist.md` — the two passes (correctness + quality) and what
  each lens looks for.
- `references/quality-checklist.md` — the Pass 2 criteria in full (the six criteria,
  scope/behavior/clarity rules, over-simplification guard).
