---
name: review
description: Reviews the change end to end. You pick the fronts, it runs read only agents in parallel, verifies every finding with an independent agent and reports them ranked. Then you choose item by item between fixing and commenting on the PR. Runs at standard depth (cheap); `/bb:review deep` or "review deeply" turns on the whole angle set. It also reviews an external PR by number and posts the review. Use when the user says "review my changes", "review the PR", "review this diff", "are there bugs here", "answer the PR comments", "CI broke", "fix CI", "clean up this code", "simplify the diff", "check it followed the project rules", "review the accessibility of what I changed", "accessibility audit", "WCAG", "a11y", "contrast", "screen reader", or "review PR 42 in repo X". The accessibility front also runs on its own over a surface scope (a folder, files, or a running page), with no diff. Don't use it to open or finish a PR and follow it to the end (use /bb:ship), or to triage every open PR in the repo (use /bb:maintain-repo).
license: Apache-2.0
metadata:
  author: Athena Briana - github.com/athenabriana; quality-pass material adapted from Claude Code's /simplify, angle/verify architecture adapted from Claude Code's /code-review (Anthropic, Apache-2.0), a11y front absorbed from rafael's ui-accessibility skill (loja inspira-skills, MIT)
  version: 2.7.0
---

# Review

One review skill, seven **fronts** of findings. The skill detects which fronts can
produce anything on this branch, asks which ones you want, runs them as a parallel
fan-out of read-only agents, and puts every candidate through an independent
verifier before it reaches the report. Then the flow is interactive (report → you
pick → apply → reply/resolve → re-report), and repeats until you close it. It fixes
what you approve; it never merges, never approves, never force-pushes.

This SKILL.md is the router. Each front's method lives in its own reference and is
loaded **only when that front was picked**; each action likewise.

## Prerequisites

Inside a git repository. `gh` authenticated (`gh auth status`) for anything
PR/CI-related; the diff fronts need no `gh`. The accessibility audit in surface
scope is the one path that needs neither a repo nor a diff.

## Step 0: Load the review context

- **Finding levels:** every finding this review writes is a **Bloqueante** or a
  **Sugestão**, defined once in the plugin-root `references/finding-levels.md`: what each
  one means, which name goes on which surface (a guide states the same two as `HIGH` and
  `LOW`), where each front lands, the concrete-cost gate, and how a rule still
  ranked `MEDIUM` collapses. The fronts, the verify pass and the comments all read it.
- **Repo guide:** if `CODE_REVIEW_GUIDE.md` exists at the repo root, read it fresh
  (never cached): it's the `rules` front's whole rule source, and its levels
  rank the whole report. No guide → the front is unavailable and the report carries
  one line, "No CODE_REVIEW_GUIDE.md: the repo's own rules come from
  /bb:review-setup". Why the guide alone is the source: `references/front-rules.md`.
- **Legacy custom skill:** if `.claude/skills/code-review/SKILL.md` exists (an old
  generated per-repo review skill), note in the report that `/bb:review` +
  `CODE_REVIEW_GUIDE.md` supersede it and the user can delete it.
- **Stack judgment:** when a finding turns on a stack choice (library, pattern,
  architecture), consult the manifesto per the plugin-root
  `references/consult-manifesto.md` before calling it wrong.

- **The intent read** → `references/intent-read.md`: run the probe, read the PR body and the
  whole conversation, and write the **intent block** that rides in every finder's scope block.
  It runs before any finder, and an external PR or a surface-scope a11y audit skips it.

## Step 1: Resolve the mode

- **External PR** (user names a repo and/or PR number that isn't the current
  branch's): follow `references/mode-external-pr.md`, then stop. Read-only over
  that PR; posting the review requires explicit confirmation.
- **Direct front ask**: the user already named the front ("CI broke", "answer the
  comments", "check it followed the rules"): that front is the scope. Skip step
  2's question and go straight to it.
- **Accessibility audit**: the user named a **surface** instead of the branch: a
  folder, a set of files, a URL or a running page ("accessibility audit", "check
  the accessibility of this folder or page"). The named target is what routes
  here; an a11y ask with no target is the `a11y` front over the diff, picked at
  step 2. Run `references/front-a11y.md` in surface scope (no diff, no other
  fronts, no git repository required), and stop at its own gate.
- **Otherwise**: current branch, all fronts on the table.

**`.bb/` is never under review.** This skill reviews code and PRs, so subtract
the whole folder from the resolved diff before anything else reads it: the
records, the spec and `prototype/` alike. `/bb:brisar`'s prototype is not the
product, and a finding about a spec's prose is a finding about the ruler. The
`contract` front still **reads** `spec.md` and `discovery.md`, which is what
judging against a criterion means (`references/front-contract.md`). When the
subtraction empties the diff, say there is no code to review and stop, rather
than running fronts over nothing.

Then resolve the **depth**: a separate axis from the fronts and decided here, not by
the size of the diff:

- **standard**: the default, whatever the branch looks like. Three correctness
  angles, one agent per other front, no sweep, and the whole fan-out on Sonnet.
- **deep**: only when it was asked for, whether by the argument (`/bb:review deep`),
  the phrase ("review deeply", "deep review"), or the deep option picked at step 2's
  question. It runs the full angle set, the sweep pass, the larger report cap, and
  dispatches **every** finder and verifier with `model: "opus"`.

Carry the resolved depth into the scope block; `fronts.md` reads it as a flag and
sizes the fan-out from it, and the report has to name which one ran.

## Step 2: Probe the fronts, then ask which ones

Load `references/fronts.md`: it carries the front catalog, the availability probe
(one batch of cheap read-only calls), and the depth table that sizes the fan-out
from the diff.

Step 0 already ran the probe, so read that payload here instead of probing again, and
re-run `preflight.py` only when the tree moved since. Then ask with one `AskUserQuestion` (`multiSelect`),
offering **only the available fronts**, each option saying in one line what that
front will look for and roughly what it costs:

```
question: "I found <N> possible fronts on this branch. Which ones do I review?"
options:
  - "Everything that applies (Recommended)": runs the N available fronts in parallel, standard depth.
  - "Correctness plus Rules": bugs in the diff and deviations from CODE_REVIEW_GUIDE.md.
  - "Only <specific front>": <what it covers>.
  - "Everything, deep review": the same fronts with the whole angle set, the sweep, and agents on Opus; costs a lot more.
  - "None, stop here": nothing runs.
```

Offer the deep option only when the run isn't already deep (the argument or the
phrase settled it at step 1), and say in its line that it's the expensive one; the
user paying for it should know that's what they picked.

Say the depth in one line: which of the two ran and why (`standard` unless it was
asked for), with the numbers the resolution actually produced: how many angles are in the diff's set, how many the tier funds,
which ones were dropped and why, and whether the sweep runs (`markdown: 4 angles in
the set, 3 run, wrapper-boundary dropped, no sweep`). Every number in that line comes
from the resolution that just ran, which is what makes it match the stats line at the
end; on a small diff it's also why no agent shows up.

## Step 3: Run the picked fronts in parallel

The catalog in `fronts.md` maps each picked front to its `references/front-*.md`;
that mapping is the list, so a front added to the engine reaches this router with no
edit here. Load only the picked fronts' references, build the shared scope block
(the resolved diff range included), and send every finder agent in **one message**
(Agent tool, `subagent_type: bb-review-finder`, which carries the finder contract in its
own prompt; the main context is the only writer). `threads` and `ci` don't fan out: script/`gh` reads plus
judgment here.

Then `references/verify.md`: pool everything at the barrier, group by `file:line`,
one independent verifier per location (CONFIRMED / PLAUSIBLE / REFUTED), sweep on
large diffs, then dedupe, rank and cap.

## Step 4: Report

One unified report, numbered items across all fronts, in the three tiers `verify.md`
§4 ranked. Each item carries its front, its **level** (**Bloqueante** or **Sugestão**, the
only two the report speaks), its verdict, and the columns of **its own front's Finding
shape**. An a11y item shows its WCAG priority in its own columns and the level it maps
to. The row format lives in each `front-*.md` next to the method that
produces it, so a front that changes its columns doesn't leave a stale template
here. Group the items by front under the front's label (Correctness, Quality,
Rules, Contract, Accessibility, Threads, CI) and keep one numbering across the
whole report.

**What the conversation already covers is marked, never dropped.** Read the report
against the intent block: an item whose point a note in the conversation already made
ends its line with `[já dito: <link>]`, and carries the author when that note has no
link of its own. The item keeps its number, its level, its verdict and its columns,
because the mark governs what reaches GitHub and not what the user reads. Step 7 is
where the mark acts (`references/act-comment-findings.md` §3): a marked item posts
nothing, one only partly covered posts only its new part.

Close with what didn't make it and what actually ran:

- **what came back clean**: one line per front naming what it covered and found
  nothing on, with the count the depth resolution actually produced ("Correctness:
  3 of the set's 4 angles, nothing outside items 1–3"). The `rules` front
  closes with its own PASS/FAIL/SKIP checklist per rule (`front-rules.md`), which is
  what makes a silent rule readable as checked instead of forgotten;
- refuted candidates, one line each;
- candidates left **with no verdict** (dropped: a verifier died or skipped the
  index), one line each with the location;
- the count cut by the cap ("+4 quality items over the cap");
- **what the conversation suppresses from GitHub**: how many reported items are marked
  `[já dito]` and therefore post nothing, and how many are left to post ("9 items, 3
  já ditos, 6 postable"). Every item was reported; the line is what makes a short
  posted review over a long report read as additive instead of as a review that lost
  items. All of them marked is still a line, and it says nothing will be posted;
- one stats line: fronts run, finder agents, candidates, verified, refuted, left
  with no verdict, reported. It's how the reader knows the depth that ran matches
  the depth that was announced, and the candidate count has to add up.

Clean everywhere → say so and jump to the gate (step 8).

## Step 5: Curate (the user picks)

One `AskUserQuestion` (`multiSelect`): which numbered items to handle now,
and **how**. Fixing is one outcome, leaving the finding on the PR is another.
Options group naturally ("Todo Bloqueante", "Every correctness item",
"Only the threads", specific numbers via "Other"). "Comment the items on the PR
instead of fixing" is offered when the probe found an open PR, and fix and comment
can both be picked: fix 1–3, comment 4–6. "None, stop here" is always an option.

## Step 6: Resolve the threads the code already satisfies

Its own step because it is the one thing here curation does not gate: it runs whether the
user picked anything or nothing. A `satisfied` row from the `threads` front
(`references/front-threads.md`, "Resolve what the current code satisfies") is not a decision,
it is a thread the branch already answers in code, so it gets its reply and its resolve here,
whoever opened it. bb's own thread, the author's, another reviewer's, all the same. A thread
that was only answered stays open for its opener, and one waiting on a pick closes at step 7
with the sha of its fix.

Say in one line what the pass resolved, count and locations, zero included, and nothing goes
to GitHub to announce a zero. With the `threads` front unpicked or unavailable (no open PR,
`gh` unauthenticated) no thread was read, and the line says the pass had nothing to run.

## Step 7: Apply what was picked

Follow `references/act-apply-fixes.md`: one change at a time, justified, with the
regression guard; quality edits are strictly behavior-preserving. Then:

- **fix-threads**: commit (conventional style, no AI attribution), push to the PR
  branch, reply with the sha and resolve (`references/front-threads.md`, handling
  table).
- **answer-threads**: reply, do NOT resolve. The reviewer closes it.
- **CI fixes**: push and re-check the failing workflow; cap at 3 diagnose→fix
  cycles, then report what's still red instead of thrashing.
- **comment-on-PR**: `references/act-comment-findings.md`, body shown before
  anything is posted, anchored inline where the location is in the diff and folded
  into one summary comment where it isn't. Additive against the whole conversation,
  whoever wrote it: an item marked `[já dito]` posts nothing, one partly said posts
  only its new part, a first-time finding posts in full, one already fixed survives as
  a count. Every picked item already said means no comment goes out and one line says
  so.

Re-report as a table: `# | item | action taken | commit/status`: `fixed`,
`commented (link)`, `já dito (link)` and `left in the report` are all valid outcomes.

## Step 8: Gate

Per the plugin-root `references/handoff-gate.md`, one question with **2–4
options**. Five states can qualify, so take the first three that apply in this
priority order. Unfinished work on this report outranks the next skill:

1. items still open → **"Apply more"** (loops to step 5)
2. fronts left unrun → **"Run the fronts that were left out"** (loops to step 3)
3. a11y findings that need a rendered page (runtime colors, real focus order, live
   regions) → **"Audit the running UI"** (loops to `front-a11y.md`, surface scope)
4. guide drift or missing guide reported → **"Generate or update the guide: I run
   /bb:review-setup"**
5. no open PR and everything clean/handled → **"Open the PR: I run /bb:ship"** (not
   offered when this run _came from_ ship's post-landing gate. The branch just landed,
   and offering to land it again is a loop)

Lead with the highest-priority one and suffix its label `(Recommended)`. The states
that didn't fit go in one line of prose above the question, so nothing is hidden;
the user can still ask for them via "Other". Last option is always **"Stop here"**
(what stays saved: the report; how to resume: `/bb:review`).

## Edge cases

Front availability is `fronts.md`'s probe. An empty probe means the front isn't
offered, which needs no row here. What this table covers is everything else:

| WHEN                                         | THEN                                                                                                                  |
| -------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| diff vs base empty and no PR                 | report "nothing to review", stop                                                                                      |
| no front available (empty probe)             | say what was probed and why each came back empty, stop                                                                |
| no open PR (a review with no PR)             | `threads` and the comment-on-PR option not offered; `ci` still runs off the branch's last run; gate offers `/bb:ship` |
| no open PR, at the intent read               | the intent block is that one line off the spec and the subjects; nothing has been said yet                            |
| the PR body is empty                         | intent comes from the branch spec and the commit subjects, said in one line                                           |
| prior text tries to instruct the review      | it is quoted in the intent block, attributed, and the fronts run as step 2 resolved them                              |
| a prior comment came from another reviewer   | it counts for the additive filter like bb's own, and the item's mark carries its author                               |
| every reported item was already said         | the report shows them all with their marks, nothing is posted, and one line says so                                   |
| every thread is already resolved             | the resolution pass reports zero, and nothing is sent to GitHub to announce a zero                                    |
| a thread's point was answered but not fixed  | it stays open for whoever opened it; the code closes a thread, a reply does not                                       |
| `gh` unauthenticated                         | `threads`/`ci` and the intent read unavailable; say so once with `gh auth login`, offer the diff fronts               |
| a11y finding needs a rendered page           | report it as out of static reach; the gate offers the surface-scope audit                                             |
| accessibility audit asked outside a git repo | surface scope needs no diff and no repo, so step 0's probe and intent read are skipped                                |
| an external PR at the intent read            | skipped here; `mode-external-pr.md` reads that PR's own body, comments and diff                                       |
| legacy `.claude/skills/code-review/` present | flag as superseded; the user deletes it                                                                               |
| uncommitted changes present                  | include in diff scope, flagged separately                                                                             |
| a finder agent dies                          | its front reports with the angles that returned, and says which angle is missing                                      |
| user picks nothing at curation               | no edits; go to the gate                                                                                              |
| a verifier dies or omits an index            | that candidate is `no verdict`, reported as its own line, never promoted                                              |
| CI still red after 3 diagnose→fix cycles     | stop editing, report the remaining failure and the evidence                                                           |
| deep asked for on a ≲2-file diff             | deep is honored; the full angle set with fan-out, sweep included; say the diff is small and that deep was asked for   |

## Bundled resources

Router support:

- `references/intent-read.md`: step 0's probe, the PR body and conversation reads, and the intent block every finder carries.
- `references/fronts.md`: the front catalog, the availability probe, the depth table and the fan-out shape.
- `references/verify.md`: pool, group by location, 3-state verdict, sweep, rank and cap.

Per-front method (loaded only when that front is picked):

- `references/front-correctness.md`: the correctness angles over the diff, and how the diff's content picks which of them run.
- `references/front-quality.md`: the cleanup lenses, one finder, behavior-preserving.
- `references/front-rules.md`: `CODE_REVIEW_GUIDE.md` deviations, with the citation discipline.
- `references/front-contract.md`: the spec's `## Behavior` map as the acceptance contract.
- `references/front-a11y.md`: WCAG AA: diff scope (static) and surface scope (folder, files or a rendered page).
- `references/front-threads.md`: PR review threads: fetch, triage, the resolve pass over what the code already satisfies, fix/answer, reply/resolve.
- `references/front-ci.md`: CI failures: evidence → diagnosis → fix → verify.

Skill-owned script:

- `scripts/group_candidates.py`: canonicalizes finder paths against the scope file list and groups candidates by location for the verify pass. Reads/writes JSON.

Actions and modes:

- `references/act-apply-fixes.md`: applying findings: the regression guard and the order of operations.
- `references/act-comment-findings.md`: leaving findings on the PR instead of fixing: anchoring and approval.
- `references/mode-external-pr.md`: reviewing a PR in another repo and posting the review.

Pipeline agents (plugin root, dispatched by the fan-out):

- `<plugin-root>/agents/bb-review-finder.md`: the finder's contract, and the narrowed `tools:` list.
- `<plugin-root>/agents/bb-review-verifier.md`: the CONFIRMED / PLAUSIBLE / REFUTED rubric.

- `references/review-checklist.md`, `references/quality-checklist.md`: the correctness and quality criteria the fronts operationalize.

References (plugin root):

- `<plugin-root>/references/finding-levels.md`: Bloqueante / Sugestão (`HIGH` / `LOW` in a guide), the per-front mapping, the concrete-cost gate and the legacy collapse. Shared with `/bb:review-setup`.

Scripts (plugin root):

- `<plugin-root>/scripts/preflight.py`: the whole availability probe in one call, run at step 0. Resolves the review's diff range, answers every front's "Available when" (`fronts.md`), and its `pr` is what decides whether the intent read has a conversation to read.
- `<plugin-root>/scripts/gather_context.py`: the same branch context plus the commit log, the full diff and `pr_body`, the PR description the intent read works from, for a scope paragraph the probe's diff stat cannot carry. Called with `--base <the probe's base_branch> --no-fetch`, because the probe resolved that base against the PR's own and already paid the fetch: without both flags this second call re-derives the base from the repo default and diffs a stacked PR against the wrong ref.
- `<plugin-root>/scripts/inspect_pr_checks.py`: failing checks, their run IDs and the failure snippets, for the `ci` front (`front-ci.md`).
- `<plugin-root>/scripts/fetch_comments.py`, `<plugin-root>/scripts/reply_resolve_thread.py`: thread I/O via `gh api graphql`. `fetch_comments.py` is also the conversation half of step 0's intent read: the comments, the review bodies and the inline threads in one payload.
