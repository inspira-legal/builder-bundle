# Front: instrumentation, the events the diff owes its plan

One scope this lap: the **diff**. One finder over the interactions the branch added,
judged against the plan and the convention the ladder below resolves. The standalone
surface scope a11y and design have comes later, and until it does the criteria live
inline here (§2) instead of in a shared checklist file.

What it checks is semantic, not presence. A diff that calls an emit function
somewhere is not covered; covered means every interaction the diff adds has its
planned event, named the way the project names events, carrying only what the
payload rule allows, flowing to the channel the plan names. The discipline is the
`rules` front's: **a finding is worth what its citation is worth**, so every finding
names the source it deviates from (an events table row, the convention in source,
the payload rule), and one that cannot is dropped, never reported as a guess.

## 1. The source ladder

Two rungs, resolved by the probe (`fronts.md`) before the front offers itself. Keep
every rung that resolves; they answer different questions:

1. **The branch spec's events table**: the `## Metric` section of the branch's
   `.bb/<slug>/spec.md`, when it carries the table or an explicit `Events: none`
   line. This rung is the **plan**: which events exist, which behavior rows each
   instruments, the payload fields, and the channel. `Events: none` is a plan that
   plans zero events, not an absent one: every emit the diff adds is then the
   reverse finding, citing that line.
2. **The analytics convention the project itself shows in source**: a typed event
   map, an emit wrapper, a generated client, whatever the code the diff touches
   already routes events through. This rung is the **convention**: how an event is
   named, what shape it takes, where it flows. bb names no analytics product; the
   convention is detected in the project's own source, never assumed.

Neither rung resolving makes the front **unavailable**, never a degraded run. The
decision, and the remedy line the report owes when it fires, live in the probe
(`fronts.md`).

Report at the top of the front's section which rungs resolved and were judged
against. The rungs disagreeing is itself a finding: a planned event the project's
wrapper cannot express, or an emitted name the plan never mentions.

## 2. The criteria, inline

Four checks. Coverage and channel read the plan (rung 1), naming reads the
convention (rung 2, falling back to the table's own names), and payload runs on any
rung; with one rung missing, say in the front's section which checks had no source
to read.

- **Coverage**: every interaction the diff adds has its planned event. An added
  interaction the events table plans an event for, with no emit in the diff, is a
  finding citing the table row. An emitted event the plan does not name is the
  reverse finding, same citation.
- **Naming**: event names follow the resolved convention, the project's own where
  it shows one, the table's names where it does not. A name that matches neither is
  a finding citing the convention's source.
- **Payload**: payload fields hold only what the payload rule allows. The rule's
  single home is the events-table paragraph of
  `<plugin-root>/skills/spec/references/spec-format.md` (spec's reference;
  read it there, this front cites it and never restates it). A dispatched finder
  has no plugin root of its own, so the caller puts the resolved path into the scope block
  beside the rungs (`fronts.md`, fan-out step 2). A field past the rule is a
  finding citing it.
- **Channel**: events flow to the channel the plan names. An event routed to a sink
  the plan does not name is a finding citing the channel column, or the event's own
  table row where the plan carries no channel column (a single-sink project's table
  omits it), and a sensitive payload routed to a third-party sink is that finding at
  its most severe.

## Finding shape

```
# | file:line | check (coverage, naming, payload, channel) | what deviates | source cited | priority | fix
```

`source cited` is the citation the discipline demands: the events table row, the
convention's file and line, or the payload rule's paragraph. Priorities are
**High** (a payload or channel finding, the data duty the mandate protects),
**Medium** (a planned event missing, or emitted off-plan), and **Low** (a name off
the convention that routing survives). The report ranks the three per `verify.md`
§4, which names them in its tiers. Cap 8.

## Scope discipline

- Only interactions and emit sites the diff added or changed. A surface that was
  already uninstrumented before this branch is not this branch's finding: one line
  at the end as existing debt.
- An added interaction no plan covers (rung 1 absent, which `Events: none` is not)
  is not a coverage finding; with no plan there is nothing to cite. One closing
  line names the gap: in local mode, for the spec's events table; in the
  external-PR mode, where rung 1 never exists, against the project's own
  convention, never a bb artifact the other repo does not have.
- When the repo's `CODE_REVIEW_GUIDE.md` itself states an analytics rule, a
  violation of it is a `rules` finding with the guide cited, not a duplicate here.
  This front judges against the ladder's sources.
