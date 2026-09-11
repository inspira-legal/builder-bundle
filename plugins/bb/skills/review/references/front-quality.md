# Front: quality, one finder, all cleanup lenses

The criteria are its sibling `quality-checklist.md`, the single source of truth
for what a quality finding is, so a diff is judged identically on every run. This
front is **strictly behavior-preserving**: same inputs, same
outputs, same side effects. Bugs belong to `front-correctness.md`.

One finder covers all six lenses (they overlap heavily; splitting them into six
agents buys duplicate candidates, not coverage). Cap: 10 candidates, prioritizing
the highest-cost ones across lenses, no obligation to produce a finding per lens.

## How to read the lenses

The six (reuse, simplification, dead weight, efficiency, altitude, consistency)
are defined in the shared checklist; read them there rather than from a copy here.
What this front adds is how to _hunt_ with them:

- **Search before concluding.** A "duplicate" you didn't grep for is a guess: check
  the shared/utility modules and the files adjacent to the change, then name the
  existing helper to call instead.
- **Name the replacement, not the complaint.** Every candidate says what the simpler
  form is: the helper to call, the flattened conditional, the param to drop.
- **Only what the diff introduced.** The checklist's scope rule is the filter:
  untouched code the branch merely sits next to isn't this front's work.

## Finding shape

```
# | file:line | smell | custo concreto | edit sugerido
```

Every finding here is a **Sugestão**, the front being behavior-preserving: the
plugin-root `references/finding-levels.md` maps it that way and this front assigns no
level of its own.

## Failure scenario, for cleanup

The `failure_scenario` field states the **concrete cost** instead of a crash:
what exactly is duplicated (and where the existing helper is), what work is
wasted per call, what a future editor has to keep in sync. "This could be more
limpo" is not a cost.

That column is also the **gate** `finding-levels.md` reads: a Sugestão naming a
concrete cost can be posted as an inline comment, one that cannot goes into a single
aggregated line in the review body. It still gets its full line in the report either
way, so writing the cost is what decides whether GitHub sees the finding.

## Hold back when the cleanup hurts

The over-simplification guard in the shared checklist applies here: an edit that
merges separate concerns to save a definition, removes an abstraction that
genuinely organizes the code, or trades legibility for line count is a defect
dressed as a cleanup. Flag the idea instead of proposing the edit.
