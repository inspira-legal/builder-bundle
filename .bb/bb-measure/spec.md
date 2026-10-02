---
status: in-progress
created: 2026-10-02
slug: bb-measure
---

# /bb:measure, and the level the spec proposes for each event

The cycle already writes the measure down. Every spec carries `## Metric`, with a baseline, a
target and the events its behaviors emit (`.bb/metricas-no-ciclo/spec.md`). Nothing reads that
section after the landing: the read half was parked there for a second lap, and this is that lap.
`/bb:measure` answers "did the feature hit the target its own spec wrote?" and any other usage
question about a product, through a guard that cannot write to the database and cannot return a
person's data. Beside it, the events table gains an optional level column, so `/bb:spec` proposes
each event's level when the company classifies its events, and the task agent writes the level in
code with the event.

Success is a person with bb installed, a login to the company's documentation base and read
access to the company's database measuring a feature alone, with the company's own definitions and the same
guard every other person uses.

## Where the company's definitions live

bb is public, so it carries the method and never the content. The content is the company's, and
the skill fetches it at run time: which tables hold the events, which filters every query carries,
what counts as usage, how to ask for access, the official metrics and each team's own metric.

It lives in the company's documentation base, read with the `wave` CLI. Each document declares
its own role with a tag, and a skill lists by the tag of the role a request needs:

| tag                  | what the document holds                                    | read when                           |
| -------------------- | ---------------------------------------------------------- | ----------------------------------- |
| `bb-measure:data`    | which database, the tables, the filters, the project id    | every measurement                   |
| `bb-measure:usage`   | what counts as usage, the level values, where the level is | every measurement, and by the spec  |
| `bb-measure:access`  | which permission to ask for, from whom, how to log in      | only when the credential fails      |
| `bb-measure:metrics` | the official metrics and the active OKRs                   | a target, or an `okr:` line         |
| `bb-measure:team`    | one team's official metric, beside the team's own tag      | someone asks for that team's metric |

A role can hold more than one document, and the skill reads every one the tag returns: a document
that grows splits by subject and both parts keep the tag. The skill says which documents it read.
`plugins/bb/references/company-definitions.md` owns this convention, and it has two readers,
`/bb:spec` for the `usage` role and `/bb:measure` for all five.

## The level column

The events table in `## Metric` gains one optional column, `level`. Its values are the company's,
declared in the `usage` document; bb defines none of them. When the draft designs an event, it
reads the `usage` document and proposes a level per row by the rule written there. A case the rule
does not settle is a gray area, asked like any other. Without a `usage` document the column does
not appear and the table is proposed the way it is today.

The column is documentary for the two programs that read the table: `lint_spec.py` finds the
`behaviors` column by name and `check_events.py` reads only `event` and `payload`. Its reader is
the task agent, which writes the level in code beside the event it wires.

## The skill

`/bb:measure` ports a method already proven on a real product: four modes, an inventory before any
query, a reading as product rather than numbers, and a delivery shaped by the intent of the
request.

| mode                   | when                                                          | what comes out                                                |
| ---------------------- | ------------------------------------------------------------- | ------------------------------------------------------------- |
| explore                | an open question about behavior                               | the number, its denominator, the caveat                       |
| measure a feature      | adoption, entry point, funnel or plan split of a live feature | one answer per question asked, what changes for the product   |
| official metric        | a company or team metric for a closed week                    | the series, compared with the week before                     |
| hypotheses and actions | after a measurement: where to evolve, what to do first        | each front with its data and hypothesis, the actions in order |

**Against the spec.** When the request names a feature with a spec, the skill starts from that
spec's `## Metric`: the metric, the baseline, the target, the `okr:` line and the events table.
The events table is the inventory's first list. The answer leads with the reading against the
target and the window it came from.

**The guard.** Every query goes through one script, `skills/measure/scripts/db_read.py`, standard
library only. Five locks, in order: a local check with no network (one statement, and it starts as
a read); the database's own classification of the statement in a dry run; a cost ceiling, sent
again with the real run so the database refuses on its side too; a refusal of any output column
that names a person or a conversation; and a refusal of any output value shaped like an email or a
long free text. The skill speaks of "the database" and never names one. The `data` document names
which database the company uses and its project id, and the skill passes both to the script. The
first and only adapter is BigQuery; a database the script has no adapter for is refused by name.
The ceiling is the script's own default.

**The credential.** Each person uses their own credential for the database, and their permission
there decides what they see. The skill never uses a key it finds in a repository's `.env`.

**Where the result goes.** The answer goes to chat by default. When it becomes context, the skill
writes `.bb/<slug>/measure.md` beside the feature's spec, a record only `/bb:measure` writes, and
the next measurement of that feature compares with it. With no spec, the skill asks where to save.
When someone else will read it, the skill builds a shareable document in two parts (the answer,
then how the analysis was built) with the document tool the session offers, preferring a claude.ai
artifact because people can share it, edit it and audit it. With no document tool, the saved file
is the document, and the skill says so in one line.

## Decisions

- The skill is `/bb:measure`. It closes the build trilha in verbs: discover, spec, implement,
  ship, measure.
- Nothing from any one company enters bb: no table name, no client id, no event name, no document
  key. Examples and tests use an invented product.
- The definitions are fetched at run time from the documentation base by role tag, and only the
  roles a request needs are read: `data` and `usage` always, `access` only when the credential
  fails, `metrics` only against a target or an `okr:` line, `team` only for that team's metric.
- A missing source stops the skill with the name of the source: a tag with no document, the
  `wave` CLI absent or logged out, the database credential expired. It never falls back to a
  copy.
- The guard lives in the script, never in the skill's text, and a refusal for cost is answered by
  rewriting the query, never by raising the ceiling.
- Output is aggregate numbers only: never a name, an email, a list of people or the text of a
  conversation. A request about content is refused, and the aggregate that answers the same
  question is offered.
- Every analysis starts with the inventory of what actually fires, and closes with what changes
  for the product.
- The delivery follows the intent: chat by default, `.bb/<slug>/measure.md` when it becomes
  context, a shareable document when someone else will read it, a claude.ai artifact first when
  the session offers one. When the intent is unclear, the answer goes to chat with a one line offer
  to go up a level.
- The method is neutral about the database. The skill's text says "the database", the `data`
  document names which one, and each database the guard speaks to is an adapter inside the
  script. BigQuery is the first.
- The level column is optional and its values are the company's. The lint never validates a value.

## Behavior

Happy path, against a spec:

1. A person asks whether a feature hit its target, from the repository that holds its spec.
2. The skill reads the spec's `## Metric`: metric, baseline, target, `okr:` line, events table.
3. It lists the `data`, `usage` and `metrics` documents by tag and reads each one.
4. It runs the inventory of the table's events through the guard, then the metric's query.
5. It answers with the reading against the target, the window, the denominator, what changes for
   the product and the caveats, and names the documents it read.

Happy path, a new event in a spec:

6. A person runs `/bb:spec` for a feature that emits events.
7. The draft reads the `usage` document and the events table arrives with a proposed level per
   row.
8. The lint and the event checker pass, and the task agent writes the level beside the event.

| WHEN                                                              | THEN                                                                         |
| ----------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| the query is not a read, holds more than one statement            | the guard refuses before anything leaves the machine, and says why           |
| the dry run classifies the statement as anything but a read       | the guard refuses, including when the database names no type                 |
| the query would read past the ceiling                             | the guard refuses; the skill rewrites the query and never raises the ceiling |
| the output has a person or conversation column                    | the guard refuses and shows no row                                           |
| an output value looks like an email or a long free text           | the guard refuses and shows no row                                           |
| a tag the request needs returns no document                       | the skill stops and names the missing tag                                    |
| the `wave` CLI is missing or logged out                           | the skill stops and says the documentation base was the source that failed   |
| the database credential expired                                   | the skill stops, reads the `access` document and gives its renewal step      |
| the `data` document names a database the guard has no adapter for | the guard refuses and names the database, and the skill stops                |
| the request has no spec                                           | the skill measures anyway, in the modes that need no target                  |
| the spec's baseline is `skipped`                                  | the skill measures the baseline first and says it is the first reading       |
| the request asks for what a person wrote                          | the skill refuses and offers the aggregate                                   |
| the week asked for has not closed                                 | the skill says the number is partial, or uses the last closed week           |
| the company has no `usage` document                               | the spec's events table carries no level column, as today                    |
| a spec carries the level column, or does not                      | the lint and `check_events.py` pass either way                               |

## Metric

- Metric: landed specs whose `## Metric` got a measured reading through `/bb:measure`, counted by
  hand over the dogfood window.
- Baseline: 0, since no skill reads `## Metric` after a landing (repo state, 2026-10-02).
- Target: three landed specs read against their target within 6 weeks of this landing (Matheus
  Aguiar's estimate).
- Events: none; internal tooling, and the reading itself is the measure.

## Attention points

- BigQuery returns the statement type only on a simulated job (`jobs.insert` with `dryRun`), not
  on the `jobs.query` shortcut, and the guard's second lock depends on that field.
- The output column check matches names, so `email AS x` passes it; only the content check catches
  it, and that check is a net, not a guarantee.
- A table cell above 100 characters breaks `fmt:check`, and the method's tables carry long cells.
- The `wave` CLI's JSON shape is owned outside this repo; a CLI update can change it under the
  skill.
- A role tag is free text, so a typo makes a document invisible to the skill.
- The method comes from a private skill, and any example, query or test copied from it carries a
  real company's table names, client ids or usage numbers into a public repo.

## Tasks

### Foundation

- [ ] **1. The company definitions**: `plugins/bb/references/company-definitions.md` states the
      five role tags, how a skill lists and reads them with the `wave` CLI, what it says when a
      role is missing, and its two readers. · verify: reading

### The two readers

- [ ] **2. The level column**: the events table in `spec-format.md` gains the optional `level`
      column, and `draft-first.md` proposes it from the `usage` document. · verify:
      `lint_spec.py` and `check_events.py` pass over a spec with the column and one without
- [ ] **3. The read-only guard**: `skills/measure/scripts/db_read.py` and its tests, the locks
      that need no database written once, BigQuery as the first adapter, the database and the
      project id as arguments, invented data in every case. · verify: the test script passes
      with no network

### The skill

- [ ] **4. /bb:measure**: the `SKILL.md` as a router over one reference per mode, the reading of
      a spec's `## Metric`, the delivery by intent and the closing gate, and `measure.md` joins
      the folder contract in `spec-state.md`. · verify: reading

### Close

- [ ] **5. What the person installing sees**: the README, the skill count in the README and the
      plugin description, the version, the `CHANGELOG.md` entry and the handoff journey map. ·
      verify: `bun run validate`, `bun run fmt:check`, and a search of the diff for a real
      company's tables, client ids and event names comes back empty

## Out of scope

- The level written into each event by the product's own code: the product's work, read here only
  through the `usage` document.
- `/bb:spec` filling the `okr:` line from the `metrics` document; _revisit_ once `/bb:measure`
  reads it.
- A second database adapter; _revisit_ when a company on another database asks.
- The lint validating a level value against the company's rule.
- Any write to the database, and any key that is not the person's own credential.

## Open

Nothing.
