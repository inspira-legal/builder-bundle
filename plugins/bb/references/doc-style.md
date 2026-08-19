# Documentation style

## Where this applies

Every English sentence this plugin writes. That is two bodies of prose: the instruction
agents read (`SKILL.md` bodies, `references/`, the repo `README.md`, `.claude/CLAUDE.md`) and
the documents a skill generates for another repo (the README from `/bb:write-readme`, the
CODE_REVIEW_GUIDE from `/bb:review-setup`, the report templates that live inside fenced
blocks). A fenced block that is an output template is prose bb writes outward, so it follows
this page too.

The Portuguese layer belongs to `vocabulario.md`: the `description:` field, gate questions,
option labels, reports, and plain chat. This page is English, which is where American
spelling and the word choices below apply. One rule crosses both languages, the dash rule,
because it is punctuation rather than vocabulary.

This page is the whole ruler. Every rule bb writes by is stated here, so writing to it is a
local read, never a fetch.

## Precedence

A project guideline first, this page second. Where a skill states its own contract, the
contract wins: `/bb:write-readme` keeps all lowercase, its four blocks, and one badge per
verifiable fact. What neither settles goes to the closest rule on this page.

## Dashes

Where a dash would go, write a comma, a colon, a period, or rewrite the sentence. A colon
fits when the second half explains the first, and a period fits when it stands on its own.
Two things keep the character: a functional token (inside a command, a regex, a path, a
string compared in code, or a value a format reserves, like the `dep: —` a task line
carries when nothing blocks it), and a verbatim quote from an outside source, which keeps the
punctuation of its source.

Inside YAML frontmatter the colon is unavailable: a `: ` in an unquoted value reads as a
nested mapping and fails the parse. A dash in a `description:` becomes a period, parentheses,
or a comma.

## Voice and tone

- Address the reader as "you", and name who acts. "Run the script", "the hook injects the
  context".
- Put the condition before the instruction: "To land on a protected branch, open a PR."
- Write for a reader in their second language: short sentences, one idea each, ordinary words
  in place of jargon.
- Keep every sentence carrying something the reader can act on. A step reads as an
  instruction and its outcome, and how fast or how simple it is comes across from the step
  itself.
- Metaphor is welcome where it names a mechanism: the safety valve that fires, the gate that
  blocks, a tool that is a smaller door and not a closed one. A figure that carries a
  mechanism is what makes an instruction stick to the agent reading the `SKILL.md`. Where the
  literal sentence is already short, write the literal sentence.
- Use American spelling, and call each thing by the name the code gives it.

## Headings

- Sentence case: the first word goes up, and proper nouns and identifiers keep the case they
  already have. `# Builder Bundle (bb)` is a name. `### Naming conventions` is a phrase.
- A task heading opens with a bare infinitive: "Resolve the target spec".
- A conceptual heading is a noun phrase: "The exit gate".
- One h1 per document, and each level follows the one above it.
- Write headings in plain words: a heading is what a search matches and what a table of
  contents shows.
- Where a section introduces its subsections, refer to them as "the following sections".

## Text formatting

| what                                                                       | how                 |
| -------------------------------------------------------------------------- | ------------------- |
| filename, path, command, flag, class, method, field, value, console output | code font           |
| HTTP status code, environment variable, literal value                      | code font           |
| placeholder inside a command or path                                       | code font, ALL CAPS |
| UI element the reader clicks                                               | bold                |
| run-in heading at the start of a list item                                 | bold                |
| a term the first time you introduce it                                     | italic              |
| a link                                                                     | underline           |

## Lists and tables

- A numbered list carries a sequence, a bulleted list carries a set.
- Start every item the same way: all imperative, or all noun phrases.
- One idea per item. A bold run-in heading carries the label, and the rest of the line
  carries the explanation.
- Keep a table cell short enough to read across the row. A cell that wants a paragraph
  belongs in prose.
- Give every table a header row, and keep the columns in the order the reader needs them.

## Links

- Link text describes its destination: "the spec format", not the bare URL and not "here".
- Point at a file the reader will open locally with a code span:
  `plugins/bb/references/spec-state.md`.

## Numbers, dates, and units

- Spell out zero through nine in prose. Use numerals from 10 up, and for every version,
  count, and measurement.
- Write a date unambiguously: `2026-08-18`, or "August 18, 2026".
- Put a space between a number and its unit, and use the unit the tool prints.
- A number range keeps its en dash: `3–5 bullets`, `0.1–0.3`, `rungs 1–3`.

## Punctuation

- Serial comma in a list of three or more: "the finder, the verifier, and the gate".
- A colon introduces what explains the clause before it. A semicolon joins two clauses that
  could stand alone.
- Quotation marks go around a phrase quoted verbatim, with the source named.
- Dashes follow their own section above, in English and in Portuguese.

## Accessibility

- Every image carries alt text that says what the image shows.
- Name a UI control by its label, so a reader who cannot see the layout still finds it.
