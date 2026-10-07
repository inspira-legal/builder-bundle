---
status: in-progress
created: 2026-10-07
slug: descricoes-que-ativam
---

# skill descriptions that fire on what people type

A skill's `description:` is the only text the model reads when it decides whether a request
belongs to that skill. The 15 descriptions today open with how the skill works inside
(fronts, trilha, double diamond, take mode, gate), quote their trigger phrases only in
English, and run up to 953 characters. People at Inspira ask in Portuguese, with words like
"revisa o que eu mudei" or "abre a PR", and none of those words appear. In a session with
more than 130 skills installed, five bb skills (`code-deep-research`,
`gather-branch-context`, `legal-lens`, `maintain-repo`, `write-readme`) reached the model
with their name and no description at all, so they could not fire on their own.

This change rewrites the 15 descriptions around the request instead of the mechanism, and
proves the rewrite with a battery of realistic requests that stays in the repo. Success is
the battery firing the right skill more often than today, and at least 85% of the time.

## The shape of a description

Every rewritten description follows one shape:

1. One sentence saying what the person gets, in the words a person would use to ask for it.
2. The trigger phrases: short requests the way people type them.
3. A "not for X (use /bb:Y)" line, only where a real bb neighbor competes for the same
   requests.

The target is 400 to 600 characters. How the skill works inside stays in the `SKILL.md`
body, which the model reads only after the skill fired.

## Three candidates, one winner

The language of the descriptions is decided by the battery, not upfront. Three candidates
run against the same requests:

| candidate | prose      | trigger phrases        |
| --------- | ---------- | ---------------------- |
| A         | today's    | today's (English)      |
| B         | English    | Portuguese and English |
| C         | Portuguese | Portuguese and English |

A is the baseline and never wins on its own. B keeps the `english-only` decision intact,
because a quoted request is the user's words and not the plugin's prose. C reverses
`english-only` for the descriptions only.

## The battery

About 40 requests in Portuguese and 8 in English, each one naming the skill it should fire,
or `none`. The set covers three kinds:

- **Direct requests**: at least two per skill, phrased the way a builder at Inspira would.
- **Requests between neighbors**: ones that sit between two skills that compete
  (`think` and `challenge`, `review` and `ship`, `spec` and `discover`, `brisar` and
  `spec`, `review` and Claude Code's own `/simplify` and `/code-review`).
- **Requests for no bb skill**: a typo fix, a question about a library, running the
  tests. These measure false fires.

The English requests check that a Portuguese candidate does not stop firing for people who
use bb in English through the other agents `npx skills` installs it on.

## Decisions

- **Scope is the 15 `description:` fields.** The agents' descriptions, the README's skills
  table and the two manifests stay as they are.
- **Every description follows the shape above** and stays a plain YAML scalar: no `: `,
  no ` #`, no `<` or `>`, no dash, at most 1024 characters.
- **A "not for" line names only bb neighbors.** A trigger phrase that is another installed
  skill's own name or job (today's "simplify the diff" in `review`) is dropped.
- **The battery decides the language.** The winner is the candidate with the most hits.
  Between B and C, a difference of two hits or less is a tie, and a tie goes to B, because
  B does not reverse a decision someone else made.
- **The winner has to beat A and reach 85%.** Below that, one adjustment round rewrites
  the descriptions of the skills whose requests missed, and the battery runs again. Still
  below after that round, nothing lands and the result is reported.
- **C winning reverses `english-only` for the descriptions alone.** The rest of the bundle
  stays English, and the result goes to athena, who made that decision, before the change
  lands.
- **The expected skill of every request is fixed before any candidate runs**, so the
  battery cannot be tuned to the candidate that ends up winning.
- **Each request runs three times**, and it counts as a hit when at least two of the three
  runs fire the expected skill.
- **The battery measures the choice, not the work.** A run stops at the first skill the
  model picks, or at its first answer when it picks none.
- **The result does not depend on the machine that runs it.** A run loads the bb copy
  under test and Claude Code's built-in skills, and nothing else installed on the machine.
- **The battery stays in the repo and runs by hand.** It costs money on every run and
  needs a signed-in Claude, so it stays out of CI. Its result stays on the machine that
  ran it, and the score table goes into the commit body.
- **The version goes up one minor**, with a `CHANGELOG.md` entry that carries the score of
  each candidate.

## Behavior

Happy path:

1. The battery runs candidate A, today's descriptions, and prints the score, the misses by
   skill, and what the run cost.
2. Candidates B and C are written for all 15 skills, each in its own copy of the plugin,
   with the `SKILL.md` files of the working tree untouched.
3. The battery runs B and C over the same requests.
4. The winner is picked by the rule in `## Decisions`.
5. The winner's 15 descriptions land in the `SKILL.md` files, and the frontmatter check
   passes.
6. The score table of the three candidates goes into the commit body and the
   `CHANGELOG.md` entry.

| #   | edge                                                              | outcome                                                 |
| --- | ----------------------------------------------------------------- | ------------------------------------------------------- |
| 1   | WHEN a description passes 1024 characters or carries `<` or `>`   | THEN the frontmatter check fails the build              |
| 2   | WHEN B and C differ by two hits or less                           | THEN B wins                                             |
| 3   | WHEN the best of B and C scores at or below A                     | THEN nothing lands, and the result is reported          |
| 4   | WHEN the best candidate beats A but stays under 85%               | THEN one adjustment round on the skills that missed     |
| 5   | WHEN it is still under 85% after the adjustment round             | THEN nothing lands, and the result is reported          |
| 6   | WHEN a request fires a non bb skill where a bb skill was expected | THEN that run is a miss                                 |
| 7   | WHEN a request expected to fire nothing fires a bb skill          | THEN that run is a miss, counted as a false fire        |
| 8   | WHEN a run fails or times out                                     | THEN it runs once more; failing again, it is a miss     |
| 9   | WHEN a run is about to pass the cost ceiling given to the battery | THEN the battery stops and prints the partial result    |
| 10  | WHEN C wins                                                       | THEN the result goes to athena before the change lands  |
| 11  | WHEN an English request misses under C and hits under B           | THEN it shows in the misses by skill, marked as English |

## Metric

- Metric: the share of battery requests whose majority of three runs fires the expected
  skill, or no bb skill where none is expected
- Baseline: skipped: not-instrumented (the battery's first run, over candidate A, measures it)
- Target: at least 85% and above the baseline, within this change (Leo's call in the spec
  conversation, 2026-10-07)
- Events: none, this is repo tooling with no user-triggered product behavior

## Attention points

- A headless `claude -p --plugin-dir` run also loads the machine's other plugins and user
  skills, and the published bb from the marketplace may load beside the working copy, so
  the listing a run sees can hold two copies of every bb skill.
- Every headless session runs `plugins/bb/hooks/sync_instructions.py`, which rewrites
  `~/.claude/BUILDER-BUNDLE.md` with the copy under test.
- The skill choice happens in the model's first turn. A run allowed to go on executes the
  skill, which costs many times more, and for `ship` or `implement` can act on the
  directory the run sits in.
- `claude plugin eval` reads exactly this kind of battery, but it is in early access and
  closed for this account today.
- The repo's own tooling under `.github/scripts/` is bun and TypeScript.
- Portuguese prose reaches for `: ` often, and an unquoted `description:` breaks on it.
- The same request can fire different skills on different runs of the same model.

## Tasks

### The runner

- [ ] **1. The battery runner**: takes a plugin copy and a requests file, runs each request
      three times, stops each run at the first skill choice, loads nothing but the copy
      under test and the built-in skills, takes a cost ceiling, and prints the score, the
      misses by skill (English requests marked) and the cost. · verify: a run over two
      sample requests

### Requests and candidates

- [ ] **2. The requests**: about 40 Portuguese and 8 English requests, each with its
      expected skill or `none`, covering direct requests, requests between neighbors and
      requests for no bb skill. · verify: reading
- [ ] **3. Candidate B**: the 15 descriptions in English prose with Portuguese and English
      trigger phrases, in their own plugin copy, following the shape. · verify: the
      frontmatter check over the copy
- [ ] **4. Candidate C**: the 15 descriptions in Portuguese, trigger phrases in Portuguese
      and English, in their own plugin copy, following the shape. · verify: the
      frontmatter check over the copy

### Measure

- [ ] **5. The three runs and the winner**: the battery over A, B and C, the winner picked
      by the rule, and the one adjustment round when the rule calls for it. · verify: the
      score table

### Land

- [ ] **6. The winner lands**: its 15 descriptions in the `SKILL.md` files, the minor
      version, and the `CHANGELOG.md` entry with the score table. · verify: CI

## Out of scope

- The agents' descriptions, the README's skills table and the two manifests.
- Running the battery in CI.
- Reverting `english-only` anywhere beyond the 15 descriptions.
- Removing the old copies of `spec`, `brisar`, `desafio` and `nise` that people keep
  installed beside bb. _revisit_: `/bb:profile` could spot them.
- Moving the battery onto `claude plugin eval` once it opens. _revisit_

## Open

Nothing.
