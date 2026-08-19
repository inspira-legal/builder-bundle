---
status: done
created: 2026-08-05
slug: spec-legivel
---

# spec: a document meant to be read

`/bb:spec` produces briefs nobody reopens. The three specs on disk add up to 485 lines and the
cost shows up at the far end: whoever is going to build prefers rereading the conversation. The
change is to treat the spec as a **document** and not as a form: a free opening and a free body,
written to be read, resting on a fixed set of sections the other skills consume.

Along with it come four things the same change resolves: the independent reviewer becomes a
structural step, the rationale for a change leaves the file and goes to the commit, `## tasks`
starts carrying what a workflow needs, and `shape` leaves the vocabulary.

Success: the builder opens the spec and knows what to build without reopening the conversation.

## What broke in the three specs

None of the defects is "there is too much prose". There are four, and every one has its cause in
the prompt:

**Prose that recounts the conversation.** `ship-lexflow` has a whole section called _"Correção
de leitura própria"_, "I had recorded X, reading the source refines that". `review-agents`
records "Decisão do usuário, com o custo declarado" and cites the sha `9a461e8`. That is
history, and history has a place of its own: the commit message.

**A table used as prose.** `review-agents`'s `## decisions` is a two column table whose right
column holds paragraphs of 300 characters and more; oxfmt then aligns everything by the widest
cell. One row even broke: an unescaped `|` inside `file:line | summary` destroyed line 103.
Prose in a table cell is unreadable in a way prose in a paragraph is not.

**Six sections saying the same thing.** `what`, `why`, `decisions`, `design`, `behavior` and
`tasks` repeat the same fact three or four times: `review-agents`'s
`tools: Read, Grep, Glob, Bash` appears in four places. The cause is two competing indexes:
`draft-first.md:13-25` lists 7 things the draft has to cover and `SKILL.md`'s "Capture the
alignment" lists others. The model writes both.

**And the prompt asks for what we do not want.** `SKILL.md:55` says "Don't write a design
document"; twenty eight lines later, `:83` orders writing `## design` with "components and their
boundaries, the data model, key data flows". Between a prohibition and a positive instruction,
the positive one always wins, and `## design` is precisely the section nobody reads afterward
(`implement` reads `tasks` and `behavior`, the review walks `behavior`, `delegate` reads the
frontmatter). A section with no consumer drifts.

## The new form

The spec comes to have two halves, with different rules.

```
---  frontmatter  ---                    the contract (task-state.md)

# title
opening, 1-3 paragraphs                  ┐
                                         │  top half: free
## <the section the problem asks for>    │  as many sections as you want, with the
## <another>                             ┘  names the problem asks for: prose, a
                                            diagram, a short table, code.
## decisions                             ┐
## behavior                              │  the fixed set, in this order
## tasks                                 │  each one has a reader
## out of scope                          │
## open                                  ┘
```

The fixed set is fixed because it has readers. The top half has no machine consumer, it has a
human reader, and that is why its form belongs to the author.

`## design` does not come back in either half: in bb the word already means screen design
(`/bb:brisar` writes the visual direction in `design.md`, in the task's own folder).
Architecture, when the case asks for it, lives in the top half under the name it has in that
problem: "the seam between agent and caller" says more than "design".

## Decisions

- **A fixed set at the bottom, a free top**: `decisions`, `behavior`, `tasks`, `out of scope`
  and `open` in this order at the end; above them, an opening and as many sections as the
  problem asks for.
- **The prose describes, it does not recount**: what the thing is and how it behaves stays in
  the spec; how we got there goes to the commit body. That is the criterion separating the two.
- **A table cell is for short data**: past 100 characters it becomes prose or a bullet. The
  number comes from oxfmt: `fmt:check` runs `oxfmt --check .` with no ignore, so it already
  formats `.bb/` and aligns the whole column by the widest cell. A cell of 300 characters pushes
  the entire table off the screen.
- **Required versus recommended members**: the lint errors on a missing `## decisions` or
  `## open`; it warns on a missing `## behavior` and `## tasks`, which a Medium spec does not
  need to have.
- **`## design` is a dead name**: the lint bars it. Architecture goes to the top, under a name
  of its own.
- **`## still open` → `## open`**: a single name, and only a decision that is genuinely open.
- **discover's `## cuts` stays**: it is scope cut _in the problem phase_, with the why;
  `## out of scope` is what this spec does not do. The lint accepts both.
- **Remove rather than negate**: out of the prompt go the `## design` paragraph
  (`SKILL.md:83`), "map them meticulously" (`:68`), "Don't abbreviate" (`:70`) and the list of 7
  items in `draft-first.md:13-25`, which is the competing index.
- **A task carries its dep and its verification**: the line becomes
  `**N. name** — what it delivers → behaviors 1,3 · dep: N-1 · verifica: <how>`. It is the DAG a
  workflow consumes without reinterpreting prose.
- **The reviewer is a step of its own**: required in Medium and up, before the gate, with a one
  line verdict at the gate. Today it is a sub-bullet of a conditional step.
- **The lint only on the mechanical**: an error for `## design`, `## still open`, a row with the
  wrong cell count, a cell over 100 characters, invalid frontmatter, a missing required section.
  No line ceiling: size is judgment, and judgment belongs to the independent reviewer, which
  gains duplication and archaeology in its mandate.
- **CI: one `python3` step in `validate.yml`**: `python3 plugins/bb/skills/spec/scripts/lint_spec.py .bb/tasks/*/spec.md`,
  with no `setup-python` (`ubuntu-latest` already ships it), plus `.bb/tasks/**` in the `paths:`
  so the job fires when only the spec changes. `fmt:check` already covers those files today.
- **The rename only in the process sense**: `shape`/`shaped`/`shapear`/`re-shape` →
  spec/especificar. `Finding shape` and `return shape` stay: they are a data format, another
  sense.
- **Version**: `plugin.json` `2.3.0` → `2.4.0`. Each touched SKILL.md increments **its own**
  version (`spec` goes from `2.0.0` to `2.1.0`); the two numbers are independent.

## Behavior

1. `/bb:spec <idea>` runs draft-first, the highest stakes fork first, the gray areas batched
   through the question tool, and the draft is already born in the new form.
2. The brief has a free top and the fixed set; what is history does not enter, it goes to the
   commit.
3. Each task cites the behaviors it delivers, `dep:` and `verifica:`. That is where the coverage
   trace and the DAG a workflow consumes come from.
4. The independent reviewer runs on every Medium and up brief, in a fresh context, with only the
   brief.
5. `lint_spec.py` runs before the gate; whatever it points at is fixed right there.
6. The gate shows the happy path, the edges, the coverage and the reviewer's verdict, finalizes
   `.bb/tasks/<slug>/spec.md` and offers implement / delegate / stop.
7. Every skill that talks about the brief says "spec"; "shape" survives only as a data format.

| WHEN                                          | THEN                                                                            |
| --------------------------------------------- | ------------------------------------------------------------------------------- |
| the spec is rewritten after landing           | the why it changed goes in the commit; the file gains only the new decision     |
| a `## design` section shows up                | the lint fails naming the line and points at the top half                       |
| a table cell passes 100 characters            | the lint fails; the content becomes prose or a bullet                           |
| a row has an unescaped `\|`                   | the lint catches it by the cell count, the `review-agents:103` bug              |
| `## behavior` or `## tasks` is missing        | the lint warns; a Medium spec may not have both                                 |
| the author creates sections of their own      | it passes, that is the point; the lint only checks the fixed set                |
| an old spec from another repo has `## design` | the lint only runs on what `/bb:spec` just wrote                                |
| there is no Agent tool in the host            | the reviewer does not run and the gate says so, instead of omitting it          |
| the reviewer finds a load-bearing hole        | it goes back to the question step; the gate does not open with an open decision |
| the work is Tiny                              | no spec, it follows the auto-size rule that already exists                      |
| the brief was seeded by `/bb:discover`        | the upstream sections stay at the top, which is free                            |

## Tasks

- [x] **1. The format and the lint**: `references/spec-format.md` (the two halves, the fixed
      set, the describes-versus-recounts criterion) and `scripts/lint_spec.py` (stdlib,
      `path:line CODE msg`, exit 1 on an error) → behaviors 2, 3, 5 · dep: — · verify: CI
- [x] **2. Pruning the prompt**: deletes the `## design` paragraph, "meticulously" and "Don't
      abbreviate" from `SKILL.md`; kills `draft-first.md`'s list of 7; both come to point at
      `spec-format.md` → behaviors 1, 2 · dep: 1 · verify: CI
- [x] **3. The reviewer as a step of its own**: a dedicated step in `SKILL.md`, required in
      Medium and up, with duplication and archaeology in its mandate; a one line verdict at the
      gate → behaviors 4, 6 · dep: 2 · verify: reading
- [x] **4. A task ready for a workflow**: `dep:` and `verifica:` in `spec-format.md`;
      `implement` and `delegate` read both → behavior 3 · dep: 1 · verify: reading
- [x] **5. The rationale in the commit**: a line in `SKILL.md` and in `.claude/CLAUDE.md`'s
      Commits section → behavior 2 · dep: — · verify: reading
- [x] **6. The shape→spec rename**: `task-state.md`, `delegate`, `implement`, `discover`,
      `brisar`, `operating-context.md`, `routines.md`, `spec/SKILL.md`, README
      → behavior 7 · dep: — · verify: CI
- [x] **7. Migrating the 3 specs and wiring CI**: rewrites `builder-bundle`, `ship-lexflow` and
      `review-agents` in the new form; the `python3` step and `.bb/tasks/**` in `validate.yml`
      → behavior 5 · dep: 1, 6 · verify: CI green
- [x] **8. Version and docs**: `plugin.json` `2.4.0`, `spec/SKILL.md` `2.1.0`, the CHANGELOG,
      `.claude/CLAUDE.md` → behavior 7 · dep: 1-7 · verify: CI

## Out of scope

- A workflow in `implement`/`delegate` to build the tasks: a spec of its own, right after this
  one. Only what the spec has to deliver to it enters here.
- `Finding shape` and `return shape` in the review: another sense of the word.
- Export mode (`references/export-spec.md`): an external document, not the brief.

## Open

- Nothing.
