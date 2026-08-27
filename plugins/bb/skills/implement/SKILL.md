---
name: implement
description: Runs a spec (`.bb/<slug>/spec.md`) as far as this run is meant to go. Selects the spec, asks once whether the run is build, build and review, build and ship, or all three, builds every task, tracks the spec's `status`, and chains into `/bb:review` and `/bb:ship` when the scope says so. `/bb:implement <slug>` targets a named spec; bare `/bb:implement` takes the spec this session is on, or the oldest pending one. The single verb of the Construir trilha. Use when the user says "implement the spec", "build the tasks", "build it", "run the task", "build and ship the spec", "do it all", "run everything", or right after /bb:spec. Don't use it to align on an idea first (use /bb:spec) or to land a branch that is already built (use /bb:ship).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 3.0.0
---

# Implement

Take a specced idea as far as this run is meant to go. implement selects the spec, builds every task against it, and then follows the scope it settled once at the start: review the branch, ship it, both, or neither. It owns the spec's `status` lifecycle (contract in the plugin-level `references/spec-state.md`) and the `## Tasks` checkboxes inside it.

## Prerequisites

Inside a git repository with a `.bb/` directory, and a validated spec with a `## Tasks` checklist at `.bb/<slug>/spec.md` (same contract). If there's no spec for this work, stop and suggest `/bb:spec` first. Implementing without alignment is exactly what the spec prevents.

## Workflow

`<plugin-root>` is this plugin's own directory, and the plugin-root `references/plugin-root.md` is where the rule that resolves it lives.

1. **Resolve the target spec** per the spec-state contract. `python3 <plugin-root>/scripts/scan_specs.py` is that contract's selection rule as code: it resolves the `.bb/` root, reads every `spec.md` frontmatter block, and prints each spec's `status`, `created`, unticked task count and, for a blocked one, the line its `## Open` carries, alongside the `selected` the rule picks and `pending_slugs` for the report.
   - **Named** (`/bb:implement <slug>`): pass `--slug <slug>`. `found: false` means report the error, list `pending_slugs`, and stop.
   - **Bare** (`/bb:implement`): **prefer the spec this session is already on**, the one `/bb:spec` just wrote or the one already being built, and confirm it against the scan. The script knows nothing about the session, so this preference is read here. With nothing in context, take `selected`; null means report "no pending specs" and stop.
   - A spec already `done`: report it's done and ask whether to re-run. A `blocked` spec is skipped in bare selection and reported, not silently dropped: name it with the blocker its `## Open` carries, and where that blocker sends it. The spec's own gap is `/bb:spec`'s to close; a check the run had no permission to execute, a tree already red, and a stop on the way to the ship all predate the spec and get fixed where they live, after which implement runs again.

2. **Settle the scope, once.** How far this run goes has no default the skill can derive, so it's asked, one `AskUserQuestion` with four **exclusive** options (plugin-level `references/handoff-gate.md` for the format):
   - **Build only**: every task built, the checks green, the tree committed, and a gate at the end offering the ship.
   - **Build and review**: the build, then `/bb:review` over the branch, with the findings applied before that same gate.
   - **Build and ship**: the build, then `/bb:ship` settles the destination and ships it.
   - **Build, review and ship**: all three, the review running on the branch before the ship.

   **How it was invoked sets which option leads** and carries `(Recommended)`. "run everything", "build and ship the spec", "do it all", "delegate this" lead with build, review and ship; "implement the spec", "build the tasks", "build it" lead with build only. One keystroke confirms either way. **Invoked from `/bb:spec`'s exit gate the question is already answered**: that gate offers the same four, and its pick is the scope. Nothing else about the run is asked; the build itself is dispatched with no question of its own.

3. **Open the run, flip `status: in-progress`.** Edit the spec's frontmatter and commit that edit (conventional style; no AI attribution).

4. **Load the spec.** Read it whole: the opening and the free top half describe the thing and how it's put together, and they're written to be read once, start to finish. Then the fixed sections: the `## Decisions` (including the **reuse** notes), the `## Behavior` map (happy path + edge→outcome: **build to this; it's the acceptance contract**), what `## Out of scope` puts off the table (a hard line: do not build it), and the tasks in `## Tasks`.

5. **Reuse first.** Before writing anything, confirm the code/patterns named in the spec's reuse notes still exist, and prefer extending them over reinventing. If one has moved or changed, flag it and adjust rather than guessing: the path you found outranks the one the spec names. If one is **gone**, that's step 10's valve firing, not something to work around.

6. **Build every unchecked task, respecting `dep:`. The build is dispatched, not run here.** One agent per task, as a dynamic workflow, run by the fixed script the plugin ships. **Invoking this skill is the request for that workflow**, and that request is the opt-in the `Workflow` tool asks for, for this build. The build lands back in this context only at the last step of the reference's fallback chain. **Read the plugin-level `references/build-tasks-workflow.md` before invoking**: it carries the `args` shape, the per-run items the skill confirms, the `Bash` call that resolves and proves the script, the invoke line, the fallback chain and what the return means. Two things the reference leaves to this skill: `checks` is `<plugin-root>/scripts/resolve_checks.py`'s output passed through whole, the same call step 7 makes, so the chain is walked once per run and stage zero is what runs what it found; and `tasks` carries the **unticked ones only**, ordered so `dep:` is already satisfied. **With every task already ticked there's nothing to dispatch**: say so and go on to whatever the scope has next, which reads a build with nothing to do as a clean one.

   Then read the return: the tasks in `built` are already committed and ticked, `pendingVerify` names the ones whose proof is CI, and a non-null `stopped` is a stop of step 10's kind, whichever bucket the blocker falls in.

   **The fallback owes one line.** Whichever step of the reference's chain the run lands on past the first, **name the reason in one line**: which step, and what refused. On the last step that line is what makes building here read as the session's limit and not as a choice. Building the tasks here is steps 7 to 9 below plus this task discipline: follow `dep:` order, not list order; each task is a thin end-to-end cut, built as one; stay inside scope, since the out-of-scope bucket is a boundary, not a suggestion; and a **stack choice** the spec didn't close (framework, package manager, tooling) goes to the manifesto first (plugin-level `references/consult-manifesto.md`).

7. **Keep the project's checks green as you go.** `python3 <plugin-root>/scripts/resolve_checks.py` walks the authority chain its own docstring states and prints `{commands, source, truncated, resolved_count, runnable, policy, notes, unresolved, candidates, git_root}`. One call, and its output is what step 6 passes as `checks`, so the chain is resolved once and read twice. Run every command it returns, not a subset, and fix before moving on; when `truncated` is true, `resolved_count` is how many there were, and the difference is what you say instead of treating the list as the whole suite. An empty `commands` with a non-null `source` is a tier that answered; with `source: null` no tier resolved anything. **`unresolved` is the one field that is not an answer**: each entry is a command the script saw and could not turn into something runnable, with its `reason` (`unrecognized-runner` or `shell-dependent`) and the `where` to open. Not empty means the list is not settled, so read those files and decide yourself rather than running what came back: a stack whose runner the script cannot name arrives as an empty `commands`, and an empty `commands` reads as a project with no checks. `candidates` holds what each tier offered separately, for comparing a list that looks wrong instead of re-walking the chain. `runnable: false` means local runs are forbidden, `policy.evidence` is the line that says so, and `policy.scope` is who said it: `repo` when the project's own documents did, `machine` when it was the user's `~/.claude/CLAUDE.md`, which governs this machine and not this repo. Name the checks the PR will run and let CI be the proof.

8. **Run the task's `verify:` before you tick it.** It names how that task is proven: a test, a command, reading the result, green CI. It's the task's own check, on top of the project's checks; a task whose `verify:` didn't run is a task that isn't done.

9. **Commit per task, check the box.** Commit in logical units (conventional style; no AI attribution), and tick that task's `- [ ]` → `- [x]` in the `## Tasks` section as it lands, so progress is visible and a partial run is resumable.

10. **Safety valve.** If a task reveals the idea was underspecified (surprises pile up, scope wants to grow, a decision the spec skipped now bites), STOP and hand back to `/bb:spec` to re-spec it. Don't improvise past the spec; that's the signal alignment was incomplete. A reuse note pointing at code that's **gone** fires the same valve: the spec was written against something that no longer exists, so it's the spec that has to change. From the workflow both arrive as a returned blocker instead of a realization mid-build. Two stage-zero blockers are **not** the spec's fault and route elsewhere: a check the run has no permission to execute (report the command so the allowlist can be widened) and a tree already red before task 1 (the red predates the build; report it so it gets fixed where it lives). A task that came back red on its own, and an agent that returned nothing, are a third kind: nothing upstream is at fault, and what they take is the blocker read and that task run again. One returned `stopped` can name more than one blocker, because stage zero proves the whole ground in one pass.

    Every one of them stops the build, and the tree is left as the run left it, for diagnosis. **A stop is recorded, not just reported**: flip `status: blocked` and write the blocker into the spec's own `## Open`, one line naming it and what it needs, committed with the status flip. `status: blocked` alone tells the next run nothing, and by then the context that read the blocker is gone. That's the line step 1 reads back when it skips a blocked spec. Neither review nor ship runs after a stop, whatever the scope said.

11. **Scope included review: run the fronts on the branch, before anything ships.** Follow `/bb:review`'s workflow over what the build produced, at **standard depth across every front its availability probe finds**, with no fronts question and no gate of its own: the scope answer at step 2 is the authorization those would ask for. Before the ship there is no PR, so the probe drops the `threads` and `ci` fronts on its own. A deep pass stays `/bb:review deep`, invoked separately.

    **Apply every CONFIRMED finding, report every PLAUSIBLE one.** There is no PR to comment on yet and no item-by-item curation: the independent verifier's verdict is what decides. Applied fixes go through steps 7 to 9 like any other change, so the checks are green and committed before the ship, and the PR opens from code that was already read. Report both sets, and say so in one line when the review found nothing.

12. **Scope included ship: follow `/bb:ship`'s workflow.** Green the project's checks, commit and ship per ship's own destination logic; ship settles the destination, asking only on real doubt, and implement adds no destination logic of its own. If ship hits an unrecoverable stop, flip `status: blocked`, and put the blocker where the run can be found again: the PR description when there is a PR, otherwise the spec's own `## Open` on the pushed branch. Report it, then exit.

13. **Close the run, flip `status: done`.** Once the ship completes, edit the frontmatter to `done` and commit. **On the PR path that's right after the PR is open and its checks are handled, before the watch settles in**: `ship-pr.md` ends resident, so a flip waiting for ship to return would never happen. On a protected branch the ship is the push ship handed over, so `done` waits for it. Either way that commit only reaches the default branch when a human merges, the same gate the `## Tasks` checkboxes already pass through; implement never writes status to a protected branch directly.

14. **Report, and hand off when the run stopped short of shipping.** Name the slug, what shipped (tasks, check results, and the review's two sets when it ran), and the destination when there was one (branch / PR URL / the hand-off command for a protected branch). A build that fell back to this context says so here too, naming the step of the reference's fallback chain the run landed on.
    - **The scope did not include ship, and the run was clean**: `status` stays `in-progress`, and one handoff gate offers the ship (plugin-level `references/handoff-gate.md`): lead **"Ship now"** (invoke `/bb:ship`) against **"Stop here"** (print the command and stop). The tree is green and committed by then, so this is a different question from step 2's, asked with the build in hand.
    - **The scope did not include ship, and the run was not clean**: report done/skipped/blocked and hand back where step 10 sends it, with no ship offered. A partial build shouldn't become a PR that claims to satisfy the spec.
    - **The scope included ship**: the ship is the end of the run. Report and stop.

The hard line holds throughout: implement never merges, never approves, never force-pushes; shipping to a protected branch stays a human action.

## Edge cases

| WHEN                                             | THEN                                                                                                                   |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------- |
| `/bb:implement <slug>`, slug exists, not done    | run it at the scope step 2 settles                                                                                     |
| `/bb:implement <slug>`, slug not found           | report the error, list `pending_slugs`, stop                                                                           |
| `/bb:implement <slug>`, status `done`            | report it's done, ask whether to re-run                                                                                |
| bare, this session is already on a spec          | take that one, confirmed against the scan                                                                              |
| bare, nothing in context, one or more pending    | take `scan_specs.py`'s `selected`                                                                                      |
| bare, nothing in context, none pending           | report "no pending specs", stop                                                                                        |
| bare, the oldest spec is `blocked`               | skipped, and reported with the blocker its `## Open` carries and where that blocker sends it                           |
| spec has no frontmatter                          | the scan still selects it; run it, and `/bb:spec` backfills the block next time                                        |
| selected spec already `in-progress`              | resume: the build skips ticked tasks; `status` stays `in-progress` until the ship                                      |
| invoked from `/bb:spec`'s exit gate              | that gate's pick is the scope; step 2 asks nothing                                                                     |
| every task already ticked                        | nothing dispatched; the run goes on to whatever the scope has next                                                     |
| safety valve fires (underspecified)              | `status: blocked`, the blocker into the spec's `## Open`, point back to `/bb:spec`, stop; do not improvise             |
| the build stops (stage zero or a task)           | `status: blocked`, the blocker into the spec's `## Open`, no review and no ship                                        |
| the build falls back to this context             | it runs the same way; the reason names which step of the reference's fallback chain, in one line and again in step 14  |
| the review finds nothing                         | say so in one line and go on to the ship                                                                               |
| a CONFIRMED fix turns a check red                | fixed before the ship, through steps 7 to 9 like any other change                                                      |
| ship hits an unrecoverable stop / blocker        | `status: blocked`; the blocker into the PR description, or into the spec's `## Open` when there is no PR; report; exit |
| ship takes the PR path                           | `done` is flipped before the watch settles in                                                                          |
| ship takes a protected branch                    | ship hands over the push command; `done` waits for that push                                                           |
| not in a git repo / no `.bb/` dir in either root | report the error, stop                                                                                                 |
