---
status: in-progress
created: 2026-09-02
slug: build-phases-and-cost
---

# Phases from the spec, and the floor under stage zero

The build's progress display names its phases `Ground` and `Build` for every spec it ever
runs, because both titles are literals in `build-tasks.js`. A run over a spec about the
ingestion pipeline and a run over a spec about a CLI flag look identical from the outside,
and the person watching learns nothing from the two group headers. The phases should read
like the work: `Prove the ground`, `Migrate the callers`, `Drop the old path`.

That was the ask, and answering it found two things sitting next to it. The dispatch this
display belongs to does not run at all on a Windows install: every installed copy of
`build-tasks.js` carries CR, the permission layer refuses it as a control character, and the
documented fallback chain ends in the in-context build every time. And stage zero costs more
than the build it introduces: on the measured run, eight reuse agents at 57k to 64k each
against one task agent, out of 631.9k for the whole run.

The three land together because they are one path, in one order. The dispatch has to work
before a phase title has anywhere to appear, and the stage zero it dispatches is where the
tokens go. Done, a build over this repo announces its own phases, the workflow runs from a
Windows install, and stage zero costs one context floor instead of eight.

## What the card can and cannot say

The progress card draws from two places, and only one of them is writable at runtime:

| the card shows           | comes from         | runtime |
| ------------------------ | ------------------ | ------- |
| `build-tasks`            | `meta.name`        | no      |
| the one-line description | `meta.description` | no      |
| `Ground`, `Build`        | `phase()`          | yes     |
| `8/8`, `0/1`             | the run itself     | yes     |
| `reuse: …`, `task 3: …`  | `opts.label`       | yes     |
| the narrator line        | `log()`            | yes     |

`meta` must be a pure literal, so the workflow's name and description cannot carry the slug.
Everything the group headers show can, which is what the phases decision below rests on.

## Where stage zero's tokens went

Five of that run's eight reuse agents, read from their transcripts under
`subagents/workflows/wf_dbe35cc4-8af/`:

| reuse agent | tool calls                   | output | cache write |
| ----------- | ---------------------------- | ------ | ----------- |
| aff01169    | Bash, Bash, Bash             | 761    | 44,497      |
| ad87a620    | Bash, Grep, Bash             | 658    | 44,790      |
| a81d2ffa    | Glob, Grep, Read             | 307    | 74,154      |
| a40d1407    | Grep, Glob, Read, Read       | 909    | 76,348      |
| a4d076e3    | Bash, Grep, Bash, Read, Read | 749    | 180,469     |

Nobody swept the repo: three to five tool calls, 11 to 19 seconds, 300 to 900 tokens of
output. The cost is context prefix, and it has two parts. The floor is ~44k per subagent,
which the two cheapest rows are made almost entirely of, paid once per agent and re-read on
every one of that agent's six to eight turns (271k of cache read for a 307-token answer).
On top of the floor, each whole-file `Read` adds ~30k, which is the part `reusePrompt`'s
`Read the repo.` invites. One agent for eight notes pays the floor once; the read protocol
is what keeps the second part off.

## The dispatch on Windows

The repo's `plugins/bb/workflows/build-tasks.js` is LF, `.gitattributes` is
`* text=auto eol=lf`, and `core.autocrlf` is false. Every installed copy carries CR anyway,
the version caches under `~/.claude/plugins/cache/inspira-legal/bb/` and the marketplace
clone alike. The installer does not honor `.gitattributes`, so nothing in the repo fixes
this, and CR takes out both dispatch steps at once, because step 2 inlines the same bytes
step 1 was refused for. Normalizing at dispatch time is the fix, and it makes step 2
redundant rather than fixed.

## What the platform says, and where

Three of this spec's claims are about the `Workflow` tool rather than about this repo, so
they are attested by its authoring reference and by no file here. Written down because the
grounding read of a task will otherwise find them unsupported:

- `opts.agentType` on an `agent()` call takes a custom subagent type, resolved from the same
  registry as the `Agent` tool, and composes with `schema`.
- A `phase()` call with no matching `meta.phases` entry gets its own progress group, so
  deleting `meta.phases` improves the headers instead of removing them.
- `agent()` returns null when the user skips it or the subagent dies on a terminal error,
  which is the null the build loop already reads as `stopped`.

## Decisions

- **The phases come from the spec, as `###` inside `## Tasks`.** The heading is the phase
  title, the tasks under it are its members, and document order is run order. The skill
  never names a phase at dispatch time: a name invented per run is unreviewed, and it
  invalidates the resume cache, which keys on the prompt and the label.
- **`meta` stays a literal.** `name` and `description` keep their current values;
  `meta.phases` is deleted, which is what frees `phase()` to take a computed title. The
  identification moves to a `log()` on the script's first line, rendering the slug as prose:
  hyphens to spaces, first letter capitalized, so `build-phases-and-cost` reads
  `Build phases and cost`. The separator is `·`, the one the task shape already uses.
- **The ground keeps a fixed title.** Stage zero belongs to the script, not to any task, so
  it stays `Ground`. The spec's phases cover the tasks.
- **A stopped task ends the run, not just its phase.** That is today's behavior, the `break`
  out of the single loop, and the phases change keeps it: the loop gains an outer level, and
  a stop leaves both. Later phases are never announced, because `phase()` fires as its group
  is entered.
- **Nothing loops above the fan-out.** `validate-workflow-script.ts:39` matches `for`,
  `while` and `do` as words and fails any of them positioned before the `parallel()` call,
  so the `log()` line and the reuse payload are built without one; `args` arrives shaped and
  the phase walk lives after the ground.
- **`lint_spec.py` does not change.** `HEADING` is `^##\s+`, which `### Prove the ground`
  cannot match, so the grouping is invisible to it and to `scan_specs.py`, which counts
  tasks by `^\s*-\s+\[ \]`, over all the specs already in `.bb/`.
- **One `bb-reuse-check` carries every note.** One floor instead of eight. The schema is
  `{verdicts: [{index, verdict, note, where}]}`, one entry per note, `index` into the array
  the prompt sent, `verdict` the existing `intact` / `moved` / `gone`, and `where` the path
  only when the verdict is `moved`. Stage zero's `parallel()` keeps two thunks, reuse and
  checks, so the validator's single-`parallel()` invariant holds untouched.
- **The reuse contract splits by kind, and the prompt keeps a floor.** The agent owns the
  role and the read protocol: confirm by `Grep` on the symbol, and when code must be seen,
  read the window around the cited line, never a whole file, never an edit. The script owns
  the notes and the schema, plus one line of that protocol, so an `agentType` that fails to
  resolve degrades into a working generic agent instead of an unbounded one. That is the
  fallback `.bb/review-agents/spec.md:119` already set for `bb-finder`.
- **The normalizer's contract is a CLI.**
  `<plugin-root>/scripts/normalize_workflow.py <source> [--out <dir>]` reads the source as
  bytes, drops every `\r`, writes the copy under the out dir and prints its path, one line,
  nothing else. `--out` defaults to a directory under the system temp, so the script needs
  nothing published to it; the skill passes its session scratchpad when it has one. It sits
  at the plugin root rather than in `skills/implement/scripts/` because its reader is the
  plugin-level `references/build-tasks-workflow.md`, which is what any future dispatcher of
  a workflow reads.
- **The dispatch normalizes unconditionally.** A conditional strip is a branch that saves
  microseconds and only runs on the machines where it is wrong. `scriptPath` points at the
  copy.
- **The fallback chain loses step 2.** With the normalizer between the file and the tool, an
  inline `script` read off the same bytes adds nothing, and the CR paragraph goes with it.
  The chain becomes two conditions: dispatch, or the in-context build with the reason named.
- **Task parallelism is not in this spec.** See `## Out of scope`.

## Behavior

The happy path, one line per step:

1. `/bb:implement <slug>` resolves the spec, reads `## Tasks` with its `###` groups, and
   builds `args` with `phases` next to `tasks`.
2. It runs `<plugin-root>/scripts/normalize_workflow.py` over the workflow, which writes the
   CR-free copy under the out dir and prints that one path.
3. `Workflow` dispatches with `scriptPath` set to the copy, and the approval dialog shows
   the copy's path.
4. The script's first line logs `Build phases and cost · 7 tasks, 4 phases`.
5. Stage zero fans out two thunks: one `bb-reuse-check` carrying every reuse note, one
   checks agent.
6. The build walks `args.phases` in order, calling `phase(title)` and then running that
   phase's tasks sequentially.
7. The script returns `{slug, built, skipped, pendingVerify, stopped, conventions}`,
   unchanged in shape.

| WHEN                                       | THEN                                                                |
| ------------------------------------------ | ------------------------------------------------------------------- |
| the source script is missing or unreadable | the normalizer exits non-zero and the run builds in context         |
| the out dir cannot be written              | the same: the normalizer is the one failure the chain reads         |
| the source is already LF                   | the copy is byte-identical and the dispatch proceeds                |
| the user denies the approval dialog        | report the denial and ask, outside the chain, as today              |
| `args.phases` is absent                    | the script falls back to `Ground` and `Build`, as today             |
| a task sits before the first `###`         | it joins an implicit `Build` phase, in list order                   |
| a phase has no unticked task               | no `phase()` fires for it, and an empty group is never announced    |
| every task is already ticked               | nothing is dispatched and the run reads as clean                    |
| a task stops mid-run                       | the run ends there and the later phases never announce              |
| the reuse agent returns fewer verdicts     | stage zero stops, naming how many notes went unanswered             |
| a note comes back `gone`                   | stop, and the safety valve hands back to `/bb:spec`                 |
| a note comes back `moved`                  | the new path travels in the convention note                         |
| there are no reuse notes                   | no reuse thunk is sent                                              |
| local checks are forbidden                 | stage zero sends the reuse thunk alone                              |
| neither notes nor runnable checks          | `parallel([])` returns `[]` and the synthetic green baseline stands |
| `bb-reuse-check` does not resolve          | the generic agent runs on the prompt's own floor, as review does    |

## Tasks

### The dispatch

- [x] **1. The normalizer**: `plugins/bb/scripts/normalize_workflow.py` with the CLI the
      decision states, reading bytes and writing the copy with `write_bytes`
      → behavior 2 and the missing-source, unwritable-out and already-LF rows · dep: — ·
      verify: command, running it over the repo's own workflow and counting CR in the copy
- [x] **2. The chain shrinks to two**: `references/build-tasks-workflow.md` invokes through
      the normalizer, loses step 2 and loses the CR paragraph, and `implement/SKILL.md`
      step 6 follows it
      → behavior 3 and the denial row · dep: 1 · verify: reading

### Phases from the spec

- [x] **3. The script takes phases**: `meta.phases` deleted, the `log()` first line with the
      slug as prose, and the phase walk after the ground, with the two-title fallback and
      the return shape untouched
      → behaviors 4, 6, 7 and the absent-phases, pre-`###`, empty-phase and stopped rows ·
      dep: — · verify: reading
- [x] **4. The payload and the format**: `implement/SKILL.md` builds `phases` from the `###`
      groups, the reference's `args` section carries the field, and `spec-format.md`
      documents the grouping under the task shape
      → behavior 1 and the every-ticked row · dep: 3 · verify: reading

### The floor under stage zero

- [ ] **5. `bb-reuse-check`**: `plugins/bb/agents/bb-reuse-check.md` with
      `tools: Read, Grep, Glob`, the role, and the read protocol that keeps whole-file reads
      out
      → behavior 5 · dep: — · verify: CI
- [ ] **6. One agent for every note**: `reusePrompt` takes the list and one line of the
      protocol, the schema becomes the indexed array, the thunk carries `agentType`, the
      verdict count is checked before the ground is called proven, and the reference's
      stage-zero section stops describing one agent per note
      → behavior 5 and the reuse, checks-forbidden, empty-fan-out and unresolved rows ·
      dep: 5 · verify: reading

### Landing

- [ ] **7. Docs and version**: `README.md`'s agent count and `.claude/CLAUDE.md`'s tree gain
      the fourth agent and the new script, `CHANGELOG.md` gains the entry, and the bumps are
      plugin `3.5.0` to `3.6.0` and implement `3.0.0` to `3.1.0`
      → no behavior of its own · dep: 1-6 · verify: CI

Suggested PR: `feat(build): fases vindas da spec, dispatch sem CR e um agente de reuse`.

## Out of scope

- Running independent tasks in parallel (_revisit_). It needs a worktree per task and a
  merge agent per level, and the convention note stops being serial, which is where `dep:`
  actually lives. Nothing here blocks it later.
- Replacing the validator's single-`parallel()` invariant (_revisit_). It only becomes wrong
  alongside the item above, and this spec leaves the count at one.
- Making the review a phase of `build-tasks.js` (_revisit_, as its own spec). Its fan-out is
  a second `parallel()`, which the invariant above forbids, its orchestration lives in
  `skills/review/references/` and copying it here would be a second definition of that
  engine, and the fronts probe it opens with is shell work a workflow script cannot do. What
  it would buy is the card, `Find` and `Verify` as group headers, and that belongs to a
  `workflows/review-fronts.js` of its own, dispatched by `/bb:review`.
- Generating the workflow script per run. It buys a dynamic `meta`, and it costs the task
  agent's contract being versioned, reviewed and validated, plus the resume cache.
- Chasing `.gitattributes` or the plugin installer. The CR is normalized at the point of
  use, and where it comes from stays broken.

## Open

Nothing.
