# Landing

The orchestrator owns every PR the fronts open. This page covers following CI, when the
orchestrator merges and how, the order of merges, and repos that release on every merge.

## Follow CI

Each side session opens its PR with Auto-fix on, so the app wakes it on CI failures,
review comments and conflicts. The orchestrator follows each PR's checks with
`gh pr checks` or `gh pr view`, tells the person when one turns green or stays red, and
sends a stuck failure back to its side session.

## Merge only what the person allowed

The orchestrator merges a PR when all of these hold:

- **The person allowed it**, for that PR or for the whole run ("merge when it is green").
  Without that permission, report the PR green and ask.
- **CI is green** on the head commit.
- **The repository's own rules allow it**: the reviews it requires, its branch protection,
  and any rule in its `CLAUDE.md`, `CONTRIBUTING.md` or review guide. Never bypass one,
  with `--admin` or any other way.

Merge with the method the repository uses (the one its settings allow and its history
shows; squash when both allow it), pinned to the head that was checked:

```bash
gh pr merge PR_NUMBER --squash --match-head-commit HEAD_SHA
```

Where the repository's rules forbid an agent merge, or require something only the person
can do, hand the person the command and say what it waits on.

The orchestrator merges instead of the side session because the auto mode classifier
tends to deny a merge a side session runs.

## Merge in sequence

1. Merge one PR.
2. Wait for GitHub to recompute the next PR's mergeable state before merging it.
3. Repeat for the next PR.

Tell the person that PRs merged in sequence are tested together only by `main`'s CI, and
follow that run. After each merge, tell every side session with an open PR in the same
area to merge `main` into its branch.

## Repos that release on every merge

Check whether the repository publishes a release on each merge (semantic-release, a
release workflow on `main`). There, the commit type decides the version: `fix` cuts a
patch, `feat` a minor, a breaking change a major. Make sure the squash title carries the
type the change deserves before merging.
