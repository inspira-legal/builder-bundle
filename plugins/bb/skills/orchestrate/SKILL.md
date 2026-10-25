---
name: orchestrate
description: Turns this session into an orchestrator that delegates every piece of work to side sessions and runs the project from one conversation. It opens one side session per front with a standalone brief, relays their questions, screenshots and reports to you, follows their PRs and CI, merges what you allowed under the repository's rules, and archives and cleans up after each front lands. You talk only to the orchestrator and never open a side session. Runs on the Claude Code desktop app's session tools. Use when the user says "orchestrate my sessions", "be the orchestrator", "delegate everything", "run this with sub-sessions", "split this into fronts", "orquestra minhas sessões", "seja o orquestrador", "delegue tudo", or invokes /bb:orchestrate. Don't use it for a single task or work of a few steps (just do it), or to build one spec yourself (use /bb:implement).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.0.0
---

# Orchestrate

Run the whole project from this conversation while side sessions do the work. The orchestrator understands what the person asks, opens one side session per front, and conducts everything from here: it relays questions and artifacts, follows PRs and CI, merges what the person allowed, and tidies up after each front lands. **The person talks only to the orchestrator.** Every question, file and decision comes here, so the person never has to open a side session.

## The role

- **Do no code work and read no repository.** Each front goes to a side session at once, in the same turn the person asked for it. Reading the code is the side session's job; the orchestrator holds the conversation, the decisions and the state of every front.
- **Open the side session with `start_session`**, with `initiation: "user_asked"` when the person asked for the work, and `use_worktree: true` for every front that writes code. A front that only reads can share the checkout.
- **Keep product decisions with the person.** Bring each one as a question with a recommendation, through `AskUserQuestion`.
- **Talk short, in product words.** Say what changed for the person, not which file changed. A decision arrives as a question with a recommended pick, never as a paragraph to answer in prose.

## When the mode pays off

Use it for work with several fronts that run at the same time or over days: design, QA, fixes, a release, copy. For one task, or work of a few steps, say in one line that the mode does not pay off here, and do the task normally.

## What the mode needs

The mode runs on the Claude Code desktop app's session tools: `start_session`, `SendMessage` to a `local_…` id, `list_sessions` with `linked: true`, `list_events`, `archive_session`, `set_session_title` and `SendUserFile`. When they are listed as deferred tools, load them with `ToolSearch` before the first call. When they are not there at all, say that this agent cannot open sessions, and offer a background agent or plain work in this session.

## The four moments

Each moment has its own reference. Load it when the moment happens:

| moment                                                                     | reference               |
| -------------------------------------------------------------------------- | ----------------------- |
| Opening a front: the brief, how the front proves its work, the screen rule | `references/briefs.md`  |
| While fronts run: messages, artifacts, conflicts, plan changes, old ones   | `references/relay.md`   |
| Landing: CI, the merge under the repo's rules, merges in sequence          | `references/landing.md` |
| Cleaning up: archive, stop leftovers, close abandoned PRs, rename          | `references/cleanup.md` |

Most runs cycle through all four many times: new fronts open while others land.

## Limits to say out loud

- **Remote Control can refuse to open sessions.** Then run the front as a background agent, or ask the person to type the request in the desktop app.
- **A turn that began with another session's message cannot open a session.** Bring the start to the person, who opens it with one word in their own turn.
- **A repository the app never opened asks for "Trust repository"** before its first side session. Ask the person to open it once.
- **Approvals can stall tidying up.** Outside auto mode, the app asks the person to approve each archive and each monitor switch, so say which approval is waiting.

## Beside the other skills

The orchestrator runs no other bb skill. The side sessions do: a front that needs alignment runs `/bb:spec`, a specced front runs `/bb:implement`, and a branch to read or land runs `/bb:review` and `/bb:ship`. The brief names which one the front runs. Merging is the one step the orchestrator takes over from those skills, because a merge run by a side session tends to be denied, and only with the person's permission (`references/landing.md`).

The mode has no handoff gate. It stays resident until the person ends it, and when they do, it reports what landed, what is still open and which side sessions remain.
