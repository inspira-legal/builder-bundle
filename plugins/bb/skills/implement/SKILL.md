---
name: implement
description: Builds a validated spec (`.bb/<slug>/spec.md`) in the working tree. Implements the tasks, keeps the project's checks green, commits per task and offers the ship at the end (or chains straight into it when ship was already authorized). The executor of the Construir trilha. Use when the user says "implement the spec", "build the tasks", "build it", "implement this", or right after /bb:spec. Don't use it to align on an idea first (use /bb:spec) or to open and green a PR on its own (use /bb:ship).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 2.5.0
---

# Implement

Build the validated spec in the working tree, taking it from alignment to code that's ready to ship. The trio's executor: it builds the backlog, then offers to ship.

## Prerequisites

A validated spec with a `## Tasks` checklist, resolved per the spec-state contract (plugin-level `references/spec-state.md`): `.bb/<slug>/spec.md`. If there's no spec for this work, stop and suggest `/bb:spec` first. Implementing without alignment is exactly what the spec prevents.

## Workflow

1. **Load the spec.** Read it whole: the opening and the free top half describe the thing and how it's put together, and they're written to be read once, start to finish. Then the fixed sections: the `## Decisions` (including the **reuse** notes), the `## Behavior` map (happy path + edge→outcome: **build to this; it's the acceptance contract**), what `## Out of scope` puts off the table (a hard line: do not build it), and the tasks in `## Tasks`. A spec written before the rename spells those `## Decisões`, `## Comportamento`, `## Fora de escopo` and `## Tarefas`, which are the same sections, read the same way (the whole pairing is in the plugin-level `references/spec-state.md`).
2. **Reuse first.** Before writing anything, confirm the code/patterns named in the spec's reuse notes still exist, and prefer extending them over reinventing. If one has moved or changed, flag it and adjust rather than guessing: the path you found outranks the one the spec names. If one is **gone**, that's step 7's valve firing, not something to work around.
3. **Build every unchecked task, respecting `dep:`. The build is dispatched, not run here.** One agent per task, as a dynamic workflow, run by the fixed script the plugin ships; nothing about this is asked. **Read the plugin-level `references/build-tasks-workflow.md` before invoking**: it holds `args`, the invoke line, the fallback chain, the three per-run checks and what the return means. **With every task already ticked there's nothing to dispatch**: say so and go to step 8, which reads that as a clean run. Otherwise, four moves, in order:
   - **Build `args` by reading the spec**, in the shape the reference states. `checksHint` is step 4's authority chain resolved and not run, since stage zero is what runs the checks; `tasks` carries the **unticked ones only**, ordered so `dep:` is already satisfied (older spelling `depende:` included, per the plugin-level `references/spec-state.md`).
   - **Confirm the three per-run items** the reference leaves to the skill: `args` as a JSON value with only unticked tasks, the branch already checked out, and the agent count against the size guideline the session declares.
   - **Resolve and prove the script in one `Bash` call**, the one the reference gives. A non-zero exit is the missing-file case; the path it prints is what goes into `scriptPath`, already expanded, because the tool takes a literal path.
   - **Invoke `Workflow`** with that `scriptPath` and `args`, then read the result: the tasks in `built` are already committed and ticked, `pendingVerify` names the ones whose proof is CI, and a non-null `stopped` is step 7 firing from inside the run.

   **The fallback owes one line.** Whichever step of the reference's chain the run lands on past the first, **name the reason in one line**, so a downgrade doesn't read as a preference. Building the tasks here is steps 4–6 below plus this task discipline: follow `dep:` order, not list order; each task is a thin end-to-end cut, built as one; stay inside scope, since the out-of-scope bucket is a boundary, not a suggestion; and a **stack choice** the spec didn't close (framework, package manager, tooling) goes to the manifesto first (plugin-level `references/consult-manifesto.md`).

4. **Keep the project's checks green as you go.** Detect the project's checks in this order of authority: CLAUDE.md / docs → CI workflow files → `package.json` / `justfile` / `Makefile` / `pyproject.toml`. That resolution is also what fills step 3's `checksHint`, so it happens either way; here it's run as well. Run lint/format/typecheck/tests; fix before moving on. Run what CI runs, not a subset.
5. **Run the task's `verify:` before you tick it.** It names how that task is proven: a test, a command, reading the result, green CI. It's the task's own check, on top of the project's checks; a task whose `verify:` didn't run is a task that isn't done.
6. **Commit per task, check the box.** Commit in logical units (conventional style; no AI attribution), and tick that task's `- [ ]` → `- [x]` in the `## Tasks` section as it lands, so progress is visible and a partial run is resumable.
7. **Safety valve.** If a task reveals the idea was underspecified (surprises pile up, scope wants to grow, a decision the spec skipped now bites), STOP and hand back to `/bb:spec` to re-spec it. Don't improvise past the spec; that's the signal alignment was incomplete. A reuse note pointing at code that's **gone** fires the same valve: the spec was written against something that no longer exists, so it's the spec that has to change. From the workflow both arrive as a returned blocker instead of a realization mid-build. Two stage-zero blockers are **not** the spec's fault and route elsewhere: a check the run has no permission to execute (report the command so the allowlist can be widened) and a tree already red before task 1 (the red predates the build; report it so it gets fixed where it lives). All three stop the build, and the tree is left as the run left it, for diagnosis.
8. **Hand off: offer to ship, or chain.** Summarize what landed against the task list (done / skipped / blocked). Then branch on how the run went:
   - **Clean** (every task landed, checks green): offer ship via a handoff gate (plugin-level `references/handoff-gate.md`): lead **"Ship now"** (invoke `/bb:ship`) against **"Stop here"** (print the command and stop). Either path, ship loads this same spec as the intent. (When the whole run is wanted up front without this stop, that's `/bb:delegate`. It drives this build loop and chains into ship itself; implement, whether picked at the spec gate or run by command, is the build-then-decide path.)
   - **Not clean** (a task blocked, or the safety valve fired): report done/skipped/blocked and hand back where step 7 sends it; `/bb:spec` when the spec is what has to change, the allowlist or the pre-existing red check when it isn't. Either way **don't** offer ship: a partial build shouldn't become a PR that claims to satisfy the spec.
