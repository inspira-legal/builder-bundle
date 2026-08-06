# Build mode — workflow or main context

Two ways to build a brief's slices, and the user picks per run:

- **Workflow** — one agent per slice, dispatched as a dynamic workflow. Each slice
  starts on a clean budget carrying only the brief and its own cut, and a convention
  note is threaded between them. Shape of the script: `build-slices-workflow.md`.
- **Context** — the main session builds every slice itself. What `/bb:implement` has
  always done.

The reason to offer the choice isn't speed. A brief of eight slices built in one
context hits compaction mid-build, and that's exactly where the loop degrades: the
`## behavior` map falls out of context and the build starts drifting from the
`## decisions`. Losing tacit context between agents is the price, and the convention
note is what's paid with — lossy on purpose instead of lossy by accident.

## When the question is asked

`/bb:implement` and `/bb:delegate` ask it **once, at the start of every supervised
run**, before the first slice — no size threshold. A brief with a single slice is
still asked; the choice is the user's, not a heuristic's. When `/bb:delegate` drives
the build it's delegate that asks, and the implement loop it drives takes the answer
as given.

Two things skip it entirely. A brief with **no `## tasks` section** has no slices to
fan out over — and no build either: implement's Prerequisites stop the run and send
it back to `/bb:spec` before this question would have been reached. The other is a
run where workflows aren't available, below.

This is a mid-skill question, not the handoff gate — the gate convention in
`handoff-gate.md` still applies to the one at the end of the skill. What carries over
from it: the question goes through `AskUserQuestion` (a question printed as text has
no response path), the tool supplies "Other" on its own, and the recommended option
leads and is suffixed `(Recomendado)`.

## The question

All of it in PT-BR:

```
question: "O brief tem N slices. Construir via workflow (um agente por slice) ou no contexto desta sessão?"
options:
  - "Via workflow (Recomendado)" — Um agente por slice, em sequência, na mesma árvore. Cada um começa com contexto limpo; as convenções passam adiante numa nota. Você acompanha em /workflows.
  - "Neste contexto" — Construo as slices aqui mesmo, como sempre. Num brief grande o build bate compactação no meio e começa a derivar do brief.
```

Which one leads depends on the brief: several unticked slices makes the compaction
risk real, so workflow is the recommendation; one or two slices doesn't, and context
is the simpler answer. Swap the `(Recomendado)` suffix accordingly — the option text
itself doesn't change.

## Unattended

Under `BB_UNATTENDED` there's no question: the run goes via workflow and records the
choice in its report. This is the documented lean the unattended frame takes, the
same as every other skipped question.

## When workflows aren't available

The `Workflow` tool is absent from the session when the `disableWorkflows` setting is
on, when org-managed settings turn it off, or when the client predates the version
that shipped dynamic workflows. Check before asking: an option that can't be executed
isn't a choice.

Absent, both skills build in context and **say why in one line** — "workflows
desligados nesta sessão, construindo aqui". A silent downgrade reads as a preference
and hides a setting the user may not know is on. Unattended, the same line goes into
the run's report, which is what `/bb:ship` already carries into the PR description.

## After the pick

- **Workflow** — read `build-slices-workflow.md`, author the script, run the
  pre-invoke checklist at the end of that file, invoke `Workflow`. When it returns,
  pick up the caller's own contract from its result.
- **Context** — build the slices as implement's steps 3–7 describe. Nothing about
  the brief, the gate or the commits changes.
