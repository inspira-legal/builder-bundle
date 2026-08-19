---
status: done
created: 2026-08-06
slug: build-via-workflow
---

# building the slices through a dynamic workflow

A new path in `/bb:implement` and in `/bb:delegate`: instead of building every slice in the
main context, dispatch a dynamic workflow that runs one agent per slice. The `dep:` and the
`verify:` each slice already carries are the DAG this orchestrator consumes without
reinterpreting prose.

The problem it solves is not speed. An eight slice brief built in a single context hits
compaction halfway through the build, and that is exactly where implement degrades: it
forgets the `## behavior`, it drifts from the `## decisions`. One agent per slice starts with
a clean budget and loads only the brief plus its own slice. The tacit context lost between
slices is paid for by a conventions note that crosses the stages, because compaction is
lossy too, with the difference that compaction is automatic and the note is designed.

Success: a large brief runs to the end without compacting, and what slice 3 built uses the
names slice 1 established.

## What the platform decides for us

**No input in the middle of a run.** Only a permission prompt pauses a workflow; the docs
say to run each stage as a separate workflow when you want sign off between them. That takes
implement's conversational safety valve out of the run: a slice agent can only _return_ "the
brief is underspecified", and the script is what decides.

**The script has no shell and no filesystem.** Only agents read, write and run a command.
Every gate, every commit, every `verify:` happens inside an agent; the script only
coordinates and reads structured returns.

**A command outside the allowlist does not ask for permission in a routine.** In `claude -p`
and in the SDK there is nobody to ask, so the call follows the configured rules without
confirmation, which in practice means it fails. A gate the routine has no permission to run
does not become a question, it becomes a red slice.

## Sequential, and why

The slices run in a `for` with `await`, not in `pipeline()`. `pipeline` runs each item
through every stage independently and concurrently, which is the wrong primitive here,
because the slices share the working tree and `dep:` exists precisely to say that slice 2
leans on what slice 1 created. Parallelizing would conflict in the tree, or would demand an
isolated worktree and a merge the script cannot execute.

The only genuinely parallel point is stage zero, read only by nature. There `parallel()` is
a legitimate barrier: nothing starts before every verdict arrives.

## Decisions

- **The choice is a question, in every run**: supervised `/bb:implement` and `/bb:delegate`
  open by asking between building through a workflow or in context, whatever the size of the
  brief. Unattended does not ask: always workflow.
- **The script is generated per run**: the skill authors the JS and passes it in `script`;
  the runtime persists it in the session directory and returns the path. It does not go to
  the plugin's `workflows/`, so it never becomes a `/bb:build-slices` command and never shows
  up in autocomplete.
- **The script's shape is a reference, not an executable**: `build-slices-workflow.md` fixes
  the contract the generated script has to meet, and the skill checks it before invoking.
- **A sequential `for`, `parallel()` only in stage zero.**
- **Stage zero runs the whole gate once**: it does not just locate the commands through
  implement's chain of authority, it executes all of them. That proves the permission and
  establishes the green baseline, so a tree that is already red becomes a blocker before
  slice 1 instead of a failed slice.
- **Whoever builds the slice runs the gate**: the same agent builds, meets the `verify:`,
  runs the gate, fixes what broke (a cap of 3 retries only on a flake signature, as
  implement already defines) and commits. No dedicated gate agent: whoever broke it has the
  context to fix it, and it is one agent less per slice.
- **A non-executable `verify:` becomes self inspection**: `reading` means the agent checks
  what it produced against the behaviors its slice cites and returns short evidence. `CI` is
  out of the run's reach, so it goes back pending for the ship. No `verify:` is silently
  skipped.
- **The conventions note accumulates, with a ceiling**: slice N receives the conventions of
  every earlier slice, not only of the immediately preceding one. Past roughly 1500
  characters the agent itself condenses the oldest ones and returns the version the next
  slice receives; no dedicated summary agent.
- **The commit is the checkpoint**: each agent commits only the files it touched, with its
  slice's `- [x]` in the same commit. A workflow resume only works in the same session and
  re runs everything that started after the first unfinished agent; the commits survive
  anything, so that is where the progress lives.
- **Idempotence through the checkbox**: the agent rereads `## tasks` on disk before building
  and returns right away if its slice is already ticked. Re running a half built brief does
  not redo what already landed.
- **A red slice does not commit and does not revert**: the tree stays as it is, for the
  diagnosis. The caller is who handles it, through the contract that already exists:
  implement stops at step 7, delegate flips `blocked` and does not go on to the ship.
- **A dead reuse note stops the run**: this is implement's safety valve firing at the
  cheapest possible price. `moved` goes on and enters the conventions note; `gone` stops.
- **Delegate does not ask twice**: it already suppresses implement's step 8, and now it also
  suppresses the mode question and passes along the decision it made.
- **`routines.md` loses the fan out ban**: the rule "single-agent only until you've measured
  cost" goes, and in its place comes the description of workflow mode as the routine's
  default, with the gate commands in the provisioning allowlist.
- **Low effort in stage zero, inherited model in the slices**: the pre-flight agents are
  read only lookups; the slice agents build and stay on the session's model.
- **Version**: `plugin.json` `2.6.0` → `2.7.0`; `implement` `2.1.0` → `2.2.0`; `delegate`
  `2.2.0` → `2.3.0`.

## Behavior

1. Supervised, `/bb:implement` and `/bb:delegate` open by asking between workflow and
   context; unattended does not ask and goes with the workflow.
2. Once the workflow is chosen, the skill authors the script per the reference and invokes
   `Workflow`, passing in `args` the slug, the path to the brief and the list of slices not
   yet ticked, each one with its `dep:` and its `verify:`.
3. Stage zero runs in parallel: one agent per reuse note in the brief, plus one that resolves
   the gate commands and runs all of them once.
4. A stage zero with a `gone` reuse note, an unexecutable gate or a tree already red stops
   the script before slice 1 and returns the blocker.
5. The slices run in a sequential `for`, one per agent, in the order `dep:` implies, in the
   same working tree.
6. Each agent rereads its slice's checkbox on disk before building; already ticked, it
   returns without touching anything.
7. It builds, meets the `verify:`, runs the gate, commits the files it touched together with
   the `- [x]`, and returns a verdict, the evidence and the conventions it established.
8. The conventions note accumulates: each agent receives the earlier ones and returns them
   plus its own, condensed by itself when it passes the ceiling.
9. An unrecoverable red gate, a failed `verify:`, a lost agent or an underspecified brief
   stops the loop without committing the slice; what came out green is already committed.
10. All green, the workflow returns and the caller goes on: implement at step 8, delegate at
    the ship. With the loop stopped, the caller receives the blocker and does not go on to
    the ship.
11. With no workflow available, both paths build in context and say why.

| WHEN                                     | THEN                                                                        |
| ---------------------------------------- | --------------------------------------------------------------------------- |
| workflows off by config or by org        | it does not offer the choice; it builds in context naming why               |
| unattended and workflows off             | it builds in context; the reason enters delegate's report                   |
| a reuse note points at code that is gone | stops before slice 1; the caller flips `blocked` and cites the spec         |
| a reuse note points at code that moved   | goes on; the new path enters the conventions note                           |
| a brief with no reuse note at all        | stage zero runs only the gate agent                                         |
| stage zero finds no gate at all          | goes on and reports there was no gate; it does not block                    |
| a gate command outside the allowlist     | fails in stage zero; stops with a permission blocker                        |
| the tree is already red before slice 1   | stops; the broken gate is not the build's and comes back a blocker          |
| the slice's `verify:` is `reading`       | the agent checks against the cited behaviors and returns evidence           |
| the slice's `verify:` is `CI`            | it comes back pending in the return; the ship is what checks it             |
| a red gate after the 3 retries           | the slice does not commit, the loop stops, the tree stays for the diagnosis |
| the agent finds the brief underspecified | it returns the blocker instead of improvising; the loop stops               |
| a slice agent comes back `null`          | treated as a failed slice, stops the loop, preserves what is green          |
| the run is stopped halfway               | commits and checkboxes hold the progress; re running resumes                |
| re run with slices already ticked        | their agents return right away; stage zero runs again                       |
| you leave Claude Code with the run alive | the next session does not resume the run; it resumes by the checkboxes      |
| delegate drives the build                | it asks only once; implement does not ask again                             |
| the brief has no `## tasks`              | it does not enter workflow mode                                             |
| the brief has a single slice             | it asks anyway; the choice is the user's, not a threshold's                 |

## Tasks

- [x] **1. The script shape reference**: `references/build-slices-workflow.md`, a sequential
      `for`, `parallel()` in stage zero, the return schemas, the accumulated note with its
      ceiling, idempotence through the checkbox, the commit scope, the handling of gate and
      allowlist, and the checklist the skill checks before invoking
      → behaviors 2, 3, 5, 6, 7, 8, 9 · dep: — · verify: reading
- [x] **2. The choice gate**: a shared reference with the question, when it appears and the
      unattended rule, in the format of `handoff-gate.md`
      → behavior 1 · dep: — · verify: reading
- [x] **3. delegate**: a new step between 2 and 3, passes the decision along to the build,
      suppresses implement's question and handles the blocker coming back by flipping
      `blocked`
      → behaviors 1, 4, 10 · dep: 1, 2 · verify: reading
- [x] **4. implement**: the same choice when invoked directly, suppressed when delegate
      drives; a blocker coming back falls into step 7's valve
      → behaviors 1, 4, 10 · dep: 1, 2 · verify: reading
- [x] **5. The fallback with no workflow**: detection and the in context path in both, with
      the reason stated → behavior 11 · dep: 3, 4 · verify: reading
- [x] **6. routines.md**: removes the fan out ban, describes workflow mode as the routine's
      default and puts the gate allowlist in the provisioning
      → behaviors 1, 3 · dep: 2 · verify: reading
- [x] **7. Version and docs**: `plugin.json` `2.7.0`, the versions of `implement` and
      `delegate`, the CHANGELOG, the new reference in `.claude/CLAUDE.md`
      → behavior 1 · dep: 1-6 · verify: CI

## Out of scope

- Parallelizing slices against each other: `dep:` and the shared tree prevent it. If one day
  there is a wide brief with several `dep: —` slices over disjoint files, that is a brief of
  its own (_revisit_).
- Pre-flight in the in context path: only workflow mode gets stage zero (_revisit_).
- A script versioned in `workflows/` and a `/bb:build-slices` command: decided against.
- Measuring cost per run automatically: `/workflows` already shows tokens per agent.
- Any change in `/bb:ship`; the workflow hands control back before the landing.

## Open

- Nothing.
