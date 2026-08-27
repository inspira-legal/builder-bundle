# Finding levels

Every finding bb writes carries one of two levels. A review calls them **Bloqueante** and
**Sugestão**; a repository's `CODE_REVIEW_GUIDE.md` calls the same two `HIGH` and `LOW`. Two
names, one pair of levels. This page is their definition: what each one means, which name goes
on which surface, which findings land where, what separates an inline comment from a line in
the review body, and how a guide that still ranks a rule `MEDIUM` reads.

## Where this applies

`/bb:review` reads it when a front assigns a level, when the verify pass ranks, and when the
report and the comments go out. `/bb:review-setup` reads it when it writes a repository's
`CODE_REVIEW_GUIDE.md`. Both write findings, neither owns the scale, so the scale lives here.

## The two levels

- **Bloqueante**, `HIGH` in a guide: something the diff shipped is broken, unusable for
  someone, or breaks a rule the guide states as mandatory. The verdict is CHANGES REQUESTED.
- **Sugestão**, `LOW` in a guide: everything else that is still worth saying. Alone it
  never sets the verdict; three or more in one PR make it NEEDS DISCUSSION.

There is no third level. What went is the middle rung, where a reader stops deciding, because
`MEDIUM` meant "worth saying" in one file and "almost blocking" in the next.

Where a run needs a finer cut than two, it is the concrete-cost gate below, which is a bar the
review already measures, not a new rung.

The level says how bad the finding is. The verify verdict (`CONFIRMED`, `PLAUSIBLE`,
`REFUTED`) says how sure the reviewer is. They are two axes, and `verify.md` §4 combines them
when it ranks.

## Which name goes where

| surface                                                                 | vocabulary                            |
| ----------------------------------------------------------------------- | ------------------------------------- |
| the review's report, its item labels, a PR comment body, a verdict line | **Bloqueante** / **Sugestão**         |
| a guide's **Level** field, its levels table, a verdict rule it states   | `HIGH` / `LOW`                        |
| a JSON field, a script argument, any other machine value                | `bloqueante` / `sugestao`, unaccented |

The guide keeps `HIGH` and `LOW` because that is the field every `CODE_REVIEW_GUIDE.md` in the
org already carries: a guide written before this page reads correctly with no migration, and a
verdict rule it states in those terms still answers. The translation happens where the finding
is written, so a deviation from a rule the guide ranks `HIGH` enters the report as a
Bloqueante and nobody has to hold two ladders in their head.

Spelling: `Sugestão` carries its accent in prose and in a report label, and `HIGH` / `LOW` are
uppercase wherever a guide states them.

## Where each front lands

| finding                                                                   | front                  | level      |
| ------------------------------------------------------------------------- | ---------------------- | ---------- |
| a bug the diff shipped, at either verdict                                 | `front-correctness.md` | Bloqueante |
| a deviation from a rule that states the stakes (mandatory, never, quebra) | `front-rules.md`       | Bloqueante |
| every other deviation, and every rule the guide states with no level      | `front-rules.md`       | Sugestão   |
| a missing happy path                                                      | `front-contract.md`    | Bloqueante |
| a missing mapped edge, a missing test, scope drift                        | `front-contract.md`    | Sugestão   |
| a `Critical` or `Major` accessibility failure                             | `front-a11y.md`        | Bloqueante |
| a `Minor` failure or an `Enhancement`                                     | `front-a11y.md`        | Sugestão   |
| every cleanup, since the front is behavior-preserving                     | `front-quality.md`     | Sugestão   |

`front-a11y.md` keeps `Critical` / `Major` / `Minor` / `Enhancement` internally, because those
priorities are WCAG's and not bb's. The mapping in the table above happens at the report
boundary, when the front's findings enter the unified report, so a finding reads as one of the
two levels everywhere the user and GitHub see it.

## The concrete-cost gate

A **Sugestão** that names a **concrete cost** can be posted as an inline comment. One that
cannot goes into a single aggregated line in the review body, never inline.

A concrete cost is what `front-quality.md` asks for in its `custo concreto` column: what
exactly is duplicated and where the existing helper already is, what work is wasted per call,
what a future editor has to keep in sync, who reads the wrong value. "This could be cleaner"
is not a cost.

Two things the gate does not touch:

- **A Bloqueante never passes through it.** It earns its inline comment by being a Bloqueante.
- **The report stays complete.** The gate governs what reaches GitHub. Every verified finding
  gets its line in the report either way, and the aggregated body line names the count it
  carries so the reader can go find them.

## Reading a guide that still ranks a rule MEDIUM

A `CODE_REVIEW_GUIDE.md` with `MEDIUM` rules collapses them **at read time**. No repository is
blocked by a three-rung guide.

| in the guide | a review reads it as | the migration rewrites it to |
| ------------ | -------------------- | ---------------------------- |
| `HIGH`       | Bloqueante           | `HIGH`                       |
| `MEDIUM`     | Sugestão             | `LOW`                        |
| no level     | Sugestão             | `LOW`                        |

The third column is `/bb:review-setup`'s, which is what closes the drift instead of
re-reading it every run (`skills/review-setup/references/update-delta.md`).

A verdict rule the guide states in three rungs ("qualquer MEDIUM ⇒ NEEDS DISCUSSION") reads
through the same table, so it is the Sugestão count that answers it.

Whenever the collapse fires, the report carries **one drift line**, separate from the rule
deviations as `front-rules.md` §5 keeps every drift finding:

```
Ladder drift: CODE_REVIEW_GUIDE.md ranks 12 rules MEDIUM, read here as Sugestão. Run
`/bb:review-setup` to migrate the guide.
```

One line per review, with the rule count, not one line per rule.
