---
status: in-progress
created: 2026-09-27
slug: lean-spec-parallel-build
---

# A lean spec, and a build that runs each phase in parallel

The spec today is written for a builder that needs every technical fork closed before it
starts. With Opus 5.5 on the other side that is no longer true: the model settles the
technical details better at build time, with the code open, than a reviewer does ahead of
it. What the spec spends on those details comes back as review passes that keep finding
more of them, and as a long wait before anything gets built.

This change moves the spec closer to a plan. It says what gets built, the business rules
and the expected behavior, and the order the work runs in. A technical risk the author
sees goes in as an attention point: named, with no solution attached. The build side
changes with it: the `###` phases inside `## Tasks` run in sequence, and the tasks inside
one phase run in parallel.

Success: a Medium spec reaches the gate in one sitting, with at most one reviewer pass, and a spec
with a phase of three independent tasks builds that phase in the wall-clock time of its
slowest task.

## What the spec carries now

- **The opening**: what it is, why now, what success looks like.
- **The business rules**: what the thing must do and must never do, in the words of the
  product. A technical choice appears only when the user made it (a stack the company
  settled, a contract another team depends on).
- **`## Behavior`**: the happy path and the edges that change the outcome for the user.
- **`## Attention points`**: the technical risks the author saw. Each one names the risk
  and where it lives; the solution is the builder's.
- **`## Tasks`**, grouped in phases (below).
- **`## Out of scope`** and **`## Open`**, as today.

## How the phases are written

The author orders the work by what depends on what. A foundation that everything else
builds on is a phase of its own, with one task. The tasks that only need that foundation,
and that change different parts of the code, share the next phase. A closing task that
needs all of them is the last phase.

```
### Foundation          one task, runs alone
### The three surfaces  three tasks, run together
### Close               one task, runs after all three landed
```

Two tasks go in the same phase only when neither needs what the other produces. Phase
order replaces `dep:`.

## The gate

The gate is where the spec proposes the build, and it asks two things in one call:

- **What now**: `Build`, `Review the spec` or `Stop here`. `Review the spec` is offered
  only while the spec carries text no review has read.
- **What comes after the build**, as two boxes the user ticks or leaves: `Review the
branch` (`/bb:review`) and `Ship` (`/bb:ship`). Both empty is a build only.

The review runs once over what it gets, its findings are resolved, and the gate opens
again with the review option gone. What the user changes at that gate is new text, so
the option comes back; what the review's own findings changed is not.

`/bb:implement` asks the same second question at its step 2 when nobody asked it yet, so
the four scopes stop being four exclusive options that the spec gate had to cut to three.

## Decisions

- The review stops being an automatic step. The lint still runs before every gate; the
  reviewer, `bb-spec-reviewer`, runs only when the user picks `Review the spec` at the
  gate. The two lenses become one, and it reads for four things:
  - **happy path**: a step the flow takes that the spec skips or glosses over;
  - **edge cases**: a deviation that changes the outcome for the user and has no row, or
    a row with no decided outcome;
  - **coherence**: a contradiction between sections, a business rule no task delivers, a
    task outside the rules;
  - **attention points**: a technical risk the spec does not name, and a named one that
    does not matter to this build.
- The reviewer may open the files the spec names, to find the risks it names in the last
  item. It does not check every claim about the code against the repo: a wrong claim is
  paid at build time, where `bb-reuse-check`, the CI and `/bb:review` already look.
- An attention point the reviewer finds goes into `## Attention points` the way the author
  would write it: the risk and where it lives, with no solution.
- The adversarial completeness pass (step 5, `completeness-generators.md`, the coverage
  table) goes away. The gray-area loop with the user stays.
- The required technical forks section of `/bb:spec` goes away. The questions to the user
  are about what gets built and how it behaves.
- The task line keeps its title, what it delivers and `verify:`. It drops `dep:` and
  `→ behaviors`; the gate drops the coverage counter.
- Inside a phase the tasks run in parallel; the phases run in document order.
- A spec whose `## Tasks` has no `###` heading builds one task at a time, as today, so a
  spec written before this change keeps its order.
- A red task inside a phase does not cancel the others in that phase. The green ones land,
  the run stops before the next phase, and the red one is recorded in `## Open`.
- The task agent settles the technical details itself. It returns `underspecified` only
  when a business rule or a behavior is missing or contradicts another, and it reads
  `## Attention points` as risks to handle, not as instructions.
- The cheap tier of the build moves from `haiku` to `sonnet`: `CHEAP_MODEL` in
  `build-tasks.js`, which the reuse agent and the mechanical checks agent run on, and the
  tier the skill gives a mechanical task. `opus` and the session's model stay where they
  are, and `haiku` leaves the build.

## Behavior

Happy path, spec side: the user brings the idea, `/bb:spec` drafts it, asks about the gray
areas of what gets built, writes the phases, runs the lint, and opens the gate with what
it does, the phases with their tasks (marking which run together), and what is open.

Happy path, build side: stage zero proves the ground, then each phase dispatches all its
unticked tasks at once, waits for every one, lands the green ones on the run branch, ticks
their boxes, and moves to the next phase.

| WHEN                                             | THEN                                                                 |
| ------------------------------------------------ | -------------------------------------------------------------------- |
| a phase has one task                             | it runs the way a task runs today                                    |
| a phase has three independent tasks              | all three run at the same time                                       |
| one of three tasks in a phase comes back red     | the other two land, the run stops, the red one goes to `## Open`     |
| two parallel tasks changed the same lines        | the run stops before the next phase, naming both tasks and the files |
| the run resumes after a stop                     | ticked tasks are skipped; a phase with none left is skipped          |
| a spec has no `###` heading                      | the tasks run one at a time, in document order                       |
| a spec written before this change carries `dep:` | the build reads it and ignores the field                             |
| the author sees a technical risk                 | it goes in `## Attention points`, with no solution                   |
| the reviewer finds a risk the spec does not name | it goes in `## Attention points`, with no solution                   |
| the reviewer finds an edge with no row           | the row is added, or the outcome goes to `## Open`                   |
| the reviewer finds nothing                       | the gate says `clean`                                                |
| the user picks `Build` on a spec never reviewed  | it builds; the review is an option, not a requirement                |
| the review ran and nothing changed since         | the gate opens without `Review the spec`                             |
| the user changes the spec at the gate            | the gate opens with `Review the spec` again                          |
| the user picks `Review the spec` or `Stop here`  | the answer about after the build is ignored                          |
| `/bb:implement` invoked from the spec gate       | it asks nothing; the gate's answer is the scope                      |
| `/bb:implement` invoked on its own               | step 2 asks the second question, with the invocation's lead ticked   |
| a task agent meets a technical gap               | it decides and records the choice in the convention note             |
| a task agent meets a missing business rule       | it returns `underspecified` and the run stops                        |

## Attention points

- Parallel tasks sharing one working tree collide on files, on the git index and on the
  commit. `agent()` takes `isolation: 'worktree'`; each worktree has to start from the run
  branch as the previous phase left it, and its commits have to come back onto that branch.
- Every task ticks its box in the same `spec.md`, so ticking inside the task commit
  conflicts across a phase.
- Running the project's checks once per task, in parallel worktrees, multiplies memory use
  on a machine that has none to spare. Where the checks run (per task, or once per phase
  after the tasks land) is a build-time choice.
- The convention note is sequential today. Tasks in the same phase all receive the note as
  the previous phase left it, and their notes have to be joined for the next phase.
- `.github/scripts/validate-workflow-script.ts` fails any script with more than one
  `parallel()`. The rule has to follow the new shape.
- The resume cache is keyed on each agent's `(prompt, opts)`; the parallel dispatch has to
  keep the same prompt for the same task across runs.
- Knowing whether the spec changed since the last review: `references/spec-state.md`
  keeps the review's verdict out of the frontmatter, and a gate in a later session has
  no memory of the one before.
- `AskUserQuestion` takes at most 4 options per question; the gate's first question has
  3 and its second is `multiSelect`.
- Stage zero reads the reuse notes from `## Decisions`. With the lean format a reuse note
  is a technical detail, so it may move or disappear, and `bb-reuse-check` would receive
  nothing to check.
- `references/handoff-gate.md` carries the spec gate as its example and in the journey
  map; `/bb:brisar`'s Deliver and the gates of `think`, `challenge` and `discover` invoke
  `/bb:spec` and land on the new gate.
- `/bb:review`'s `contract` front reads `## Behavior` row by row, so the section keeps its
  table.

## Tasks

### The new format

- [ ] **1. The spec format**: `spec-format.md` describes the new sections, the phases and
      the task line; `lint_spec.py` knows `## Attention points`. · verify: reading

### Both sides adopt it

- [ ] **2. `/bb:spec` gets lean**: the loop without step 5, without the forks section and
      without the automatic review; the gate with its two questions, the review as an
      option and no coverage counter; `draft-first.md` follows;
      `completeness-generators.md` is deleted. · verify: reading
- [ ] **3. The reviewer's contract**: `agents/bb-spec-reviewer.md` loses the two lenses
      and reads for happy path, edge cases, coherence and attention points; its `tools:`
      stays read only. · verify: reading
- [ ] **4. The build runs phases in parallel**: `workflows/build-tasks.js` dispatches each
      phase's tasks together, lands them before the next phase and takes `sonnet` as its
      cheap tier; `taskPrompt()` settles technical gaps and reads `## Attention points`;
      the validator follows. · verify: CI
- [ ] **5. `/bb:implement` follows**: `implement/SKILL.md` and `build-tasks-workflow.md`
      describe the parallel phases, the stop inside a phase, the payload without `dep`, the
      tiers with `sonnet` in place of `haiku`, and step 2 as the second question of the
      gate. · verify: reading

### Close

- [ ] **6. The rest of the repo catches up**: `handoff-gate.md`, `operating-context.md`, `README.md`,
      `.claude/CLAUDE.md`, `doc-style.md`, the plugin version and `CHANGELOG.md`. · verify: CI

## Out of scope

- Parallelism across phases, or a task graph finer than the phases.
- Rewriting specs already in `.bb/` to the new format.
- The export mode (`export-spec.md`).
- A reviewer at build time; revisit if builds start stopping on underspecified specs.

## Open

Nothing.
