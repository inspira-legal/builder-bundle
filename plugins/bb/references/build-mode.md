# Build mode: workflow or main context

Two ways to build a spec's tasks, and the user picks per run:

- **Workflow**: one agent per task, dispatched as a dynamic workflow. Each task
  starts on a clean budget carrying only the spec and its own cut, and a convention
  note is threaded between them. Shape of the script: `build-tasks-workflow.md`.
- **Context**: the main session builds every task itself. What `/bb:implement` has
  always done.

The reason to offer the choice isn't speed. A spec of eight tasks built in one
context hits compaction mid-build, and that's exactly where the loop degrades: the
`## Behavior` map falls out of context and the build starts drifting from
the `## Decisions`. Losing tacit context between agents is the price, and the
convention note is what's paid with, lossy on purpose instead of lossy by
accident.

## When the question is asked

`/bb:implement` and `/bb:delegate` ask it **once, at the start of every run**, before
the first task, no size threshold. A spec with a single task is still asked; the
choice is the user's, not a heuristic's. When `/bb:delegate` drives the build it's
delegate that asks, and the implement loop it drives takes the answer as given.

Two things skip it entirely. A spec with **no `## Tasks` section** (and none
under the older `## tasks` either) has no tasks to fan out over, and no build
either: implement's Prerequisites stop the run and send it back to `/bb:spec`
before this question would have been reached. The other is a run where workflows
aren't available, below.

This is a mid-skill question, not the handoff gate. The gate convention in
`handoff-gate.md` still applies to the one at the end of the skill. What carries over
from it: the question goes through `AskUserQuestion` (a question printed as text has
no response path), the tool supplies "Other" on its own, and the recommended option
leads and is suffixed `(Recommended)`.

## The question

```
question: "The spec has N tasks. Build via workflow (one agent per task) or in this session's context?"
options:
  - "Via workflow (Recommended)". One agent per task, in sequence, in the same tree. Each one starts on clean context; the conventions travel forward in a note. You follow along in /workflows.
  - "In this context". I build the tasks right here, as always. On a big spec the build hits compaction halfway and starts drifting from the spec.
```

Swap the `(Recommended)` suffix per the rule below; the option text itself doesn't
change.

## Which one leads: how self-sufficient the spec is

A task agent receives the spec, its own line and the convention note. Nothing else.
So the question to answer before recommending is: **what does this session know that
the file doesn't?** Task count is the size of the bet, not the discriminator.

**Nothing → workflow leads.** The spec is the whole picture, so a fresh agent per
task reads what the main context would have read. Signals: the spec was written in
another session or on an earlier day; the run is a resume with tasks already ticked;
a bare `/bb:delegate` selected it, so nothing about it is in this context at all.

**Something load-bearing → context leads, and say which piece.** Signals: this run
arrived from `/bb:spec`'s own exit gate, so the conversation that produced the spec
is still live and was richer than the file; the spec was edited or argued with in
this session; a premise got corrected here and landed in the file as one dry line.
This case peaks exactly where the compaction risk is highest (a big spec just
specced), which is why it gets read rather than assumed.

Naming the piece matters more than the recommendation. A spec that needs this
session to be buildable is a spec no fresh agent can build from, and writing the
missing piece into it is the durable fix. It makes workflow safe on the
spot, and the user is the only one who can judge whether the piece belongs in the
spec. Offer that in the same breath as the question.

**One or two tasks → context leads regardless.** There's no compaction to buy off,
and each agent would pay from scratch for the repo orientation this context already
has.

## When workflows aren't available

The `Workflow` tool is absent from the session when the `disableWorkflows` setting is
on, when org-managed settings turn it off, or when the client predates the version
that shipped dynamic workflows. Check before asking: an option that can't be executed
isn't a choice.

Absent, both skills build in context and **say why in one line**: "workflows are off
in this session, building here". A silent downgrade reads as a preference
and hides a setting the user may not know is on.

## After the pick

- **Workflow**: read `build-tasks-workflow.md`, author the script, run the
  pre-invoke checklist at the end of that file, invoke `Workflow`. When it returns,
  pick up the caller's own contract from its result.
- **Context**: build the tasks as implement's steps 3–7 describe. Nothing about
  the spec, the project's checks or the commits changes.
