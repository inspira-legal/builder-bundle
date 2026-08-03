# Front: correctness — five angles over the diff

Operationalizes Pass 1 of the plugin-root `references/quality-checklist.md`'s
sibling, `references/review-checklist.md`: the checklist says _what counts as a
bug_, this says _how to go looking for one_. Each angle is a different way of
reading the same diff, so two angles flagging the same line for different reasons
both get recorded — one angle's conclusion never suppresses another's.

Every candidate carries `file`, `line`, a one-line `summary`, and a concrete
`failure_scenario` — **the user-visible consequence** (wrong output, crash, data
loss, hung request), not an intermediate state ("o valor fica stale", "o set
cresce"). A candidate with no nameable consequence is not a finding.

Read hunks with their enclosing function open, not just the diff. Bugs on
unchanged lines of a touched function are in scope — the branch re-exposes them
or fails to fix them.

## Angle `diff-scan` — line by line

Read every hunk line by line, then read the enclosing function. For each line
ask: which input, state, timing, or platform makes this line wrong? Hunt for
inverted or wrong conditions, off-by-one, null/undefined deref, missing `await`,
falsy-zero treated as absent, wrong-variable copy-paste, an error swallowed in a
`catch` that should propagate, unescaped regex metacharacters.

## Angle `removed-behavior` — what the diff deleted

For every line the diff **removes or replaces**, name the invariant or behavior
it enforced, then find where the new code re-establishes it. When you can't find
it, that's a candidate: a removed guard, a dropped error path, a narrowed
validation, a deleted test that covered a real case, a lost regex anchor.

## Angle `cross-file` — callers and callees

For each function the diff changes, Grep for its symbol and check every call
site against the change: a new precondition, a changed return shape, a new
exception, a new timing or ordering dependency. Then the other direction — does a
parallel change in the same branch make one of its calls unsafe?

## Angle `language-pitfalls` — the stack's classic footguns

Scan for the pitfalls specific to the diff's language and framework. Examples of
the shape: JS falsy-zero, `==` coercion, closure-captured loop variables;
Python mutable default args, late-binding closures, dataclass defaults evaluated
once; Go nil-map writes, range-variable capture; SQL injection; timezone/DST
drift; float equality; React stale closures and missing dependency entries.

## Angle `wrapper-boundary` — types that wrap other types

When the diff adds or changes a cache, proxy, decorator, adapter, or middleware:
check that every method routes to the wrapped instance rather than back through a
registry, session, or global — a caching provider whose `delegate` field resolves
through `session.get(...)` instead of `delegate.get(...)` re-enters its own cache
or recurses. Check it forwards every method its callers actually use, and that
the error/timeout envelope survives the hop.

## Async and state

These live inside the angles above rather than as a sixth angle, because they
show up through all of them: unawaited promises, race conditions on shared
mutable state, missing cleanup or cancellation, resources opened and not closed,
retry storms and partial failures, ordering assumptions that only hold under one
scheduler.
