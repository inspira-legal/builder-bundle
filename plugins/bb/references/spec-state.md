# Spec state: the `.bb/<slug>/` contract

The single on-disk contract for a spec's durable artifacts. The spec is written by
`/bb:spec` (and seeded by `/bb:discover`), consumed by `/bb:implement`, `/bb:ship`
and `/bb:delegate`; the visual direction is written by `/bb:brisar`. Any skill that
reads or writes spec state follows this file. The contract lives here and nowhere
else.

## Location

`.bb/<slug>/` is the spec's folder; `<slug>` is a short kebab name matching
the dir, and everything durable about that work lives inside it:

```
.bb/<slug>/
├── spec.md              # the spec, /bb:discover seeds, /bb:spec finalizes
├── brief-design.md      # the design brief, /bb:brisar first diamond
├── design.md            # visual direction, single surface, /bb:brisar Phase 4
├── design/              # …or one file per surface, when there is more than one
│   ├── README.md        # index + suggested drawing order
│   └── <surface>.md
├── develop-notes.md     # the surfaces as built, /bb:brisar Develop
└── design-review.md     # …plus accessibility-checklist.md and handoff.md, Deliver
```

- `design.md` and `design/` are the same artifact in two shapes: one surface writes
  the flat file, two or more write the folder. A slug never has both.
- **`brief-design.md` is a different artifact from both.** It is the design brief:
  the research record, the reconciliation against the framing, the directions and the
  chosen one. `spec.md` answers _is it worth building, and what did we cut?_;
  `brief-design.md` answers _how should this be, and why?_; the design files say what
  each surface looks like. The two documents **coexist**. Neither replaces the other,
  and where they disagree **`spec.md` wins**, because the design brief is a record and
  the spec is the contract.
- Members are independent. A brisar run that never went through `/bb:discover`
  leaves a folder with design and no `spec.md`; a specced idea that never touched
  design has only `spec.md`.
- **`.bb/tasks/<slug>/` is the layout this folder had before, and it still resolves.**
  A named slug reads `.bb/<slug>/spec.md` and falls back to `.bb/tasks/<slug>/spec.md`;
  bare selection (`/bb:delegate` with no slug) scans `.bb/*/spec.md` **and**
  `.bb/tasks/*/spec.md` before picking by `created`. A folder without a spec is
  simply not a candidate. A spec still written under the old path (in another repo,
  or in one not migrated yet) is found either way, and the other members are **read**
  beside it, in whichever of the two folders the spec was found. The folder's `<slug>`
  is the key: the same slug seen under both paths is one spec, and the `.bb/<slug>/`
  copy is the one read. **Writing is where the two paths stop being symmetric**: a new
  member goes to `.bb/<slug>/` even when the spec was found under the old path, while
  an update is written back to the file it was read from. So a reader looks for a
  member in both folders and takes the `.bb/<slug>/` copy when both answer.
- The `.bb/` root is the nearest ancestor of the cwd that already has one; if none
  does, it is created in the cwd. **Resolve it that way every time**. A bare relative
  `.bb/` mints a second root whenever a skill runs from a subfolder, and the slug's
  members end up in different trees.
- **The folder may be a symlink into a canonical store** (the pattern used when a
  project's specs live outside the repo). Read through it and write to the canonical
  target. The Edit tool refuses to write through a symlink on purpose, and that refusal
  is what stops a copy being born in the repo. Two obligations: the in-repo path stays in
  place as the symlink, because every reader and every resumption glob names
  `.bb/<slug>/…`; and **all** members travel together, so a spec written to the
  canonical store cannot leave its `design.md` behind in a local `.bb/`.

## Frontmatter (selection & tracking)

Every **`spec.md`** opens with:

```yaml
---
status: pending # pending | in-progress | done | blocked
created: 2026-07-23 # YYYY-MM-DD, set when the spec is first written
slug: <kebab-slug> # matches the dir name
---
```

**Every member carries its own frontmatter, and none of them is a state file.** What a
later session needs to know about a document is written at the top of that document, so
there is nothing beside them to keep in sync and nothing outside `.bb/<slug>/` to read
first.

`brief-design.md` opens with the journey's block (the contract is
`${CLAUDE_PLUGIN_ROOT}/skills/brisar/references/brief.md`):

```yaml
---
status: in-progress | bootstrapped-to-discover | completed
phase: research | brief | diverge | medium | develop | deliver | done
round: 1
slug: <kebab-slug>
created: <ISO>
canonical: <absolute path actually written, when the folder is a symlink; else omitted>
---
```

That `status` is the journey's, not the spec's. `/bb:delegate` selects on `spec.md`'s
block and neither reads nor writes this one. A brief with no frontmatter reads as
`phase: brief`, `round: 1`, `status: in-progress`.

`design.md`, or `design/README.md` when there is more than one surface, carries the
surfaces list in its own frontmatter: `name`, `file`, `state` and `last_updated` per
surface, with `file` relative to the task folder. The members brisar writes later,
`develop-notes.md`, `design-review.md`, `accessibility-checklist.md` and `handoff.md`,
each summarize themselves the same way.

- `pending`: no task done yet.
- `in-progress`: some tasks done, not landed (resumable).
- `done`: the implement→ship chain completed its landing.
- `blocked`: implement's safety valve or ship hit an unrecoverable stop; needs a human.

**`/bb:delegate` owns the `status` lifecycle**: it flips the value as it selects,
runs and lands a spec. `spec` only writes the initial block (`status: pending`) on
finalize. The `## Tasks` checkboxes inside the spec stay `implement`'s concern. A spec
without the block is treated as `pending` with unknown `created` (sorted last in
bare selection).

## Upstream sections (discover → spec)

`/bb:discover` seeds the spec with `## Problem` / `## Hypothesis` (problem
framing) and `## Fit` / `## Cuts` (appetite & scope). `/bb:spec` reads them as
the intent this work serves and builds the rest of the spec in the same file; the
upstream sections stay where they are, in the free top half, and the fixed sections
(`## Decisions`, `## Behavior`, `## Tasks`, `## Out of scope`, `## Open`) go below
them. The format is
`${CLAUDE_PLUGIN_ROOT}/skills/spec/references/spec-format.md`.

## Both names read the same

A spec written before the rename carries the older section names.
**Every reader takes both**, one pair per section:

| written           | older spelling      | written         | older spelling |
| ----------------- | ------------------- | --------------- | -------------- |
| `## Decisions`    | `## Decisões`       | `## Problem`    | `## Problema`  |
| `## Behavior`     | `## Comportamento`  | `## Hypothesis` | `## Hipótese`  |
| `## Tasks`        | `## Tarefas`        | `## Fit`        | `## Encaixe`   |
| `## Out of scope` | `## Fora de escopo` | `## Cuts`       | `## Cortes`    |
| `## Open`         | `## Em aberto`      | `## Legal`      | `## Jurídico`  |

The task line's dependency field is one field under two spellings, `dep:` and
`depende:`, and reads the same either way.

**Writing is not symmetric.** A new section is written under the name in the left
column; a section already on disk keeps the spelling it has. The lint answers an older
heading with `W003` and the name to write, and the file stays valid.

A half-migrated spec can carry **both** names for the same thing, `## Tasks` and
`## Tarefas` in one file. Read both and treat them as one section, in file order: the
task lines under either heading are as unbuilt as the ones under the other, and
stopping at the first match would let a run report clean over work it never did.
