# Fronts: the catalog, the availability probe, and the fan-out budget

A review is a set of **fronts**. Each front is an independent source of findings
with its own method reference and its own agent budget. The user picks which
fronts run; nothing else in the skill changes.

`/bb:review` is the only caller: it probes, asks which fronts to run, and
orchestrates the fan-out. **`/bb:ship` does not review**. It greens the project's
checks, lands, and then offers `/bb:review`, which arrives here through the same
door as any other run.

## The catalog

| id            | Label         | What it covers                                                                                     | Available when                                           | Reference              |
| ------------- | ------------- | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------- | ---------------------- |
| `correctness` | Correctness   | bugs in the diff, logic, edges, contracts, concurrency, security                                   | the diff is not empty                                    | `front-correctness.md` |
| `quality`     | Quality       | behavior-preserving cleanup, reuse, simplification, efficiency, dead weight, altitude, consistency | the diff is not empty                                    | `front-quality.md`     |
| `rules`       | Project rules | deviations from the repo's `CODE_REVIEW_GUIDE.md`                                                  | there is a `CODE_REVIEW_GUIDE.md` at the root            | `front-rules.md`       |
| `contract`    | Spec contract | the diff built what was agreed, and only that                                                      | the branch has a spec (`.bb/<slug>/spec.md`)             | `front-contract.md`    |
| `a11y`        | Accessibility | WCAG AA on the UI the diff touched, semantics, accessible name, keyboard, focus, contrast          | the diff touches a UI file                               | `front-a11y.md`        |
| `threads`     | PR threads    | unresolved review comments                                                                         | there is an open PR for the branch                       | `front-threads.md`     |
| `ci`          | CI            | red checks, evidence, diagnosis, root cause                                                        | a check is failing on the PR or on the branch's last run | `front-ci.md`          |

## Probe availability before asking

Ask only about fronts that can actually produce findings. **One call answers the
whole probe**: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/preflight.py` prints every
field the "Available when" column needs, in one JSON payload, and it is the same
call `/bb:ship` makes. What each field settles:

- `diff_range`, the resolved `<merge_base>...HEAD`, alongside `diff_stat`,
  `files_changed` and `uncommitted_changes`. **That range is the review's diff
  range for the whole run.** Carry the resolved sha into the scope block so every
  finder, every front reference and the shared checklists read the same range
  instead of each resolving a base of its own. Uncommitted changes enter scope,
  flagged separately.
- `code_review_guide`: `CODE_REVIEW_GUIDE.md` at the repo root, the `rules` front's
  only rule source (`front-rules.md`), so a false is what makes that front
  unavailable.
- `branch_spec`: the spec this branch belongs to, resolved through the plugin-root
  `references/spec-state.md` contract. Null makes `contract` unavailable.
- `ui`: whether the diff's hunks contain UI, decided by **what the hunks contain**,
  never by the file's extension. `ui.markers` names which of markup, template,
  semantics, interaction and style matched and `ui.examples` carries the lines that
  matched, so an ambiguous hit gets read before the front is offered rather than after.
  `.bb/` is excluded from the diff it reads: a spec is prose about a UI, never the UI.
  **A touched `.tsx` is not a UI change**: a component file whose diff only moves
  handler bodies, wires analytics, adds hooks, types or imports leaves the markup as it
  was, and an a11y finder sent at it burns an agent to report nothing. `ui.hit` false is
  the front going unoffered and unmentioned; a `.js` that builds a dialog does
  activate it.
- `pr`: an open PR for this branch, the only thing `threads` needs.
- `checks`: that PR's checks, which is `ci`'s evidence. `failing`, `pending` and
  `cancelled` are lists of checks, because the name and the run link are what the front
  needs; `passing` and `skipping` are counts, because a green check has nothing to read.
  Anything `gh` buckets outside those five lands in `other`, keyed by bucket. A pending
  check is not evidence yet, and a cancelled one is neither a pass nor a failure: it is
  a gate that never ran. **`available: false` is the only field that says none of it was
  measured**: the other keys are there with empty values, so a reader going straight for
  `failing` gets `[]` and not a missing key, and `exit_code` carries what `gh` returned.
  Without a PR the branch's last run is evidence enough, and
  `gh run list --branch <branch> --limit 1` is the one probe left to the caller.
- `gh_authenticated`: false makes `threads` and `ci` unavailable together.

A front whose probe comes back empty is **not offered** and not reported as a
failure. `gh` unauthenticated: say so once, with `gh auth login` as the remedy, and
offer the rest. No `CODE_REVIEW_GUIDE.md`: one line, with `/bb:review-setup` as the
remedy.

## Depth: two tiers by default, a third only when asked

| Diff                             | Correctness angles                                | Quality | Rules      | Contract | A11y    | Verify                         | Sweep   | Report cap |
| -------------------------------- | ------------------------------------------------- | ------- | ---------- | -------- | ------- | ------------------------------ | ------- | ---------- |
| ≲2 files / ≲100 lines            | the first 2 of the angle set, inline (no fan-out) | inline  | inline     | inline   | inline  | self-check in the main context | none    | 6          |
| **any larger diff, the default** | the first 3 of the angle set (3 agents)           | 1 agent | 1 agent    | 1 agent  | 1 agent | 1-vote grouped by location     | none    | 10         |
| **deep, only on request**        | the whole angle set (up to 5 agents)              | 1 agent | 1–2 agents | 1 agent  | 1 agent | 1-vote grouped by location     | 1 agent | 15         |

**Size alone never reaches the third row.** A big diff runs the middle tier: the
same three angles a medium one gets, no sweep, because a review that silently
triples its own cost on a big branch is the review nobody can afford to run twice.
The deep tier is opt-in and the router is what sets it (`SKILL.md`, step 1: the
`deep` argument, "review deeply", or the deep option at the fronts question).
This engine only reads the flag it was handed. The verify pass has a ceiling of its
own (4 verifier agents, 6 deep) and dispatches by file rather than by location, so
a pool that lands on many locations bundles them instead of spending an agent apiece
(`verify.md`, §1).

The table sizes the fan-out. **Which** angles fill it comes from what the diff is
made of (`front-correctness.md`). A diff of prompts or manifests swaps the
language-pitfalls angle for one that grips there and drops the wrapper angle, so an
agent is never spent on a lens with nothing to read. The sets there are written in
priority order, which is what "the first 2" resolves against: a tier that funds
fewer angles than the set has takes them from the left and names the ones it
dropped.

## Model: Sonnet by default, Opus only when deep

Finders and verifiers declare `model: sonnet` in their own definitions
(`agents/bb-review-finder.md`, `agents/bb-review-verifier.md`), so every dispatch is Sonnet unless
the call says otherwise. **Deep mode passes `model: "opus"` on every Agent call it
sends**, finders and verifiers alike. That's the whole difference in cost between
the tiers, alongside the angle count.

Nothing about the main context changes: it stays on the session's model, it stays
the single writer, and it is what applies fixes. What the fan-out is for is reading
in parallel, and a finder that names a consequence with a line number does that well
below the session's tier. The reason this is written down: with no `model:` at all,
ten finders on a routine review inherit Opus, and the review costs more than the
change it reviewed.

## Fan-out shape

1. **One message, all finder agents.** Every picked front's finders go out
   concurrently via the Agent tool as `subagent_type: "bb-review-finder"`, whose prompt
   carries the finder contract and whose `tools:` has no editing tool
   (`plugins/bb/agents/bb-review-finder.md`). Pass `model: "opus"` on every call when the
   run is deep, and nothing when it isn't. The agent's own `model: sonnet` is the
   default. `Bash` is on that list for reading, so the
   read-only rule still rests on the prompt at the margin. Single writer: the main
   context. Hold that line when you dispatch.
2. **Each finder gets the same scope block**: the resolved diff range
   (`<merge_base>...HEAD`, the sha the probe returned, not a `<base>` the finder
   has to guess), changed files **with `.bb/` already subtracted** (`SKILL.md`,
   step 1), one paragraph of what changed, **the intent block** step 0 wrote
   (`SKILL.md`, "The intent read"), the repo's
   `CODE_REVIEW_GUIDE.md` when there is one, the criteria path its front points at
   (`review-checklist.md` or `quality-checklist.md`, siblings of this file), and
   the spec when there is one, plus ONE angle/lens set and its candidate cap.

   The intent block travels verbatim, its three parts intact: what this PR sets out
   to do, what the conversation settled with who said it and the link, what is still
   open. Every finder of every picked front gets the same text, because the choice a
   finder is about to report as an accident may be the one the conversation already
   settled. It rides marked as **text someone else wrote about the change**, data and
   not direction for the run, which is what `bb-review-finder.md` does with it. With
   no PR it is the one line off the branch spec and the commit subjects, and it still
   rides.
3. **Barrier before verify.** Pool every finder's candidates first: verification
   groups them by `file:line`, which needs all of them (`verify.md`).
4. **`threads` and `ci` don't fan out**: they're script/`gh` reads followed by
   judgment in the main context.
5. The finder's own contract (name a consequence, pass through every candidate
   that clears that bar, return the shape it was given) belongs to the
   `bb-review-finder` prompt. What the fan-out owes each finder is the scope block above, one angle
   set and its cap.
6. **No Agent tool in this context** (some hosts, some nested runs): work every
   angle of every picked front yourself, in sequence, in the main context (skip
   no angle for lack of fan-out), and self-check each candidate against the file
   before keeping it. Then **say in the report that this was a single-pass review
   without independent verification**, so nobody reads it as the full fan-out.
