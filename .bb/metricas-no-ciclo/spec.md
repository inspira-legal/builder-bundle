---
status: pending
created: 2026-08-24
slug: metricas-no-ciclo
---

# the cycle learns to measure

The instrumentation exists in the code and not in the process; the framing and the
evidence live in `.bb/metricas-no-ciclo/discovery.md` and this spec builds on them.
The change makes the cycle carry measurement at the gates it already has: a spec
names its metric with provenance and the events its behaviors emit, instrumentation
enters the build as ordinary tasks, and review gains a ninth front that checks
coverage against the convention the project itself uses. Success is a cycle where an
unmeasured landing is a visible, deliberate exception instead of the silent default.

The read half (pulling live usage data into the cycle) stays out of this lap by the
cut recorded in the discovery; this spec creates the data that lap will read.

## The Metric section

`## Metric` joins the spec's fixed section set, placed between `## Behavior` and
`## Tasks`: events cite the behavior rows above them, tasks cite the events below.
Every spec created from the landing on carries it, in one of two forms, and an honest
skip always beats an invented number:

- **The metric block**: the one metric, its baseline, its target, and a timeframe,
  each value with its provenance (a query, a log, a named person's estimate marked as
  such), plus an optional `okr:` line naming the connected OKR when one exists.
  Internal work names an operational measure (error rate, runtime, adoption) where no
  product metric applies.
- **The skip**: one line, `skipped: <reason>`, when no honest measure exists.

When the work has user-triggered behavior, the section also carries the **events
table**: one row per event, with the event name (following the project's own
convention), the behavior rows it instruments, the payload fields, and the channel
when the project has more than one sink. Payload fields are IDs and enums, never free
text and never document content; that rule is what keeps mandatory instrumentation
compatible with a legaltech's data duties, and this paragraph is its single home.
Instrumentation then enters `## Tasks` as ordinary tasks with their own `verify:`,
each citing the event rows it wires; an event row's own behavior citations are what
the coverage table counts, so an instrumentation task covers its behaviors through
the event row it cites, and the existing build machinery proves it with no change.

## The ninth front

`/bb:review` gains the `instrumentation` front, built the way the design front was:
one catalog row, one availability probe, one reference with the method, zero changes
to the finder and verifier agents. This lap it runs over the diff only; the
standalone surface scope a11y and design have comes later.

Its sources are a two-rung ladder, resolved by the probe before the front offers
itself: rung 1 is the branch spec's `## Metric` events table, rung 2 is the analytics
convention the project itself shows in source (a typed event map, an emit wrapper, a
generated client). When neither rung resolves, the front is unavailable and the
report names the remedy (write the events table, or point at the project's wrapper),
never a degraded run. What it checks is semantic, not presence: every interaction the
diff adds has its planned event, event names follow the resolved convention, payloads
hold only what the payload rule allows, and events flow to the channel the plan
names, so a sensitive payload routed to a third-party sink is a finding. The triage
note that today keeps analytics-wiring diffs away from the UI fronts (correctness and
quality still run on them, but neither checks events) is extended: those hunks now
activate this front. The front's criteria live inline in its own reference until the
surface scope exists to justify a shared checklist file.

## What discover and export gain

Upstream, discover's success signal gains the baseline and the target: the capture
format asks for the metric's current reading with provenance, `skipped:
not-instrumented` is a valid baseline that flags instrumentation work, and the
testable hypothesis hardens from "the metric moves" to "the metric moves from
<baseline> to <target> within <timeframe>". Downstream, the export's
hypothesis-OKR-metric trio stops asking at render time: the hypothesis comes from the
discovery record as today, the metric and the OKR come from `## Metric` by path, the
export asks only for a field genuinely absent from both records, and a skipped
section omits the trio whole under the existing all-or-nothing rule.

## Decisions

- `## Metric` is fixed, ordered between `## Behavior` and `## Tasks`, mandatory for
  every spec created from the landing on; content is the metric block with provenance
  (optional `okr:` line) or one explicit `skipped: <reason>` line. The mandate's
  rationale and accepted risk are recorded in the discovery and read there by path.
- Events are born in the spec, in the Metric events table, under the payload rule
  stated in that section's paragraph.
- Lint enforcement starts as warnings, three checks: no `## Metric` section; a metric
  value without provenance; an event row citing a behavior row that does not exist,
  checked only when the spec has a `## Behavior` section (Medium specs carry
  behaviors inline and the gate judges their trace).
- The front's id is `instrumentation`: diff scope only this lap, criteria inline in
  `front-instrumentation.md`, source ladder of spec events then project convention.
- bb names no analytics product anywhere; the front checks against what the project
  itself does, detected in source.
- No durable record of review outcomes is built this lap; the soft component of the
  success signal is counted as `## Metric` states.

## Behavior

Happy path, once built:

1. A new spec's draft arrives with `## Metric` filled from the discovery record or as
   an explicit skip, and the exit gate renders it beside the coverage counter.
2. User-triggered behavior rows get rows in the events table, each citing the
   behaviors it instruments, with payload fields and channel.
3. Instrumentation enters `## Tasks` as ordinary tasks citing event rows, covering
   behaviors through those rows, and the existing build machinery proves them
   unchanged.
4. CI lints every spec and the three new warnings fire where expected.
5. On review, the probe resolves the ladder and offers the front; the finder checks
   the diff's added interactions against plan and convention; the verifier confirms;
   findings arrive ranked under the Instrumentation label.
6. Discover captures the success signal as "from <baseline> to <target> within
   <timeframe>" with provenance.
7. The export renders the trio from the two records without asking.

| WHEN                                            | THEN                                                             |
| ----------------------------------------------- | ---------------------------------------------------------------- |
| the work is internal, no user-visible behavior  | `## Metric` carries an operational measure or a reasoned skip    |
| a spec predates the landing                     | the warnings fire but nothing fails; no rewrite of history       |
| a metric value has no provenance                | the lint warns and the gate blocks it as an open item to resolve |
| the diff only wires analytics, no UI change     | the probe activates the instrumentation front                    |
| neither ladder rung resolves                    | the front is unavailable and the report names the remedy         |
| a payload field carries free text or content    | the front reports a finding citing the payload rule              |
| an event flows to a sink the plan does not name | the front reports a finding citing the channel                   |
| `## Metric` is skipped and the export runs      | the trio is omitted whole, no placeholder                        |
| a Medium spec carries behaviors inline          | the citation warning stays silent; the gate judges the trace     |
| the trio needs an OKR and no record carries one | the export asks for that field alone, and never invents it       |

## Metric

- Metric: the share of bb landings that cross the cycle measured, in two components.
  Hard: new specs whose `## Metric` passes the lint clean, read from CI output. Soft:
  landings whose review ran the instrumentation front and confirmed coverage, counted
  by hand over the dogfood window.
- Baseline: 0 of 15 records under `.bb/` carry any metric section (counted from the
  repo on 2026-08-24).
- Target: hard 100% of new specs, soft 80% of the first five landings, within 8 weeks
  of landing (the discovery's hypothesis, hardened at this spec's gate).
- Events: none; internal tooling, and the `.bb/` records themselves are the
  measurement surface (operational measure).

## Tasks

- [x] **1. Metric in the format and the lint**: `## Metric` added to
      `spec-format.md` (shape, order, skip form, events table with the payload rule,
      the task-through-event-row trace), the three warnings added to `lint_spec.py`,
      and the fixed-set mentions in the spec SKILL.md updated → behaviors 2, 3, 4 ·
      dep: — · verify: command (lint this spec, which carries the section, and an old
      spec, which lacks it: the new warnings fire only where expected and nothing
      errors)
- [ ] **2. The loop asks for it and the gate holds it**: in the spec SKILL.md and
      `draft-first.md`, the draft arrives with the Metric guessed with provenance or
      skipped; the exit gate renders the section beside the coverage counter, blocks
      a value without provenance as an open item, and judges the event trace for
      Medium specs the lint cannot check → behavior 1 · dep: 1 · verify: reading
- [ ] **3. The ninth front**: catalog row, availability probe, depth column, the
      criteria-path enumeration in the fan-out shape grown to hand the finder
      `front-instrumentation.md`, that new reference (ladder, criteria, finding
      shape, payload and channel checks, verify addendum), the review SKILL.md
      enumerations grown to nine, and the analytics-wiring triage note extended →
      behavior 5 · dep: 1 · verify: reading
- [ ] **4. Discover closes upstream**: baseline and target with provenance in the
      frame capture, the hardened hypothesis format in fit, the phase-table wording
      in the discover SKILL.md → behavior 6 · dep: — · verify: reading
- [ ] **5. Export reads instead of asking**: the trio sourced from the discovery
      record and `## Metric` by path in `export-spec.md`, asking only for a genuinely
      absent field, skip omitting the trio whole → behavior 7 · dep: 1 · verify:
      reading

## Out of scope

- the read half: live usage data pulled into the cycle, connector auth, a profile
  question for the person's analytics tools, an analytics page in the manifesto;
  _revisit_ on the second lap, over the data this lap creates
- the front's standalone surface scope, and with it the split of its criteria into a
  shared checklist file; _revisit_ when the surface scope lands
- the warning-to-error flip and its retroactivity; _revisit_ after the first five
  landings
- brisar capturing per-surface events in `design.md`; _revisit_ after the spec-side
  convention settles
- a durable record of review outcomes (what the soft count would read instead of a
  hand tally); _revisit_ alongside `exportar-pro-observador`
- data retention of the emitted events; the product's duty, not the cycle's

## Open

Nothing.
