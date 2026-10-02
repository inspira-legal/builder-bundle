# Draft-first: propose, then react to alignment

The move: don't ask the user to fill a blank. Read the one-liner, glance at the
codebase, and **write a draft spec with your best guesses already made.** Hand them
something concrete to react to, people correct a proposal far faster, and more
accurately, than they answer open questions cold.

## What the draft must cover

The spec's form belongs to `spec-format.md`: the free top half, then the fixed sections.
The draft's job is to arrive with those already filled from your best read of the goal
and the codebase, so the user reacts to a proposal instead of completing a blank. Mark
anything you're guessing so it reads as a guess rather than a fact.

The draft is a plan: what gets built, the business rules, the behavior you expect and the
order the work runs in. Two things a first draft earns the most from. First, the
**business rules**: what the thing must do and must never do, in the words of the
product, which is what the build cannot re-derive on its own. Second, the **smallest
version still worth shipping**, which is what turns a scope edge into a line you can
actually hold.

Reading the codebase is still where the draft starts, because it shows you what the work
touches. What you see there goes into the spec as a risk, never as a design: a technical
risk becomes a bullet in `## Attention points`, the risk and where it lives, and the
builder decides how to handle it with the code open.

`## Metric` is part of the arrival, not a blank left for later. Seed the baseline and
the target from the discovery record when it carries them, carrying each value's own
source into the seeded note with the record named beside it
(`(XRAY query 2026-08, via discovery.md)`): the materialized value keeps a source the
gate can judge, not just a pointer to where it came from, and after the gate hardens
it the spec's value wins, per the reversal rule in the plugin-level
`references/spec-state.md`. Guess what
remains with each value's provenance on its own bullet (an estimate marked as such
reads as a guess the user corrects), keep a value's own `skipped: <reason>` when only
that value is unmeasured, or write the one-line `skipped: <reason>` when no honest
measure exists at all. An honest skip beats an invented number; the shape and the
events table live in `spec-format.md`.

## Propose the events table

A project with `EVENTS.md` at its root
(`<plugin-root>/references/events-convention.md`) gets its `## Metric` events
table proposed the same draft-first way as the rest of the spec: read the file, then write the table instead of leaving it blank.

- **Name**: `{prefix}_{type}_{element}`, the prefix from `## Prefix registry`, the type
  from `## Grammar`, the element a short lowercase phrase for what happened.
- **Payload**: the fields `## Dictionary` already lists for the behavior's feature,
  backticked in the cell.
- **Granularity**: the file's own guidance, 8–12 events per feature, never one per
  form field.

Two gaps the file can't close on its own, and the draft never guesses past them:

- **No registered prefix for the feature**: don't invent one. Add a task that
  registers the prefix in `## Prefix registry` of `EVENTS.md`, and write the row's
  name cell as plain prose citing that task (no backticks) instead of a name, for
  example `waits on task 4, registers the prefix`. The checker reads a cell that does
  not open with a backtick and holds a space as prose, so it says the row names no
  event yet and flags it (`C002`), one line per row and never a collision between two
  rows waiting on the same task; that is the open item the gate holds until the task
  lands and the row carries its real name.
- **No dictionary entry for a payload field**: add a task that adds the field to
  `## Dictionary` of `EVENTS.md`, the same way, but write the row complete: name and
  payload field both, backticked as usual. The checker warns instead of blocking
  (`C005`); the gate shows it, and the person keeps the last word while the dictionary
  task is pending. A field the dictionary does not carry has no type yet, so the free
  text check cannot run on it and that one warning is the whole signal: when the field
  is free text, the task that adds the dictionary row carries its `## Exceptions` row
  too, with status, justification and retention, and the task says so in its own line.

Without `EVENTS.md`, the events table is proposed the way it always was, from the
behavior rows alone; nothing here changes.

## Propose each event's level

When the company classifies its events, the events table carries a `level` per row
(`spec-format.md`, its events-table paragraph). The values and the rule that picks one live in
the company's `usage` document, found by its tag the way
`<plugin-root>/references/company-definitions.md` states.

- **Read the rule first.** List the `usage` role, read every document it returns, and take the
  level values and the question the rule asks of an event.
- **Propose one value per row**, by that rule, the same draft-first way as the name and the
  payload. The task agent writes what the row says, so the row is the decision.
- **A case the rule does not settle is a gray area**, asked through `AskUserQuestion` like any
  other, with your lean and the line of the rule it turns on.
- **No `usage` document, or the `wave` CLI unavailable**: the table carries no `level` column.
  Say in one line which of the two it was, and go on.

At the gate, a value the rule does not list is an open item, fixed in its row.

## Surfacing the gray areas (the only thing you ask about)

A call earns a question only when it **genuinely could go more than one way**
and the goal or codebase doesn't already settle it. Everything else: decide it,
note it, move on. That filter is what keeps this from becoming an interrogation.

The questions are about **what gets built and how it behaves**: a business rule, a scope
edge, the outcome of an edge case. A technical detail is the builder's and does not reach
the user. The one exception is a technical choice only the user can make, like a stack the
company settled or a contract another team depends on.

Ask them through the **`AskUserQuestion` tool**: concrete options the user picks, not open prose. For each real gray area:

- Present **concrete options**: "card layout" vs "table", not "Option A / B".
- State **your lean and why**, so the user can approve it in one word.
- Make it a clean either/or; offer "your call" when you truly have no preference.
- **Size the ask to the stakes:** cheap-to-reverse → lead with your pick and let
  them veto; expensive-to-undo → lay the options out and let them choose.

## How to drive it

- On the **single highest-stakes question**, ask how the user would decide _before_
  revealing your pick. Anchoring is strongest on the call that matters most,
  so don't pre-frame that one. Everything else stays draft-first.
- One **small batch** of questions at a time via `AskUserQuestion` (up to 4 per
  call), never a wall.
- After each round, **fold the answers into the draft and show only what
  changed**: the diff, not the whole document again.
- **When the gray areas run dry, order the work and open the gate.** Group the tasks in
  `###` phases, write the attention points, run the lint, and show the gate. The review
  is one of the gate's options: the user picks it or builds without it.
- **The gate blocks on open load-bearing decisions.** Never offer a clean "build"
  while one is unresolved. The user must resolve it or defer it explicitly
  ("decide at build time", recorded in the spec). No silent "build anyway".
- **The gate shows `## Metric` and holds it where the lint cannot.** A `Baseline:` or
  `Target:` without provenance is an open item the gate blocks on like any
  load-bearing decision, resolved or explicitly deferred; the lint checks the note's
  shape, and whether it names a real source is your judgment at the gate. A value
  whose own `skipped: <reason>` names the missing measurement is not an open item; it
  is the honest state, and the instrumentation it flags is work for `## Tasks`. The
  `Events:` line is held here too: the block carries the table or its explicit
  `none`, because the review front's plan rung resolves on exactly that line and the
  lint does not check it. On a Medium spec, whose behaviors live inline, judge the
  event trace yourself: each event row against the inline behavior it instruments,
  payload fields against the rule stated in `spec-format.md`. The lint's citation
  check needs numbered behavior rows and stays silent here; on a Large spec it walks
  event rows to behavior rows only, so the reverse direction, every user-triggered
  behavior row having its event, is yours to judge at the gate.
- **A checker line whose path is the project's `EVENTS.md` is an external blocker**, whatever
  its code: there is no row in this spec to fix, so it is resolved in that file and deferred
  until it is. Three shapes arrive that way. `C001` is the file malformed, a part missing or
  written twice or a table without its header. A line prefixed `catalog row:` or
  `dictionary row:` is the file held to its own rules, and the remedy is in the file: a name
  that predates the file carries the literal `legacy` in its `status` cell, which is what
  keeps a name nobody here planned from blocking every spec in the project, and a `text`
  field owes its row in `## Exceptions`. `C010` is an input that could not be read, fixed at
  that path.
- **Reflect back:** "So we're building X, for Y, and NOT doing Z, right?"
- **Alignment is active, not silent.** It's confirmed when the user restates the
  idea in their own words or explicitly approves the written spec, never by the
  mere absence of objections. No reaction usually means they checked out, not that
  they agree; prompt for the explicit nod.
- **The validated spec is the checkpoint.** When the user approves (or sends last
  edits), that `.bb/<slug>/spec.md` is the artifact. The gate then offers to
  build, with what runs after the build ticked in the same call, and an explicit
  build pick is the user affirmatively starting execution, not the spec silently
  rolling into it. Never start building off the back of a re-read; only off that
  explicit pick.
- Keep **deferred decisions visible**: anything handed back to you ("your call")
  gets noted, so it's not silently assumed.
- When a good idea surfaces that's **out of scope**, don't drop it and don't build
  it; park it in the spec's out-of-scope bucket as a plain bullet (never a
  checkbox, which the task selector would mistake for work).
- If a question can't be settled without facts, go check (codebase → docs → web) and
  come back with the options, rather than guessing.
