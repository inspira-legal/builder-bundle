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
## Behavior                              │  fixed, in this order
## Metric                                │  each one has a reader
## Tasks                                 │
## Out of scope                          │
## Open                                  ┘
```

**The top half is yours.** Open with what the thing is, why now, and what success
looks like, then describe the problem in whatever sections it calls for. A UI change
might want "The three screens"; a CLI might want "What the tool already does"; an
architectural change might want "The boundary between agent and caller". Prose is the
default; diagrams, short tables and code fragments earn their place when they carry the
idea better than a sentence would.

**The fixed sections are fixed because each one has a reader.** `/bb:implement` consumes
`## Tasks` and builds against `## Behavior`; the `contract` front of `/bb:review` walks
`## Behavior` row by row; the exit gate renders `## Metric` beside the coverage table,
the export reads its trio by path, and review's instrumentation front resolves its
events table first; the spec gate itself blocks on `## Open`. A section nobody reads is
a section that drifts, which is why the set is small and every member earns its slot.

- `## Decisions`: the closed calls, one bullet each, so the build side never has to
  re-derive them from prose.
- `## Behavior`: the happy path step by step, then a `WHEN … THEN …` table where every
  row reads as a test. The acceptance contract.
- `## Metric`: the measure the landing is judged by, or one explicit `skipped: <reason>`
  line. Its own section below.
- `## Tasks`: vertical tasks (below).
- `## Out of scope`: the hard line, including ideas parked for later (mark them
  _revisit_). Plain bullets, never checkboxes.
- `## Open`: genuinely unresolved load-bearing decisions. `Nothing.` when there are
  none.

`## Behavior` and `## Tasks` are what Large work needs; a Medium spec can carry those
inline and skip them, which is why the lint only warns on their absence. `## Metric`
rides every spec at every size; its checks warn instead of erroring so a spec that
predates it stays valid.

## The Metric section

`## Metric` sits between `## Behavior` and `## Tasks` because the trace runs through it:
an event row cites the behavior rows above it, and an instrumentation task cites the
event rows below it. Every spec carries the section, whatever its size, in one of two
forms, and an honest skip always beats an invented number.

**The metric block**: the one metric, its baseline, its target, and a timeframe.

```
- Metric: <the one measure, and how it is read>
- Baseline: <the current reading> (<provenance>)
- Target: <where it should land>, within <timeframe> (<provenance>)
- okr: <the connected OKR>
- Events: <the table below, or `none` and why>
```

The `Baseline:` and `Target:` bullets each carry their value's provenance as a
parenthesized note on the same bullet: a query, a log, or a named person's estimate
marked as such. The note is the shape the lint checks; whether it names a real source is
the gate's judgment. A value nothing measures yet is its own honest skip, `skipped:
<reason>` in place of the value (`- Baseline: skipped: not-instrumented`, the form
discover blesses): no provenance note, and the target and the events table stay while
the skip flags the instrumentation as the first work. Internal work names an
operational measure (error rate, runtime, adoption) where no product metric applies.
The `okr:` line names the connected OKR when one exists, and is omitted when none does.

**The skip**: one line, `skipped: <reason>`, when no honest measure exists. It replaces
the whole section body.

### The events table

When the work has user-triggered behavior, the block also carries the events table, one
row per event:

| event                | behaviors | payload                   | channel  |
| -------------------- | --------- | ------------------------- | -------- |
| `vault_doc_uploaded` | 2, 3      | `doc_id`, `source` (enum) | internal |

The event name follows the project's own convention. `behaviors` cites the numbered
happy-path rows the event instruments. `channel` names the sink, and the column exists
only when the project has more than one. Payload fields are IDs and enums, never free
text and never document content: that rule is what keeps mandatory instrumentation
compatible with a legaltech's data duties, and this paragraph is its single home; the
gate and the review front cite it here instead of restating it.

Instrumentation enters `## Tasks` as ordinary tasks with their own `verify:`, each
citing the event rows it wires (`→ events <name>, <name>` in place of the behavior
citation). An event row's own behavior citations are what the coverage table counts, so
an instrumentation task covers its behaviors through the event row it cites; the build
side resolves that citation into behavior numbers when it loads the spec (implement's
step 1), and the machinery downstream consumes numbers the way it always did.

A Medium spec carries its behaviors inline, so an event row there has no numbered row to
cite; its `behaviors` cell names the inline behavior in a short phrase instead. The
lint leaves prose cells alone and the gate judges the trace. A re-size to Large numbers
the behavior rows and rewrites those cells as numbers, part of the re-size itself.

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
so its words become the words of the build. `${CLAUDE_PLUGIN_ROOT}/references/doc-style.md`
carries the principle.

## Tables carry short cells

A table cell holds a value, not a paragraph. Past ~100 characters it stops being a table:
`fmt:check` runs `oxfmt --check .` across the repo, and oxfmt pads every cell in a column
to the width of the widest one, so a single 300-character cell drags the whole table off
screen. Long content is prose or a bullet.

Escape any literal `|` inside a cell as `\|`; an unescaped one silently splits the row
into the wrong number of columns.

## Tasks carry their own dependencies

Each task is a thin end-to-end cut, and it states what it delivers, what has to land
first, and how it gets checked:

```
- [ ] **3. Independent reviewer**: dedicated step in `SKILL.md`, verdict at the gate
      → behaviors 4, 6 · dep: 2 · verify: reading
```

`dep:` is `—` when nothing blocks it. Those three fields are the DAG: what can run in
parallel, what has to wait, and what proves each one landed, so the build side reads a
graph instead of re-interpreting prose.

Every task cites at least one behavior and every behavior is cited by at least one
task. That two-way trace is what the gate renders as the coverage table; an unlinked
row on either side is an omission made visible. An instrumentation task cites event
rows instead, and counts as citing the behaviors those rows cite (the Metric section
above).

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

| code | level   | what it catches                                                       |
| ---- | ------- | --------------------------------------------------------------------- |
| E001 | error   | frontmatter missing, incomplete, or with an invalid status or date    |
| E002 | error   | no `## Decisions` or no `## Open`                                     |
| E003 | error   | a dead section name (`## design`, `## still open`)                    |
| E004 | error   | a table cell above 100 characters                                     |
| E005 | error   | a row whose cell count differs from the header                        |
| W001 | warning | no `## Behavior`                                                      |
| W002 | warning | no `## Tasks`                                                         |
| W004 | warning | no `## Out of scope`                                                  |
| W005 | warning | no `## Metric`                                                        |
| W006 | warning | a `Baseline:`/`Target:` bullet missing, or a value without provenance |
| W007 | warning | an event row citing a numbered behavior row that does not exist       |

Whether the document is too long, repeats itself, or recounts the conversation is not a
lint check; it's what the independent reviewer is asked to find. A line ceiling on a
document meant to be read just rebuilds the form.
