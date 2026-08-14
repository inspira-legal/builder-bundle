# Building the tasks as a dynamic workflow — the script's shape

The workflow build mode runs one agent per task instead of building the whole spec
in the main context. This file is the **contract the generated script has to meet**;
`/bb:implement` and `/bb:delegate` author the JS per run and pass it inline via the
`Workflow` tool's `script` input. What ships is this contract; the script itself is
authored fresh per run and lives only in the session directory.

The mode choice itself — when it's offered and the question it asks — is
`build-mode.md`, next to this file. Read this one only once workflow was chosen.

## What the platform forces

- **No user input mid-run.** Only a permission prompt pauses a workflow. A task
  agent can _return_ "the spec is underspecified"; it can't ask. The script decides.
- **The script has no shell and no filesystem.** Only agents read, write and run
  commands. Every gate, commit and `verifica:` happens inside an agent; the script
  coordinates and reads structured returns.
- **Out-of-allowlist commands don't prompt.** A task agent runs under `claude -p`
  and the Agent SDK, where there is nobody to ask, so the call follows the configured
  rules without confirmation — in practice it fails. A gate the run can't execute is
  a red task, not a question. Stage zero exists to catch that first.
- **`Date.now()`, `new Date()` and `Math.random()` throw** — they'd break resume.
  Vary anything per-task by index, and stamp times after the workflow returns.

## Sequential, with one parallel stage

The tasks run in a `for` loop with `await` — not `pipeline()`. `pipeline` runs each
item through the stages independently and concurrently, which is the wrong primitive
here: the tasks share one working tree, and `dep:` exists precisely to say that
task 2 builds on what task 1 created. `parallel()` appears exactly once, in stage
zero, which is read-only.

## `args`

The skill passes a real JSON value (never a stringified one):

```
{
  slug: "<slug>",
  specPath: ".bb/tasks/<slug>/spec.md",
  gateHint: "<what the authority chain resolved, or null>",
  reuseNotes: ["<one string per reuse note in ## decisions>"],
  tasks: [
    { n: 1, title: "...", delivers: "...", behaviors: [2, 3], dep: [], verifica: "..." }
  ]
}
```

`tasks` carries only the ones still unticked at invoke time, in an order that
already satisfies `dep:`. The agents re-read the spec anyway — `args` is the plan,
the file on disk is the truth.

## Stage zero — prove the ground before task 1

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

`commands` is the discriminator. **Empty means no gate was found** — the script logs
that and proceeds; `ran` and `green` say nothing in that case. **Non-empty** puts two
stops on the table: `ran: false` (the run has no permission to execute it) and
`green: false` (the tree was already red — a broken gate the build didn't cause).
A note that came back `gone` is the third stop. `moved` is not a stop: the new path
goes into the convention note, and from task 1 on it outranks the path the spec's
reuse note names.

A stage-zero stop is normalized into the shape a task result has, so the caller has
one thing to read and a blocker to name:
`{ n: 0, status: "red", blocker: "<which note died, or which command, and why>" }`.

## The task loop

```
for (const t of args.tasks) {
  const r = await agent(taskPrompt(t, conventions), {
    label: `task ${t.n}: ${t.title}`,
    phase: "Build",
    schema: TASK_RESULT,
  })
  if (!r) {
    stopped = { n: t.n, status: "red", blocker: "agente perdido (retorno null)" }
    break
  }
  if (r.status === "skipped") { skipped.push(r.n); continue }
  if (r.status !== "green") { stopped = r; break }
  conventions = r.conventions
  if (r.verifica.result === "pending") pendingVerifica.push(r.n)
  results.push(r)
}
```

Three exits, and each needs its own line. A `null` return (the user skipped the
agent, or it died on a terminal API error) is a failed task that carries no blocker
of its own, so the script writes one — assigning `stopped = r` there would hand the
caller a `null` `stopped`, which reads as a clean run over a half-built spec. A
`skipped` task was already ticked before the run: count it and move on, keeping the
conventions the loop already had. Anything else stops the loop and keeps what's green.

## What the task agent is told to do

The prompt carries the spec path, the task's own line, the behaviors it cites, the
accumulated convention note, and the gate commands stage zero resolved. Its steps:

1. **Re-read `## tasks` on disk.** If this task is already `- [x]`, return
   immediately with `status: "skipped"` — the run is resumable and re-running a
   half-built spec must not redo what already landed.
2. **Build the task**, staying inside the spec's `## out of scope`. A **stack
   choice** the spec didn't close (framework, package manager, tooling) is settled
   against the manifesto first — the plugin-level `references/consult-manifesto.md`,
   whose path goes into the prompt.
3. **Satisfy `verifica:`.** A command gets run: `result` is `passed` or `failed`.
   `leitura` means self-inspection — read what you produced against the behaviors
   this task cites and return short evidence. `CI` is out of reach inside the run:
   return `result: "pending"`, which is neither a pass nor a failure; `/bb:ship` is
   what covers it. No `verifica:` is silently skipped.
4. **Run the gate** and fix what broke.
5. **Commit** — only the files this task touched, with its `- [ ]` → `- [x]` in the
   same commit, on the branch the run is already on. **Conventional style, and no AI
   attribution** — the agent starts with no memory of the target repo's habits, so
   the convention travels in the prompt. The commit is the checkpoint (workflow
   resume is same-session only and replays everything that started after the first
   unfinished agent; commits survive anything).
6. **Return** the structured result. A red gate after the retries, a `verifica:` that
   came back `failed`, or a spec too underspecified to build against all mean:
   **don't commit, don't revert.** Leave the tree as it is for diagnosis and return
   the blocker. A `verifica:` still `pending` is a green task — it commits, and the
   pending rides the script's return out to ship.

Return shape:

```
{
  n: 1,
  status: "green" | "red" | "skipped" | "underspecified",
  verifica: { kind: "command" | "leitura" | "ci", result: "passed" | "failed" | "pending", evidence: "..." },
  commit: "<sha, or null>",
  conventions: "<the accumulated note this task hands forward>",
  blocker: "<what stopped it, when not green>"
}
```

## The convention note

This is what pays for the context each fresh agent doesn't have. It **accumulates**:
task N receives the conventions of every earlier task, not just the previous one —
the whole point is that task 3 uses the names task 1 established.

The agent returns the note it received plus what it established. Past roughly 1500
characters it condenses the oldest entries itself before returning; no dedicated
summarizer agent. What belongs in it: names and paths introduced, signatures other
tasks will call, a pattern chosen among alternatives, and any `moved` reuse target
from stage zero. What doesn't: anything already written in the spec.

## Effort and model

Stage zero at `effort: 'low'` — read-only lookup. Task agents inherit the session
model and effort; they're doing the same work the main context would have done.

## What the script returns

```
{ slug, built: [<n>], skipped: [<n>], pendingVerifica: [<n>], stopped: <the failing result, or null>, conventions }
```

The caller reads that and follows its own contract: `/bb:implement` goes to its
step 8, `/bb:delegate` to ship. A non-null `stopped` means neither proceeds to
landing — delegate flips `status: blocked`, implement stops at its safety valve.
`pendingVerifica` names the tasks whose proof is CI, which is ship's to close.

## Before invoking — the checklist

The generated script is only as trustworthy as this check, since it isn't versioned
and CI never sees it. Confirm all of it, then invoke:

- `export const meta` is a pure literal (no variables, calls, spreads or template
  strings) with `name`, `description` and one `phases` entry per `phase()` call.
- Exactly one `parallel()`, in stage zero. The tasks are a `for` with `await`.
- Every `agent()` that needs a typed answer passes `schema`; every result is
  null-checked before use.
- No `Date.now()`, `new Date()` or `Math.random()` anywhere.
- `args` is passed as a JSON value, and `tasks` holds only unticked tasks.
- The task prompt includes: the spec path, the task line, its behaviors, the
  accumulated note, the gate commands, the commit convention (conventional style, no
  AI attribution), the manifesto's path for stack choices, and the six steps above.
- The branch the commits belong on already exists and is checked out — the agents
  commit where the run puts them.
- The agent count is `tasks.length + reuseNotes.length + 1` — under the session's
  workflow size guideline, and far under the 1000-per-run cap.
