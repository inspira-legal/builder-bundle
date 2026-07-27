# Applying findings — the regression guard

Applying a review finding is where a review can _cause_ the next bug. This pass
is deliberately conservative: a cleanup that changes behavior is a defect, not an
improvement, and a "fix" that isn't justified against its finding is a guess.

## The guard (the #1 rule)

- **One change at a time.** Apply edits incrementally and re-run the relevant
  local check (lint / typecheck / tests for the touched area) after each, so a
  regression is isolated to a single edit and caught immediately — never batch a
  pile of edits and check once at the end.
- **Justify before you touch.**
  - A **correctness fix** must map to its finding: state the triggering
    input/scenario the finding named and how the edit closes it.
  - A **quality edit** must be behavior-preserving: same inputs → same outputs →
    same side effects. If you can't say why, don't make it.
- **Untested code is higher-risk.** If the touched code has no test covering it,
  keep edits trivial and obvious, add a quick characterization test first, or
  **leave it and flag it** — do not rework untested logic on faith.
- **Watch the classic traps** that turn an edit into a regression: changed
  evaluation / short-circuit order; truthiness or coercion shifts when collapsing
  conditionals; removing "dead" code that actually has side effects; merging
  error handling so different errors now propagate the same; altering async
  timing/ordering; off-by-one when refactoring a loop or slice.
- **When in doubt, leave it and flag it.** A missed cleanup costs nothing; a
  regression costs trust.

## Order of operations

1. Correctness fixes first (highest severity first), then quality edits — a
   quality pass over code about to be fixed is wasted work.
2. Scope stays the code this branch already changed — no refactoring untouched
   code "while at it" (the scope rule in the plugin-root
   `references/quality-checklist.md`).
3. Match the surrounding naming, error envelopes, and patterns.
4. Commit in logical units (conventional style, no AI attribution). With an open
   PR, push to the PR branch; thread replies happen after the push so the sha is
   real.
5. At the end, re-run the full local gate (reuse the project's check commands —
   CLAUDE.md / CI workflows / package scripts) and include the result in the
   re-report.

Anything held back as too risky goes in the re-report as flagged, not silently
dropped.
