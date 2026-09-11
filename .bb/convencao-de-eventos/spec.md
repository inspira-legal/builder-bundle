---
status: done
created: 2026-09-10
slug: convencao-de-eventos
---

# the event convention becomes a file bb reads

Inspira's event convention is about to lose the app that mediated between its written
rule and its practice (the framing is `.bb/convencao-de-eventos/discovery.md`, `## Problem`).
This spec gives the convention a form bb can read and check, without carrying its values:
bb defines the **format** of a project-level event convention file and ships the
**checker** that reads it; the project writes the **content**. The same split
`spec-format.md` already makes for specs. Three moments of the cycle then read the file:
`/bb:spec` proposes the events table from it, the exit gate checks the table against it,
and `/bb:review`'s instrumentation front cites it above the convention it used to infer
from code. The manual itself, the Inspira convention file in `inspira-legal/app`, is a
later round; this spec ends with a draft of it, run dry through the checker, as the proof
the format holds real data (`## Cuts` in the discovery record names what stays out).

## The convention file

One Markdown document at the repository root, `EVENTS.md`: a person reads it as the
manual, the checker reads its tables. Five parts, each a section the checker finds by
name:

| Part            | What it carries                                                      | Read by             |
| --------------- | -------------------------------------------------------------------- | ------------------- |
| Grammar         | the name template and the closed list of type abbreviations          | checker, spec draft |
| Prefix registry | feature slug to its home (grupo, produto, feature)                   | checker, spec draft |
| Dictionary      | payload field, type, description, feature scope                      | checker, spec draft |
| Exceptions      | free-text fields allowed, each with status, justification, retention | checker, gate       |
| Catalog         | every existing event name, the pre-file ones marked `legacy`         | checker, landing    |

The grammar is a template with three slots, `{prefix}_{type}_{element}`, the separator
fixed. The project fills the slot vocabularies: the registry is the set of valid prefixes,
the abbreviations table the set of valid types, and an element is lowercase words joined by
underscores. A prefix may itself contain underscores (`ai_chat`, `trial_checkout`), which is
why the checker splits a name by the registry and not by counting separators: the longest
registered prefix the name starts with, then `_<type>_`, then the element. Guidance the
checker cannot count, the generator's granularity rule (eight to twelve events per feature,
never one per form field), lives in the file as prose for the spec draft to follow.

The registry is one namespace: a prefix is registered once, whatever its home, and the
home columns place a feature for the spec draft and for the reader; the checker only asks
whether the prefix is registered. The dictionary's feature-scope column is documentary the
same way: the draft reads it to pick a feature's fields, the checker ignores it.

The catalog is the file's memory. Names marked `legacy` predate the file and are exempt
from the grammar; every name after it is on the grammar, and every spec whose events land
appends them to the catalog as part of landing, so the next spec's duplicate check sees
them. The checker reads the catalog; it never writes it.

## Where the checks run

- **Spec draft** (`/bb:spec`, step 1): with a convention resolved, the events table arrives
  proposed from the behavior rows: names on the grammar, prefixes from the registry, payload
  fields from the dictionary. A behavior whose feature has no registered prefix does not get
  an invented one: the draft proposes the registry entry as a task that edits the convention
  file, and the name waits on it. A payload field the dictionary lacks is proposed the same
  way, as a task adding the entry, without the wait: the row stands and the gate shows the
  warning.
- **Spec check and gate** (`/bb:spec`, steps 6 and 7): the checker runs beside the lint
  over the spec's events table. Its E-codes are open items the gate blocks on, resolved by
  fixing the row or by an exception written as a task on the convention file; never waved
  through. Its W-codes are shown and judged.
- **Landing** (`/bb:implement`, through the spec's instrumentation tasks): the task that
  wires an event also appends its name to the catalog, so the file grows with use.
- **Review** (`/bb:review`, the instrumentation front): the probe resolves the convention
  file as a rung of its own, between the spec's plan and the convention inferred from code.
  The caller runs the checker over the emitted names the diff adds, before the fan-out, and
  hands its output to the finder inside the scope block; the finder cites those lines and
  the file's rows for naming and payload, and reports the file and the code disagreeing as
  a finding, the same as the two existing rungs disagreeing today.

## The checker

`check_events.py`, a shared script (spec and review both call it), Python standard library
only, output in the lint's own shape: `path:line CODE message`, exit 1 when an E-code
fired. Two inputs: the convention file (resolved from the repository root, or passed) and
either a spec path, whose `## Metric` events table it reads, or a list of event names (the
review's emitted names). It never edits anything, it never raises on input (every malformed
input is a coded line), and it always prints at least one line: the findings, or
`checked N names, clean`, so silence never reads as a pass.

| Code | Severity | Fires when                                                                                        |
| ---- | -------- | ------------------------------------------------------------------------------------------------- |
| C001 | E        | the convention file is malformed: a part missing, a table without header, a prefix or field twice |
| C002 | E        | a name starts with no registered prefix (an empty name included)                                  |
| C003 | E        | the type slot is not in the abbreviations table (`erro`, `click`)                                 |
| C004 | E        | the element is not lowercase words joined by underscores                                          |
| C005 | W        | a payload field is not in the dictionary                                                          |
| C006 | E        | a payload field typed `text` has no exception row                                                 |
| C007 | E        | a new name duplicates a catalog name or another planned name                                      |
| C008 | W        | an exception row was used, named with its status (`approved` or `under-review`)                   |
| C009 | W        | no source to check against: no convention file, no repository root, or no `event` column          |
| C010 | E        | an input could not be read: the spec path, the names file, a bad encoding                         |

A catalog name marked `legacy` is exempt from C002 to C004 and collides on C007 when a spec
plans it again. A plan of zero events (`Events: none`, a `skipped:` section, a table with a
header and no rows) is not a missing source: the checker prints the clean line with zero
names. In the events table the payload fields are the backticked tokens of the
cell; anything else in the cell is a note and is left alone.

The convention file resolves before any plan is read, so a missing file is the C009 line
even when the spec plans zero events. A line with no path of its own (no file, no root)
anchors to the spec path when one was given and to the working directory otherwise, at
line 0, so the shape stays `path:line CODE message` for every reader.

## Decisions

- **One Markdown document at the repository root, fixed name `EVENTS.md`.** People read it
  as the manual; the checker reads its tables. The precedent is `CODE_REVIEW_GUIDE.md`: a
  fixed name at the root the review already knows how to find, visible to the whole team
  and not only to bb users. Resolution is the repository root, the directory holding
  `.git`, from wherever the script runs; a monorepo has one file, and the registry's home
  column tells the apps apart. No `.bb/` fallback and no pointer file: one place, or none.
- **The checker is one shared script**, `plugins/bb/scripts/check_events.py`, because spec
  and review both read it (the shared-scripts rule in `.claude/CLAUDE.md`). It carries its
  own small table parser rather than importing `lint_spec.py` across skill folders: fifteen
  lines duplicated beat a cross-folder import path that breaks when a skill moves. (guess:
  cheap to reverse)
- **`lint_spec.py` does not grow.** Grammar is the checker's; the lint stays the spec's
  mechanical shape. Step 6 of `/bb:spec` runs the two scripts side by side when a
  convention resolves. (guess: cheap to reverse)
- **Grammar as a three-slot template, not a regex.** The author of a convention file writes
  vocabularies, never patterns; the checker owns the one shape and never builds a pattern
  from project text. A project whose names do not fit three slots has no convention file,
  and bb behaves as today.
- **Payload types are a closed list**: `id`, `enum`, `number`, `boolean`, `text`. The first
  four widen the payload rule `spec-format.md` states today, which names IDs and enums only:
  task 3 rewrites that paragraph to name the four, because a count and a flag are not
  content, so the checker's list and the paragraph C006 cites agree. `text` exists so the
  file can name its exceptions instead of hiding them, and every `text` field needs an
  exception row with status, justification and retention.
- **Precision is absolute on names and advisory on fields** (owner's call). A field the
  dictionary does not list is a warning, C005, never a block: the gate shows it, the person
  keeps the last word, and the draft still proposes the dictionary entry as a task so the
  dictionary grows by proposal and not by silence. An exception row carries a `status`,
  `approved` or `under-review` (the literal values the file carries), and both let a `text`
  field through with C008 naming the status; only a `text` field with no row at all blocks (C006). The accepted risk is free
  text growing under an exception nobody approved yet; C008 is what keeps it visible, and
  the legal-lens round is where those exceptions get their verdict.
- **The catalog remembers what landed.** Duplicate detection needs every existing name, not
  only the pre-file ones, and the checker reads names, never code (resolved at the gate: the
  discovery record's hypothesis reads "over the typed event map's additions", the review's
  caller extracts the added names from the diff instead, and the record's writer registers
  the wording on its next round, per spec-state's reversal rule). So the file carries the catalog, the pre-file names marked `legacy`, and the spec's
  instrumentation task shape gains the append: landing an event is landing its name in
  `EVENTS.md`. The checker cannot see another branch's plan; two branches planning the
  same new name collide when the second appends, in that pull request's review.
- **Rung order in the instrumentation front**: the spec's plan, then the convention file,
  then the convention inferred from code. The file outranks inference because it is the
  team's statement; the plan outranks the file because it is this branch's contract. The
  caller runs the checker once, before the fan-out, and the finder reads its output from
  the scope block instead of re-deriving it.
- **A new prefix or a new exception is a task, never a silent acceptance.** The spec draft
  writes it as a task editing the convention file (the agent as curator, per the discovery
  record's owner stance), and the events table row waits on the prefix; a new dictionary
  field gets its task too, and its row stands under the warning.
- **Proof by running, not by fixtures.** The repository keeps no test files today; the
  checker is verified by running it over a fixture pair in the scratchpad during the build
  and over the Inspira draft. (guess: revisit if the checker grows)
- **The Inspira draft is delivered, not committed here.** Seeded from the registry sheet and
  the typed map, run dry, and handed to the user as a file for the `inspira-legal/app`
  round; this repository carries no Inspira event names.

## Behavior

1. A project carries `EVENTS.md` at its root; the checker resolves it from wherever it
   runs, or reports C009 in one line and exits 0.
2. `/bb:spec` drafts a spec in a project with a convention: the `## Metric` events table
   arrives proposed, names on the grammar with registered prefixes, payload fields from the
   dictionary, the granularity guidance followed.
3. A behavior's feature has no registered prefix: the draft adds a task that registers it in
   the convention file, and the event row cites that task instead of carrying an invented
   prefix. A payload field the dictionary lacks gets its task the same way, and the row
   stands.
4. Step 6 runs the lint and the checker over the spec; the checker prints
   `path:line CODE message` per finding, or the one clean line.
5. The gate lists each E-code as an open item; the user fixes the row or writes the
   exception as a task; a W-code is shown and does not block.
6. `/bb:review` runs on a diff that adds interactions or emits: the probe resolves the
   convention file as its middle rung; the caller runs the checker over the emitted names
   and hands the output to the finder; the finder cites the file's rows for naming and
   payload, and reports a disagreement between file and code as a finding.
7. The checker is given a list of emitted names: the same grammar, registry and duplicate
   checks run, `legacy` names exempt, a name repeated in the list collides on C007.
8. A project without `EVENTS.md`: every skill behaves as before this spec, and the spec's
   step 6 says in one line how to create one.
9. A spec's instrumentation task lands: its event names are appended to the catalog in the
   same change, and the next spec's duplicate check sees them.

| WHEN                                                                              | THEN                                                                              |
| --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| the convention file is missing                                                    | C009 once, exit 0, nothing else changes                                           |
| the convention file is missing and the spec plans zero events                     | C009: the source resolves before the plan is read                                 |
| the checker runs outside a git repository                                         | C009 naming the missing root, exit 0                                              |
| a part is missing, or a table has no header                                       | C001 naming the part, nothing else checked                                        |
| the same field appears twice in the dictionary, or a prefix twice in the registry | C001, the part is malformed                                                       |
| the spec path or the names file cannot be read                                    | C010 naming the path, exit 1                                                      |
| the spec's `## Metric` reads `Events: none`                                       | nothing to check, the clean line                                                  |
| the spec's `## Metric` is one `skipped:` line                                     | nothing to check, the clean line                                                  |
| the events table has a header and no rows                                         | nothing to check, the clean line                                                  |
| the events table has no `event` column                                            | C009 naming the header, exit 0                                                    |
| a row's event cell is empty                                                       | C002, the message names the empty cell                                            |
| a name starts with no registered prefix                                           | C002, the remedy names the registry task                                          |
| a name uses `erro`, `click`, `impression` as its type                             | C003 with the closed list                                                         |
| an element carries uppercase, hyphens or accents                                  | C004                                                                              |
| a payload cell is empty or `—`                                                    | no field checks, the row passes                                                   |
| a payload cell mixes backticked fields and prose                                  | only the backticked tokens are checked                                            |
| a payload field is not in the dictionary                                          | C005 as a warning: the gate shows it, the draft proposes the dictionary entry     |
| a payload field is `text` with no exception row                                   | C006 citing the payload rule paragraph in spec-format.md                          |
| a payload field is `text` with an approved exception row                          | passes, C008 names the exception and its status                                   |
| a payload field is `text` with an `under-review` exception                        | passes, C008 says `under-review`: the legal-lens round decides the field          |
| a new name equals a catalog name, `legacy` or not                                 | C007                                                                              |
| two rows of the same spec plan the same name                                      | C007 on the second row                                                            |
| a names list repeats a name                                                       | C007 on the second occurrence                                                     |
| a catalog name marked `legacy` is off the grammar                                 | exempt: no C002 to C004                                                           |
| a catalog name not marked `legacy` is off the grammar                             | C003 or C004 on the catalog row: the file itself is held to its grammar           |
| the convention file changed after the spec was written                            | step 6 reruns on every pass, so the gate reads the current file                   |
| the checker runs from a subfolder                                                 | the file resolves at the repository root, never a second root                     |
| the review runs on an external PR in another repository                           | that repository's `EVENTS.md` if it has one, else inference as today              |
| a row cell carries characters that could form a pattern                           | cells are compared as words; the checker never builds a pattern from project text |
| the registry lists two prefixes where one extends the other                       | the longest match wins (`ai_chat` over `ai`)                                      |
| two branches plan the same new name                                               | both pass locally; the second to append to the catalog collides in its PR review  |
| the checker hits content it did not expect                                        | a coded line, never a traceback                                                   |

## Metric

- Metric: the share of specs carrying an events table that pass the checker at their first
  gate, read from the gate's own output in the sessions that follow the landing
- Baseline: skipped: not-instrumented
- Target: 100% of the first five specs with an events table after the landing, within one
  quarter (the operator's target, stated as such); and, inside this build, the dry run over
  the Inspira draft reports the known deviation set and nothing else: 40 names under the
  registered prefix `tabular_review` whose type slot spells `click` or `impression` in full
  (C003), 3 names whose type slot is `erro` (C003), and the free-text fields on C008 as
  `under-review` exceptions
- okr: none connected
- Events: none. This work changes skill files and scripts; nothing here is a product
  interaction that emits an event.

## Tasks

- [x] **1. The format reference**: `plugins/bb/references/events-convention.md`, the five
      parts, their table shapes, the template, the granularity guidance, the catalog's
      `legacy` mark and append duty, and who reads each part, named in `.claude/CLAUDE.md`'s
      structure tree and the README → behaviors 1, 2, 9 · dep: — · verify: reading; the
      sample file's parse is task 2's verify
- [x] **2. The checker**: `plugins/bb/scripts/check_events.py`, root resolution, parsing,
      the ten codes, the two input modes, the clean line, named in `.claude/CLAUDE.md`'s
      shared-scripts list → behaviors 1, 4, 7, 8 · dep: 1 ·
      verify: the reference's sample file parses without C001; run over a fixture pair (one
      clean file plus one spec, one file seeded with each defect) every code fires exactly
      where the fixture places it, and a clean run prints the one line
- [x] **3. Spec reads the file**: `draft-first.md` proposes the table from it and writes
      the prefix and dictionary tasks, `spec-format.md` names the file beside the payload
      rule, widens that rule's paragraph to the four types and adds the catalog append to
      the instrumentation task shape, `SKILL.md` step 6 runs the checker and says how to
      create the file when none resolves, step 7 treats E-codes as open items → behaviors
      2, 3, 4, 5, 8, 9 · dep: 2 · verify: reading, and `lint_spec.py` clean on this spec
- [x] **4. Review cites the file**: `fronts.md` probe resolves the middle rung and the
      caller runs the checker before the fan-out, `front-instrumentation.md` carries three
      rungs and the citation, the fan-out scope block passes the checker output and the
      resolved path → behaviors 6, 7 · dep: 2 · verify: reading
- [x] **5. The Inspira draft, run dry**: the convention file seeded from the registry
      sheet and the typed map, the checker run over the 190 names and the dictionary, the
      file and the report handed to the user → behaviors 1, 7 · dep: 2 · verify: the report
      lists the known deviation set (task-level target in `## Metric`)

## Out of scope

- writing the Inspira manual into `inspira-legal/app`: its own round, after the format
  exists (the draft of task 5 is its seed)
- renaming legacy events; the catalog's `legacy` mark exempts them instead
- deciding the fate of the free-text feedback fields (`response`, `question`, `content`)
  and of `search_term`: `/bb:legal-lens` carries it; the file records them as exceptions
  under review
- moving the registry off the Google Sheet into the repository
- a checker that reads the typed event map in code directly; the review's finder reads
  code, the checker reads names it is handed
- enforcing an exception's retention: the file records it, nothing checks the data
- a CI step in a project's own workflow that runs the checker: `/bb:review-setup`'s
  business, a later round; in this repository nothing would resolve
- an analytics page in the manifesto for greenfield products (carried from
  `metricas-no-ciclo`)

## Open

Nothing.
