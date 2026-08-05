# Task state — the `.bb/tasks/<slug>/` contract

The single on-disk contract for a task's durable artifacts. The brief is written by
`/bb:spec` (and seeded by `/bb:discover`), consumed by `/bb:implement`, `/bb:ship`
and `/bb:delegate`; the visual direction is written by `/bb:brisar`. Any skill that
reads or writes task state follows this file — the contract lives here and nowhere
else.

## Location

`.bb/tasks/<slug>/` is the task's folder — `<slug>` is a short kebab name matching
the dir, and everything durable about that task lives inside it:

```
.bb/tasks/<slug>/
├── spec.md              # the brief — /bb:discover seeds, /bb:spec finalizes
├── design.md            # visual direction, single surface — /bb:brisar Phase 4
└── design/              # …or one file per surface, when there is more than one
    ├── README.md        # index + suggested drawing order
    └── <surface>.md
```

- `design.md` and `design/` are the same artifact in two shapes: one surface writes
  the flat file, two or more write the folder. A task never has both.
- Members are independent. A brisar run that never went through `/bb:discover`
  leaves a folder with design and no `spec.md`; a specced task that never touched
  design has only `spec.md`.
- Bare selection (`/bb:delegate` with no slug) scans `.bb/tasks/*/spec.md` and
  picks by `created` — a folder without a brief is simply not a candidate.
- The `.bb/` root is the nearest ancestor of the cwd that already has one; if none
  does, it is created in the cwd.

## Frontmatter (selection & tracking)

Every brief opens with:

```yaml
---
status: pending # pending | in-progress | done | blocked
created: 2026-07-23 # YYYY-MM-DD, set when the brief is first written
slug: <kebab-slug> # matches the dir name
---
```

- `pending` — no slice done yet.
- `in-progress` — some slices done, not landed (resumable).
- `done` — the implement→ship chain completed its landing.
- `blocked` — implement's safety valve or ship hit an unrecoverable stop; needs a human.

**`/bb:delegate` owns the `status` lifecycle** — it flips the value as it selects,
runs and lands a task. `spec` only writes the initial block (`status: pending`) on
finalize. The slice-level `## tasks` checkboxes stay `implement`'s concern. A brief
without the block is treated as `pending` with unknown `created` (sorted last in
bare selection).

## Upstream sections (discover → spec)

`/bb:discover` seeds the brief with `## problem` / `## hypothesis` (problem
framing) and `## fit` / `## cuts` (appetite & scope). `/bb:spec` reads them as the
intent this work serves and builds the rest of the brief in the same file — the
upstream sections stay where they are, in the free top half, and the spine
(`## decisions`, `## behavior`, `## tasks`, `## out of scope`, `## open`) goes
below them. The format is
`${CLAUDE_PLUGIN_ROOT}/skills/spec/references/spec-format.md`.
