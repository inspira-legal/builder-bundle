---
slug: metricas-no-ciclo
created: 2026-08-24
phase: done
verdict: build-mvp
---

# the cycle learns to measure

## Problem

The instrumentation exists in the code and not in the process. Inspira's main app
(inspira-legal/app) already carries a mature measurement stack: a typed event bus
(`eventEmitter` over an `AnalyticsEventMap` spanning trial, search, vault, chat and
subscription), listeners fanning events out to an internal analytics API
(`captureEventV1` / `identifyV1` / `pageviewV1`, gated by the XRAY feature flag), a
GraphQL `event` mutation, and GTM/GA4 loaded inline in index.html. The bb cycle is
blind to all of it: a screen gets changed without consulting the data that already
exists, a feature gets created without a target and a baseline, and what bb builds is
not held to the event convention the app already has, so coverage erodes silently. The
cycle's own seams confirm the gap from both ends: discover's success signal has no
baseline or target slot, and spec's export asks for the hypothesis-OKR-metric trio
that nothing upstream ever filled. [confidence: high]

- who & impact: Inspira builders running the bb cycle, and the readers of what they
  export (Carol's roadmap, the Estilário). Every feature landed through bb today lands
  unmeasured; how many builders and how many landings per month, unsized.
  [confidence: med]
- appetite: ~2 weeks, first lap only (the write half; the read half is explicitly out)
- success signal: the share of bb landings whose spec names a metric with baseline and
  target and whose event coverage the review confirmed. Measured from `.bb/` records
  and review reports, no external tool needed. Baseline today: 0%. [confidence: med]

## Hypothesis

If the cycle carries the discipline at its existing gates (baseline and target on
discover's success signal, events on the spec's behavior rows plus instrumentation
tasks, and a review front that checks coverage against the project's own event
convention), then the success signal moves from 0% to 80% of landings within the
first five specs that cross the cycle after it lands, because the same gates that
already refuse unproven tasks and unmapped behaviors will refuse unmeasured landings.
[confidence: med]

## Fit

Worth building. Demand is internal and evidenced from both sides: the org already
paid for a measurement platform (the internal analytics API and the typed event map
in inspira-legal/app, verified in source) [evidence: high], and the cycle's operator
asked for the discipline unprompted [evidence: high]. The structural gap is verified
in this repo: no baseline slot in discovery, no tracking plan in any document, an
export that must ask for numbers nobody recorded, and a review triage that classifies
analytics-only diffs as invisible to every front [evidence: high]. Broader team
demand beyond the operator is assumed, not measured [evidence: none].

- next_action: build-mvp
- confidence: high

Owner's call, against the recommended conditional gate: the discipline is mandatory
for every spec, not gated on user-visible behavior. Internal work names an
operational measure (error rate, runtime, adoption) where a product metric does not
apply; skip-with-a-reason stays as the only escape. The accepted risk is empty ritual
on mechanical changes; revisit if it shows up in practice.

The bet is legal-sensitive: behavioral tracking sits under LGPD, and the app already
treats it as such (encrypted analytics payloads, sanitized campaign params).
`/bb:legal-lens` over this record is recommended before the build.

## Cuts

Cut:

- the read half (pulling live usage data into discover before a screen changes: GA4,
  the internal analytics API, connector auth, a profile question for the person's
  analytics tools), depends-on-other: it needs an access decision and a second lap,
  and the write half creates the very data it would read. _revisit_
- a fixed `## Tracking` section in the spec format (new lint rule, new reader),
  low-confidence: events on behavior rows plus tasks cover the first lap with zero
  contract change; revisit if the review front needs a structured plan to cite.
  _revisit_
- brisar capturing per-surface events (the surfaces frontmatter, the per-surface
  template), out-of-appetite and depends-on-other: the spec-side convention settles
  first, and design.md registers on a later round. _revisit_
- an analytics SDK page in the manifesto (which tool greenfield products adopt),
  depends-on-other: a team decision, not bb's to write; bb detects the project's own
  convention meanwhile. _revisit_

Kept, in priority order:

1. the spec carries the events: each behavior row a user can trigger names the event
   it emits, and instrumentation enters as ordinary tasks with their own verify
   (high impact, low effort, zero contract change)
2. the review front: instrumentation, the ninth, checking that every interaction the
   diff adds emits its event and that events match the spec and the project's own
   convention (the design front is the template; the triage note that classifies
   analytics-only diffs as non-UI is reassigned to this front)
3. discover closes the loop upstream: the success signal gains baseline and target
   ("from X to Y within Z"), with "skipped: not-instrumented" as a valid baseline
   that flags the instrumentation work
