---
status: done
created: 2026-08-20
slug: frente-de-design
---

# review gains a design front

`/bb:review` runs seven fronts, and none of them checks the design system. The closest
neighbor is accessibility, which explicitly hands design-system contract violations to
the `rules` front, and `rules` only exists where a `CODE_REVIEW_GUIDE.md` does. So a
diff that paints a raw hex where a token exists, or rebuilds a button the DS already
ships, passes review clean unless someone happens to notice. The design journey has a
review of its own (brisar's Deliver phase), but it lives inside the journey; a change
that never went through brisar never meets it.

This adds the eighth front: `design`, deviations from the design system the project
actually has. Same engine as every other front, one finder, the barrier, an independent
verifier, and the same citation discipline as `rules`: a finding is worth what its
citation is worth, so every finding names the source it deviates from, a token file and
line, a component path, or the branch's own visual direction. Like the accessibility
front, it runs in two scopes: over the diff inside a review, and standalone over a
surface the user points at (a folder, files, or a running page), which is the design
review loop on its own.

## What it judges against

The front resolves the project's design source before it offers itself, in this order:

1. A token source the project itself reads: a `tokens.json`, CSS custom properties, or
   a Tailwind theme config; in a brisar prototype, the `tokens*.css` under
   `.bb/<slug>/prototype/src/`.
2. The branch's `.bb/<slug>/design.md` (or `design/<surface>.md`), the visual
   direction, which supplements the token source with intended hierarchy and states.

Nothing resolving makes the front unavailable, the same way no `CODE_REVIEW_GUIDE.md`
makes `rules` unavailable: a design review with no source to cite is opinion, and the
engine does not ship opinion.

## Boundaries with the neighboring fronts

- Contrast, accessible names, keyboard and focus stay with `a11y`. A color that breaks
  the palette is a design finding even when its contrast passes.
- Generic code reuse stays with `quality`. When the duplicate is a DS component, the
  finding is design's and cites the component it rebuilds.
- Copy and voice stay with brisar's Deliver phase, which reads the brand references.

## Behavior

| WHEN                                                        | THEN                                                              |
| ----------------------------------------------------------- | ----------------------------------------------------------------- |
| the diff touches UI and a design source resolves            | the `design` front is offered at the fronts question              |
| no design source resolves                                   | the front is not offered; the report does not mention it          |
| the diff paints a raw value where a token exists            | a finding, citing the token file and line                         |
| the diff rebuilds a component the DS ships                  | a finding, citing the component's path                            |
| the diff builds interaction missing states the DS documents | a finding, citing where the states are documented                 |
| a deviation has no source to cite                           | it is dropped, not reported as a guess                            |
| the user names a surface and asks for a design review       | the front runs standalone: no diff, no other fronts, its own gate |
| the surface scope has a running page                        | computed styles settle what source alone cannot                   |
| drift exists in lines the branch never touched              | one closing line as existing debt, never an item to fix here      |

## Decisions

- The front is `/bb:review`'s, in the engine, not a new skill and not a brisar-only
  loop: two entry points (the fronts question and the standalone surface ask), one
  method.
- The citation discipline is the `rules` front's, applied to design sources: every
  finding cites what it deviates from, and an uncitable finding is dropped.
- The source resolution is the front's own three-rung ladder over the repo. It does
  not borrow brisar's research (five rungs, remote reads): a review front judges
  against what the repo carries, and a source the repo does not carry cannot be cited.
- Priorities are High (the source explicitly forbids it, or a second source of truth
  ships, like a rebuilt component), Medium (a raw value where a token exists), Low
  (drift inside a scale that still reads fine).
- The depth table funds it like `a11y`: inline on a small diff, one finder otherwise,
  on Sonnet unless the run is deep.
- brisar's Deliver gate keeps offering `/bb:review` as its audit door, now naming the
  design front next to accessibility.

## Tasks

- [x] **1. The criteria**: `references/design-checklist.md`, tokens, components,
      states, consistency, and the citation rule → behaviors 3, 4, 5, 6 · dep: — ·
      verify: reading
- [x] **2. The front**: `references/front-design.md`, two scopes, the source ladder,
      the finding shape, the boundaries → behaviors 2, 7, 8, 9 · dep: 1 · verify:
      reading
- [x] **3. The catalog**: `references/fronts.md` gains the row, the probe, and the
      depth column → behavior 1 · dep: 2 · verify: reading
- [x] **4. The router**: review's `SKILL.md` routes the standalone ask, groups the
      report, lists the references, and the description carries the triggers
      → behaviors 1, 7 · dep: 3 · verify: reading
- [x] **5. The doors**: README's review row and brisar's Deliver gate name the front
      → behavior 7 · dep: 4 · verify: reading

## Out of scope

- A design front that reads Figma or Paper files through their MCPs. The review
  engine's finders are read-only over the repo and a rendered page; auditing a canvas
  stays with brisar's Deliver, which owns the reader per medium.
- Blocking severity semantics shared with brisar's Deliver (blocker, significant,
  divergence). The review report ranks by its own three levels; the Deliver review is
  a different document with a different reader.
- Autofixing design findings beyond the existing apply step. `act-apply-fixes.md`
  already governs how a picked finding is applied.

## Open

Nothing.
