---
name: tidy-pr
description: Tidy the open PR for the current branch — a lightweight, curated pass over its review threads. You pick which unresolved threads to handle; it fixes or answers, replies, and resolves them, and can polish the title/body to convention. No CI watch, no quality pass, no merge, no PR creation. Use when the user says "tidy my PR", "handle these PR comments", "address PR feedback", "reply to review threads", "clean up the PR", or "respond to PR review". Do NOT use for full PR finalization with review + CI watch (use /ofc:ship), to open a PR (use /ofc:ship), or to review the diff for bugs (use /ofc:review-changes).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.1.0
---

# Tidy PR

A lightweight, **curated** pass over an open PR's review threads. You stay in the
loop — you pick which unresolved threads to handle — and it does the mechanical
work: apply the fix or compose the answer, reply, and resolve. The hand-tended
counterpart to `/ofc:ship`'s automatic finalization: no review fan-out, no CI
watch, no quality pass, no merge, no PR creation. Reach for it when a PR just needs
a few threads cleared, not the full ship treatment.

## Prerequisites

- `gh` authenticated (`gh auth status`). If not, instruct the user to run `gh auth login`.
- An open PR for the current branch (`gh pr view --json number,url,title,baseRefName`).
  If none exists, tell the user and suggest `/ofc:ship` to create one — this skill
  doesn't open PRs.

## Workflow

1. **Fetch the threads** — `python ${CLAUDE_PLUGIN_ROOT}/scripts/fetch_comments.py`
   prints conversation comments, reviews, and review threads (with `id` and
   `isResolved`) as JSON.

2. **Present the unresolved threads, numbered**, each with a one-line summary of what
   handling it would take (a code fix vs. a reply). Resolved threads are not shown.

3. **Let the user curate.** Ask which numbered threads to handle. Handle only those —
   this is the curated mode; there is no auto-triage of everything.

4. **Handle each picked thread:**
   - **fix** (code change): apply it in the main context, commit in a logical unit
     (conventional style; no AI attribution), push to the PR branch, then reply with
     what changed + the commit sha and resolve —
     `python ${CLAUDE_PLUGIN_ROOT}/scripts/reply_resolve_thread.py --thread-id <id> --body "Fixed in <sha>: <one-liner>"`
   - **answer** (no code): reply but do NOT resolve — the reviewer closes it —
     `python ${CLAUDE_PLUGIN_ROOT}/scripts/reply_resolve_thread.py --thread-id <id> --body "..." --no-resolve`

5. **Optionally polish title/body.** Offer to bring the PR title/body to convention
   (conventional-commit title; Context → Changes → Breaking Changes body, or the repo's
   `.github/pull_request_template.md`). Apply only if the user wants it.

6. **Report what was handled** as a table: `# | file:line | thread summary | verdict | action taken`.

## Edge cases

| WHEN | THEN |
| --- | --- |
| no open PR for the branch | tell the user, suggest `/ofc:ship` to create one, stop |
| `gh` not authenticated | prompt `gh auth login`, stop |
| no unresolved threads | report "nothing to address", offer the title/body polish |
| user selects no threads | do nothing, stop (optionally offer the polish) |
| fix-thread code change made | reply with what changed + commit sha, resolve, push to the PR branch |
| answer-thread | reply, do NOT resolve (the reviewer closes it) |
| `gh` hits auth/rate issues mid-run | prompt `gh auth login`, then retry |

Pushing fixes to the PR branch is reversible, so this runs without pausing; merge,
approve, and force-push stay yours — tidy-pr never runs them.

## Bundled Resources

Shared plugin-root scripts (also used by `/ofc:ship`):

- `${CLAUDE_PLUGIN_ROOT}/scripts/fetch_comments.py` — fetch conversation comments,
  reviews, and review threads (thread IDs + resolved state) via `gh api graphql`.
- `${CLAUDE_PLUGIN_ROOT}/scripts/reply_resolve_thread.py` — reply to a thread and/or
  resolve it (`--thread-id`, `--body`, `--no-resolve`).
