# Front: contract — the diff against the brief that specified it

Available only when a task brief matches this branch (resolve per the plugin-root
`references/task-state.md` — `.bb/tasks/<slug>/spec.md`). It's the one front that
can catch a diff where every line is correct and the wrong thing got built.

## The two questions

1. **Did it build the specified thing?** Walk the brief's `## behavior` map. Each
   `WHEN … THEN …` row is an acceptance row: find the code that implements it and
   the test that pins it. A mapped row with no corresponding code **or** no test
   is a finding — cite the row verbatim and say which half is missing.
2. **Did it build only that?** Anything in the diff that no brief section asked
   for is scope drift: name it, and say whether it looks like a necessary
   dependency of the specified work (fine, mention once) or an unrelated ride-along
   (a finding — it belongs in its own branch).

## Also read the upstream sections when present

`## problem`, `## hypothesis`, `## fit`, and `## cuts` (written by
`/bb:discover`) bound the work too. A diff that implements something `## cuts`
explicitly deferred is a finding with a strong citation — the decision to leave it
out was already made.

## Finding shape

```
# | linha do brief citada | file:line (ou "ausente") | o que falta ou sobra | severidade
```

Severity: a missing happy path is HIGH; a missing mapped edge or a missing test
for a built behavior is MEDIUM; scope drift is MEDIUM; a stylistic divergence from
the brief's wording is not a finding at all.

Cap: 8. When the brief has no `## behavior` map (a small brief that skipped it),
say so and fall back to question 2 alone rather than inventing acceptance rows.
