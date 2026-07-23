# Phase 1 — Frame the problem

Get the **problem** sharp before anyone talks solution. The asset is a problem
statement you'd defend, not a filled form.

## What you converge on

Five fields, each **confidence-tagged** `[low | med | high]` by how clear,
specific, and causal the answer is — the tags travel into the brief and flag
what still needs validation before it becomes code:

- **Problem** — what's wrong today, stated concretely. The pain, not the missing
  feature ("reviewers lose 20 min/PR hunting context", not "we need a context
  panel").
- **Who & impact** — who feels it, how many, how badly. An impact nobody can
  size is a `low`-confidence problem.
- **Hypothesis** — the bet: the change you believe will move the problem, and
  _why_ it would (the mechanism). Phase 2 hardens this into a testable form;
  here it's the directional bet.
- **Success signal** — the observable thing that shifts if the problem is being
  solved. One metric beats five.
- **Appetite** — how much this is worth (a budget in time, Shaping-style — "duas
  semanas", not an estimate). It bounds the solution before one exists.

## The loop

1. **Develop the draft.** Read the one-liner, look at the codebase/context, and
   fill the five fields with best-guess values — marking each as a guess. Bring
   a trio to react to, not blank prompts.
2. **Ask only the genuine gaps**, through `AskUserQuestion`, per the interview
   discipline in SKILL.md (max 2/turn, your lean on each, echo after).
3. Keep looping until a round surfaces no new gaps and the problem statement is
   one you'd defend.

## Capture

Write two sections into the brief (location per the task-state contract):

```
## problem
<one-paragraph statement>  [confidence: med]
- who & impact: <who, how many, how badly>  [confidence: low]
- appetite: <budget, e.g. "~2 semanas">
- success signal: <the one observable metric>  [confidence: med]

## hypothesis
If <change>, the <success signal> moves, because <mechanism>.  [confidence: low]
```

Then move to Phase 2 (`references/fit.md`) — the frame decided what the problem
is; fit decides whether and how much of it survives to design.
