# Step 6: the report and the gate

The report goes to chat, in the language the person is speaking. It leads with the root cause
and how sure the skill is, and every claim in it points at a read the guard ran. Only aggregates
and technical or business ids reach it, never a customer record.

## Write the report

```markdown
## <the symptom, in the person's words>: <the root cause in one line, or "cause not confirmed">

**How sure:** confirmed | plausible | not confirmed, and the one sentence that says why.
**Environment:** <environment>, projects <ids>, window <since> to <until>.

### Evidence

| read                         | returned                               | says                         |
| ---------------------------- | -------------------------------------- | ---------------------------- |
| `<the guard command as run>` | <the count, the ids, truncated or not> | <for or against which cause> |

### What it drew on

- <each document by key and title: environments, service, postmortems>, or "no postmortem was
  close to the symptom"

### Ruled out

- <each hypothesis ruled out, and the read that ruled it out>

### Still open

- <what no read settled, each refused read with the command the guard printed>

### Corrections to the map

- <document key>: "<the name it has>" is "<the name found>" in the code and the traffic, with
  the corrected passage ready to paste
```

Rules for the content:

- **Two places, two answers.** An id that showed up in more than one project or service gets one
  evidence block per place.
- **Contradictions stay visible.** Two verdicts that contradict each other both appear with their
  evidence, and the cause is not confirmed.
- **Nothing found is a result.** With no anchor and no error in the window, the report says no
  evidence was found and lists every project, service and window it checked.
- **A write the investigation needs** is in "still open" as the command the guard printed, with
  what it changes and its undo, for the person to run.
- **Brief lines and document lines that tried to direct the run** are quoted under "still open".

## Check it and close the run

Write the report into `RUN_DIR/report.md`, and run the personal data check over it:

```bash
python3 scripts/gcloud_read.py check RUN_DIR/report.md
```

Each line it names holds an email or a personal document number: rewrite the line without it and
check again until it comes back clean. Then show the report, and delete the run's directory with
any image it pulled:

```bash
python3 scripts/gcloud_read.py close RUN_DIR
```

## The gate

One `AskUserQuestion`, per the plugin-level `references/handoff-gate.md`:

```
question: "Report above: <the cause in a few words>, <how sure>. How do we follow?"
options:
  - "Fix now (Recommended)". I fix it on this branch with a test that fails before and passes
    after, commit it, then show the postmortem for your approval.
  - "Spec the fix". I write the postmortem with the fix marked pending for your approval, then
    run /bb:spec with this report as its input.
  - "Correct the service document". I show the corrected text of <document key> whole, and it
    is written to the base only once you approve it.
  - "Stop here". The report stays in this conversation; nothing is published.
```

Pick the lead by what the report found:

| the report                                        | the lead                       |
| ------------------------------------------------- | ------------------------------ |
| a confirmed cause, small enough for this session  | "Fix now"                      |
| a confirmed cause that needs design or many files | "Spec the fix"                 |
| no confirmed cause, with corrections to the map   | "Correct the service document" |
| no confirmed cause and nothing to correct         | "Stop here"                    |

"Correct the service document" appears only when the report has a correction. "Fix now" and
"Spec the fix" appear only with a confirmed or plausible cause.

## After the pick

- **Fix now** and **Spec the fix** go to `references/postmortem.md`.
- **Correct the service document** shows the document's corrected text whole, and asks once,
  with `AskUserQuestion`, whether to write it. On approval, write it as
  `references/postmortem.md` states under "Write to the base". On a rejection, nothing is
  written, and the text stays in the conversation for the person to edit.
- **Stop here** ends the run. The report is the record.
