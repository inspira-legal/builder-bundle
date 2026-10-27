# Step 7: the fix and the postmortem

A cause that got fixed becomes a postmortem, and every later run reads the postmortems before it
lists a hypothesis. This step runs from the gate's "Fix now" or "Spec the fix", and the
postmortem's approval is a confirmation inside that path, not a second gate. The run ends after
it.

## Fix now

1. **The failing test first.** Use the test step 5 wrote, or write it now: the smallest test that
   reproduces the anchor's failure with invented data. Run it and see it fail for the reason the
   cause names.
2. **The fix.** Change the code on the current branch, the smallest change that removes the
   cause. Run the test again and see it pass, then run the tests around the code you touched.
3. **The commit.** Commit the fix and its test on the current branch, in the repository's commit
   style. The fix counts as applied once it is committed; note the sha.

When the fix is abandoned, or its test doesn't pass, stop here: no postmortem is written, and the
report stands as the record. Say so in one line.

## Spec the fix

Write the postmortem with the fix marked pending, take it through the check and the approval
below, and then run `/bb:spec` with the report as its input. A later `/bb:debug` run finds the
pending postmortem by search and offers to complete it once the fix lands.

## Draft the postmortem

Open a run directory for the draft (step 6 closed the investigation's), and write the draft into
it, in the language the person is speaking:

```bash
python3 scripts/gcloud_read.py start
```

```markdown
# <the symptom, in a few words>: <the cause, in a few words>

- **Date:** <the date of the symptom>, investigated <today>
- **Environment:** <environment>, projects <ids>
- **Services affected:** <services, queues, jobs>

## Symptom

<what was seen, and from when to when>

## Cause

<the root cause, and the evidence behind it>

**How sure:** <confirmed or plausible, as the report said, and what would settle a plausible one>

## Evidence

| read                         | returned                   |
| ---------------------------- | -------------------------- |
| `<the guard command as run>` | <the count, technical ids> |

## Fix

<what changed>, commit <sha>. Or: pending, through /bb:spec.

## Ruled out

<each hypothesis ruled out, and the read that ruled it out>
```

A postmortem carries technical ids only: a trace, a task, a revision, a commit. Never a
workspace, user or customer id, a person's name, or a document's content. Keep it under 6000
characters, so the base's search finds it whole, and to one cause, since every new task in the
base is checked against it.

## Check it

Run the personal data check with every business id the run touched (the anchor's id and every id
in the evidence) passed as `--id`:

```bash
python3 scripts/gcloud_read.py check RUN_DIR/postmortem.md --id ID --id ID
```

Each line it names holds an email, a personal document number or one of those ids: rewrite the
line and check again until it comes back clean. The check is a net: an id shaped like a business
id but named otherwise passes it, and so do a name and a document's text. Read the draft once
more for those before the person sees it.

## Approve it

Show the whole text, then one `AskUserQuestion`:

```
question: "Postmortem above, to publish in the documentation base as kind postmortem, tagged
  <system>. Publish this text?"
options:
  - "Publish (Recommended)". It goes to the base exactly as shown, and the run ends.
  - "Don't publish". Nothing goes to the base; the draft stays here for you to edit.
```

On "Publish", write it to the base from `RUN_DIR/postmortem.md`, as "Write to the base" states,
and close the run directory after the write. When the person rejects it, nothing is published,
the draft stays in the conversation for the person to edit, and the run directory closes then.
An edited text goes through the check again and is shown whole before it is published. Close it
only once the text is written or set aside:

```bash
python3 scripts/gcloud_read.py close RUN_DIR
```

## Write to the base

Only text the person approved, shown whole, reaches the base.

- **A new postmortem:**

  ```bash
  wave doc new "TITLE" --kind postmortem --tag SYSTEM --body - < RUN_DIR/postmortem.md
  ```

  `SYSTEM` is the system's name as its `service` documents spell it, or the name the person
  confirms when there is none. Name the new document's key in the last line of the run.

- **A change to a document that exists** (a completed postmortem, a corrected `service`
  document): when `wave doc --help` lists a verb that updates a document's body, use it with
  the approved text. When it doesn't, give the person the document's key and the approved text
  whole, to paste in the base. Never delete and recreate a document: its key and its tags are
  how readers find it.

## Complete a pending postmortem

A postmortem found in step 2 whose fix is marked pending, matching this symptom, gets completed
once the person says the fix landed and names its commit or PR. Ask once, with
`AskUserQuestion`, whether to complete it. On yes, write the completed text (the fix section with
the commit or PR, the rest unchanged), run it through the check, show it whole, and write it on
approval as "Write to the base" states. The investigation goes on either way.
