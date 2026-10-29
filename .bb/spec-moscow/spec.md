---
status: done
created: 2026-10-28
slug: spec-moscow
---

# /bb:spec cuts the version and reads the backlog

`/bb:backlog` gives a place to what the work left for later, but it reads `## Out of scope` as
free text: whether an item comes back or was dropped for good is a guess the skill makes from the
wording. And nothing brings a parked item back. The next spec on the same area starts from the
one-liner and never opens `backlog.md`.

This change closes the loop on the spec side. The spec ends its phasing with a MoSCoW cut, so
every item it leaves out is born typed: `_revisit_` with the trigger that brings it back, or
`_discarded_` with the reason. And the spec reads the backlog before drafting, so an item whose
trigger fired reaches the person as a gray area.

## The cut

The deadline MoSCoW sorts against is the version this spec builds:

- **Must**: the tasks the version cannot stand without. They are the phases.
- **Should and Could**: in the version when they fit, in the last phases. What does not fit
  moves to Won't when the spec closes.
- **Won't, this time**: a bullet in `## Out of scope` marked _revisit_, followed by the trigger
  that brings it back. A trigger, not a version number: a "v3" named today is a roadmap promise
  that ages before v2 ships.
- **Won't, for good**: a bullet in `## Out of scope` marked _discarded_, followed by the reason.

The MoSCoW words stay in the conversation. The spec carries the result: the tasks, and two
markers in `## Out of scope`, which is what `/bb:backlog` reads.

## Decisions

- The cut runs at the end of step 5 of the loop, after the phases are ordered. The person
  confirms it in the same `AskUserQuestion` batch as the last gray areas.
- `## Out of scope` bullets carry one of two markers: _revisit_ plus a trigger, or _discarded_
  plus a reason. _revisit_ keeps its name, so the specs already landed stay valid.
- The lint warns (`W009`) on an `## Out of scope` bullet with neither marker. A warning, not an
  error: the corpus has specs written before the rule, and the person decides at the gate.
- The spec reads `.bb/<slug>/backlog.md` and the `## Next version` of the other slugs'
  `backlog.md` before drafting. An item whose trigger fired becomes a gray area the person
  decides; it never enters the draft on its own. The spec cites it by path and never writes the
  backlog.
- `harvest.py` returns a `discarded` flag beside `revisit`, so the backlog places a _discarded_
  item without reading the wording.

## Behavior

1. The person runs `/bb:spec` on an idea.
2. The skill reads the upstream records, the backlog among them, and turns the items whose
   trigger fired into gray areas.
3. The loop orders the phases, then proposes the cut; the person confirms it.
4. The lint runs, and the gate shows the cut beside the phases.
5. Later, `/bb:backlog` places each _revisit_ in `## Next version` and each _discarded_ in
   `## Discarded`.

| when                                                      | then                                                       |
| --------------------------------------------------------- | ---------------------------------------------------------- |
| WHEN no `backlog.md` exists anywhere                      | THEN the spec drafts as before, with no backlog line       |
| WHEN a backlog item's trigger has not fired               | THEN it is not raised                                      |
| WHEN a backlog item's trigger fired and touches this idea | THEN it is asked as a gray area, never drafted in silently |
| WHEN every Should and Could fits the version              | THEN `## Out of scope` holds only what was always out      |
| WHEN an `## Out of scope` bullet has neither marker       | THEN the lint prints `W009` and exits 0                    |
| WHEN a bullet says _revisit_ with no trigger after it     | THEN the lint stays quiet; the gate shows the item         |
| WHEN `## Out of scope` is `Nothing.`                      | THEN the lint stays quiet                                  |
| WHEN `harvest.py` reads a _discarded_ bullet              | THEN the item has `discarded: true`                        |

## Metric

skipped: the cycle's measures (share of new specs that pull a backlog item, share of parked
items picked up within 90 days) need several specs over time; they are read by hand on the
next round of the backlog.

## Attention points

- The whole corpus is linted when `lint_spec.py` changes, so `W009` prints on every spec landed
  before the rule. Warnings exit 0, but the CI log grows.
- The marker is matched in emphasis (`_revisit_`, `*discarded*`); a bare word in the prose must
  not count, or a sentence that mentions "revisit" silences the warning.

## Tasks

### Spec side

- [x] **1. The cut**: step 5 of `SKILL.md` closes the phasing with the MoSCoW cut, the gate
      shows it, and `spec-format.md` defines the two markers. · verify: reading
- [x] **2. Read the backlog**: "Read the upstream records first" reads `backlog.md`, and
      `spec-state.md` names the spec as its reader. · verify: reading
- [x] **3. W009**: `lint_spec.py` warns on an unmarked `## Out of scope` bullet, with the code in
      the lint table. · verify: the lint over this spec and over a sample with each case

### Backlog side

- [x] **4. The discarded flag**: `harvest.py` returns `discarded`, `destination.md` places it,
      and a test covers it. · verify: `harvest_test.py`
- [x] **5. Release**: version, changelog. · verify: `bun run validate`

## Out of scope

- The tracker side of the backlog (the `bb-backlog` label in Wave): it waits for `/bb:backlog`
  to sync with the tracker. _revisit_ when `/bb:backlog` writes to Wave.
- MoSCoW in `/bb:discover`'s `## Cuts`: discover is optional, and the cut belongs where every
  piece of work passes. _discarded_ because the spec is the one record every slug has.
- Rewriting the landed specs to carry the markers. _discarded_ because `W009` is a warning, and a
  spec gets the markers the next time its own round touches it.

## Open

Nothing.
