# Quality Checklist

The canonical quality pass over the code a branch changed — the single source of
truth shared by `ofc:improve-code` (standalone) and `ofc:ship`'s Pass 2, so a diff
is judged identically wherever it is reviewed. **Quality only, strictly
behavior-preserving** — finding or fixing bugs is correctness review (ship's Pass
1), not this.

Read every hunk with its surrounding context (open the file, not just the diff)
before judging it.

**Scope rule:** only touch code already changed by this branch — do not refactor
untouched code "while at it".

**Behavior rule:** zero behavior change. Same inputs, same outputs, same side
effects. A "simplification" that changes what the code does is a regression.

**Clarity rule:** clarity over brevity. Explicit, readable code beats clever or
compact code — never trade legibility for fewer lines (no nested ternaries, no
dense one-liners). Prefer a `switch` or an `if`/`else` chain over stacked
ternaries for multiple conditions.

## The six criteria

- **Reuse** — logic duplicated within the diff, or re-implementing a helper that
  already exists in the codebase (search before concluding it doesn't).
- **Simplification** — collapse needless indirection, flatten over-nested
  conditionals, remove flags/params with a single caller.
- **Dead weight** — unused imports/variables/branches introduced by the branch,
  leftover debug code, commented-out code.
- **Efficiency** — obvious O(n²) over collections that can be O(n), repeated I/O
  or queries inside loops, recomputing invariants per iteration.
- **Altitude** — code placed at the wrong layer (e.g. project-specific logic in
  shared, or reusable logic buried in a feature folder), respecting the project's
  stated architecture conventions.
- **Consistency** — naming, error envelopes, and patterns matching what
  neighboring code does.

## Maintain balance — over-simplification is its own defect

A cleanup that hurts the code is not a cleanup. Hold back when an edit would:

- combine separate concerns into one function/component just to save a definition,
- remove a helpful abstraction that genuinely organizes the code,
- make the code harder to debug, extend, or read, or
- buy a marginal line count at a real cost to clarity.

When in doubt, leave the code and flag the idea instead of applying it silently.

## After each edit

Re-run the relevant local check (lint / typecheck / tests for the touched area).
A simplification that breaks behavior is a regression, not a cleanup.
