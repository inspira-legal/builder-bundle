---
status: pending
created: 2026-08-18
slug: english-only
---

# one language: the bundle writes English

The bundle has carried two languages since `vocabulario-pt`: English instruction
bodies, and a Portuguese layer for everything the user sees. The layer was built to
guarantee the user gets answered in their language. Claude already follows the
language the user writes in, so the guarantee was never the mandate's to give: what
the mandate actually buys is a second vocabulary to maintain, a reference to police
it, and a bilingual document every time a gate question sits inside an English step.

So the layer goes. Every sentence in the bundle becomes English, and every line that
orders a Portuguese answer is deleted rather than reversed, because an instruction
about output language is exactly what the model does on its own.

## Decisions

- **The hybrid policy ends.** No file states an output language, for prose or for
  gates or for reports. What replaces it is nothing: the model reads the user and
  answers in kind.
- **`plugins/bb/references/vocabulario.md` is deleted.** It exists to rule the
  Portuguese layer. The one rule that survives it, call each thing by the name the
  code gives it, is already in `doc-style.md`, and the four readers point there.
- **The spec's fixed sections go back to English**: `## Decisions`, `## Behavior`, `## Tasks`,
  `## Out of scope`, `## Open`. The task fields become `dep:` and `verify:`.
  `lint_spec.py` keeps resolving both spellings, and `W003` now carries the English
  name to write instead.
- **The `references/ds/` package stays untouched.** It is the Inspira brand package, and its
  Portuguese voice is the asset itself.
- **The record gets translated too**: the 12 `CHANGELOG.md` entries and the 8 landed
  specs in `.bb/`. A bilingual archive is the same maintenance problem one directory
  down.
- **Identifiers keep their names.** `/bb:brisar` stays `brisar`, the `.bb/<slug>/`
  slugs stay, `CODE_REVIEW_GUIDE.md` stays. A name is a token users type and files
  carry, not prose.
- **The `—` in `dep: —` survives the rename.** It is a value the format reserves,
  which `doc-style.md` already exempts.
- **Every rewritten `description:` stays a plain YAML scalar**, so no `: ` and no
  ` #` inside it. Both break the parse or silently truncate the value.
- **The new English prose follows `doc-style.md`**: no dash, sentence case in
  headings, one idea per list item.
- **A figure of speech has to name a mechanism the code has.** `spine` for the fixed
  sections and `ruler` for this page name nothing, so they become what they are, and
  `doc-style.md` states the rule in that form. `safety valve`, `gate`, `front` and
  `trilha` stay: each one is a name the plugin already uses for a real mechanism.

## Behavior

Happy path, one area at a time, each area a commit:

1. The section rename lands first, in `lint_spec.py` and in every page that names a
   section or a task field. Nothing else can be written against the new names until
   this is true.
2. The 15 `SKILL.md` descriptions and the 2 agent descriptions become English, each
   one still a plain YAML scalar.
3. The gate questions, option labels, and report templates inside the skills become
   English.
4. Every sentence that orders an output language is deleted, in `.claude/CLAUDE.md`,
   `hooks/operating-context.md`, `doc-style.md`, and the skills.
5. `vocabulario.md` is deleted and its four readers are repointed.
6. `README.md` becomes English, keeping the all lowercase house style.
7. The two manifests carry English descriptions.
8. `CHANGELOG.md` becomes English, entry by entry.
9. The 8 landed specs in `.bb/` become English, section names included.
10. Every figure that names nothing is replaced by the literal name.
11. The version goes to 2.13.0 with an English entry describing the change.

| WHEN                                                       | THEN                                                                             |
| ---------------------------------------------------------- | -------------------------------------------------------------------------------- |
| a rewritten `description:` would need a colon              | it takes a period, parentheses, or a comma, and never a quoted scalar            |
| a `description:` carries a `#`                             | the `#` goes, because YAML reads it as a comment and drops the rest of the line  |
| a page names a fixed section                               | it names the English one, and no page teaches the Portuguese spelling as current |
| a landed spec still uses the Portuguese section names      | the lint accepts it, and task 9 rewrites it anyway                               |
| a line in `ds/` is Portuguese                              | it stays Portuguese                                                              |
| a Portuguese word is an identifier (`brisar`, a slug)      | it stays as written                                                              |
| a translated sentence wants a dash                         | it takes what `doc-style.md` prescribes                                          |
| the `fmt:check` reflows a table after a cell changes width | the padding change rides along in that area's commit                             |
| CI fails on a rewritten frontmatter                        | the fix comes from the CI log, not from a local run                              |

## Tasks

- [x] **1. English section names**: `lint_spec.py` (canonical set, `W003` message, dead
      section text), `spec-format.md`, `spec-state.md`, `export-spec.md`,
      `build-tasks-workflow.md`, `build-mode.md`, `delegate/SKILL.md`,
      `implement/SKILL.md`, `spec/SKILL.md`, `review/SKILL.md`, `front-contract.md`,
      `phase-4-design-direction.md`, `doc-style.md`, `operating-context.md`,
      `.claude/CLAUDE.md`
      → behaviors 1, table rows 3 and 4 · dep: — · verify: `grep -rn "## Decisões\|## Comportamento\|## Tarefas\|## Fora de escopo\|## Em aberto\|depende:\|verifica:"` outside `.bb/` and `CHANGELOG.md` returns only the lines that name those as the older spelling, which the compat rule keeps
- [x] **2. Frontmatter descriptions**: 15 `SKILL.md` plus `bb-review-finder.md` and
      `bb-review-verifier.md`
      → behaviors 2, table rows 1 and 2 · dep: — · verify: the frontmatter sweep finds no `: ` and no ` #` in any plain scalar
- [x] **3. Gates, options, and report templates**: every skill, `handoff-gate.md`,
      `brisar/references/*`, `challenge/references/modes.md`,
      `review-setup/references/interview.md`
      → behavior 3 · dep: 1 · verify: reading, plus the Portuguese line census on the touched files
- [x] **4. The language mandate goes**: `.claude/CLAUDE.md` (the hybrid section),
      `hooks/operating-context.md`, `doc-style.md` (the Portuguese layer paragraph),
      and every "in PT-BR" instruction in the skills
      → behavior 4 · dep: 3 · verify: `grep -rniE "PT-BR|português|portuguese"` outside `ds/` returns only the compat lines that name the Portuguese section spellings as the older ones, and the `lang="pt-BR"` a scaffold example writes into a page it builds
- [x] **5. `vocabulario.md` deleted**: the file goes, `doc-style.md` states the naming
      rule, and `.claude/CLAUDE.md`, `operating-context.md`, `guide-template.md`,
      `spec/SKILL.md` point there
      → behavior 5 · dep: 4 · verify: `grep -rn "vocabulario"` outside `.bb/` and `CHANGELOG.md` returns nothing
- [x] **6. `README.md`**: the whole page, all lowercase kept
      → behavior 6 · dep: 1 · verify: the Portuguese line census on the file returns nothing
- [x] **7. Manifests**: `plugins/bb/.claude-plugin/plugin.json` and
      `.claude-plugin/marketplace.json`
      → behavior 7 · dep: — · verify: both descriptions read English
- [x] **8. `CHANGELOG.md`**: the 12 entries, headings and prose
      → behavior 8 · dep: 1 · verify: the Portuguese line census on the file returns only the tokens an entry quotes from the version it describes
- [x] **9. The 8 landed specs**: `.bb/*/spec.md`, prose and section names
      → behaviors 9, table row 4 · dep: 1 · verify: the census returns nothing and the CI lint stays green
- [x] **10. Literal names**: `spine` and `ruler` become the thing they name, the
      figures that name nothing go (rubber-stamp, "that bite", the smaller door), and
      `doc-style.md` states the rule
      → behavior 10 · dep: — · verify: `grep -rniE "spine|ruler|rubber-?stamp|that bite"` outside `.bb/`, `CHANGELOG.md` and `ds/` returns nothing
- [ ] **11. 2.13.0**: version in the plugin manifest, English `CHANGELOG` entry, spec
      closed
      → behavior 11 · dep: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 · verify: `gh pr checks --watch` green

## Out of scope

- `plugins/bb/skills/brisar/references/ds/**`, the brand package.
- Renaming any skill, slug, or file. `brisar` keeps its name.
- The `vocabulario-pt` spec's own history. Task 9 translates the document, and the
  fact that this work reverses it belongs in the commit body.
- A CI check that detects Portuguese. The census greps are how each task proves
  itself, and a language detector over mixed prose costs more than the drift.

## Open

- The census grep is a heuristic: it counts lines whose Portuguese function words
  outnumber the English ones, so a short line either way reads as neither. Reading is
  what closes each area, and the per area commit is what makes that reading fit.
