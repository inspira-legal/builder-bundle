# The review loop: rounds, budget, stop, record

A review of the current branch runs as a loop by default. The main context is the **owner**:
it wrote or now holds the code, and it decides every verified finding alone, fixing it or
refusing it with a ground. A **reviewer** that did not write the code judges the findings in
round 1 and re-reads only what changed in every round after. The loop ends when a round
brings no Bloqueante or when the budget is spent. This file is the contract; `SKILL.md`
routes here, and `references/loop-reviewer.md` says who the reviewer is.

## When the loop runs

The loop is the default for a review of the current branch (`SKILL.md`, step 1,
"Otherwise"). The manual flow, with the fronts question and item by item curation, runs
instead when:

- the user asked for it: `/bb:review manual`, "manual review", "let me pick";
- the mode is an external PR, a surface audit, or a direct front ask;
- the current branch is the repository's default branch. The loop commits its fixes, and
  those commits belong on a feature branch;
- the working tree has uncommitted changes. A fix commit would sweep in the user's own
  work, so say in one line why the manual flow runs.

## When `/bb:implement` runs the loop

`/bb:implement` with review in its scope runs this loop on the branch before its ship (its step
11). The scope it settled at its step 2 is the authorization, so the run is the loop below with
four differences, all because the ship comes next:

- **Round 1 leaves out `threads` and `ci`**, even when a PR already exists for the branch:
  the ship answers the threads and follows CI.
- **After the last round nothing goes out**: no push, no thread replies, no CI read. The
  commits stay on the branch for the ship.
- **No gate**: the report goes back to implement, which ships next.
- **The verdict note goes to the PR description.** It opens with
  `Review loop: <N> rounds, verdict <verdict>.`, a round 1 with nothing verified included
  (`1 round, verdict clean`). `open` and `disputed` add each open Bloqueante and each
  disputed refusal (number, `file:line`, claim), and `open` says the PR is not ready to
  merge until they are settled. The outward rule of the record holds.

The probe and the intent read (`SKILL.md`, step 0) still run first, and the depth is
standard. Implement's tree is committed when it calls, so the uncommitted route above does not
apply.

## Round 1: the complete pass

1. **Every available front runs.** The step 2 question is not asked: the probe's available
   fronts are the scope, `threads` and `ci` included when the probe finds them (a run
   `/bb:implement` started leaves them out, above). Depth is
   standard unless `deep` was asked (`SKILL.md`, step 1).
2. **The finders fan out** as `references/fronts.md` describes.
3. **The loop's reviewer judges the candidates.** It takes the verifier's seat in
   `references/verify.md` §2, with the same three verdicts and the same evidence rule, and
   §4 ranks and caps what comes back.
4. **The owner decides each verified item** (below).
5. **Set the budget**: 3 rounds, or 5 when a Bloqueante of round 1 concerns security,
   permissions or data loss. Say the budget and its reason in one line.

## Rounds 2 and on: the delta

The reviewer gets, in one call:

- the diff from the head the previous round started at to `HEAD` (the owner's fixes);
- every finding still open, with its number, level and location;
- every refusal of the previous round, with its ground.

It returns three lists:

- **per open finding**: `closed` (the fix holds, quote the line) or `open` (say what is
  still wrong);
- **per refusal**: `accepted` or `contested` (say why the ground fails);
- **new findings**, only on lines the delta changed, in the finding shape of the front that
  would own them, each with its verdict and evidence.

A new finding outside the delta is not this round's: it goes to the report as out of the
loop's reach, unfixed.

## What the owner does with each item

- **Fix** it under `references/act-apply-fixes.md`: one change per commit, justified against
  the finding, behavior-preserving for quality.
- **Refuse** it with a ground the reviewer can check: the finding is wrong (quote the line
  that proves it), or it asks for work outside the branch's change or its intent (out of
  scope). Refusing is part of the job: a wrong finding fixed is a regression shipped.
- **A contested refusal**: fix it, or keep it. A kept one is **disputed** in the report and
  opens no extra round.

PLAUSIBLE items are decided like CONFIRMED ones. Sugestões are decided too, in the same
round.

## When the loop stops

- **A round brings no Bloqueante**: no new one, and none of the earlier ones still `open`
  after the reviewer's pass. Round 1's Bloqueantes, fixed, still need round 2 to close them. That round's
  Sugestões (nits, comments, docs) are decided, and no
  further round runs. Verdict `clean`, or `disputed` when a refusal stayed contested.
- **The budget is spent.** Verdict `open` when a Bloqueante is still open.
- **Round 1 has no verified finding.** The loop ends there, verdict `clean`, nothing
  committed.

## After the last round

A run `/bb:implement` started skips this section (above).

1. **Push once**, when an open PR exists, to the PR branch. With no PR the commits stay
   local and the gate offers `/bb:ship`.
2. **Thread replies** from round 1's `threads` items go out after the push, with the sha
   (`references/front-threads.md`).
3. **CI is read once** after the push (`references/front-ci.md`). Still red goes to the
   report with the evidence and opens no round.

## The record

The record has two audiences, and only one of them sees the reviewer's name.

**In the session report**, a `Loop` block before the items:

```
Loop: 2 of 3 rounds, reviewer: <reviewer name>, verdict: clean
| round | reviewer | in | fixed | refused | new Bloqueantes |
| ----- | -------- | -- | ----- | ------- | --------------- |
| 1     | ...      | 9  | 6     | 2       | 4               |
| 2     | ...      | 3  | 1     | 0       | 0               |
```

Then the refusals, one line each with the ground, and the disputed ones marked. A round
that fell back to `bb-review-verifier` names it in its row and says why in one line.

**Outward**, in commit bodies and anything posted to the PR, only the round and the verdict
appear: `Review round 2.` in a fix commit body, `Review loop: 2 rounds, verdict clean.` in a
comment the user picks at the gate. A reviewer, model or harness name stays out of
everything outward, which is how the repo's rule against AI attribution holds.

## Without an Agent tool

The loop still runs, in the main context, with a self-check in the reviewer's seat when no
outside reviewer is installed. The report says this was a loop without an independent
reviewer.
