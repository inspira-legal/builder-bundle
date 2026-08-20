---
name: profile
description: Calibrate once who is on the other side, and every bb session after this one is calibrated. Asks four questions (are you used to editing code, to the terminal, to technical instructions, to technical vocabulary) plus which design tools are part of your day (Figma, Paper, Pencil, or none), writes ~/.claude/bb.config.json and ~/.claude/BUILDER-BUNDLE.md, and shows or recalibrates a profile that already exists. Use when the user says "/bb:profile", "set my profile", "recalibrate", "bb is explaining too much", "bb is explaining too little", "stop using bb's custom instructions", or "stop offering me design tools I don't use", or when a bb skill runs with no profile set.
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.1.0
---

# Profile

**Scope: the person's profile, plus whether bb keeps its custom instructions.** How much
to spell out, which words to use, whether a command comes as one line or as numbered
steps, which design tools a journey offers first, and whether
`~/.claude/BUILDER-BUNDLE.md` exists at all. Not the project, not the machine, not the
ship destination.

The profile is a fact about the person, so it is asked once and stored once, at
`~/.claude/bb.config.json`. The answers reach a session through
`~/.claude/BUILDER-BUNDLE.md`, which `~/.claude/CLAUDE.md` imports, both written by
`hooks/sync_instructions.py`. The full contract, the schema, the reading rules and what
the writer touches live in the plugin-level `references/bb-config.md`; read it before
writing anything.

## Workflow

1. **Read `~/.claude/bb.config.json`.** Missing, unreadable or malformed all mean the
   same thing: no profile. Never report a malformed file as an error the person has to
   fix; offer to calibrate over it.

2. **With no profile: calibrate.** Go to step 4.

3. **With a profile: show it first, then offer.** Print the four answers as sentences,
   not as flags, plus the design answer (which tools, "none of them", or "not asked yet"
   when the config predates the question), when it was calibrated, and one line saying
   whether the custom instructions are in place. Then one `AskUserQuestion`: keep it,
   recalibrate, or only turn the instructions on or off. Keeping it ends the skill;
   there is nothing to write. Recalibrating asks everything again, the four and the
   design question both.

4. **Ask the four, as one question.** A single `AskUserQuestion` with `multiSelect: true`
   and these four options. Each one names a habit the person either has or does not, so
   checked always means the same thing: they are used to this, so say less about it.

   | option label                                     | description                                                                                                 |
   | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
   | I am used to reading and editing code            | You work in the code, not only in the result. Leave it blank if you only want the result.                   |
   | I am used to working in the terminal             | Commands and git are part of your day. Leave it blank if you have never opened one.                         |
   | I am used to technical instructions              | A command on one line is enough. Leave it blank and each one arrives with where it runs and what it prints. |
   | I am used to terms like `branch`, `MCP`, `embed` | They land without a translation. Leave it blank if you prefer plain words.                                  |

   Checked is `true`, unchecked is `false`, and all four point the same way. Nothing
   checked is a valid answer, and it is the most careful profile there is.

   **The labels above are the wording, not the string to print.** They are English because
   the repo is; what the person reads follows the language they are speaking. The rule is
   in the plugin-level `references/doc-style.md`.

5. **Ask which design tools are part of their day.** A second `AskUserQuestion` with
   `multiSelect: true`, its own question because it is a list and not a habit-flag, and
   because a person who never designs should be able to leave it all blank without that
   reading as a careless answer:

   | option label | description                                                                 |
   | ------------ | --------------------------------------------------------------------------- |
   | Figma        | You design in Figma. A design journey offers it first when it is connected. |
   | Paper        | You design in Paper. Same lean, for the Paper canvas.                       |
   | Pencil       | You design in Pencil (`.pen` files). Same lean.                             |

   Say in the intro line that leaving everything blank is an answer: design happens in
   code and in the conversation's own preview, and journeys will lean that way. Checked
   tools go into `design_tools` in the order the person's day actually uses them when
   they say so; otherwise keep the order above. This never installs or connects
   anything: what is connected is detected per session, and a tool named here but not
   connected is simply named as absent when a journey reaches it.

6. **Ask whether bb keeps its custom instructions.** One `AskUserQuestion`, two options,
   asked apart from the others because this one is about the plugin and not about the
   person:

   | option label                                        | description                                                                                                       |
   | --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
   | Open every session with the custom instructions     | How bb works and who you are, which is what survives a compaction.                                                |
   | Do not use the builder bundle's custom instructions | The hook stays silent, so nothing comes back after a compaction. Your four answers are still read by every skill. |

   The first is the default, and it is what an unanswered file already does. Say in the
   second option's own line what turning it off costs, rather than after the fact.

7. **Write the config, then run the writer.** Create `~/.claude` if it is missing and
   write `~/.claude/bb.config.json` in the shape `references/bb-config.md` states:
   `version` and `custom_instructions` at the top level, and the four flags
   (`reads_code`, `uses_terminal`, `technical_instructions`, `technical_vocabulary`)
   plus `design_tools` and `calibrated_at`, today's ISO date, inside `profile`.
   `design_tools` is always written on a calibration, `[]` included: an empty list is
   the person's answer, and only a config that predates the question may lack the key.
   The flags have to sit under `profile`, because that is where the writer reads them;
   flat, they read as no profile at all. Write the whole file; never merge into a shape
   you did not read. Then run the writer, from the plugin root two directories above
   this skill:

   ```bash
   python3 hooks/sync_instructions.py
   ```

   It reads the config you just wrote and settles both files: it renders
   `~/.claude/BUILDER-BUNDLE.md` and adds the marked `@BUILDER-BUNDLE.md` import to
   `~/.claude/CLAUDE.md`, or removes both when the answer was no. Do not write either file
   by hand: the script is the only writer, which is what keeps the text in step with the
   installed version.

8. **Print what was written**, as the four sentences plus the design answer and which
   of the two answers the instructions took, and name both paths so the person can open
   them. Say plainly that it
   is in effect **from here on**: what this session started with does not reload, so it is
   you carrying the answers for the rest of this session, and the file takes over in the
   next one. Offer nothing further; this skill has no next step.

## Edge cases

| WHEN                                       | THEN                                                                                    |
| ------------------------------------------ | --------------------------------------------------------------------------------------- |
| no file                                    | calibrate, write, print what was written                                                |
| a valid profile exists                     | show it, offer keep, recalibrate, or flip `custom_instructions`                         |
| `custom_instructions: false` on disk       | nothing is in `~/.claude` right now: say so, and offer to turn it back on               |
| `custom_instructions` absent               | reads `true`; write it explicitly on this calibration                                   |
| the writer script cannot be found or run   | say the config was written and the instructions were not; never write the files by hand |
| the file is malformed                      | treat as no profile, say the old file will be replaced, calibrate                       |
| `~/.claude/` cannot be written             | say where it failed and that the session runs uncalibrated; never retry elsewhere       |
| `CLAUDE.md` already carries the import     | the writer replaces the marked block in place; the rest of the file is never touched    |
| `CLAUDE.md` has a start marker with no end | the writer leaves that file alone; say the import was not added and why                 |
| the person checks nothing                  | valid; write all four `false`                                                           |
| nothing checked on the design question     | valid; write `design_tools: []` and say the lean will be code and the preview           |
| a config on disk lacks `design_tools`      | it predates the question; show "not asked yet" and offer the recalibration              |
| an old `profile.persona_id` in the project | derived into the four flags, pre-checked; the person confirms and the file is written   |
| called by another skill mid task           | calibrate, write, and hand back; the answers apply to the rest of this session too      |

The last row of the table is the one to get right: nothing reloads mid session, so after
writing the files **carry the four answers into how you speak for the rest of this
session**, rather than telling the person to restart.
