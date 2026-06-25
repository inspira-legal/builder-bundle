---
name: gather-branch-context
description: Gather and summarize all changes on the current branch compared to main. Use when user says "compare against main", "branch context", "what changed on this branch", "summarize my branch", "diff against main", "review my changes", or "what did I do on this branch". Do NOT use to fix or green a PR (use /ofc:ship), open a PR (use /ofc:ship), or improve the diff's quality (use /ofc:tidy) — this only summarizes, it never edits.
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.0.0
---

# Branch Context

Gather all changes on the current branch relative to the base branch (main/master) and present a structured summary.

## Workflow

### 1. Gather Context

Run the shared plugin-root script:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gather_context.py
```

Optional flags:

- `--base <branch>` to compare against a specific branch (default: repo's default branch)
- `--repo <path>` to target a specific repo

Returns JSON with: `branch`, `base_branch`, `merge_base`, `commit_log`, `commit_count`, `diff_stat`, `files_changed`, `full_diff`, `uncommitted_changes` (plus `upstream` and `pr_template` when available, used by `/ofc:ship`).

If the script returns an `error` field, report it and stop.

### 2. Present Summary

Show a structured overview:

**Branch info:**

```
Branch: feature/my-feature (12 commits ahead of main)
```

**Commit history** — show the oneline log.

**Files changed** — group by change type and directory:

```
Modified:
  src/components/  Button.tsx, Card.tsx
  src/utils/       format.ts
Added:
  src/hooks/       useDebounce.ts
Deleted:
  src/legacy/      old-helper.ts
```

**Diff stats** — show the stat summary (files changed, insertions, deletions).

**Uncommitted changes** — if any, list them separately with a warning.

### 3. Analyze the Diff

Read through the full diff and provide:

1. **Change summary** — what the branch does, grouped by purpose (not by file)
2. **Potential issues** — anything that looks risky, incomplete, or inconsistent:
   - TODO/FIXME comments added
   - Console.log / debug statements left in
   - Large files or binary additions
   - Missing test coverage for new code
   - Breaking API changes
3. **Suggestions** — optional, only if something clearly stands out

### 4. Offer Next Steps

Based on the state of the branch:

- If clean and ready: "Want me to open a PR? (/ofc:ship)"
- If uncommitted changes: "You have uncommitted changes — want to commit first?"
- If issues found: "Want me to fix any of these before opening a PR?"
