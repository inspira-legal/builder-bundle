# Update mode: delta discovery and surgical edits

Runs when `CODE_REVIEW_GUIDE.md` already exists. The contract: detect what
changed since the guide was written, validate **only that** with the maintainer,
and edit the guide surgically. Untouched rules stay byte-identical.

## 1. Read the existing guide

Load the full guide first: rule IDs and levels, file categories, rule
categories, last-updated date. This is the baseline every subagent compares
against.

Note which rungs the guide uses. One that ranks any rule `MEDIUM`, or carries the
field as **Severity**, gets the ladder migration in §4, on top of the delta.

## 2. Delta discovery: 3 parallel subagents

Fire all 3 in one message. Each reads the guide first, then investigates, and
returns JSON: `{new_patterns: [], changed_rules: [], removed_patterns: [],
evidence: []}`.

### Subagent 1: New patterns

> You are a codebase analyst. Read CODE_REVIEW_GUIDE.md, then compare the
> current repo against it. Find: (1) new directories/modules that fit no
> existing category; (2) new frameworks/libraries in the dependency manifests;
> (3) new file patterns not covered by the current categorization; (4) moved or
> reorganized structure. For each: `{pattern, evidence, suggested_category}`.

### Subagent 2: Drifted conventions

> You are a code conventions analyst. Read CODE_REVIEW_GUIDE.md, then verify
> its rules still match reality. Find: (1) rules that no longer describe the
> code (naming changed, import pattern changed); (2) HIGH rules now followed
> inconsistently; (3) new test patterns; (4) new error-handling approaches. For
> each: `{rule_id, current_description, actual_state, evidence,
recommendation: update|remove|keep}` with concrete example files.

### Subagent 3: Git history since the guide

> You are a git history analyst. Get the guide's last change date
> (`git log -1 --format=%ai CODE_REVIEW_GUIDE.md`; fall back to the last 30
> days if uncommitted). List commits after it and look for: architectural
> changes, major new dependencies, large refactors (many files in one commit),
> CI/CD changes. Use `git log --oneline --after=<date>` and `git diff --stat`
> on high-impact commits. For each finding: pattern/rule impact + the commit
> hash as evidence.

## 3. Consolidate and short-circuit

Merge the three results, dedupe, group by type (new / drifted / obsolete). If
**nothing** was found, report "no significant changes since the guide was last
updated" and stop, no interview, no edits. A three rung guide is the one exception:
with no delta but a rule still at `MEDIUM`, say so and run the ladder migration
alone.

Otherwise print the summary (new patterns / rules to revisit / patterns
obsoletos, each with evidence) and run the **update-mode interview**
(`interview.md`). One item at a time, only on changed items.

## 4. Surgical edit

Use the **Edit** tool, never rewrite the whole file:

- **Add** approved new rules with the next free ID in their domain (PAT-003
  exists → PAT-004). Level from the maintainer's answer; category per the
  guide-template vocabulary (an older guide using **Lens** keeps that heading);
  real Do/Don't examples when available.
- **Update** approved drifted rules: change only the fields that drifted,
  **preserve the original ID**, never renumber.
- **Remove** rules the maintainer approved for removal.
- **Preserve** everything else exactly as-is.
- **Migrate the ladder** when the guide still ranks a rule `MEDIUM`, or still calls
  the field **Severity**. The collapse is deterministic, so it takes no interview: read
  it from the table in the plugin-root `references/finding-levels.md` (`MEDIUM` and a
  rule with no level to `LOW`, `HIGH` unchanged), rewrite the levels section from
  `guide-template.md`, rename each rule's **Severity** field to **Level**, and regroup
  the rules under `### HIGH` and `### LOW`. A verdict rule stated in three rungs
  migrates with the ladder. Every rule already at `HIGH` or `LOW` keeps its own text
  byte-identical, and this is what clears the drift line `/bb:review` reports.
- Update the "Last updated" date and append a row to the change history
  table. The ladder migration gets its own row, so a reader can tell the vocabulary
  change from the rule changes.
