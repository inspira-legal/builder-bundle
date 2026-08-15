# Spec state — the `.bb/<slug>/` contract

The single on-disk contract for a spec's durable artifacts. The spec is written by
`/bb:spec` (and seeded by `/bb:discover`), consumed by `/bb:implement`, `/bb:ship`
and `/bb:delegate`; the visual direction is written by `/bb:brisar`. Any skill that
reads or writes spec state follows this file — the contract lives here and nowhere
else.

## Location

`.bb/<slug>/` is the spec's folder — `<slug>` is a short kebab name matching
the dir, and everything durable about that work lives inside it:

```
.bb/<slug>/
├── spec.md              # the spec — /bb:discover seeds, /bb:spec finalizes
├── brief-design.md      # the design brief — /bb:brisar first diamond
├── design.md            # visual direction, single surface — /bb:brisar Phase 4
└── design/              # …or one file per surface, when there is more than one
    ├── README.md        # index + suggested drawing order
    └── <surface>.md
```

- `design.md` and `design/` are the same artifact in two shapes: one surface writes
  the flat file, two or more write the folder. A slug never has both.
- **`brief-design.md` is a different artifact from both.** It is the design brief —
  the research record, the reconciliation against the framing, the directions and the
  chosen one. `spec.md` answers _is it worth building, and what did we cut?_;
  `brief-design.md` answers _how should this be, and why?_; the design files say what
  each surface looks like. The two documents **coexist** — neither replaces the other,
  and where they disagree **`spec.md` wins**, because the design brief is a record and
  the spec is the contract.
- Members are independent. A brisar run that never went through `/bb:discover`
  leaves a folder with design and no `spec.md`; a specced idea that never touched
  design has only `spec.md`.
- **`.bb/tasks/<slug>/` is the layout this folder had before, and it still resolves.**
  A named slug reads `.bb/<slug>/spec.md` and falls back to `.bb/tasks/<slug>/spec.md`;
  bare selection (`/bb:delegate` with no slug) scans `.bb/*/spec.md` **and**
  `.bb/tasks/*/spec.md` before picking by `created` — a folder without a spec is
  simply not a candidate. A spec still written under the old path — in another repo,
  or in one not migrated yet — is found either way, and the other members resolve
  beside it, in whichever of the two folders the spec was found. The folder's `<slug>`
  is the key: the same slug seen under both paths is one spec, and the `.bb/<slug>/`
  copy is the one read. New work is written to `.bb/<slug>/`.
- The `.bb/` root is the nearest ancestor of the cwd that already has one; if none
  does, it is created in the cwd. **Resolve it that way every time** — a bare relative
  `.bb/` mints a second root whenever a skill runs from a subfolder, and the slug's
  members end up in different trees.
- **The folder may be a symlink into a canonical store** (the pattern used when a
  project's specs live outside the repo). Read through it and write to the canonical
  target — the Edit tool refuses to write through a symlink on purpose, and that refusal
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

`brief-design.md` carries its own, smaller block — it is a record, not a selection
candidate, so it has no `status` for `/bb:delegate` to drive:

```yaml
---
slug: <kebab-slug>
canonical: <absolute path actually written, when the folder is a symlink; else omitted>
---
```

- `pending` — no task done yet.
- `in-progress` — some tasks done, not landed (resumable).
- `done` — the implement→ship chain completed its landing.
- `blocked` — implement's safety valve or ship hit an unrecoverable stop; needs a human.

**`/bb:delegate` owns the `status` lifecycle** — it flips the value as it selects,
runs and lands a spec. `spec` only writes the initial block (`status: pending`) on
finalize. The `## Tarefas` checkboxes inside the spec stay `implement`'s concern. A spec
without the block is treated as `pending` with unknown `created` (sorted last in
bare selection).

## Upstream sections (discover → spec)

`/bb:discover` seeds the spec with `## Problema` / `## Hipótese` (problem
framing) and `## Encaixe` / `## Cortes` (appetite & scope). `/bb:spec` reads them as
the intent this work serves and builds the rest of the spec in the same file — the
upstream sections stay where they are, in the free top half, and the spine
(`## Decisões`, `## Comportamento`, `## Tarefas`, `## Fora de escopo`,
`## Em aberto`) goes below them. The format is
`${CLAUDE_PLUGIN_ROOT}/skills/spec/references/spec-format.md`.

## Both names read the same

The section names are Portuguese, and a spec written before the rename carries the
English one. **Every reader takes both**, one pair per section:

| português           | inglês         | português     | inglês       |
| ------------------- | -------------- | ------------- | ------------ |
| `## Decisões`       | `decisions`    | `## Problema` | `problem`    |
| `## Comportamento`  | `behavior`     | `## Hipótese` | `hypothesis` |
| `## Tarefas`        | `tasks`        | `## Encaixe`  | `fit`        |
| `## Fora de escopo` | `out of scope` | `## Cortes`   | `cuts`       |
| `## Em aberto`      | `open`         | `## Jurídico` | `legal`      |

The task line's dependency field is one field under two spellings — `depende:` and
`dep:` — and reads the same either way.

**Writing is not symmetric.** A new section is written in Portuguese; a section
already on disk keeps the spelling it has. The lint answers an English heading with
`W003` and the Portuguese name to write, and the file stays valid.

A half-migrated spec can carry **both** names for the same thing — `## Tarefas` and
`## tasks` in one file. Read both and treat them as one section, in file order: the
task lines under the English heading are as unbuilt as the ones under the Portuguese
heading, and stopping at the first match would let a run report clean over work it
never did.
