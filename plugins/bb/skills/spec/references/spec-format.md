# The spec format: a document made to be read

A spec is a **document**, not a form. Someone opens it to learn what to build; the
writing has to reward that. Which is why the format fixes only what has a consumer
and leaves the rest to whoever is describing the problem.

## Two halves

```
---  frontmatter  ---                    the on-disk contract (references/spec-state.md)

# title
opening, 1–3 paragraphs                  ┐
                                         │  top half: free
## <whatever section the problem needs>  │  as many as the problem needs, named for
## <another>                             ┘  the problem. prose, diagram, short table, code.

## Decisions                             ┐
## Behavior                              │
## Attention points                      │  fixed, in this order
## Tasks                                 │  each one has a reader
## Out of scope                          │
## Open                                  ┘
```

**The top half is yours.** Open with what the thing is, why now, and what success
looks like, then describe the problem in whatever sections it calls for. A UI change
might want "The three screens"; a CLI might want "What the tool already does"; an
architectural change might want "The boundary between agent and caller". Prose is the
default; diagrams, short tables and code fragments earn their place when they carry the
idea better than a sentence would.

**A spec is a plan, not a design document.** It says what gets built, the business rules,
the expected behavior and the order the work runs in. The technical details are the
builder's: the task agent settles them at build time, with the code open. A technical
choice appears in the spec only when the user made it, like a stack the company settled
or a contract another team depends on. A technical risk the author sees goes in
`## Attention points`, named and with no solution attached.

**The fixed sections are fixed because each one has a reader.** `/bb:implement` consumes
`## Tasks` and builds against `## Behavior`; the task agent reads `## Attention points` as
the risks it has to handle; the `contract` front of `/bb:review` walks `## Behavior` row by
row; the spec gate itself blocks on `## Open`. A section nobody reads is a section that
drifts, which is why the set is small and every member earns its slot.

- `## Decisions`: the business rules and the calls closed with the user, one bullet each,
  in the words of the product: what the thing must do and what it must never do. The
  build side never has to re-derive them from prose.
- `## Behavior`: the happy path step by step, then a `WHEN … THEN …` table of the edges
  that change the outcome for the user, where every row reads as a test. The acceptance
  contract.
- `## Attention points`: the technical risks the author saw (below). `Nothing.` when
  there are none.
- `## Tasks`: vertical tasks grouped in phases (below).
- `## Out of scope`: the hard line, including ideas parked for later (mark them
  _revisit_). Plain bullets, never checkboxes.
- `## Open`: genuinely unresolved load-bearing decisions. `Nothing.` when there are
  none.

`## Behavior` and `## Tasks` are what Large work needs; a Medium spec can carry those
inline and skip them, which is why the lint only warns on their absence. The same goes for
`## Attention points`: the lint warns when it is missing, and `Nothing.` silences it.

## The rule that does the most work

**The prose describes the thing; it doesn't recount how you got there.** What it is,
how it behaves, what was decided. That's the spec. "I had recorded X, then reading the
source refined it", "decision made by the user in the thread", a commit sha as evidence:
that's the history of the conversation, and it belongs in the commit message that
carries the change. A spec rewritten after landing gains the new decision; the reason it
changed goes in the commit body.

Say each thing once. A fact that appears in the opening, again in a decision, and again
in a behavior row is one fact and two copies to keep in sync.

**Name things the way the repo names them.** The spec is the document the builder rereads,
so its words become the words of the build. `<plugin-root>/references/doc-style.md`
carries the principle.

## Tables carry short cells

A table cell holds a value, not a paragraph. Past ~100 characters it stops being a table:
`fmt:check` runs `oxfmt --check .` across the repo, and oxfmt pads every cell in a column
to the width of the widest one, so a single 300-character cell drags the whole table off
screen. Long content is prose or a bullet.

Escape any literal `|` inside a cell as `\|`; an unescaped one silently splits the row
into the wrong number of columns.

## Attention points name the risk, not the fix

Each attention point is one bullet: the technical risk, and where it lives in the code
(the file, the function, the tool whose limit it runs into).

```
- Every task ticks its box in the same `spec.md`, so ticking inside the task commit
  conflicts across a phase.
```

The solution is the builder's. The task agent reads the list as risks to handle, never as
instructions, and it decides how to handle each one with the code open. A bullet that
carries a fix has turned back into a technical decision the spec no longer makes: cut the
fix and keep the risk.

The author writes what they saw, and `bb-spec-reviewer`, when the user asks for it at the
gate, adds a risk the spec does not name in the same shape: the risk and where it lives,
with no solution.

## Tasks, and the phases they run in

A task is a thin end-to-end cut. Its line carries three fields: the title, what it
delivers, and how it gets checked.

```
- [ ] **3. The reviewer's contract**: `agents/bb-spec-reviewer.md` reads for four
      things; its `tools:` stays read only. · verify: reading
```

`verify:` is `reading` (the task agent inspects what it produced), a command it runs, or
`CI` when only the pipeline can prove it.

### The `###` headings inside `## Tasks` are the build's phases

The author orders the work by what depends on what, and writes that order as phases:

```
## Tasks

### Foundation

- [ ] **1. The normalizer**: …

### The three surfaces

- [ ] **2. The CLI reads it**: …
- [ ] **3. The API reads it**: …
- [ ] **4. The UI reads it**: …

### Close

- [ ] **5. The docs catch up**: …
```

- **The phases run in document order.** A phase starts after every task of the phase
  before it landed.
- **The tasks inside one phase run in parallel.** Two tasks share a phase only when
  neither needs what the other produces. Tasks that change the same parts of the code go
  in different phases, even when neither needs the other: two tasks in parallel that edit
  the same lines stop the run.
- **A foundation is a phase of its own.** What everything else builds on runs alone, with
  one task, so the tasks after it all start from it.
- **A closing task that needs all the others is the last phase.**

The heading is the phase title, and `/bb:implement` passes it to the build, where the
progress card shows it as a group header. Someone watching a run over this spec reads the
work this spec describes, so name a heading after what that group of tasks does, the way
you would name a section: `Foundation`, `Migrate the callers`, `Drop the old path`.

Phase order is the only dependency the format carries. A spec written before this change
may still carry `dep:` and `→ behaviors` on its task lines: the build reads the line and
ignores both fields.

**A spec with no `###` heading runs one task at a time**, in document order, the way a
spec written before this change expects. A task that sits above the first `###` runs the
same way: alone, before the first phase. Nothing else reads the headings:
`lint_spec.py` matches `^##\s+` and `scan_specs.py` counts tasks by their checkbox, so
both see a flat list.

## Dead names

`## design` is not a spec section. Inside bb the word already means screen design:
`/bb:brisar` writes the visual direction (hierarchy, components and states) into
`.bb/<slug>/design.md`, next to this spec.
Architecture, when a spec needs it, lives in the top half under the name it actually has
in that problem.

`## still open` is spelled `## Open`.

`## Problem`, `## Hypothesis`, `## Fit` and `## Cuts` are **not** sections of a spec.
`/bb:discover` writes them into `.bb/<slug>/discovery.md`, and this spec reads them
there by path (plugin-level `references/spec-state.md`); the lint fires `E003` on all
four. `## Cuts` is scope dropped while framing the problem, with the appetite behind
it, and it stays in that record; `## Out of scope` is what this spec doesn't do, and it
belongs here.

## The lint

`scripts/lint_spec.py` checks the mechanical half and stays out of judgment:

```bash
python3 plugins/bb/skills/spec/scripts/lint_spec.py .bb/<slug>/spec.md
```

| code | level   | what it catches                                                    |
| ---- | ------- | ------------------------------------------------------------------ |
| E001 | error   | frontmatter missing, incomplete, or with an invalid status or date |
| E002 | error   | no `## Decisions` or no `## Open`                                  |
| E003 | error   | a dead section name (`## design`, `## still open`)                 |
| E004 | error   | a table cell above 100 characters                                  |
| E005 | error   | a row whose cell count differs from the header                     |
| W001 | warning | no `## Behavior`                                                   |
| W002 | warning | no `## Tasks`                                                      |
| W003 | warning | no `## Attention points`                                           |
| W004 | warning | no `## Out of scope`                                               |
| W005 | warning | above 800 lines, or above 100 rows in the `## Behavior` tables     |

Whether the document repeats itself, recounts the conversation, or carries a fix inside an
attention point is not a lint check. That is judgment, and it belongs to
`bb-spec-reviewer`, which runs only when the user picks `Review the spec` at the gate. The
ceiling `W005` sets is not about how the prose reads: it measures the review surface, the
text the reviewer's one pass has to cover.
Its advice is to split the spec along its `###` phases into sibling specs, never to trim
prose to fit. It stays a warning, so the exit code is 0 and whether to split is the
user's call at the gate.

Every code reads the document's own bytes, and what the reviewer returned is not among
them: its verdict reaches the user at the gate, and the plugin-level
`references/spec-state.md` says why it stays out of the frontmatter.
