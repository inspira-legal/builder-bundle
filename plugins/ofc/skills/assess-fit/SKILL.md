---
name: assess-fit
description: Pressure-test a framed problem before it becomes design — decide whether it's worth building, what to cut to fit the appetite, in what order what survives, and the one testable hypothesis you're betting on. Advocate for the thesis with evidence, not a cheerleader — name it when the market is overestimated or alternatives are underestimated. Evidence-tags every claim, gives each cut a reason, and writes `## fit` / `## cuts` into `.ofc/tasks/<slug>/shape.md`. Use when the user says "is this worth building", "validate the market", "what should we cut", "prioritize these", "pivot or persevere", "TAM/SAM/SOM", or "what's the testable hypothesis". Do NOT use to frame the problem first (use /ofc:frame-problem) or to shape the solution/build (use /ofc:shape).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.0.0
---

# Assess fit

Decide what survives to design. You are the **lawyer of the problem**, not its
salesperson — argue the thesis with evidence, and when the market is
overestimated or the alternatives undersold, say so. The output is a defensible
go/cut/order decision plus the one bet you'll measure, written onto the same
brief the build reads.

## Upstream

Read `.ofc/tasks/<slug>/shape.md` first. If `## problem` / `## hypothesis` exist
(from `/ofc:frame-problem`), echo the trio and build on it. If they don't,
suggest `/ofc:frame-problem` once — non-blocking; if the user wants to continue
here, note `ran without a framed problem` in `## fit` and proceed.

## The four modes

Pick one, or run them in order (market → cuts → prioritization → hypothesis).
Lead with the pipeline when the work came from a framed problem; otherwise ask
which mode fits where the user is.

- **Market fit** — is it worth building? Who's the customer, what's the demand
  evidence, how big if size matters. Lands a `next_action`: build-mvp / validate
  first / pivot / persevere / shelve.
- **Cuts** — lean the scope to the appetite. Every cut carries a reason
  (`no-market` / `out-of-appetite` / `depends-on-other` / `low-confidence`). A
  silent cut is product debt.
- **Prioritization** — order what stays. Use the framework the data supports —
  RICE when Reach/Impact/Confidence/Effort exist, else ICE or a small Kano. Don't
  ask for data the user doesn't have; fall back.
- **Hypothesis** — always close here. Harden the bet into testable form:
  _"If <change>, then <observable metric> within <timeframe>, because
  <mechanism>."_ A wish ("we'll improve UX") is not a hypothesis; don't close the
  phase without the testable shape.

## How it runs

- **Evidence before canvas.** Before filling any block, ask what data or
  observation backs it, and tag each `[evidence: high | med | low | none]`.
  Tagging `none` is the most valuable mark on the page — it's where the risk is.
- **Auto-size from signals, don't ask depth.** Read the trio's appetite and
  confidence: a small appetite with a confident problem doesn't need a full
  TAM/SAM/SOM — a back-of-envelope is enough. You decide the depth; asking "do
  you want a full TAM?" just shifts the cost to the user.
- **Question tool, at most 2 per turn**, each with your lean; echo what you
  captured after each turn.
- **Check facts you'd otherwise guess** — market size, competitors, prior art:
  search the web rather than inventing numbers, and tag the confidence of what
  you find.

## Capture (on disk)

Write into the same `.ofc/tasks/<slug>/shape.md`, accreting alongside the trio:

```
## fit
<worth-building verdict + the demand evidence, each claim evidence-tagged>
- next_action: build-mvp | validate-first | pivot | persevere | shelve
- confidence: med

## cuts
Cut:
- <feature> — <reason: out-of-appetite>
Kept, in priority order:
1. <feature>  (ICE 7 — high impact, low effort)
2. <feature>
```

And refine the `## hypothesis` section in place into the testable form. Keep cut
ideas worth revisiting as plain bullets marked _revisit_ — never checkboxes.

## Hand off

assess-fit ends at a decision, not an automatic next step. State it; don't
auto-invoke:

- **build-mvp** → `/ofc:shape` — it reads `## problem` / `## hypothesis` /
  `## fit` as upstream intent and shapes the design, behavior, and slices.
- **validate-first / low confidence** → suggest running an experiment against the
  testable hypothesis before building.
- A legal-sensitive bet → `/ofc:legal-lens` over the brief before committing.
