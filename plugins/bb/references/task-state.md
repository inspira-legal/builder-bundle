# Task state — the `.bb/tasks/<slug>/spec.md` contract

The single on-disk contract for shaped work. Written by `/bb:spec` (and seeded by
`/bb:discover`), consumed by `/bb:implement`, `/bb:ship` and `/bb:delegate`. Any
skill that reads or writes task state follows this file — the contract lives here
and nowhere else.

## Location

- **New work is always written to** `.bb/tasks/<slug>/spec.md`. `<slug>` is a short
  kebab name matching the dir.
- **Legacy fallback (read-only path choice):** when resolving a slug, look in
  `.bb/tasks/<slug>/spec.md` first; if absent, fall back to the legacy
  `.ofc/tasks/<slug>/shape.md`. A legacy brief found this way is executed and
  updated **in place** (status flips, checkbox ticks) — never moved or copied.
- **Both exist for the same slug:** `.bb/` wins; mention the ignored legacy file in
  the report.
- Bare selection (`/bb:delegate` with no slug) scans **both** roots, applying the
  same per-slug precedence before picking by `created`.

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
finalize, and backfills it on legacy briefs that predate the convention. The
slice-level `## tasks` checkboxes stay `implement`'s concern. Legacy briefs without
the block are treated as `pending` with unknown `created` (sorted last in bare
selection).

## Upstream sections (discover → spec)

`/bb:discover` seeds the brief with `## problem` / `## hypothesis` (problem
framing) and `## fit` / `## cuts` (appetite & scope). `/bb:spec` reads them as the
intent the shaping serves and builds the full brief in the same file: `## what`,
`## why`, decisions, out-of-scope, and for Large work `## design`, `## behavior`
and `## tasks` (the slice checklist).
