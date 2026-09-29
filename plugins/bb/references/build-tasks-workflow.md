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

A task agent receives the spec, its own line and the convention note, and it settles the
technical details the spec leaves open itself, with the code open. The spec says what gets
built and how it behaves; a gap there, a business rule or a behavior missing or
contradicting another, is the one thing the agent cannot decide, and it returns
`underspecified` for it. The review `/bb:spec` offers at its gate is an option the user
picks, so a spec can reach the build without one.

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

## Phases in order, the tasks of a phase together

The phases run in a `for` loop with `await`, in document order, not `pipeline()`.
`pipeline` runs each item through the stages independently and concurrently, which is the
wrong primitive here: a phase builds on what the phase before it landed, and phase order is
the only dependency the spec carries. `phaseGroups()` turns `args.phases` into the groups
the loop walks, and each group takes one of two paths:

- **`runInLine()`**, one task at a time on the shared tree: the implicit `Build` group of
  the tasks above the first `###` heading (or of every task, when the spec has no heading),
  and a `###` group left with a single unticked task. This is how a task ran before
  phases.
- **`runTogether()`**, for a `###` group with more than one unticked task: one `parallel()`
  dispatches every task at once, each with `isolation: "worktree"`, then one landing agent
  brings the green commits onto the run branch. A red task cancels nothing: its neighbours
  were written to need nothing from it, so the green ones land and the run stops before
  the next phase.

The first `parallel()` is stage zero, which is read-only and runs on the shared tree. Every
later one is a phase's fan-out, and each of its agents writes in a worktree of its own,
because parallel tasks on one tree would collide on the files, the git index and the
commit.

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
    { n: 1, title: "...", delivers: "...", verify: "...", model: "sonnet" }
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

`tasks` carries only the ones still unticked at invoke time, in document order. A task
carries no `dep` and no `behaviors`: phase order replaced the first, and the agent reads the
`## Behavior` rows its task touches in the spec itself, the way an instrumentation task reads
the `## Metric` event rows it names. A spec written before this change may still carry
`dep:` and `→ behaviors` on its lines; the skill reads the line and leaves both out. The
agents re-read the spec anyway: `args` is the plan, the file on disk is the truth.

`model` on a task is **optional and the only tier the payload sets**, because how hard a task
is, is the one thing about it the script cannot read. It takes `sonnet` or `opus`; the
script drops any other name, `haiku` included, says so in one line and runs that task on the
session's model, since a typo passed through would take down a run that had already proved
its ground. Omitted, the task inherits the session's model, which is the default and the
right answer for most tasks: the agent is doing the work the main context would have done. `## Effort and model`
below is the rule the skill applies to decide, and resume is what makes it a rule rather than
a judgment per run: the cache is keyed on the agent's `(prompt, opts)`, so a task whose model
moved between two runs of the same spec re-runs from scratch.

`phases` is the `###` headings inside `## Tasks` on the wire, one entry per heading in
document order, the heading's own text as `title` and its tasks named by `n`. The rule
those headings follow is `skills/spec/references/spec-format.md`'s. Read the section as
written, ticked tasks included: the script keeps only the members `tasks` still carries
and drops a group left with none, so a resumed run announces the phases it will actually
run and skips a phase with no task left. A task no heading claims sat above the first `###`
and runs first, alone, under the fixed title `Build`. A `## Tasks` with no `###` heading
sends no `phases` at all, and every task runs that way, one at a time in document order; the
ground keeps `Ground` either way, since stage zero belongs to the script and not to any task.

An empty `tasks` is not a run. The skill sees it first and reports nothing to build
without invoking; the script returns the empty report before stage zero, so a caller that
invoked anyway does not pay for the project's checks and every reuse note to build no
task.

## Stage zero: prove the ground before task 1

Two thunks at most, inside a single `parallel()`: one `bb-reuse-check` carrying every
reuse note the spec has, and the checks agent when there is something to run. This is a
legitimate barrier: nothing starts until every verdict is in. Both are read-only, and their
tiers are the script's own, computed from the payload: `## Effort and model` below is where
that rule is stated.

The reuse agent is dispatched **once per build and not once per note**, because a
subagent's context floor is paid per agent and re-read on every turn it takes: on the run
that measured it, eight notes over eight agents cost ~44k of prefix each for lookups of
three to five tool calls and a few hundred tokens of answer. One agent pays that floor
once. With no reuse note in the spec, no reuse thunk is sent at all, and stage zero is the
checks agent alone.

The role and the read protocol are `agents/bb-reuse-check.md`'s, delivered as the system
prompt through `opts.agentType`. `reusePrompt()` carries what only the caller has, the
numbered notes, and the schema carries the return shape. It returns:

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
`{ n: 0, status: "red", blocker: "<which note is gone, which went unanswered, which verdict cannot be placed, which command and why, or which agent could not be dispatched and what the platform said>" }`.

A dispatch that never happens is the newest of those kinds. When the platform refuses the name
an agent is sent under, the thunk throws before any agent exists, and the slot `parallel()`
hands back is empty in exactly the way a lost answer is. So each stage-zero thunk records the
platform's message on the way past, logs it and re-throws: the run keeps the platform's own
failure record, and the stop reads `the reuse agent could not run: <message>`, or the same
sentence with `the checks agent` in front. With no message recorded the two branches keep
saying `returned nothing`, which is then true. When both agents fail the reuse blocker is the
one reported, since the branches are a chain; the checks cause sits in the log beside it.

A repo whose top authority forbids running checks locally fails here by policy and not by
breakage, so it is not a stop. The policy arrives as `runnable: false`, stage zero sends no
checks agent, `commands` is empty for the task agents too, and the log says the checks
belong to CI here. The build proceeds with the proof deferred to the PR, which is where
that policy wanted it.

`ran: false` keeps its meaning for the case it was written for: a command the run was
refused with no policy saying so. That is still a stop before task 1 and still a blocker to
report, naming the command, so the allowlist can be widened and the next run gets past
stage zero.

## The phase loop

`failureOf()` reads every task result the same way, whichever path ran it. Five exits, and
each needs its own line. A `null` return (the user skipped the agent, or it died on a
terminal API error) is a failed task that carries no blocker of its own, so the script
writes one. Assigning `stopped = r` there would hand the caller a `null` `stopped`, which
reads as a clean run over a half-built spec. A `skipped` task was already ticked before the
run: count it and move on, keeping the conventions the loop already had. A `green` task
whose `verify` is missing, or whose `verify.result` is `failed`, is a failure too: `verify:`
is what makes a task done, so green over an absent proof is a task the caller would read as
proven. A task built in a worktree that returns green with no `commit` is one more, since
its sha is the only way its work lands. Anything else is a failure as it came back.

In line, the first failure stops the loop and keeps what is green. Together, every result of
the phase is read first, and then the landing agent, `land: <title>` on the cheap tier, runs
over the whole phase. It confirms the main checkout is on a branch with a clean tree, then:

1. cherry-picks the green commits in `n` order, and removes each worktree whose commit
   landed, since that commit now lives on the run branch;
2. aborts a pick that stops on a conflict and names it, with the tasks already landed whose
   commits touched the same files, keeps that worktree, and resolves nothing: two tasks that
   changed the same lines are the author's to reconcile;
3. writes one line per task that did not come back green into `## Open`, in its own commit;
4. runs the project's checks over the landed tree, when something landed, and fixes what the
   landed tasks broke together, in a commit of its own, under the same flake rule a task
   agent follows;
5. ticks the landed tasks in one commit when the checks are green; when one is still red, it
   ticks nothing and writes into `## Open` which tasks landed and which check their boxes
   wait for;
6. joins the notes of the landed tasks onto the note the phase started from.

It returns:

```
{ landed: [<n>], conflicts: [{ n, with: [<n>], files: ["..."] }], checksGreen: true | false, blocker: "...", conventions: "..." }
```

`landed` and `conflicts` together have to account for every green commit the agent was
handed, and the script checks that: a commit neither landed nor named as a conflict is a
cause of its own. The phase stops the run when any task was red, any commit conflicted or
went unaccounted for, the checks went red after the landing, or the landing agent returned
nothing, which leaves the green commits waiting in their worktrees and names them. A lone
red task is handed back as it came, so an `underspecified` reaches the caller intact;
anything more is one stop, `{ n, status: "red", blocker }`, with every cause joined by
`|`. A stop ends the run and not just its phase: the next phase builds on what this one
landed, and a half-landed phase is not that ground.

## What the task agent is told to do

`taskPrompt()` in the script, and only there. It carries the spec path, the task's own
line, the accumulated convention note and the check commands stage zero resolved, then
tells the agent what to do with them: build inside `## Out of scope`, handle the risks
`## Attention points` names the way it chooses, settle a technical gap itself and record the
choice, satisfy `verify:`, keep the checks green, commit the files it touched together with
its `- [x]`, return the result.

Its last argument, `together`, is the one fork in the contract. A task that shares its
phase starts by resetting its worktree to the run branch's tip, found from
`git worktree list --porcelain`, runs none of the checks, makes exactly one commit without
ticking its box, and returns its `worktree` path beside the `commit` and only the note it
established. What it would otherwise do on the shared tree moves to the landing agent, which
sees the whole phase at once. Nothing about the phase's other tasks enters the prompt, so the
same task sends the same string whichever of its neighbours already landed, and the resume
cache still finds it. Read the string when you need the wording: a
paraphrase here would be the second contract the opening says not to keep.

Two of its rules reach the caller, because they show up in the return:

- **A task already `- [x]` on disk returns `status: "skipped"` and builds nothing.** The
  agent re-reads the checklist itself, so a resumed run does not redo what landed: `args`
  is the plan, the file on disk is the truth. In a worktree it reads the checklist after
  the reset, so the ticks it sees are the run branch's.
- **`underspecified` is for a business rule or a behavior** the task needs that the spec
  does not state, or that contradicts another. A technical gap is not one: the agent
  decides and records the choice in the convention note.
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
  worktree: "<the worktree's absolute path, when built in one>",
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
dedicated summarizer agent.

Inside a phase that runs together the note stops being a chain. Every task receives the note
as the previous phase left it and returns only what it established; the landing agent joins
the landed tasks' entries onto the phase's starting note and condenses it past the same
ceiling. A task that did not land adds nothing, and when the landing agent returns no note,
the script's own join of the landed entries is what travels to the next phase. What belongs in it: names and paths introduced, signatures
other tasks will call, a pattern chosen among alternatives, and any `moved` reuse target
from stage zero. What does not: anything already written in the spec.

## Effort and model

One dispatch, and each agent on the model its own job earns. Cost is bought with the
**model** and capability is kept with **`effort`**, so the two move together: a cheap
tier is never a strong model with its reasoning cut, which would be saving on the
answer instead of on the lookup.

The rule is the script's, computed from the payload it already has, so the same spec
dispatches the same tiers twice and the decision is readable in one place:

- **The reuse agent: `sonnet` at `effort: 'low'`, always.** `Grep` on the symbol a note
  names and a verdict per note is the whole job, and `REUSE_VERDICTS` is what shapes
  the answer. Nothing here is bought by a stronger model.
- **The checks agent: the payload decides.** Confirming a list `resolve_checks.py`
  already produced and running it is mechanical, so that one is `sonnet` at
  `effort: 'low'` too. A `checks` that is `null`, `truncated`, or carrying `unresolved`
  leads hands the agent the judgment the resolver could not make, and that one keeps
  the session's model and effort. The run logs which of the two it got, because silent,
  the expensive branch reads as the cheap one.
- **The landing agent: `sonnet`, at the session's effort.** Cherry-picks and ticks are
  mechanical; naming a conflict, fixing what the phase broke together and condensing the
  note are the judgment, and the cheap tier carries all three.
- **Task agents inherit the session's model and effort**, unless the task's own `model`
  says otherwise. They are doing the work the main context would have done, and settling
  the technical details the spec leaves open.

`CHEAP_MODEL` in the script is `sonnet`, and it is the one name the reuse agent, the
mechanical checks agent and the landing agent take. `haiku` left the build with it.

`model` on a task is the skill's to set, and it is set from the task's own line rather
than from a fresh judgment each run: a doc-only cut, a mechanical rename, a `verify:`
that is one command all earn the cheap tier, `sonnet`; the one task the spec's
`## Decisions` turned on earns the strong one, `opus`; everything else says nothing and
inherits. Two runs of the same spec have to reach the same answer, or resume re-runs the
tasks whose tier drifted. Set none, and every task runs on the session's model, which is what the build
did before this rule existed.

## What the script returns

```
{ slug, built: [<n>], skipped: [<n>], pendingVerify: [<n>], stopped: <the failing result, or null>, conventions }
```

The caller reads that and follows its own contract: `/bb:implement` goes on to whatever
its scope has next, the review, the ship, or the gate that offers one. A non-null
`stopped` is its safety valve, so it flips `status: blocked` and nothing further in the
chain runs. After a stop inside a phase, `built` still names the tasks of that phase that
landed and were ticked, and the red ones are already in the spec's `## Open`. A phase whose
checks stayed red after the landing adds nothing to `built`: its tasks landed unticked, and
the stop names them. `pendingVerify` names the tasks whose proof is CI, which is ship's to close.

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
- the first `parallel()` comes before every loop, since stage zero proves the ground before
  the first task runs, and every later one passes `isolation: "worktree"`, since only stage
  zero reads without writing;
- `Date.now()`, `new Date()` and `Math.random()` appear nowhere, in any spelling: optional
  chaining is flattened before the scan, and `Date[...]` or `Math[...]` fails on its own.

`.github/scripts/validate-agent-names.ts` is the third validator, and it reads a wider
tree: every `.js` and `.md` under `plugins/bb/`, anchored on the keys `agentType:` and
`subagent_type:`. A bb agent's name written without the plugin prefix fails, and so does a
`bb:` name with no such agent. Any other name passes in silence, so a dispatch of a
platform agent is not a false failure.

All three run inside `package.json`'s `validate`, which is what lefthook's pre-commit job
runs, so the guards fire before the commit and not only in CI. oxfmt formats `js` and `ts`
alongside `json` and `md`.

**A one-time PR review** owns what only reading the code settles: `schema` on every
`agent()` that needs a typed answer, and every result null-checked before use. That is a
review of a change to this script, not a step in a build run.

**The skill** owns the three that are genuinely per-run, and confirms them before
invoking:

- `args` is passed as a JSON value, `tasks` holds only unticked tasks, `phases` repeats the
  `###` headings of the same `## Tasks` in document order, and `checks` is
  `resolve_checks.py`'s output passed through whole.
- A task carries `model` only where its own line earns a tier other than the session's, by
  the rule in `## Effort and model`, and the same spec earns the same answer on a re-run.
  Stage zero's two tiers are the script's and take nothing from the payload.
- The branch the commits belong on already exists and is checked out; the agents commit
  where the run puts them.
- The agent count is `tasks.length`, plus one for the reuse agent when `reuseNotes` is not
  empty, plus one for the checks agent when `checks.runnable` is not false, plus one landing
  agent per `###` phase with more than one unticked task: stage zero is two agents at most,
  whatever the note count. Over the size guideline the session declares, say so
  in one line and invoke anyway; the real cap is 1000 agents per run.
