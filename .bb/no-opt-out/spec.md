---
status: done
created: 2026-08-19
slug: no-opt-out
---

# the build stops being optional: it always runs as a workflow

`build-via-workflow` shipped the one-agent-per-task build as a **choice**, asked at the
start of every `/bb:implement` and `/bb:delegate` run, and shipped the script as prose the
skill re-authors per run. The pass that catches what the main context loses is assembled by
the context that is about to skip it.

This change executes it instead of offering it. The mode question goes, the workflow becomes
the only build path, and the in-context build survives as the last step of the fallback chain
in `## Decisions`, for a session that cannot dispatch.

Success: `/bb:implement` and `/bb:delegate` reach the build with nothing asked.

## Why the script stops being generated

Every per-run variation is already in `args`. The generated script decides nothing `args`
does not carry, so authoring it per run is the same file rewritten from prose every time,
with a hand-run checklist as its only test, in a file CI never sees. Fixed, it becomes code
oxfmt formats, a PR reviews once, and CI parses. The cost is that a signature error stops
being caught by the next run and starts being caught by nothing, which is why task 1 owes a
smoke run and not a re-read.

It also retires the mode question's second argument. "What does this session know that the
file doesn't" was the discriminator for recommending the in-context build; with no choice
left it becomes a **requirement on the spec**. A task agent gets the spec, its own line and
the convention note, so a spec no fresh agent can build from is a broken spec, not a reason
to build elsewhere. `/bb:spec`'s step 6 is where that question gets asked.

## Decisions

- **The build mode question is deleted.** `/bb:implement` and `/bb:delegate` invoke the
  workflow. No threshold: a spec with one task goes the same way, because the value of the
  rule is having no branch, and one agent paying from scratch for repo orientation is the
  price of that.
- **The in-context build survives as the fallback only**, announced in one line so the
  downgrade does not read as a preference. It fires when the `Workflow` tool is absent
  (`disableWorkflows`, org-managed settings, a client that predates it), when the script
  file cannot be read, and when both ways of passing the script are refused.
- **The script is fixed and versioned**: `plugins/bb/workflows/build-tasks.js`. A new
  directory, because `scripts/` means "executable a skill calls through Bash" and this one
  is loaded by the workflow runtime.
- **The skill resolves the path and proves the file in one `Bash` call**, a `cat` of
  `$CLAUDE_PLUGIN_ROOT/workflows/build-tasks.js` into `/dev/null` followed by an `echo` of
  that same path. A non-zero exit is the missing-file case, and the printed path is what
  goes into `scriptPath`, expanded before the call because the tool takes a literal path.
- **`scriptPath` refused falls back to inline `script`**, read off the same file, then to
  the in-context build. One attempt each, one source either way.
- **A name in autocomplete is an accepted cost, not a blocker.** Named workflows resolve
  from `.claude/workflows/`, and whether a plugin's own `workflows/` directory registers
  anything is undocumented and unverified. If it turns out to register, `build-tasks`
  appears in autocomplete and nothing else changes; the invocation stays `scriptPath`.
- **`.claude/CLAUDE.md` registers the JS exception** and its reason: the workflow runtime
  is JS, so the language is not a choice here. The Python-first rule keeps holding for
  everything a skill invokes through Bash.
- **The skill still builds `args` by reading the spec.** No parser script: the reading
  implement already does stays where it is, and `tasks` keeps the fields the current schema
  carries (`n`, `title`, `delivers`, `behaviors`, `dep`, `verify`). It still resolves the
  project's checks through the authority chain to fill `checksHint`; only the running of
  them moves into stage zero.
- **The task agent's contract lives inline in the script**, as the prompt string, and it is
  the definition. The **retry cap becomes a constant in the script, 3**, and applies only to
  a check that failed and then passed on a re-run with no file changed in between. That is
  the whole definition of the flake signature, and it lives in the script beside the
  constant, because today the number exists only inside `.bb/build-via-workflow/spec.md`,
  attributed to an `implement` rule that was never written.
- **The API the script is written against is `build-tasks-workflow.md` plus the `Workflow`
  tool's own description**, and the proof it was read correctly is task 1's smoke run: a
  throwaway one-task spec, invoked exactly the way the skills invoke it, asserted to return
  that task as built. Reading cannot catch a wrong call signature, and a fixed script that
  CI only parses would ship the error.
- **`build-mode.md` is deleted by the last task**, once no reader is left: the two skills
  go first, the `.claude/CLAUDE.md` tree goes with the deletion. Both of its arguments move
  into `build-tasks-workflow.md`, the compaction one (a spec of eight tasks built in one
  context drifts from its own `## Decisions`) and the self-sufficiency one, which becomes a
  requirement on the spec that `/bb:spec`'s step 6 already checks.
- **`build-tasks-workflow.md` stops being a contract to meet and starts documenting the
  script**: `args`, the return schemas, the convention note with its ceiling, and the
  pre-invoke checklist split three ways.
- **The checklist splits into CI, PR review and the skill.** CI takes what a parse or a
  regex settles: the file parses, `export const meta` is present, a pure literal, and
  carries `name` and `description`, its `phases` entries match the `phase()` calls title by
  title, there is exactly one `parallel()` and it precedes the task loop, and none of
  `Date.now()`, `new Date()` or `Math.random()` is reachable, including through optional
  chaining and through a subscript. A one-time PR review takes what only reading the code settles (`schema`
  on every typed `agent()`, every result null-checked). The skill keeps the three that are
  genuinely per-run: `args` passed as a JSON value with only unticked tasks, the branch
  already checked out, and the agent count against the guideline the session declares.
- **The CI guard is a bun script over the source**: `Bun.Transpiler` proves the file
  parses, and a regex over the same source fails the forbidden calls. No new dependency,
  and the prompt string never names those calls, so a match is a real finding. It joins
  `package.json`'s `validate` script, which is what lefthook's pre-commit job runs, so the
  guard fires before the commit and not only in CI.
- **`js` joins the lefthook oxfmt glob**, which today covers `json` and `md` only, so the
  formatter is not what first meets the file in CI.
- **A blocked run records why, not just that it blocked.** `/bb:delegate` already flipped
  `status: blocked`, and the blocker itself lived only in the session that hit it. Ship's own
  stop has written it down all along, so the build side matching it closes an asymmetry rather
  than adding a rule. Where it lands follows the destination, the PR description or the
  spec's `## Open`, and the route follows the kind: the spec's fault back to `/bb:spec`, a
  stage-zero blocker to whoever owns the allowlist or the red that predates the build, a red
  task to the task.
- **Versions**: `plugin.json` `2.15.0` to `2.16.0`; `implement` `2.4.0` to `2.5.0`;
  `delegate` `2.5.0` to `2.6.0`.

## Behavior

1. `/bb:implement` and `/bb:delegate` ask nothing about how to build. Delegate flips
   `status: in-progress` and goes straight to the build; implement goes there after its
   reuse check.
2. The skill reads the spec, builds `args` (slug, spec path, the checks hint it resolves
   through the authority chain, reuse notes, and the unticked tasks with `n`, `title`,
   `delivers`, `behaviors`, `dep`, `verify`), confirms its three pre-invoke items, resolves
   and proves the script path in one `Bash` call, and invokes `Workflow` with `scriptPath`.
3. Stage zero runs one `parallel()`: one agent per reuse note, plus one that runs the
   project's checks once, from the hint `args` carries.
4. The tasks run in a sequential `for`, one agent each, in the order `dep:` implies, in the
   same working tree.
5. Each agent re-reads its checkbox on disk, builds the task, satisfies `verify:`, runs the
   checks (re-running a failed one up to 3 times, and only while no file changed between
   runs), commits the files it touched together with its `- [x]`, and returns its structured
   result plus the convention note it hands forward.
6. The script's return is the build report: implement reads it at its step 8, delegate takes
   it to ship. A non-null `stopped` stops both before landing.
7. A refused `scriptPath` becomes an inline `script` off the same file, in the same run.
8. With no `Workflow` tool, a `Bash` call that fails to read the script, or both call shapes
   refused, the skills build in context and name the reason in one line.
9. CI and the pre-commit hook guard the script: it parses, `export const meta` is a literal
   carrying `name` and `description`, its `phases` match the `phase()` calls by title, there
   is exactly one `parallel()` before the task loop, no spelling of the forbidden time and
   random calls is reachable, and oxfmt formats `js` alongside `json` and `md`.
10. A run that stops writes the blocker where the run can be found again: the PR description
    when the destination has a PR, the spec's `## Open` on the pushed branch when it does
    not. The report names which kind of blocker it was.

| WHEN                                         | THEN                                                             |
| -------------------------------------------- | ---------------------------------------------------------------- |
| every task already ticked                    | it does not invoke; reports nothing to build and goes on         |
| the spec has no `## Tasks`                   | implement's Prerequisites stop the run before this               |
| the spec has one task                        | workflow all the same; there is no threshold                     |
| the spec has no reuse note                   | stage zero runs the checks agent alone                           |
| a reuse note points at code that is gone     | stops before task 1; delegate flips `blocked`                    |
| a reuse note points at code that moved       | goes on; the new path enters the convention note                 |
| the authority chain resolves no check        | `checksHint` is empty; stage zero reports it and does not block  |
| a check command outside the allowlist        | fails in stage zero; stops with a permission blocker             |
| the tree is already red before task 1        | stops; the red predates the build and is reported as such        |
| a check red after 3 re-runs, files untouched | the task does not commit and does not revert; the loop stops     |
| a check red and a file did change            | not a flake; no re-run, the task fixes it or returns the blocker |
| a task agent returns `null`                  | a failed task; the loop stops and what is green stays committed  |
| the agent finds the spec underspecified      | it returns the blocker instead of improvising; the loop stops    |
| `verify:` is `reading`                       | self-inspection against the behaviors the task cites             |
| `verify:` is `CI`                            | comes back `pending`; `/bb:ship` is what covers it               |
| more tasks than the session's guideline      | says so in one line and invokes; the real cap is 1000 agents     |
| `scriptPath` refuses the plugin path         | reads the file and passes the content inline as `script`         |
| inline `script` is refused too               | builds in context naming the reason                              |
| the `Bash` call cannot read the script       | builds in context naming the reason                              |
| `Workflow` is off by config or by org        | builds in context naming the reason                              |
| a plugin `workflows/` dir does register      | `build-tasks` shows in autocomplete; the invocation is unchanged |
| delegate drives the build                    | nothing is asked, at either end of the chain                     |
| the build stops and the destination has a PR | the blocker goes into the PR description                         |
| the build stops with no PR anywhere          | the blocker goes into the spec's `## Open`                       |
| the run is interrupted halfway               | commits and checkboxes hold the progress; re-running resumes     |

## Tasks

- [x] **1. The fixed script, proven by a run**: `plugins/bb/workflows/build-tasks.js`,
      carrying stage zero in one `parallel()`, the sequential task `for` with its three
      exits, the task agent's prompt inline with its six steps, the retry constant and the
      flake definition, the result schemas, the accumulating convention note with its
      ceiling, and the script's return. Written against `build-tasks-workflow.md` and the
      `Workflow` tool's description, then smoke-run once: a throwaway one-task spec whose
      `verify:` is `reading`, invoked through `scriptPath` the way the skills invoke it, and
      the return carries that task as built
      → behaviors 3, 4, 5, 6 · dep: — · verify: command
- [x] **2. The reference documents the script**: `build-tasks-workflow.md` rewritten as
      documentation, with the compaction argument moved in from `build-mode.md`, the `args`
      shape, and the checklist split into CI, PR review and the skill's three per-run items
      → behaviors 2, 6, 9 · dep: 1 · verify: reading
- [x] **3. implement**: step 3 loses the question and gains the path resolution, the
      invocation and the three fallbacks; steps 4 to 6 shrink to the in-context path, keeping
      the checks authority chain the build step now needs for `checksHint`; the `## Tasfas`
      typo goes with them
      → behaviors 1, 2, 7, 8 · dep: 2 · verify: reading
- [x] **4. delegate**: step 3 deleted and the rest renumbered; the build step resolves,
      invokes and reads the return, with the same fallbacks; step 7 stops reporting "the
      build mode it ran in"; the edge row "workflow mode stops" loses the mode word; a
      stopped run writes the blocker into the PR description, or into the spec's `## Open`
      when there is no PR
      → behaviors 1, 2, 6, 7, 8, 10 · dep: 2 · verify: reading
- [x] **5. The guard around the script**:
      `.github/scripts/validate-workflow-script.ts` parsing the file with `Bun.Transpiler`
      and failing the forbidden calls, the meta interpolation and a second `parallel()`;
      added to `package.json`'s `validate` script (which is what lefthook runs) and to
      `validate.yml` as its own step; `js` added to the lefthook oxfmt glob
      → behavior 9 · dep: 1 · verify: CI
- [x] **6. Versions, docs, and the deletion**: `plugin.json` `2.16.0`, the two skill
      versions, the CHANGELOG entry naming which `build-via-workflow` decisions this
      reverses, `build-mode.md` deleted now that no reader is left, and `.claude/CLAUDE.md`
      (the tree, the new `workflows/` dir, the JS exception)
      → behaviors 1, 9 · dep: 1, 2, 3, 4, 5 · verify: CI

## Out of scope

- Parallelizing tasks against each other: `dep:` and the shared tree still prevent it
  (_revisit_).
- A named workflow in `.claude/workflows/` and a `/bb:build-tasks` command: still no, for
  the reason `build-via-workflow` gave and because the plugin registry is undocumented.
- A parser script that builds `args`: the skill keeps reading the spec (_revisit_).
- Stage zero in the in-context fallback: it stays the plain build it is today.
- Any change to `/bb:ship`, which still receives control after the workflow returns.
- Editing `.bb/build-via-workflow/spec.md`, which is `done` and describes what was built
  then. The reversal is the CHANGELOG's to record.

## Open

- Nothing.
