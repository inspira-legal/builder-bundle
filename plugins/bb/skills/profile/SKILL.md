---
name: profile
description: Calibrate once who is on the other side, and every bb session after this one is calibrated. Asks four questions (do you read the code, do you run commands, do you want the technical parts step by step, does technical vocabulary read fine), writes ~/.claude/bb.config.json, and shows or recalibrates a profile that already exists. Use when the user says "/bb:profile", "set my profile", "recalibrate", "bb is explaining too much" or "bb is explaining too little", or when a bb skill runs with no profile set.
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.0.0
---

# Profile

**Scope: the person's profile, and nothing else.** How much to spell out, which words to
use, and whether a command comes as one line or as numbered steps. Not the project, not
the machine, not the ship destination.

The profile is a fact about the person, so it is asked once and stored once, at
`~/.claude/bb.config.json`. The SessionStart hook reads it into every session. The full
contract, the schema and the reading rules live in the plugin-level
`references/bb-config.md`; read it before writing the file.

## Workflow

1. **Read `~/.claude/bb.config.json`.** Missing, unreadable or malformed all mean the
   same thing: no profile. Never report a malformed file as an error the person has to
   fix; offer to calibrate over it.

2. **With no profile: calibrate.** Go to step 4.

3. **With a profile: show it first, then offer.** Print the four answers as sentences,
   not as flags, plus when it was calibrated. Then one `AskUserQuestion`: keep it, or
   recalibrate. Keeping it ends the skill; there is nothing to write.

4. **Ask the four, as one question.** A single `AskUserQuestion` with `multiSelect: true`
   and these four options. Every option carries the hint of who it is for, so nobody has
   to know the term to answer:

   | option label                  | description                                                                                                   |
   | ----------------------------- | ------------------------------------------------------------------------------------------------------------- |
   | I open and edit the code      | You work in the code, not only in the result. Leave it blank if you only want the result.                     |
   | I run commands and git        | The terminal is part of your day. Leave it blank if you have never opened one.                                |
   | Spell out the technical parts | Every command with where to run it and what it prints when it works. Made for non technical people.           |
   | Technical terms read fine     | `scaffold`, `branch`, `MCP` and `embed` land without a translation. Leave it blank if you prefer plain words. |

   Checked is `true`, unchecked is `false`. Nothing checked is a valid answer, and it is
   the most careful profile there is.

   **Pre-fill from an old profile when there is one.** A project that brisar ran before the
   profile file existed carries `profile.persona_id` in its `.brisar/session.yaml`. Derive the
   four flags from it (the table in `references/bb-config.md`), pre-check them, and say in
   one line where they came from so the person corrects instead of re-answering.

5. **Write the file.** Create `~/.claude` if it is missing. `version: 1`, the four flags,
   and `calibrated_at` as today's ISO date. Write the whole file; never merge into a
   shape you did not read.

6. **Print what was written**, as the four sentences, and say plainly that it is in
   effect **from here on**: the frame this session started with does not reload, so it is
   you carrying the answers for the rest of this session, and the hook takes over in the
   next one. Offer nothing further; this skill has no next step.

## Edge cases

| WHEN                                       | THEN                                                                                  |
| ------------------------------------------ | ------------------------------------------------------------------------------------- |
| no file                                    | calibrate, write, print what was written                                              |
| a valid profile exists                     | show it, offer keep or recalibrate                                                    |
| the file is malformed                      | treat as no profile, say the old file will be replaced, calibrate                     |
| `~/.claude/` cannot be written             | say where it failed and that the session runs uncalibrated; never retry elsewhere     |
| the person checks nothing                  | valid; write all four `false`                                                         |
| an old `profile.persona_id` in the project | derived into the four flags, pre-checked; the person confirms and the file is written |
| called by another skill mid task           | calibrate, write, and hand back; the answers apply to the rest of this session too    |

The last row is the one to get right: the hook cannot re-run mid session, so after
writing the file **carry the four answers into how you speak for the rest of this
session**, rather than telling the person to restart.
