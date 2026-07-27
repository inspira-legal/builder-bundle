---
name: delegate
description: Roda uma task shaped de ponta a ponta — seleciona um brief não-concluído (`.bb/tasks/<slug>/spec.md`), constrói todas as slices e landa (`/bb:implement` → `/bb:ship`), rastreando o `status` do brief. `/bb:delegate <slug>` mira uma task nomeada; `/bb:delegate` sem argumento pega a pendente mais antiga. O único verbo "roda tudo", usado igual na sua mesa e numa rotina unattended (`BB_UNATTENDED`). Use quando o usuário disser "delega isso", "roda a task", "constrói e landa o brief", "faz tudo", "delegate <slug>", ou "roda tudo". NÃO use pra alinhar uma ideia primeiro (use /bb:spec) nem pra construir sem landar (use /bb:implement).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 2.0.0
---

# Delegate

Take a shaped task all the way: select it, build every slice, and land it — the
`/bb:implement` → `/bb:ship` chain defined in one place. delegate is the single
"run everything" verb, routed through identically whether you call it at your desk
or a Cloud Routine fires it overnight under `BB_UNATTENDED` (see the routine guide,
`references/routines.md` at the plugin root). It owns the brief's `status` lifecycle
(contract in the plugin-level `references/task-state.md`); the slice-level `## tasks`
checkboxes stay `implement`'s.

## Prerequisites

Inside a git repository with a `.bb/tasks/` directory. If neither holds, report it
and stop.

## Workflow

1. **Resolve the target brief** per the task-state contract (plugin-level
   `references/task-state.md`).
   - **Named** (`/bb:delegate <slug>`): use `.bb/tasks/<slug>/spec.md`. If it
     doesn't exist, report the error, list the available pending slugs, and stop.
   - **Bare** (`/bb:delegate`): scan `.bb/tasks/*/spec.md`, read each frontmatter
     block, keep those with `status ∈ {pending, in-progress}`, and pick the smallest
     `created` (tie-break: slug alphabetical). A brief with no frontmatter counts
     as `pending` with unknown `created` (sorted last). If none qualify, report "no
     pending tasks" and stop.
   - A brief already `done`: report it's done; supervised, ask whether to re-run;
     unattended, stop (no-op). A `blocked` brief is skipped in bare selection and
     reported, not silently dropped — name it so the user can re-shape.

2. **Open the run — flip `status: in-progress`.** Edit the brief's frontmatter and
   commit that edit (conventional style; no AI attribution). Unattended: put it on the
   `claude/<slug>` branch the build will use.

3. **Build — follow `/bb:implement`'s workflow (steps 1–6), then return here.** Load
   the brief, honor its reuse notes and `## behavior` contract, build every unchecked
   slice in order, keep the gate green, and commit per slice ticking its box. **Do not
   run implement's step-7 ship hand-off** — delegate owns the transition to landing, so
   the chain lives here, not split across skills. If implement's **safety valve** fires
   (the brief was underspecified), stop: flip `status: blocked`, point back to
   `/bb:spec` to re-shape, and exit — do not improvise past the brief.

4. **Land — follow `/bb:ship`'s workflow.** Run the quality pass and land per ship's
   own destination logic: supervised, ship settles the destination (asking only on real
   doubt); unattended, ship opens a **draft PR** on `claude/<slug>` and watches it.
   delegate adds no destination logic of its own. If ship hits an unrecoverable stop
   (or an unattended blocker), flip `status: blocked` — write the blocker into the PR
   description when unattended, report it when supervised — and exit.

5. **Close the run — flip `status: done`.** Once the chain lands cleanly, edit the
   frontmatter to `done` and commit. Unattended, this commit rides `claude/<slug>` and
   only reaches the default branch when a human merges the PR — the same merge gate the
   `## tasks` checkboxes already pass through; delegate never writes status to a
   protected branch directly.

6. **Report.** Name the slug, what landed (slices, gate result), and the destination
   (branch / PR URL / the hand-off command for a protected branch).

## Edge cases

| WHEN                                            | THEN                                                                                                           |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `/bb:delegate <slug>`, slug exists, not done    | run it end to end                                                                                              |
| `/bb:delegate <slug>`, slug not found           | report the error, list available pending slugs, stop                                                           |
| `/bb:delegate <slug>`, status `done`            | report it's done; supervised ask to re-run, unattended stop                                                    |
| bare `/bb:delegate`, one+ pending               | pick smallest `created` (tie-break slug alpha), run it                                                         |
| bare `/bb:delegate`, none pending               | report "no pending tasks", stop                                                                                |
| selected task already `in-progress`             | resume — implement skips checked slices; status stays `in-progress` until landing                              |
| brief has no frontmatter                        | treat as `pending`, unknown `created` (sorts last); run it; `/bb:spec` backfills the block next time           |
| implement safety valve fires (underspecified)   | flip `status: blocked`, point back to `/bb:spec`, stop — do not improvise                                      |
| ship hits an unrecoverable stop / blocker       | flip `status: blocked`; write the blocker into the PR description (unattended) or report it (supervised); exit |
| `BB_UNATTENDED` set                             | no questions; ship opens a DRAFT PR on `claude/<slug>`; never merge / never push a protected branch            |
| not in a git repo / no tasks dir in either root | report the error, stop                                                                                         |

The hard line holds throughout: delegate never merges, never approves, never
force-pushes — landing on a protected branch stays a human action, enforced by
capability scoping on the unattended path.
