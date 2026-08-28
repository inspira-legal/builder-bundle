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

**The fixed sections are fixed because each one has a reader.** `/bb:implement` consumes
`## Tasks` and builds against `## Behavior`; the `contract` front of `/bb:review` walks
`## Behavior` row by row; the spec gate itself blocks on `## Open`. A section nobody
reads is a section that drifts, which is why the set is small and every member earns its
slot.

- `## Decisions`: the closed calls, one bullet each, so the build side never has to
  re-derive them from prose.
- `## Behavior`: the happy path step by step, then a `WHEN … THEN …` table where every
  row reads as a test. The acceptance contract.
- `## Tasks`: vertical tasks (below).
- `## Out of scope`: the hard line, including ideas parked for later (mark them
  _revisit_). Plain bullets, never checkboxes.
- `## Open`: genuinely unresolved load-bearing decisions. `Nothing.` when there are
  none.

`## Behavior` and `## Tasks` are what Large work needs; a Medium spec can carry those
inline and skip them, which is why the lint only warns on their absence.

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
row on either side is an omission made visible.

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
| W004 | warning | no `## Out of scope`                                               |

Whether the document is too long, repeats itself, or recounts the conversation is not a
lint check; it's what the independent reviewer is asked to find. A line ceiling on a
document meant to be read just rebuilds the form.
