# Cloud Routines — the unattended trio, AFK to a draft PR

A Cloud Routine is the **only true AFK option** (see
`../hooks/scheduling-decision.md`): it runs on Anthropic infra from a fresh
clone, with no local files and no mid-run approval prompts, and its only durable
output is a commit on a `claude/` branch / a draft PR. That makes it the home for
running the trio overnight: a routine fires, sets `BB_UNATTENDED`, and runs
`/bb:delegate <slug>` against one shaped brief — `delegate` drives the whole
`implement → ship` chain, building the backlog and leaving a
reviewed-in-the-morning draft PR.

There's no dedicated overnight skill — the unattended path is the same
`/bb:delegate` you run at your desk, with the `BB_UNATTENDED` frame changing the
behavior underneath it (no questions, fixed draft-PR destination, capped
retries). The frame is injected by the SessionStart hook when `BB_UNATTENDED` is
truthy.

## When to reach for a routine

- **The work must run while your laptop is closed.** A session `/loop` expires
  and dies on sleep; a routine survives. If you're at your desk, just run
  `/bb:implement` directly — you don't need a routine.
- **You have a committed, validated brief.** The fresh clone can only see what's
  in git, so `.bb/tasks/<slug>/spec.md` (brief + `## tasks` checklist — see the
  plugin-level `references/task-state.md`) must be committed to the target repo.
  No brief → nothing to build → don't schedule one.
- **One brief per routine.** Each routine targets a single `<slug>`. Queue a
  second brief as a second routine; don't try to make one routine drain a backlog
  of unrelated briefs.

## The never-merge guarantee is server-side, not prose

The unattended frame tells the run to stop at a draft PR — but that's UX, not the
safety boundary. Merge and protected-branch push stay out of reach because of how
the routine is provisioned, and that holds even if the frame is ignored:

- **Capability-scope the token.** The routine's GitHub token / App has **no merge
  permission**, "Allow unrestricted branch pushes" is **OFF** (so it can only push
  `claude/` branches), and no merge-capable connector is attached.
- **Enable branch protection** on `main` / `master` / `release` (require a PR,
  block direct and force pushes) — the server-side backstop that holds even if the
  token scoping above is misconfigured.
- **Scope the outward reach the same way.** A skipped question must not be able to
  resolve into a post somewhere public, so make that unreachable rather than
  discouraged: install the App on **only** the repos the routine works, and attach
  **no** outward connector (Slack, email, social). What's left is the run's own
  draft PR and its threads — which is exactly the documented lean.
- **Network:** the Trusted preset (registries + GitHub) is enough.

## The routine prompt

Generate it with `scripts/scaffold_routine.py` (see below) so the slug, repo, and
base branch are filled in and the wording stays consistent. The prompt is
self-contained — the routine has no session memory:

> Set `BB_UNATTENDED=1`. Run `/bb:delegate <slug>` against the brief for
> `<slug>` in this repo: it builds every unchecked task in the brief, keeping the
> local gate green (cap retries at 3 on known-flake signatures only), commits per
> slice to a `claude/<slug>` branch, then chains into `/bb:ship` to open a
> **DRAFT** PR against `<base>` and watch it to resolution (green CI + handled
> review-bot threads), bounded by the run budget. Do **not** merge, do **not**
> push to a protected branch. If a task or the gate blocks unrecoverably, flip
> the brief's `status` to `blocked`, write the blocker into the PR description,
> and exit.

## Trigger & cadence

- Trigger: schedule, daily, an overnight slot (the 1-hour minimum is easily met).
  Pick an off-the-hour minute.
- A routine fires against a `<slug>`; with the brief already `done` (or every task
  checked), the run is a no-op (delegate finds nothing to build and nothing to
  open) — it reports and exits rather than inventing work.
- **Single-agent only** inside the run until you've measured cost — no sub-agent
  fan-out (≈15× tokens compounds per run). Routines have a per-account daily run
  cap; read your usage at claude.ai after the first week.

## Morning

You review the draft PR and merge what you want. That review/land step is the
binding human constraint by design — start with one brief and one small task
category before trusting larger ones.
