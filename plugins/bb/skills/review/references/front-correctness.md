# Front: correctness — the angle set over the diff

Operationalizes Pass 1 of the plugin-root `references/quality-checklist.md`'s
sibling, `references/review-checklist.md`: the checklist says _what counts as a
bug_, this says _how to go looking for one_. Each angle is a different way of
reading the same diff, so two angles flagging the same line for different reasons
both get recorded — one angle's conclusion never suppresses another's.

Every candidate carries `file`, `line`, a one-line `summary`, and a concrete
`failure_scenario`. What makes a consequence worth reporting — and why a
half-believed candidate goes through anyway — is the finder's own contract, in
`plugins/bb/agents/bb-finder.md`.

Read hunks with their enclosing function open, not just the diff. Bugs on
unchanged lines of a touched function are in scope — the branch re-exposes them
or fails to fix them.

Cap: **8 candidates per angle**. The cap is on what each finder hands to the
barrier, not on what it looks at — when an angle is over, keep the ones with the
sharpest failure scenario and say how many were cut.

## Finding shape

```
# | file:line | o que quebra | cenário que dispara | fix sugerido | veredito
```

The `veredito` column is filled by `verify.md`, not by the angle that found it.

## Pick the angles the diff can activate

The depth table (`fronts.md`) sizes the fan-out; **what the diff is made of**
decides which angles are in it. An angle with nothing to grip costs a full agent
and returns nothing, so the set is trimmed to the angles the artifact activates —
and the stats line reports that trimmed count, which is the depth that actually
ran.

Each set below is in **priority order** — a depth tier that funds two or three
angles takes them from the left:

| Diff is mostly                 | Angle set (priority order)                                                                                            |
| ------------------------------ | --------------------------------------------------------------------------------------------------------------------- |
| code (the default)             | `diff-scan`, `removed-behavior`, `cross-file`, `language-pitfalls`, `wrapper-boundary`                                |
| prompt / skill / docs markdown | `diff-scan`, `removed-behavior`, `cross-file`, **`instruction-integrity`** (replaces the pitfalls angle)              |
| config, manifest, IaC, schema  | `diff-scan`, `removed-behavior`, `cross-file`, plus a **validity** angle against the format's own schema or inventory |

For the last two rows `wrapper-boundary` drops out — there's no wrapped type to
route through — and the async/state material has nothing to attach to. Say which
angles ran, and name the dropped ones with the reason, so the depth that's reported
is the depth that happened. A caller can override the lens _content_ for its own
artifact the way `/bb:ship` does for LexFlow manifests
(`${CLAUDE_PLUGIN_ROOT}/skills/ship/references/land-lexflow.md`).

### Angle `instruction-integrity` — for a diff that instructs a model

The failure scenario here is a **run that goes wrong**, stated the same way as any
other: which instruction fires, and what the model then does. Hunt for two
sections that contradict each other so the reader's behavior depends on which one
it hits first; a pointer to a file, section or command that doesn't resolve from
where it's cited; a rule stated in the negative that writes the unwanted behavior
into the prompt (a "don't do X" and catalogs of wrong examples both prime X — the
positive form is the fix, and the exceptions are anti-hallucination, safety, and a
default verbal tic with no positive form); an instruction the prompt no longer
needs because what it guarded against was deleted; an unbounded output where the
surrounding document caps its others; and a precondition the flow never probes
before offering the action that needs it.

## Angle `diff-scan` — line by line

Read every hunk line by line, then read the enclosing function. For each line
ask: which input, state, timing, or platform makes this line wrong? Hunt for
inverted or wrong conditions, off-by-one, null/undefined deref, missing `await`,
falsy-zero treated as absent, wrong-variable copy-paste, an error swallowed in a
`catch` that should propagate, unescaped regex metacharacters.

This angle owns the checklist's **security** and **type safety** rows
(`references/review-checklist.md`, Pass 1), which are line-local the same way:
untrusted input reaching a query, shell, path or template without validation or
escaping; a secret landing in code or a log line; a cast, `any` or `type: ignore`
covering a mismatch the compiler was right about.

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
