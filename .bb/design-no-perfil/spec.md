---
status: done
created: 2026-08-20
slug: design-no-perfil
---

# the profile learns how the person designs

`/bb:profile` calibrates how bb explains things, and nothing else. The four flags say
whether the person reads code, runs commands, wants steps spelled out and tolerates
jargon, but a design journey learns nothing from them about the one habit it needs:
which design tools are part of the person's day. So `/bb:brisar` re-derives it on every
journey from detection alone, and the medium question (code, Claude design, Figma,
Paper or Pencil) opens every time as if the person had never answered it.

The habit is a fact about the person, exactly the kind of fact the profile exists to
hold. This change adds it there, and adds the project-level counterpart: a product in
the registry can lean the same question toward one medium, because some products have a
settled design workflow that outranks any one person's habit. Neither level answers the
question for the builder. The medium is still always asked; what the two levels set is
the order the options arrive in and which one carries the recommendation.

## The two levels and who wins

The person's habit lives in `~/.claude/bb.config.json` as `profile.design_tools`, a
list drawn from `figma`, `paper` and `pencil`. Code and Claude design are not in the
list because they need nothing and are always offered. An empty list is an answer, the
person works without canvas tools; a missing list is a profile written before this
question existed, and reads as not asked, never as "none".

The product's lean lives in `references/product-registry.yaml` as an optional
`medium_default` on the product entry. When the cwd resolves to a product that carries
one, that medium is offered first, above the person's habit, because a product with a
settled design workflow settles it for everyone who works on it. With no product match
or no `medium_default`, the person's habit orders the list. With neither, the ordering
stays what `phase-medium.md` already does: fit signals from the direction and the
profile's `reads_code`.

## Behavior

The happy path: the person runs `/bb:profile`, answers the four communication
questions, then answers one more, which canvas tools are part of their day. The config
gains `design_tools`, the writer renders one extra line into the profile block of
`~/.claude/BUILDER-BUNDLE.md`, and the next `/bb:brisar` journey that reaches the
medium question puts what they use first.

| WHEN                                                              | THEN                                                                                |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| `/bb:profile` calibrates                                          | a second multiSelect asks which of Figma, Paper, Pencil are their day               |
| the person checks nothing on the design question                  | `design_tools: []` is written; it is an answer, not an omission                     |
| a config written before this change is read                       | `design_tools` missing reads as not asked; no line is rendered                      |
| the writer renders a profile with `design_tools` present          | the profile block carries one design line after the four flag lines                 |
| the medium question runs with a habit on file                     | the person's tools come first among the offered options                             |
| the medium question runs and the product carries `medium_default` | that medium comes first, above the habit, and the intro line says so                |
| the habit names a tool whose MCP the preflight did not find       | the intro line names it once; the option is not offered, nothing blocks             |
| more options qualify than the question tool holds                 | the product default, then the person's tools survive; the rest go to the intro line |
| `/bb:profile` shows an existing profile                           | the design answer prints as a sentence next to the four                             |

## Decisions

- The habit is stored per person in `profile.design_tools`, not per project: it is a
  fact about the person, the same argument that moved the four flags there.
- The values are `figma`, `paper` and `pencil` only. Code and Claude design need no
  MCP and no habit; listing them would make absence ambiguous.
- Missing and empty are different answers. Missing means the question was never asked
  (an older config) and renders nothing; empty means the person answered "none" and
  renders a line saying canvas tools are not their day.
- The product's `medium_default` outranks the person's habit in ordering, because a
  product with a settled design workflow settles it for everyone who works on it.
- Neither level ever skips the medium question. brisar's principle stands: the medium
  is always asked, and the levels only set the order and the recommendation.
- The writer renders the design line inside the existing profile block, not as a new
  section: the frame already names that block as what closes it.

## Tasks

- [x] **1. Config contract**: `references/bb-config.md` gains `design_tools` in the
      schema, the missing-versus-empty rule, and its row in the readers table
      → behaviors 2, 3 · dep: — · verify: reading
- [x] **2. Profile asks it**: `/bb:profile` gains the design question, prints it on
      show, and writes it on calibrate → behaviors 1, 2, 9 · dep: 1 · verify: reading
- [x] **3. Writer renders it**: `hooks/sync_instructions.py` renders the design line,
      one for a habit, one for none, nothing when unasked
      → behaviors 3, 4 · dep: 1 · verify: run the script over each config shape
- [x] **4. Medium question leans**: `phase-medium.md` orders by product default, then
      habit, then fit; the trim keeps the product default and the person's tools
      → behaviors 5, 6, 8 · dep: 1 · verify: reading
- [x] **5. Preflight names the gap**: `preflight-tooling.md` gains the row for a habit
      tool with no MCP → behavior 7 · dep: 4 · verify: reading
- [x] **6. Registry carries the lean**: `product-registry.yaml` documents the optional
      `medium_default` → behavior 6 · dep: — · verify: reading

## Out of scope

- Auto-answering the medium question from the habit, even when profile and detection
  agree. The question stays, by brisar's own principle.
- A per-repo design preference outside the product registry (a `.bb/` level default).
  Revisit if per-project leans turn out to be needed on repos the registry never lists.
- Asking the design question inside `/bb:brisar` when the profile predates it. The
  journey reads the config as not asked and proceeds on detection, and the person
  recalibrates through `/bb:profile` when they want the lean.

## Open

Nothing.
