---
status: done
created: 2026-08-18
slug: doc-style-google
---

# documentation style: the Google guide inside bb

bb writes English prose in two places. In the documents it generates outward, the README from
`/bb:write-readme` and the CODE_REVIEW_GUIDE from `/bb:review-setup`, and in the instruction
the agents read: the `SKILL.md` files, the `references/`, the repo's `README.md`, the
`.claude/CLAUDE.md`. Neither of the two has a rule today. `## How It Works` sits next to
`## Style contract`, `# Quality Checklist` next to `## Bundled Resources`, and the em dash
shows up 1737 times in 84 files, even with `/bb:write-readme` banning its own since the first
version.

The guide at https://developers.google.com/style fills exactly that gap: it is the most
tested technical documentation guide there is, written for people reading in a second
language, and bb already agrees with half of it by instinct (second person, active voice,
condition before instruction). This spec distills the guide into a reference, records the two
exceptions bb keeps, and runs the rule over what is already written.

Success: an agent about to write English prose opens a file and knows what to do, and the
prose it reads around that file does not contradict it.

## The border between the two languages

The guide is English: American spelling, word list, tone. It holds over the English prose,
which is the method's instruction and what bb generates outward. The Portuguese layer
(`description:`, a gate question, an option label, a report) stays governed by
`vocabulario.md`, which already asks for sentence case and already carries the term table.

The em dash rule is the only one that crosses both languages, because it is punctuation and
not vocabulary: the 22 em dashes living inside `description:` are Portuguese lines and they
fall with the rest.

## The two exceptions

The guide comes in whole, with two decided divergences the reference records in its opening,
so a reader knows it is not an oversight:

1. **No em dash, ever.** Stronger than Google, which allows the em dash unspaced. Where one
   would go, a comma goes, or a colon, or a period, or the sentence gets rewritten. It is the
   contract `/bb:write-readme` already has, promoted to the whole plugin.
2. **The figurative voice stays.** Google bans metaphor because it travels badly through
   translation. In bb the metaphor is payload: it is what makes the instruction stick to the
   agent reading the `SKILL.md`. The rest of the tone chapter comes in as written.

## The size of the migration

The scope is everything outside `references/ds/**`, `CHANGELOG.md` and the specs in `.bb/`.
Each removal is a judgment per sentence, not a `sed`, which is why the file column matters as
much as the occurrence column: slicing by area exists so each commit fits in one reading.

| area                                            | files | em dashes |
| ----------------------------------------------- | ----- | --------- |
| `skills/brisar/**`, without `ds/`               | 18    | 784       |
| `skills/review/**` and `skills/review-setup/**` | 21    | 331       |
| `skills/spec/**` and `skills/ship/**`           | 13    | 234       |
| the other 9 skills                              | 15    | 220       |
| `plugins/bb/references/`, `hooks/`, `agents/`   | 12    | 127       |
| `README.md`, `CLAUDE.md`, CI and the 2 `.json`  | 5     | 41        |
| total                                           | 84    | 1737      |

Beyond the em dash, the sweep found 33 en dashes, 54 unspaced em dashes and 37 headings in
declared title case (`### Naming Conventions`, `## Bundled Resources`,
`# Quality Checklist`). The 259 headings that contain an em dash are rewritten by the dash
rule, not by a casing task.

## Decisions

- The new reference is `plugins/bb/references/doc-style.md`, at plugin level and not scoped to
  a skill, because it governs the prose of every skill and of the repo.
  `hooks/operating-context.md` points at it alongside `vocabulario.md`, which is how the rule
  reaches a session in any repo, not only in this one. No new skill and no docs lens in
  `/bb:review`: the rule is reading for whoever writes, not a review step.
- Inside it, positive form only. No recommended/not recommended pair and no catalog of the
  wrong version: writing the wrong one next to the right one primes the wrong one, which is
  the prompt rule from the global `CLAUDE.md`.
- Precedence: the house rule first, the guide after. It is the hierarchy Google itself
  publishes. Where `/bb:write-readme` already has a contract (all lowercase, four blocks, a
  badge per verifiable fact), the contract wins, and its `SKILL.md` points at the reference
  instead of repeating the dash rule.
- No em dash ever, in both languages. The en dash leaves the same way, and the unspaced em
  dash enters the same sweep.
- A dash that is a functional token stays: when the character sits inside a command, a regex,
  a path or a string compared in code, removing it is not style, it is a behavior change.
- A verbatim quote from an external source keeps the source's punctuation. It is the only
  exception to the dash rule.
- A generated template follows the rule. The fenced block that is an output model, the
  `review-setup/references/guide-template.md` and the report templates, is prose bb writes
  outward.
- Headings in sentence case outside `ds/`. A proper noun and an identifier keep their casing:
  `# Builder Bundle (bb)`, `Mobbin`, `Framer`, `LexFlow`, `Phase Framer`.
- `references/ds/**` stays untouched. It is the Inspira brand package, brand content with a
  voice of its own.
- In `CHANGELOG.md`, the old entries stay. The new entry switches its heading to
  `## 2.12.0 (2026-08-18)`, because the current format separates version and date with an em
  dash.
- The 7 specs in `.bb/` stay as they are. They are a landed record; only this one follows the
  new rule.
- The enforcement is the reference being read. No CI check and no script: a dash detector over
  mixed PT/EN prose flags a functional token and a quote, and the false positive costs more
  than the drift.
- Lands in a single PR, with one commit per area.
- Version `2.12.0`.

## Behavior

Happy path:

1. An agent is about to write English prose → `.claude/CLAUDE.md` points at `doc-style.md` →
   it reads the reference before writing.
2. It writes headings in sentence case, second person, active voice, condition before the
   instruction, code font on a filename, a class, a method, an HTTP status and a placeholder,
   and no em dash.
3. `/bb:write-readme` runs → it keeps everything lowercase, the four blocks and the badge per
   verifiable fact → the README comes out with no em dash and no en dash.
4. `/bb:review-setup` runs → `guide-template.md` generates the CODE_REVIEW_GUIDE with headings
   in sentence case and no em dash.
5. `/bb:spec` writes a spec → Portuguese prose per `vocabulario.md`, and no em dash.
6. CI runs on the PR → frontmatter, the spec lint and `fmt:check` green.

| #   | WHEN                                                     | THEN                                                  |
| --- | -------------------------------------------------------- | ----------------------------------------------------- |
| 7   | an em dash grep outside `ds/`, `CHANGELOG.md` and `.bb/` | zero occurrences                                      |
| 8   | an en dash grep in the same scope                        | zero, outside a functional token                      |
| 9   | the prose quotes verbatim a source that uses an em dash  | the quote keeps the source's punctuation              |
| 10  | the character sits in a command, regex, path or string   | it stays; removing it would change behavior           |
| 11  | the heading carries a proper noun or an identifier       | the original casing stays                             |
| 12  | the heading joins a label and a phrase with an em dash   | it becomes `## Phase 2: maturity gate`                |
| 13  | a guide rule meets a `/bb:write-readme` contract         | the house contract wins                               |
| 14  | a new entry in `CHANGELOG.md`                            | the heading `## 2.12.0 (2026-08-18)`                  |
| 15  | an old CHANGELOG entry or a spec in `.bb/`               | untouched                                             |
| 16  | a file inside `references/ds/**`                         | nothing changes                                       |
| 17  | a Portuguese line: `description:`, a gate, a report      | `vocabulario.md` rules; only the dash comes from here |
| 18  | the English prose uses a metaphor                        | it stays; the exception is written in the reference   |

## Tasks

- [x] **1. `references/doc-style.md`**: the guide distilled in positive form, covering tone and
      voice, headings, text formatting, lists and tables, links, dates and numbers, plus the
      two exceptions and the precedence
      → behaviors 1, 2, 11, 13, 17, 18 · dep: — · verify: reading
- [x] **2. The four readers**: a pointer in `.claude/CLAUDE.md`, in
      `hooks/operating-context.md`, in `write-readme/SKILL.md` and in
      `review-setup/references/guide-template.md`; write-readme keeps only the house rules
      → behaviors 1, 3, 4, 5, 13 · dep: 1 · verify: reading
- [x] **3. Heading triage**: the 37 in declared title case outside `ds/`, plus the candidates
      where the casing depends on a proper noun or on a template
      → behaviors 2, 11 · dep: 1 · verify: reading
- [x] **4. The em dash in `brisar`**: 784 across 18 files, with `ds/` out
      → behaviors 7, 12, 16 · dep: 1 · verify: an empty grep
- [x] **5. The em dash in `review` and `review-setup`**: 331 across 21 files, including the
      report templates and `guide-template.md`
      → behaviors 7, 9, 10, 12 · dep: 1 · verify: an empty grep
- [x] **6. The em dash in `spec` and `ship`**: 234 across 13 files, including the report
      templates and the fixed set `/bb:spec` writes
      → behaviors 5, 7, 12 · dep: 1 · verify: an empty grep
- [x] **7. The em dash in the other 9 skills**: 220 across 15 files: `discover` 44, `challenge`
      32, `code-deep-research` 27, `maintain-repo` 24, `implement` 23, `legal-lens` 23,
      `delegate` 19, `think` 19, `gather-branch-context` 9; the 22 from `description:` live in
      those files → behaviors 7, 17 · dep: 1 · verify: an empty grep
- [x] **8. The em dash in the plugin references, the hooks and the agents**: 127 across 12
      files, including `vocabulario.md` and `operating-context.md`
      → behavior 7 · dep: 1 · verify: an empty grep
- [x] **9. The em dash in the repo docs**: 41 across 5 files: `README.md` 18,
      `.claude/CLAUDE.md` 20, the echo message in `validate.yml` and the 2 plugin `.json`
      → behavior 7 · dep: 2 · verify: an empty grep
- [x] **10. The en dash and the unspaced em dash**: the 33 and the 54 in scope, with the
      functional token preserved → behaviors 8, 10 · dep: 4, 5, 6, 7, 8, 9 · verify: a grep
- [x] **11. Version and CHANGELOG**: `plugin.json` at `2.12.0` and the new entry with the
      heading `## 2.12.0 (2026-08-18)`, in prose with no em dash
      → behaviors 6, 14, 15 · dep: 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 · verify: CI green

## Out of scope

- `references/ds/**`: 383 em dashes, 74 headings with an em dash and 70 in title case. It is
  the Inspira brand package, brand content with a voice of its own.
- The old `CHANGELOG.md` entries, 122 em dashes. A historical record: rewriting it changes
  what was already published.
- The 7 specs in `.bb/`, 231 em dashes. They have landed.
- A CI check or a detection script. _revisit_ if the written rule does not hold; the measure is
  a fresh grep after a few weeks of use.
- A docs lens in `/bb:review`, and a `/bb:docs` skill.
- American spelling and the word list in the Portuguese prose. `vocabulario.md` stays alone
  there.
- Rewriting the plugin's figurative voice.
- Translating the English prose, the new reference included: it is method instruction, so it
  stays English.

## Open

- The `verify: an empty grep` of tasks 4 to 9 proves the character left, not that the sentence
  came out well. The mechanical comma in the dash's place sometimes has to become a colon or a
  new sentence, and only reading catches that. The per area commit exists so that reading
  fits.
- `fmt:check` reformats a table: a rewrite that changes one cell's width changes the padding
  of the whole column. That is expected noise in the diff of tasks 4 to 9, not a defect.
