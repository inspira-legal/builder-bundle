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
names the source it deviates from (an events table row, `EVENTS.md`'s own rows, the
convention in source, the payload rule), and one that cannot is dropped, never
reported as a guess.

## 1. The source ladder

Three rungs, resolved by the probe (`fronts.md`) before the front offers itself.
Keep every rung that resolves; they answer different questions:

1. **The branch spec's events table**: the `## Metric` section of the branch's
   `.bb/<slug>/spec.md`, when it carries the table or an explicit `Events: none`
   line. This rung is the **plan**: which events exist, which behavior rows each
   instruments, the payload fields, and the channel. `Events: none` is a plan that
   plans zero events, not an absent one: every emit the diff adds is then the
   reverse finding, citing that line.
2. **The project's `EVENTS.md`**, at the repository root (the format is
   `plugins/bb/references/events-convention.md`). This rung is the **file**: the
   registered prefixes, the type abbreviations, the dictionary and its exceptions.
   The caller resolves it and runs the checker over the emitted names the diff
   adds, once, before the fan-out, and hands its output and the file's resolved
   absolute path to the finder in the scope block (`fronts.md`, the instrumentation
   ladder and the fan-out step 2); the finder cites those lines and the file's rows
   instead of re-running the checker. A repository with no `EVENTS.md` skips this
   rung, and nothing else about the front changes. A file that resolves but comes back
   from the checker as `C001` alone is malformed (a part missing or written twice, a
   table without its header): that rung did not resolve for this run, so the front
   reports the `C001` line once, as a finding against the file itself, and reads naming
   and payload from rung 3 below.
3. **The analytics convention the project itself shows in source**: a typed event
   map, an emit wrapper, a generated client, whatever the code the diff touches
   already routes events through. This rung is the **convention inferred from
   code**, read whether or not the file above resolved: how an event is named,
   what shape it takes, where it flows. bb names no analytics product; the
   convention is detected in the project's own source, never assumed.

No rung resolving makes the front **unavailable**, never a degraded run. The
decision, and the remedy line the report owes when it fires, live in the probe
(`fronts.md`).

Report at the top of the front's section which rungs resolved and were judged
against. The plan disagreeing with either source is a finding, as it already was:
a planned event neither source can express, or an emitted name the plan never
mentions. The file and the code disagreeing is one too, the same way: a name or a
payload field the file's tables accept that the code's own convention shapes
differently, or the reverse.

## 2. The criteria, inline

Four checks. Coverage and channel read the plan (rung 1). Naming reads the file
(rung 2) where it resolves, the code's own convention (rung 3) where it doesn't,
and falls back to the table's own names where neither does. Payload runs on any
rung, citing the file's `## Dictionary` and `## Exceptions` rows and the checker's
own output line where rung 2 resolved and fired, alongside the payload rule; with a
rung missing, say in the front's section which checks had no source to read.

- **Coverage**: every interaction the diff adds has its planned event. An added
  interaction the events table plans an event for, with no emit in the diff, is a
  finding citing the table row. An emitted event the plan does not name is the
  reverse finding, same citation.
- **Naming**: event names follow the resolved convention: `EVENTS.md`'s grammar
  and prefix registry where the file resolves, the project's own source where it
  doesn't, the table's names where neither does. A name that matches none of them
  is a finding citing the convention's source, the checker's `C002` to `C004`
  line when the file is what caught it.
- **Payload**: payload fields hold only what the payload rule allows. The rule's
  single home is the events-table paragraph of
  `${CLAUDE_PLUGIN_ROOT}/skills/spec/references/spec-format.md` (spec's reference;
  read it there, this front cites it and never restates it). A dispatched finder
  cannot expand that variable, so the caller resolves it into the scope block
  beside the rungs (`fronts.md`, fan-out step 2). A field past the rule is a
  finding citing it; a field the checker already flagged as undocumented or
  unexcepted (`C005`, `C006`) is the same finding, citing the checker's line
  beside the payload rule. A field the checker passed under an exception (`C008`)
  is not a finding; the front names it in the report the way `## Exceptions`
  itself does, `approved` clean and `under-review` pending legal-lens.
- **Channel**: events flow to the channel the plan names. An event routed to a sink
  the plan does not name is a finding citing the channel column, or the event's own
  table row where the plan carries no channel column (a single-sink project's table
  omits it), and a sensitive payload routed to a third-party sink is that finding at
  its most severe.

## Finding shape

```
# | file:line | check (coverage, naming, payload, channel) | what deviates | source cited | priority | fix
```

`source cited` is the citation the discipline demands: the events table row,
`EVENTS.md`'s own row (or the checker's `path:line CODE` line reporting it, which in
the review's names mode points at the `EVENTS.md` row or section that caught the name), the
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
