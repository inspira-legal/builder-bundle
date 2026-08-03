# Front: quality — one finder, all cleanup lenses

The criteria are the plugin-root `references/quality-checklist.md` — the single
source of truth shared with `/bb:ship`, so a diff is judged identically wherever
it's reviewed. This front is **strictly behavior-preserving**: same inputs, same
outputs, same side effects. Bugs belong to `front-correctness.md`.

One finder covers all six lenses (they overlap heavily; splitting them into six
agents buys duplicate candidates, not coverage). Cap: 10 candidates, prioritizing
the highest-cost ones across lenses — no obligation to produce a finding per lens.

## The lenses

- **Reuse** — new code re-implementing something the codebase already has. Grep
  shared/utility modules and the files adjacent to the change, then name the
  existing helper to call instead. A "duplicate" you didn't search for is a guess.
- **Simplification** — complexity the diff adds: redundant or derivable state,
  copy-paste with slight variation, deep nesting, needless indirection, a
  flag/param with a single caller. Name the simpler form that does the same job.
- **Dead weight** — unused imports, variables, branches introduced by the branch;
  leftover debug code; commented-out code.
- **Efficiency** — wasted work the diff introduces: redundant computation,
  repeated I/O or queries inside a loop, independent operations run sequentially,
  blocking work added to startup or a hot path. Also long-lived objects built from
  closures or captured environments — they keep the whole enclosing scope alive
  for the object's lifetime, which is a leak when that scope holds large values;
  a struct/class copying only the fields it needs is the cheaper form.
- **Altitude** — the change implemented at the wrong depth or the wrong layer:
  project-specific logic in a shared module, reusable logic buried in a feature
  folder, special cases stacked on shared infrastructure where generalizing the
  underlying mechanism is the real fix.
- **Consistency** — naming, error envelopes, and patterns diverging from
  neighboring code.

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
