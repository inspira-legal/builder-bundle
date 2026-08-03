# Verify — pool, group by location, one independent vote, then rank

Between the finders and the report there is exactly one gate: every candidate gets
judged by an agent that didn't produce it. A finder is optimistic by design (it
passes through everything with a nameable failure scenario); this pass is what
keeps the report worth reading.

Runs for the fan-out depths. At the tiny-diff depth there are no finder agents, so
the "verify" step is a self-check in the main context: re-read each candidate
against the file before keeping it.

## 1. Pool and group

Wait for **all** finders across all picked fronts (the barrier). **Canonicalize
every path first**: a finder may return the same file as an absolute path, a
repo-relative one, or with backslashes. Match each candidate's path by suffix
against the changed-file list from the scope block (longest match wins) and
rewrite it to that form. Skipping this splits one location into several groups,
which is exactly what the grouping exists to prevent.

Then group the candidates by `file:line`. Grouping is not dedup — every candidate keeps its own
verdict; candidates at the same line are often distinct issues. Cross-finder
location collisions are common, and one verifier agent per location costs far
fewer agents than one per candidate with no loss.

Candidates with no line (a whole-file or cross-file claim) group by `file`.

## 2. One verifier per location

Each verifier agent gets the scope block, the candidates at that location labeled
`[0]`, `[1]`, …, and returns one verdict per index, judging each **independently
on its own claim**, with evidence that quotes or cites the relevant line:

- **CONFIRMED** — can name the inputs/state that trigger it and the wrong output
  or crash. Quote the line.
- **PLAUSIBLE** — the mechanism is real, the trigger is uncertain (timing, env,
  config). State what would confirm it.
- **REFUTED** — factually wrong (the code doesn't say that) or guarded elsewhere.
  Quote the line that proves it.

**PLAUSIBLE is the default when the state is realistic.** Concurrency races,
nil/undefined on a rare-but-reachable path (error handler, cold cache, missing
optional field), falsy-zero treated as missing, off-by-one on a boundary the code
doesn't exclude, retry storms, a regex or allowlist that lost an anchor — all
PLAUSIBLE, not refuted for being "speculative".

**REFUTED only when constructible from the code**: factually wrong (quote the
actual line); provably impossible via a type, constant, or invariant (show it);
already handled in this diff (cite the guard); or pure style with no observable
effect.

A candidate the verifier rendered no verdict on (agent died, index omitted) is
**dropped** — never promoted to PLAUSIBLE on the strength of the finder alone. It
still gets its line in the report (§4): a candidate nobody judged is a different
thing from one that was judged and refuted, and the reader has to be able to tell.

## Rule, contract and a11y candidates verify differently

For `rules` and `contract` candidates, the verifier checks the **citation**, not a
crash: does the quoted rule text actually appear in the named source, does its
scope reach the changed file, and does the quoted line actually break it. A
citation that doesn't hold up is REFUTED regardless of how sensible the rule
sounds. This is where hallucinated rules die.

`a11y` candidates verify the same way against WCAG: does the cited criterion
actually cover this element, and does the markup in the file actually fail it —
an accessible name supplied further up the tree, a native element that already
carries the semantics, a focus style defined in a companion stylesheet all refute
the finding. A criterion number that doesn't match the criterion's real content is
REFUTED. Contrast claims are checked by recomputing the ratio from the resolved
colors.

## 3. Sweep (large diffs only)

One fresh finder gets the verified list and hunts **only for gaps** — no
re-deriving, no re-confirming. Focus it on what a first pass misses: moved or
extracted code that dropped a guard or anchor; second-tier footguns (a default
evaluated once at definition, non-deterministic hashing, a lock scope that shrank,
a predicate method with side effects); setup/teardown asymmetry in tests; config
defaults flipped. Up to 8 new candidates, which then go through verify. An empty
sweep is a real answer.

## 4. Dedupe, rank, cap

- **Dedupe by root cause**, across fronts: same defect, same reason → keep the
  entry with the most concrete failure scenario, and note the other locations on
  it (`[mesma causa também em: …]`).
- **Rank**, most severe first:
  1. CONFIRMED correctness bugs, HIGH rule deviations, **Critical** a11y failures
     (something the diff shipped is unusable for someone)
  2. PLAUSIBLE correctness bugs, missing happy-path contract rows, **Major** a11y
  3. MEDIUM rule deviations, remaining contract findings, **Minor** a11y
  4. quality findings and a11y **Enhancement**s (always last — a cleanup never
     outranks a bug)
- **Cap** at the depth's report cap. Cuts come off the bottom, so quality is what
  gets trimmed, never a correctness bug.
- **Nothing vanishes silently.** Every candidate that came out of a finder ends up
  in exactly one of four places: reported, **refutados** (one line each at the end of
  the report), **sem veredito** (the dropped ones, one line each with the location and
  why the verdict is missing — dead agent, omitted index), or counted under the cap
  ("+4 findings de qualidade fora do cap"). The stats line's `candidatos` has to add
  up across the four.
