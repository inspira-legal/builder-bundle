# Diff review checklist

Two passes over the review's diff range, in this order. The range is resolved once by the caller and handed down in the scope block (`<merge_base>...HEAD`, per the probe in `fronts.md`) — don't re-resolve a base here. Read every hunk with its surrounding context (open the file, not just the diff) before judging it.

## Pass 1 — Correctness (find bugs)

Every finding names a **concrete user-visible consequence** — wrong output, crash, data loss, hung request — with the line that causes it. A candidate with no nameable consequence isn't a finding; one whose trigger is uncertain still is, and the verdict on it belongs to the verify pass (`verify.md`), not to the pass that found it.

- **Logic errors** — inverted conditions, off-by-one, wrong operator, unreachable branches
- **Edge cases** — empty/null/undefined inputs, zero-length collections, first/last iteration, unicode
- **Error handling** — swallowed exceptions, missing error paths, error states that leave inconsistent data
- **Async/concurrency** — unawaited promises, race conditions, shared mutable state, missing cleanup/cancellation
- **State & lifecycle** — stale closures, missing dependency-array entries, resources opened but not closed
- **Contract breaks** — changed function signatures/return shapes with un-updated call sites, API/schema drift, broken serialization
- **Security** — injection (SQL/shell/path), unvalidated input crossing a trust boundary, secrets in code or logs
- **Type safety** — casts that hide real mismatches, `any`/`type: ignore` covering an actual error

Report each finding as `file:line | summary | failure_scenario | suggested fix`. The verdict column is added by the verify pass, which is what makes CONFIRMED / PLAUSIBLE / REFUTED mean anything — a finder that grades its own candidates bypasses it. What happens next is the router's call: `/bb:review` reports first and applies only what the user picks at its curation step.

## Pass 2 — Quality (simplify; no behavior changes)

Apply the **quality checklist** — `quality-checklist.md`, its sibling here and the single source of truth for what a quality finding is. It covers the six criteria (reuse, simplification, dead weight, efficiency, altitude, consistency), the scope/behavior/clarity rules, and the over-simplification guard.

Scope is code this branch already changed. A consumer that _applies_ Pass 2 (`/bb:review` after its curation step) re-runs the relevant local check after each quality edit — a simplification that breaks behavior is a regression, not a cleanup. In report mode the smells are just listed for the user to pick from.
