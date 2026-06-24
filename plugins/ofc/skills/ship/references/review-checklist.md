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

Apply the shared **quality checklist** — `references/quality-checklist.md` at the plugin root, the single source of truth used here and by the standalone `/ofc:improve-code` skill, so a diff is judged identically wherever it's reviewed. It covers the six criteria (reuse, simplification, dead weight, efficiency, altitude, consistency), the scope/behavior/clarity rules, and the over-simplification guard.

Only touch code already changed by this branch. After each quality edit, re-run the relevant local check (lint/typecheck/tests for the touched area) — a simplification that breaks behavior is a regression, not a cleanup.
