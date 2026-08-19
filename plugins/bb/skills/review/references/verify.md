# Verify: pool, group by location, one independent vote, then rank

Between the finders and the report there is exactly one gate: every candidate gets
judged by an agent that didn't produce it. A finder is optimistic by design (it
passes through everything with a nameable failure scenario); this pass is what
keeps the report worth reading.

Runs for the fan-out depths. At the tiny-diff depth there are no finder agents, so
the "verify" step is a self-check in the main context: re-read each candidate
against the file before keeping it. Verifiers dispatch on Sonnet like the finders,
and go to Opus on the same condition they do, a deep run (`fronts.md`, "Model").

## 1. Pool and group

Wait for **all** finders across all picked fronts (the barrier), then run
`scripts/group_candidates.py`: it canonicalizes the paths and groups by location
in one deterministic pass:

```bash
python scripts/group_candidates.py < candidates.json
```

Input is `{"scope_files": [...], "candidates": [...]}`; output is the groups, the
paths that matched nothing in scope, and the counts for the stats line. A finder
may return the same file as an absolute path, a repo-relative one, or with
backslashes. The script matches by path segment suffix (longest match wins) and
rewrites each to the scope form. Skipping this splits one location into several
groups, which is exactly what the grouping exists to prevent.

**`scope_files` is whatever enumerated the review's scope**: the changed-file list
in diff scope, and in surface scope (a11y over a folder, a file set or a rendered
page) the file set the audit enumerated. There is always a list to canonicalize
against; a review with no diff is not a review with no scope.

Grouping is not dedup. Every candidate keeps its own verdict; candidates at the
same line are often distinct issues, and cross-finder collisions on one line are
common. Candidates with no line (a whole-file or cross-file claim) group by `file`.

So grouping is what keeps two candidates on one line from collapsing into one
verdict. It is **not** what decides how many agents go out: locations are cheap to
make and agents are not, and four finders returning 25 candidates across 20 locations
would otherwise fund 20 agents to produce a report that keeps 10.

**The dispatch unit is the file, and at most 4 agents go out** (6 on a deep run). A
verifier that opens `src/a.ts` once can judge every candidate in it: the file's
locations ride along in one prompt, each still labeled, each still judged on its own
claim. When the pooled candidates touch more files than the cap allows, bundle the
files across the calls. Every file holding a `correctness` candidate placed first,
then `rules` and `contract`, then the rest, so the heaviest files get the most
attention and the cheap ones share. Nothing is dropped and no verdict changes; what
changes is that one agent reads a file once for five candidates instead of five
agents reading it five times.

## 2. One verifier per file, up to 4 agents

Each verifier goes out as `subagent_type: "bb-review-verifier"`
(`plugins/bb/agents/bb-review-verifier.md`), which owns the rubric: the three verdicts, the
PLAUSIBLE default and what makes a REFUTED constructible from the code all live in
that prompt, so both callers of this engine judge the same way without a second copy
to keep in sync, and without the fan-out having to re-send it.

What this pass hands it: the scope block, the candidates in its file (or files)
labeled `[0]`, `[1]`, … with the `file:line` each index sits at, and the addendum
below when the front calls for one. Back comes one verdict per index, each judged
independently on its own claim, with evidence.

A candidate the verifier rendered no verdict on (agent died, index omitted) is
**dropped**: never promoted to PLAUSIBLE on the strength of the finder alone. It
still gets its line in the report (§4): a candidate nobody judged is a different
thing from one that was judged and refuted, and the reader has to be able to tell.

## The addendum: rules, contract and a11y verify differently

These fronts don't turn on a crash, so their verifiers get one extra paragraph in
the prompt saying what verification means there. It replaces the crash question and
leaves the three verdicts and the evidence rule untouched.

For `rules` and `contract` candidates, the verifier checks the **citation**, not a
crash: does the quoted rule text actually appear in the named source, does its
scope reach the changed file, and does the quoted line actually break it. A
citation that doesn't hold up is REFUTED regardless of how sensible the rule
sounds. This is where hallucinated rules die.

`a11y` candidates verify the same way against WCAG: does the cited criterion
actually cover this element, and does the markup in the file actually fail it. An accessible name supplied further up the tree, a native element that already
carries the semantics, a focus style defined in a companion stylesheet all refute
the finding. A criterion number that doesn't match the criterion's real content is
REFUTED. Contrast claims are checked by recomputing the ratio from the resolved
colors.

## 3. Sweep (deep runs only)

Only the deep tier funds this pass. A large diff on the default tier doesn't get
it (`fronts.md`, depth table). One fresh finder gets the verified list and hunts
**only for gaps**: no
re-deriving, no re-confirming. Focus it on what a first pass misses: moved or
extracted code that dropped a guard or anchor; second-tier footguns (a default
evaluated once at definition, non-deterministic hashing, a lock scope that shrank,
a predicate method with side effects); setup/teardown asymmetry in tests; config
defaults flipped. Up to 8 new candidates, which then go through verify. An empty
sweep is a real answer.

## 4. Dedupe, rank, cap

- **Dedupe by root cause**, across fronts: same defect, same reason → keep the
  entry with the most concrete failure scenario, and note the other locations on
  it (`[same cause also in: …]`).
- **Rank**, most severe first:
  1. CONFIRMED correctness bugs, HIGH rule deviations, **Critical** a11y failures
     (something the diff shipped is unusable for someone)
  2. PLAUSIBLE correctness bugs, missing happy-path contract rows, **Major** a11y
  3. MEDIUM rule deviations, remaining contract findings, **Minor** a11y
  4. quality findings and a11y **Enhancement**s (always last: a cleanup never
     outranks a bug)
- **Cap** at the depth's report cap. Cuts come off the bottom, so quality is what
  gets trimmed, never a correctness bug. A front that states **no cap for its own
  scope** wins over a depth cap resolved from a diff. A surface-scope a11y audit
  reports every verified failure (`front-a11y.md`), because a cap there would hide
  exactly what the audit was asked for.
- **Nothing vanishes silently.** Every candidate that came out of a finder ends up
  in exactly one of four places: reported, **refuted** (one line each at the end of
  the report), **no verdict** (the dropped ones, one line each with the location and
  why the verdict is missing: dead agent, omitted index), or counted under the cap
  ("+4 quality findings outside the cap"). The stats line's `candidates` has to add
  up across the four.
