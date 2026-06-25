---
status: done
created: 2026-06-25
slug: delegate-and-task-metadata
---

# /ofc:delegate skill + task-brief metadata + shape hand-off unification

## what

Three interlocking changes that turn "run a shaped task end-to-end" into one named
path used identically at the desk and overnight:

1. **New `/ofc:delegate` skill** — finds a not-yet-done task and runs it from start
   to landing (`/ofc:implement` → `/ofc:ship`). `/delegate <slug>` targets a named
   task; bare `/delegate` picks the oldest pending one. The canonical "run
   everything" entrypoint.
2. **Standardized task-brief metadata** — a YAML frontmatter block at the top of
   every `.ofc/tasks/<slug>/shape.md` (`status`, `created`, `slug`), so both the
   manual `/delegate` and a Cloud Routine select and track work the same way.
3. **Unify the hand-offs onto delegate** — `shape`'s exit gate becomes 2-way
   (**Stop** / **Delegate**); the Cloud Routine prompt (`routines.md` +
   `scaffold_routine.py`) calls `/ofc:delegate <slug>` instead of spelling out
   `implement → ship`. One orchestration, two moments (daytime supervised /
   unattended).

## why

Today "run everything" lives in three places that drifted apart: `shape`'s gate has
a "Build and ship" option, `implement` soft-chains into `ship`, and the routine
prompt hardcodes `implement → ship`. The user's ask is one verb — _delegate_ — that
both the daytime and the unattended moment route through, so the chain is defined
once. The metadata is what makes selection possible without a human in the loop
(the routine can't answer a "which task?" prompt) and gives a standard place to read
"was this executed?". Frontmatter (not prose) because the routine and delegate parse
it without heuristics, and it stays out of the brief's narrative.

## decisions

- **Unify: delegate is the entrypoint.** delegate selects the task (by frontmatter
  `status`) and runs `/ofc:implement` → `/ofc:ship` end to end. `shape`'s gate and
  the routine both call `/ofc:delegate`. The "run everything" chain is defined once,
  inside delegate.
- **Frontmatter schema** at the top of `shape.md`:
  ```yaml
  ---
  status: pending # pending | in-progress | done | blocked
  created: 2026-06-25 # YYYY-MM-DD, set when the brief is first written
  slug: <kebab-slug> # matches the dir name
  ---
  ```
  `pending` = no slice done. `in-progress` = some slices done, not landed (resumable).
  `done` = implement→ship completed its landing. `blocked` = implement's safety-valve
  or ship hit an unrecoverable stop (needs a human).
- **delegate owns the status lifecycle.** It flips `pending`/`in-progress` →
  `in-progress` on start, → `done` when the implement→ship chain lands, → `blocked`
  when the chain bails. The `## tasks` checkboxes stay slice-level and are ticked by
  `implement` as today — status is the coarse, selectable task-level state on top.
- **Bare `/delegate` selects the oldest pending.** Filter `status ∈ {pending,
in-progress}` (in-progress is resumable), pick smallest `created`; tie-break by
  slug alpha. `done`/`blocked` are skipped (blocked is reported, not silently
  dropped). `/delegate <slug>` overrides selection entirely.
- **Gate becomes 2-way: Stop / Delegate.** When nothing load-bearing is open, shape
  offers **Stop here** (just save) or **Delegate** (run everything via `/ofc:delegate
<slug>` on the brief it just wrote). Drops the separate "Build only" gate option —
  running `/ofc:implement` directly stays the manual escape hatch for build-without-ship.
  The open-decision branch is unchanged (resolve-now / defer; never a clean run).
- **shape writes the frontmatter.** On finalize, shape emits the block (`status:
pending`, `created: <today>`, `slug`). If an upstream skill (frame-problem /
  assess-fit) created the file first without frontmatter, shape backfills it.
- **delegate inherits ship's landing logic** — daytime: ship settles the destination
  (asks only on doubt). Unattended (`OFC_UNATTENDED`): ship opens a draft PR. delegate
  adds no destination logic of its own.
- **Status propagation is merge-gated, by design (inherited).** An unattended `done`
  flip commits to `claude/<slug>` and only reaches `main` when the human merges the PR
  — identical to how the `## tasks` checkboxes already propagate. delegate does not
  try to write status back to a protected branch.
- **The routine stays one-brief-per-routine** (`routines.md`'s existing rule). Its
  prompt calls `/ofc:delegate <slug>` (named, not bare) — keeps one routine → one
  task. Bare-`/delegate` backlog-draining is a daytime convenience.
- **Legacy briefs without frontmatter** are treated as `status: pending` with unknown
  `created` (sorted after dated briefs in bare-selection). `/delegate <slug>` works on
  them regardless; shape backfills frontmatter the next time it touches one.

## design

```
plugins/ofc/
├── skills/
│   ├── delegate/SKILL.md          # (NEW) select task → implement → ship; owns status
│   ├── shape/SKILL.md             # gate → 2-way (Stop/Delegate); writes frontmatter
│   ├── implement/SKILL.md         # unchanged behavior; (optional) note status is delegate's
│   └── ship/SKILL.md              # unchanged
└── references/
    ├── routines.md                # routine prompt → /ofc:delegate <slug>
    └── scripts/scaffold_routine.py# emit the delegate-based prompt
.claude/CLAUDE.md                  # documents the task-brief frontmatter schema
```

- **delegate/SKILL.md** — prerequisite: `.ofc/tasks/` exists. Resolve target: named
  arg → that slug; bare → scan `.ofc/tasks/*/shape.md`, parse frontmatter, pick oldest
  pending/in-progress. Flip status `in-progress` (commit the edit). Invoke
  `/ofc:implement` (build unchecked slices, gate green, tick boxes) then `/ofc:ship`
  (land per its own destination logic). On clean landing → status `done`; on
  safety-valve/unrecoverable → status `blocked` + report. Self-contained orchestration;
  no new scripts (frontmatter parse is a few lines of inline reading, or a tiny stdlib
  helper if cleaner).
- **shape/SKILL.md** — finalize writes the frontmatter block; gate's nothing-open
  branch → Stop / Delegate; hand-off text points to `/ofc:delegate`.
- **routines.md + scaffold_routine.py** — the prompt sets `OFC_UNATTENDED=1` and runs
  `/ofc:delegate <slug>` (which chains implement→ship and opens the draft PR), keeping
  the never-merge / capped-retry wording.

## behavior

### delegate (run everything)

Happy path (bare): `/delegate` → scan `.ofc/tasks/*/shape.md` → parse frontmatter →
pick oldest `pending`/`in-progress` → flip `status: in-progress` (commit) → run
`/ofc:implement` (build unchecked slices, keep gate green, tick boxes) → run
`/ofc:ship` (settle destination / draft PR under `OFC_UNATTENDED`) → flip `status:
done` (commit) → report the slug, what landed, and the destination.

| WHEN                                              | THEN                                                                                                                                       |
| ------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `/delegate <slug>` and slug exists, not done      | run it end to end                                                                                                                          |
| `/delegate <slug>` and slug not found             | report the error, list available pending slugs, stop                                                                                       |
| `/delegate <slug>` and status is `done`           | report already done; ask to re-run (supervised) / stop (unattended)                                                                        |
| bare `/delegate`, one+ pending                    | pick oldest `created`; tie-break slug alpha; run it                                                                                        |
| bare `/delegate`, none pending                    | report "no pending tasks", stop                                                                                                            |
| selected task already `in-progress`               | resume — implement skips checked slices; status stays `in-progress` until landing                                                          |
| brief has no frontmatter (legacy)                 | treat as `pending`, unknown `created` (sorts last); run; shape backfills later                                                             |
| implement safety-valve fires (underspecified)     | stop, flip `status: blocked`, report to re-shape; do not improvise                                                                         |
| ship hits unrecoverable stop / unattended blocker | flip `status: blocked`, write blocker into PR description (unattended) / report (daytime), exit                                            |
| `OFC_UNATTENDED` set                              | no questions; ship opens a DRAFT PR; never merge/protected-push; `done` flip commits to `claude/<slug>` (reaches main only on human merge) |
| not in a git repo / `.ofc/tasks/` missing         | report the error, stop                                                                                                                     |

### shape gate + frontmatter

| WHEN                                            | THEN                                                                                                   |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| brief finalized, nothing load-bearing open      | gate offers **Stop here** / **Delegate**; Delegate → `/ofc:delegate <slug>` on the new brief           |
| load-bearing decision still open                | unchanged: resolve-now / defer-explicitly; no clean Delegate offered                                   |
| shape writes a new brief                        | emit frontmatter (`status: pending`, `created: <today>`, `slug`) at top                                |
| upstream skill created the file w/o frontmatter | shape backfills the block on finalize                                                                  |
| user picks Stop                                 | save brief; hand-off names `/ofc:implement` (build) and `/ofc:delegate` (run everything) as next steps |

### routine (unattended)

| WHEN                                      | THEN                                                                                           |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------- |
| routine fires                             | prompt sets `OFC_UNATTENDED=1`, runs `/ofc:delegate <slug>` (chains implement→ship → draft PR) |
| every slice already checked + status done | delegate/implement find nothing to build, ship nothing to open → report no-op, exit            |
| scaffold_routine.py emits a prompt        | wording uses `/ofc:delegate <slug>`, keeps never-merge + capped-retry clauses                  |

## tasks

- [x] **Document the task-brief frontmatter schema** in `.claude/CLAUDE.md` — the
      `status`/`created`/`slug` block, the four status values and their meaning, and that
      delegate owns the lifecycle. (delivers: standardized metadata convention)
- [x] **Create `/ofc:delegate`** — `skills/delegate/SKILL.md`: named/bare selection,
      status lifecycle (`in-progress`→`done`/`blocked`), chain `implement`→`ship`,
      report. Honors `OFC_UNATTENDED`. (delivers: all delegate behaviors)
- [x] **Update `shape`** — write frontmatter on finalize (+ backfill legacy);
      nothing-open gate → 2-way Stop/Delegate; hand-off text → `/ofc:delegate`.
      (delivers: shape emits metadata, gate, hand-off)
- [x] **Unify the unattended path** — `routines.md` prompt + `scaffold_routine.py`
      emit `/ofc:delegate <slug>`; keep never-merge/retry wording. (delivers: unified
      daytime+unattended orchestration)
- [x] **Docs + release** — README (add `/ofc:delegate` to the shape & ship group),
      `.claude/CLAUDE.md` structure tree (add `delegate`), bump `plugin.json` minor
      version, run `bun run fmt` + `fmt:check` + `validate`. (delivers: discoverability,
      release)

## out of scope

- **Bare-`/delegate` as a routine backlog-drainer** — the routine stays one-brief
  (named slug). _revisit_ if multi-task overnight is wanted and merge-gated propagation
  is solved.
- **A `priority` frontmatter field** — selection is oldest-`created` for now. _revisit_
  if ordering needs manual control.
- **implement/ship flipping status when invoked directly** (not via delegate) — status
  is delegate's concern; direct `/ofc:implement` is the manual hatch and manages no
  status. _revisit_ if direct runs should also track status.
- **Migrating/backfilling all existing legacy briefs in one pass** — backfill happens
  lazily when shape next touches a brief.
- **Concurrent delegate runs** on the same repo — single-agent only (matches routines).

## still open

- None load-bearing. Build-time call: whether frontmatter parsing is inline-read or a
  tiny stdlib helper script (decide while writing delegate — lean inline unless it gets
  repetitive across skills). The exact minor version depends on whether the
  review-skill-and-script-dedup brief lands first.
