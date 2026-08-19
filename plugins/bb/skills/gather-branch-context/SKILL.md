---
name: gather-branch-context
description: Coleta e resume todas as mudanças da branch atual comparada com a main. Use quando o usuário disser "compara com a main", "contexto da branch", "o que mudou nessa branch", "resume minha branch", "diff contra a main", ou "o que eu fiz nessa branch". NÃO use pra julgar o diff por bugs ou qualidade (use /bb:review), consertar ou esverdear uma PR (use /bb:ship), nem abrir uma PR (use /bb:ship). Isso só resume, nunca edita.
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 2.0.0
---

# Branch context

Gather all changes on the current branch relative to the base branch (main/master) and present a structured summary.

## Workflow

### 1. Gather context

Run the shared plugin-root script:

```
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/gather_context.py
```

Optional flags:

- `--base <branch>` to compare against a specific branch (default: repo's default branch)
- `--repo <path>` to target a specific repo

Returns JSON with: `branch`, `base_branch`, `merge_base`, `commit_log`, `commit_count`, `diff_stat`, `files_changed`, `full_diff`, `uncommitted_changes` (plus `upstream` and `pr_template` when available, used by `/bb:ship`).

If the script returns an `error` field, report it and stop.

### 2. Present the summary

Show a structured overview:

**Branch info:**

```
Branch: feature/my-feature (12 commits ahead of main)
```

**Commit history**: show the oneline log.

**Files changed**: group by change type and directory:

```
Modified:
  src/components/  Button.tsx, Card.tsx
  src/utils/       format.ts
Added:
  src/hooks/       useDebounce.ts
Deleted:
  src/legacy/      old-helper.ts
```

**Diff stats**: show the stat summary (files changed, insertions, deletions).

**Uncommitted changes**: if any, list them separately with a warning.

### 3. Analyze the diff

Read through the full diff and provide:

1. **Change summary**: what the branch does, grouped by purpose (not by file)
2. **Potential issues**: anything that looks risky, incomplete, or inconsistent:
   - TODO/FIXME comments added
   - Console.log / debug statements left in
   - Large files or binary additions
   - Missing test coverage for new code
   - Breaking API changes
3. **Suggestions**: optional, only if something clearly stands out

### 4. Report and stop

This skill summarizes. It has no handoff gate. Close the report by naming the natural next command in one line, without asking:

- Clean and ready: "Pra abrir a PR: `/bb:ship`."
- Uncommitted changes: point them out with the warning above.
- Issues found: "Pra revisar e corrigir: `/bb:review`."
