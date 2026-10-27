# While fronts run

The orchestrator is the only place the person looks. This page covers how messages and
artifacts reach the person, what to do when fronts collide, how a change of plan travels,
and what happens to sessions that existed before the run.

## Messages

- **Questions, open decisions and reports** arrive as messages between sessions. Say each
  to the person in plain product words, with a recommendation when it is a decision, and
  ask through `AskUserQuestion` with everything the decision takes inside the call.
- **Send the answer back in the person's words**, quoted, through `SendMessage` to the
  side session's `local_…` id or its name from `ListAgents`. A paraphrase is a second
  decision the person did not make.
- **A side session that stopped on a question for the person** shows as idle in
  `list_sessions`, with no report sent. Read its question with `list_events` and bring it
  into the conversation; the person never has to open that session to unblock it.
- **A report is that session's claim, not proof.** Check the PR, the diff or the file
  before telling the person a front is done.

## Artifacts

Every file a front produces reaches the person here: screenshots, boards, videos,
reports. Send a file with `SendUserFile`, and open a published artifact with the
`Artifact` tool's `open` action. Name what each file shows in one line, so the person
knows what to look at.

## Fronts that collide

- **Two fronts touching the same files**: tell both, name the other front and the files,
  and ask each for the smallest change that does its job. The second PR to land merges
  `main` first.
- **The person spoke to a side session directly**: what they said there stands. Read the
  end of that conversation with `list_events` before replacing the side session or
  sending it anything that contradicts it.

## A change of plan

- **Relay a correction at once**, in the person's words. A front that keeps building on
  the old plan wastes the work after the correction.
- **Change the goal of the side session** when its context helps the new goal. Open a new
  one only when the old context would mislead it.
- **Pausing a front** means it stops with no PR and keeps what it did, committed on its
  branch or written to the notes folder, so it can resume.

## Sessions from before the run

A session that existed before `/bb:orchestrate` started does not become a side session.
Ask it for a hand-over summary (what it did, what is left, its branch and PR), open a new
side session with that summary in the brief, and archive the old one once the new one has
started.
