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

## The rule

- **Suggest, never auto-invoke.** A gate offers; the user picks. The only
  exceptions: `/bb:delegate` (the explicit "run everything" verb; chaining is its
  job), and the `implement → ship` auto-chain when shipping was already authorized
  up front (a delegate run).
- **"Stop here" is always an option.** Picking it ends the turn; nothing is
  invoked, no follow-up question. The user is never trapped in the flow.
- **One gate per skill, at the end.** Mid-skill questions are the skill's own
  business (gray areas, confirmations); the handoff gate is the last interaction.
- **Skills without a natural next step have no gate**: they just report and stop:
  `legal-lens`, `maintain-repo`, `review-setup`, `write-readme`,
  `code-deep-research`, `gather-branch-context`.

## The format

Ask one question:

- `question`: one sentence naming what just finished and asking how to follow.
- `options`: 2–4, each a next skill (or action) with a one-line description of
  what invoking it will do **now**. Lead with the recommended pick and suffix its
  label with `(Recommended)`.
- Last option: **"Stop here"**. Description says what stays saved and how to
  pick the flow back up later (the exact `/bb:<skill>` command).

Example (spec's exit gate, 3-way):

```
question: "Spec validated and saved at .bb/<slug>/spec.md. Where do we go?"
options:
  - "Implement (Recommended)". I run /bb:implement now: I build the tasks and stop ready to ship.
  - "Delegate". I run /bb:delegate <slug>: implement plus ship, end to end.
  - "Stop here". The spec stays saved; pick it back up with /bb:implement or /bb:delegate <slug>.
```

## Journey map (what gates typically offer)

- `discover` → spec (it's code) / brisar (it's design) / challenge (test the thesis) / stop
- `spec` → implement / delegate / stop
- `implement` → ship / stop
- `ship` → review (of the PR it opened) / stop
- `review` → apply more items / run the fronts that were skipped / audit the running UI / review-setup / ship (when there is no PR) · three at most, by priority, plus stop
- `brisar` (on delivery) → review (accessibility audit) / spec / stop
- `think` (once it converged) → spec / discover / stop
- `challenge` → hands the thesis back to its owner; offers spec when the thesis survived and is buildable
