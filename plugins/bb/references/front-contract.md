# Front contract: how a skill runs in a front

A _front_ is a side session that `/bb:orchestrate` opened with a brief. The person talks
only to the orchestrator, so in a front every question, every page and every report
reaches them through it. This page states what changes in a front: how a session knows it
is one, how its questions travel, what it reports, and where its pages and files go.
Every bb skill follows it.

## Know you are a front

A session is a front when its brief says so and names the orchestrator's session id, the
`local_…` id `SendMessage` takes in `to`. Read the brief once, at the start of the run, and
keep that id for every message below.

Without such a brief, nothing on this page applies: the skill asks the person through
`AskUserQuestion`, as it always does.

## Write to the orchestrator in English

Every message a front sends the orchestrator is English: its questions, its options and
its reports. The traffic between sessions is read by sessions, so it narrows the rule of
`references/doc-style.md` that a string the person reads follows their language. The
orchestrator puts each question to the person in their language. The person's words stay
as they said them: quote the request and every answer exactly as the brief and the
orchestrator give them.

## Send each question to the orchestrator

In a front, every question a skill would ask through `AskUserQuestion` goes to the
orchestrator through `SendMessage`, to its `local_…` id. That includes the mid-skill
questions and the handoff gate of `references/handoff-gate.md`. The message carries what
the dialog would have carried, since the person reads it through the orchestrator's dialog:

- **The question**: what is being decided and why it is open.
- **Every option**: its label, what that pick does next, and what it costs.
- **The recommended pick**, named as such, first in the list.

A question with a setting that goes with it, like the second question of the spec's exit
gate, travels in the same message, with the pick it counts for.

After sending, end the turn and wait. The orchestrator asks the person and sends the
answer back quoted, in the person's words. Act on those words as the answer to the dialog:
a pick names an option, and free text is the person's own answer.

## When the message fails

When `SendMessage` to the orchestrator fails, stop idle with the question, its options and
the recommended pick as your last message. The orchestrator reads it from `list_events`
and relays it from there, and its answer reaches the front as a new message.

## Report to the orchestrator

When the run ends, at done or at a blocker, send the orchestrator one message with:

- **The result**: what changed, in the words of the goal the brief set.
- **The PR url**, when there is one, and the state of its CI.
- **The blockers**: what stopped the run, and what it takes to unblock it.

## Pages and files

The person sees what the front produces through the orchestrator:

- **A page** (a board, a report, a design): publish it as an Artifact and send its URL to
  the orchestrator. The orchestrator opens it for the person.
- **A local file** (a screenshot, a video): leave it in the notes folder the brief names
  and send its path. The orchestrator puts it in front of the person with `SendUserFile`.

Edits to a published artifact belong to the orchestrator: it reads the artifact and
publishes it again to the same URL. An edit that needs code or the front's context comes
back to the front as a message, with the person's words quoted. Apply it, republish to the
same URL, and send the URL again.
