---
status: pending
created: 2026-09-11
slug: fonte-de-design-declarada
---

# the design front finds its source in any web repo

The `design` front of `/bb:review` resolves its source through a closed list of three
file formats and goes silent when none matches. A portability review of PR 25 read the
ladder against the web ecosystem and found a good share of ordinary web repos landing
in that silence: a theme declared in TypeScript, preprocessor variables, tokens a build
step generates, a design-system package inside the same workspace. The feature exists
and is invisible, with no signal that it was there to be had.

This spec changes what the plugin carries. Instead of a catalog of formats it carries
the **criterion** (the file the build consumes is the authority, whatever its format)
and a way to find it that presumes no layout; when nothing resolves it **asks**, one
question that works in any stack; and the repo can **declare its own source**, giving
`design` the same per-repo authority the `rules` front already has through the review
guide. The same lap closes the profile's design-tools question, which accepts only three
names and shows "not asked yet" for an answer it did not recognize.

## The ladder, rebuilt

Today's two rungs become four, resolved in order, every resolving rung kept:

0. **The repo's declaration**, in `CODE_REVIEW_GUIDE.md`. A repo that says which file is
   its design source settles the question for everyone who clones it, the way the same
   guide settles the rules, and the front gains the per-repo authority `rules` has. It
   is one row of the guide's `## Reference files` table, under the fixed pattern label
   `Design source`, naming the file, or `none` when the repo has no token source: a
   settled "none" is a declaration too, and it keeps the question from firing until the
   guide's update mode sees a token candidate and reopens it. `/bb:review-setup` writes
   the row, in setup and in update mode, after the maintainer names the file or says
   there is none; its discovery runs the same walk from the repo's UI entry points,
   since there is no diff to start from. The row's path is read under the repo root
   only: a path that escapes it, or names nothing, is absent with that drift line. A
   guide written before the row existed has no row and no drift, the way it has no rule
   it never had. `## Reference files` is a table people read today and no front parses,
   which is why the label is fixed: this row is the first one a front reads by its
   label. Several `Design source` rows (a workspace with two apps) are several sources,
   and a row's description may name the folder it governs; a row without one governs the
   whole repo, and disagreement is judged only between sources that govern the same
   changed file. A row naming a file that no longer exists is read as absent, and the
   review prints one drift line per stale row, the guide drift `rules` already fires for
   a citation whose path is gone.
1. **The file the changed UI consumes.** The criterion, not a list: the module the
   changed UI files take their colors, spacing and type from is the authority on what a
   token is, and a brand package nothing imports is not one. Resolution walks from the
   diff's UI files along their imports, transitively, until it reaches a module that
   defines values instead of consuming them, three hops at most; what the walk saw past
   the cap or could not prove are the question's candidates. It presumes nothing about
   the repo's layout. The formats the ladder used to enumerate become examples of the
   criterion, in example grammar: a `tokens.json` a build step reads, a stylesheet of
   CSS custom properties, a Tailwind theme, a theme object in TypeScript, a preprocessor
   variables file, a generated tokens module, a design-system package in the workspace,
   brisar's `tokens-brand.css` or its static variant's `styles.css`. Two modules
   resolving are two sources, and a value they disagree on is a finding, as the two
   rungs already are today.
2. **The branch's visual direction**, `.bb/<slug>/design.md`, unchanged.
3. **The question.** UI in the diff and nothing above resolving makes the probe ask, one
   `AskUserQuestion`: which file is this project's design source, with the candidates
   the walk saw but could not prove as options, and "there is none" as the last one. A
   picked file is the run's source and the front is offered on it. "None" leaves the
   front unavailable for the run, said in one line. Either answer lives for the run; the
   review's gate offers to keep it through `/bb:review-setup`, which is the guide's only
   writer, in update mode when the guide exists and in setup mode when the repo has
   none, where the row lands with the rest of the guide. A question declined or
   dismissed reads as "not now": the front is unavailable for the run, one line, nothing
   persisted.

The front's section opens by naming each source it judged against and the rung it came
from, the answer to the question included; when the front does not run, the probe's one
line says why (no source, a declared `none`, a declined question), so a run's silence
and a run's source are both readable from the report.

In external-PR mode rung 0 reads the guide the mode already fetches, the walk runs
through the contents API from the PR's changed files, the question still fires, and
nothing is persisted: the repo is not yours to write. In surface scope the ladder is the
same and the walk starts from the surface's files. A run with no one to ask (a review
inside `/bb:implement`'s scope, which asks no fronts question) skips rung 3: the front
is unavailable, one line names what would create a source, as today.

## The profile's free answer

`/bb:profile`'s design-tools question keeps its three options and gains a rule for the
free text the question tool always offers. What the person types is their answer: it is
stored in `design_tools` lowercased and trimmed, split on commas when it names several
tools, a known name in any case folding to its key (the session writer folds case again
on read, so a hand-edited `FIGMA` still renders as Figma), and the writer renders an
unknown key capitalized ("They design in Sketch; bb has no canvas path for it, so a
design journey leans on code and the in-conversation preview"). Step 3 shows it as the
design answer instead of "not asked yet". brisar's medium question names such a tool
once in its intro line and offers no option for it, the same shape it already has for a
known tool whose connection is absent. Empty or whitespace text reads as nothing
checked.

## Decisions

- The plugin carries the criterion and the walk, never a layout: the ladder's formats
  are examples, and adding one is editing an example, not a rule.
- Rung 0 is the repo's declaration in `CODE_REVIEW_GUIDE.md`, one `Design source` row of
  `## Reference files`, written only by `/bb:review-setup`; `/bb:review` reads it and
  never writes it. Persisting an answered question is a gate offer, not a side effect of
  the review.
- A declared source and a module the walk resolves are both sources, and a value they
  disagree on is a finding: UI consuming values from outside the declared source is
  what the front is there to see.
- The question fires only with UI in the diff (or a surface) and every rung empty; a
  diff with no UI keeps today's silence. "None" is an answer like a file: the gate offers
  to declare it, and a declared `none` silences the question until the guide's update
  mode reopens it.
- `design_tools` accepts any string; the three known keys keep their journey paths, an
  unknown one is rendered and named, never dropped and never mapped to "none".
- `medium_default` keeps its closed vocabulary: its values are bb's own mediums.
- The `frente-de-design` and `design-no-perfil` specs stay the records of their laps;
  this spec supersedes the former's ladder and the latter's closed `design_tools`
  vocabulary, and the build reads both here.

## Behavior

Happy path, once built:

1. The probe sees UI in the diff and a declaration in the repo: rung 0 resolves and
   the front is offered, the report citing the declared file as its source.
2. No declaration: the resolution walks from the changed UI files to the module they
   take their values from, and that module is the source whatever its format.
3. The branch's `design.md` supplements the source as today.
4. Nothing resolves with UI in the diff: one question lists the candidates and "none";
   a picked file is the run's source and the front is offered on it.
5. `/bb:review-setup` writes the declaration after the maintainer names the file, in
   setup mode and in update mode, and the next review reads it at rung 0.
6. After a review that asked and got a file, the gate offers `/bb:review-setup` to keep
   the answer.
7. The profile's design question receives a tool outside the three: it is stored,
   rendered in the profile block, and shown by step 3 as the answer it is.
8. brisar's medium question meets a stored tool bb has no path for: named once in the
   intro line, no option, the lean falls to the next signal.

| WHEN                                                      | THEN                                                                                         |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| the diff touches no UI file                               | no probe, no question, no mention, as today                                                  |
| the declaration names a file that does not exist          | read as absent, one drift line names it, the ladder continues at rung 1                      |
| the walk resolves two modules                             | both are sources; a value they disagree on is a finding                                      |
| the person answers "none" to the question                 | the front is unavailable for the run, one line; the gate offers to declare it                |
| the guide declares `none` and the diff touches UI         | no question, no front; the probe's line says the guide declares none; update mode reopens it |
| external PR, nothing resolves                             | the question fires for the run; nothing is written to the foreign repo                       |
| surface scope, nothing resolves                           | the same question, candidates drawn from the surface's files                                 |
| the guide has no declaration and rung 1 resolves          | no question; the gate offers `/bb:review-setup` to declare what resolved                     |
| `design_tools` holds `["sketch"]`                         | the profile block renders Sketch as unsupported; step 3 shows the answer                     |
| the free text is a known tool in another case (`FIGMA`)   | it folds to `figma` and keeps that tool's journey path                                       |
| the free text is empty or whitespace                      | reads as nothing checked: `design_tools: []`                                                 |
| a hand-edited config holds a non-string in `design_tools` | the hook skips the value and renders the rest, as it does today                              |
| no one can be asked (implement's review scope)            | rung 3 is skipped; the front is unavailable, one line names the remedy                       |
| the walk passes three hops without a defining module      | the modules it saw are the question's candidates, none is assumed                            |
| the guide carries several `Design source` rows            | each governs the folder its description names, or the repo; disagreement judged per file     |
| external PR whose fetched guide declares a source         | rung 0 resolves from that guide; nothing is written back                                     |
| the question is declined or dismissed                     | read as "not now": front unavailable for the run, one line, nothing persisted                |
| no guide in the repo and the person keeps the answer      | `/bb:review-setup` runs setup mode and the row lands with the rest of the guide              |
| the declared path escapes the repo root                   | read as absent, with the drift line; nothing outside the root is opened                      |
| a guide written before the row existed                    | rung 0 is absent and no drift line fires; the ladder continues at rung 1                     |
| the free text names several tools (`sketch, penpot`)      | split on commas, each trimmed and lowercased, each stored                                    |

## Metric

- Metric: the share of `/bb:review` runs with UI in the diff where the design front is
  offered or asks, never silent, read by hand from the review reports over the dogfood
  window (operational measure; internal tooling).
- Baseline: skipped: not-instrumented
- Target: 100% of such runs over the first five landings after this ships, within 6
  weeks of landing (the author's estimate, to harden at this spec's gate).
- Events: none; internal tooling, and the review reports themselves are the measurement
  surface.

## Tasks

### The front stops guessing

- [ ] **1. Criterion, walk and question in the front**: `front-design.md` §1 rebuilt
      as the four rungs (criterion with example grammar, the import walk, the question,
      the external-PR and surface variants); `fronts.md`'s probe row and no-source line
      become the question; the review `SKILL.md` edge row for "design review asked and
      no design source" points at it; `mode-external-pr.md`'s gather step reads rung 0 from the fetched guide and walks imports through the contents API → behaviors 2, 3, 4 · dep: — · verify: reading, plus one
      dry run of the probe over a diff with UI and no source (the question fires)

### The repo declares

- [ ] **2. The declaration in the guide's writer**: `/bb:review-setup` gains the design
      source in discovery (candidates from the same walk), in the interview (the
      maintainer names the file), in `guide-template.md` and in `update-delta.md`;
      `front-design.md` reads it at rung 0 with the stale-file drift line → behaviors
      1, 5 · dep: 1 · verify: reading, plus this repo's guide regenerated in update
      mode carrying the declaration
- [ ] **3. The gate keeps the answer**: the review's gate offers `/bb:review-setup` after
      a run that asked and got a file, and after a run where rung 1 resolved with no
      declaration → behavior 6 · dep: 2 · verify: reading

### The profile hears the answer

- [ ] **4. Free text in the design question**: `profile/SKILL.md` step 5 and step 3, the
      edge table, `bb-config.md`'s `design_tools` contract (any string, lowercased, known
      keys folded), `sync_instructions.py`'s `design_line` rendering unknown names →
      behavior 7 · dep: — · verify: command (the hook run against configs holding
      `["sketch"]`, `["FIGMA"]`, `[""]` and `[3]`: the rendered line matches the table)
- [ ] **5. brisar names the unsupported tool**: `phase-medium.md` Step 1's intro line
      covers a `design_tools` entry with no path, same shape as the absent connection
      → behavior 8 · dep: 4 · verify: reading

## Out of scope

- A layout catalog inside the plugin, however long: the walk replaces it; _revisit_
  never, the criterion is the design.
- Reading a token source that only exists at runtime (a theme fetched from an API): the
  front is static; _revisit_ with the rendered-page checks of surface scope.
- Editing the `frente-de-design` spec or PR 25's description; the former is a record of
  its lap, the latter is the author's text.
- A journey path in `/bb:brisar` for a tool outside Figma, Paper and Pencil (a Sketch or
  Penpot reader): the profile stores the answer, the journey does not gain a medium;
  _revisit_ when a connector exists.
- Widening `medium_default`'s vocabulary.

## Open

Nothing.
