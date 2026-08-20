# Spec state: the `.bb/<slug>/` contract

The single on-disk contract for a slug's durable artifacts. **Every skill writes its
own document, and `spec.md` has exactly one writer.** `/bb:discover` writes
`discovery.md`, `/bb:brisar` writes `design.md`, `/bb:spec` writes `spec.md`, and
`/bb:implement`, `/bb:ship` and `/bb:delegate` read the spec. Any skill that reads or
writes this state follows this file. The contract lives here and nowhere else.

## Location

`.bb/<slug>/` is the slug's folder; `<slug>` is a short kebab name matching the dir,
and everything durable about that work lives inside it:

```
.bb/<slug>/
├── discovery.md   # the framing, /bb:discover
├── spec.md        # the contract, /bb:spec, single writer
├── design.md      # the journey and the prototype record, /bb:brisar
└── prototype/     # the clickable artifact, /bb:brisar Develop
```

- **Three documents, three writers, one each.** `discovery.md` answers _is this worth
  building, and what did we cut?_; `design.md` answers _how should this be, and why,
  and what got built?_; `spec.md` answers _what exactly do we build?_. They coexist,
  and none of them replaces another.
- **The two records are read by path, never copied.** When the spec needs a fact that
  lives in a record, it cites the document and the section, and the reader opens it. A
  section quoted into the spec is a second copy that goes stale the next time its own
  skill runs.
- **`prototype/` is the only non-document member.** It holds a clickable prototype
  brisar's Develop phase built: the journey's screens, their states, the DS tokens
  applied. It is not the product's code, which is `/bb:implement`'s output and lives in
  the project.
- Members are independent. A brisar run that never went through `/bb:discover` leaves a
  folder with `design.md` and no `spec.md`; a specced idea that never touched design has
  only `spec.md`.
- The `.bb/` root is the nearest ancestor of the cwd that already has one; if none
  does, it is created in the cwd. **Resolve it that way every time**. A bare relative
  `.bb/` mints a second root whenever a skill runs from a subfolder, and the slug's
  members end up in different trees.
- **The folder may be a symlink into a canonical store** (the pattern used when a
  project's specs live outside the repo). Read through it and write to the canonical
  target. The Edit tool refuses to write through a symlink on purpose, and that refusal
  is what stops a copy being born in the repo. Two obligations: the in-repo path stays
  in place as the symlink, because every reader and every resumption glob names
  `.bb/<slug>/…`; and **all** members travel together, `prototype/` included, so a spec
  written to the canonical store cannot leave its `design.md` or its prototype folder
  behind in a local `.bb/`.

## Reversal: the spec wins, the record's writer registers it

Where a record and the spec disagree, **`spec.md` wins**: the records record, the spec
is the contract. The correction runs one way only. `/bb:spec` never edits `discovery.md`
or `design.md`, because that would give a document two writers, which is the disease
this contract cures. The record's **own writer** registers the reversal on its next
round, as a reversal (_"revokes D4, per the spec"_), so the history stays readable and a
stale record never silently outranks the contract.

## Frontmatter

**Every document carries its own frontmatter, and none of them is a state file.** What a
later session needs to know about a document is written at the top of that document, so
there is nothing beside them to keep in sync and nothing outside `.bb/<slug>/` to read
first.

**`spec.md`** opens with:

```yaml
---
status: pending # pending | in-progress | done | blocked
created: 2026-07-23 # YYYY-MM-DD, set when the spec is first written
slug: <kebab-slug> # matches the dir name
---
```

- `pending`: no task done yet.
- `in-progress`: some tasks done, not landed (resumable).
- `done`: the implement→ship chain completed its landing.
- `blocked`: implement's safety valve or ship hit an unrecoverable stop; needs a human.

**`/bb:delegate` owns the `status` lifecycle**: it flips the value as it selects, runs
and lands a spec. `spec` only writes the initial block (`status: pending`) on finalize.
The `## Tasks` checkboxes inside the spec stay `implement`'s concern. A spec without the
block is treated as `pending` with unknown `created` (sorted last in bare selection).

**`discovery.md`** opens with the framing's block (the contract is
`${CLAUDE_PLUGIN_ROOT}/skills/discover/SKILL.md`):

```yaml
---
slug: <kebab-slug>
created: 2026-08-20
phase: frame | fit | done
verdict: build-mvp | validate-first | pivot | persevere | shelve # omitted before Phase 2
---
```

**`design.md`** opens with the journey's block (the contract is
`${CLAUDE_PLUGIN_ROOT}/skills/brisar/references/brief.md`, which owns the full
`surfaces` shape):

```yaml
---
status: in-progress | bootstrapped-to-discover | completed
phase: research | brief | diverge | medium | develop | deliver | done
round: 1
slug: <kebab-slug>
created: <ISO>
canonical: <absolute path actually written, when the folder is a symlink; else omitted>
medium: code | claude-design | paper | figma | pencil
surfaces: # the locator Deliver reviews against, and the document's own index
  - name: <surface>
    artifact: <path under prototype/, or file + page + artboard on a canvas>
    states_built: [default, empty, loading, error]
    states_not_built: [<state>]
    variants: [<variant>]
    deviations: [<what departed from the direction, and why>]
wcag_aa_status: pass | fail | partial | not-assessed
blockers: [<what has to be fixed before merge>]
---
```

Those two `status` and `phase` values are their own document's, not the spec's.
`/bb:delegate` selects on `spec.md`'s block and neither reads nor writes the records'. A
`design.md` with no frontmatter reads as `phase: brief`, `round: 1`,
`status: in-progress`.

**The sections inside a record replace, they do not accumulate.** `.bb/` is tracked in
git, so the history of rounds is `git log`, and each document carries the current state.

## Upstream records (discover → spec)

`/bb:discover` writes `## Problem` / `## Hypothesis` (problem framing) and `## Fit` /
`## Cuts` (appetite & scope) into **`discovery.md`**, and never touches `spec.md`.
`/bb:spec` reads them as the intent this work serves, echoes the framing in one line,
and drafts the spec on top; `## Cuts` is also read from there by `/bb:review`'s contract
front, and `## Hypothesis` by spec's export mode. Those four names inside a `spec.md`
are dead section names, and `scripts/lint_spec.py` fires `E003` on them pointing here.
The spec's own format is
`${CLAUDE_PLUGIN_ROOT}/skills/spec/references/spec-format.md`.
