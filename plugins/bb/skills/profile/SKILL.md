---
name: profile
description: Calibrate once who is on the other side, and every bb session after this one is calibrated. Asks four questions (are you used to editing code, to the terminal, to technical instructions, to technical vocabulary), writes ~/.claude/bb.config.json, and shows or recalibrates a profile that already exists. Use when the user says "/bb:profile", "set my profile", "recalibrate", "bb is explaining too much", "bb is explaining too little" or "stop injecting bb's context every session", or when a bb skill runs with no profile set.
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.0.0
---

# Profile

**Scope: the person's profile, plus whether the hook injects at all.** How much to spell
out, which words to use, whether a command comes as one line or as numbered steps, and
whether a session opens with bb's operating frame. Not the project, not the machine, not
the ship destination.

The profile is a fact about the person, so it is asked once and stored once, at
`~/.claude/bb.config.json`. The SessionStart hook reads it into every session, unless
`inject_frame` says not to. The full
contract, the schema and the reading rules live in the plugin-level
`references/bb-config.md`; read it before writing the file.

## Workflow

1. **Read `~/.claude/bb.config.json`.** Missing, unreadable or malformed all mean the
   same thing: no profile. Never report a malformed file as an error the person has to
   fix; offer to calibrate over it.

2. **With no profile: calibrate.** Go to step 4.

3. **With a profile: show it first, then offer.** Print the four answers as sentences,
   not as flags, plus when it was calibrated and one line saying whether the frame
   injects. Then one `AskUserQuestion`: keep it, recalibrate the four, or only flip the
   injection. Keeping it ends the skill; there is nothing to write.

4. **Ask the four, as one question.** A single `AskUserQuestion` with `multiSelect: true`
   and these four options. Each one names a habit the person either has or does not, so
   checked always means the same thing: they are used to this, so say less about it.

   | option label                                     | description                                                                                                 |
   | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
   | I am used to opening and editing code            | You work in the code, not only in the result. Leave it blank if you only want the result.                   |
   | I am used to working in the terminal             | Commands and git are part of your day. Leave it blank if you have never opened one.                         |
   | I am used to technical instructions              | A command on one line is enough. Leave it blank and each one arrives with where it runs and what it prints. |
   | I am used to terms like `branch`, `MCP`, `embed` | They land without a translation. Leave it blank if you prefer plain words.                                  |

   Checked is `true`, unchecked is `false`, and all four point the same way. Nothing
   checked is a valid answer, and it is the most careful profile there is.

   **The labels above are the wording, not the string to print.** They are English because
   the repo is; what the person reads follows the language they are speaking. The rule is
   in the plugin-level `references/doc-style.md`.

   **Pre-fill from an old profile when there is one.** A project that brisar ran before the
   profile file existed carries `profile.persona_id` in its `.brisar/session.yaml`. Derive the
   four flags from it (the table in `references/bb-config.md`), pre-check them, and say in
   one line where they came from so the person corrects instead of re-answering.

5. **Ask whether the hook injects at all.** One `AskUserQuestion`, two options, asked
   apart from the four because this one is about the plugin and not about the person:

   | option label                      | description                                                             |
   | --------------------------------- | ----------------------------------------------------------------------- |
   | Open every session with the frame | How bb works and who you are, which is what survives a compaction.      |
   | Inject nothing                    | The hook stays silent. Your four answers are still read by every skill. |

   The first is the default, and it is what an unanswered file already does. Say in the
   second option's own line what turning it off costs, rather than after the fact.

6. **Write the file.** Create `~/.claude` if it is missing. `version: 1`, `inject_frame`,
   the four flags (`reads_code`, `uses_terminal`, `technical_instructions`,
   `technical_vocabulary`), and `calibrated_at` as today's ISO date. Write the whole file; never
   merge into a shape you did not read.

7. **Print what was written**, as the four sentences plus which of the two the hook will
   do, and say plainly that it is in effect **from here on**: the frame this session
   started with does not reload, so it is you carrying the answers for the rest of this
   session, and the hook takes over in the next one. Offer nothing further; this skill has
   no next step.

## Edge cases

| WHEN                                       | THEN                                                                                  |
| ------------------------------------------ | ------------------------------------------------------------------------------------- |
| no file                                    | calibrate, write, print what was written                                              |
| a valid profile exists                     | show it, offer keep, recalibrate, or flip the injection                               |
| `inject_frame: false` on disk              | nothing calibrated this session: say so, and offer to turn it back on                 |
| `inject_frame` absent                      | reads `true`; write it explicitly on this calibration                                 |
| the file is malformed                      | treat as no profile, say the old file will be replaced, calibrate                     |
| `~/.claude/` cannot be written             | say where it failed and that the session runs uncalibrated; never retry elsewhere     |
| the person checks nothing                  | valid; write all four `false`                                                         |
| an old `profile.persona_id` in the project | derived into the four flags, pre-checked; the person confirms and the file is written |
| called by another skill mid task           | calibrate, write, and hand back; the answers apply to the rest of this session too    |

The last row is the one to get right: the hook cannot re-run mid session, so after
writing the file **carry the four answers into how you speak for the rest of this
session**, rather than telling the person to restart.
