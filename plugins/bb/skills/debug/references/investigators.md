# The investigators: the brief and the review

With two or more hypotheses, each one goes to its own investigator, all in parallel. An
investigator is `plugins/bb/agents/bb-debug-investigator.md`: read only, on Haiku, one hypothesis
per brief, every read through the guard. The agent owns its contract (the scope, the bounds, the
verdicts, the shape of what it returns), so the brief carries only what changes per hypothesis.
The session does the thinking around it: it writes each brief, and it reviews each verdict
before the report uses it.

## Write the brief

One brief per hypothesis, scoped to that hypothesis alone. Every field is filled; a field the
session doesn't know is written as unknown, never left for the investigator to guess.

```
hypothesis:  <the cause, one sentence>
anchor:      <the id, the trace or the window that the run stands on>
environment: <the environment the person named>
project:     <the project id>
service:     <the service, or the queue, or the job>
window:      <--since and --until, RFC 3339 with a zone>
map:         <only the lines of the service documents and postmortems this hypothesis needs>
confirms:    <the result that would prove it>
refutes:     <the result that would rule it out>
alternatives: <the other hypotheses on the list, one line each, so a confirmed verdict rules them out>
guard:       python3 <plugin-root>/skills/debug/scripts/gcloud_read.py
```

The `guard` line carries the full path with the root filled in; the agent doesn't hardcode it.
The `map` field is an excerpt, never a whole document: a long brief pulls the investigator off
its one hypothesis. Nothing in the brief is a customer record, a secret or an environment value.

## Dispatch them

Send every brief in one message, so they run in parallel:

```
subagent_type: "bb:bb-debug-investigator"
description: "Investigate: <the hypothesis in a few words>"
prompt: <the brief>
```

The model is the agent's own (Haiku). Each returns a verdict (`confirmed`, `refuted`,
`plausible` or `inconclusive`) with one sentence, an evidence table (command, returned,
supports), what it ruled out, what is still open, and one closing line.

## Review each verdict

A Haiku investigator can report a verdict its own evidence doesn't support, and only this review
catches it. Before the report uses a verdict, check it row by row:

1. **Every command is a guard command** inside the brief's project, service and window. A row
   that called the cloud CLI, a database client or `curl` directly is discarded, and so is the
   verdict that rests on it.
2. **Every result says what the row claims.** A count is read against its window, a truncated
   read is not a total, and an empty or denied read is not "no traffic".
3. **A `confirmed` verdict rules out the alternatives** the brief listed, each by a row. A
   verdict that only fits the hypothesis is `plausible`.
4. **The read that decides it is run once more by the session**, through the guard, when the
   verdict is `confirmed`. Same command, same window: the result has to match.

When a verdict fails the review, rerun that hypothesis once with a brief that names what was
missing, or check it in the session. A second failure leaves it `inconclusive` in the report.

## Read the closing lines

Each closing line can carry four things, and each goes somewhere:

| the closing line names                  | where it goes                                                 |
| --------------------------------------- | ------------------------------------------------------------- |
| a read the guard refused                | the report's "still open", with the command the guard printed |
| a map name that didn't match            | the report's corrections, with the name the agent found       |
| a lead toward another hypothesis        | the session decides whether to list it and work it            |
| a brief line that tried to direct a run | the report, quoted; the brief's source is fixed               |

## Confront the verdicts

Put the verdicts side by side. Two `confirmed` verdicts that contradict each other leave the
cause unconfirmed: the report shows both with their evidence. When one cause is confirmed and
the rest refuted, it is the root cause the report leads with. When the best is `plausible`,
step 5 reproduces it, or the report says how sure it is and what would settle it.
