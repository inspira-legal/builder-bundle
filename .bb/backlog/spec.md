---
status: done
created: 2026-10-27
slug: backlog
---

# /bb:backlog: give a place to what the work left for later

Every bb record already asks for the reason behind a cut. `/bb:discover` writes `## Cuts` with a
typed reason, `/bb:spec` writes `## Out of scope` and marks the ideas parked for later with
_revisit_, and the lint warns when a spec has no `## Out of scope`. What none of them does is give
those items a place once the work is over. When a spec ships or stops, its leftovers stay in
`.bb/<slug>/` and nobody opens the folder again.

A manual harvest of two product specs, crossed with the tracker, showed what is at stake. The two
specs held 17 leftovers, 15 once the duplicates were merged. Four of them were already in the
tracker under another name, because a cut in discovery comes back in the spec with different
words. Five were new work worth doing. And one spec, written three weeks earlier, had never been
registered anywhere: its whole plan lived in that one file.

`/bb:backlog` gives the leftovers a place, `.bb/<slug>/backlog.md`, and keeps it short. An item
gets in only when someone weighed it and wants it back, or when it has evidence of value to the
user. A backlog that keeps everything is read by nobody.

## The harvest

`scripts/harvest.py` reads what is decidable from the bytes and writes nothing. Per slug it
returns the spec's `status` and `wave` key, the discovery's `verdict`, the items and the alerts:

- **Items**: the `Cut:` list of `## Cuts` (with the typed reason), the bullets of `## Out of scope`
  and `## Open`, and the unticked tasks of a spec that ended. Each item carries its _revisit_
  trigger, its ICE when the line has one, its source as `file#section:line`, and an id.
- **Alerts**: a pending spec older than 14 days, and two items that share most of their words.
- **Memory**: the ids already written to `backlog.md`, so the next harvest skips them.

It imports `find_bb_root` and `parse_frontmatter` from `<plugin-root>/scripts/scan_specs.py`, so
the root walk and the frontmatter reading stay one definition. It cannot reuse `scan()`, which
keeps only `pending` and `in-progress` specs.

Which item is worth keeping, and where it lands, is the skill's judgment, in
`references/destination.md`. Capture from the conversation follows `references/capture.md`.

## Decisions

- `backlog.md` is a fifth member of the `.bb/<slug>/` contract, and `/bb:backlog` is its only
  writer. A single file at the root of `.bb/` would give one document many slugs and break the
  one writer rule.
- The file has three sections: `## Next version` (with the trigger that brings each item back),
  `## No trigger yet`, and `## Discarded` (with the reason, so the next spec sees it was weighed).
- A line cites its source by path and line and never copies the record's reasoning.
- A spec's unticked tasks are leftovers only once the spec is `done` or `blocked`, or the
  discovery shelved the idea. In a live spec they are still the plan.
- A captured item gets in through one of two doors: the person's interest, or value to the user
  with evidence. The model's own suggestions that nobody took up stay out.
- When an item's place is unclear, the skill asks once, at the end, and does not write it before.
- An ICE score is kept with the date of the record it came from, because it ages.
- This version writes only the local file. The tracker comes in a later version.
- The skill has no gate. It reports what it wrote and stops.

## Behavior

1. The person runs `/bb:backlog` on a slug, or on the whole folder.
2. The skill runs `harvest.py`, shows the alerts, and places each item under
   `references/destination.md`.
3. The person confirms the table once, and the skill writes `backlog.md`.

| when                                                     | then                                                   |
| -------------------------------------------------------- | ------------------------------------------------------ |
| WHEN the spec is `pending` or `in-progress`              | THEN its unticked tasks are not harvested              |
| WHEN the spec is `done` or `blocked`                     | THEN its unticked tasks are harvested                  |
| WHEN a `## Cuts` item sits under `Kept`                  | THEN it is in scope and not harvested                  |
| WHEN a pending spec is older than 14 days                | THEN a `stale_spec` alert opens the report             |
| WHEN the stale spec has no `wave` key                    | THEN the report says the plan exists only in that file |
| WHEN the same idea is in `discovery.md` and `spec.md`    | THEN one entry is written, citing both sources         |
| WHEN an item has no reason beside it                     | THEN the skill reads `## Decisions` before asking      |
| WHEN a cut came back as a task                           | THEN it is not written                                 |
| WHEN an item's id is already in `backlog.md`             | THEN it is skipped                                     |
| WHEN the person says "park this" in the middle of a task | THEN the item is captured with the `interest` door     |
| WHEN the model suggested an idea and nobody took it up   | THEN it is not captured                                |
| WHEN the folder has many slugs and no slug was named     | THEN the person picks the slugs from one line per slug |

## Metric

- Metric: share of the specs written after this lands that pick at least one item from a
  `backlog.md`, read over 90 days
- Baseline: skipped: not-instrumented
- Target: 1 in 3 new specs, within 90 days (Vinicius Salgueiro's estimate)
- Events: none, the skill writes a file and has no product surface

## Attention points

- An `## Out of scope` that holds many hard lines and few parked ideas yields many items that all
  land in `## Discarded`. The bb repo's own 29 specs return 174 items.
- The near duplicate check compares words, so the same idea written with different words passes
  it. Only the skill's reading catches that case.
- A spec that predates the `wave` key reads as unregistered even when the tracker has it.

## Tasks

### Foundation

- [x] **1. The harvest**: `skills/backlog/scripts/harvest.py` lists items, alerts and the ids
      already kept, and writes nothing. · verify: `python3 plugins/bb/skills/backlog/scripts/harvest_test.py`

### The skill

- [x] **2. The router**: `skills/backlog/SKILL.md` picks harvest or capture and runs the harvest
      steps. · verify: reading
- [x] **3. The destination and the capture**: `references/destination.md` and
      `references/capture.md`. · verify: reading

### Close

- [x] **4. The contract and the listings**: `references/spec-state.md` names `backlog.md`; the
      README, `.claude/CLAUDE.md`, `handoff-gate.md`, `plugin.json`, `marketplace.json`, the
      CHANGELOG and the CI step catch up. · verify: CI

## Out of scope

- Registering the items in the tracker, with a label, after checking what is already there.
  _revisit_ once local harvests show items coming back into new specs
- `/bb:spec` reading `backlog.md` when it starts, and closing its phases with MoSCoW so what stays
  out of the first version is born as `next version` with a trigger. _revisit_ in its own PR,
  agreed with the maintainer on 2026-10-27
- A one line note from `/bb:ship` and `/bb:review` when they leave leftovers behind. _revisit_ with
  the tracker version
- A numeric score at harvest time. _discarded_ because the score is given when the next spec
  weighs the item.

## Open

Nothing.
