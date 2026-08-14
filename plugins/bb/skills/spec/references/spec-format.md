# The spec format — a document made to be read

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

## Decisões                              ┐
## Comportamento                         │  the spine: fixed, in this order
## Tarefas                               │  each one has a reader
## Fora de escopo                        │
## Em aberto                             ┘
```

**The top half is yours.** Open with what the thing is, why now, and what success
looks like — then describe the problem in whatever sections it calls for. A UI change
might want "As três telas"; a CLI might want "O que a ferramenta já faz"; an
architectural change might want "O seam entre agente e caller". Prose is the default;
diagrams, short tables and code fragments earn their place when they carry the idea
better than a sentence would.

**The spine is fixed because it has readers.** `/bb:implement` consumes `## Tarefas`
and builds against `## Comportamento`; the `contract` front of `/bb:review` walks
`## Comportamento` row by row; the spec gate itself blocks on `## Em aberto`. A section
nobody reads is a section that drifts, which is why the set is small and every member
earns its slot.

- `## Decisões` — the closed calls, one bullet each, so the build side never has to
  re-derive them from prose.
- `## Comportamento` — the happy path step by step, then a `WHEN … THEN …` table where
  every row reads as a test. The acceptance contract.
- `## Tarefas` — vertical tasks (below).
- `## Fora de escopo` — the hard line, including ideas parked for later (mark them
  _revisit_). Plain bullets, never checkboxes.
- `## Em aberto` — genuinely unresolved load-bearing decisions. `Nada.` when there are
  none.

`## Comportamento` and `## Tarefas` are what Large work needs; a Medium spec can carry
those inline and skip them, which is why the lint only warns on their absence.

A spec written before the rename keeps its English spine and still builds: both names
resolve everywhere, and the lint answers with `W003` naming the Portuguese one to write.

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

## Tasks carry their own dependencies

Each task is a thin end-to-end cut, and it states what it delivers, what has to land
first, and how it gets checked:

```
- [ ] **3. Independent reviewer** — dedicated step in `SKILL.md`, verdict at the gate
      → behaviors 4, 6 · depende: 2 · verifica: leitura
```

`depende:` is `—` when nothing blocks it, and a task line still written with `dep:`
reads the same. Those three fields are the DAG: what can run in parallel, what has to
wait, and what proves each one landed — so the build side reads a graph instead of
re-interpreting prose.

Every task cites at least one behavior and every behavior is cited by at least one
task. That two-way trace is what the gate renders as the coverage table; an unlinked
row on either side is an omission made visible.

## Dead names

`## design` is not a spec section. Inside bb the word already means screen design —
`/bb:brisar` writes the visual direction — hierarchy, components and states — into
`.bb/<slug>/design.md`, next to this spec.
Architecture, when a spec needs it, lives in the top half under the name it actually has
in that problem.

`## still open` is spelled `## Em aberto`.

Sections seeded upstream by `/bb:discover` (`## Problema`, `## Hipótese`, `## Encaixe`,
`## Cortes`) live in the top half and stay as they are. `## Cortes` is scope dropped
while framing the problem, with the appetite behind it; `## Fora de escopo` is what this
spec doesn't do. Both can appear in the same file.

## The lint

`scripts/lint_spec.py` checks the mechanical half and stays out of judgment:

```bash
python3 plugins/bb/skills/spec/scripts/lint_spec.py .bb/<slug>/spec.md
```

| code | level | what it catches                                               |
| ---- | ----- | ------------------------------------------------------------- |
| E001 | erro  | frontmatter ausente, incompleto ou com status/data inválidos  |
| E002 | erro  | `## Decisões` ou `## Em aberto` ausente                       |
| E003 | erro  | seção de nome morto (`## design`, `## still open`)            |
| E004 | erro  | célula de tabela acima de 100 caracteres                      |
| E005 | erro  | row com número de células diferente do cabeçalho              |
| W001 | aviso | sem `## Comportamento`                                        |
| W002 | aviso | sem `## Tarefas`                                              |
| W003 | aviso | seção com o nome em inglês — a mensagem traz o nome português |

Whether the document is too long, repeats itself, or drifts into archaeology is not a
lint check — it's what the independent reviewer is asked to find. A line ceiling on a
document meant to be read just rebuilds the form.
