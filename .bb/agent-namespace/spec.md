---
status: in-progress
created: 2026-09-04
slug: agent-namespace
---

# The agent name carries the plugin's namespace

The platform publishes a plugin's agents under the plugin's own name, so
`plugins/bb/agents/bb-reuse-check.md` answers to `bb:bb-reuse-check` and to nothing else.
`plugins/bb/workflows/build-tasks.js:319` asks for `bb-reuse-check`, and a name the platform
does not know is not a soft miss: `agent()` throws. Stage zero's reuse thunk dies, `ground[0]`
comes back empty, and the build stops before task 1 with `built: []`. Every spec carrying at
least one reuse note, which is the ordinary spec, is unbuildable from an installed bb.

Two more defects sit on top of that one. The script's comment and the reference both promise
that an `agentType` which fails to resolve degrades into a generic agent working from the
prompt and the schema. No such mechanism exists, and that promise is what let a naming slip
read as cosmetic. And the blocker the script reports, `the reuse agent returned nothing`,
describes a different failure: it says the agent ran and came back empty, when the agent was
never dispatched. `/bb:implement`'s step 10 buckets that phrasing with the stops whose remedy
is to run the task again, so the person who hits this re-runs a deterministic failure until
they give up, and marks a correct spec `blocked` on the way.

The same bare spelling appears in four places of prose, telling the model to dispatch
`bb-review-finder`, `bb-review-verifier` and `bb-spec-reviewer`. Those do not resolve either.
There the miss is survivable, since the Agent tool returns the error together with the list of
real names and the model can send it again, so what it costs is a wasted round trip per
dispatch, and a fan-out of ten finders sent in one message wastes ten.

## Why the fallback is not the fix

Making the documented degradation real means dispatching with no `agentType` when the name
fails. That trades away the thing `agentType` buys. The system prompt it selects comes from
`plugins/bb/agents/bb-reuse-check.md`, whose `tools: Read, Grep, Glob` is a capability the
harness enforces: the agent cannot write. A generic agent arrives with `Write` and `Edit`, and
the only thing left holding stage zero read-only is the sentence `do not edit anything` inside
`reusePrompt()`.

The repo already treats that as an invariant rather than a preference.
`.github/scripts/validate-frontmatter.ts` fails the commit when a bb agent lists a write tool,
and `.claude/CLAUDE.md` states the rule: enforce irreversible hazards with capability scoping,
not prose. A runtime fallback that routes around a guarantee CI protects is the wrong shape of
insurance. The insurance goes into CI instead, where a name that does not match a shipped agent
fails the commit and costs nothing at runtime.

## What the field run already proved

The incident this spec fixes is also the evidence for how `parallel()` treats a thunk that
throws. The reuse thunk threw, and the workflow still returned its report, with
`stopped.blocker` set and the checks agent's own result intact in the last slot, while the
platform's `<failures>` named `parallel[0] failed`. So a throwing thunk does not take the
workflow down: its slot is preserved holding nothing, the sibling thunk completes, and the
script runs on to build the stop. That is what lets the fix below record the cause and re-throw
rather than swallow, keeping the platform's own failure record alongside the blocker.

The other half is already proven too: the platform's own error, when it refuses a name, prints
the agents it does know, and `bb:bb-reuse-check` is among them. So the spelling this spec moves
to is the spelling the harness resolves, and what remains to be checked per run is that the
string in the script still names a shipped agent, which is the guard's job.

## Decisions

- The workflow names the agent `bb:bb-reuse-check` and offers no second spelling.
  `plugins/bb/workflows/build-tasks.js:319` is the only `agentType` in the plugin.
- The degradation promise is deleted, not implemented, in both places that make it: the comment
  at `plugins/bb/workflows/build-tasks.js:86-89`, and
  `plugins/bb/references/build-tasks-workflow.md:202-206`, whose last sentence, "That is the
  same fallback the review fan-out sets for `bb-review-finder`", goes with it. That clause is
  false on its own terms too: no fan-out in `/bb:review` sets any fallback.
- Both stage-zero thunks record the platform's error message, log it and re-throw it, on the
  evidence above.
- The blocker names the agent and then the platform's message, so the reuse one reads
  `the reuse agent could not run: <message>` and the checks one reads the same with its own
  name in front. With no recorded message the two branches keep the wording they have,
  `returned nothing`, which is then true.
- The existing chain stays a chain, so when both stage-zero agents fail the reuse blocker is
  the one reported. The checks cause is not lost: `log()` carries it into the run's own output,
  next to the platform's `<failures>`.
- `plugins/bb/references/build-tasks-workflow.md:238-240`, which enumerates the stage-zero
  stops the caller can be handed, gains this new kind, so the contract doc and the script keep
  saying the same thing.
- The four prose dispatches are respelled with the namespace:
  `plugins/bb/skills/review/references/fronts.md:114`,
  `plugins/bb/skills/review/SKILL.md:127`,
  `plugins/bb/skills/review/references/verify.md:56` and
  `plugins/bb/skills/spec/SKILL.md:74`.
- A new `.github/scripts/validate-agent-names.ts` is the guard, built on the tree walk and the
  CLI shape `.github/scripts/lib/validate-common.ts` already exports. It is its own script
  because one existing validator reads frontmatter only and the other reads `workflows/*.js`
  only, while this rule spans both and the skills' prose besides.
- The guard anchors on the keys `agentType:` and `subagent_type:`, taking the value quoted,
  bare or inside backticks. An agent name mentioned anywhere else, a file path or a role named
  in a sentence, is not a dispatch and is not read.
- It rejects exactly two shapes: a bb agent's name written without the plugin prefix, and a
  `bb:` prefixed name with no such agent. Any other name passes in silence, so a skill that
  later dispatches a platform agent is not a false failure and no hand-kept list of platform
  agents has to stay current.
- Scope is enforced by the `keep()` predicate the guard hands `resolveTargets`, which takes
  only `.js` and `.md` under `plugins/bb/`. `resolveTargets` defaults its walk to the working
  directory, so without that predicate a bare run from the repo root would read `.bb/` and
  `CHANGELOG.md`, the two places whose whole job is to quote a broken spelling while describing
  it.
- The valid set is derived, never written down: each agent's frontmatter `name:` under
  `plugins/bb/agents/`, prefixed with the `name` field of
  `plugins/bb/.claude-plugin/plugin.json`. The frontmatter is what the platform resolves, so it
  is what the guard reads, and an agent file whose basename disagrees with its own `name:` is
  itself an error, which keeps the two from drifting apart unseen.
- A derived set that comes out empty is an error and not a clean run, since an empty set turns
  every correct name into an unknown one and reports the opposite of the truth.
- It is wired into `package.json`'s `validate` script, which lefthook runs pre-commit, and into
  `.github/workflows/validate.yml` as its own step, matching the two validators already there.
- `lefthook.yml`'s oxfmt job takes `ts` into its glob, which is `*.{json,md,js}` today. CI's
  `fmt:check` runs `oxfmt --check .` over everything, so a `.ts` the pre-commit hook never
  formats is a red run on a finished PR.
  `plugins/bb/references/build-tasks-workflow.md:353-372`, which lists what CI guards, gains
  the third validator and the corrected oxfmt line.
- The release is `3.6.1`, with a `CHANGELOG.md` entry, since a run reads the installed copy and
  the fix reaches nobody until a version ships.

## Behavior

**Happy path.** `/bb:implement <slug>` on a spec with reuse notes dispatches the workflow.
Stage zero sends the reuse agent as `bb:bb-reuse-check`; the harness resolves it and delivers
`plugins/bb/agents/bb-reuse-check.md` as the system prompt, with its `tools:` narrowing the
agent to reading. The agent returns one verdict per note, the checks agent returns the green
baseline, and the build proceeds to task 1.

| #   | WHEN                                                       | THEN                                                               |
| --- | ---------------------------------------------------------- | ------------------------------------------------------------------ |
| 1   | the reuse agent's name does not resolve                    | the blocker reads `the reuse agent could not run: <message>`       |
| 2   | the reuse agent is dispatched and returns nothing          | the blocker stays `the reuse agent returned nothing`               |
| 3   | the checks agent cannot be dispatched                      | the blocker reads `the checks agent could not run: <message>`      |
| 4   | both stage-zero agents fail                                | the reuse blocker is reported, the checks cause goes to `log()`    |
| 5   | a stage-zero thunk throws                                  | its slot is preserved empty and the script still returns `stopped` |
| 6   | the spec carries no reuse note                             | no reuse thunk is sent and nothing on this path changes            |
| 7   | a review or spec skill dispatches one of the bb agents     | it writes the namespaced name and the dispatch resolves first try  |
| 8   | a `.js` under `plugins/bb/` writes a bare bb `agentType:`  | the guard errors, naming file, line and the namespaced spelling    |
| 9   | a `.md` under `plugins/bb/` gives a bare `subagent_type:`  | the same error, for the value quoted, bare or backticked           |
| 10  | either key names `bb:` plus no such agent                  | the guard errors, calling the agent unknown                        |
| 11  | either key names an agent that is not this plugin's        | the guard passes it in silence                                     |
| 12  | a bb agent's name appears with neither key                 | the guard does not read it                                         |
| 13  | a path outside `plugins/bb/` holds a bare name             | the guard never opens it, `.bb/` and `CHANGELOG.md` included       |
| 14  | an agent's basename disagrees with its frontmatter `name:` | the guard errors on that file                                      |
| 15  | the derived set of valid names comes out empty             | the guard exits non-zero saying so, rather than reporting clean    |
| 16  | the guard runs over the tree as it stands today            | it names the five bare dispatches, one per site                    |
| 17  | the guard runs once every task has landed                  | zero errors, and `bun run validate` is green                       |
| 18  | the new `.ts` is committed                                 | lefthook formats it and CI's `fmt:check` stays green               |
| 19  | an installed bb runs its daily self-update                 | `3.6.1` is what carries the fix into the copy a run reads          |

## Tasks

### The guard first, while the offenses are still there

- [x] **1. `validate-agent-names.ts`**: the script, on `validate-common.ts`, deriving the valid
      set from each agent's frontmatter `name:` and from `plugin.json`, anchored on the two
      keys, scoped by its `keep()` predicate to `.js` and `.md` under `plugins/bb/`
      → behaviors 8, 9, 10, 11, 12, 13, 14, 15, 16 · dep: — · verify: command, run over the
      current tree; it names five errors, one per site, and nothing outside `plugins/bb/`

### Fix the dispatch

- [x] **2. The name carries the namespace**: `agentType: "bb:bb-reuse-check"` in
      `plugins/bb/workflows/build-tasks.js`, and the degradation promise deleted from its
      comment and from `plugins/bb/references/build-tasks-workflow.md`, orphan clause included
      → behaviors happy path, 6 · dep: 1 · verify: command, the task 1 guard stops reporting
      `workflows/build-tasks.js`; the four prose sites still fail until task 4

- [x] **3. The cause reaches the blocker**: a `.catch()` on both stage-zero thunks records the
      platform's message, logs it and re-throws; the two `stopped` branches read it; the
      reference's stage-zero stop list gains the new kind
      → behaviors 1, 2, 3, 4, 5 · dep: 2 · verify: reading

### Fix the prose

- [x] **4. The four dispatch names in the skills**: the namespaced spelling in `fronts.md`,
      `review/SKILL.md`, `verify.md` and `spec/SKILL.md`
      → behaviors 7 · dep: 1 · verify: command, the task 1 guard stops reporting the four
      prose sites, leaving it clean

### Wire it up and ship

- [ ] **5. Wired into the three places that run it**: `package.json`'s `validate` script, a step
      in `.github/workflows/validate.yml`, and `ts` in `lefthook.yml`'s oxfmt glob; the
      reference's CI list gains the validator and the corrected oxfmt line
      → behaviors 17, 18 · dep: 2, 3, 4 · verify: `bun run validate` and `bun run fmt:check`

- [ ] **6. `3.6.1` and its entry**: the `version` in `plugins/bb/.claude-plugin/plugin.json`
      and a `CHANGELOG.md` section in the prose the file already uses
      → behaviors 19 · dep: 5 · verify: reading

## Out of scope

- Reclassifying the stop in `/bb:implement`'s step 10. The blocker now names its own cause,
  which is what the reader was missing, and the new wording no longer matches the phrase step
  10 lists for the stops whose remedy is another run. What stays is that the step still tells a
  stop of any kind to flip the spec to `blocked`, so a plugin install defect can still mark a
  correct spec. Whether a dispatch failure deserves a bucket of its own is a call about that
  skill's routing. _revisit_
- Making the degradation into a generic agent real, for the reason the section above gives.
- Resolving the agent name in `/bb:implement` and passing it through `args`. It survives any
  future namespace change and costs a value written per run, which is what the reference
  restricts because it invalidates the `resumeFromRunId` cache.
- The `sed` workaround on the normalized copy, and any change to
  `plugins/bb/scripts/normalize_workflow.py`. The copy is a byte transform and the name is not
  its business.
- Auditing how other plugins on this machine name their agents.

## Open

Nothing.
