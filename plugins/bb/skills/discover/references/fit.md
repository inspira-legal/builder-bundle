# Phase 2: Fit, decide what survives

You are the **lawyer of the problem**, not its salesperson. Advocate for the
thesis with evidence, and when the market is overestimated or the alternatives
undersold, say so. The output is a defensible go/cut/order decision plus the one
bet you'll measure.

## The four modes

Run them in order (market → cuts → prioritization → hypothesis) when the work
came from a framed problem; otherwise run only the mode the user asked for.

- **Market fit**: is it worth building? Who's the customer, what's the demand
  evidence, how big if size matters. Lands a `next_action`: build-mvp /
  validate-first / pivot / persevere / shelve.
- **Cuts**: lean the scope to the appetite. Every cut carries a reason
  (`no-market` / `out-of-appetite` / `depends-on-other` / `low-confidence`). A
  silent cut is product debt.
- **Prioritization**: order what stays. Use the framework the data supports,
  RICE when Reach/Impact/Confidence/Effort exist, else ICE or a small Kano.
  Don't ask for data the user doesn't have; fall back.
- **Hypothesis**: always close here. Harden the bet into testable form:
  _"If <change>, then <observable metric> within <timeframe>, because
  <mechanism>."_ A wish ("melhorar a UX") is not a hypothesis; don't close the
  phase without the testable shape.

## How it runs

- **Evidence before canvas.** Before filling any block, ask what data or
  observation backs it, and tag each `[evidence: high | med | low | none]`.
  Tagging `none` is the most valuable mark on the page. It's where the risk is.
- **Auto-size from signals, don't ask depth.** Read the frame's appetite and
  confidence: a small appetite with a confident problem doesn't need a full
  TAM/SAM/SOM. A back-of-envelope is enough. You decide the depth; asking "do you
  want a full TAM?" just shifts the cost to the user.
- **Check facts you'd otherwise guess** (market size, competitors, prior art):
  search the web rather than inventing numbers, and tag the confidence of what
  you find.
- Question tool, echoes, and confidence tags per the interview discipline in
  SKILL.md.

## Capture

Write into the same spec, accreting alongside `## Problem` / `## Hypothesis`:

```
## Fit
<worth-building verdict + the demand evidence, each claim evidence-tagged>
- next_action: build-mvp | validate-first | pivot | persevere | shelve
- confidence: med

## Cuts
Cut:
- <feature>, <reason: out-of-appetite>
Kept, in priority order:
1. <feature>  (ICE 7, high impact, low effort)
2. <feature>
```

And refine the `## Hypothesis` section in place into the testable form. Keep cut
ideas worth revisiting as plain bullets marked _revisit_, never checkboxes.

A legal-sensitive bet deserves `/bb:legal-lens` over the spec before committing;
mention it in the report when it applies.
