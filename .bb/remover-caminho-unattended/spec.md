---
status: done
created: 2026-08-11
slug: remover-caminho-unattended
---

# removing the unattended path from bb

Take the whole unsupervised path out of the `bb` plugin: the `BB_UNATTENDED` env var, the
addendum it injects, the Cloud Routines guide, the routine scaffold, `maintain-repo`'s two own
routines, and every conditional "unattended" branch spread across the skills. After that the
bundle has a single mode, supervised, with a human in the session.

The path **never ran**. There is no Cloud Routine configured on the GitHub/Anthropic side, and
there never was. That changes what is being deleted: it is not working code, it is speculative
design. Every claim in `hooks/unattended-context.md`, in `land-pr.md`'s unattended watch and in
implement's retry caps is behavior no run ever exercised: written, reviewed, versioned, never
verified by anything.

What it charges in return is expensive and visible: the debate over where the blocker shows up
(the PR description versus `## open` on a pushed branch), the ship running over an incomplete
tree, a parallel rule in `build-mode.md`, a security provisioning section in `routines.md`, and
an "Unattended:" sentence in almost every step of the trio.

## The measured surface

`rg -i 'BB_UNATTENDED|unattended|routine|AFK'` in `plugins/bb/` matches **142 lines across 22
files**. They split into two uneven groups:

- **4 files die whole**: `hooks/unattended-context.md` (5), `references/routines.md` (25),
  `references/scripts/scaffold_routine.py` (13) and
  `skills/maintain-repo/references/routines-setup.md` (22). That is 65 of the 142.
- **18 files get edited**: the remaining 77. The per file count sits in each slice; it is the
  inventory the build consumes, because a line number changes during the edit and a count does
  not.

Outside `plugins/bb/` there are `README.md` (2) and `.claude/CLAUDE.md` (8). `CHANGELOG.md` and
the old briefs in `.bb/tasks/` also match, and they stay: they are history.

**The `-i` is not a detail.** `rg` is case sensitive by default, and a good part of the
occurrences are capitalized: `## Unattended`, `**Unattended:**`, `Cloud Routine`, `Routine A`. A
sweep without `-i` comes back green over a plugin that is still dirty. Every `verify:` in this
brief uses `-i`, and so does the success criterion.

Success: `rg -i 'BB_UNATTENDED|unattended|routine|AFK'` returns zero in `plugins/bb/`,
`README.md` and `.claude/CLAUDE.md`, and no skill references a deleted file.

## Decisions

- **Reuse:** nothing new gets written. The removal is subtractive; where a sentence is left
  incomplete, it gets shortened, not replaced by new prose. It follows the rule in the user's
  `CLAUDE.md`, remove before you negate: nowhere does "there is no unattended mode" enter.
- **The never-merge guarantee through capability scoping dies with it.** With no routine there
  is no token to scope. The never-merge that stays is the skill's own ("ship never merges,
  never approves, never force pushes") plus the repo's branch protection, which is a fact of
  the repo and not of bb. Every "enforced by capability scoping on the unattended path" clause
  becomes just the hard line.
- **`hooks/enter_worktree.py` stays, and there are three spots, not two.** It is worktree
  isolation for a local run and a parallel task, and its own docstring says a routine does
  _not_ need it. That note is a comparison against a thing that stops existing: the whole
  `NOTE:` paragraph goes (it also points at the table row slice 1 deletes), and `unattended`
  leaves two more comments. No logic changes.
- **The `claude -p` / Agent SDK fact survives in `build-slices-workflow.md`.** The bullet today
  is titled "Out-of-allowlist commands don't prompt **in a routine**", but the condition the
  next sentence itself states is `claude -p` and the Agent SDK, which is how the slice agents
  run even in a supervised session. The routine framing leaves the bullet title; the fact and
  the stage zero it justifies stay standing.
- **`hooks/scheduling-decision.md` stays, without the Cloud Routine row, and without one
  column.** The table stays useful for the five remaining mechanisms (`/loop`, a Desktop task,
  Channels, `/goal`, Monitor). What goes: the row, the two "How to pick" bullets that point at
  it, and the opening sentence promising to solve the AFK overnight job. The
  **`Survives laptop closed?`** column goes too, since without the Cloud Routine it reads `No`
  in all five rows, and a single value column informs nothing.
- **The inconsistency in implement's step 4 closes by deletion, not by new text.** The passage
  telling it to chain `/bb:ship` on an incomplete build sits entirely inside the
  "**Unattended:**" prefix. Delete the prefix and the contradiction with delegate's step 4
  goes, and the rule that remains is already the right one: step 8, "not clean → don't offer
  ship".
- **Stage zero and workflow mode stay.** Neither depends on a routine: the green baseline is
  independent, and the allowlist is an SDK question (above).
- **The CHANGELOG and the old briefs in `.bb/tasks/` are not rewritten**: they are history, and
  they stay outside the scope of every sweep. Only a new CHANGELOG entry goes in.
- **`references/scripts/` goes along with `scaffold_routine.py`**: it is the only file there.
- **Version:** `plugin.json` goes to `2.8.0` and the **8 touched skills** take a
  `metadata.version` bump (delegate, implement, ship, review, review-setup, discover, spec,
  maintain-repo, and no other). Removing documented behavior is a behavior change, including
  when it is only one edge case line.
- **The gate runs in CI only.** `bun run fmt:check`, `validate-frontmatter.ts` and
  `lint_spec.py` run on the PR. Each slice's `verify:` is `rg -i -c` over its own scope
  returning zero, a search and not a build.

## Behavior

1. Any session in a repo with the plugin enabled: `inject_operating_context.py` reads
   `operating-context.md` and injects it, with no conditional branch. `BB_UNATTENDED=1` in the
   environment produces no effect at all, because the var is no longer read.
2. `enter_worktree.py` keeps creating an isolated worktree for a local or autonomous run and
   keeps refusing a protected branch; none of its comments cite a routine.
3. `/bb:delegate <slug>`: it resolves the brief, flips `in-progress`, asks the build mode
   (always), builds, runs the ship, lands, flips `done`. No step and no edge case line has an
   unattended variant.
4. `/bb:implement` invoked directly: it asks the build mode, and with the gate breaking
   unrecoverably it commits what is green, reports done/skipped/blocked and **does not offer
   the ship**.
5. `/bb:ship`: Step 1 always resolves the destination by signal or by asking. There is no fixed
   destination, no automatic draft PR, no comment round cap, no AFK watch.
6. Every skill with a natural next step ends at the handoff gate. No exception is left that
   skips the question and takes the documented lean on its own.
7. `/bb:maintain-repo`: it runs supervised end to end, phases 1 to 4, the digest in Slack
   through the session's MCP tools, the merge in a human's hands. No provisioning prerequisite.
8. Whoever looks for how to run overnight opens `scheduling-decision.md`, finds five mechanisms
   compared, and none of them survives a closed laptop.
9. `review`, `review-setup`, `discover` and `spec` lose the mentions they carried; their
   supervised behavior does not change at all.
10. The README, `.claude/CLAUDE.md` and `plugin.json`'s `description` describe the bundle
    without the path; `2.8.0`, the skill bumps and one CHANGELOG entry record the removal.
11. The set's `rg -i` returns zero in `plugins/`, `README.md` and `.claude/CLAUDE.md`, and no
    reference points at a deleted file.

| WHEN                                                 | THEN                                                                                        |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `BB_UNATTENDED=1` set after the removal              | nothing happens; the session runs supervised as usual                                       |
| the sweep runs without `-i`                          | it passes green over a dirty plugin: `Unattended:` and `Cloud Routine` escape               |
| `unattended-context.md` goes but the `if` stays      | the hook injects an empty block, which is why the `if` and the helper go in the same commit |
| some skill still points at a deleted file            | CI does not catch it; slice 7's sweep is what catches it                                    |
| the "Survives laptop closed?" column holds only `No` | the column goes; a single value informs nothing                                             |
| the allowlist bullet loses the routine framing       | the `claude -p` / SDK fact stays; stage zero is still justified                             |
| `enter_worktree.py`'s `NOTE:` compares to a routine  | the whole paragraph goes; the file's logic does not change                                  |
| implement's step 4, an unrecoverable gate            | the unattended paragraph goes; step 8's rule already covers it, with no new text            |
| `plugin.json` loses the capability scoping clause    | never-merge stays asserted as a hard line in ship and delegate                              |
| `maintain-repo` loses its two own routines           | the whole supervised path remains; the provisioning prerequisite goes                       |
| the CHANGELOG and old `.bb/tasks/` cite unattended   | they stay; they are outside the scope of every sweep                                        |
| CI does not fire on a PR touching only `references/` | this PR touches 8 `SKILL.md`, so it fires; the trigger does not change                      |
| a half sentence is left after a clause is removed    | shorten the sentence; no new prose explaining the absence enters                            |

## Tasks

- [x] **1. hooks**: delete `unattended-context.md` (5); remove the `if`, the helper and the
      constant from `inject_operating_context.py` (7); the capability scoping clause from
      `operating-context.md` (1); the `NOTE:` paragraph and two comments from
      `enter_worktree.py` (3); the Cloud Routine row, the "Survives laptop closed?" column, the
      two AFK bullets and the opening sentence of `scheduling-decision.md` (5)
      → behaviors 1, 2, 8 · dep: — · verify: `rg -i -c` in `hooks/` returns zero
- [x] **2. plugin root references**: delete `routines.md` (25) and all of `scripts/` (13); in
      `build-mode.md` (6) the `## Unattended` section, the sentence "won't survive an unattended
      run either" and the report line; in `build-slices-workflow.md` (4) the routine framing in
      the allowlist bullet, the pointer at the top, the retry cap and the branch; in
      `handoff-gate.md` (3) the "unattended runs never gate" rule and the auto-chain clause
      → behaviors 4, 6 · dep: — · verify: `rg -i -c` in `references/` returns zero
- [x] **3. the trio**: `delegate` (15: the description, the opening, steps 1 to 6, three edge
      case lines, the closing), `implement` (7: the description, the opening, steps 3/4/6/7/8,
      where 4 closes by deletion and 7 points at `routines.md`), `ship` (2: the Step 1 paragraph
      and the bundled resource line) and `land-pr.md` (6: `--draft`, a thread with no pause, the
      round cap, "not an AFK agent", the Channel/routine pointer and the unattended watch)
      → behaviors 3, 4, 5 · dep: 1, 2 · verify: `rg -i -c` in the three skills returns zero
- [x] **4. peripheral skills**: `review` (3: the fan out, the curation, an edge case line),
      `mode-external-pr.md` (1: the report only paragraph), `review-setup` (1) and `discover`
      (1), one edge case line each; `spec` (3: the reload mention, the "same verb as the
      routine" in Delegar and the guide pointer in "Encerrar aqui")
      → behavior 9 · dep: — · verify: `rg -i -c` in the five skills returns zero
- [x] **5. maintain-repo**: delete `references/routines-setup.md` (22); in the `SKILL.md` (8)
      the "runs two ways" framing, the provisioning prerequisite, the never-merge by capability
      bullet, the delivery through the Slack connector, the bundled resource entry and the
      `### Safety model` section
      → behavior 7 · dep: — · verify: `rg -i -c` in the skill returns zero
- [x] **6. repo docs and version**: `README.md` (2: the `/bb:delegate` row in the table and the
      "rodar sem supervisão" section); `.claude/CLAUDE.md` (8: the claim at the top, four tree
      lines including the `scheduling-decision.md` comment, which stays, and the hooks note);
      `plugin.json`'s `description` and `2.8.0`; the `metadata.version` of the 8 skills; a
      CHANGELOG entry
      → behavior 10 · dep: 3, 4, 5 · verify: `rg -i -c` in `README.md` and `.claude/` zero
- [x] **7. the sweep**: the set's `rg -i` in `plugins/`, `README.md` and `.claude/` returns
      zero, and `rg -i 'routines(-setup)?\.md|scaffold_routine|unattended-context'` over the
      whole repo matches only in `CHANGELOG.md` and `.bb/`; the PR green
      → behavior 11 · dep: 1-6 · verify: CI

## Out of scope

- **A CI guard against regression.** A job that fails if `BB_UNATTENDED` reappears is permanent
  weight for a one time removal.
- **Rewriting the CHANGELOG and the old briefs.** History stays.
- **Touching stage zero, workflow mode or `enter_worktree.py`'s logic.**
- **Reassessing whether `/bb:delegate` still justifies itself as a verb.** It survives: it is
  the "yes" to implement's gate given in advance. Only the description and the opening get
  rewritten.
- **The conventions note not surviving a resume**: a real finding from build-via-workflow, and a
  brief of its own.

## Open

Nothing open.
