# The spec format — a document made to be read

A spec is a **document**, not a form. Someone opens it to learn what to build; the
writing has to reward that. Which is why the format fixes only what has a consumer
and leaves the rest to whoever is describing the problem.

## Two halves

```
---  frontmatter  ---                    the on-disk contract (references/task-state.md)

# title
opening, 1–3 paragraphs                  ┐
                                         │  top half: free
## <whatever section the problem needs>  │  as many as the problem needs, named for
## <another>                             ┘  the problem. prose, diagram, short table, code.

## decisions                             ┐
## behavior                              │  the spine: fixed, in this order
## tasks                                 │  each one has a reader
## out of scope                          │
## open                                  ┘
```

**The top half is yours.** Open with what the thing is, why now, and what success
looks like — then describe the problem in whatever sections it calls for. A UI change
might want "As três telas"; a CLI might want "O que a ferramenta já faz"; an
architectural change might want "O seam entre agente e caller". Prose is the default;
diagrams, short tables and code fragments earn their place when they carry the idea
better than a sentence would.

**The spine is fixed because it has readers.** `/bb:implement` consumes `## tasks` and
builds against `## behavior`; the `contract` front of `/bb:review` walks `## behavior`
row by row; the spec gate itself blocks on `## open`. A section nobody reads is a
section that drifts, which is why the set is small and every member earns its slot.

- `## decisions` — the closed calls, one bullet each, so the build side never has to
  re-derive them from prose.
- `## behavior` — the happy path step by step, then a `WHEN … THEN …` table where every
  row reads as a test. The acceptance contract.
- `## tasks` — vertical slices (below).
- `## out of scope` — the hard line, including ideas parked for later (mark them
  _revisit_). Plain bullets, never checkboxes.
- `## open` — genuinely unresolved load-bearing decisions. `Nada.` when there are none.

`## behavior` and `## tasks` are what Large work needs; a Medium spec can carry those
inline and skip them, which is why the lint only warns on their absence.

## The rule that does the most work

**The prose describes the thing; it doesn't recount how you got there.** What it is,
how it behaves, what was decided — that's the spec. "I had recorded X, then reading the
source refined it", "decision made by the user in the thread", a commit sha as evidence
— that's the history of the conversation, and it belongs in the commit message that
carries the change. A spec rewritten after landing gains the new decision; the reason it
changed goes in the commit body.

Say each thing once. A fact that appears in the opening, again in a decision, and again
in a behavior row is one fact and two copies to keep in sync.

**Name things the way the repo names them.** The spec is the document the builder rereads,
so its words become the words of the build — the plugin-level `references/vocabulario.md`
carries the principle, the EN→PT table and the capitalization rule for the Portuguese it
gets written in.

## Tables carry short cells

A table cell holds a value, not a paragraph. Past ~100 characters it stops being a table:
`fmt:check` runs `oxfmt --check .` across the repo, and oxfmt pads every cell in a column
to the width of the widest one — so a single 300-character cell drags the whole table off
screen. Long content is prose or a bullet.

Escape any literal `|` inside a cell as `\|`; an unescaped one silently splits the row
into the wrong number of columns.

## Slices carry their own dependencies

Each slice is a thin end-to-end cut, and it states what it delivers, what has to land
first, and how it gets checked:

```
- [ ] **3. Independent reviewer** — dedicated step in `SKILL.md`, verdict at the gate
      → behaviors 4, 6 · dep: 2 · verifica: leitura
```

`dep:` is `—` when nothing blocks it. Those three fields are the DAG: what can run in
parallel, what has to wait, and what proves each one landed — so the build side reads a
graph instead of re-interpreting prose.

Every slice cites at least one behavior and every behavior is cited by at least one
slice. That two-way trace is what the gate renders as the coverage table; an unlinked
row on either side is an omission made visible.

## Dead names

`## design` is not a spec section. Inside bb the word already means screen design —
`/bb:brisar` writes the visual direction — hierarchy, components and states — into
`.bb/tasks/<slug>/design.md`, next to this brief.
Architecture, when a spec needs it, lives in the top half under the name it actually has
in that problem.

`## still open` is spelled `## open`.

Sections seeded upstream by `/bb:discover` (`## problem`, `## hypothesis`, `## fit`,
`## cuts`) live in the top half and stay as they are. `## cuts` is scope dropped while
framing the problem, with the appetite behind it; `## out of scope` is what this spec
doesn't do. Both can appear in the same file.

## The lint

`scripts/lint_spec.py` checks the mechanical half and stays out of judgment:

```bash
python3 plugins/bb/skills/spec/scripts/lint_spec.py .bb/tasks/<slug>/spec.md
```

| code | level | what it catches                                              |
| ---- | ----- | ------------------------------------------------------------ |
| E001 | erro  | frontmatter ausente, incompleto ou com status/data inválidos |
| E002 | erro  | `## decisions` ou `## open` ausente                          |
| E003 | erro  | seção de nome morto (`## design`, `## still open`)           |
| E004 | erro  | célula de tabela acima de 100 caracteres                     |
| E005 | erro  | row com número de células diferente do cabeçalho             |
| W001 | aviso | sem `## behavior`                                            |
| W002 | aviso | sem `## tasks`                                               |

Whether the document is too long, repeats itself, or drifts into archaeology is not a
lint check — it's what the independent reviewer is asked to find. A line ceiling on a
document meant to be read just rebuilds the form.
