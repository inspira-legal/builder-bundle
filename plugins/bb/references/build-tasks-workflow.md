# The build: one agent per task, run by `workflows/build-tasks.js`

`/bb:implement` and `/bb:delegate` build a spec's tasks by dispatching one agent per
task as a dynamic workflow. The script that does it is fixed and versioned at
`plugins/bb/workflows/build-tasks.js`, and **the script is the definition**: the task
agent's contract is the prompt string inside it, not a paraphrase kept here. This file
documents what the skills need to know to call it and what its return means.

There is no mode question. The in-context build survives as the fallback for a session
that cannot run this, and the skills announce that downgrade in one line.

## Why the build runs here and not in the main context

A spec of eight tasks built in one context hits compaction mid-build, and that is
exactly where the loop degrades: the `## Behavior` map falls out of context and the
build starts drifting from the `## Decisions`. Each task agent instead starts on a
clean budget carrying only the spec and its own cut. Losing the session's tacit context
between agents is the price, and the convention note is what pays it, lossy on purpose
instead of lossy by accident.

That price is also why the spec is reviewed before it ever gets here. A task agent
receives the spec, its own line and the convention note, so a spec that only its author
can build from is a broken spec. `bb-spec-reviewer` asks that question in `/bb:spec`.

## What the platform forces

- **No user input mid-run.** Only a permission prompt pauses a workflow. A task agent
  can _return_ "the spec is underspecified"; it cannot ask. The script decides.
- **The script has no shell and no filesystem.** Only agents read, write and run
  commands. Every check, commit and `verify:` happens inside an agent; the script
  coordinates and reads structured returns.
- **Out-of-allowlist commands do not prompt.** A task agent runs under `claude -p` and
  the Agent SDK, where there is nobody to ask, so the call follows the configured rules
  without confirmation; in practice it fails. A check the run cannot execute is a red
  task, not a question. Stage zero exists to catch that first.
- **`Date.now()`, `new Date()` and `Math.random()` throw**: they would break resume.
  Anything per-task varies by index, and times are stamped after the workflow returns.

## Sequential, with one parallel stage

The tasks run in a `for` loop with `await`, not `pipeline()`. `pipeline` runs each item
through the stages independently and concurrently, which is the wrong primitive here:
the tasks share one working tree, and `dep:` exists precisely to say that task 2 builds
on what task 1 created. `parallel()` appears exactly once, in stage zero, which is
read-only.

## How the skills invoke it

The path is resolved and the file proved in one `Bash` call: a `cat` of
`$CLAUDE_PLUGIN_ROOT/workflows/build-tasks.js` into `/dev/null`, then an `echo` of that
same path. A non-zero exit is the missing-file case. The printed path is what goes into
`scriptPath`, already expanded, because the tool takes a literal path.

Three fallbacks, one attempt each: `scriptPath` refused becomes an inline `script` read
off the same file; that refused too, or no `Workflow` tool in the session, or a `Bash`
call that cannot read the file, becomes the in-context build with the reason named.

## `args`

The skill builds this by reading the spec, and passes a real JSON value (never a
stringified one):

```
{
  slug: "<slug>",
  specPath: ".bb/<slug>/spec.md",
  checksHint: "<what the authority chain resolved, or null>",
  reuseNotes: ["<one string per reuse note in ## Decisions>"],
  tasks: [
    { n: 1, title: "...", delivers: "...", behaviors: [2, 3], dep: [], verify: "..." }
  ]
}
```

`tasks` carries only the ones still unticked at invoke time, in an order that already
satisfies `dep:`. The agents re-read the spec anyway: `args` is the plan, the file on
disk is the truth.

An empty `tasks` is not a run. The skill sees it first and reports nothing to build
without invoking; the script returns the empty report before stage zero, so a caller that
invoked anyway does not pay for the project's checks and every reuse note to build no
task.

## Stage zero: prove the ground before task 1

One agent per reuse note, plus one checks agent, all inside a single `parallel()`. This
is a legitimate barrier: nothing starts until every verdict is in. These agents are
read-only lookups, so they run at `effort: 'low'`.

Each reuse-note agent returns:

```
{ verdict: "intact" | "moved" | "gone", note: "<the note>", where: "<new path, if moved>" }
```

The checks agent resolves the project's checks through implement's authority chain
(CLAUDE.md and docs, then CI workflow files, then `package.json` / `justfile` /
`Makefile` / `pyproject.toml`) and then **runs all of them once**. Running them is the
point: it proves the run has permission to execute each one, and it establishes the
green baseline. It returns:

```
{ commands: ["..."], ran: true | false, green: true | false, blocker: "<why, if any>" }
```

`commands` is the discriminator. **Empty means no check was found**: the script logs
that and proceeds, and `ran` and `green` say nothing in that case. **Non-empty** puts
two stops on the table: `ran: false` (the run cannot execute it) and `green: false`
(the tree was already red, a red check the build did not cause). A note that came back
`gone` is the third stop. `moved` is not a stop: the new path goes into the convention
note, and from task 1 on it outranks the path the spec's reuse note names.

A stage-zero stop is normalized into the shape a task result has, so the caller has one
thing to read and a blocker to name:
`{ n: 0, status: "red", blocker: "<which note died, or which command, and why>" }`.

One environment fails here by policy rather than by breakage: a repo whose top
authority forbids running checks locally resolves commands and then cannot run them,
which is `ran: false` and a stop before task 1. That is the contract working, and it
means the workflow build does not complete on such a machine until the policy, or the
hint the skill passes, says the project exposes nothing this run may execute.

## The task loop

Four exits, and each needs its own line. A `null` return (the user skipped the agent,
or it died on a terminal API error) is a failed task that carries no blocker of its
own, so the script writes one. Assigning `stopped = r` there would hand the caller a
`null` `stopped`, which reads as a clean run over a half-built spec. A `skipped` task
was already ticked before the run: count it and move on, keeping the conventions the
loop already had. A `green` task whose `verify` is missing, or whose `verify.result` is
`failed`, stops the loop too: `verify:` is what makes a task done, so green over an
absent proof is a task the caller would read as proven. Anything else stops the loop and
keeps what is green.

## What the task agent is told to do

The prompt carries the spec path, the task's own line, the behaviors it cites, the
accumulated convention note, and the check commands stage zero resolved. Its steps, in
the script's words:

1. **Re-read `## Tasks` on disk** (plus `## Tarefas`, the older spelling, and a
   half-migrated spec carrying both headings gets **both** enumerated, in file order;
   the whole pairing is in the plugin-level `references/spec-state.md`). If this task is
   already `- [x]`, return `status: "skipped"` immediately: the run is resumable and
   re-running a half-built spec must not redo what already landed.
2. **Build the task**, staying inside the spec's `## Out of scope`. A **stack choice**
   the spec left open (framework, package manager, tooling) is settled against the
   manifesto first: the plugin-level `references/consult-manifesto.md`, whose path goes
   into the prompt.
3. **Satisfy `verify:`.** A command gets run: `result` is `passed` or `failed`.
   `reading` means self-inspection, read what you produced against the behaviors this
   task cites and return short evidence. `CI` is out of reach inside the run: return
   `result: "pending"`, which is neither a pass nor a failure, and `/bb:ship` covers it.
   Every `verify:` runs.
4. **Run the project's checks** and fix what broke. A failed check is re-run at most
   `RETRY_CAP` times (3), and only while no file changed between runs. A check that
   fails and then passes with the tree untouched is the whole definition of a flake
   here. Once a file changed, the failure is the task's to fix.
5. **Commit** only the files this task touched, with its `- [ ]` to `- [x]` in the same
   commit, on the branch the run is already on. **Conventional style, and no AI
   attribution**. The agent starts with no memory of the target repo's habits, so the
   convention travels in the prompt. The commit is the checkpoint: workflow resume is
   same-session only and replays everything that started after the first unfinished
   agent, and commits survive anything.
6. **Return** the structured result. A red check after the retries, a `verify:` that
   came back `failed`, or a spec too underspecified to build against all mean the same
   thing: **do not commit, do not revert.** Leave the tree as it is for diagnosis and
   return the blocker. A `verify:` still `pending` is a green task: it commits, and the
   pending rides the script's return out to ship.

Return shape:

```
{
  n: 1,
  status: "green" | "red" | "skipped" | "underspecified",
  verify: { kind: "command" | "reading" | "ci", result: "passed" | "failed" | "pending", evidence: "..." },
  commit: "<sha, or null>",
  conventions: "<the accumulated note this task hands forward>",
  blocker: "<what stopped it, when not green>"
}
```

## The convention note

This is what pays for the context each fresh agent does not have. It **accumulates**:
task N receives the conventions of every earlier task, not just the previous one; the
whole point is that task 3 uses the names task 1 established.

The agent returns the note it received plus what it established. Past `NOTE_CEILING`
characters (roughly 1500) it condenses the oldest entries itself before returning; no
dedicated summarizer agent. What belongs in it: names and paths introduced, signatures
other tasks will call, a pattern chosen among alternatives, and any `moved` reuse target
from stage zero. What does not: anything already written in the spec.

## Effort and model

Stage zero at `effort: 'low'`, read-only lookup. Task agents inherit the session model
and effort; they are doing the same work the main context would have done.

## What the script returns

```
{ slug, built: [<n>], skipped: [<n>], pendingVerify: [<n>], stopped: <the failing result, or null>, conventions }
```

The caller reads that and follows its own contract: `/bb:implement` goes to its step 8,
`/bb:delegate` to ship. A non-null `stopped` means neither proceeds to landing; delegate
flips `status: blocked`, implement stops at its safety valve. `pendingVerify` names the
tasks whose proof is CI, which is ship's to close.

## What guards the script, and what the skill still checks per run

The script is code now, so most of the old pre-invoke checklist moved off the run.

**CI and the pre-commit hook** own what a parse or a scan settles, in
`.github/scripts/validate-workflow-script.ts`, over a source whose comment, string,
template and regex bodies are blanked first, so only code is read:

- the file parses, wrapped the way the platform runs it;
- `export const meta` is present, and a pure literal: no interpolation, no spread, and no
  bare word other than `true`, `false`, `null` and `undefined`;
- `meta.phases`, when the block declares it, has one entry per `phase()` call;
- there is exactly one `parallel()`, and it comes before the task loop;
- `Date.now()`, `new Date()` and `Math.random()` appear nowhere.

It runs inside `package.json`'s `validate`, which is what lefthook's pre-commit job runs,
so the guard fires before the commit and not only in CI. oxfmt formats `js` alongside
`json` and `md`.

**A one-time PR review** owns what only reading the code settles: `schema` on every
`agent()` that needs a typed answer, and every result null-checked before use. That is a
review of a change to this script, not a step in a build run.

**The skill** owns the three that are genuinely per-run, and confirms them before
invoking:

- `args` is passed as a JSON value, and `tasks` holds only unticked tasks.
- The branch the commits belong on already exists and is checked out; the agents commit
  where the run puts them.
- The agent count is `tasks.length + reuseNotes.length + 1`. Over the size guideline the
  session declares, say so in one line and invoke anyway; the real cap is 1000 agents
  per run.
