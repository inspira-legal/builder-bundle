# The config: `~/.claude/bb.config.json`

One question, asked once, that every bb skill reads. What the person does is a fact
about the person, so it is not asked per project and it is not stored per project. The
same file carries the one setting that is about the plugin instead of the person:
whether bb writes its custom instructions into `~/.claude` at all.

`/bb:profile` is the only writer of this file, and `hooks/sync_instructions.py` is the
only writer of the two files this one decides. Every other reader is a skill reading a
flag it needs.

## Location

`~/.claude/bb.config.json`, expanded from `Path.home()`. Outside the plugin on purpose:
the install path carries the version (`plugins/cache/inspira-legal/bb/<version>`), so
anything written inside it is lost on the next update. JSON because the hook is Python
and `json` is stdlib; a hook that must never fail cannot carry a dependency.

## Schema

```json
{
  "version": 1,
  "custom_instructions": true,
  "profile": {
    "reads_code": true,
    "uses_terminal": true,
    "technical_instructions": true,
    "technical_vocabulary": true,
    "calibrated_at": "2026-08-19"
  }
}
```

| flag                     | true means                                              |
| ------------------------ | ------------------------------------------------------- |
| `reads_code`             | reads and edits the code, wants the reasoning behind it |
| `uses_terminal`          | runs commands and git without being walked through them |
| `technical_instructions` | reads a command on one line and knows where to run it   |
| `technical_vocabulary`   | reads `scaffold`, `branch` and `MCP` without a gloss    |

`calibrated_at` is an ISO date, written by `/bb:profile` and read by nobody. It is there
so a person can see how old the answers are.

## `custom_instructions`

Whether bb keeps its custom instructions in `~/.claude`. `true`, the default, and
`BUILDER-BUNDLE.md` holds the operating frame plus the profile block while `CLAUDE.md`
imports it. `false` and both go away: the import block leaves `CLAUDE.md` and the file is
deleted. Frame and profile travel together, because the frame names the profile block as
the section that closes it, and half of it is worth less than either half whole.

It sits beside `profile` rather than inside it because it is not a fact about the person.
Turning it off costs what the frame is for, re-establishing the thread after a context
compaction; what it buys is a session where nothing from bb arrives unasked. The four
flags stay written either way, and every skill that runs still reads them.

## What gets written, and where

`hooks/sync_instructions.py` owns two files, and `/bb:profile` runs it right after
writing the config. The SessionStart hook runs it again, which is the whole reason that
hook still exists: the frame lives inside the versioned install path, so an update would
otherwise leave the previous version's text sitting in `~/.claude` for good.

| file                          | what is in it                                                                                                                |
| ----------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `~/.claude/BUILDER-BUNDLE.md` | the whole file is bb's: `hooks/operating-context.md` plus the profile block, under a header naming the version that wrote it |
| `~/.claude/CLAUDE.md`         | three lines fenced by `<!-- bb:start -->` and `<!-- bb:end -->`, holding the import `@BUILDER-BUNDLE.md`                     |

Four rules bound the writing, and together they are what makes it safe to run on every
session:

- **Only between the markers.** `CLAUDE.md` is a file the person writes by hand.
  Everything outside the two markers is theirs and is never rewritten, line endings
  included.
- **Nothing before consent.** With no config there is nothing to write, so neither file
  is created on install. Until the first `/bb:profile`, the hook carries the frame in the
  session itself and says once where it will live.
- **Written only when it changed.** The rendered text is compared to what is on disk, so
  a session that changes nothing writes nothing.
- **The opt out is a removal.** `custom_instructions: false` deletes
  `BUILDER-BUNDLE.md` and takes the block out of `CLAUDE.md`, rather than leaving behind
  a file nobody reads.

What this shape cannot do is clean up after itself: nothing runs at uninstall time, so
both files stay and keep shaping sessions until someone deletes them. That is why the
header of `BUILDER-BUNDLE.md` names what wrote it, which version, and how to make it
stop.

## Reading it

Three rules, and they are what keep a hook from ever blocking a session:

- **Missing file: no profile.** Not an error, not a warning. The frame carries the
  invitation to run `/bb:profile`.
- **Unreadable or malformed: no profile.** A truncated file, bad JSON, a `profile` that
  is not an object, all read the same as missing. Never raise, never print to stderr.
- **A missing flag is `false`.** A file written by an older version stays valid, and the
  safe default is more explanation, not less. All four flags point the same way, so this
  holds on every one of them: absent reads as the person not being used to it yet.
- **Only an explicit `false` opts out.** `custom_instructions` absent, or holding
  anything other than `false`, reads as `true`. A file nobody has answered yet keeps the
  instructions.

## What the flags decide

Each flag answers one question, and a reader reads the one it needs rather than
inferring a whole person from a single id.

| flag                     | who reads it                                                    |
| ------------------------ | --------------------------------------------------------------- |
| `reads_code`             | the intake's depth, the medium's lean, how a decision is argued |
| `uses_terminal`          | scaffold or hosted, and whether the preflight walks through git |
| `technical_instructions` | whether a command prints as one line or as numbered steps       |
| `technical_vocabulary`   | whether `scaffold`, `embed`, `MCP` and `branch` are replaced    |

`uses_terminal` is about knowing how, not about having it installed. What is installed
and authenticated is the preflight's question, detected and never asked.

`technical_instructions` decides how a command is written, never what runs. True and it
is `pnpm install && pnpm dev` on one line; false and the same commands come as numbered
steps, each with where to run it, how long it takes, and what success prints.

## Deriving an old profile

Before the profile file existed, brisar kept a `profile.persona_id` inside a project's
`.brisar/session.yaml`. A person who answered it once should not have to answer again, so
the first bb run that finds one and has no profile derives the four flags from it:

| the old id       | `reads_code` | `uses_terminal` | `technical_instructions` | `technical_vocabulary` |
| ---------------- | ------------ | --------------- | ------------------------ | ---------------------- |
| `builder-senior` | true         | true            | true                     | true                   |
| `builder-junior` | true         | true            | false                    | true                   |
| `executive`      | false        | false           | false                    | false                  |

`content` was never a person, it was the Framer output path (`brand.workflow ==
framer-harpa`, a project fact). It derives nothing: the checklist gets asked.

Three rules bound the derivation:

- **Only when there is no profile.** A profile on disk is the person's own answer and always
  wins; an old id in a project is never read over it.
- **Derived once.** The derivation pre-fills the `/bb:profile` checklist, the person
  confirms or corrects, and `/bb:profile` writes the file, which is what makes it stop being
  derived. `/bb:profile` stays the only writer.
- **The old file is left alone.** `.brisar/` is read, never written and never deleted.
