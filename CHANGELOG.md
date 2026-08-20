# Changelog

## 2.18.0 (2026-08-20)

**bb keeps itself current.** An install stayed on the version it arrived at. Claude Code
has no notice for an outdated plugin, and a marketplace clone is refetched only when
someone runs `claude plugin marketplace update` by hand, so an install from July still
served July's skills. With 16 skills that change by PR every week, that is people running
a bb the CHANGELOG no longer describes.

The `SessionStart` hook now does the update, silently: nothing appears on screen, nothing
is asked, and there is no flag that turns it off. The effect lands on the next session
either way, because a session has already loaded its plugins by the time a hook runs. So
the running session keeps the version it loaded, and the line it carries says which
version starts next.

### Added

- **`plugins/bb/hooks/check_version.py`**, both halves of the update in one file.
  `report()` runs in process on the session start: it reads the stamp and returns the line
  the session context carries when the last run installed something. The `__main__` path
  is the detached worker, spawned with `sys.executable` because `python3` is not on every
  PATH a child inherits, and it does the slow half: `git fetch` in the marketplace clone,
  the version compare, the two commands a person would run,
  `claude plugin marketplace update MARKETPLACE` and
  `claude plugin update bb@MARKETPLACE -s SCOPE -y`. It calls the CLI instead of writing
  into the cache and rewriting `installed_plugins.json`, which would be a hook
  reimplementing the installer that owns those files.
- **The stamp, `update-stamp.json`, is the only channel between the two.** It holds
  `date`, `outcome`, `from`, `to`, and `reason`, and it sits under `CLAUDE_PLUGIN_DATA`,
  falling back to `~/.claude/plugins/data/bb-MARKETPLACE`, because the install path carries
  the version and is replaced on every update. The session start pays one file read: no
  network, no install, and no wait. **The day is claimed before the spawn**, so two
  sessions starting at the same moment leave only the first one spawning a worker, and a
  run that fails records the reason and leaves tomorrow as the retry.
- **The guard on a clone that is a working tree.** `claude plugin update` installs what
  the marketplace clone holds in its working tree, not what the default branch holds, so
  the worker installs only when the clone sits on the remote default branch with a clean
  tree. Any other state writes the branch name or the dirt into `reason` and installs
  nothing. Checking the branch out is never an option, because the clone is someone's
  checkout.
- **Never a downgrade.** The comparison is the `version` in
  `plugins/bb/.claude-plugin/plugin.json`, read from the fetched tip and compared as
  integer tuples so `2.9.0` reads below `2.16.0`, and the install runs only when the remote
  is greater. The bump is the release: a commit that lands on `main` without one reaches
  nobody, and with a daily check and no opt out, keeping `main` green is the gate this
  leans on.

### Changed

- **`hooks/sync_instructions.py` carries the update on every path it has.**
  `update_note()` asks `check_version.py` for the line, claims the day and spawns the
  worker; `emit()` is now the single print, so all three paths merge into one JSON
  document. The child gets the null device on all three streams, plus
  `DETACHED_PROCESS | CREATE_NO_WINDOW` on Windows and `start_new_session` elsewhere: the
  hook's stdout is the payload the runner parses, and a child that inherits it corrupts
  the session start.
- **The update line sits outside the instructions opt out**, under its own
  `## bb's own version` heading. `custom_instructions: false` governs
  `~/.claude/BUILDER-BUNDLE.md` and the `CLAUDE.md` import, which is all it ever governed;
  the version bb runs is not an instruction. Every failure in the new path stays silent,
  which is the hook's existing contract: exit 0 and print nothing.
## 2.17.0 (2026-08-20)

**One skill, one document.** `/bb:discover` used to seed `## Problem` / `## Hypothesis` /
`## Fit` / `## Cuts` inside `spec.md`, and `/bb:brisar` used to write a brief, a handoff
and a design file beside it. Three skills wrote into the same folder with overlapping
claims on the same sections, so a later run could not tell whose sentence it was reading
or whether the spec's copy of a framing was still the framing.

Each skill now owns exactly one document, and `spec.md` has exactly one writer.
`/bb:discover` writes `discovery.md`, `/bb:brisar` writes `design.md` plus a `prototype/`
folder, `/bb:spec` writes `spec.md`, and the build side reads the spec. The two records
are read **by path and never copied**: when the spec needs a fact one of them carries, it
cites the document and the section. A quoted section is a second copy that goes stale the
next time its own skill runs.

The correction runs one way. Where a record and the spec disagree the spec wins, and
`/bb:spec` still does not edit the record: the record's own writer registers the reversal
on its next round, so the history stays readable.

### Changed

- **`references/spec-state.md`** is the contract for the new layout: `discovery.md`,
  `spec.md`, `design.md`, `prototype/`. Each document carries its own frontmatter, and
  `discovery.md` gets a `phase` / `verdict` block of its own.
- **`/bb:brisar`**'s Deliver phase drops `handoff.md` and invokes `/bb:spec` at its gate,
  so the design work reaches the contract instead of a document nobody reads next.
- **`/bb:spec`** reads the two records as upstream and cites them.
- **`/bb:review`**'s contract front and `fronts.md` follow the spec to its single writer.

### Breaking

A `.bb/<slug>/` written by an earlier version carries `brief-design.md` and a seeded
`spec.md`. Nothing migrates it. Move the framing sections into `discovery.md` and rename
`brief-design.md` to `design.md` before running the new skills against that slug.

## 2.16.1 (2026-08-20)

**The dispatch carries its own opt-in, and the fallback chain is stated once.** A run read
2.16.0's "the fallback for a session that cannot run it" as covering a session carrying a
standing rule against workflows, and built the whole spec in the main context. The fix says
opposite in the place the run reads: invoking `/bb:implement` or `/bb:delegate` is the
request for the workflow, and that request is the opt-in.

Saying it three times is what the first attempt got wrong. The count of fallbacks landed in
five sentences across three files, in two spellings that contradicted each other, and one
of them read a refusal of `scriptPath` as a reason to build in the main context, when that
refusal still has an inline `script` dispatch after it. The chain is now a numbered list in
`references/build-tasks-workflow.md` and nowhere else; the skills point at it by name.

### Changed

- **`references/build-tasks-workflow.md`**: the fallback chain is three ordered steps, with
  step 2 marked as still a dispatch. Two stops that are not steps of it are named: a denied
  permission dialog, which is reported and asked about, and a stage zero that cannot run
  the project's checks, which is a blocker naming the command it could not execute.
- **`/bb:implement` and `/bb:delegate`** carry no count of their own, and the opt-in covers
  the build it was invoked for. Both name the `description` triggers alongside the slash
  command, so a run that started from "build it" is covered too.
- The one line a fallback owes now names which step the run landed on.

## 2.16.0 (2026-08-19)

**The build has one path.** 2.7.0 gave `/bb:implement` and `/bb:delegate` a second
build path and made it a question asked once per run. The question is gone: the build
is one agent per task, dispatched as a workflow, and the in-context build survives only
as the fallback for a session that cannot run it.

The mode question cost more than it bought. Both answers had to stay documented and
both had to stay correct, so every change to the build loop was written twice, and the
user was asked to pick between an argument they already agreed with (a spec of eight
tasks built in one context hits compaction mid-build) and the path that argument
rejects. What the answer never was is a preference: it was the session's capabilities,
which the skill can read for itself.

### New

- **`plugins/bb/workflows/build-tasks.js`**, the script the run dispatches, fixed and
  versioned instead of authored per run. `references/build-tasks-workflow.md` now
  documents it, and **the script is the definition**: the task agent's contract is the
  prompt string inside the file, not a paraphrase kept next to it. This reverses
  2.7.0's `build-slices-workflow.md`, which was the contract a generated script had to
  meet, re-derived by whoever ran the build.
- **`.github/scripts/validate-workflow-script.ts`**, the guard that replaces most of
  the old pre-invoke checklist. It blanks comment, string, template and regex bodies
  first, so every check reads code and not text, then asks: the script parses;
  `export const meta` is present, a pure literal (no interpolation, no spread, and no
  bare word other than `true`, `false`, `null`, `undefined`) and carries a `name` and a
  `description`; `meta.phases`, when declared, has one entry per `phase()` call and the
  titles match one for one, since the title is what pairs an entry to a call; there is
  exactly one `parallel()` and it precedes the task loop; and no spelling of
  `Date.now()`, `new Date()` or `Math.random()` is reachable, optional chaining and
  `Date[...]` included. It runs inside `package.json`'s `validate`, which is what lefthook's
  pre-commit job runs, and as its own step in `validate.yml`.
- **`.github/scripts/lib/validate-common.ts`**, the tree walk, the argv resolution and
  the report tail both validators had a copy of. Two argv bugs died with the
  duplication: a mixed `dir file.js` call inferred its branch from the extension and ran
  `readdir` on a file, and a path the validator does not read was dropped silently,
  printing the same `0 errors` a clean run prints.

### Changed

- **`/bb:implement`** (2.5.0) keeps its 8 steps, and step 3 no longer asks. It builds
  `args` by reading the spec, confirms the three items that are genuinely per-run,
  proves the script with one `Bash` call, and invokes `Workflow` with `scriptPath`. The
  fallback chain lives in `build-tasks-workflow.md` and step 3 points at it instead of
  restating it; what the step keeps is the rule that the downgrade **names its reason in
  one line**, so it doesn't read as a preference. With every task already ticked there
  is nothing to dispatch: the step says so and goes to step 8, and the script returns
  the empty report before stage zero for a caller that invoked anyway.
- **`/bb:delegate`** (2.6.0) lost 2.7.0's step 3 entirely, and the rest renumbered.
  Nothing about how to build is asked at either end of the chain, and the report no
  longer names a mode; a run that fell back to this context says so instead. A blocked
  run now records **why**: the blocker goes into the spec's own `## Open` with the
  status flip, which is the line bare `/bb:delegate` reads back when it skips that spec,
  and the skip names where the blocker sends it instead of pointing everything at
  `/bb:spec`.
- **A stage-zero stop names every blocker it found.** Both agents have already
  returned when the verdicts are read, so a reuse note pointing at code that is gone no
  longer hides a check the run cannot execute, or a tree that was already red. The old
  `if / else if` reported the first and dropped the rest, which cost a whole round trip
  to discover the second.
- **The task loop has a fourth exit.** A task that returns `green` with a missing
  `verify` result, or with `failed`, stops the build instead of landing in `built`:
  `verify:` is what makes a task done, so green over an absent proof is a task the
  caller and ship would both read as proven.
- **oxfmt formats `js`** alongside `json` and `md` in the lefthook glob. CI already
  formatted the file through `oxfmt --check .`; the hook did not.

### Removed

- **`references/build-mode.md`**: with the question deleted there is no reader left.
  Its argument for why the build runs outside the main context moved into
  `build-tasks-workflow.md`, which is where the build now lives.

## 2.15.0 (2026-08-19)

**bb's context is a file you own, and having it is a choice.** The frame used to arrive
as something a hook printed into every session, which nobody could read, edit or refuse.
It is now `~/.claude/BUILDER-BUNDLE.md`, imported from `~/.claude/CLAUDE.md`, written by
`/bb:profile` with the profile already in it.

### Added

- **`~/.claude/BUILDER-BUNDLE.md`**, written by `hooks/sync_instructions.py`: the
  operating frame plus the four profile sentences, under a header naming the version that
  wrote it and how to make it stop. `~/.claude/CLAUDE.md` gets the `@BUILDER-BUNDLE.md`
  import, three lines fenced by `<!-- bb:start -->` and `<!-- bb:end -->`. Everything
  outside those markers is the person's, and is never rewritten, line endings included.
- **`custom_instructions`**, a top level field beside `profile`. `false` and both go away:
  the file is deleted and the block leaves `CLAUDE.md`, because an opt out that leaves a
  file behind is not one. Absent, or holding anything other than `false`, reads as `true`.
  `/bb:profile` asks it as its own two option question, apart from the four about the
  person. The contract is in `references/bb-config.md`.

### Changed

- **The SessionStart hook stopped being the injector.** `hooks/sync_instructions.py`
  replaces `inject_operating_context.py`, and what it does on a session is keep the file
  in step with the installed plugin: the frame lives inside the versioned install path, so
  without this an update would leave the previous version's text in `~/.claude` for good.
  It writes only when the rendered text differs from what is on disk.
- **Nothing is written before it is asked for.** With no config there are no files, so
  installing the plugin writes nothing into anyone's `~/.claude`. Until the first
  `/bb:profile`, the hook still carries the frame in the session itself, with one line
  saying where it will live once it is asked for. What this shape cannot do is clean up at
  uninstall time, which is why the file's own header says what wrote it.

### Fixed

- **The hook is invoked as `python3`.** `hooks/hooks.json` said `python`, which is absent
  on a machine that only ships `python3`. Because the hook must never block a session, it
  failed the only way it can: silently, with no frame arriving at all.

## 2.14.0 (2026-08-19)

**The profile is asked once, globally, and the journey lives in the brief.** Calibration
used to be Phase 0 of `/bb:brisar`: every design journey opened by asking the same person
the same four things, and the answer died with the project. It is now `/bb:profile`, asked
once, written to `~/.claude/bb.config.json` and carried into every session by the
`SessionStart` hook. With the profile out of brisar, the last reason for a session file
went with it, and `.brisar/` is gone: the brief carries the journey.

### Added

- **`/bb:profile`**: a checklist of four habits the person either has or does not,
  `reads_code`, `uses_terminal`, `technical_instructions` and `technical_vocabulary`. All
  four point the same way, so checked always means say less about it and nothing checked
  is the most careful profile there is. It writes `~/.claude/bb.config.json`, shows the profile on disk and
  recalibrates it. It is the only writer of that file. The contract, the JSON shape and
  what each flag changes are in `references/bb-config.md`.
- **The hook always injects.** `inject_operating_context.py` composes the frame with the
  profile block when the file exists, and with an invitation naming `/bb:profile` when it
  does not, so a session is never silently uncalibrated. A missing flag reads `false`, and
  a malformed file reads as no profile. (2.15.0 replaced that script with
  `hooks/sync_instructions.py`, which writes the file instead of printing into a session.)
- **An old persona is derived, not re-asked.** A project brisar ran before the profile
  carries `profile.persona_id` in its `.brisar/session.yaml`. When there is no profile, the
  four flags are derived from it once and pre-fill the `/bb:profile` checklist, which the
  person confirms. The old file is read, never written.

### Changed

- **brisar reads the profile instead of asking for it.** Each phase that changed its voice
  by persona now reads the flag it actually needs: the intake reads `reads_code` and
  `technical_instructions`, the scaffold reads `uses_terminal`, the handoff reads both of
  those, and the vocabulary bans key on `technical_vocabulary`. Tooling stays where it
  was, in the preflight, and the output path stays a project decision.
- **The brief carries the journey.** `brief-design.md` opens with `status`, `phase`,
  `round`, `slug` and `created`, and the resume reads that block instead of a state file.
  Phase 1 opens the brief, and every phase after it updates it where it hands off. The
  Develop and Deliver artifacts, `develop-notes.md`, `design-review.md`,
  `accessibility-checklist.md` and `handoff.md`, each summarize themselves in their own
  frontmatter, and the surfaces list lives in `design.md`'s. `spec-state.md` states the
  shape: no member of `.bb/<slug>/` is a state file.

### Removed

- **`.brisar/` entirely**, with `session.yaml` and `config.yaml`. Everything durable about
  a journey lands in `.bb/<slug>/`, beside the spec it serves.
- **`phase-0-calibration.md`** and the four personas it asked between, and
  **`references/persistence.md`**, the page that described the state file.

## 2.13.0 (2026-08-18)

**One language: the bundle writes English.** Since `vocabulario-pt` the plugin
carried two, English instruction bodies over a Portuguese layer for everything the
user sees. That layer existed to guarantee the user is answered in their language,
which Claude already does by reading the user, so what the mandate actually bought
was a second vocabulary to maintain, a reference to police it, and a bilingual
document every time a gate question sat inside an English step. The layer is gone,
and every line that ordered an output language was deleted instead of reversed.

### Changed

- **The fixed sections of a spec are English again**: `## Decisions`, `## Behavior`,
  `## Tasks`, `## Out of scope`, `## Open`, with `dep:` and `verify:` as the task
  fields. `lint_spec.py` still resolves the Portuguese spelling of every section and
  of both fields, so a spec written before this still builds; `W003` now names the
  English one to write instead.
- **Every sentence the user reads is English**: the 15 skill descriptions, the 2 agent
  descriptions, the gate questions, the option labels and the report templates, plus
  the `README.md` (all lowercase kept) and both manifests.
- **The record was translated with the code.** The 12 CHANGELOG entries and the 8
  landed specs in `.bb/` are English now. What an entry quotes from the version it
  describes stays as written: an old section name, a deleted filename, an old option
  label, a trigger phrase the user types.
- **A style rule names no language.** `doc-style.md` scoped itself to "every English
  sentence" and carried a spelling rule for one language, which is not what the page
  does: its rules are about how a sentence is built, so they hold in whatever language
  the reader arrived in. The spelling rule is gone, the date format and the pointer to
  a document's subsections became the outcome they buy instead of a literal wording,
  and so did the serial comma. `.claude/CLAUDE.md`, `hooks/operating-context.md`,
  `write-readme/SKILL.md` and the discovery table stopped qualifying the prose they
  govern. The compat rule for the section names points at the older spelling and the
  current one instead of at two languages, in `spec-state.md`, `spec-format.md` and in
  `lint_spec.py` (`RENAMED_SECTIONS`, and the `W003` message with it). The scaffold
  templates carry `lang="<locale>"`, a placeholder like the `<slug>` next to it, in
  place of a locale nobody chose.
- **A figure of speech has to name a mechanism the code has.** `spine` for the fixed
  sections and `ruler` for a style page named nothing, so they became what they are,
  and `doc-style.md` states the test. `safety valve`, `gate`, `front` and `trilha`
  stay: each names a real mechanism.

### Removed

- **`plugins/bb/references/vocabulario.md`**, and with it the hybrid language policy
  in `.claude/CLAUDE.md` and `hooks/operating-context.md`. The one rule that survives
  it, call each thing by the name the code gives it, lives in `doc-style.md`, and its
  four readers point there.

## 2.12.1 (2026-08-18)

**The style rules became self-sufficient.** `doc-style.md` pointed at the source on
the web as the thing that settles what the page does not, which puts a read in the
cloud in the middle of a local write. The page now carries every rule: whoever
writes reads one file in the repo and nothing else.

### Changed

- **The citation of the source is gone**, from the title, the precedence and the
  framing. It is no longer "Google's guide as the way bb writes", it is bb's style,
  with the rules written out. Precedence came down to two steps, the skill's
  contract first and the page second, and what neither settles goes to the closest
  rule right there.
- **The two divergences became rules of their own.** The dash has its own section
  now, instead of existing as a difference from another guide. The figure of speech
  became a voice bullet and got the test it was missing: it holds when it names a
  mechanism, like the safety valve that fires. Where the literal sentence is already
  short, write the literal one.

### New

- **A colon does not work inside frontmatter.** The dash section records that a `: `
  in an unquoted YAML value reads as a nested mapping and fails
  `validate-frontmatter.ts`. There a dash becomes a period, parentheses or a comma.
  This is the rule that was missing in writing when 2.12.0 broke CI in 10 SKILL.md
  files.

## 2.12.0 (2026-08-18)

**bb's English prose got style rules, and the dash is gone.** The documents bb
generates outward and the instruction agents read had no standard at all:
`## How It Works` sat next to `## Style contract`, and the dash showed up 1737 times
in 84 files, even with `/bb:write-readme` banning its own since the first version.
Now [Google's documentation guide](https://developers.google.com/style) is the rule,
distilled into a reference whoever writes reads before writing.

### New

- **`plugins/bb/references/doc-style.md`**, plugin level rather than skill scoped,
  because it governs the prose of every skill and of the repo. It covers tone and
  voice, headings, text formatting, lists and tables, links, numbers, dates and
  punctuation, all in positive form: no recommended/not recommended pair, because
  writing the wrong one next to the right one primes the wrong one.
- **Two divergences, recorded in the opening** so nobody reads them as oversights.
  Never a dash, which is stronger than Google (it allows the dash without spaces).
  And the figurative voice stays: Google avoids metaphor because it travels badly
  through translation, but here the metaphor is what makes the instruction stick to
  the agent reading the `SKILL.md`.
- **Precedence written down**: the house rule first, the guide second, which is the
  hierarchy Google itself publishes. Where `/bb:write-readme` already has a contract
  (all lowercase, four blocks, one badge per verifiable fact), the contract wins,
  and its `SKILL.md` points at the reference instead of repeating the rule.

### Changed

- **The dash left 87 files.** Every removal was a judgment per sentence, not `sed`:
  where it went, a comma, a colon or a period went in, or the sentence was
  rewritten. Where a pair of dashes was an aside, it became parentheses.
- **The headings in declared title case outside `ds/` became sentence case**, with
  proper nouns and identifiers keeping their case.
- **The rules reach any session**: `hooks/operating-context.md` points at the
  reference alongside `vocabulario.md`, and so do `.claude/CLAUDE.md`,
  `write-readme/SKILL.md` and `review-setup/references/guide-template.md`.
- **The dash rule crosses both languages**, because it is punctuation rather than
  vocabulary: the 22 dashes that lived in a `description:` are Portuguese lines and
  fell with the rest. The remaining Portuguese stays governed by `vocabulario.md`.

### Unchanged

- **`references/ds/` stays untouched.** It is Inspira's brand package, brand content
  with a voice of its own: 383 dashes and 70 title-case headings that stay where
  they are.
- **The older entries in this CHANGELOG and the 7 specs in `.bb/`.** They are a
  landed record; rewriting changes what was already published.
- **The dash that is a functional token.** The 5 occurrences of `depende: —` a task
  line carries when nothing blocks it stay: there the character is a value the
  format reserves, and removing it would be a change in behavior. An en dash in a
  numeric range (`3–5 bullets`) stays for the same reason.
- **No CI check and no script.** The enforcement is the reference being read: a dash
  detector over mixed Portuguese and English prose flags functional tokens and
  quotations, and the false positive costs more than the drift.

## 2.11.0 (2026-08-18)

**The skills' `description:` fields got leaner.** Every `description:` in the bundle
enters the context of every session: it is the text Claude reads to decide which
skill to call, and it is paid for even when no skill is used. Ten of them had turned
into a summary of the SKILL.md: `/bb:review` listed the seven fronts, the verdict
rubric and the surface mode; `/bb:brisar` narrated the four phases. None of that
helps routing, because the skill explains all of it once loaded.

### Changed

- **~2,000 characters less in every session's preamble.** The descriptions added up
  to 11,431 characters; they now add up to 9,460. What left was execution detail
  (which agents it dispatches, in what order, under which rubric); what stayed is
  what decides routing: what the skill does in one sentence, the user's trigger
  phrases, and the "don't use it for … (use /bb:other)".
- **Skills touched**: `review` (1780 to 1087), `brisar` (1203 to 779), `discover`,
  `spec`, `legal-lens`, `maintain-repo`, `review-setup`, `think`, `challenge` and
  `write-readme`. The other five already fit the budget and stayed as they were.

## 2.10.0 (2026-08-18)

**Reviewing got cheap, and `/bb:ship` stopped reviewing.** A routine `/bb:review`
fired ten agents on Opus: the two fan-out agents declared no `model:`, so they
inherited the session's model, and the depth table escalated to the most expensive
tier on its own as soon as the diff grew. Reviewing cost more than the change under
review. On the other side, `ship` ran the whole engine before landing, without
asking, so the most expensive pass in the bundle happened every time someone wanted
to push a branch.

### Changed

- **Both agents declare `model: sonnet`.** Without the declaration an agent inherits
  the session's model, which is Opus. Deep can still ask for Opus, but it is a choice
  now, not a silent default.
- **Depth became an axis you decide**, not a function of the diff's size.
  **Standard**: three correctness angles, one agent per front, no sweep, the whole
  fan-out on Sonnet, which is what runs on any diff, large or small. **Deep**: only
  on request (`/bb:review deep`, "review it deeply", or the option in the fronts
  question), with the whole angle set, the closing sweep, a larger cap and the agents
  on Opus.
- **Verify got a cap and changed its dispatch unit.** It used to send one agent per
  location, and locations come from the raw candidates, so 25 candidates in 20
  locations funded 20 agents to deliver a report that keeps 10. Now it is **at most 4
  agents** (6 on deep), dispatched **per file** instead of per location: one agent
  opens `src/a.ts` once and judges the five candidates in it. Above the cap the files
  go in batches, correctness first; no candidate goes unjudged.
- **`bb-finder` and `bb-verifier` became `bb-review-finder` and
  `bb-review-verifier`.** The prefix says which pipeline they belong to and clears
  the risk of an agent being picked in place of `/bb:review`, which is the real entry
  point.
- **The accessibility front stopped firing by extension.** A `.tsx` that only touched
  a handler, a hook, a type or an import is not a UI change, so availability now
  reads the content of the hunks (markup, an attribute that decides semantics, focus
  or contrast CSS) and the front is simply not offered when there is nothing to read.
- **`/bb:ship` lands; reviewing is a question afterward.** Ship does only the
  mechanical half: it greens the **project's checks** (lint, format, typecheck,
  tests, whatever CI runs), commits, and lands through the chosen destination. After
  landing, a two-way gate: **"Review now"** (invokes `/bb:review`, which asks about
  the fronts as always) or **"Stop here"**.
- **"Local gate" left the vocabulary.** The word already meant the handoff gate, the
  brisar gate and the LexFlow gate; lint and tests are now called the **project's
  checks** across the whole Construir trilha.
- **`review-checklist.md` and `quality-checklist.md` changed homes**, from
  `references/` at the plugin root to `skills/review/references/`. They were shared
  because ship reviewed; with ship out, the criteria belong to whoever uses them.
  **Ship stopped reading the whole engine**, including `act-apply-fixes.md`, whose
  useful half for ship (one change at a time, untested code left trivial or flagged)
  is now two lines in its own step 2. Reading 55 lines of finding ordering to fix a
  red lint cost more than it saved.

## 2.9.0 (2026-08-15)

**One word per thing, in Portuguese.** The item of `## Tarefas` is a **tarefa**, the
top-level artifact is the **spec**, the spec's fixed sections became Portuguese and
the folder on disk lost a level. Along with it comes the rule that prevents the next
coinage: `references/vocabulario.md`.

The symptom was the plugin writing `slice` 125 times and the session answering
"fatia", a word that exists neither in the code nor in the conversation, with its
gender shifting inside one session. When the name is the concept, changing the name
kills the leak at the source. When it is ordinary English in an English document,
like `load-bearing`, `fan-out` or `seam`, the document stays as it is and the table
says what to write when the sentence is Portuguese. Two causes, two remedies.

### New

- **`references/vocabulario.md`**, carrying the principle (call each thing by the
  name it has in the code or in the repo), the `chave`→`escreva` table and the
  capitalization: Portuguese in sentence case, proper nouns and identifiers with
  their exact case. Written as a positive instruction: the column is "escreva", and
  the English term enters only as a search key. The pointer lives in
  `hooks/operating-context.md`, which is injected at the start of the session **and
  after every compaction**, so it holds for every skill and for a plain chat;
  `spec/references/spec-format.md` gets a line of its own, because the spec is the
  text the builder repeats afterward.
- **`W003` in `lint_spec.py`**, so an English section stays valid and gains a warning
  with the translation next to it. A spec written before the rename, in any repo,
  still builds.

### Changed

- **`slice` to tarefa (task in English).** They are cognates, so the concept has one
  name and no third word enters. 12 files, including `lint_spec.py`'s `W002` message;
  `references/build-slices-workflow.md` became `build-tasks-workflow.md`.
- **`brief` to spec** at the top level, in both languages: the file is `spec.md`, the
  command is `/bb:spec`, and `references/task-state.md` became `spec-state.md`.
  Inside `skills/brisar/**` the word "brief" stays: there it is `brief-design.md`,
  another artifact, with a file and a name of its own. The exception to the exception
  is where brisar's text points at `spec.md`.
- **The folder loses a level: `.bb/<slug>/`.** `.bb/` held nothing but `tasks/`, and
  the intermediate level only repeated the word being retired. The scan glob became
  `.bb/*/spec.md`, and `validate.yml` with it, while `.bb/tasks/*/spec.md` stays in
  the scan for a spec that lives in another repo. The folder's slug is the key, so
  the same spec in both places counts once. The 7 specs in this repo already
  migrated.
- **The spec's fixed sections in Portuguese:** `## Decisões`, `## Comportamento`,
  `## Tarefas`, `## Fora de escopo`, `## Em aberto`, plus `## Problema`,
  `## Hipótese`, `## Encaixe` and `## Cortes`, seeded by `/bb:discover`, and
  `## Jurídico`, from `/bb:legal-lens`. `dep:` became `depende:`. The readers take
  both names, and the EN/PT pairing lives in one place, `references/spec-state.md`;
  the others cite that file instead of repeating the list. The frontmatter stays
  English: `status`, `created` and `slug` are data keys, validated by `E001` and
  written by `/bb:delegate`.
- **The `description:` of `bb-finder` and `bb-verifier`** rewritten from the table:
  "só leitura", "despacha em paralelo", "veredito", "ângulo/lente", "formato do
  achado". The skills' trigger phrases stay intact: "landa essa branch", "esverdeia a
  PR" and "shapeia essa ideia" are how the user speaks and are what routes.

### Unchanged

- The English prose of the reference documents and the SKILL.md files. An English
  document writing "load-bearing decision" is ordinary English; swapping it for
  "decisão estruturante" mid-sentence produces broken text.
- The capitalization of the Portuguese text was already right: the sweep found two
  lines in Title Case outside the design system, and both defend themselves. What was
  missing was the written rule, not a correction pass.

## 2.8.0 (2026-08-11)

**The unattended path left the plugin.** `BB_UNATTENDED` and the Cloud Routines
guide no longer exist: bb now has one way to run, the supervised one.

The path was never switched on, no routine ever ran a `/bb:delegate`, but it
charged a toll in almost every skill of the Construir trilha. The whole debate
about where the blocker appears (the PR description or the brief's `## open`),
`ship`'s fixed destination, build-mode's "unattended is always workflow" rule, the
retry cap on the slices, the `claude/<slug>` line repeated in three skills and the
four "under `BB_UNATTENDED` there is no question" lines scattered through `review`
existed only because of it. A branch nobody walks is a branch nobody fixes: step 4
of `/bb:implement` already carried a retry cap that contradicted the gate right
above it.

### Removed

- **`hooks/unattended-context.md`** and `inject_operating_context.py`'s
  `is_unattended()`: the hook injects one frame, the same one in every session.
- **`references/routines.md`** and **`references/scripts/scaffold_routine.py`**:
  the Cloud Routine guide and the scaffold of the routine prompt.
- **`skills/maintain-repo/references/routines-setup.md`** and the skill's routine
  setup section: triage is still decision support, now only as a supervised run.
- The Cloud Routine line in `hooks/scheduling-decision.md`, and with it the
  `Survives laptop closed?` column, which only separated routine from everything
  else.
- The `## Unattended` section of `references/build-mode.md` and the gate bullet of
  `references/handoff-gate.md`.
- The "run without supervision" section of the README.

### Changed

- **`/bb:delegate`** (2.4.0), **`/bb:implement`** (2.3.0) and **`/bb:ship`**
  (2.3.0) lost the double branches: one destination, one branch question, one
  behavior per step. `references/land-pr.md` loses the cap on comment rounds and
  the AFK watch, because the PR loop lives and dies with the session, and to go
  past it there are Channels or a scheduled task on the Desktop.
- **Never-merge still holds, anchored in what is left.** The guarantee used to be
  capability scoping in the routine; now it is what was always true at the desk
  too: the skills have no merge step and the protected branch is the server-side
  backstop.
- **Stage zero is still justified.** The fact holding it up was not the unattended
  path, it was the runtime: a slice agent runs under `claude -p` and the Agent SDK,
  where there is nobody to ask, so a command outside the allowlist fails instead of
  pausing. That is now said in `references/build-slices-workflow.md` without going
  through the routine.
- **`/bb:review`** (2.4.0) dedupes against an earlier review comment. On a PR that
  already carries one, each point appears once: the still-open ones as a status
  line, the new ones in full, the resolved ones as a count
  (`references/act-comment-findings.md` §3, which `mode-external-pr.md` now points
  at too).

## 2.7.0 (2026-08-06)

`/bb:implement` and `/bb:delegate` gain a **second build path**: dispatching a
dynamic workflow with one agent per slice, instead of building the whole brief in
the main context. The old path stays exactly as it was, and the choice is the
user's, once per run.

The problem was not speed. An eight-slice brief built in a single context hits
compaction mid-build, and that is where the loop degrades: the `## behavior` falls
out of context and the build starts drifting from the `## decisions`. One agent per
slice starts on a clean budget carrying only the brief and its own piece; what gets
lost of the tacit context is paid for by a conventions note that crosses the
stages, lossy on purpose instead of lossy by accident.

### New

- **`references/build-mode.md`**: the choice between workflow and context. When it
  is asked (once, at the start of every supervised run, with no size threshold),
  the question in PT-BR, the unattended rule (always workflow, no question) and the
  fallback for when `Workflow` does not exist in the session: `disableWorkflows`,
  org policy or an old client. Without it, both paths build in context **and say
  why**, because a silent downgrade reads as a preference.
- **`references/build-slices-workflow.md`**: the contract the generated script has
  to meet. The slices run in a `for` with `await`, not in `pipeline()`: they share
  one working tree, and `dep:` exists precisely to say that 2 leans on what 1
  created. `parallel()` appears once, in **stage zero**, which is read-only: one
  agent per reuse note, plus one that resolves the gate's commands **and runs all
  of them once**. Running is the point: it proves the permission and establishes
  the green baseline, so a tree that is already red becomes a blocker before slice
  1 instead of a false-red slice halfway through.

### Changed

- **`/bb:implement`** (2.2.0) picks the mode inside step 3, and step 7's safety
  valve now also catches the blocker that comes back from inside the run, from
  stage zero or from a slice agent. The tree stays as the run left it, for the
  diagnosis.
- **`/bb:delegate`** (2.3.0) chooses once and passes the decision along, so
  implement's loop does not ask again. A workflow stopped halfway lands where the
  valve already landed: `status: blocked`, blocker named, no landing. What came
  back green is already committed and ticked.
- **`references/routines.md`** lost the "single-agent only until you've measured
  cost" rule. It existed because fan-out had no defined shape; now it has one, and
  it is in a run with nobody awake that mid-build compaction hurts most.
  Provisioning gained the **allowlist of gate commands**: a command outside it does
  not pause in a routine, it fails.

The commit is the checkpoint: each agent commits only the files it touched, with
its slice's `- [x]` in the same commit. The workflow's resume works only in the
same session and re-runs everything that started after the first unfinished agent;
the commits survive anything, so re-running a half-built brief picks up from the
checkboxes, not from the run.

## 2.6.0 (2026-08-05)

`/bb:brisar` now covers the **whole double diamond**. It used to start at the
scaffold: the builder arrived with an idea and left with a screen, with no step
between the two beyond their own repertoire. The first diamond, researching the
space before designing inside it, existed in no skill of the bundle.

Nothing was removed and no existing phase changed its contract. Phases 0 to 3
(calibration, intake, maturity gate, scaffold) stay as they were.

### New: the first diamond

- **`references/phase-research.md`**: research before pixel, in parallel
  subagents. **The floor, which runs in any mode:** a market bench (Mobbin), the
  design system **read from the source** (not from memory, not from a frozen copy),
  and an explicit answer to "does this need a new component?".
  **Discretionary, and declared:** behavioral biases with provenance (a primary
  source or `[não verificado]`), heuristics, mental models, and "what the product
  already has to show" (assets in the repo, data that actually exists, live copy in
  the i18n, locales). The mode (`pocket`/`full`) is judged, not asked, and whatever
  was skipped is said out loud. A silent cut reads as full coverage.
- **`references/brief.md`**: the design brief as a **living contract** in
  `.bb/tasks/<slug>/brief-design.md`, recorded in `gate.design_brief`. Updated
  every round without being asked, and at the end it becomes a delta for the spec.
  It brings the **mandatory reconciliation** against `/bb:discover`'s framing
  (_confirms · contradicts · does not reach_) and the **read in chat** as part of
  the delivery, not a courtesy.
- **`references/phase-diverge.md`**: directions **on equal footing**. Each one with
  five mandatory parts (the bet · the composition · the copy it expects · a
  rationale anchored in the research · risk and cost), after declaring the base
  common to all of them. Recommending is allowed; describing one in detail and the
  others in a paragraph is not, and the equal-treatment check **blocks the gate**.
- **`references/phase-medium.md`**: the medium became a **question**: code, Claude
  design, Figma, Paper or Pencil, offering only what the preflight detects and
  **naming** what is missing. The brief serves all five; only the build changes. A
  canvas medium skips the scaffold, and canvas-first-code-later is a normal path,
  not a restart.

### Changed: the second diamond became medium-aware, and the review senior

- **Develop** reads `medium.chosen` and builds in the chosen medium. It now records
  a **precise locator** per surface × variant (the file, or the file plus the page
  plus the boards) and the deliberate **deviations**. Without those, Deliver cannot
  open or judge what was made.
- **Deliver** gained what it was missing:
  - it **reads the artifact from any medium** (files, a preview, the Paper/Figma/
    Pencil MCP). The input used to be literally "HTML/React in `src/`": whoever
    designed on a canvas had nothing it could open;
  - **the unit of review is surface × variant**, not surface. It is in the deltas
    between variants that the contract gets violated;
  - **seven lenses** instead of four. The three new ones: **copy read word by
    word** (a label naming a process that does not exist, a claim the source does
    not support, a Portuguese error in the hero), **contrast computed as a number**
    against the WCAG minimum, and the **triangulation**;
  - **triangulation of problem × research × what was built.** The
    `gate.design_brief` **adds to** the `gate.discover_brief`, never replaces it.
    Three questions: does what was built honor the research? does the research
    honor the problem? where they disagree, who is wrong? The answer can be **the
    framing**;
  - **the `divergência` severity**: the build is faithful and the review disagrees
    with a decision of the brief or of the spec. It never blocks; it opens a
    decision, and it demands the argument (without one it is a preference, and a
    preference does not enter a review);
  - **a delta for the spec** at the handoff, so the contract reaches what the
    design learned.
- **`preflight-tooling.md`** detects `paper`/`figma`/`pencil`/`mobbin`, and now
  reads **both scopes** of `mcpServers` (global and project). A server configured
  only for the current directory did not show up at the top and was reported as
  absent, which silently removed a medium the builder had.
- **Resuming**: a `brief-design.md` on disk is a signal of resumption on its own,
  with or without a session. brisar continues from where the brief stopped and
  **never re-runs the research on top of an existing brief**.

### The stance kept on purpose

Deliver's editorial stance did not change: it only flags what matters, every issue
comes with a solution, **one specific piece of praise** ("it is not cheerleading,
it is information"), non-blocking when context is missing, review and a11y in
separate files. What changed was the reach of the lenses, not the tone.

And one new rule that crosses everything: **legibility is a requirement of the
artifact.** The audience is not only designers. An internal pointer carries its
meaning at first use, and a design concept gets a 5 to 10 word gloss. Dense is
good; needing a decoder is not.

### When the tool is not there: degrade without lying

The research floor is non-negotiable, which means it needs a path for when the tool
is missing. That path used to be one sentence ("degrade and say which front"), so
the floor ran and the result got worse without anybody knowing by how much.

- **Front A without Mobbin**: an explicit ladder, and its first rung is deciding
  whether the screen is **public or behind a login**, because that defines which
  rungs exist. **Behind a login, which is most of a product** (paywall,
  expiration, upgrade modal, empty state, post-signup onboarding): the
  competitor's app **is not a source**, and the skill does not plan on getting
  into it, since brisar creates no account and does not log in. What is left:
  **public galleries via `site:`** (Land-book, SaaS Landing Page, Refero,
  Pageflows, Nicelydone, some of which index a recorded flow instead of a loose
  frame, which is the closest substitute for a logged-in screen), **the
  screenshots the builder already has** (the most signal per token, and the rung
  most often skipped out of politeness), **the product's own precedent**, and only
  then a generic search. **Public, meaning a landing page, pricing, an
  institutional site:** there the browser earns its place, with the caveat that it
  reads the _marketing_ surface and says nothing about how the platform behaves
  inside. And one obligation **tightens**: a negative finding now travels with
  **the size and the origin of the corpus**, or it does not travel. "None of the 18
  screens uses urgency" only carries weight if the 18 were not handed over by a
  ranking.
- **Front B: "it is not in the cwd" is not "it is not on the disk".** A new rung
  **before** the remote one: look for the repo in the rest of the machine (`mdfind`
  on macOS, `find` as the portable option, always excluding `node_modules`),
  searching for **the artifact and not the repo's name**, because the folder can be
  called anything. It was the silliest and the most expensive hole: brisar run from
  a neighboring folder declared the repo absent with the file right there,
  degrading three fronts for no reason. And this rung is worth **more** than the
  remote one, because it reads real source, so it recovers the component inventory
  and the "how many places use this" that the remote path does not give. With two
  caveats: confirm the hit is the right checkout (an old worktree or a vendored
  copy answers confidently and wrong), and more than one plausible hit is a
  question for the builder, not a coin toss.
- **And when `gh` is not available**, which is not an edge case: it may not be
  installed, may not be authenticated, or may be on an account with no access to
  the private repo. That path got designed instead of shrunk: search the disk
  **before** offering authentication · offer `gh auth login` (never run it alone,
  because it is authentication, and it is the builder's) · **ask the builder where
  it is**, which is the cheapest answer and the one most often skipped out of a
  self-sufficiency reflex · ask for **the repo's own rules file** instead of the
  tokens, which is better because it is authored guidance and **stays right when
  the paths change** · and only then the brand package, with the gap declared.
- **Where the paths should live, and it is not inside the skill.** Hardcoding a
  product's token path into the plugin leaves the plugin wrong on the day of the
  refactor. Two better homes, in this order: **the rules file of the product's
  repo** (the only thing capable of keeping that true) and the `ds_source` of
  `product-registry.yaml`, or a `.brisar/config.yaml`/`BRISAR_DS_PATH` for a
  per-machine override. When the search takes work, the skill **suggests
  registering it**, because the next round should not repeat the hunt.
- **Front B with the repo nowhere**: the remote rung, **reading the repo via
  `gh`** without cloning. Two calls: the **whole tree** of paths
  (`git/trees/HEAD?recursive=1`) as the map, and `contents` to read the files the
  map pointed at. It solves the common case (`gh` authenticated, repo not here) and
  covers **tokens and live copy in the i18n**. What it does **not** cover: the
  component inventory with its traps (a component's real semantics needs a source
  sweep, not two reads) and "how many places use this". **Don't use
  `gh search code`:** it has a budget of **10 requests per minute**, a subagent
  fan-out exhausts it in one round, the 403 comes back empty (exactly like "found
  nothing"), and the `path:` qualifier takes no glob, so a reasonable query
  returns zero and reads as absence. The tree stays in the normal 5,000/hour
  budget, comes complete in one call and is greppable locally; when
  `truncated: false`, **the absence of a path is conclusive**. brisar **does not
  clone on its own**, because a company's private repo on somebody's computer is
  the builder's decision.
- **The packaged fallback stopped passing itself off as a design system.**
  `references/ds/brand/` is a **brand package**: voice, principles, the meaning of
  a color, logo usage. Its `tokens.json` is a brand artifact and is **not** the
  production token vocabulary. It still serves visual intent; it stopped being
  presented as tokens read from the source, which produced classes the codebase
  does not have.
- **The mode line gained a fourth part: what the degradation invalidates.** Naming
  the tool that was missing informs nothing. "I did not read the tokens from the
  source, so the values are second-hand, the component inventory does not exist,
  and I did not verify whether this page is already in production" informs what not
  to trust.

### Not a designer: the calibration contract now holds in the new phases

Phase 0 defines a forbidden vocabulary for the `executive` profile (`scaffold`,
`embed`, `npm`, `MCP`, `repo`, `branch`, `slug`) and the four new phases of the
first diamond did not honor it, since none of them read `profile.persona_id`.

- **The phases name themselves by the result, not by the method.** "I put together
  2 or 3 different paths and you choose" instead of "diverge into directions".
  Someone who is not a designer has no reason to know what divergence is, and the
  gate was asking them to choose exactly that.
- **The medium question sells the consequence, not the tool.** Nobody without the
  repertoire chooses between Paper and Figma; they choose between "see it fast",
  "show it and get comments" and "this goes to production". `MCP` left the user's
  text.
- **The recommendation became mandatory** for the `executive` and `content`
  profiles. N paths at the same level of detail and no criterion is not
  neutrality: it is handing the hardest judgment of the flow to whoever has the
  least repertoire, and the result is usually picking the first one. It does not
  loosen the equal treatment, because the rule forbids **asymmetric description**,
  never a declared recommendation.
- **And the vocabulary contract gained a mechanical check.** The profile rule was
  aspirational: two places said "write for someone who is not a designer" and
  nothing checked. Now the self-check before presenting has **two passes with a
  target of zero**: a bare pointer (which already existed) and, when the profile is
  `executive`/`content`, the forbidden vocabulary **plus the names of the method
  itself** (`divergência`, `reconciliação`, `piso`, `pocket`/`full`), each
  occurrence **replaced** by what it means, never annotated. A rule with a check is
  followed; a rule with an adjective drifts, and that is exactly how the contract
  slipped past four phases.

### The read in chat got shorter without getting poorer

Legibility had a mechanical self-check and concision had only an adjective, so the
text had a structural bias toward inflating: glossing, expanding a pointer and
citing evidence all push it up. Three necessity tests, plus a symmetrical
self-check: each block exists to enable **one decision or one opinion**; the
finding travels with **the consequence, not with the journey**; and the
**evidence lives in the document, the chat carries the conclusion**. And **the chat
presents the delta when the reader has already read**, because "assume nobody read
it" is true for the stakeholder and false for the builder on the fourth round of a
brief they helped write. The discriminator is **the reader, not the round number**:
presenting to someone new is round 1 for that person, and the whole read comes
back.

And the tie between the two rules got resolved instead of staying implicit:
**legibility wins.** A sentence the reader cannot decode costs them the whole
point; a sentence ten words longer costs ten words. So the gloss stays and the
pointer stays expanded, always, and concision aims somewhere else: **it cuts whole
items, not the words inside them.** Concision decides **what** enters the read,
legibility decides **how** each surviving thing is written. Shortening by scraping
the gloss is the one move that fails both at once.

## 2.5.0 (2026-08-05)

### brisar's visual direction lives next to the brief

`/bb:brisar` wrote the visual direction inside the scaffolded folder
(`<slug>/design/<surface>.md`), far from the brief it serves. Now it is a member of
the task's folder: one surface becomes `.bb/tasks/<slug>/design.md`, two or more
become `.bb/tasks/<slug>/design/<surface>.md` plus an index. The project's folder
keeps the code and `design-context/` (tokens and components, which belong to the
scaffold); what left it is only the screen brief.

The folder's two members are independent: brisar without `/bb:discover` leaves a
task with design only, and a spec with no design is fine. `/bb:delegate`'s
selection scans `spec.md`, so a folder without a brief is simply not a candidate.

Whoever reads does not hardcode a path: `.brisar/config.yaml` gained `design_path`
(absolute, in the same language as the existing `ds_path`) and `surfaces[].file`
became relative to it. The choice between one file and a folder happens once, in
Phase 4, and is never re-derived downstream.

## 2.4.0 (2026-08-05)

### The spec became a document meant to be read

`/bb:spec`'s briefs were a form: six fixed sections saying the same thing three
times, a table with a 300 character paragraph inside a cell, and a whole section
recounting the conversation that produced the brief. Whoever was going to build
preferred re-reading the chat. Now the spec has **two halves**:

- **a free top**: a 1 to 3 paragraph opening and as many sections as the problem
  asks for, with the names it asks for. Architecture, when the case has any, lives
  here under a name of its own: "the seam between agent and caller" says more than
  "design".
- **a fixed set**: `decisions`, `behavior`, `tasks`, `out of scope`, `open`, in
  this order. Fixed because each one has a reader: `implement` consumes `tasks`,
  review's `contract` front walks `behavior`, the gate blocks on `open`.

One criterion separates the two halves: **the prose describes, it does not
recount.** What the thing is stays in the spec; how we got there goes into the
commit body. `## design` is gone for good, because in bb the word already means
screen design.

### The independent reviewer became a step of its own

It was a sub-bullet of a conditional step; now it is a mandatory step in every
Medium+ brief, before the gate, in fresh context and with nothing but the brief in
hand. The mandate gained the half it was missing: beyond what is missing, find
**what is redundant**, a fact repeated in three sections, prose that recounts the
conversation. The verdict shows up at the gate in one line.

### A mechanical lint, and CI running it

`lint_spec.py` (stdlib, no dependency) bars what is objective: a dead section
(`## design`, `## still open`), a table cell over 100 characters, a row with the
wrong cell count (the unescaped `|` bug), invalid frontmatter and a missing
section. No line ceiling, because size is judgment, and judgment belongs to the
reviewer. `validate.yml` runs it over every `.bb/tasks/*/spec.md`.

### A slice ready for a workflow

Every slice of `## tasks` now carries its dependency and its verification:

```
- [ ] **3. name** — what it delivers → behaviors 1,3 · dep: 2 · verifica: CI verde
```

`implement` reads `dep:` as the build order (not the order of the list) and runs the
`verifica:` before ticking the checkbox. It is the DAG that a workflow adoption
consumes without reinterpreting prose.

### `shape` left the vocabulary

A brief is a **spec**; the verb is **especificar**. In `/bb:discover` and
`/bb:brisar`, where "shaping" meant framing the problem, it became **enquadrar**.
`Finding shape` and `return shape` stay: they are a data format, another sense of
the word.

## 2.2.0 (2026-08-03)

### `/bb:review` became seven fronts you choose

`review` did too much at once: it ran the diff, the threads and CI in sequence
without asking, and what was a "project rule" stayed diluted inside the
correctness and quality lenses. Now it **detects what there is to review on this
branch and asks which fronts to run**:

| front         | what it looks for                                                                          |
| ------------- | ------------------------------------------------------------------------------------------ |
| `correctness` | bugs in the diff, across 2 to 5 named angles                                               |
| `quality`     | reuse, simplification, dead weight, efficiency, altitude, consistency                      |
| `rules`       | deviations from `CODE_REVIEW_GUIDE.md` and from the `CLAUDE.md` files that govern the diff |
| `contract`    | the brief's `## behavior` map as the acceptance contract                                   |
| `a11y`        | WCAG AA in whatever the diff touched in the UI, static, no browser                         |
| `threads`     | unresolved review comments on the PR                                                       |
| `ci`          | red checks, evidence before editing                                                        |

The question offers only the available fronts (with no open PR there is no
`threads` and no `ci`; with no brief there is no `contract`; with no UI file in the
diff there is no `a11y`), and it says the depth the diff resolved before spending
an agent.

### Parallel execution, with independent verification

The chosen fronts become a fan-out of read-only agents in a single message: they
report candidates and never edit, and the main context is the only one that writes.
Then comes the barrier: the candidates are grouped by `file:line` and each group
passes through an independent verifier that answers **CONFIRMED / PLAUSIBLE /
REFUTED**. An unverified candidate is discarded, never promoted. Every candidate
that left a finder ends up in one of four places, and the stats line closes the
account: reported, **refuted** (one line each), **without a verdict** (the
discarded one, with the location and the reason the verdict is missing) or counted
in the cap.

The size of the diff sizes the fan-out; **the content** decides which angles enter
it. A code diff runs all five. A prompt/skill/markdown diff swaps the
language-footguns angle, which has nothing to grip there, for
`instruction-integrity`: two sections that contradict each other, a pointer that
does not resolve from where it is cited, a rule in the negative that writes into
the prompt the behavior it forbids, an instruction left over from a deleted guard,
an output with no cap in a doc that caps the others, and an action offered without
a probe for its precondition. A config/manifest diff gains an angle of validity
against the format's schema. A dropped angle is named in the report with the
reason, because the reported depth is the one that ran.

The angle and verification architecture is adapted from Claude Code's
`/code-review` (Anthropic, Apache-2.0).

### A rule deviation now comes with the rule quoted

The `rules` front is the one that answers "did it follow the project's rules?".
Each finding carries **the rule's exact text** (with an ID or `path§section`) next
to **the line that breaks it**, which is what kills a hallucinated rule, because
the verifier checks the citation, not a crash. Three sources in order of
precedence: `CODE_REVIEW_GUIDE.md` (read fresh), the set of `CLAUDE.md` files that
govern the touched files (scoped by ancestor directory), and guidance comments in
the code itself. A divergence between the guide and the code becomes a separate
item pointing at `/bb:review-setup`, both a rule citing a path that no longer
exists and a **rule deviated from in 40%+ of the files it reaches**, which at that
density says more about the outdated guide than about the diff (the finding stays,
the verdict does not change, and the report offers to regenerate the rule instead
of asking for seven edits).

### The report says what passed, and you choose to fix or to comment

Two things the old plugin's generated skill did well came back. The report closes
with **what came out clean**, one line per front saying what it covered without
finding anything, and in the `rules` front a PASS/FAIL/SKIP checklist rule by rule,
with the SKIPs collapsed into one line. A silent rule now reads as checked, not as
forgotten.

And in the curation, fixing is not the only outcome: item by item you choose
between **fixing** and **commenting on the PR**, and you can mix (fix 1 to 3,
comment 4 to 6). The comment goes out anchored to the diff's line, with the rule's
citation or the WCAG criterion alongside, and only after you have seen the exact
body and approved it, because a PR comment faces outward. A finding whose location
is outside the diff (a bug on an unchanged line of a function the branch touched)
has nowhere to anchor: it goes in a summary comment with the `file:line` written in
the text, and the re-report says which ones went that way. The option only appears
when there is an open PR. The re-report now has three outcomes: `corrigido`,
`comentado` and `deixado no relatório`.

### Accessibility came in as a front, and `/bb:ui-accessibility` left

When the diff touches UI, the `a11y` front runs what can be proven from the code:
semantic role, accessible name, field label, keyboard reach, visible focus, live
region, and contrast when both colors are in the diff or resolve through the
tokens. Each finding says **who ends up blocked**, which is that front's
`failure_scenario`, and it carries a Critical/Major/Minor/Enhancement priority.

The same front runs in **surface scope**: point it at a folder, a set of files or a
running page and it audits everything, with no diff and no git repo, with the
browser resolving what the code does not settle (computed contrast, the real focus
order, what the screen reader announces, reflow at 320px). The report is grouped by
priority, with a `WCAG AA: pass | fail | partial` verdict.

With that, **`/bb:ui-accessibility` was removed**, since they were two skills
asking for the same checklist. `/bb:review` answers the same triggers ("auditoria
de acessibilidade", "WCAG", "contraste", "leitor de tela"), and the gate of
`/bb:brisar`'s Deliver now offers that audit. There are **15 skills** now.

### `/bb:ship` started using the same engine

ship had a review pass of its own, four fixed lenses, no probe, no independent
verification, and that was the one running in `/bb:delegate` and in the nightly
routine. Which means: on the path that actually puts code next to main, the repo's
`CODE_REVIEW_GUIDE.md` was not checked and accessibility did not exist.

Now ship's Step 2 **reads `/bb:review`'s references**
(`${CLAUDE_PLUGIN_ROOT}/skills/review/references/{fronts,verify,front-*,act-apply-fixes}.md`) and
runs every available front except `threads` and `ci`, which stay ship's own work.
No question and no gate: ship is a delivery path. Reading a reference is not
invoking a skill, so ship stays self-contained; what died was the second definition
of "how you review". The direct consequence: `/bb:delegate` now checks project
rules, the brief's contract and accessibility, and every finding passes through the
verifier before becoming a fix.

### SKILL.md became a router

Each front and each action became its own reference, loaded only when that front
was chosen: `references/front-{correctness,quality,rules,contract,a11y,threads,ci}.md`,
`references/fronts.md` (catalog + probe + depth), `references/verify.md`,
`references/act-apply-fixes.md`, `references/act-comment-findings.md`,
`references/mode-external-pr.md`.

In `/bb:review-setup`, the rules' `Lens` field became `Categoria`: it no longer
routes anything (the `rules` front reads every rule), it only says what kind of
concern the rule is. Guides already generated with `Lens` stay valid.

## 2.1.0 (2026-07-30)

### `/bb:ship` gained the **LexFlow** destination

Whoever builds a LexFlow app had `ship` always ending in a PR, and part of the team
does not have `gh`. Now LexFlow is a **4th destination**, next to branch / main /
PR. The destinations are exclusive: whoever wants a PR **and** a deploy runs `ship`
twice.

What the path does: it detects `lexflow.toml` at the root, runs a gate of its own,
reviews the YAML workflows with lenses that fit a declarative app, commits, pushes
the app's repo, and **hands over** `lexflow deploy --ref <sha>` with the sha that
went through the review. `ship` never deploys; the deploy mechanics stay with
`lexflow-builder`, the platform team's skill.

The gate has three layers, each with an authority of its own:

- `scripts/check_lexflow_manifest.py`: parses `lexflow.toml` through `tomllib`,
  requires `[app]`, and checks that every declared `source` (deployments,
  workflows, middlewares) points at a real file. It runs in milliseconds, with no
  network, and works logged out. With `--changed`, it maps the diff's files onto the
  deployments they affect, directly or by a reference from inside a YAML.
- `lexflow deploy --dry-run`: the authority over the manifest. `Manifest error:`
  **blocks** (it is the app's error, and it happens before any network call); a 5xx
  in the diff phase **reports** platform instability; a missing or logged-out CLI
  **skips** the check and points at `lexflow login`.
- the opcode check: `lexflow opcodes list` crossed against the touched YAMLs.

### `/bb:delegate` followed the new destination

`delegate`'s landing step asserted a draft PR for the unattended path, which does
not exist in a LexFlow repo. Now it forks by destination, and the blocker of a
stopped run lands in the brief's `## still open` when there is no PR to write it in.

### The landings were extracted into `references/`

`ship`'s `SKILL.md` became a router: the four landings now live in
`references/land-{branch,main,pr,lexflow}.md`, loaded only when that destination is
the chosen one. The `SKILL.md` went from 170 to 135 lines while carrying one more
destination.

## 2.0.0 (2026-07-23)

The `ofc` plugin (Oficina) became the **Builder Bundle** (`bb`): 28 skills from 4
sources (ofc, the brisar bundle, copies from the inspira-skills store,
inspira-code-review) consolidated into **16 skills** organized in 6 trilhas. The
repo was renamed from `inspira-legal/ofc-skills` to
`inspira-legal/builder-bundle` (GitHub redirects the old name).

### Migrating from ofc

This repo's marketplace now lists **only the `bb` plugin**: the `ofc` entry was
removed on purpose (a major break). The consequences:

- **`claude plugin update` on the old ofc fails.** That is the expected behavior:
  there is no `ofc` left to update. Migrate like this:

  ```bash
  claude plugin uninstall ofc@inspira-legal
  claude plugin marketplace add inspira-legal/builder-bundle
  claude plugin install bb@inspira-legal
  ```

- **ofc + bb coexistence works, but do not stay there.** The prefixes are distinct
  (`/ofc:` and `/bb:`), so nothing breaks, but both plugins have a `SessionStart`
  hook, so you start injecting the operating context **twice** in every session.
  Uninstall ofc first.
- **Old briefs have to be moved.** The only path read now is
  `.bb/tasks/<slug>/spec.md`; there is no fallback to `.ofc/`. Migrate with:

  ```bash
  git mv .ofc/tasks .bb/tasks
  find .bb/tasks -name shape.md -execdir git mv shape.md spec.md \;
  ```

- **The routine's env var is `BB_UNATTENDED`**: the old `OFC_UNATTENDED` is no
  longer read. Update the Cloud Routine to set the new one and run `/bb:delegate`.
- **maintain-repo's sticky comment marker changed from `ofc:` to `bb:`**:
  `/bb:maintain-repo` does not recognize the old comment and creates a new one, so
  delete the old `/ofc:maintain-repo` sticky in the triaged repo.
- **A custom skill generated by the old code-review-setup** keeps working in
  isolation in its own repo, but we recommend removing it and using `/bb:review` +
  `/bb:review-setup` (which now generates only the `CODE_REVIEW_GUIDE.md`, with no
  per-repo skill).

### Mapping: 28 skills → 16

| source              | old skill               | destination in bb                                         |
| ------------------- | ----------------------- | --------------------------------------------------------- |
| ofc                 | `frame-problem`         | `/bb:discover` (the framing phase)                        |
| ofc                 | `assess-fit`            | `/bb:discover` (the fit phase)                            |
| brisar              | `nise`                  | `/bb:discover` (discovery material)                       |
| brisar              | `esperanca`             | `/bb:discover` (hypothesis material)                      |
| store               | `desafio`               | `/bb:challenge` (renamed)                                 |
| store               | `think`                 | `/bb:think` (the base of the method)                      |
| ofc                 | `answer-yourself`       | `/bb:think` (take mode: a direct verdict)                 |
| ofc                 | `legal-lens`            | `/bb:legal-lens`                                          |
| ofc                 | `shape`                 | `/bb:spec` (the method came from here)                    |
| store               | `spec`                  | `/bb:spec` (export format in `references/export-spec.md`) |
| ofc                 | `implement`             | `/bb:implement`                                           |
| ofc                 | `ship`                  | `/bb:ship`                                                |
| ofc                 | `delegate`              | `/bb:delegate`                                            |
| ofc                 | `gather-branch-context` | `/bb:gather-branch-context`                               |
| ofc                 | `review-changes`        | `/bb:review` (the diff source)                            |
| ofc                 | `tidy`                  | `/bb:review` (the quality pass)                           |
| ofc                 | `tidy-pr`               | `/bb:review` (the threads source)                         |
| store               | `pr-review`             | `/bb:review`                                              |
| store               | `fix-ci`                | `/bb:review` (the CI source, absorbed)                    |
| ofc                 | `maintain-repo`         | `/bb:maintain-repo`                                       |
| inspira-code-review | `code-review-setup`     | `/bb:review-setup`                                        |
| inspira-code-review | `code-review-update`    | `/bb:review-setup` (update absorbed)                      |
| brisar              | `brisar`                | `/bb:brisar`                                              |
| brisar              | `tarsila`               | `/bb:brisar` (the Develop phase)                          |
| brisar              | `clarisse`              | `/bb:brisar` (the Deliver phase)                          |
| store               | `ui-accessibility`      | `/bb:review` (the `a11y` front, since 2.2.0)              |
| ofc                 | `code-deep-research`    | `/bb:code-deep-research`                                  |
| ofc                 | `write-readme`          | `/bb:write-readme`                                        |

### The bundle's architecture

- **Progressive disclosure** in every fused skill: a lean `SKILL.md` that routes;
  the material of each phase/mode lives in `references/` and loads only when the
  phase runs.
- **Handoff gates**: a skill with a natural next step ends in an
  `AskUserQuestion` that suggests the next trilha, and it suggests, never
  auto-invokes (the exception: `delegate` and the implement→ship auto-chain when
  pre-authorized). The single convention lives in
  `plugins/bb/references/handoff-gate.md`.
- **The manifesto at runtime**: `implement`, `ship`, `review` and `review-setup`
  consult `inspira-legal/manifesto` for stack decisions; without access, they
  follow the current repo's patterns and say so.
- **A review engine shared** between `ship` and `review` in
  `plugins/bb/references/` + `scripts/`: distinct roles, one engine.

The history before 2.0.0 (the `ofc` plugin up to 1.16.0) lives in this repo's git
log.
