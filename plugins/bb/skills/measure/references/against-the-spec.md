# Against the spec: did the feature hit its target?

Read this when the request names a feature with a spec, or asks whether a feature hit its target.
The spec's `## Metric` already says what success looks like, in the team's own words, so the
measurement starts there instead of from a blank question. The section's shape belongs to
`<plugin-root>/skills/spec/references/spec-format.md`, `## The Metric section`; this file says how
to read it as a measurement plan.

## Find the spec

The spec lives at `.bb/<slug>/spec.md` in the repository the feature was built in. Match the
feature the person named against the slugs and the titles there. When more than one fits, or none
does, ask which one, with the candidates as options. When the person names no feature and the
session is already on a spec, take that one and say so in one line.

## Read the block

| line        | what it gives the measurement                                                |
| ----------- | ---------------------------------------------------------------------------- |
| `Metric:`   | the one measure, and how it is read: the query's definition                  |
| `Baseline:` | the reading before the landing, with its provenance: the point of comparison |
| `Target:`   | where it should land and within which timeframe: the bar and the window      |
| `okr:`      | the OKR it serves: read the `metrics` document for its official definition   |
| `Events:`   | the table of events, or `none` and why: the inventory's first list           |

- **The `Metric:` line is prose.** Turn it into a definition before writing a query: who counts,
  what they do, over which window, against which denominator. Write that definition at the top of
  the query file, so the person can check the translation.
- **A target with no timeframe has no window.** Say so, and measure the window since the landing
  until the last closed week.
- **The landing date** comes from the inventory, not from the spec: the first day the table's
  events fire for customers. A spec does not know the day it shipped.
- **`Baseline: skipped: <reason>`** means nothing measured it before. Measure the baseline first,
  over the window before the landing, and say it is the first reading.
- **An `okr:` line** names an official metric: its definition in the `metrics` document wins over a
  paraphrase in the spec, and a difference between the two is a caveat in the answer.
- **`Events: none`** leaves the inventory without a first list: build it from the behaviors the
  spec describes and the events the code emits for them.

## Read the events table

Each row is an event the feature promised to emit. The inventory runs over every name in the
table, and each row gets one of three readings:

- **fires as planned**: it fires, from the landing on, with the payload the row lists;
- **fires differently**: a field missing or a value the row did not plan, which is a measurement
  gap to number in the answer;
- **does not fire**: a caveat that limits what the measurement can say, never a zero.

When the table carries a `level` column, the company's `usage` document says what each level
means for its metrics. Read the levels the spec planned against the ones the events actually
carry, when the `usage` document says where the level lives in the data.

## The answer

Open with the reading against the target, in one sentence: the number, the target, the window and
the denominator. "73 of 210 teams with the feature (35%) shared a board in the 4 weeks since the
landing, against a target of 40%." Then:

1. **The verdict**, one of three: hit, missed, or too early to read (the window has not closed, or
   the events do not fire yet). Never a verdict the data does not carry.
2. **How it moved**: from the baseline to now, and the week by week series when the window has
   five weeks or more.
3. **The events table, read**: the rows that fire as planned, differently, or not at all.
4. **What changes for the product**, and the caveats, as `method.md` closes every answer.
5. **The documents read**: the key and the title of each company document the answer used.
