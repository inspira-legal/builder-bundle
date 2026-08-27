# Finding levels

Every finding bb writes carries one of two levels, `Bloqueante` or `Sugestão`. This page is
their definition: what each one means, which findings land where, what separates an inline
comment from a line in the review body, and how a guide written in the old vocabulary reads.

## Where this applies

`/bb:review` reads it when a front assigns a level, when the verify pass ranks, and when the
report and the comments go out. `/bb:review-setup` reads it when it writes a repository's
`CODE_REVIEW_GUIDE.md`. Both write findings, neither owns the scale, so the scale lives here.

## The two levels

- **Bloqueante**: something the diff shipped is broken, unusable for someone, or breaks a rule
  the guide states as mandatory.
- **Sugestão**: everything else that is still worth saying.

There is no third level. Where a run needs a finer cut than two, it is the concrete-cost gate
below, which is a bar the review already measures, not a new rung.

The level says how bad the finding is. The verify verdict (`CONFIRMED`, `PLAUSIBLE`,
`REFUTED`) says how sure the reviewer is. They are two axes, and `verify.md` §4 combines them
when it ranks.

## Where each front lands

| finding                                                                    | front                  | level      |
| -------------------------------------------------------------------------- | ---------------------- | ---------- |
| a bug the diff shipped, at either verdict                                  | `front-correctness.md` | Bloqueante |
| a deviation from a rule that states the stakes (mandatory, never, quebra)  | `front-rules.md`       | Bloqueante |
| every other deviation, and every rule the guide states with no severity    | `front-rules.md`       | Sugestão   |
| a missing happy path                                                       | `front-contract.md`    | Bloqueante |
| a missing mapped edge, a missing test, scope drift, a stylistic divergence | `front-contract.md`    | Sugestão   |
| a `Critical` or `Major` accessibility failure                              | `front-a11y.md`        | Bloqueante |
| a `Minor` failure or an `Enhancement`                                      | `front-a11y.md`        | Sugestão   |
| every cleanup, since the front is behavior-preserving                      | `front-quality.md`     | Sugestão   |

`front-a11y.md` keeps `Critical` / `Major` / `Minor` / `Enhancement` internally, because those
priorities are WCAG's and not bb's. The mapping in the table above happens at the report
boundary, when the front's findings enter the unified report, so a finding reads as one of the
two levels everywhere the user and GitHub see it.

## The concrete-cost gate

A Sugestão that names a **concrete cost** can be posted as an inline comment. One that cannot
goes into a single aggregated line in the review body, never inline.

A concrete cost is what `front-quality.md` asks for in its `custo concreto` column: what
exactly is duplicated and where the existing helper already is, what work is wasted per call,
what a future editor has to keep in sync, who reads the wrong value. "This could be cleaner"
is not a cost.

Two things the gate does not touch:

- **A Bloqueante never passes through it.** It earns its inline comment by being a Bloqueante.
- **The report stays complete.** The gate governs what reaches GitHub. Every verified finding
  gets its line in the report either way, and the aggregated body line names the count it
  carries so the reader can go find them.

## Reading a guide written in HIGH / MEDIUM / LOW

A `CODE_REVIEW_GUIDE.md` still written in the legacy ladder collapses **at read time**. No
repository is blocked by an old guide.

| in the guide | read as    |
| ------------ | ---------- |
| `HIGH`       | Bloqueante |
| `MEDIUM`     | Sugestão   |
| `LOW`        | Sugestão   |
| no severity  | Sugestão   |

A guide that mixes both vocabularies reads the same way: an entry already at two levels stands
as written, a legacy entry collapses by the table, and the drift line below fires once for the
file. A verdict rule stated in the legacy vocabulary ("qualquer HIGH ⇒ CHANGES REQUESTED")
reads through the same table, so any Bloqueante requests changes.

Whenever the collapse fires, the report carries **one drift line**, separate from the rule
deviations as `front-rules.md` §5 keeps every drift finding:

```
Guide drift: CODE_REVIEW_GUIDE.md ranks its rules as HIGH / MEDIUM / LOW (12 rules), read here
as Bloqueante / Sugestão. Run `/bb:review-setup` to migrate the guide.
```

One line per review, with the rule count, not one line per rule.

## How to spell the level

- Prose, report labels, and comment bodies carry the accent: `Bloqueante`, `Sugestão`.
- A JSON field, a script argument, and any other machine value are lowercase and unaccented:
  `bloqueante`, `sugestao`.
