---
status: in-progress
created: 2026-08-19
slug: no-opt-out
---

# two steps stop being optional: the build always runs as a workflow, the spec is always reviewed

`build-via-workflow` shipped the one-agent-per-task build as a **choice**, asked at the
start of every `/bb:implement` and `/bb:delegate` run, and shipped the script as prose the
skill re-authors per run. `spec` shipped its independent reviewer as a step whose mandate
the skill re-composes from prose every time, right at the point where the run wants to
reach its gate.

Both are the same shape: the pass that catches what the main context loses is assembled by
the context that is about to skip it. This change executes both instead of offering them.
The mode question goes, the workflow becomes the only build path, the in-context build
survives as the fallback for a session with no `Workflow` tool, and the reviewer becomes a
dispatched agent whose mandate lives in a system prompt the harness delivers.

Success: `/bb:implement` and `/bb:delegate` reach the build with nothing asked, and no spec
reaches its exit gate without a verdict from something that did not write it.

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
to build elsewhere. That is the `bb-spec-reviewer`'s question, and it is why both halves are
one spec: making every build fresh is what makes the review necessary.

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
- **`build-mode.md` is deleted by task 8**, the last task, once no reader is left: the two
  skills go first, the `.claude/CLAUDE.md` tree goes with the deletion. The compaction
  argument (a spec of eight tasks built in one context drifts from its own `## Decisions`)
  moves into `build-tasks-workflow.md`; the self-sufficiency argument moves into the
  reviewer's mandate.
- **`build-tasks-workflow.md` stops being a contract to meet and starts documenting the
  script**: `args`, the return schemas, the convention note with its ceiling, and the
  pre-invoke checklist split three ways.
- **The checklist splits into CI, PR review and the skill.** CI takes what a parse or a
  regex settles: the file parses, `export const meta` is present and free of
  interpolation, exactly one `parallel()`, and no `Date.now()`, `new Date()` or
  `Math.random()`. A one-time PR review takes what only reading the code settles (`schema`
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
- **The reviewer becomes an agent**: `agents/bb-spec-reviewer.md`, `tools: ["Read",
  "Grep", "Glob"]`, no Bash, no `model:` so it inherits the session's. Completeness
  judgment is the same order of work as writing the spec was, so it runs at the same tier.
- **Its mandate covers the repo, not only the text**: omission, contradiction and surplus,
  plus "do the reuse notes point at code that exists" and "is this spec buildable by an
  agent that has only this file". A dead reuse note found here costs a read; found in
  stage zero it costs a run.
- **The reviewer weighs its own findings, the skill decides the round.** Each finding comes
  back with `weight: load-bearing | minor` and a one-line reason. The reviewer proposes
  because it read the spec; the skill decides because only it knows what the fold changed.
- **One trigger for round two, and two rounds is the ceiling.** Round one is mandatory.
  Round two runs when round one returned at least one `load-bearing` finding, whatever
  section the fold touched. Anything still `load-bearing` after round two is written into
  `## Open`, and the exit gate treats it exactly like an open decision: no clean build
  option, only resolve now or defer explicitly.
- **The gate always states the review's status**: the verdict in one line, or that it did
  not run and why. It never shows a verdict that did not happen.
- **Versions**: `plugin.json` `2.13.0` to `2.14.0`; `implement` `2.4.0` to `2.5.0`;
  `delegate` `2.5.0` to `2.6.0`; `spec` `2.3.0` to `2.4.0`.

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
9. Every spec dispatches `bb-spec-reviewer` before its exit gate. It receives the spec's
   path and nothing about the conversation that produced it; its mandate is its own system
   prompt.
10. The reviewer returns findings, each weighed `load-bearing` or `minor`; the skill folds
    them into the gray-area loop, and one `load-bearing` finding is what makes round two run.
11. The exit gate states the review's status in one line, and a `load-bearing` finding that
    survived round two sits in `## Open`, which the gate blocks on like an open decision.
12. CI and the pre-commit hook guard the script: it parses, `export const meta` is a literal,
    there is exactly one `parallel()`, the forbidden time and random calls are absent, and
    oxfmt formats `js` alongside `json` and `md`.

| WHEN                                         | THEN                                                            |
| -------------------------------------------- | --------------------------------------------------------------- |
| every task already ticked                    | it does not invoke; reports nothing to build and goes on         |
| the spec has no `## Tasks`                   | implement's Prerequisites stop the run before this               |
| the spec has one task                        | workflow all the same; there is no threshold                     |
| the spec has no reuse note                   | stage zero runs the checks agent alone                           |
| a reuse note points at code that is gone     | stops before task 1; delegate flips `blocked`                    |
| a reuse note points at code that moved       | goes on; the new path enters the convention note                 |
| the authority chain resolves no check        | `checksHint` is empty; stage zero reports it and does not block   |
| a check command outside the allowlist        | fails in stage zero; stops with a permission blocker             |
| the tree is already red before task 1        | stops; the red predates the build and is reported as such        |
| a check red after 3 re-runs, files untouched | the task does not commit and does not revert; the loop stops     |
| a check red and a file did change            | not a flake; no re-run, the task fixes it or returns the blocker  |
| a task agent returns `null`                  | a failed task; the loop stops and what is green stays committed  |
| the agent finds the spec underspecified      | it returns the blocker instead of improvising; the loop stops    |
| `verify:` is `reading`                       | self-inspection against the behaviors the task cites             |
| `verify:` is `CI`                            | comes back `pending`; `/bb:ship` is what covers it               |
| more tasks than the session's guideline      | says so in one line and invokes; the real cap is 1000 agents     |
| `scriptPath` refuses the plugin path         | reads the file and passes the content inline as `script`         |
| inline `script` is refused too               | builds in context naming the reason                              |
| the `Bash` call cannot read the script       | builds in context naming the reason                              |
| `Workflow` is off by config or by org        | builds in context naming the reason                              |
| a plugin `workflows/` dir does register      | `build-tasks` shows in autocomplete; the invocation is unchanged  |
| delegate drives the build                    | nothing is asked, at either end of the chain                     |
| the run is interrupted halfway               | commits and checkboxes hold the progress; re-running resumes     |
| one finding comes back `load-bearing`        | folded into the loop, and round two runs                         |
| every finding comes back `minor`             | folded, no round two                                             |
| the reviewer finds a dead reuse note         | `load-bearing` by definition: back to the loop before the gate    |
| round two still returns load-bearing         | into `## Open`; the gate offers resolve or defer, not build       |
| no Agent tool in the session                 | the gate says the review did not run and why                     |

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
      → behaviors 2, 6, 12 · dep: 1 · verify: reading
- [x] **3. implement**: step 3 loses the question and gains the path resolution, the
      invocation and the three fallbacks; steps 4 to 6 shrink to the in-context path, keeping
      the checks authority chain the build step now needs for `checksHint`; the `## Tasfas`
      typo goes with them
      → behaviors 1, 2, 7, 8 · dep: 2 · verify: reading
- [x] **4. delegate**: step 3 deleted and the rest renumbered; the build step resolves,
      invokes and reads the return, with the same fallbacks; step 7 stops reporting "the
      build mode it ran in"; the edge row "workflow mode stops" loses the mode word
      → behaviors 1, 2, 6, 7, 8 · dep: 2 · verify: reading
- [x] **5. The reviewer agent**: `agents/bb-spec-reviewer.md` with `description` and
      `tools` and no `model`, carrying the omission, contradiction and surplus mandate, the
      reuse-note check, the buildable-by-a-fresh-agent question, and the weighed return
      → behaviors 9, 10 · dep: — · verify: reading
- [ ] **6. spec**: step 6 dispatches the agent unconditionally in place of the
      "Medium-and-up" qualifier, with the one-load-bearing-finding trigger for round two and
      the two-round ceiling; step 7's gate states the review's status every time and blocks
      on a surviving `load-bearing` finding in `## Open` the way it blocks on a decision
      → behaviors 9, 10, 11 · dep: 5 · verify: reading
- [ ] **7. The guard around the script**:
      `.github/scripts/validate-workflow-script.ts` parsing the file with `Bun.Transpiler`
      and failing the forbidden calls, the meta interpolation and a second `parallel()`;
      added to `package.json`'s `validate` script (which is what lefthook runs) and to
      `validate.yml` as its own step; `js` added to the lefthook oxfmt glob
      → behavior 12 · dep: 1 · verify: CI
- [ ] **8. Versions, docs, and the deletion**: `plugin.json` `2.14.0`, the three skill
      versions, the CHANGELOG entry naming which `build-via-workflow` decisions this
      reverses, `README.md`'s agent count going from two to three, `build-mode.md` deleted
      now that no reader is left, and `.claude/CLAUDE.md` (the tree, the new agent, the new
      `workflows/` dir, the JS exception)
      → behaviors 1, 9, 12 · dep: 1, 2, 3, 4, 5, 6, 7 · verify: CI

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
