---
name: improve-code
description: Improve the quality of the code this branch changed — reuse, simplification, dead weight, efficiency, altitude, consistency — and apply the cleanups, quality only and strictly behavior-preserving, with a hard regression guard (verify behavior, re-run checks after every edit). Use when the user says "improve this code", "clean this up", "simplify the diff", "tidy this code", "reduce complexity", or "refactor for clarity". Do NOT use to find or fix bugs (that is correctness review — use /ofc:ship), to open a PR (use /ofc:ship), or to touch code this branch did not change.
license: Apache-2.0
metadata:
  author: adapted from Claude Code's /simplify (Anthropic, Apache-2.0), with stricter regression guards, by Athena Briana - github.com/athenabriana
  version: 1.1.0
---

# Improve Code

A focused quality pass over the current change: make it simpler, leaner, and more
consistent **without changing behavior**. The standalone version of `ofc:ship`'s
Pass 2 — reach for it any time, not just when finalizing a PR.

**Quality only.** It does not hunt for or fix bugs. If you want correctness
review, that is Pass 1 of `/ofc:ship` — use that skill. Mixing the two makes
both passes worse.

## Regression guard (the #1 rule)

The built-in `/simplify` is prone to **introducing regressions** while "cleaning
up" — this skill is deliberately conservative. A cleanup that changes behavior is
a defect, not an improvement. So:

- **One change at a time.** Apply edits incrementally and re-run the relevant
  check after each, so a regression is isolated to a single edit and caught
  immediately — never batch a pile of edits and check once at the end.
- **Justify before you touch.** For each edit, be able to say _why_ it is
  behavior-preserving (same inputs → same outputs → same side effects). If you
  can't, don't make it.
- **Untested code is higher-risk.** If the touched code has no test covering it,
  keep edits trivial and obvious, add a quick characterization test first, or
  **leave it and flag it** — do not "simplify" untested logic on faith.
- **Watch the classic traps** that turn a "simplification" into a regression:
  changed evaluation / short-circuit order; truthiness or coercion shifts when
  collapsing conditionals; removing "dead" code that actually has side effects;
  merging error handling so different errors now propagate the same; altering
  async timing/ordering; off-by-one when refactoring a loop or slice.
- **When in doubt, leave it and flag it.** A missed cleanup costs nothing; a
  regression costs trust.

## Scope (read before editing)

- **Only touch code this branch already changed.** Never refactor untouched code
  "while at it" — that turns a clean diff into an unreviewable one.
- **Zero behavior change.** Every edit must be behavior-preserving. A
  "simplification" that changes what the code does is a regression, not a cleanup.
- **Clarity over brevity.** Explicit, readable code beats clever or compact code.
  Do not trade "fewer lines" for legibility — collapsing logic into a dense
  one-liner or a nested ternary is not a simplification.

## Workflow

1. **Get the change scope.** Resolve the base (default branch) and read the diff —
   `git diff <base>...HEAD` plus any uncommitted changes (`git diff`). Read each
   hunk **with its surrounding file context** (open the file, not just the diff)
   before judging it.
2. **Review against the checklist** in `references/quality-checklist.md` (reuse,
   simplification, dead weight, efficiency, altitude, consistency). Before
   concluding a helper doesn't exist, **search the codebase** — duplication you
   can't see isn't reuse you can claim.
3. **Apply the cleanups incrementally**, scoped to changed code only, matching the
   surrounding naming/error-envelope/patterns. Apply one logical change, re-run
   the relevant check, then the next (regression guard). For a large diff, fan out
   read-only review sub-agents (one per checklist area) to FIND candidates
   (`file:line | what | suggested fix | confidence`); the single writer still
   applies them one at a time with checks between risky edits.
4. **Re-run the full local gate** at the end (lint / format / typecheck / tests) —
   reuse the project's check commands (CLAUDE.md / CI workflows / package scripts).
5. **Summarize** what changed and why, grouped by checklist area, and flag any
   cleanup you held back as too risky to do silently.

## Maintain balance — do NOT over-simplify

Stop short of changes that hurt the code even if they shrink it:

- Don't fold separate concerns into one function/component to save a definition.
- Don't strip a helpful abstraction that genuinely organizes the code.
- Don't make the code harder to debug, extend, or read in pursuit of "elegance".
- When an edit's value is marginal and its risk to clarity is real, leave it.

## Bundled Resources

### references/quality-checklist.md

The six quality criteria applied here — the canonical checklist, kept consistent
with `ofc:ship` Pass 2 so the standalone and PR-finalization flows judge a diff
the same way.
