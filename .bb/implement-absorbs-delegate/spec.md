---
status: done
created: 2026-08-27
slug: implement-absorbs-delegate
---

# implement absorbs delegate, and gains a scope of its own

`/bb:delegate` has no build loop. Its step 3 says "follow `/bb:implement`'s workflow,
steps 1 to 7, then return here", so what the second verb actually owns is three things:
a spec selection rule, the `status` lifecycle, and chaining into `/bb:ship` without
asking. Everything else in its 115 lines is implement's, re-narrated well enough to drift.

The cost of the split is visible outside the two files. `build-tasks-workflow.md` closes
with a paragraph explaining that implement goes to its step 8 and delegate goes to ship;
`handoff-gate.md` opens a named exception to "never auto-invoke" for delegate;
`operating-context.md` carries that exception into everyone's
`~/.claude/BUILDER-BUNDLE.md`; `spec-state.md` assigns the lifecycle to a skill that only
borrows the build. Five files maintaining a distinction worth three bullets.

So delegate goes, and implement asks instead. One question at the start settles what the
run covers, and the run covers it: build, or build and review, or build and ship, or all
three. That question is also what replaces delegate's whole reason to exist, and it makes
a capability the bundle never had reachable, reviewing the change **before** it ships
rather than after.

Success: one verb in the Construir trilha builds a spec, and how far it goes is a choice
made once, at the start, in the same place every time.

## What this reopens, on purpose

`.bb/no-opt-out/spec.md` deleted a question from the start of implement, and stated its
success as "`/bb:implement` and `/bb:delegate` reach the build with nothing asked". This
change puts a question back there. It is a different question: no-opt-out removed **how
to build**, which had one right answer and was asked anyway; what returns is **how far
this run goes**, which has no default the skill can derive. The build itself still reaches
the workflow with nothing asked, and the CHANGELOG records the partial reversal in those
terms.

## Why review runs before the ship and not after

Today the only review the bundle offers on a build is ship's step 4, after the landing.
On the PR path that means the PR is opened from unreviewed code and the fixes arrive as
follow-up commits on top of it. Running the same fronts on the branch before ship starts
puts the fixes in the same set of commits the tasks produced, and the PR opens from code
that was already read. Ship's post-landing offer then has nothing left to add, which is
why it goes.

## Decisions

- **`/bb:delegate` is deleted**, skill folder and all. The CHANGELOG carries the
  migration: `/bb:delegate <slug>` becomes `/bb:implement <slug>` with review and ship
  picked at the scope question. No stub and no alias; two names for one thing is the
  complaint this change answers.
- **Reuse: the selection rule is already code.** `plugins/bb/scripts/scan_specs.py` resolves
  the `.bb/` root, reads every `spec.md` frontmatter block and prints `selected` alongside
  `pending_slugs`. Implement calls it with `--slug` for a named spec and reads `selected`
  for the sweep, the way delegate's step 1 does today; preferring the session's own spec is
  a layer above it, since the script has no notion of a session. `resolve_checks.py` stays
  implement's step 4 and the source of `args.checks`, and `preflight.py` stays ship's
  Prerequisites and Step 0. None of the three changes shape.
- **Implement asks the scope once, as four exclusive options**, not as checkboxes:
  build only, build and review, build and ship, build and review and ship.
  `AskUserQuestion` cannot pre-check a `multiSelect` option, and the pre-filled default is
  the point, so the default is expressed as the option that leads and carries
  `(Recommended)`.
- **The invocation sets which option leads.** "run everything", "build and ship it",
  "delegate this" lead with all three; "implement the spec", "build the tasks" lead with
  build only. The question appears either way and one keystroke confirms it.
- **`/bb:spec`'s exit gate is the scope answer.** Its options become Build, Build and
  ship, Build review and ship, Stop here. Implement invoked from there does not ask again;
  invoked by command, it asks.
- **Implement owns the `status` lifecycle**, the whole of what `spec-state.md` assigned to
  delegate: `in-progress` on opening, `blocked` on any stop, `done` after the landing. The
  `## Tasks` checkboxes were already implement's.
- **`done` is flipped when the landing completes, not when ship's run ends.** The PR path
  ends resident, watching the PR, so a flip that waited for ship to return would never
  happen. The flip goes right after the PR is open and its checks are handled, which is
  where ship's step 4 used to sit.
- **Bare `/bb:implement` prefers the spec this session is on**: the one just written by
  `/bb:spec`, or the one already being built. With nothing in context it falls back to
  delegate's sweep, smallest `created` among `pending` and `in-progress`, slug alphabetical
  to break ties.
- **The selection rules come over unchanged otherwise**: a named slug that does not exist
  reports and lists the pending ones, a `done` spec asks before re-running, a `blocked`
  spec is skipped in the sweep and reported with the blocker its `## Open` carries.
- **Review and ship run in the main context after the workflow returns**, not as phases of
  `build-tasks.js`. A `Workflow` cannot ask anything, and ship's destination logic and its
  PR watch both need to. The scope answer is the authorization; their own gates are what it
  replaces.
- **The chained review runs at standard depth over every available front**, with no fronts
  question. Its `threads` and `ci` fronts drop out on their own, because the availability
  probe finds no PR before the ship. A deep review stays `/bb:review deep`, invoked
  separately.
- **The chained review applies every CONFIRMED finding and reports every PLAUSIBLE one.**
  There is no PR to comment on before the ship, and no item-by-item curation: the
  independent verifier's verdict is what decides. The report names both sets before the
  ship starts.
- **Ship's step 4 is deleted**, for the chained run and for `/bb:ship` on its own. Ship
  becomes terminal: it reports what shipped and stops. `handoff-gate.md`'s journey map
  loses the `ship → review` edge and ship joins the skills with no gate.
- **Ship's step 1 is untouched.** It settles the destination by signal and asks only on
  real doubt; implement adds no destination logic, exactly as delegate added none.
- **The final handoff gate survives for a run that did not include ship**, offering ship
  against stopping. The tree is green and committed by then, so it is a different question
  from the one asked at the start, not the same one repeated.
- **A run with review but no ship** stops at that same gate, after the findings are applied
  and reported.
- **A stop anywhere flips `status: blocked`** and writes the blocker where the run can be
  found again, the PR description when there is a PR and the spec's `## Open` otherwise.
  The routes are unchanged: the spec's own gap back to `/bb:spec`, a stage-zero blocker to
  the allowlist or to the red that predates the build, a red task to the task.
- **A run that did not include ship leaves `status: done`.** Nothing landed, and
  `done` means the chain landed.
- **Everything this change writes or rewrites calls the action ship**, not land. Both words
  are in the repo today for one action, which is what the one-name-per-thing rule in
  `doc-style.md` exists to prevent.
- **Versions**: `plugin.json` `2.19.0` to `3.0.0` and its skill count 16 to 15;
  `implement` `2.6.0` to `3.0.0`; `ship` `3.1.0` to `4.0.0`; `spec` `2.3.0` to `2.4.0`.

## Behavior

1. `/bb:implement` resolves the spec: a named slug first, then the one this session is
   already on, then the sweep over `.bb/*/spec.md`.
2. It asks the scope once, four exclusive options, the leading one set by how it was
   invoked. A pick carried over from `/bb:spec`'s gate answers it and nothing is asked.
3. It flips `status: done` and commits that edit.
4. It loads the spec, confirms the reuse notes, builds `args` and dispatches
   `build-tasks.js`, all per `build-tasks-workflow.md`, unchanged.
5. Scope included review: `/bb:review` runs over the branch at standard depth across every
   available front, with no fronts question and no gate of its own.
6. It applies every CONFIRMED finding, reports every PLAUSIBLE one, keeps the project's
   checks green and commits.
7. Scope included ship: `/bb:ship` runs, settling the destination by its own step 1.
8. Once the landing completes, implement flips `status: done` and commits, before the PR
   watch settles in.
9. Scope did not include ship: the run ends at the handoff gate offering ship against
   stopping, and `status` stays `in-progress`.
10. Any stop flips `status: blocked`, writes the blocker where the run can be found, and
    exits without going further down the chain.
11. `/bb:ship` invoked on its own reports what shipped and stops, offering no review.
12. Every file this change rewrites names the action ship.

| WHEN                                           | THEN                                                      |
| ---------------------------------------------- | --------------------------------------------------------- |
| `/bb:implement <slug>`, slug exists, not done  | run it at the scope the question settles                  |
| `/bb:implement <slug>`, slug not found         | report it, list the pending slugs, stop                   |
| `/bb:implement <slug>`, status `done`          | report it, ask whether to re-run                          |
| bare, this session already has a spec          | that one, without a sweep                                 |
| bare, nothing in context, one or more pending  | smallest `created`, slug alphabetical to break ties       |
| bare, nothing in context, none pending         | report "no pending specs", stop                           |
| bare, the oldest spec is `blocked`             | skipped, reported with the blocker from its `## Open`     |
| spec has no frontmatter                        | treat as `pending`, unknown `created`, sorted last        |
| invoked as "run everything"                    | the question leads with build, review and ship            |
| invoked as "implement the spec"                | the question leads with build only                        |
| invoked from `/bb:spec`'s gate                 | the gate's pick is the scope, nothing is asked            |
| scope is build only, every task green          | gate offers ship, `status` stays `in-progress`            |
| scope is build and review, every task green    | findings applied, then the same gate                      |
| every task already ticked                      | nothing dispatched, the run goes to its scope's next step |
| the build stops for any reason                 | `status: blocked`, no review and no ship                  |
| review finds nothing                           | say so in one line and go on to the ship                  |
| a CONFIRMED fix turns a check red              | fixed before the ship, as the build step already does     |
| review runs and there is no PR yet             | the probe drops `threads` and `ci` on its own             |
| ship hits an unrecoverable stop                | `status: blocked`, blocker into the PR or `## Open`       |
| ship lands on the PR path                      | `done` is flipped before the watch settles in             |
| ship lands on a protected branch               | ship hands over the command; `done` waits for the push    |
| `/bb:ship` invoked on its own                  | it reports and stops, with no review offered              |
| someone types `/bb:delegate`                   | no such skill; the CHANGELOG names the replacement        |
| not in a git repo, or no `.bb/` in either root | report it, stop                                           |

## Tasks

- [x] **1. implement becomes the one verb**: `SKILL.md` rewritten end to end, the
      `description` taking delegate's trigger phrases, prerequisites carrying the selection
      rules off `scan_specs.py`, a new scope question before the build, the `status` flips
      around it, and the review and ship steps after the workflow returns; the final gate
      kept for a run that did not include ship
      → behaviors 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 · dep: — · verify: reading
- [x] **2. delegate deleted, its contract reassigned**: `plugins/bb/skills/delegate/`
      removed, and `references/spec-state.md`, `scripts/scan_specs.py`'s docstring and
      `scripts/preflight.py`'s comment moved to naming `/bb:implement` as the owner of the
      `status` lifecycle and as the caller that selects on `spec.md`'s block
      → behaviors 3, 8, 10 · dep: 1 · verify: reading
- [x] **3. ship becomes terminal**: step 4 deleted with its PR-path paragraph, the
      `description` no longer promising a review after the landing, and `land` renamed to
      `ship` through `SKILL.md`, including `references/land-*.md` renamed to `ship-*.md`
      and the paths that point at them
      → behaviors 7, 11, 12 · dep: — · verify: reading
- [x] **4. the spec gate carries the scope**: `/bb:spec`'s exit gate rewritten to the four
      options, its lifecycle line pointing at implement, and the two hand-off bullets
      rewritten for one verb
      → behaviors 2, 9 · dep: 1 · verify: reading
- [x] **5. the shared references**: `build-tasks-workflow.md` losing its delegate branch,
      `handoff-gate.md` losing the delegate exception and the `ship → review` edge and
      gaining the new spec gate example, and `hooks/operating-context.md` losing the
      delegate line
      → behaviors 2, 5, 7, 11 · dep: 1, 3 · verify: reading
- [x] **6. docs, versions and the record**: `README.md` (the delegate row out, implement
      and ship rewritten), `.claude/CLAUDE.md` (the trilha list, the skill count, the
      lifecycle owner), `brisar/references/phase-deliver.md`'s reader column,
      `plugin.json` at `3.0.0` with 15 skills, the three skill versions, and a CHANGELOG
      entry naming what it reverses from `no-opt-out` and how to migrate a
      `/bb:delegate` call
      → behaviors 11, 12 · dep: 1, 2, 3, 4, 5 · verify: CI

## Out of scope

- Running review or ship as phases inside `build-tasks.js`. Neither survives a runtime that
  cannot ask a question (_revisit_).
- A second review pass after the PR is open. One pass, before the ship.
- Deep depth in the chained review. `/bb:review deep` stays its own invocation (_revisit_).
- A `--review` / `--ship` argument on the command, alongside the question (_revisit_).
- A deprecation stub or alias for `/bb:delegate`.
- Any change to `build-tasks.js`, or to how the build is dispatched.
- Renaming `land` to `ship` inside `CHANGELOG.md` history or inside the `done` specs in
  `.bb/`. Both describe what was built at the time.

## Open

- Nothing.
