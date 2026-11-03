# While fronts run

The orchestrator is the only place the person looks. This page covers how questions,
reports and artifacts reach the person, how many fronts run at once, what to do on the
usage limit and when fronts collide, how a change of plan travels, and what happens to
sessions that existed before the run.

## Questions from a front

A front sends each question its skill would have asked, with the options and the
recommended pick written in the message (see `<plugin-root>/references/front-contract.md`).

- **Relay it through `AskUserQuestion`**, in the same turn it arrives: the question in
  plain product words, every option the front sent with what it does and what it costs,
  and the front's pick first, marked as the recommendation. The front writes in English;
  the person reads the question and its options in the person's language.
- **Send the answer back in the person's words**, quoted, through `SendMessage` to the
  side session's `local_…` id or its name from `ListAgents`. A pick goes back as the
  option's label as the front sent it; free text goes back as the person wrote it, in
  their language. A paraphrase or a translation is a second decision the person did not
  make. The rest of the message is English, by the rule in `references/briefs.md`.
- **A side session that stopped on a question for the person** shows as idle in
  `list_sessions`, with no message sent. Read its last message with `list_events`, relay
  the question from there, and send the answer as a new message; the person never has to
  open that session to unblock it.

## Reports

- **Say each report to the person** in plain product words and in the person's language,
  with a recommendation when it leaves a decision.
- **A report is that session's claim, not proof.** Check the PR, the diff or the file
  before telling the person a front is done.

## Artifacts

Every page a front produces reaches the person here, and the person changes it here.

- **When a front sends an artifact URL**, open it for the person in the same turn, with
  the `Artifact` tool's `open` action, and name in one line what it shows.
- **When the person asks to change an artifact**, edit it here: read it with the
  `Artifact` tool's `read` action, apply the edit, and publish again to the same URL, so
  the link the person holds keeps working.
- **When the edit needs code or the front's context**, send it to the front with the
  person's words quoted. The front republishes to the same URL and sends it back; open it
  again.
- **A local file** (a screenshot, a video, a long report) reaches the person through
  `SendUserFile`, from the path the front sent or from the notes folder. Name what each
  file shows in one line, so the person knows what to look at.

## Many fronts at once

There is no fixed cap on fronts at once. Above four fronts working at the same time, tell
the person before opening the next one, in one line with the fronts already running.

## The usage limit

A front that stops on the usage limit shows its reset time in its last message.

1. Tell the person the reset time once, in one line, for every front that stopped on it.
2. Once the reset passes, send each stopped front a message to continue where it stopped.

The session tools do not wake the orchestrator at a given time, so the message goes out
on the first turn after the reset: the person's next message, or a front that wakes the
orchestrator. Say so in the same line as the reset time.

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
side session with that summary in the brief, and once the new one has started, archive
the old one by the steps in `references/cleanup.md`.
