# The build: one agent per task, run by `workflows/build-tasks.js`

`/bb:implement` builds a spec's tasks by dispatching one agent per
task as a dynamic workflow. The script that does it is fixed and versioned at
`plugins/bb/workflows/build-tasks.js`, and **the script is the definition**: the task
agent's contract is the prompt string inside it, not a paraphrase kept here. This file
documents what the skills need to know to call it and what its return means.

There is no mode question. The in-context build survives as the last step of the
fallback chain below, and the skills say in one line why the build ran in the main
context.

## Why the build runs here and not in the main context

A spec of eight tasks built in one context hits compaction mid-build, and that is
exactly where the loop degrades: the `## Behavior` map falls out of context and the
build starts drifting from the `## Decisions`. Each task agent instead starts on a
clean budget carrying only the spec and its own cut. Losing the session's tacit context
between agents is the price, and the convention note is what pays it, lossy on purpose
instead of lossy by accident.

That price is also why the spec is reviewed before it ever gets here. A task agent
receives the spec, its own line and the convention note, so a spec that only its author
can build from is a broken spec. `/bb:spec`'s step 6 asks that question.

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

The script is at `<plugin-root>/workflows/build-tasks.js`, and the root is the one the
SessionStart hook published into this session. That hook resolved it from a directory an
interpreter on this machine had already opened, so the path is proven before any skill
reads this line, and nothing here searches for it.

**The dispatch points at a copy of that file, never at the file.** Every installed copy
carries CR, and `Workflow` inlines a `scriptPath` into the approval dialog as `script`,
where the permission layer refuses a control character that would be hidden there.
`<plugin-root>/scripts/normalize_workflow.py` reads the source as bytes, drops every `\r`,
writes the copy under its out dir and prints that one path, which is what `scriptPath`
takes. Substitute the root and run it, in one `Bash` call:

```bash
python3 "<plugin-root>/scripts/normalize_workflow.py" "<plugin-root>/workflows/build-tasks.js"
```

`--out <dir>` chooses where the copy lands: pass the session's scratchpad when there is
one, and the default is a directory under the system temp, which needs nothing published
to it. The copy keeps the source's basename, so the path the approval dialog shows is the
same one on every run. The script's own docstring owns why the strip is unconditional.

A non-zero exit is the one failure the chain reads, and the message on stderr names the
path it choked on: the source is missing or unreadable, or the out dir cannot be written.
With no root in the session at all, the chain goes straight to its last step: a guess at
the path is what the hook exists to replace.

The **fallback chain**, one attempt each, in this order. It is stated here and nowhere
else, so the skills point at it by name and carry no count of their own:

1. `Workflow` with `scriptPath` set to the printed copy. This is the dispatch.
2. The `scriptPath` dispatch came back refused: `Workflow` with `script` set to the copy's
   text, read from the printed path. The normalize step only answers for CR, and a refusal
   has other causes, so the inline form is the attempt that does not depend on which one it
   was.
3. No `Workflow` tool in the session, or the `Bash` call came back non-zero, whether
   because the session carries no published root, because the source is not readable under
   it, or because the out dir could not be written: the in-context build, with the reason
   named. Those are different lines to say, so say which one it was.

Only step 3 builds in the main context, and only the conditions it names reach it. A first
path that does not resolve is a step of the resolution rule and not a step of this chain,
so a `Bash` call that comes back empty is step 3 only after the whole rule has been walked.
A run that has tasks to build and meets none of these conditions dispatches at step 1.
Invoking `/bb:implement`, by the command or by the phrases its `description` lists, is the
request for this workflow, and that request is the opt-in the `Workflow` tool asks for. It
covers this build and nothing beyond it.

**A session that forbids workflows outright is a third way to end up here, and it is not a
step of the chain.** An account or session level rule saying not to use workflows unless the
user asked outranks the opt-in above, and the tool never runs. The build proceeds in the
main context like step 3, and the line the skill owes says the session's own rules vetoed
the dispatch, so the reason reads as a veto and not as a missing file.

Two stops sit outside the chain, and neither is a step of it. A user who denies the
permission dialog has declined this dispatch: report the denial and ask what they want
instead. A stage zero that resolves the project's checks and is then **refused permission**
to run one stops the run before task 1: that is the `ran: false` case below. The policy
case is not a stop at all, and the two are easy to confuse because both end with nothing
having run.

## `args`

The skill builds this by reading the spec, and passes a real JSON value (never a
stringified one):

```
{
  slug: "<slug>",
  specPath: ".bb/<slug>/spec.md",
  checks: {
    commands: ["..."],
    source: "<which tier answered, null when none did>",
    truncated: true | false,
    resolved_count: 0,
    runnable: true | false,
    policy: { decision: "ci-only", source: "<path>", scope: "repo" | "machine", evidence: "<the line>" },
    unresolved: [{ command: "...", reason: "unrecognized-runner" | "shell-dependent", where: "<file>" }]
  },
  reuseNotes: ["<one string per reuse note in ## Decisions>"],
  phases: [{ title: "<the ### heading>", tasks: [1, 2] }],
  tasks: [
    { n: 1, title: "...", delivers: "...", behaviors: [2, 3], dep: [], verify: "..." }
  ]
}
```

`checks` is `scripts/resolve_checks.py`'s output, passed through
whole (or `null` when the skill could not run it). The script walks the authority chain,
so nothing in the run resolves it a second time: it is the same call implement's step 7
and ship's Step 2 make. `runnable: false` means local runs are forbidden, and it is what
makes stage zero skip the checks agent instead of spending it to be refused; `policy.scope`
says which document forbade them, the repo's own or the user's `~/.claude/CLAUDE.md`.

`null` and an empty `commands` are **not** the same ground, which is why `source` is in the
payload: `null` means the skill never resolved anything and the agent has to walk the chain
itself, while a non-null payload with `source: null` means the chain was walked and this
project has no checks. The prompt says whichever of the two it is, so a repo without a suite
is not sent looking for one.

`unresolved` is the third ground, and the only field in the payload that is not an answer. It
carries what the resolver saw and could not turn into something runnable: a command whose
runner it cannot name (`unrecognized-runner`), or one that needs the shell step that defined
it (`shell-dependent`). Non-empty, it is what keeps an empty `commands` from reading as "this
project has no checks" when it means "no runner I recognize", and what keeps a resolved list
from reading as the whole suite when it is not. `checksPrompt()` hands those leads over as
files to read rather than as a list to confirm, so the judgment lands with the agent that can
open the file. The alternative is a confident empty list over a suite that exists.

`tasks` carries only the ones still unticked at invoke time, in an order that already
satisfies `dep:`. The agents re-read the spec anyway: `args` is the plan, the file on
disk is the truth.

`phases` is the `###` headings inside `## Tasks` on the wire, one entry per heading in
document order, the heading's own text as `title` and its tasks named by `n`. The rule
those headings follow is `skills/spec/references/spec-format.md`'s. Read the section as
written, ticked tasks included: the script keeps only the members `tasks` still carries
and drops a group left with none, so a resumed run announces the phases it will actually
run. A `## Tasks` with no `###` heading sends no `phases` at all, and the script falls
back to its own fixed titles; the ground keeps `Ground` either way, since stage zero
belongs to the script and not to any task.

An empty `tasks` is not a run. The skill sees it first and reports nothing to build
without invoking; the script returns the empty report before stage zero, so a caller that
invoked anyway does not pay for the project's checks and every reuse note to build no
task.

## Stage zero: prove the ground before task 1

Two thunks at most, inside a single `parallel()`: one `bb-reuse-check` carrying every
reuse note the spec has, and the checks agent when there is something to run. This is a
legitimate barrier: nothing starts until every verdict is in. Both are read-only lookups,
so they run at `effort: 'low'`.

The reuse agent is dispatched **once per build and not once per note**, because a
subagent's context floor is paid per agent and re-read on every turn it takes: on the run
that measured it, eight notes over eight agents cost ~44k of prefix each for lookups of
three to five tool calls and a few hundred tokens of answer. One agent pays that floor
once. With no reuse note in the spec, no reuse thunk is sent at all, and stage zero is the
checks agent alone.

The role and the read protocol are `agents/bb-reuse-check.md`'s, delivered as the system
prompt through `opts.agentType`. `reusePrompt()` carries what only the caller has, the
numbered notes and one line of that protocol, and the schema carries the return shape, so
an `agentType` that does not resolve leaves a generic agent working from a floor rather
than an unbounded one. That is the same fallback the review fan-out sets for
`bb-review-finder`. It returns:

```
{ verdicts: [{ index: 0, verdict: "intact" | "moved" | "gone", note: "<what it looked for, plus file:line>", where: "<new path, required when moved>" }] }
```

`index` is the note the entry answers, numbered as the prompt sent them. **The script
checks the index set before it calls the ground proven**, not the count: a note left
unanswered and an index no note carries are each a stop naming what happened, since a note
nobody looked for would otherwise read as `intact` and the build would extend code that is
not there, and a count alone reads one note answered twice as two notes answered. A `moved`
verdict with no `where` is a stop for the same reason: that path is what the convention note
would otherwise render as `undefined` into every task prompt.

The checks agent confirms the list `args.checks` carries and then **runs all of them
once**. Running them is the point: it proves the run has permission to execute each one,
and it establishes the green baseline. With `args.checks` null it resolves the chain
itself, which is the only place the order is still spelled out at runtime. With
`unresolved` non-empty it opens the files that field names and decides there, so the list
it returns can be longer than the one it was handed. It returns:

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
`{ n: 0, status: "red", blocker: "<which note is gone, which went unanswered, which verdict cannot be placed, or which command and why>" }`.

A repo whose top authority forbids running checks locally fails here by policy and not by
breakage, so it is not a stop. The policy arrives as `runnable: false`, stage zero sends no
checks agent, `commands` is empty for the task agents too, and the log says the checks
belong to CI here. The build proceeds with the proof deferred to the PR, which is where
that policy wanted it.

`ran: false` keeps its meaning for the case it was written for: a command the run was
refused with no policy saying so. That is still a stop before task 1 and still a blocker to
report, naming the command, so the allowlist can be widened and the next run gets past
stage zero.

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

`taskPrompt()` in the script, and only there. It carries the spec path, the task's own
line, the behaviors it cites, the accumulated convention note and the check commands
stage zero resolved, then tells the agent what to do with them: build inside
`## Out of scope`, satisfy `verify:`, keep the checks green, commit the files it touched
together with its `- [x]`, return the result. Read the string when you need the wording: a
paraphrase here would be the second contract the opening says not to keep.

Two of its rules reach the caller, because they show up in the return:

- **A task already `- [x]` on disk returns `status: "skipped"` and builds nothing.** The
  agent re-reads the checklist itself, so a resumed run does not redo what landed: `args`
  is the plan, the file on disk is the truth.
- **`verify: CI` cannot run inside the build**, so it returns `result: "pending"` on a
  task that is otherwise green and committed, neither a pass nor a failure. That is what
  `pendingVerify` collects and what `/bb:ship` closes.

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

The caller reads that and follows its own contract: `/bb:implement` goes on to whatever
its scope has next, the review, the ship, or the gate that offers one. A non-null
`stopped` is its safety valve, so it flips `status: blocked` and nothing further in the
chain runs. `pendingVerify` names the tasks whose proof is CI, which is ship's to close.

## What guards the script, and what the skill still checks per run

Being code, the script gets most of its guarding from tooling rather than from a checklist
the run walks.

**CI and the pre-commit hook** own what a parse or a scan settles, in
`.github/scripts/validate-workflow-script.ts`, over a source whose comment, string,
template and regex bodies are blanked first, so only code is read:

- the file parses, wrapped the way the platform runs it;
- `export const meta` is present, and a pure literal: no interpolation, no spread, and no
  bare word other than `true`, `false`, `null` and `undefined`;
- `meta` carries a `name` and a `description`, which the platform reads for the permission
  dialog and for the workflow list;
- `meta.phases`, when the block declares it, has one entry per `phase()` call, and the
  titles match one for one, since a title is how the platform pairs an entry to a call;
- there is exactly one `parallel()`, and it comes before the task loop;
- `Date.now()`, `new Date()` and `Math.random()` appear nowhere, in any spelling: optional
  chaining is flattened before the scan, and `Date[...]` or `Math[...]` fails on its own.

It runs inside `package.json`'s `validate`, which is what lefthook's pre-commit job runs,
so the guard fires before the commit and not only in CI. oxfmt formats `js` alongside
`json` and `md`.

**A one-time PR review** owns what only reading the code settles: `schema` on every
`agent()` that needs a typed answer, and every result null-checked before use. That is a
review of a change to this script, not a step in a build run.

**The skill** owns the three that are genuinely per-run, and confirms them before
invoking:

- `args` is passed as a JSON value, `tasks` holds only unticked tasks, `phases` repeats the
  `###` headings of the same `## Tasks` in document order, and `checks` is
  `resolve_checks.py`'s output passed through whole.
- The branch the commits belong on already exists and is checked out; the agents commit
  where the run puts them.
- The agent count is `tasks.length`, plus one for the reuse agent when `reuseNotes` is not
  empty, plus one for the checks agent when `checks.runnable` is not false: stage zero is
  two agents at most, whatever the note count. Over the size guideline the session declares, say so
  in one line and invoke anyway; the real cap is 1000 agents per run.
