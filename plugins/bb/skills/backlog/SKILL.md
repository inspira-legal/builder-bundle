---
name: backlog
description: Gives a place to what the work left for later, so an idea someone already weighed is not lost and an idea nobody wanted does not pile up. Harvests the cuts, the out of scope and the revisit items that sit in the .bb folder of a slug once the work ships or stops, flags a spec that went stale, and captures from the conversation only what the person asked to keep or what has evidence of value to the user. Writes backlog.md next to the spec, the list the next round of work picks from. Use when the user says "organize the backlog", "what did we leave out", "harvest the leftovers", "park this for later", "note this for the next version", "don't lose this idea", or "anota pra depois". Don't use it to plan the current version (use /bb:spec) or to frame a new problem (use /bb:discover).
license: MIT
metadata:
  author: Vinicius Salgueiro
  version: 1.0.0
---

# Backlog

Every bb record already asks for the reason behind a cut: `## Cuts` in `discovery.md`,
`## Out of scope` and _revisit_ in `spec.md`. What is missing is a place for those items once
the work is over. This skill gives them one, `.bb/<slug>/backlog.md`, and keeps it short: an
item gets in only when someone weighed it and wants it back, or when it has evidence of value
to the user.

The file is a member of the `.bb/<slug>/` contract (plugin-level `references/spec-state.md`),
and this skill is its only writer.

## Pick the mode

The person's words decide it. Both modes can run in one session.

| the person says                                             | mode    | reference                   |
| ----------------------------------------------------------- | ------- | --------------------------- |
| "organize the backlog", "what did we leave out", a slug     | harvest | `references/destination.md` |
| "park this", "note this for later", in the middle of a task | capture | `references/capture.md`     |

## Harvest the records

1. **Read the folder.** Run `python3 scripts/harvest.py`, with `--slug SLUG` when the person
   named one. It prints JSON: per slug, the spec's `status` and `wave` key, the discovery's
   `verdict`, the items and the alerts. It writes nothing.
2. **Pick the slugs.** With no slug named and more than one in the result, show one line per
   slug (its status and how many items are not `in_backlog` yet) and ask which to harvest in
   one `AskUserQuestion`. Lead with the slugs whose spec ended or went stale.
3. **Show the alerts first.** A `stale_spec` alert is a pending spec older than 14 days; when
   it has no `wave` key, say the plan exists only in this file. A `near_duplicate` pair is the
   same idea written twice: keep one entry and cite both sources.
4. **Place each item** under `references/destination.md`. An item with no reason beside it gets
   its reason from the spec's `## Decisions` before you ask the person.
5. **Confirm once.** Show the table of items and their sections, then one `AskUserQuestion`:
   **Write it as shown** (recommended), **Adjust items**, or **Stop**.
6. **Write `backlog.md`** in the format the reference gives, adding to what is there. An item
   with `in_backlog: true` is already written or already skipped: leave it. An item that stays
   out gets its id on the file's `<!-- skipped -->` line, so the next harvest skips it too.

## Capture from the conversation

Run `references/capture.md`. It holds the two doors an item has to pass and what stays out.

## Close

Report how many items went to each section and the path of every `backlog.md` written, then
stop. This skill has no gate: the file waits for the next round of work on that slug.
