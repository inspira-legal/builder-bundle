# Task state — the `.bb/tasks/<slug>/spec.md` contract

The single on-disk contract for a specced brief. Written by `/bb:spec` (and seeded by
`/bb:discover`), consumed by `/bb:implement`, `/bb:ship` and `/bb:delegate`. Any
skill that reads or writes task state follows this file — the contract lives here
and nowhere else.

## Location

- Briefs live at `.bb/tasks/<slug>/spec.md`. `<slug>` is a short kebab name
  matching the dir.
- Bare selection (`/bb:delegate` with no slug) scans `.bb/tasks/*/spec.md` and
  picks by `created`.

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
