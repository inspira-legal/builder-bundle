---
status: done
created: 2026-11-04
slug: measure-activation
---

# Activation events in the spec, and a measure that checks the machine first

Two things kept `/bb:measure` on its author's machine. A person without the `wave` CLI, the
`gcloud` CLI or a login ran it, and the skill went on with a file the person brought, as if that
file were data. And the way a company counts usage moved: a catalog of events in code marks each
event that counts as a person using the product, an _activation event_, the list applies to the
whole history, and it changes over time. The events table's `level` column and the measure's
check for "events with no level" no longer describe that.

This version moves bb to the activation vocabulary at both ends of the cycle, from the spec that
plans an event to the measurement that counts it, and puts a diagnosis in front of every
measurement.

## Decisions

- **The `level` column becomes `activation`, `yes` or `no`.** Every row carries the decision, `no`
  included, so a reviewer sees the question was asked of each event. The rule is the company's,
  in its `usage` document; no program checks the value.
- **The funnel is an optional line of the metric block**, the table's events in order. A step is
  never a new name, so the line adds no instrumentation.
- **The instrumentation task declares the event, its activation and the funnel where the project
  declares events**: `EVENTS.md` (an optional `activation` column in `## Catalog`, an optional
  `## Funnels` section the checker does not read) or the catalog in code the project's own
  instructions name.
- **`/bb:spec` proposes `okr:` from the `metrics` document, and `/bb:discover` reads the same
  document to propose the hypothesis, the OKR and the success signal as one set.** The signal a
  spec targets is then the number the company already publishes.
- **`references/company-definitions.md` holds the activation rule and where the list lives**: a
  catalog in code read with `gh`, a table, or a frozen list. The `data` document can name the
  company's dashboard.
- **The diagnosis runs before anything, in two halves.** The documentation base first, before any
  document is read; the database and the code right after the `data` and `usage` documents,
  because they name what to check.
- **No shell, no measurement.** The skill stops before reading any reference, and offers one
  alternative: reviewing what the person brought, every number marked _not checked_.
- **The person always logs in, in a terminal.** bb never asks for, reads, copies or shows a token.
  The diagnosis sends the token to `/dev/null` and never prints the output of `wave doctor` or
  `gh auth status`.
- **The guard owns the credential's messages.** `db_read.py` tells a missing CLI from an expired
  login and from a missing permission, and the diagnosis reuses those messages. A 403 for a quota
  is not a missing permission.
- **The list is read at a version and named in every answer.** A catalog in code is read at the
  commit of the branch's remote tip, saved as `catalog.csv` beside the queries, and named in the
  `catalog:` line of `measure.md`.
- **List and behavior are told apart with three numbers**: the published one, the previous window
  recounted with today's list, and today's. They add up exactly.
- **`unclassified.py` becomes `catalog_changes.py`.** With only activation events marked, every
  other event carries no mark, so "which fired events have no level" has no answer. The script
  compares two snapshots instead, counts a declared rename as one event, and prints the list for a
  query's `IN (...)`. The series marks no entry date, because the list applies to every week.

## Behavior

| WHEN                                                         | THEN                                                                 |
| ------------------------------------------------------------ | -------------------------------------------------------------------- |
| the session has no shell tool                                | the skill stops before any reference and says where it runs          |
| it stops for any reason                                      | the one alternative is the review, every number marked _not checked_ |
| `wave` is not installed                                      | the diagnosis points at `inspira-legal/builder-setup` and stops      |
| `wave doctor` fails                                          | the diagnosis points at `wave doctor` and stops                      |
| `gcloud` is not installed                                    | the diagnosis points at Google's official guide and stops            |
| the `gcloud` login expired                                   | the diagnosis gives `gcloud auth login --update-adc` and stops       |
| the account cannot read the events table                     | the diagnosis stops and the `access` document says what to ask for   |
| the list lives in code and `gh`, its login or the repo fails | the diagnosis stops before any query and names what failed           |
| the catalog file is not on the branch                        | the skill stops and reads no copy                                    |
| a spec row has an `activation` cell                          | the task writes the decision where the project declares the event    |
| the metric block has a `Funnel:` line                        | the task declares the funnel, and the measure counts it step by step |
| the company has a `metrics` document                         | the spec proposes `okr:`, and discover proposes the trio             |
| a number counts activation events                            | it carries the list's version                                        |
| the list changed since the last saved measurement            | the answer splits the difference into list and behavior              |
| no measurement was saved before                              | the answer says there is nothing to compare with                     |
| a week already published is counted with another version     | the new number sits beside the published one, both versions named    |
| an activation event left the catalog                         | the answer says how many people its exit took out                    |
| the catalog declares a rename                                | both names count as one event                                        |
| the table read receives only part of the catalog's events    | the answer says how many activation events it cannot see             |
| the `data` document names the dashboard                      | the link goes beside the number                                      |

## Metric

- Metric: people other than the skill's author who measured with `/bb:measure` end to end (the
  diagnosis passed, the query ran through the guard, the delivery named the list's version),
  counted from their measurement records and what they report
- Baseline: 0 (the one attempt reported before this version stopped with no `gcloud`, no login and
  no `wave`)
- Target: 3 people from at least two teams, within 2026-11-14 (set by the project's owner)
- Events: none, bb is a tool and emits no product event

## Attention points

- The catalog is read as text: the agent turns the file into `catalog.csv` by the marks the
  `usage` document describes. A change of the catalog's format breaks the snapshot without an
  error, and the counts compared with the document are the only check (`activation-list.md`).
- The diagnosis's read check is a dry run of a one-row query. An account that may plan the query
  but not read the rows passes it, and the real run stops later with the same access message
  (`diagnose.py`, `check_database`).
- `wave doctor`'s exit code is the only session check (`diagnose.py`, `check_docs`); a version of
  the CLI that exits 0 on a failed check would pass the diagnosis.
- A person without read access to the catalog's repository measures nothing that counts activation,
  until the company publishes the list in a table.

## Tasks

### The spec and discover

- [x] **1. Activation, funnel and OKR in the spec**: `spec-format.md`, `draft-first.md`,
      `events-convention.md`, `frame.md` and `company-definitions.md`. · verify: `lint_spec.py`
      and `check_events.py` pass with and without the column and the funnel line

### The measure

- [x] **2. The diagnosis**: `diagnose.py` and its tests, the credential messages in `db_read.py`,
      `diagnosis.md` and step 0 in `SKILL.md`. · verify: `diagnose_test.py` and `db_read_test.py`,
      with no network
- [x] **3. The list at a version**: `activation-list.md`, `catalog_changes.py` and its tests, and
      the readings in `official-metric.md`, `against-the-spec.md`, `measure-a-feature.md`,
      `method.md` and `deliver.md`. · verify: `catalog_changes_test.py`

### The release

- [x] **4. Release**: version, changelog, and what `/bb:measure` needs on the machine in the
      README. · verify: `bun run validate`, and no company name of a table, an event or a
      document in the diff

## Out of scope

- A data server the agent reads through, with its own credential. _revisit_ when a company offers
  one that is read only and returns aggregate numbers only
- A program that checks the `activation` value. _discarded_ the value is a decision, and a check
  could only check its spelling
- Logging in or installing a tool for the person. _discarded_ a login belongs to the person, in
  their terminal

## Open

Nothing.
