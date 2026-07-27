# Diff review — the two-pass engine over the branch diff

The same engine `/bb:ship` runs in its quality pass. Here it produces the
**Correctness** and **Quality** sections of the report; applying anything waits
for the user's curation.

## 1. Get the change scope

Resolve the base (the repo's default branch unless the user names one) and read
the diff — `git diff <base>...HEAD` plus any uncommitted changes (`git diff`),
flagged separately in the report. Read each hunk **with its surrounding file
context** (open the file, not just the diff) before judging it.

## 2. Fan out one read-only agent per lens

Each agent gets the diff scope, the path to the plugin-root
`references/review-checklist.md`, the repo's `CODE_REVIEW_GUIDE.md` rules for its
domain (when the guide exists), and ONE lens:

- `logic-edges` — logic errors, edge cases, error handling
- `async-state` — async/concurrency, state & lifecycle
- `contracts-security` — contract breaks, security, type safety
- `quality` — the entire Pass 2 (plugin-root `references/quality-checklist.md`:
  reuse, simplification, dead weight, efficiency, altitude, consistency)

Each verifies every finding against the actual file (not just the diff) and
returns `file:line | what | evidence | suggested fix | confidence`, citing the
guide rule ID when one matches. For tiny diffs (≲2 files / ≲100 lines), skip the
fan-out and apply the checklist in the main context.

## 3. Review against the brief, when one matches

If a task brief matches this branch (resolve per the plugin-root
`references/task-state.md` — `.bb/tasks/<slug>/spec.md`), pass it to the agents
as the intended scope:
review the diff against what was agreed — did it build the shaped thing, and
only that? Its `## behavior` map is the acceptance contract: a mapped
`WHEN … THEN …` row with no corresponding code or test is a finding.

## 4. Dedupe and rank

Merge overlapping findings across lenses. Rank by severity: guide-rule matches
use the guide's HIGH/MEDIUM/LOW; unmatched findings rank by confidence and blast
radius. The output feeds the unified report — no edits happen here.
