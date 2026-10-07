# Handoff gate: the one convention for "what's next"

Every skill whose outcome has a natural next step ends with a **handoff gate**: a
single `AskUserQuestion` that offers the next skill(s) in the journey. The gate is
how the bundle gives the user a sense of place ("here's where you are, here's
what usually comes next") without ever deciding for them.

## Why the tool (applies to any question, not just gates)

Anything expecting an answer goes through `AskUserQuestion`. A question printed
as plain text has no response path, so the flow stalls. The tool auto-provides
an "Other" free-text option; a manual "Other"/"Change something" option is
redundant.

**The call carries what it takes to decide.** Whoever answers is looking at the
dialog, not at the transcript above it, so the reasoning has to travel inside the
call: the `question` names what is being decided and why it is open, and each
option's `description` says what that pick does next and what it costs. The
`label` is a name (1–5 words) and the `header` a chip of 12 characters, so
neither of them is where the substance goes. The test: if the answer would change
depending on something you know and did not write down, the call is incomplete.
Explaining the fork in prose and then asking "A or B" makes the person scroll
back to answer, which is the same stall as printing the question as text.

## The rule

- **Suggest, never auto-invoke.** A gate offers; the user picks. The one exception
  is a chain the user authorized up front: `/bb:implement` settles at its step 2 how
  far the run goes, and a scope that includes the review or the ship runs them without
  asking again, because that answer is the ask.
- **"Stop here" is always an option.** Picking it ends the turn; nothing is
  invoked, no follow-up question. The user is never trapped in the flow.
- **One gate per skill, at the end.** Mid-skill questions are the skill's own
  business (gray areas, confirmations); the handoff gate is the last interaction.
- **Skills without a natural next step have no gate**: they just report and stop:
  `ship`, `legal-lens`, `maintain-repo`, `review-setup`, `write-readme`,
  `code-deep-research`, `gather-branch-context`.

## The format

Ask one question, or two in one call when the pick needs a setting to go with it, the way
the spec's exit gate asks what comes after the build:

- `question`: one sentence naming what just finished and asking how to follow.
- `options`: 2–4, each a next skill (or action) with a one-line description of
  what invoking it will do **now**. Lead with the recommended pick and suffix its
  label with `(Recommended)`.
- Last option: **"Stop here"**. Description says what stays saved and how to
  pick the flow back up later (the exact `/bb:<skill>` command).
- A second question, when there is one, is `multiSelect` and carries the setting,
  with no "Stop here" of its own. It counts only with the pick it sets, and the
  first question's description says so.

Example (spec's exit gate, two questions in one call):

```
question 1, single choice: "Spec validated and saved at .bb/<slug>/spec.md. What now?"
options:
  - "Build (Recommended)". I invoke /bb:implement <slug> now, at the scope the second question sets.
  - "Review the spec". One bb-spec-reviewer pass over the spec, then this gate opens again.
  - "Stop here". The spec stays saved; pick it back up with /bb:implement <slug>.

question 2, multiSelect, counted only when the first answer is "Build": "After the build?"
options:
  - "Review the branch". /bb:review runs over the branch before anything ships.
  - "Ship". /bb:ship settles the destination and ships it.
  Both left unticked is a build only.
```

## Journey map (what gates typically offer)

- `discover` → spec (it's code) / brisar (it's design) / challenge (test the thesis) / measure (the baseline stayed skipped: it takes challenge's slot on design-led work, brisar's on the rest) / stop
- `spec` → implement, at the scope the gate's second question set / review the spec / stop
- `implement` → ship / stop, only when the scope didn't already include it
- `ship` → no gate; it reports what shipped and stops
- `review` → apply more items / run the fronts that were skipped / audit the running UI / review-setup / ship (when there is no PR) · three at most, by priority, plus stop
- `brisar` (on delivery) → review (accessibility or design audit) / spec / stop
- `think` (once it converged) → spec / discover / stop
- `measure` (a saved file or a document; a chat answer has no gate) → hypotheses / discover / spec / stop
- `challenge` → hands the thesis back to its owner; offers spec when the thesis survived and is buildable
