# Building the slices as a dynamic workflow — the script's shape

The workflow build mode runs one agent per slice instead of building the whole brief
in the main context. This file is the **contract the generated script has to meet**;
`/bb:implement` and `/bb:delegate` author the JS per run and pass it inline via the
`Workflow` tool's `script` input. Nothing here ships as an executable — there is no
`workflows/` entry and no `/bb:build-slices` command.

The mode choice itself — when it's offered, the question, the unattended rule — is
`build-mode.md`, next to this file. Read this one only once workflow was chosen.

## What the platform forces

- **No user input mid-run.** Only a permission prompt pauses a workflow. A slice
  agent can *return* "the brief is underspecified"; it can't ask. The script decides.
- **The script has no shell and no filesystem.** Only agents read, write and run
  commands. Every gate, commit and `verifica:` happens inside an agent; the script
  coordinates and reads structured returns.
- **Out-of-allowlist commands don't prompt in a routine.** Under `claude -p` and the
  Agent SDK there is nobody to ask, so the call follows the configured rules without
  confirmation — in practice it fails. A gate the run can't execute is a red slice,
  not a question. Stage zero exists to catch that first.
- **`Date.now()`, `new Date()` and `Math.random()` throw** — they'd break resume.
  Vary anything per-slice by index, and stamp times after the workflow returns.

## Sequential, with one parallel stage

The slices run in a `for` loop with `await` — not `pipeline()`. `pipeline` runs each
item through the stages independently and concurrently, which is the wrong primitive
here: the slices share one working tree, and `dep:` exists precisely to say that
slice 2 builds on what slice 1 created. `parallel()` appears exactly once, in stage
zero, which is read-only.

## `args`

The skill passes a real JSON value (never a stringified one):

```
{
  slug: "<slug>",
  briefPath: ".bb/tasks/<slug>/spec.md",
  gateHint: "<what the authority chain resolved, or null>",
  reuseNotes: ["<one string per reuse note in ## decisions>"],
  slices: [
    { n: 1, title: "...", delivers: "...", behaviors: [2, 3], dep: [], verifica: "..." }
  ]
}
```

`slices` carries only the ones still unticked at invoke time, in an order that
already satisfies `dep:`. The agents re-read the brief anyway — `args` is the plan,
the file on disk is the truth.

## Stage zero — prove the ground before slice 1

One agent per reuse note, plus one gate agent, all inside a single `parallel()`.
This is a legitimate barrier: nothing starts until every verdict is in. These agents
are read-only lookups, so they run at `effort: 'low'`.

Each reuse-note agent returns:

```
{ verdict: "intact" | "moved" | "gone", note: "<the note>", where: "<new path, if moved>" }
```

The gate agent resolves the project's checks through implement's authority chain
(CLAUDE.md / docs → CI workflow files → `package.json` / `justfile` / `Makefile` /
`pyproject.toml`) and then **runs all of them once**. Running them is the point: it
proves the run has permission to execute each one, and it establishes the green
baseline. It returns:

```
{ commands: ["..."], ran: true | false, green: true | false, blocker: "<why, if any>" }
```

The script stops before slice 1 when any note came back `gone`, when `ran` is false
(permission), or when `green` is false (the tree was already red — a broken gate the
build didn't cause). `moved` is not a stop: the new path goes into the convention
note. No gate found at all is not a stop either — the script logs it and proceeds.

## The slice loop

```
for (const s of args.slices) {
  const r = await agent(slicePrompt(s, conventions), {
    label: `slice ${s.n}: ${s.title}`,
    phase: "Build",
    schema: SLICE_RESULT,
  })
  if (!r || r.status !== "green") { stopped = r; break }
  conventions = r.conventions
  results.push(r)
}
```

A `null` return (the user skipped the agent, or it died on a terminal API error) is
treated as a failed slice: stop the loop, keep what's already green.

## What the slice agent is told to do

The prompt carries the brief path, the slice's own line, the behaviors it cites, the
accumulated convention note, and the gate commands stage zero resolved. Its steps:

1. **Re-read `## tasks` on disk.** If this slice is already `- [x]`, return
   immediately with `status: "skipped"` — the run is resumable and re-running a
   half-built brief must not redo what already landed.
2. **Build the slice**, staying inside the brief's `## out of scope`.
3. **Satisfy `verifica:`.** A command gets run. `leitura` means self-inspection: read
   what you produced against the behaviors this slice cites and return short
   evidence. `CI` is out of reach inside the run — return it as pending; `/bb:ship`
   is what covers it. No `verifica:` is silently skipped.
4. **Run the gate** and fix what broke. Unattended: at most 3 retries, and only on a
   known-flake signature.
5. **Commit** — only the files this slice touched, with its `- [ ]` → `- [x]` in the
   same commit. The commit is the checkpoint (workflow resume is same-session only
   and replays everything that started after the first unfinished agent; commits
   survive anything).
6. **Return** the structured result. A red gate after the retries, a failed
   `verifica:`, or a brief too underspecified to build against all mean: **don't
   commit, don't revert.** Leave the tree as it is for diagnosis and return the
   blocker.

Return shape:

```
{
  n: 1,
  status: "green" | "red" | "skipped" | "underspecified",
  verifica: { kind: "command" | "leitura" | "ci", passed: true, evidence: "..." },
  commit: "<sha, or null>",
  conventions: "<the accumulated note this slice hands forward>",
  blocker: "<what stopped it, when not green>"
}
```

## The convention note

This is what pays for the context each fresh agent doesn't have. It **accumulates**:
slice N receives the conventions of every earlier slice, not just the previous one —
the whole point is that slice 3 uses the names slice 1 established.

The agent returns the note it received plus what it established. Past roughly 1500
characters it condenses the oldest entries itself before returning; no dedicated
summarizer agent. What belongs in it: names and paths introduced, signatures other
slices will call, a pattern chosen among alternatives, and any `moved` reuse target
from stage zero. What doesn't: anything already written in the brief.

## Effort and model

Stage zero at `effort: 'low'` — read-only lookup. Slice agents inherit the session
model and effort; they're doing the same work the main context would have done.

## What the script returns

```
{ slug, built: [<n>], skipped: [<n>], stopped: <the failing result, or null>, conventions }
```

The caller reads that and follows its own contract: `/bb:implement` goes to its
step 8, `/bb:delegate` to ship. A non-null `stopped` means neither proceeds to
landing — delegate flips `status: blocked`, implement stops at its safety valve.

## Before invoking — the checklist

The generated script is only as trustworthy as this check, since it isn't versioned
and CI never sees it. Confirm all of it, then invoke:

- `export const meta` is a pure literal (no variables, calls, spreads or template
  strings) with `name`, `description` and one `phases` entry per `phase()` call.
- Exactly one `parallel()`, in stage zero. The slices are a `for` with `await`.
- Every `agent()` that needs a typed answer passes `schema`; every result is
  null-checked before use.
- No `Date.now()`, `new Date()` or `Math.random()` anywhere.
- `args` is passed as a JSON value, and `slices` holds only unticked slices.
- The slice prompt includes: the brief path, the slice line, its behaviors, the
  accumulated note, the gate commands, and the six steps above.
- The agent count is `slices.length + reuseNotes.length + 1` — under the session's
  workflow size guideline, and far under the 1000-per-run cap.
