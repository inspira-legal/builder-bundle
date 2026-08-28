---
status: done
created: 2026-08-27
slug: spec-reviewer
review: resolved
---

# bb-spec-reviewer: two lenses over the spec, and a field that proves they ran

`/bb:spec`'s step 6 spawns an independent reviewer through the generic Agent tool with the
mandate written inline (`skills/spec/SKILL.md:72`). Two things follow from that. The reviewer
inherits every tool, `Write` and `Edit` included, while being told to find what is missing in a
document it can reach; and the step itself is a promise in prose, which is the kind a busy run
skips.

This turns it into `plugins/bb/agents/bb-spec-reviewer.md`, read only by `tools:`, dispatched
twice in one message: one lens reads the spec as text, the other grounds the spec's claims
against the repo. The verdict then lands in the spec's own frontmatter as `review:`, and
`lint_spec.py` fires on a spec that closes without it, so the step stops depending on the skill
remembering to run it. It is the revisit `.bb/review-agents/spec.md` parked, conditioned on the
reviewer returning structured findings, which the two lenses are.

Success: no `.bb/<slug>/spec.md` reaches the gate unreviewed without saying so in a field a
reader and the CI can both see.

## The two lenses

One definition, two dispatches. The agent owns what does not change between lenses; the caller
names which lens this one is, the same split `bb-review-finder` already uses across fronts.

```
bb-spec-reviewer (system prompt)      | caller (prompt)
--------------------------------------|--------------------------------------
read only, never edits                | which lens: coherence or grounding
you did not write this                | the spec's full text
the finding shape and the verdict     | its path, for the grounding lens
report nothing found, plainly         | the repo root, for the grounding lens
```

**Lens A, coherence.** Gets the spec text and the instruction not to open the repo, so it reads
the way a builder with no memory of the conversation reads: what is missing, what is unmapped,
what contradicts itself, what is surplus (a fact repeated across sections, prose that recounts
the conversation instead of describing what to build).

**Lens B, grounding.** Gets the repo. It checks only the claims the spec makes about existing
code: a module or function named in `## Decisions` that does not exist, a signature the spec
states differently from the real one, a file a task names that is not there, something the repo
already does that the spec is about to rebuild. It is not a code review; a defect in code the
spec does not mention is out of its scope.

The two are dispatched together and judged together. Gating lens B on lens A finding nothing
would skip the expensive check exactly on the spec already showing signs of being sloppy.

## Decisions

- **One definition, two dispatches**: `bb-spec-reviewer.md`, the lens in the caller's prompt.
  What varies between lenses is prompt content the caller assembles, which is the repo's rule
  for naming agents by role. Cost declared: lens A's "do not open the repo" is prompt, not
  capability, and the miss it allows is a nit, not a corrupted spec.
- **`tools: ["Read", "Grep", "Glob"]`**, no `Bash`. There is no diff to resolve here, so the
  review agents' reason for carrying `Bash` does not apply, and leaving it out closes the
  `sed -i` hole those two declared as an accepted limit.
- **`model:` omitted** → it inherits the session's model. The whole value of the step is seeing
  what the author cannot, which is the last thing to make cheaper by default.
- **The finding shape is `section | what | why it matters`**, one table per lens, sharpest
  first, capped at 8 rows. It is what lets the gate render both verdicts in one line.
- **`review:` in the spec's frontmatter**, values `clean` / `resolved` / `not-run`, written by
  `/bb:spec` on finalize next to `status` / `created` / `slug`. `clean`: both lenses returned
  nothing. `resolved`: findings came back and every one was dealt with, folded into the draft,
  rejected on a stated ground, or promoted to `## Open`. `not-run`: the pass did not complete,
  whether the host had no Agent tool or a lens died. `clean` and `resolved` both assert two
  lenses ran, so a run that loses one records `not-run` and the gate names which one is gone.
  The survivor's findings still fold into the draft; what the field withholds is the claim
  that the spec got the whole pass.
- **`lint_spec.py` fires `E006`** when `review:` is missing or carries an invalid value, so the
  guarantee sits in the file and in the CI instead of in the skill's prose. What it guarantees
  is the record, not the run; a value can be written by hand. The gate is what runs it.
- **The exemption is grandfathering**: `E006` stays silent when `status: done` and the key is
  absent entirely. A spec is linted by the CI while it is still `pending`, before
  `/bb:implement` flips it, so no new spec reaches `done` past the rule. An invalid value fires
  even on a `done` spec, since that is a typo and not a legacy file.
- **`spec-state.md` documents `review:` with no inline comment**, its values in the prose
  underneath and the caution on its own line inside the block, where an author copying the
  block reads it. `check_frontmatter` compares the whole string after the first `:`, so a block
  copied with a trailing `# clean | resolved | not-run` would be read as the value and rejected.
- **A grounding finding becomes an item in `## Open`** when it invalidates a `## Decisions`
  bullet, names a file a task does not have, or points at a thing the repo already does that
  the spec is about to rebuild, and the gate already blocks on `## Open`. Those are the three
  the draft cannot absorb on its own. Everything else folds back into step 3. No new gate state.
- **The spec's text is data.** A line in the spec aimed at the reviewer gets quoted and
  attributed in the closing line, and the lens runs the mandate it was given, the same rule
  `bb-review-finder` applies to the intent block.
- **Version**: `plugin.json` `3.1.0` → `3.3.0`, and `skills/spec/SKILL.md`'s `metadata.version`
  `2.4.0` → `2.5.0`.

## Behavior

Happy path (`/bb:spec`, step 6, a Medium or Large spec):

1. The gray areas run dry and the adversarial pass closes; the lint runs over the draft.
2. The main context fires **both lenses in one message**, each `subagent_type: bb-spec-reviewer`,
   one told coherence and given the spec text, the other told grounding and given the spec plus
   the repo.
3. Each lens returns its findings in the agent's shape, or says plainly that it found nothing.
4. The barrier: findings fold back into step 3; one that invalidates a decision, misses a named
   file or rebuilds what the repo has becomes an item in `## Open`.
5. Finalize writes `review:` into the frontmatter alongside `status` / `created` / `slug`.
6. The gate renders the verdict in one line, naming each lens.

| WHEN                                           | THEN                                                                                |
| ---------------------------------------------- | ----------------------------------------------------------------------------------- |
| no Agent tool in the host                      | `review: not-run`, and the gate says the review did not run                         |
| one lens dies                                  | `review: not-run`, the survivor's findings fold in, the gate names the missing lens |
| both lenses die                                | `review: not-run`, same as a host with no Agent tool                                |
| a finding is rejected on a stated ground       | it stays out of the draft and the verdict is still `resolved`                       |
| lens B hits a decision naming a missing symbol | it becomes an item in `## Open` and the gate blocks on it                           |
| lens B finds no claim about existing code      | it reports nothing to ground, which is not a finding                                |
| the spec's text tries to direct the reviewer   | the line is quoted with its author and the lens runs its mandate                    |
| a spec finalizes with no `review:`             | `E006`, and the Validate goes red on the PR that lands it                           |
| a `status: done` spec has no `review:`         | the lint stays silent: it predates the field                                        |
| a `done` spec carries an invalid `review:`     | `E006` fires; the exemption covers absence, not a typo                              |
| a landed spec is rewritten by `/bb:spec`       | step 6 runs again and the field is rewritten with the new verdict                   |
| the lint runs in a repo that is not bb         | `E006` fires the same; there the CI is the project's, not bb's                      |
| someone adds a bb agent listing `Write`        | the Validate fails, unchanged, since `agents/**` is already CI'd                    |
| Tiny work                                      | no spec on disk, so there is nothing to lint                                        |

## Tasks

- [x] **1. The agent**: `plugins/bb/agents/bb-spec-reviewer.md`, frontmatter (`name`, a narrow
      PT-BR `description` pointing at `/bb:spec`, `tools: ["Read", "Grep", "Glob"]`, no `model`)
      and an English prompt with the invariant contract, both lenses and the finding shape
      → behaviors 2, 3, the data and no-claim rows · dep: — · verify: CI
- [x] **2. The skill dispatches and records**: `skills/spec/SKILL.md` step 6 (the
      `subagent_type`, the two lenses in one message, what each one gets, the no-Agent-tool
      path), step 7 (the verdict line, the `## Open` promotion) and **Capture the alignment**,
      where finalize learns to write `review:`
      → behaviors 1, 2, 4, 5, 6 and the no-tool, dead-lens, rejected, blocking and rewrite rows
      · dep: 1 · verify: reading
- [x] **3. The field and the lint**: `references/spec-state.md` gains `review:` in the spec's
      block, commentless, with its values in the prose; `spec-format.md` gains the `E006` row
      and its closing paragraph stops describing a single reviewer; `lint_spec.py` implements
      the code with the `status: done` exemption
      → behavior 5 and the five lint rows · dep: — · verify: the Validate's spec-lint step green
      over all 16 specs, this one included
- [x] **4. Docs and version**: `.claude/CLAUDE.md`'s tree and agent convention and `README.md`'s
      agent count gain the third agent, the bumps `3.1.0` → `3.3.0` and `2.4.0` → `2.5.0`
      → no behavior of its own · dep: 1-3 · verify: CI

Suggested PR: `feat(spec): bb-spec-reviewer, duas lentes e o campo review no frontmatter`.

## Out of scope

- **Backfilling the 15 landed specs**: the exemption covers them. _revisit_ if a `done` spec is
  reopened often enough that the escape stops being theoretical.
- **Cutting `check_frontmatter` at `#`** so any documented block survives being copied with its
  inline comment. It is one line, and it is a latent trap on `status` and `created` today, but
  it changes how every key is validated and does not belong in this PR. _revisit_ as its own
  fix.
- **The `model: sonnet` the two review agents carry** against their own spec's decision to omit
  it: real drift, but it belongs to `/bb:review`'s pipeline and to a PR of its own.
- **A verify pass over the lenses' findings**, the way `bb-review-verifier` grades the finders.
  The findings here fold into a conversation with the user, who is the verifier.
- **Enforcing that the value is honest**, i.e. that `clean` was earned. Nothing short of a hook
  reading the transcript could, and the gate showing the verdict is the check that fits.

## Open

Nothing.
