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
   `.bb/<slug>/spec.md`, when it carries one. This rung is the **plan**: which
   events exist, which behavior rows each instruments, the payload fields, and the
   channel.
2. **The analytics convention the project itself shows in source**: a typed event
   map, an emit wrapper, a generated client, whatever the code the diff touches
   already routes events through. This rung is the **convention**: how an event is
   named, what shape it takes, where it flows. bb names no analytics product; the
   convention is detected in the project's own source, never assumed.

Neither rung resolving makes the front **unavailable**, never a degraded run, and
this absence the report explains: one line naming the remedy, write the events
table in the spec's `## Metric`, or point the review at the project's emit wrapper.
The decision itself lives in the probe (`fronts.md`).

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
  `${CLAUDE_PLUGIN_ROOT}/skills/spec/references/spec-format.md` (spec's reference;
  read it there, this front cites it and never restates it). A field past it is a
  finding citing that rule.
- **Channel**: events flow to the channel the plan names. An event routed to a sink
  the plan does not name is a finding citing the channel column, and a sensitive
  payload routed to a third-party sink is that finding at its most severe.

## Finding shape

```
# | file:line | check (coverage, naming, payload, channel) | what deviates | source cited | priority | fix
```

`source cited` is the citation the discipline demands: the events table row, the
convention's file and line, or the payload rule's paragraph. Priorities are
**High** (a payload or channel finding, the data duty the mandate protects),
**Medium** (a planned event missing, or emitted off-plan), and **Low** (a name off
the convention that routing survives). The report ranks them the way it ranks
design's (`verify.md`, §4): High at tier 2, Medium at tier 3, Low at tier 4. Cap 8.

## Scope discipline

- Only interactions and emit sites the diff added or changed. A surface that was
  already uninstrumented before this branch is not this branch's finding: one line
  at the end as existing debt.
- An added interaction no events table plans for (rung 1 absent) is not a coverage
  finding; with no plan there is nothing to cite. One closing line names it as a
  gap for the spec's events table.
- When the repo's `CODE_REVIEW_GUIDE.md` itself states an analytics rule, a
  violation of it is a `rules` finding with the guide cited, not a duplicate here.
  This front judges against the ladder's sources.

## Verify addendum

`instrumentation` candidates verify like `rules`, against the cited source instead
of the guide (`verify.md`, "The addendum"): the verifier opens what the finding
cites, the events table row, the convention's source, or the payload rule's
paragraph, and checks that the source says what the finding claims and that the
diff line actually deviates from it. A citation that does not hold up is REFUTED,
the same discipline that kills hallucinated rules. This paragraph is what the
fan-out appends to the verifier's prompt for this front's candidates.
