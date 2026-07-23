---
name: delegate
description: Run a shaped task end to end — pick a not-yet-done `.ofc/tasks/<slug>/shape.md`, build every slice, and land it (`/ofc:implement` → `/ofc:ship`), tracking the brief's `status` as it goes. `/ofc:delegate <slug>` targets a named task; bare `/ofc:delegate` picks the oldest pending one. The one "run everything" entrypoint, used identically at your desk and under an unattended routine (`OFC_UNATTENDED`). Use when the user says "delegate this", "run the task", "build and ship the brief", "do the whole thing", "delegate <slug>", or "run everything". Do NOT use to shape an idea first (use /ofc:shape) or to build without landing (use /ofc:implement).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.0.0
---

# Delegate

Take a shaped task all the way: select it, build every slice, and land it — the
`/ofc:implement` → `/ofc:ship` chain defined in one place. delegate is the single
"run everything" verb, routed through identically whether you call it at your desk
or a Cloud Routine fires it overnight under `OFC_UNATTENDED` (see the routine guide,
`references/routines.md` at the plugin root). It owns the brief's `status` lifecycle
(documented in `.claude/CLAUDE.md`); the slice-level `## tasks` checkboxes stay
`implement`'s.

## Prerequisites

Inside a git repository with a `.ofc/tasks/` directory. If neither holds, report it
and stop.

## Workflow

1. **Resolve the target brief.**
   - **Named** (`/ofc:delegate <slug>`): use `.ofc/tasks/<slug>/shape.md`. If it
     doesn't exist, report the error, list the available pending slugs, and stop.
   - **Bare** (`/ofc:delegate`): scan `.ofc/tasks/*/shape.md`, read each frontmatter
     block, keep those with `status ∈ {pending, in-progress}`, and pick the smallest
     `created` (tie-break: slug alphabetical). Legacy briefs with no frontmatter count
     as `pending` with unknown `created` (sorted last). If none qualify, report "no
     pending tasks" and stop.
   - A brief already `done`: report it's done; supervised, ask whether to re-run;
     unattended, stop (no-op). A `blocked` brief is skipped in bare selection and
     reported, not silently dropped — name it so the user can re-shape.

2. **Open the run — flip `status: in-progress`.** Edit the brief's frontmatter and
   commit that edit (conventional style; no AI attribution). Unattended: put it on the
   `claude/<slug>` branch the build will use.

3. **Build — follow `/ofc:implement`'s workflow (steps 1–6), then return here.** Load
   the brief, honor its reuse notes and `## behavior` contract, build every unchecked
   slice in order, keep the gate green, and commit per slice ticking its box. **Do not
   run implement's step-7 ship hand-off** — delegate owns the transition to landing, so
   the chain lives here, not split across skills. If implement's **safety valve** fires
   (the brief was underspecified), stop: flip `status: blocked`, point back to
   `/ofc:shape` to re-shape, and exit — do not improvise past the brief.

4. **Land — follow `/ofc:ship`'s workflow.** Run the quality pass and land per ship's
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

| WHEN                                          | THEN                                                                                                           |
| --------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `/ofc:delegate <slug>`, slug exists, not done | run it end to end                                                                                              |
| `/ofc:delegate <slug>`, slug not found        | report the error, list available pending slugs, stop                                                           |
| `/ofc:delegate <slug>`, status `done`         | report it's done; supervised ask to re-run, unattended stop                                                    |
| bare `/ofc:delegate`, one+ pending            | pick smallest `created` (tie-break slug alpha), run it                                                         |
| bare `/ofc:delegate`, none pending            | report "no pending tasks", stop                                                                                |
| selected task already `in-progress`           | resume — implement skips checked slices; status stays `in-progress` until landing                              |
| brief has no frontmatter (legacy)             | treat as `pending`, unknown `created` (sorts last); run it; `/ofc:shape` backfills the block next time         |
| implement safety valve fires (underspecified) | flip `status: blocked`, point back to `/ofc:shape`, stop — do not improvise                                    |
| ship hits an unrecoverable stop / blocker     | flip `status: blocked`; write the blocker into the PR description (unattended) or report it (supervised); exit |
| `OFC_UNATTENDED` set                          | no questions; ship opens a DRAFT PR on `claude/<slug>`; never merge / never push a protected branch            |
| not in a git repo / `.ofc/tasks/` missing     | report the error, stop                                                                                         |

The hard line holds throughout: delegate never merges, never approves, never
force-pushes — landing on a protected branch stays a human action, enforced by
capability scoping on the unattended path.
