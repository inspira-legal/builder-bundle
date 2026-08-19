---
status: in-progress
created: 2026-08-19
slug: bb-config
---

# one profile, asked once, injected every session

`/bb:brisar` opens by asking who is building, and turns the answer into one of four
personas. The question is good and the place is wrong twice over. It is a fact about
the person, not about the project, so it gets asked again on the next project; and a
persona packs four independent things into one id, so every reader downstream asks
`persona == junior?` when what it wants to know is whether to spell out a command.

This replaces the persona with a checklist of what the person actually does, asks it
once through `/bb:config`, and writes `~/.claude/bb.config.json`. The SessionStart hook
reads that file and carries the answers into the operating frame of every session, so a
skill that never heard of brisar still knows whether to spell out `pnpm install` or
just print it. When the file is missing, the frame says so and names the skill that
fixes it.

Pulling the profile out empties `.brisar/` of the one thing in it that was never about
the project, which is the moment to finish the job: the session state moves into
`.bb/<slug>/`, where every other durable artifact of a slug already lives, and
`.brisar/` stops existing.

## What a persona was hiding

`phase-0-calibration.md` asks one question and derives three different things from it:

| axis                                      | stable across projects? | where it belongs               |
| ----------------------------------------- | ----------------------- | ------------------------------ |
| vocabulary, spelling out, question depth  | yes                     | `~/.claude/bb.config.json`     |
| git, `gh` auth, the unframer MCP          | no, it is machine state | `preflight-tooling.md` detects |
| output path (`embed`, `prototype-hosted`) | no, it is per project   | brisar decides per run         |

Only the first axis becomes the profile. Tooling is detected, not asked, and detection
already lives in the preflight. The output path is a project decision the same person
answers differently on two consecutive projects, so freezing it in a user-level file
would replace one question with a wrong default. `content` was never a trait of the
person: it is the Framer path wearing a persona's clothes, and it leaves with them.

## The checklist

Four independent answers, one multi-select question, the same single question Phase 0
asks today:

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

| key                    | what `/bb:config` asks                                     | the hint beside it       |
| ---------------------- | ---------------------------------------------------------- | ------------------------ |
| `reads_code`           | Você abre e edita o código, ou quer só o resultado?        | quem só quer o resultado |
| `uses_terminal`        | Você roda comandos e git no dia a dia?                     | quem nunca abriu um      |
| `step_by_step`         | Quer que as partes técnicas sejam descritas passo a passo? | ideal para não técnicas  |
| `technical_vocabulary` | Termos como `scaffold` e `branch` passam sem tradução?     | quem prefere em português |

Every option carries that hint beside it. The question names a habit and the hint names
who has it, so the person recognizes themselves without having to decode the term the
answer is about. `scaffold` in the fourth question is the point: someone who does not
know the word answers no on the strength of not knowing it.

`step_by_step` decides what a command looks like when it is printed, not what runs:
`pnpm install && pnpm dev` on one side, and on the other the numbered steps with where
to run them, how long they take and what success prints. `uses_terminal` is knowing
how, not having it installed, which is the preflight's question.

The two pairs are independent on purpose. `builder-senior` and `builder-junior` were the
same first pair with a different second one, which is the whole reason the id kept being
read for questions it could not answer.

## Which reader wants which answer

The fifteen `persona_id` reads become reads of one flag each:

| reader                   | asks today             | asks after                               |
| ------------------------ | ---------------------- | ---------------------------------------- |
| `phase-1-intake.md`      | branch by persona      | `reads_code` sets depth and language     |
| `phase-3-scaffold.md`    | `persona == executive` | `uses_terminal` picks scaffold or hosted |
| `phase-5-handoff.md`     | `persona == junior`    | `step_by_step`                           |
| `brief.md`, banned words | executive or content   | `technical_vocabulary`                   |
| `phase-medium.md`        | `persona == executive` | `reads_code` leans the medium            |
| `phase-diverge.md`       | who is choosing        | `technical_vocabulary`                   |
| `phase-research.md`      | who is reading         | `technical_vocabulary`                   |
| `preflight-tooling.md`   | senior without git     | `uses_terminal` without git              |

The Framer fork in `SKILL.md` and `product-registry.yaml` stops reading the profile
altogether: it is `brand.workflow == framer-harpa`, a project fact brisar already has.

## Where brisar keeps its state

`.brisar/` holds two files today, `session.yaml` (the journey's state machine) and
`config.yaml` (`ds_path`, `design_path`, `surfaces`). The state machine is a second copy
of a document brisar already writes: `.bb/<slug>/brief-design.md`, the living contract
the Brief phase opens and every later round updates, read by Diverge, Develop, Deliver
and the dev who implements. Its sections are the YAML in prose.

| the YAML field       | the brief's section                    |
| -------------------- | -------------------------------------- |
| `open_tension`       | the tension the research did not solve |
| `diverge.directions` | the directions                         |
| `research.ran`       | findings by front                      |
| `round`              | one block per exploration round        |
| the phase's calls    | the decision log, a dated table        |

Two sources for one truth, kept in sync by hand, and the one a person reads is not the
one the phases read. The YAML goes; the brief closes the gap with a frontmatter block
and the two sections that carry what was left out:

```yaml
---
status: in-progress | completed
phase: research | brief | diverge | medium | develop | deliver | done
round: 3
slug: <slug>
created: <ISO>
---
```

`## Left out` takes what `skipped`, `degraded` and `discard_reason` held: a front not
run and why, a front run degraded and which conclusions weaken, a direction discarded
and what killed it. This is brisar's declared-never-silent rule, and prose carries a
reason better than a YAML string. `## Open` takes `open_tension`, which the brief
already writes as a section.

What is left is not prose: `ds_path`, `design_path` and `surfaces[]`. `ds_path` already
resolves through `BRISAR_DS_PATH`, then the project, then the bundled DS, so persisting
it only adds a fourth place to look. `design_path` is `.bb/<slug>/design.md`, derivable
from the slug. `surfaces[]` is what Develop built, and it goes in that document's own
frontmatter, beside the thing it describes.

`.brisar/` stays **readable** wherever it exists, the way `.bb/tasks/<slug>/` still
resolves today: a session that finds one reads it once to know where it stopped, and
writes into the brief from then on.

Nothing is written before the slug is confirmed. Today a partial intake writes
`.brisar/session.yaml` in the cwd and Phase 3 copies it into the scaffolded folder;
after this the intake holds its answers until Phase 1 confirms the slug, and the first
write is the brief itself.

## Decisions

- **The file is `~/.claude/bb.config.json`**, outside the plugin. The install path
  carries the version (`plugins/cache/inspira-legal/bb/2.13.0`), so anything written
  inside it dies on the next plugin update. JSON because the hook is Python and `json`
  is stdlib; YAML would add a dependency to a hook that must never fail.
- **The hook always injects.** With a profile it injects the behavior the four answers
  imply; without one it injects a short line naming `/bb:config`, which the model acts
  on when a bb skill runs and otherwise leaves alone.
- **What the hook injects is behavior, not the flags.** `reads_code: false` means
  nothing on its own; the frame carries the sentences it implies.
- **The config holds the profile and nothing else**, because everything in it is
  injected in every session. `ds_path` stays out: it is a machine path, read by one
  phase, and it keeps the resolution order it has today (`BRISAR_DS_PATH`, then the
  project file, then the bundled DS).
- **`/bb:config` is the only writer**, and it does three things: calibrate on first
  run, show the current profile, recalibrate on demand. `phase-0-calibration.md`
  promises recalibration today and gives no verb for it.
- **Every option carries a hint of who it is for**, so the answer never depends on
  knowing the term the question uses.
- **The four personas are deleted, not mapped.** No translation table survives, because
  a table would keep the id alive as the real vocabulary and the flags as decoration.
- **Phase 0 goes away.** brisar with no config calls the same calibration `/bb:config`
  owns, then continues; it never carries its own copy of the question.
- **There is no state file.** `.brisar/session.yaml` and `.brisar/config.yaml` are
  deleted, and `.bb/<slug>/brief-design.md` carries the journey: the phase in its
  frontmatter, the rounds and directions in its body, what was left out in a section of
  its own. One document, read by the person and by the phases.
- **A restart appends a round, it does not archive.** The brief is a living contract and
  already grows a block per exploration round, so a second run is round `N+1` with the
  first one still readable above it.
- **`surfaces[]` moves into `design.md`'s frontmatter**, beside the document that
  describes what was built, instead of into a file that describes nothing else.
- **An unreadable or malformed config reads as missing.** The hook never blocks a
  session, the rule `inject_operating_context.py` already follows for its own missing
  file.
- **A missing flag is `false`.** A config written by an older version stays valid, and
  the safe default is more explanation, not less.

## Behavior

Happy path, first time:

1. A session starts with no `~/.claude/bb.config.json`. The frame carries one line: no
   profile calibrated, `/bb:config` sets it.
2. The user runs `/bb:config`. It asks the four-item checklist, shows what it wrote, and
   writes the file.
3. The next session starts. The hook reads the file and the frame carries the behavior
   those answers imply.
4. The user runs `/bb:brisar`. It reads the config, asks nothing about the person, and
   goes straight to the intake, at the depth `reads_code` sets.
5. Phase 1 confirms the slug. The first write is `.bb/<slug>/brief-design.md`, whose
   frontmatter says which phase is open.

| WHEN                                            | THEN                                                          |
| ----------------------------------------------- | ------------------------------------------------------------- |
| no config file                                  | frame carries the invitation naming `/bb:config`              |
| config with a valid profile                     | frame carries the behavior the four answers imply             |
| config unreadable or malformed                  | treated as missing; the session is never blocked              |
| a flag absent from the file                     | reads as `false`                                              |
| `/bb:config` with no file                       | calibrates, writes the file, prints what it wrote             |
| `/bb:config` with a file                        | shows the current profile, offers recalibrate or keep         |
| brisar with a config                            | no profile question; each phase reads the flag it needs       |
| brisar with no config                           | calls the `/bb:config` calibration, then continues            |
| `step_by_step` is true at a handoff             | commands print as numbered steps with what they print         |
| `technical_vocabulary` is false in any phase    | `scaffold`, `embed`, `MCP`, `branch` are replaced, not glossed |
| the plugin updates to a new version             | the config survives; it lives outside the install path        |
| intake runs before the slug is confirmed        | nothing is written to disk yet                                |
| a project has `.brisar/` and no brief           | read it once for the phase, then write only the brief         |
| a project has both                              | the brief's frontmatter is the one read                       |
| `.brisar/session.yaml` carries an old persona   | derived into the four flags once, written to the config       |
| a completed session restarts                    | the brief gains round `N+1`; earlier rounds stay readable     |
| `~/.claude/` cannot be written                  | `/bb:config` says so and the session runs uncalibrated        |
| the config changes while a session is open      | it applies from the next session; `/bb:config` says so        |
| a front is skipped or a direction discarded     | it lands in the brief's `## Left out` with its reason         |
| Develop finishes a surface                      | it lands in `design.md`'s frontmatter, not in a state file    |

## Tasks

- [x] **1. The config contract**: `references/bb-config.md` with the location, the JSON
      schema, the four flags, missing-reads-as-false and unreadable-reads-as-missing
      → behaviors 1, 3, 4, 11 · dep: — · verify: reading
- [x] **2. Hook reads and injects**: `inject_operating_context.py` composes the frame
      with the behavior block or the invitation; `operating-context.md` grows the slot
      → behaviors 1, 2, 3 · dep: 1 · verify: running the hook on both shapes
- [x] **3. The `/bb:config` skill**: `skills/config/SKILL.md`, calibrate, show,
      recalibrate, with its scope stated in the first line
      → behaviors 5, 6, 17, 18 · dep: 1 · verify: CI `validate-frontmatter`
- [x] **4. brisar stops asking**: `phase-0-calibration.md` is deleted, `SKILL.md` Step
      0.1 and the phase table lose it
      → behaviors 7, 8 · dep: 3 · verify: `grep -rn persona` is empty inside brisar
- [x] **5. Readers read their own flag**: `phase-1-intake`, `phase-3-scaffold`,
      `phase-5-handoff`, `brief`, `phase-medium`, `phase-diverge`, `phase-research`,
      `preflight-tooling` each switch to the flag named in the table above
      → behaviors 9, 10 · dep: 4 · verify: reading
- [x] **6. The Framer fork drops the profile**: `SKILL.md` and `product-registry.yaml`
      key it on `brand.workflow == framer-harpa`
      → behavior 7 · dep: 4 · verify: reading
- [x] **7. The brief carries the journey**: `brief.md` gains the frontmatter block
      (`status`, `phase`, `round`, `slug`, `created`) and the `## Left out` section
      → behaviors 5, 16, 19 · dep: — · verify: CI `validate-frontmatter`
- [x] **8. The state file is deleted**: `persistence.md` goes, and every phase that
      wrote a section of `session.yaml` writes its part of the brief instead
      → behaviors 12, 13, 19 · dep: 7 · verify: `grep -rn "session.yaml"` is empty
- [x] **9. Resume reads the brief**: the resume globs `.bb/*/brief-design.md` and reads
      `phase` from the frontmatter; a `.brisar/` found on the way is read once
      → behaviors 13, 14, 16 · dep: 8 · verify: reading
- [ ] **10. Derive an old persona**: a `.brisar/session.yaml` with `profile.persona_id`
      and no config is turned into the four flags once
      → behavior 15 · dep: 1, 9 · verify: reading
- [x] **11. The machine paths find their owner**: `surfaces[]` moves into `design.md`'s
      frontmatter, `ds_path` keeps its resolution order and stops being persisted
      → behavior 20 · dep: 8 · verify: reading
- [ ] **12. `spec-state.md` states the shape**: `brief-design.md` and `design.md` carry
      frontmatter, and no `.bb/<slug>/` member is a state file
      → behaviors 12, 14 · dep: 7, 11 · verify: `python3 scripts/lint_spec.py`

## Out of scope

- Tooling detection. `preflight-tooling.md` keeps detecting git, `gh` and the MCP.
- The output path (`embed`, `prototype-hosted`, `framer-handoff`). It stays a per-run
  brisar decision.
- Any config key beyond the four flags: the ship destination, the review depth, the
  report language. _revisit_ once the profile has proven itself.
- A per-repo override of the profile. _revisit_ if one person ever needs two profiles.
- Migrating a `.brisar/` folder in place, or deleting it. It stays readable and
  untouched; the next write lands in the brief.
- Teaching `lint_spec.py` the brief's sections. _revisit_ once the brief has carried a
  frontmatter through a few rounds.

## Open

Nothing.
