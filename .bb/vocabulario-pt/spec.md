---
status: done
created: 2026-08-12
slug: vocabulario-pt
---

# vocabulary: one word per thing, in Portuguese

bb writes `slice` 125 times. The user never wrote that word, and the plugin never wrote "fatia"
either, and even so "fatia" shows up in the sessions, because the model translated it on its own.
That is the portrait of the problem: the plugin names a concept in English, Claude repeats the
naming in Portuguese inventing the translation, and out comes a word that exists neither in the
code nor in the conversation. The gender wobbles inside one session ("o slice 6", "a slice 15")
and it wobbles inside the plugin itself ("construo os slices", "Construo as slices").

This spec does two things that hold each other up: it renames the concepts bb invented and it
writes the rule that stops the next one. Along with them go the spec's fixed set of sections in
Portuguese and the folder on disk, which loses a level.

Success: a non-technical person reads the output of any bb skill and finds no word that needs
translating.

## Two causes, two remedies

The survey separated the terms by where they live, and the split decides the remedy:

| term         | occurrences | in a PT line | where it lives            |
| ------------ | ----------- | ------------ | ------------------------- |
| brief        | 423         | 18           | English prose             |
| scope        | 146         | 5            | English prose             |
| slice        | 125         | 4            | English prose             |
| shape        | 64          | 3            | English prose             |
| blocker      | 42          | 1            | English prose             |
| load-bearing | 25          | 1            | English prose             |
| fan-out      | 24          | 2            | English prose             |
| veredito     | 12          | 5            | an agent's `description:` |
| gray area    | 10          | 0            | English prose             |
| seam         | 3           | 0            | English prose             |
| lente        | 3           | 2            | an agent's `description:` |
| landar       | 2           | 2            | a skill's `description:`  |

Almost everything lives in the **English** documentation, and that splits the terms into two
groups with different treatments.

**A bb proper name**: `slice` and `brief` name things that only exist in here. The name is the
concept, so changing the name kills the leak at the source, and the change holds in the English
prose too, because that is where the other 121 occurrences are. Substitution solves it.

**An English word in an English document**: `blocker`, `load-bearing`, `fan-out`, `scope`,
`gray area`, `seam`. An English document writing "load-bearing decision" is ordinary English;
swapping in "decisão estruturante" mid-sentence produces broken text. Those leak by another
path: Claude reads English and speaks Portuguese, and when it is time to speak there is no word
ready. The remedy is the translation table, not substitution: the document stays as it is, and
the table says what to say when the text is Portuguese.

## The capitalization is already right

The ask was to standardize the capitalization of the Portuguese text, and the sweep returned the
opposite of what was expected: outside the design system, the plugin's Portuguese has two lines
in Title Case, and both defend themselves. "Fase Deliver" names the double diamond phase, "Não é
o produto final" opens a sentence. The gates' option labels are already consistent sentence case,
with `(Recomendado)` as a suffix.

What is missing is not cleanup, it is the rule: there is not a single line written about
capitalization anywhere in the plugin, and that is why the spec's fixed set of sections ended up
all in lower case. What is delivered here is the written rule plus the capitalized set, not a
correction pass.

## The rule, and where it lives

The new `references/vocabulario.md` carries three things: the principle (call each thing by the
name it has in the code or in the repo), the EN→PT table resolved above, and the capitalization.
It is written as positive instruction: it says which word to use, not which one to avoid. Listing
the wrong word next to the right one writes it into the prompt and primes the model for it; it is
the same reason `## design` survived in `spec/SKILL.md` while being forbidden on line 55 and
asked for on line 83.

The pointer to it goes in `hooks/operating-context.md` because that file is injected at the start
of the session **and after each compaction**, so it holds for every skill and for a loose
conversation, which is the reach that was asked for. `spec-format.md` gains a line of its own:
the spec is a written artifact and its vocabulary is what the builder will repeat afterward.

## Decisions

- **`slice` dies.** The item in `## Tarefas` is **tarefa** in Portuguese and **task** in English.
  They are cognates, so the concept has a single name and no third word enters. The swap holds in
  the English prose too, 12 files, including `lint_spec.py`'s `W002` message.
- **`fase` is a grouping of tasks**, not a synonym for a task. `/bb:brisar` already uses it that
  way ("Fase Develop", "Fase Deliver"), so there is nothing to fix there, only the definition to
  pin down.
- **The top level is `spec`** in both languages: the file is `spec.md`, the command is
  `/bb:spec`. "a task pendente" becomes "a spec pendente"; "the brief" becomes "the spec".
  `references/task-state.md` comes to be called `spec-state.md`.
- **The word "brief" stays inside `/bb:brisar`**: in `skills/brisar/**` it is the
  `brief-design.md`, another artifact, with a file and a name of its own. That is 207 of the 423
  occurrences. The exception is where the text points explicitly at `spec.md` or at
  `/bb:discover`'s brief: those become "spec".
- **The folder loses a level: `.bb/<slug>/`.** `.bb/` holds nothing besides `tasks/` today, so
  the intermediate level existed only to repeat the word being retired. The sweep glob becomes
  `.bb/*/spec.md`.
- **The old path stays findable.** The readers sweep `.bb/*/spec.md` and `.bb/tasks/*/spec.md`;
  a spec in another repo (app, reasoning-bench) does not disappear. The folder's slug is the key,
  so the same spec in both places counts once.
- **The fixed set is translated and capitalized:** `## Decisões`, `## Comportamento`,
  `## Tarefas`, `## Fora de escopo`, `## Em aberto`. The sections seeded by `/bb:discover` come
  along, `## Problema`, `## Hipótese`, `## Encaixe`, `## Cortes`, and so does `/bb:legal-lens`'s:
  `## Jurídico`.
- **`dep:` becomes `depende:`**; `verifica:` is already Portuguese and stays.
- **The English name stays valid as a warning.** `lint_spec.py` gains `W003`: the English section
  is accepted, with the translation alongside; the section readers accept both names. An old spec
  in any repo stays buildable.
- **The frontmatter stays English** (`status`, `created`, `slug`, `pending|blocked|done`). Those
  are data keys validated by `E001` and written by `/bb:delegate`.
- **The other terms enter through a table, not through substitution.** `vocabulario.md` carries
  the EN→PT pair; the English document stays English.
- **`shape` has two senses.** In the sense of giving form to an idea it is **spec** (a rename
  already done in `spec-legivel`); in the sense of a data format (`Finding shape`) it is
  **formato**.
- **The trigger phrases in the `description:` stay intact.** "landa essa branch", "esverdeia a
  PR", "shapeia essa ideia" are how the user talks and they are what routes the skill. The table
  governs the prose of the `description:`, not the trigger list.
- **The agents' Portuguese `description:` is rewritten.** `bb-finder` and `bb-verifier`
  concentrate "veredito", "lente", "fan-out", "read-only" and "Finding shape" into two Portuguese
  sentences, so it is PT text and it follows the table.
- **Capitalization:** Portuguese in sentence case, only the first letter goes up. A proper noun
  and an identifier keep their exact case. `(Recomendado)` is a suffix of the label.
- **The rule lists no forbidden word.** Positive instruction; the table has the "escreva" column,
  and the English term appears only as a search key.

## Behavior

Happy path:

1. The session opens (or compacts) → the hook injects the pointer to `vocabulario.md` → Claude
   names things by the name they have in the repo, writes "tarefa" and "spec", and uses the
   table's "escreva" column when the document carries the English term.
2. `/bb:spec` runs → it writes `.bb/<slug>/spec.md` with the capitalized Portuguese set.
3. `lint_spec.py` on the new spec → no finding.
4. `/bb:implement` reads the spec → it finds `## Tarefas`, reads `depende:` and `verifica:`, and
   builds task by task.
5. `/bb:review` walks `## Comportamento` row by row; `/bb:spec`'s gate blocks on `## Em aberto`.
6. `/bb:delegate` with no argument sweeps `.bb/*/spec.md`, finds the migrated specs and picks the
   oldest pending one.
7. CI runs `validate.yml` → the lint over `.bb/*/spec.md` → green on all 7.
8. `/bb:review` dispatches the agents → the `description:` and the report come out in Portuguese
   with no term that needs translating.

| #   | WHEN                                                         | THEN                                                                       |
| --- | ------------------------------------------------------------ | -------------------------------------------------------------------------- |
| 9   | an old spec with `## decisions`/`## open`                    | the lint emits `W003` with the translation; no error, the file stays valid |
| 10  | an old spec reaches `/bb:implement`                          | it finds `## tasks` by the old name and builds the same                    |
| 11  | a spec mixes `## Tarefas` and `## tasks`                     | the lint emits `W003` on the English section; both are read                |
| 12  | a spec with neither `## Decisões` nor `## decisions`         | `E002` as today, now citing the Portuguese name                            |
| 13  | a spec with `## design` or `## still open`                   | `E003` as today; a dead name stays dead                                    |
| 14  | a task line still written with `dep:`                        | read normally; `depende:` and `dep:` both hold                             |
| 15  | the spec lives in another repo's `.bb/tasks/<slug>/`         | found and built; the old glob stays in the sweep                           |
| 16  | the repo has identical `.bb/<slug>/` and `.bb/tasks/<slug>/` | it counts once; the folder's slug is the key                               |
| 17  | the plugin's English text uses "load-bearing"                | it stays as it is; the table governs what gets written in Portuguese       |
| 18  | the user says "landa essa branch" or "esverdeia a PR"        | it routes to `/bb:ship` as today; the triggers do not change               |
| 19  | `/bb:legal-lens` runs over a spec                            | it appends `## Jurídico`; an existing `## legal` is read and warned about  |
| 20  | the term Claude needs is missing from the table              | it describes in three words what happens, instead of naming it             |

## Tasks

- [x] **1. `references/vocabulario.md`**: the principle, the EN→PT table and the capitalization
      rule, as positive instruction → behaviors 1, 17, 20 · dep: — · verify: reading
- [x] **2. The pointer in the hook and in the format**: a short bullet in
      `hooks/operating-context.md` and a line in `spec/references/spec-format.md`
      → behavior 1 · dep: 1 · verify: reading
- [x] **3. The `slice` → task/tarefa rename**: 12 files, including `lint_spec.py`'s `W002`;
      `build-slices-workflow.md` becomes `build-tasks-workflow.md` and the 4 pointers to it come
      along → behaviors 4, 10 · dep: 1 · verify: an empty grep
- [x] **4. The top level renamed to spec**: the 216 occurrences outside `skills/brisar/**`, plus
      brisar's that point at `spec.md`; `task-state.md` becomes `spec-state.md`
      → behaviors 2, 4 · dep: 1 · verify: a grep plus reading
- [x] **5. The `.bb/<slug>/` folder**: `spec-state.md`, the 33 files that cite the path,
      `delegate`'s glob and `validate.yml`, with the old path kept in the sweep
      → behaviors 2, 6, 7, 15, 16 · dep: 4 · verify: CI
- [x] **6. The Portuguese set in the format and in the lint**: `spec-format.md` and
      `lint_spec.py` with `W003` and the double names → behaviors 2, 3, 9, 11, 12, 13 ·
      dep: 3, 4 · verify: CI
- [x] **7. The section readers accept both names**: `implement`, `review`, `delegate`,
      `discover`, `brisar`, `legal-lens`, `build-mode`, `spec-state`, plus `depende:`/`dep:`
      → behaviors 4, 5, 10, 14, 19 · dep: 6 · verify: reading
- [x] **8. The agents' `description:` in Portuguese**: `bb-finder` and `bb-verifier` through the
      table, triggers preserved → behaviors 8, 18 · dep: 1 · verify: reading
- [x] **9. Migrating the 7 specs on disk**: moves them to `.bb/<slug>/`, the set translated and
      `depende:`, the `done` ones and this one included → behaviors 6, 7 · dep: 5, 6 ·
      verify: CI green
- [x] **10. Version and docs**: `plugin.json` `2.9.0`, the CHANGELOG, the README and
      `.claude/CLAUDE.md` → behavior 7 · dep: 1-9 · verify: CI

## Out of scope

- Translating the plugin's English prose. The reference documents are written in English and stay
  that way.
- `references/ds/brand/**`: "Rich Black", "Cornflower Blue", "Four Entities" are a color name and
  a brand principle name, not derived text.
- A capitalization correction pass over the Portuguese text: the sweep found no defect that
  justifies one.
- The frontmatter and the `status` values.
- A capitalization check in CI: detecting case by regex over mixed PT/EN text generates a false
  positive. _revisit_ if the written rule does not hold.
- Removing the English section names and the `.bb/tasks/*/spec.md` glob. They stay as a warning;
  the removal date is a decision for another moment, with the other repos' specs already
  migrated.
- Re-measuring the sessions to confirm the terms fell instead of shifting to a neighbor.
  _revisit_: that gets measured after a few weeks of use, not in the PR.

## Open

- The `verifica: CI` of tasks 5, 9 and 10 passes trivially in this repo. `validate.yml`'s second
  glob (`.bb/tasks/*/spec.md`) expands empty because there is no `.bb/tasks/` here, so the dedup
  by slug never runs; and the 7 specs on disk are already in the Portuguese set, so W003 never
  fires. The green check proves the lint runs, not that the Portuguese/English pair works. The
  real proof is the first spec from another repo still on the old path, or a fixture, which was
  decided against.
- Swapping the `paths:` filter in `validate.yml` (`skills/**` → `plugins/**`) is a deliberate
  ride-along: no task asked for it, but without it the workflow does not fire on the files this
  PR moves. It stays in the same commit instead of a branch of its own.
