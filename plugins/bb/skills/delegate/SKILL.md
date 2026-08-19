---
name: delegate
description: Runs a spec end to end. Selects an unfinished spec (`.bb/<slug>/spec.md`), builds every task and lands it (`/bb:implement` then `/bb:ship`), tracking the spec's `status`. `/bb:delegate <slug>` targets a named spec; bare `/bb:delegate` takes the oldest pending one. The single "run everything" verb. Use when the user says "delegate this", "run the task", "build and land the spec", "do it all", "delegate <slug>", or "run everything". Don't use it to align on an idea first (use /bb:spec) or to build without landing (use /bb:implement).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 2.6.0
---

# Delegate

Take a specced idea all the way: select the spec, build every task, and land it. That's the
`/bb:implement` → `/bb:ship` chain defined in one place. delegate is the single
"run everything" verb. It owns the spec's `status` lifecycle (contract in the
plugin-level `references/spec-state.md`); the `## Tasks` checkboxes inside it stay
`implement`'s.

## Prerequisites

Inside a git repository with a `.bb/` directory. If neither holds, report it
and stop.

## Workflow

1. **Resolve the target spec** per the spec-state contract (plugin-level
   `references/spec-state.md`).
   - **Named** (`/bb:delegate <slug>`): use `.bb/<slug>/spec.md`, falling back to
     `.bb/tasks/<slug>/spec.md` for a spec still on the older layout. If neither
     exists, report the error, list the available pending slugs, and stop.
   - **Bare** (`/bb:delegate`): scan `.bb/*/spec.md` and `.bb/tasks/*/spec.md`,
     read each frontmatter block, keep those with `status ∈ {pending, in-progress}`,
     and pick the smallest `created` (tie-break: slug alphabetical). The folder's
     `<slug>` is the key. A slug found under both paths is one candidate, read
     from `.bb/<slug>/`. A spec with no frontmatter counts as `pending` with
     unknown `created` (sorted last). If none qualify, report "no pending specs"
     and stop.
   - A spec already `done`: report it's done and ask whether to re-run. A `blocked`
     spec is skipped in bare selection and reported, not silently dropped: name it
     with the blocker its `## Open` carries, and where that blocker sends it. The
     spec's own gap is `/bb:spec`'s to close; a check the run had no permission to
     execute, a tree already red, and a stop on the way to landing all predate the
     spec and get fixed where they live, after which delegate runs again.

2. **Open the run, flip `status: in-progress`.** Edit the spec's frontmatter and
   commit that edit (conventional style; no AI attribution).

3. **Build: follow `/bb:implement`'s workflow (steps 1–7), then return here.** Load
   the spec, honor its reuse notes and `## Behavior` contract, build every
   unchecked task in the order its `dep:` fields imply, run each task's
   `verify:`, keep the project's checks green, and commit per task ticking its box. A spec
   written before the rename says `## behavior` and `dep:` and is read the same.
   **Do not run implement's step-8 ship hand-off**: delegate owns the transition to landing, so
   the chain lives here, not split across skills. If implement's **safety valve** fires
   (the spec was underspecified), stop: flip `status: blocked`, point back to
   `/bb:spec` to re-spec it, and exit. Do not improvise past the spec.

   Nothing about how to build is asked, at either end of the chain. The build is
   dispatched: implement's step 3 builds `args`, resolves and proves the script path in
   one `Bash` call, and invokes `Workflow` with `scriptPath`. Its result is the build
   report. The same three fallbacks apply here, each naming its reason in one line: a
   refused `scriptPath` becomes an inline `script` off the same file, and no `Workflow`
   tool, a `Bash` call that can't read the file, or both call shapes refused mean the
   tasks get built in this context instead. What the script does with the run is the
   plugin-level `references/build-tasks-workflow.md`.

   A non-null `stopped` (a stage-zero blocker such as a reuse note pointing at code
   that's gone, a check the run can't execute, or a tree already red; a red task; a
   lost agent; or a spec the agent found underspecified) lands the same place the
   safety valve does: flip `status: blocked`, exit without landing. What came back
   green is already committed and ticked.

   **A blocked run records why, not just that.** `status: blocked` alone tells the next
   run nothing, and by then the context that read the blocker is gone. Write it into the
   spec's own `## Open`, one line naming the blocker and what it needs, and commit that
   with the status flip; step 4 does the same for a stop on the way to landing, into the
   PR description when there is a PR. That's the line step 1 reads back when it skips a
   blocked spec.

4. **Land: follow `/bb:ship`'s workflow.** Green the project's checks, commit and
   land per ship's own destination logic; ship settles the destination, asking only
   on real doubt; delegate adds no destination logic of its own. **Ship doesn't
   review on the way in**: its post-landing gate offers `/bb:review` and the answer
   is the user's, so delegate adds no review logic of its own either. If ship hits an unrecoverable stop,
   flip `status: blocked`, and land the blocker where the run can be found again: the
   PR description when there is a PR, otherwise the spec's own `## Open` on the
   pushed branch. Report it, then exit.

5. **Close the run, flip `status: done`.** Once the chain lands cleanly, edit the
   frontmatter to `done` and commit. On a feature branch that commit only reaches the
   default branch when a human merges the PR, the same merge gate the `## Tasks`
   checkboxes already pass through; delegate never writes status to a protected branch
   directly.

6. **Report.** Name the slug, what landed (tasks, check results), and the destination
   (branch / PR URL / the hand-off command for a protected branch). A build that fell
   back to this context says so here too.

## Edge cases

| WHEN                                             | THEN                                                                                                                                            |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:delegate <slug>`, slug exists, not done     | run it end to end                                                                                                                               |
| `/bb:delegate <slug>`, slug not found            | report the error, list available pending slugs, stop                                                                                            |
| `/bb:delegate <slug>`, status `done`             | report it's done, ask whether to re-run                                                                                                         |
| bare `/bb:delegate`, one+ pending                | pick smallest `created` (tie-break slug alpha), run it                                                                                          |
| bare `/bb:delegate`, none pending                | report "no pending specs", stop                                                                                                                 |
| selected spec already `in-progress`              | resume: implement skips checked tasks; status stays `in-progress` until landing                                                                 |
| spec has no frontmatter                          | treat as `pending`, unknown `created` (sorts last); run it; `/bb:spec` backfills the block next time                                            |
| implement safety valve fires (underspecified)    | flip `status: blocked`, write the blocker into the spec's `## Open`, point back to `/bb:spec`, stop; do not improvise                           |
| the build stops (stage zero or a task)           | flip `status: blocked`, write the blocker into the spec's `## Open`, exit without landing                                                       |
| bare `/bb:delegate`, the oldest spec is blocked  | skipped, and reported with the blocker its `## Open` carries and where that blocker sends it                                                    |
| the build falls back to this context             | it runs the same way; the reason is named in one line, and again in step 6                                                                      |
| ship hits an unrecoverable stop / blocker        | flip `status: blocked`; write the blocker into the PR description, or into the spec's `## Open` when the destination has no PR; report it; exit |
| slug sits under both `.bb/` layouts              | one candidate; the `.bb/<slug>/` copy is the one read                                                                                           |
| spec only under `.bb/tasks/<slug>/`              | found by the second glob, run as usual                                                                                                          |
| not in a git repo / no `.bb/` dir in either root | report the error, stop                                                                                                                          |

The hard line holds throughout: delegate never merges, never approves, never
force-pushes; landing on a protected branch stays a human action.
