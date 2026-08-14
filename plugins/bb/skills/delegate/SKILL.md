---
name: delegate
description: Roda uma spec de ponta a ponta — seleciona uma spec não-concluída (`.bb/<slug>/spec.md`), constrói todas as tarefas e landa (`/bb:implement` → `/bb:ship`), rastreando o `status` da spec. `/bb:delegate <slug>` mira uma spec nomeada; `/bb:delegate` sem argumento pega a pendente mais antiga. O único verbo "roda tudo". Use quando o usuário disser "delega isso", "roda a task", "constrói e landa o brief", "faz tudo", "delegate <slug>", ou "roda tudo". NÃO use pra alinhar uma ideia primeiro (use /bb:spec) nem pra construir sem landar (use /bb:implement).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 2.4.0
---

# Delegate

Take a specced idea all the way: select the spec, build every task, and land it — the
`/bb:implement` → `/bb:ship` chain defined in one place. delegate is the single
"run everything" verb. It owns the spec's `status` lifecycle (contract in the
plugin-level `references/spec-state.md`); the `## tasks` checkboxes inside it stay
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
     `<slug>` is the key — a slug found under both paths is one candidate, read
     from `.bb/<slug>/`. A spec with no frontmatter counts as `pending` with
     unknown `created` (sorted last). If none qualify, report "no pending specs"
     and stop.
   - A spec already `done`: report it's done and ask whether to re-run. A `blocked`
     spec is skipped in bare selection and reported, not silently dropped — name it
     so the user can re-spec it.

2. **Open the run — flip `status: in-progress`.** Edit the spec's frontmatter and
   commit that edit (conventional style; no AI attribution).

3. **Pick the build mode — workflow, or this context.** Ask once, per the
   plugin-level `references/build-mode.md`: one agent per task dispatched as a
   dynamic workflow, or the tasks built here as always. The answer goes into step 4,
   and the implement loop it drives doesn't ask again. With no `Workflow` tool in the
   session there's nothing to offer: build in context and name the reason, in step 7's
   report too, so a silent downgrade doesn't pass for a choice.

4. **Build — follow `/bb:implement`'s workflow (steps 1–7), then return here.** Load
   the spec, honor its reuse notes and `## behavior` contract, build every unchecked
   task in the order its `dep:` fields imply, run each task's `verifica:`, keep the
   gate green, and commit per task ticking its box. **Do not
   run implement's step-8 ship hand-off** — delegate owns the transition to landing, so
   the chain lives here, not split across skills. If implement's **safety valve** fires
   (the spec was underspecified), stop: flip `status: blocked`, point back to
   `/bb:spec` to re-spec it, and exit — do not improvise past the spec.

   **In workflow mode** the build is dispatched rather than run here: author the
   script per the plugin-level `references/build-tasks-workflow.md`, run its
   pre-invoke checklist, and invoke `Workflow`. Its result is the build report. A
   non-null `stopped` — a stage-zero blocker (a reuse note pointing at code that's
   gone, a gate the run can't execute, a tree already red), a red task, a lost
   agent, or a spec the agent found underspecified — lands the same place the safety
   valve does: flip `status: blocked`, name the blocker, exit without landing. What
   came back green is already committed and ticked.

5. **Land — follow `/bb:ship`'s workflow.** Run the quality pass and land per ship's
   own destination logic — ship settles the destination, asking only on real doubt;
   delegate adds no destination logic of its own. If ship hits an unrecoverable stop,
   flip `status: blocked`, and land the blocker where the run can be found again: the
   PR description when there is a PR, otherwise the spec's own `## open` on the
   pushed branch. Report it, then exit.

6. **Close the run — flip `status: done`.** Once the chain lands cleanly, edit the
   frontmatter to `done` and commit. On a feature branch that commit only reaches the
   default branch when a human merges the PR — the same merge gate the `## tasks`
   checkboxes already pass through; delegate never writes status to a protected branch
   directly.

7. **Report.** Name the slug, the build mode it ran in, what landed (tasks, gate
   result), and the destination (branch / PR URL / the hand-off command for a
   protected branch).

## Edge cases

| WHEN                                             | THEN                                                                                                                                            |
| ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| `/bb:delegate <slug>`, slug exists, not done     | run it end to end                                                                                                                               |
| `/bb:delegate <slug>`, slug not found            | report the error, list available pending slugs, stop                                                                                            |
| `/bb:delegate <slug>`, status `done`             | report it's done, ask whether to re-run                                                                                                         |
| bare `/bb:delegate`, one+ pending                | pick smallest `created` (tie-break slug alpha), run it                                                                                          |
| bare `/bb:delegate`, none pending                | report "no pending specs", stop                                                                                                                 |
| selected spec already `in-progress`              | resume — implement skips checked tasks; status stays `in-progress` until landing                                                                |
| spec has no frontmatter                          | treat as `pending`, unknown `created` (sorts last); run it; `/bb:spec` backfills the block next time                                            |
| implement safety valve fires (underspecified)    | flip `status: blocked`, point back to `/bb:spec`, stop — do not improvise                                                                       |
| workflow mode stops (stage zero or a task)       | flip `status: blocked`, exit without landing                                                                                                    |
| ship hits an unrecoverable stop / blocker        | flip `status: blocked`; write the blocker into the PR description, or into the spec's `## open` when the destination has no PR; report it; exit |
| slug sits under both `.bb/` layouts              | one candidate — the `.bb/<slug>/` copy is the one read                                                                                          |
| spec only under `.bb/tasks/<slug>/`              | found by the second glob, run as usual                                                                                                          |
| not in a git repo / no `.bb/` dir in either root | report the error, stop                                                                                                                          |

The hard line holds throughout: delegate never merges, never approves, never
force-pushes — landing on a protected branch stays a human action.
