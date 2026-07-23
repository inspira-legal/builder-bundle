---
name: frame-problem
description: Frame the problem before any solution — converge on a sharp problem statement, the bet (hypothesis), who feels it and how badly, the success signal, and the appetite. Draft-first — Claude proposes the trio, then loops with you through the question tool on the gaps, confidence-tagging each field and recording skips with a reason. Writes `## problem` / `## hypothesis` into `.ofc/tasks/<slug>/shape.md` for /ofc:assess-fit and /ofc:shape to build on. Use when the user says "what problem are we solving", "frame the problem", "is this worth solving", "run the trio", "diagnose this", or starts from a fuzzy pain rather than a feature. Do NOT use to pressure-test market fit (use /ofc:assess-fit), to shape the solution/build (use /ofc:shape), or for a tiny mechanical change.
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.0.0
---

# Frame the problem

Get the **problem** sharp before anyone talks solution. Shaping the wrong problem
crisply still ships the wrong thing — this is the lowest-cost moment to catch
that. The asset is a problem statement you'd defend, not a filled form. You
converge on the trio, then hand off to `/ofc:assess-fit` (is it worth it?) or
`/ofc:shape` (build it).

## What you converge on

Five fields, each **confidence-tagged** `[low | med | high]` by how clear,
specific, and causal the answer is — the tags travel into the brief and flag what
still needs validation before it becomes code:

- **Problem** — what's wrong today, stated concretely. The pain, not the missing
  feature ("reviewers lose 20 min/PR hunting context", not "we need a context
  panel").
- **Who & impact** — who feels it, how many, how badly. An impact nobody can
  size is a `low`-confidence problem.
- **Hypothesis** — the bet: the change you believe will move the problem, and
  _why_ it would (the mechanism). `/ofc:assess-fit` later hardens this into a
  testable form; here it's the directional bet.
- **Success signal** — the observable thing that shifts if the problem is being
  solved. One metric beats five.
- **Appetite** — how much this is worth (a budget in time, Shaping-style — "two
  weeks", not an estimate). It bounds the solution before one exists.

## The loop

Draft-first, never an interrogation. You bring the pain; Claude develops it,
then loops with you through the **`AskUserQuestion` tool** until the trio holds.

1. **Develop the draft.** Read the one-liner, look at the codebase/context, and
   fill the five fields with best-guess values — marking each as a guess. Bring a
   trio to react to, not blank prompts.
2. **Ask only the genuine gaps**, through `AskUserQuestion`, **at most 2 per
   turn** (more turns it into a form, and forms get form-shaped answers). Each as
   concrete options with your lean. Decide the obvious yourself.
3. **Echo before advancing.** After each turn, confirm in one line what you
   captured ("Got it — problem: X, hypothesis: Y. On to the metric.") so a
   misread surfaces in seconds, not in sprint three.
4. **Skip with a reason, never a silent blank.** If a field can't be answered,
   record `skipped — <reason>` (e.g. "no connected metric yet"). A skip with a
   reason is information; a blank is debt.
5. **Vagueness is data.** Ask for clarification once; if it's still fuzzy, accept
   it at `low` confidence and move on rather than stalling. Where you'd be
   guessing at a fact, check (codebase → docs → web) instead.

Keep looping until a round surfaces no new gaps and the problem statement is one
you'd defend.

## Capture (on disk)

Write the trio into `.ofc/tasks/<slug>/shape.md` as two sections — accreting the
same file that `/ofc:assess-fit` and `/ofc:shape` extend, so one file
carries the full context. Generate `<slug>` as a short kebab name for the problem area; if
the file exists for a _different_ problem, suffix it (`-2`) or ask — never
overwrite another brief.

```
## problem
<one-paragraph statement>  [confidence: med]
- who & impact: <who, how many, how badly>  [confidence: low]
- appetite: <budget, e.g. "~2 weeks">
- success signal: <the one observable metric>  [confidence: med]

## hypothesis
If <change>, the <success signal> moves, because <mechanism>.  [confidence: low]
```

Keep any deferred or out-of-frame ideas as plain bullets (never checkboxes) so
nothing downstream mistakes them for tasks.

## Hand off

frame-problem ends at a captured trio and does not solution. State the next step;
don't auto-invoke it:

- **Worth pressure-testing?** → `/ofc:assess-fit` — market fit, cuts,
  prioritization, and a testable hypothesis, building on this `## problem`.
- **Ready to build?** → `/ofc:shape` — it reads the trio as upstream intent
  and shapes the design, behavior, and slices.
