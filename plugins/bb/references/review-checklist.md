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

Report each finding as `file:line | what breaks | a concrete triggering input/scenario | suggested fix | confidence`. What happens next is the calling skill's call: `/ofc:ship` applies high-confidence fixes and flags uncertain ones at its approval gate; `/ofc:review-changes` only reports and suggests the next step.

## Pass 2 — Quality (simplify; no behavior changes)

Apply the shared **quality checklist** — `references/quality-checklist.md` at the plugin root, the single source of truth used here and by the standalone `/ofc:tidy` skill, so a diff is judged identically wherever it's reviewed. It covers the six criteria (reuse, simplification, dead weight, efficiency, altitude, consistency), the scope/behavior/clarity rules, and the over-simplification guard.

Scope is code this branch already changed. A consumer that _applies_ Pass 2 (`/ofc:ship`, `/ofc:tidy`) re-runs the relevant local check after each quality edit — a simplification that breaks behavior is a regression, not a cleanup. A report-only consumer (`/ofc:review-changes`) just lists the smells and suggests `/ofc:tidy`.
