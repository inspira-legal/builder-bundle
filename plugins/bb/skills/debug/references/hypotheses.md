# Step 3: the hypotheses

A hypothesis is a cause that would produce the anchor, stated so a read can tell it true or
false. This step lists them from three places: the anchor, the map, and the postmortems.

## List them

Write each hypothesis as one line, with the read that would confirm it and the read that would
refute it:

| field    | holds                                                                         |
| -------- | ----------------------------------------------------------------------------- |
| cause    | one sentence: what broke, where (the queue went past its dispatch deadline)   |
| from     | what suggested it: the anchor's error, a known failure, a postmortem by key   |
| confirms | the result that would prove it (every failing task ends at the same deadline) |
| refutes  | the result that would rule it out (failures with no deadline in their log)    |
| source   | the cheapest source in `references/sources.md` that answers it                |

A postmortem close to the symptom gives its cause as a hypothesis, never as the answer: the same
symptom can come back from a different cause.

List at most five. When more fit, keep the five the anchor supports best, and name the rest in
the report as not tested.

A hypothesis the anchor already rules out is not listed; say in the report what ruled it out.

## Work them

- **One hypothesis.** The session works it itself, through `references/sources.md`.
- **Two or more.** One investigator per hypothesis, all at once, as
  `references/investigators.md` states. The session reviews each verdict before the report uses
  it.

The count is of the hypotheses still open once the anchor's reads are in. A hypothesis those reads
already decide is not listed, as above: the report rules it out with the read that decided it,
under "ruled out", and it is never "worked in the session". When two or more stay open, they go
to investigators, even when the session could read them itself. The one exception: every open
hypothesis waits on a source this run can't read (a database the guard keeps closed, a refused
permission). Then no investigator goes out, since each would meet the same refusal, and the
report leaves them open with the read that would decide each.

Either way, a cause is confirmed only when the evidence rules out the other hypotheses on the
list, not when it fits. When the cause fits but the proof is not there, step 5 reproduces it.
