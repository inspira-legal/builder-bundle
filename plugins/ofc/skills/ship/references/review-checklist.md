# Diff Review Checklist

Two passes over `git diff <base>...HEAD`, in this order. Read every hunk with its surrounding context (open the file, not just the diff) before judging it.

## Pass 1 — Correctness (find bugs)

Report only findings you can defend with the code in front of you; verify each one against the actual file before claiming it.

- **Logic errors** — inverted conditions, off-by-one, wrong operator, unreachable branches
- **Edge cases** — empty/null/undefined inputs, zero-length collections, first/last iteration, unicode
- **Error handling** — swallowed exceptions, missing error paths, error states that leave inconsistent data
- **Async/concurrency** — unawaited promises, race conditions, shared mutable state, missing cleanup/cancellation
- **State & lifecycle** — stale closures, missing dependency-array entries, resources opened but not closed
- **Contract breaks** — changed function signatures/return shapes with un-updated call sites, API/schema drift, broken serialization
- **Security** — injection (SQL/shell/path), unvalidated input crossing a trust boundary, secrets in code or logs
- **Type safety** — casts that hide real mismatches, `any`/`type: ignore` covering an actual error

For each finding: file:line, what breaks, a concrete input/scenario that triggers it, and the fix. Apply high-confidence fixes directly; flag uncertain ones for the user in the approval-gate summary.

## Pass 2 — Quality (simplify; no behavior changes)

These criteria are shared with the standalone `/ofc:improve-code` skill — keep the two in sync so a diff is judged identically here and there.

Only touch code already changed by this branch — do not refactor untouched code "while at it".

- **Reuse** — logic duplicated within the diff, or re-implementing a helper that already exists in the codebase (search before concluding it doesn't)
- **Simplification** — collapse needless indirection, flatten over-nested conditionals, remove flags/params with a single caller
- **Dead weight** — unused imports/variables/branches introduced by the branch, leftover debug code, commented-out code
- **Efficiency** — obvious O(n²) over collections that can be O(n), repeated I/O or queries inside loops, recomputing invariants per iteration
- **Altitude** — code placed at the wrong layer (e.g. project-specific logic in shared, or reusable logic buried in a feature folder), respecting the project's stated architecture conventions
- **Consistency** — naming, error envelopes, and patterns matching what neighboring code does

After each quality edit, re-run the relevant local check (lint/typecheck/tests for the touched area) — a simplification that breaks behavior is a regression, not a cleanup.
