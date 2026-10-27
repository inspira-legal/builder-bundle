# Destination: where each harvested item goes

`harvest.py` hands over the items. This page decides, for each one, the section of
`backlog.md` it lands in, or that it lands nowhere. Its sections follow below: the three
sections, the items that stay out, and the file's format.

## The three sections

| section             | what goes there                                                              |
| ------------------- | ---------------------------------------------------------------------------- |
| `## Next version`   | items someone wants back, each with the trigger that brings it back          |
| `## No trigger yet` | items worth keeping that nobody tied to a moment yet                         |
| `## Discarded`      | items cut for good, with the reason, so the next spec sees they were weighed |

Place an item by what its record says:

- **A _revisit_ with a trigger**: `## Next version`, with the trigger as written.
- **A _revisit_ whose trigger can never fire**: `## Next version`, rewritten as the work that
  makes it possible. A sunset that waits for "parity" while `## Open` says parity was never
  defined becomes "define what parity means".
- **An out of scope item that breaks the spec's own promise**: `## Next version`, even with no
  trigger. A spec titled "never leave the user stuck" that leaves one channel without the exit
  owes that channel.
- **Debt that degrades what shipped**: `## Next version`, first in the list, marked `debt`.
- **An unticked task of an ended spec**: `## Next version` when the person still wants it,
  `## Discarded` with their reason when not. `harvest.py` lists these only once the spec is
  `done` or `blocked`, or the discovery shelved the idea.
- **A cut or out of scope item with no _revisit_ and a reason to drop it**: `## Discarded`.
- **Anything else worth keeping**: `## No trigger yet`.

An item that carries an `ice` value keeps it, with the date of the record it came from
(`ICE 7, 2026-09-22`). The score ages, and the date tells the next spec to score it again.

## What stays out

- **Work a later task absorbed.** Read the spec's `## Tasks` and the slug's other records
  before you write: a cut that came back as a task is not a leftover.
- **A deferred decision.** An `## Open` line that a task already owns is the plan, not the
  backlog. An `## Open` line only gets in when it names work nobody owns, like a mode no route
  reaches.
- **The second copy of a `near_duplicate`.** Keep one entry and cite both sources on it.

## The format

```markdown
---
slug: <slug>
updated: <YYYY-MM-DD>
---

# Backlog: <slug>

## Next version

- **<title>**: <one line on what it is>. Trigger: <trigger>. From `<source>`, <door>. <!-- id:<id> -->

## No trigger yet

- **<title>**: <one line>. From `<source>`, <door>. <!-- id:<id> -->

## Discarded

- **<title>**: <reason>. From `<source>`. <!-- id:<id> -->
```

- **`<source>`** is the item's `source` field from `harvest.py`, such as
  `spec.md#out-of-scope:220`. The line cites the record, it never copies the record's reasoning.
- **`<door>`** says why the item is here: `cut` for a harvested item, `interest` or
  `value: <source>` for a captured one (`references/capture.md`).
- **`<!-- id:<id> -->`** is the item's `id` from `harvest.py`. It is what makes the next
  harvest skip the item, so never drop it. A captured item has no id; it carries
  `<!-- captured <YYYY-MM-DD> -->` instead.
- Leave out a section that has no items.
