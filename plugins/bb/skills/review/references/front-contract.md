# Front: contract, the diff against the spec that specified it

Available only when a spec matches this branch (resolve per the plugin-root
`references/spec-state.md`: `.bb/<slug>/spec.md`). It's the one front that
can catch a diff where every line is correct and the wrong thing got built.

## The two questions

1. **Did it build the specified thing?** Walk the spec's `## Behavior` map
   (`## behavior` on a spec written before the rename, same map). Each
   `WHEN … THEN …` row is an acceptance row: find the code that implements it and
   the test that pins it. A mapped row with no corresponding code **or** no test
   is a finding: cite the row verbatim and say which half is missing.
2. **Did it build only that?** Anything in the diff that no spec section asked
   for is scope drift: name it, and say whether it looks like a necessary
   dependency of the specified work (fine, mention once) or an unrelated ride-along
   (a finding: it belongs in its own branch).

## Also read the upstream sections when present

`## Problem`, `## Hypothesis`, `## Fit`, and `## Cuts` (written by
`/bb:discover`) bound the work too: `## Problema`, `## Hipótese`, `## Encaixe`
and `## Cortes` on a spec written before the rename, same sections. A diff that
implements something `## Cuts` explicitly deferred is a finding with a strong
citation. The decision to leave it out was already made.

## Finding shape

```
# | linha da spec citada | file:line (ou "ausente") | o que falta ou sobra | severidade
```

Severity: a missing happy path is HIGH; a missing mapped edge or a missing test
for a built behavior is MEDIUM; scope drift is MEDIUM; a stylistic divergence from
the spec's wording is not a finding at all.

Cap: 8. When the spec has neither `## Behavior` nor `## Comportamento` (a small spec
that skipped the map), say so and fall back to question 2 alone rather than inventing
acceptance rows.
