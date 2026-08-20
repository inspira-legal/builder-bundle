---
status: done
created: 2026-08-20
slug: records-out-of-the-contract
---

# one skill, one doc: the records leave the contract

`spec.md` is the contract, and today three skills write into it. `/bb:discover` seeds
`## Problem` / `## Hypothesis` / `## Fit` / `## Cuts` inside it, `/bb:spec` builds the
rest of the file around them, and `/bb:brisar` closes its journey with a `handoff.md`
that re-renders half of what the spec already says, plus a `## Spec delta` section
telling somebody to go edit the spec by hand. Three writers on one document, and the
same hierarchy-and-states fact written in three places: `design.md`, then
`develop-notes.md`'s `states_covered[]`, then the handoff.

The rule that fixes it is one sentence. **Every skill writes its own record, and
`spec.md` has exactly one writer.** `/bb:discover` writes `discovery.md`, `/bb:brisar`
writes `design.md`, `/bb:spec` writes `spec.md` and reads the other two as the intent
this work serves. The contract points at the records by path; it never copies their
prose.

There is a second thing wrong, and it is why `handoff.md` existed at all. Brisar's role
is to design the journey and prototype it, not to code the solution. The current files
say otherwise: `phase-develop.md` opens with "high-fidelity surface construction",
`develop-modes.md` sends the `embedded` hosting to write `src/pages/<surface>.tsx`
inside the real app, and `HANDOFF-DEV.md` is the artifact of a skill that believes it
finished something engineering will now continue. A skill that hands work to
engineering needs a handoff document. A skill that designs a journey needs a spec,
which is why Deliver stops suggesting `/bb:spec` and starts invoking it.

## The three documents

```
.bb/<slug>/
├── discovery.md   # the framing, /bb:discover
├── spec.md        # the contract, /bb:spec, single writer
├── design.md      # the journey and the prototype record, /bb:brisar
└── prototype/     # the clickable artifact, /bb:brisar Develop
```

Everything bb writes lives under `.bb/<slug>/`. Nothing lands in the cwd, in a
`<slug>/` sibling, or in a `design-context/` at the app root. The prototype is the only
non-document member, and it is there because it is brisar's output, not the app's code.

`design.md` absorbs six of today's members: `brief-design.md`, `design.md` and its
`design/` folder variant, `develop-notes.md`, `design-review.md`,
`accessibility-checklist.md` and `handoff.md`. The name collision resolves itself,
because the per-surface `design.md` stops being a file and becomes a section. Sections
replace rather than accumulate: `.bb/` is tracked in git, so the history of rounds is
`git log`, and the document carries the current state.

## Pointing instead of copying

The guard against rebuilding `handoff.md` under a new name is mechanical. When the spec
needs a fact that lives in a record, it cites the path and the section, and the reader
opens it. `## Cuts` is read from `discovery.md` by `/bb:review`'s front contract and by
`/bb:spec`; `## Hypothesis` is read from `discovery.md` by export mode's trio rule; the
surfaces and their states are read from `design.md`. Where a record and the contract
disagree, `spec.md` wins, and the record is corrected by its own writer on the next
round.

## Decisions

- **`/bb:discover` writes `.bb/<slug>/discovery.md`**, with its own frontmatter and the
  four sections it frames. It stops creating or touching `spec.md`.
- **`/bb:spec` is the only writer of `spec.md`.** It reads `discovery.md` and
  `design.md` as upstream when they exist, echoes the framing in one line, and drafts
  on top. No upstream is still fine.
- **`/bb:brisar` writes exactly one document, `.bb/<slug>/design.md`**, covering the
  research, the chosen direction, the journey's surfaces with their hierarchy and
  states, the token delta, what was built, the design review and the accessibility
  audit. Its frontmatter carries the journey's `status`, `phase`, `round` and the
  surfaces list, which is what `brief-design.md` carries today.
- **Brisar prototypes; it does not code the solution.** Develop delivers a clickable
  prototype: the journey's screens navigating between each other, each screen's states,
  the DS tokens applied. No real data, no integration, no error handling, no tests.
  Product code is `/bb:implement`'s job, from the spec.
- **The `embedded` hosting dies.** Every prototype is born in `.bb/<slug>/prototype/`,
  React or static HTML, with its `tokens.css` beside the `.html` because the `<link>`
  has to resolve. Brisar never writes inside the app.
- **`design-context/` dies.** Develop reads the design system from
  `${CLAUDE_PLUGIN_ROOT}/skills/brisar/references/ds/`, with `BRISAR_DS_PATH` still
  overriding it. Only what this project changed or invented is written, as a
  token-delta section of `design.md`. The per-project synthesis was a cache that never
  revalidated.
- **`handoff.md` and `HANDOFF-DEV.md` die.** Deliver's gate **invokes** `/bb:spec`, the
  way spec's gate invokes implement and delegate. This is the one named exception to
  brisar rule 11 ("suggest, never auto-invoke"), and it is recorded as such next to the
  rule, with the bootstrap protocol as its precedent.
- **The `## Spec delta` section dies with the handoff.** A divergence the invoked
  `/bb:spec` turns into a decision does not need to be written down twice on the way.
- **Reversal has one shape for all three documents.** `spec.md` wins on disagreement,
  and the record's own writer registers the reversal on its next round ("revokes D4,
  per the spec"). The rule exists today for `brief-design.md` only; it moves to
  `references/spec-state.md` and covers the three.
- **No migration and no compat layer.** The 11 folders in `.bb/` carry only `spec.md`,
  none of them carries the discover sections, and no brisar artifact exists on disk.
  There is nothing to convert.
- **The lint gains the moved names as dead names.** `## Problem`, `## Hypothesis`,
  `## Fit` and `## Cuts` inside a `spec.md` fire `E003` pointing at `discovery.md`,
  which is what stops the copy being reborn.
- **`/bb:review` never reviews `.bb/`.** It reviews code and PRs, so the whole
  folder leaves the diff every front reads: the three documents and `prototype/`
  alike. Reading `spec.md`'s `## Behavior` and `discovery.md`'s `## Cuts` as the
  **ruler** is a different act from producing findings about them, and the `contract`
  front keeps doing it. Today nothing is excluded, and this change would put three
  documents plus a prototype folder into every diff.

## Behavior

Happy path:

1. `/bb:discover` closes the first diamond and writes `.bb/<slug>/discovery.md`. No
   `spec.md` is created. Its gate suggests `/bb:spec` or `/bb:brisar`.
2. `/bb:spec` resolves `.bb/<slug>/`, reads `discovery.md` and `design.md` when they
   exist, echoes the framing in one line, runs its loop, and writes `spec.md` with the
   `status: pending` block.
3. `/bb:brisar` runs its phases writing into the single `design.md`, updating `phase:`
   in the frontmatter as it advances.
4. Develop reads the DS from the plugin and builds the clickable prototype into
   `.bb/<slug>/prototype/`, recording the artifact's path in `design.md`.
5. Deliver runs the design review and the accessibility audit into `design.md`, then
   its gate invokes `/bb:spec`, which reads both records and writes the contract.
6. `/bb:review` reads `## Cuts` from `discovery.md` as the ruler, and reviews only the
   code in the diff: `.bb/` is excluded from every front's scope.
7. `/bb:spec` export mode reads `## Hypothesis` from `discovery.md` for the trio rule.

| #   | WHEN                                                                   | THEN                                                                                      |
| --- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| E1  | there is no `discovery.md`                                             | `/bb:spec` drafts from the one-liner and does not ask for one                             |
| E2  | there is no `design.md`                                                | same: the spec is drafted without it, no prompt                                           |
| E3  | `design.md` asserts a decision the spec reversed                       | `spec.md` wins; brisar registers the reversal in `design.md` on its next round            |
| E4  | Deliver invokes `/bb:spec` and `spec.md` already exists                | spec loops on top and rewrites it; no `-2` suffix, because it is the same idea            |
| E5  | brisar runs on a slug with no `discovery.md`                           | Research step 0 states which upstream is missing and continues                            |
| E6  | the medium is `paper`, `figma` or `pencil`                             | no `prototype/` is created; `design.md` names the file, page and artboard                 |
| E7  | the builder asks brisar to write into the app's `src/`                 | brisar answers that it prototypes, and names the path: `/bb:spec` then `/bb:implement`    |
| E8  | `.bb/<slug>/` is a symlink into a canonical store                      | `prototype/` travels with the documents to the canonical target                           |
| E9  | the folder still holds `brief-design.md`, `handoff.md` or the rest     | nothing reads them; the folder is treated as if only the three documents exist            |
| E10 | `brand.workflow == framer-harpa`                                       | the harpa context becomes a section of `design.md`, not a file in the cwd                 |
| E11 | a surface's state is not built                                         | `design.md` records it as not built; the prototype does not fake it                       |
| E12 | `BRISAR_DS_PATH` points somewhere unreadable                           | brisar falls back to the plugin's `references/ds/` and says so once                       |
| E13 | a `spec.md` carries `## Problem`, `## Hypothesis`, `## Fit`, `## Cuts` | `lint_spec.py` fires `E003` naming `discovery.md` as the section's home                   |
| E14 | the diff touches `.bb/<slug>/` documents or `prototype/`               | those paths leave every front's scope; the `contract` front still reads them as the ruler |
| E15 | the diff is only `.bb/`                                                | `/bb:review` says there is no code to review and stops, instead of running empty fronts   |

## Tasks

- [x] **1. `discovery.md`**: `/bb:discover` writes its own document, with frontmatter,
      and stops touching `spec.md`; its gate wording follows
      → behaviors 1, E1, E5 · dep: — · verify: reading `skills/discover/`
- [x] **2. Two upstreams in spec**: `skills/spec/SKILL.md:26` reads `discovery.md` and
      `design.md` instead of in-file sections, and the echo names them
      → behaviors 2, E1, E2, E3 · dep: 1 · verify: reading
- [x] **3. One `design.md`**: the six brisar members collapse into one document with
      sections that replace, the frontmatter moves to it, every phase reference points
      at it
      → behaviors 3, E3, E6, E11 · dep: — · verify: `grep -rn "brief-design\|develop-notes\|design-review\|accessibility-checklist"` is empty
- [x] **4. Prototype in `.bb/`, DS from the plugin**: `embedded` and `design-context/`
      are removed, the prototype path becomes `.bb/<slug>/prototype/`, Develop's
      opening says prototype instead of high-fidelity surface construction
      → behaviors 4, E7, E8, E12 · dep: 3 · verify: `grep -rn "design-context"` is empty
- [x] **5. Deliver invokes spec**: `handoff.md`, `HANDOFF-DEV.md` and `## Spec delta`
      are deleted, the gate invokes `/bb:spec`, rule 11 gains its named exception
      → behaviors 5, E4 · dep: 3 · verify: `grep -rn "HANDOFF-DEV"` is empty
- [x] **6. The framer path lands in `.bb/`**: `phase-framer-handoff.md` writes a
      section of `design.md` instead of a file in the cwd
      → behavior E10 · dep: 3 · verify: reading
- [x] **7. `spec-state.md` rewritten**: the tree, the frontmatter schemas, the reversal
      rule for the three documents, and the symlink obligation covering `prototype/`
      → behaviors 1, 3, 4, E8, E9 · dep: 1, 3, 4 · verify: reading
- [x] **8. The outside readers repointed**: `review/references/front-contract.md:20`,
      `spec/references/export-spec.md:18`, `spec/references/spec-format.md:105`, and
      `lint_spec.py`'s `DEAD_SECTIONS` gaining the four moved names
      → behaviors 6, 7, E13 · dep: 1 · verify: CI
- [x] **9. `.bb/` out of review's scope**: the exclusion lands where the mode is
      resolved (`review/SKILL.md` step 1) and where the diff reaches the finders
      (`review/references/fronts.md`), with the ruler-not-target distinction stated
      once in `front-contract.md`
      → behaviors 6, E14, E15 · dep: — · verify: reading

## Out of scope

- Migrating the 11 existing `.bb/` folders. Verified on disk: each holds only
  `spec.md`, none carries the discover sections, no brisar artifact exists.
- A compat layer that reads the old member names.
- A lint for `discovery.md` and `design.md`. Only `spec.md` has one today (_revisit_).
- The `.bb/tasks/<slug>/` legacy path handling in `spec-state.md`, a separate question
  from where the records live.
- `/bb:implement` and `/bb:ship`. They keep reading `spec.md` and nothing changes for
  them.
- The fidelity ladder in `phase-1-intake.md` (low-fi / mid-fi / hi-fi). The ceiling
  moves; the ladder inside it stays.

## Open

Nothing.
