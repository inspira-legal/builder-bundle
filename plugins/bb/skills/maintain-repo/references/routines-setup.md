# Unattended setup — running bb:maintain-repo as Cloud Routines

This wires the skill to run **without your laptop**: an event-driven routine that
comments on Dependabot PRs the moment they open/update, and a daily routine that
posts the Slack digest and reconciles anything the event run left provisional.

Everything here exists because of how Cloud Routines actually behave:

- A routine runs on Anthropic infra on a **fresh clone of the default branch** —
  **no local files**, no access to your machine. Durable output is only a commit
  to a `claude/`-prefixed branch or a **connector** write (e.g. Slack).
- A routine runs **autonomously: no approval prompts**, and it can use every tool
  from an included connector — including writes — **without asking**.
- Everything it does carries **your** identity (commits, PR comments, Slack
  messages). There is no bot account.
- GitHub event triggers are subject to **per-account hourly caps**; events beyond
  the cap are **silently dropped** — which is why the daily run is mandatory, not
  optional.

> Create routines via `/schedule` or claude.ai/code/routines — **not** the
> session-scoped `/loop`/CronCreate path (that expires in 7 days, needs the app
> open and idle, has no catch-up, and dies when your Windows machine sleeps).

## 0. The non-negotiable: withhold merge capability

The never-merge guarantee comes from the routine **not being able to merge**, not
from a prompt. Before enabling anything:

- [ ] The routine's GitHub access is a token/App installation **without** PR-merge
      permission (read + PR-comment + statuses only). Leave **"Allow unrestricted
      branch pushes" OFF** — the default restricts pushes to the working branch and
      does **not** cover an API merge under your identity, so withholding the merge
      permission is what actually stops it.
- [ ] **No merge-capable connector** is attached (Slack write is fine; nothing that
      can call the GitHub merge endpoint).
- [ ] **Branch protection** is enabled on `main`/`master`/`release` (require a PR,
      block direct and force pushes) — the server-side backstop that holds even if
      the token scoping above is misconfigured.

## 1. Slack delivery uses the CONNECTOR, not your MCP tools

Session `slack_*` MCP tools are **not** available inside a routine. Add the **Slack
connector** at claude.ai/customize/connectors and confirm with a `Run now` that the
routine can post. If the connector has no draft API, do the first-week "draft"
ramp by posting to a **private channel / DM-to-self** instead.

## 2. Network scope (because the scan touches the network)

Keep the routine on the **Trusted** network preset (package registries + GitHub
reachable). The scan only needs `api.github.com` and, for `bun outdated`, the
registry. Do not widen it. Note even a "disabled" network still has the Anthropic
API channel open — another reason the routine must never execute untrusted
dependency code (it doesn't: the skill reports CI, it never `bun install`s).

## 3. Routine A — event-driven Dependabot comment

- **Trigger:** GitHub `pull_request` (actions: `opened`, `synchronize`,
  `reopened`), **Author filter: `dependabot[bot]`**. Requires the Claude GitHub
  App installed on the repo.
- **Prompt (self-contained):** run `bb:maintain-repo` Phase 1→3 for the triggering
  PR; for each `comments[]` entry, upsert the sticky comment (find marker → PATCH,
  else create). Mark the comment **provisional** if CI is still pending /
  `mergeable` is `UNKNOWN`.
- **Dedupe state:** commit `comment-state.json` to branch
  `claude/maintenance-comment-state`. Each event is its own stateless session, so
  state MUST live on a committed branch — read it from the fresh clone, write it
  back at the end. Use a **separate** branch from Routine B to avoid
  non-fast-forward push collisions (or fetch-rebase-retry on push).

## 4. Routine B — daily Slack digest + reconciler (the source of truth)

- **Trigger:** schedule, daily (e.g. a weekday morning slot; 1-hour minimum
  interval is easily satisfied). Pick an off-the-hour minute.
- **Prompt:** run `bb:maintain-repo` Phase 1→4 across **all** open PRs + alerts +
  outdated; post the grouped Slack digest (changed-only); and correct any sticky
  comment Routine A left at "provisional" now that CI has settled.
- **Why required:** it catches events the hourly webhook cap dropped, and the
  alert-only / outdated-only cases that have no PR event at all.
- **Dedupe state:** commit `slack-state.json` to branch
  `claude/maintenance-slack-state`.

## 5. Cost & caps (measure before scaling)

- The only hard figure from research is that multi-agent runs cost **~15× a single
  agent**. So inside these routines: **no sub-agent fan-out** — single-agent,
  deterministic-script-driven only, until measured.
- Cap to the daily digest + event comments; do not also poll on an interval.
- Routines draw down subscription usage and are subject to a **per-account daily
  run cap**. Read actual usage at claude.ai after week one, then decide whether to
  keep daily or drop to weekday-only.

## 6. Provisional-then-settled (the async gotcha)

A `pull_request` event fires **before** CI finishes and before `mergeable` is
computed, so the event-time comment will often read "ci pending / mergeability
unknown". That's expected: Routine A posts a **provisional** verdict fast, and
Routine B (daily) is the reconciler that corrects it once checks reach a terminal
state. There is no native "CI finished" routine trigger, so don't wait on one —
let the daily run be the source of truth.
