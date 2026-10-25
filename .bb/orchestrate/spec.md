---
status: pending
created: 2026-10-24
slug: orchestrate
---

# /bb:orchestrate: the session that delegates everything

`/bb:orchestrate` turns the current Claude Code session into an orchestrator. The session
writes no code and reads no repository. It understands what the person asks, opens one
side session per front, and runs everything from there: it relays the side sessions'
questions and artifacts, follows their PRs and CI, merges what the person allowed, and
cleans up after each front lands. The person talks only to the orchestrator and never
has to open a side session.

The way of working comes from a multi-day orchestration session on `inspira-desktop`,
where one session ran design, QA, fixes, a Linux release and copy fronts at the same
time. The skill writes down what that session learned, so anyone can switch the mode on.

Success: a person runs a multi-front project from one conversation, answers every
question there, sees every screenshot and report there, and never opens a side session
to unblock it.

## What the session needs

The mode runs on the Claude Code desktop app's session tools: `start_session` to open a
side session, `SendMessage` to reach one, `list_sessions` with `linked: true` and
`list_events` to read their state, `archive_session` and `set_session_title` to tidy up,
and `SendUserFile` to put a file in front of the person. In an agent without those tools
the mode has nothing to run on.

## The four moments of a run

The skill's own material follows the moments a run goes through, each loaded when it
happens:

- **Opening a front**: what a brief carries, how a front proves its work, and the screen
  rule.
- **While fronts run**: relaying messages and artifacts, conflicts between fronts, plan
  changes, sessions that existed before.
- **Landing**: CI, the merge, the order of merges, and what a release-per-merge repo
  needs.
- **Cleaning up**: archiving, stopping leftovers, closing abandoned PRs, renaming.

## Decisions

- **The orchestrator does no code work and explores no repository.** It opens a side
  session for each front at once, with `initiation: "user_asked"` when the person asked
  for the work, and its own worktree for every front that writes code. Reading the repo
  is the side session's job.
- **Every brief stands alone**, because a side session does not see the conversation. It
  carries the person's exact words in quotes, the goal and what done means, the files and
  areas, the decisions already made, what not to do, the person's global rules, how to
  validate, and how to report. A side session that opens a PR turns Auto-fix on.
- **Everything comes back to the orchestrator.** Questions, open decisions and reports
  arrive as messages between sessions; the orchestrator says them to the person in plain
  words and sends the answer back in the person's words. Screenshots, boards, videos and
  reports reach the person through `SendUserFile` or by opening the artifact. A side
  session waiting on the person gets its question read with `list_events` and brought
  into the conversation.
- **The orchestrator merges only what the person allowed, and only inside the repo's
  rules.** The person's permission can be per PR or standing for the run. The merge waits
  for green CI and follows the repository's own rules: the merge method it uses, the
  reviews it requires, its branch protection, and any rule its `CLAUDE.md` or contributing
  guide sets. It never bypasses a rule (`--admin`, skipping a required check). The merge
  pins the head it checked (`--match-head-commit`). Where the repo's own rules forbid an
  agent merge, the orchestrator hands the person the command instead.
- **Merges run one at a time.** The orchestrator waits for GitHub to recompute the next
  PR's state, says that PRs merged in sequence are only tested together by `main`'s CI,
  and after each merge tells the side sessions with an open PR in the same area to merge
  `main`. In a repo that releases on every merge (semantic-release), it checks the commit
  type, because `fix` cuts a patch and `feat` a minor.
- **The orchestrator tidies up itself**, without asking a side session to: it archives a
  side session once its PR lands, stops leftover processes and apps, closes abandoned PRs
  with a comment, renames a side session when its scope changes, and moves an app the
  person is using onto `main` before archiving the session whose folder runs it.
- **Green CI alone is not done.** A side session that changes the interface runs the app
  in an isolated instance (its own debug port and data folder), walks every behavior,
  takes screenshots, fixes what diverges and sends a board to the person.
- **A side session never takes over the person's screen.** It triggers no native dialog
  (choose folder, save, print): it mocks the dialog from the main process and never uses
  the person's real folders.
- **Fronts that touch the same files are told so.** Both get a notice and a request for
  minimal changes. When the person spoke to a side session directly, what they said there
  stands: the orchestrator reads the end of that conversation before replacing the side
  session or sending it something that contradicts it.
- **A change of plan is relayed at once, in the person's words.** When the side session's
  context helps, changing its goal beats opening another. Pausing means stopping without a
  PR and keeping what was done.
- **Sessions that existed before the run do not become side sessions.** The orchestrator
  asks each for a hand-over summary, opens a new side session with that summary, and
  archives the old one.
- **Product decisions stay with the person.** The orchestrator brings each one as a
  question with its recommendation, in product words, not code words.
- **The mode has no handoff gate.** It is resident: it runs until the person ends it, so
  it joins the list of skills that report and stop in `references/handoff-gate.md`.
- **The orchestrator runs no other bb skill.** The side sessions use `/bb:spec`,
  `/bb:implement`, `/bb:review` and `/bb:ship`; the orchestrator names the one a front
  should run in its brief.
- **It sits in the Construir trilha** in the README, beside `implement` and `ship`.
- **The plugin's "never merges" line becomes "never merges on its own"**, in `plugin.json`
  and in `hooks/operating-context.md`, so the frame and this skill say the same thing.

## Behavior

Happy path:

1. The person invokes `/bb:orchestrate` or says "be the orchestrator" and describes the
   work.
2. The orchestrator splits the work into fronts and opens one side session per front,
   each with a standalone brief, in the same turn.
3. The orchestrator tells the person in a few lines which fronts are running.
4. A side session sends a question; the orchestrator asks the person, with a
   recommendation, and sends the answer back quoting the person.
5. A side session finishes a UI change, validates it in an isolated instance, and sends a
   board; the orchestrator puts the board in front of the person.
6. A side session opens a PR with Auto-fix on; the orchestrator follows its CI.
7. The person allows the merge; CI is green; the orchestrator merges under the repo's
   rules and tells the side sessions in the same area to merge `main`.
8. The orchestrator archives the landed side session and stops what it left running.

| WHEN                                                                | THEN                                                                                  |
| ------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| the request is one small task or a few steps                        | the skill says the mode does not pay off and does the task normally                   |
| the session tools are missing                                       | the orchestrator says so and offers a background agent or plain work in this session  |
| the app refuses to open a session (Remote Control)                  | a background agent runs the front, or the person types the request in the desktop app |
| the turn began with another session's message                       | no session opens; the orchestrator brings the start to the person                     |
| the repo was never opened in the app                                | the person is asked to trust the repository before the first side session             |
| a side session sits in "needs the user"                             | the orchestrator reads its question with `list_events` and asks the person            |
| the person allowed a merge but CI is red                            | no merge; the orchestrator reports the failure and waits for the fix                  |
| the repo requires a review the PR lacks                             | no merge; the orchestrator says what is missing                                       |
| the repo's rules forbid an agent merge                              | the orchestrator hands the person the merge command                                   |
| the person never allowed merging                                    | the orchestrator reports the PR green and asks                                        |
| two PRs are ready together                                          | one merge, wait for GitHub's state, then the next                                     |
| two fronts touch the same files                                     | both are told, with a request for minimal changes                                     |
| the person spoke to a side session directly                         | its last turns are read first, and what the person said there stands                  |
| the person changes the plan                                         | the change goes to the side session at once, in the person's words                    |
| the person pauses a front                                           | it stops with no PR and keeps its work                                                |
| a session from before the run holds work                            | hand-over summary, new side session with it, old one archived                         |
| a side session about to be archived runs an app the person is using | the app moves to `main` first                                                         |
| a side session would open a native dialog                           | the dialog is mocked; the person's screen and folders stay untouched                  |

## Metric

skipped: the skill is prose an agent reads, and its use leaves no event stream to read
from.

## Attention points

- The session tools are the desktop app's, with no equivalent in other agents, so an
  install through `npx skills` carries a skill whose tools do not exist there.
- `archive_session` and `set_monitor` ask the person to approve each call outside auto
  mode, so tidying up can stall on an approval nobody is watching.
- The auto mode classifier tends to deny a merge run by a side session, which is the
  reason the orchestrator merges.
- `validate-frontmatter.ts` rejects a skill description above 1024 characters or with `<`
  or `>`.

## Tasks

### The skill

- [ ] **1. The router**: `plugins/bb/skills/orchestrate/SKILL.md` carries the role, when
      to use it and when not, what it needs, the four moments with one pointer each, the
      honest limits and how it lives beside the other skills. · verify: `bun run validate`
- [ ] **2. The references**: `references/briefs.md`, `references/relay.md`,
      `references/landing.md` and `references/cleanup.md` carry one moment each, every
      decision above in one of them. · verify: reading

### The repo catches up

- [ ] **3. Counts, trees and docs**: `.claude/CLAUDE.md`'s tree and count, the README's
      count and Construir table, the CHANGELOG entry, the version bump in `plugin.json`
      and `marketplace.json`, the no-gate list in `references/handoff-gate.md`, and the
      "never merges on its own" line. · verify: `bun run fmt:check`

## Out of scope

- A script that watches CI or merges: the orchestrator uses `gh` and the app's tools.
- An agent definition for the orchestrator: the role is the session itself.
- Evals for the skill under `evals/`. _revisit_

## Open

Nothing.
