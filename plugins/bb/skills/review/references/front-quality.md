# Front: quality — one finder, all cleanup lenses

The criteria are the plugin-root `references/quality-checklist.md` — the single
source of truth shared with `/bb:ship`, so a diff is judged identically wherever
it's reviewed. This front is **strictly behavior-preserving**: same inputs, same
outputs, same side effects. Bugs belong to `front-correctness.md`.

One finder covers all six lenses (they overlap heavily; splitting them into six
agents buys duplicate candidates, not coverage). Cap: 10 candidates, prioritizing
the highest-cost ones across lenses — no obligation to produce a finding per lens.

## How to read the lenses

The six — reuse, simplification, dead weight, efficiency, altitude, consistency —
are defined in the shared checklist; read them there rather than from a copy here.
What this front adds is how to _hunt_ with them:

- **Search before concluding.** A "duplicate" you didn't grep for is a guess: check
  the shared/utility modules and the files adjacent to the change, then name the
  existing helper to call instead.
- **Name the replacement, not the complaint.** Every candidate says what the simpler
  form is — the helper to call, the flattened conditional, the param to drop.
- **Only what the diff introduced.** The checklist's scope rule is the filter:
  untouched code the branch merely sits next to isn't this front's work.

## Finding shape

```
# | file:line | smell | custo concreto | edit sugerido
```

## Failure scenario, for cleanup

The `failure_scenario` field states the **concrete cost** instead of a crash:
what exactly is duplicated (and where the existing helper is), what work is
wasted per call, what a future editor has to keep in sync. "Poderia ser mais
limpo" is not a cost.

## Hold back when the cleanup hurts

The over-simplification guard in the shared checklist applies here: an edit that
merges separate concerns to save a definition, removes an abstraction that
genuinely organizes the code, or trades legibility for line count is a defect
dressed as a cleanup. Flag the idea instead of proposing the edit.
