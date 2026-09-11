# The event convention file: `EVENTS.md`

A project's event names and payloads are its own call, the same way a project's stack
is its own call. What bb standardizes is the shape that call gets written in, so a
script can read it and a skill can propose against it. `spec-format.md` already draws
this line for specs: bb owns the format, the project owns the content. This file is
that same split for events. bb fixes the file's name, its five parts and each part's
table shape; the project fills every cell.

`plugins/bb/scripts/check_events.py`, the checker, reads a project's `EVENTS.md` by
this contract. A convention file that drifts from the shape below is a file the checker
cannot read, reported as `C001` rather than guessed at.

## The file

One Markdown document, always named `EVENTS.md`, always at the repository root, the
directory holding `.git`. No `.bb/` fallback and no pointer file: the checker resolves
one path or reports none.

The checker finds its five parts by their heading text, a level-two heading matching
the name exactly:

- `## Grammar`
- `## Prefix registry`
- `## Dictionary`
- `## Exceptions`
- `## Catalog`

Each heading appears once and carries one table: a part written twice, or a second
table under a part, is a malformed file (`C001`), never a half-read one. Anything else
on the page, an opening paragraph, a note to the team, a changelog, is free: the checker
only reads these five sections and the tables inside them.

## Grammar

One line states the template, the three slots every event name fills:

```
{prefix}_{type}_{element}
```

The separator is fixed; the project supplies the vocabulary for each slot. A table
lists the closed set of valid types, the header row `type` and `meaning`:

| type   | meaning                        |
| ------ | ------------------------------ |
| `view` | a screen or panel rendered     |
| `sub`  | a form or action was submitted |

The registry (below) supplies the valid prefixes, and an _element_ is any run of
lowercase words joined by underscores, no further vocabulary needed for that slot.

A prefix may itself carry underscores (a project can register both `ai` and
`ai_summary`), so the checker never finds the boundary by counting separators. It takes
the longest registered prefix a name starts with, reads the next underscore-bound
token as the type, and reads everything after as the element.

Grammar also carries one paragraph of prose the checker does not parse: how many
events a feature should emit. Aim for 8–12 events per feature, never one per form
field. The spec draft follows this line when it proposes an events table; a count like
this needs judgment, not a table cell.

## Prefix registry

One namespace: a prefix is registered once, whatever feature it belongs to. The table
places each prefix in the project's own hierarchy, header row `prefix`, `group`,
`product`, `feature`:

| prefix  | group     | product | feature |
| ------- | --------- | ------- | ------- |
| `board` | Workspace | Orbit   | Boards  |

The checker asks only whether a prefix is registered; the `group`, `product` and
`feature` columns are documentary, read by a person and by the spec draft choosing
which prefix a new behavior belongs under.

## Dictionary

Every payload field a project's events carry, one row each, header row `field`,
`type`, `description`, `feature scope`:

| field      | type | description        | feature scope |
| ---------- | ---- | ------------------ | ------------- |
| `board_id` | id   | the board acted on | Boards        |

`type` is one of a closed list of five:

- `id`: an identifier for an entity or a row.
- `enum`: one of a fixed, named set of values.
- `number`: a count or another numeric measure.
- `boolean`: a true or false flag.
- `text`: free text: what a person typed, not a count or a label.

`text` is the field that lets a project name the exception instead of hiding it, and it
always needs a matching row in `## Exceptions`, keyed by the same field name. Why the
other four are the whole list without a convention file, and what free text costs a
legaltech's data duties, is the payload rule's own paragraph, in
`skills/spec/references/spec-format.md` under `### The events table`; this file names
the types and points there. `feature scope` is documentary, the same way the registry's columns are: the spec draft
reads it to find a feature's fields, and the checker ignores it. A field the dictionary
does not list is not a block; the checker warns, and the draft proposes the missing row
as a task.

## Exceptions

Every `text` field's approval, one row each, header row `field`, `status`,
`justification`, `retention`:

| field        | status       | justification                         | retention |
| ------------ | ------------ | ------------------------------------- | --------- |
| `query_text` | under-review | needed to debug empty-result searches | 30 days   |

`status` holds one of two literal values, `approved` or `under-review`. Both let the
field through; a `text` field with no row at all is what the checker blocks on. The
file records the retention window; nothing checks that the data actually expires
there.

## Catalog

Every event name the project has ever sent, one row each, header row `event` and
`status`:

| event               | status |
| ------------------- | ------ |
| `board_view_opened` |        |
| `LegacyBoardOpened` | legacy |

A name that predates this file carries the literal `legacy` in its `status` cell, and
the grammar check skips it (the duplicate check, below, does not): renaming it is out
of scope for the checker and for this convention. Every name after the file exists is
held to the grammar, an empty `status` cell, and gains the checker's full set of
checks. A pre-file name left without the mark is held to the grammar the same way, on
every run and for every spec, so a catalog seeded from a product that already emits
marks every inherited name `legacy` and renames later; otherwise that debt blocks
specs that never touched it.

The catalog is how a duplicate gets caught before it ships: a new name the checker sees
is compared against every row here, `legacy` or not. Landing an event is landing its
row: the instrumentation task shape in `skills/spec/references/spec-format.md` (its
events-table paragraph) is what appends the name here, in the change that ships the
event, with an empty `status` cell. The checker only reads this table; nothing here
writes it.

## Readers

| part            | read by                     |
| --------------- | --------------------------- |
| Grammar         | the checker, the spec draft |
| Prefix registry | the checker, the spec draft |
| Dictionary      | the checker, the spec draft |
| Exceptions      | the checker, the exit gate  |
| Catalog         | the checker, landing        |

## A worked example

A short, complete `EVENTS.md` for a fictional product, Orbit, clean by every code the
checker carries. `board` and `search` are ordinary prefixes; `ai` and `ai_summary` show
the longest-match rule, since a name under `ai_summary` never resolves to the shorter
`ai`. `LegacyBoardOpened` shows the one shape the grammar never touches.

```markdown
# Orbit: event conventions

This file is Orbit's event convention: the names a client may emit, the payload
fields they carry, and the events already live. `check_events.py` reads the five
tables below; everything else on this page is for the team.

## Grammar

Every event name follows `{prefix}_{type}_{element}`.

| type   | meaning                        |
| ------ | ------------------------------ |
| `view` | a screen or panel rendered     |
| `clk`  | a control was activated        |
| `sub`  | a form or action was submitted |
| `err`  | an operation failed            |

Aim for 8–12 events per feature, never one per form field.

## Prefix registry

| prefix       | group     | product | feature       |
| ------------ | --------- | ------- | ------------- |
| `board`      | Workspace | Orbit   | Boards        |
| `search`     | Workspace | Orbit   | Global search |
| `ai`         | Insights  | Orbit   | AI features   |
| `ai_summary` | Insights  | Orbit   | AI summaries  |

## Dictionary

| field          | type    | description                                              | feature scope |
| -------------- | ------- | -------------------------------------------------------- | ------------- |
| `board_id`     | id      | the board acted on                                       | Boards        |
| `source`       | enum    | where the action started (`toolbar`, `shortcut`, `menu`) | Boards        |
| `result_count` | number  | the number of matches returned                           | Global search |
| `is_shared`    | boolean | whether the board is shared with others                  | Boards        |
| `query_text`   | text    | the raw text the person typed into search                | Global search |

## Exceptions

| field        | status       | justification                         | retention |
| ------------ | ------------ | ------------------------------------- | --------- |
| `query_text` | under-review | needed to debug empty-result searches | 30 days   |

## Catalog

| event                    | status |
| ------------------------ | ------ |
| `board_view_opened`      |        |
| `board_clk_share`        |        |
| `search_view_opened`     |        |
| `search_sub_query`       |        |
| `ai_summary_view_opened` |        |
| `LegacyBoardOpened`      | legacy |
```
