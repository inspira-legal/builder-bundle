# The person's profile: `~/.claude/bb.profile.json`

One question, asked once, that every bb skill reads. What the person does is a fact
about the person, so it is not asked per project and it is not stored per project.

`/bb:profile` is the only writer. The SessionStart hook is the only reader that runs
unasked; every other reader is a skill reading a flag it needs.

## Location

`~/.claude/bb.profile.json`, expanded from `Path.home()`. Outside the plugin on purpose:
the install path carries the version (`plugins/cache/inspira-legal/bb/<version>`), so
anything written inside it is lost on the next update. JSON because the hook is Python
and `json` is stdlib; a hook that must never fail cannot carry a dependency.

## Schema

```json
{
  "version": 1,
  "profile": {
    "reads_code": true,
    "uses_terminal": true,
    "step_by_step": false,
    "technical_vocabulary": true,
    "calibrated_at": "2026-08-19"
  }
}
```

| flag                   | true means                                              |
| ---------------------- | ------------------------------------------------------- |
| `reads_code`           | opens and edits the code, wants the reasoning behind it |
| `uses_terminal`        | runs commands and git without being walked through them |
| `step_by_step`         | wants the technical parts described one step at a time  |
| `technical_vocabulary` | reads `scaffold`, `branch` and `MCP` without a gloss    |

`calibrated_at` is an ISO date, written by `/bb:profile` and read by nobody. It is there
so a person can see how old the answers are.

## Reading it

Three rules, and they are what keep a hook from ever blocking a session:

- **Missing file: no profile.** Not an error, not a warning. The frame carries the
  invitation to run `/bb:profile`.
- **Unreadable or malformed: no profile.** A truncated file, bad JSON, a `profile` that
  is not an object, all read the same as missing. Never raise, never print to stderr.
- **A missing flag is `false`.** A file written by an older version stays valid, and the
  safe default is more explanation, not less.

## What the flags decide

Each flag answers one question, and a reader reads the one it needs rather than
inferring a whole person from a single id.

| flag                   | who reads it                                                    |
| ---------------------- | --------------------------------------------------------------- |
| `reads_code`           | the intake's depth, the medium's lean, how a decision is argued |
| `uses_terminal`        | scaffold or hosted, and whether the preflight walks through git |
| `step_by_step`         | whether a command prints as one line or as numbered steps       |
| `technical_vocabulary` | whether `scaffold`, `embed`, `MCP` and `branch` are replaced    |

`uses_terminal` is about knowing how, not about having it installed. What is installed
and authenticated is the preflight's question, detected and never asked.

`step_by_step` decides how a command is written, never what runs. `pnpm install && pnpm
dev` on one side; on the other the same commands as numbered steps, each with where to
run it, how long it takes, and what success prints.

## Deriving an old profile

Before the profile file existed, brisar kept a `profile.persona_id` inside a project's
`.brisar/session.yaml`. A person who answered it once should not have to answer again, so
the first bb run that finds one and has no profile derives the four flags from it:

| the old id       | `reads_code` | `uses_terminal` | `step_by_step` | `technical_vocabulary` |
| ---------------- | ------------ | --------------- | -------------- | ---------------------- |
| `builder-senior` | true         | true            | false          | true                   |
| `builder-junior` | true         | true            | true           | true                   |
| `executive`      | false        | false           | true           | false                  |

`content` was never a person, it was the Framer output path (`brand.workflow ==
framer-harpa`, a project fact). It derives nothing: the checklist gets asked.

Three rules bound the derivation:

- **Only when there is no profile.** A profile on disk is the person's own answer and always
  wins; an old id in a project is never read over it.
- **Derived once.** The derivation pre-fills the `/bb:profile` checklist, the person
  confirms or corrects, and `/bb:profile` writes the file, which is what makes it stop being
  derived. `/bb:profile` stays the only writer.
- **The old file is left alone.** `.brisar/` is read, never written and never deleted.
