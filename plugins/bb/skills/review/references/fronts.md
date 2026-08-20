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
| `design`      | Design system | raw values where a token exists, rebuilt components, missing states, drift from the direction      | the diff touches a UI file and a design source resolves  | `front-design.md`      |
| `threads`     | PR threads    | unresolved review comments                                                                         | there is an open PR for the branch                       | `front-threads.md`     |
| `ci`          | CI            | red checks, evidence, diagnosis, root cause                                                        | a check is failing on the PR or on the branch's last run | `front-ci.md`          |

## Probe availability before asking

Ask only about fronts that can actually produce findings. Run the probe as one
batch of cheap read-only calls (parallel background where possible):

- `${CLAUDE_PLUGIN_ROOT}/scripts/gather_context.py`: one call returns
  `base_branch`, `merge_base`, `diff_stat`, `files_changed` and
  `uncommitted_changes`. **`<merge_base>...HEAD` is the review's diff range for
  the whole run**. Carry the resolved sha into the scope block so every finder,
  every front reference and the shared checklists read the same range instead of
  each resolving a base of its own. Uncommitted changes enter scope, flagged
  separately.
- `CODE_REVIEW_GUIDE.md` at the repo root. The `rules` front's only rule source
  (`front-rules.md`), so its absence is what makes the front unavailable.
- spec lookup for this branch (plugin-root `references/spec-state.md`).
- UI in the diff, decided by **what the hunks contain**, never by the file's
  extension. Grep the added/removed lines (`git diff <range> -U0`) for one of:
  - rendered markup: a JSX/HTML element, a tagged template with tags,
    `createElement`, `innerHTML`, server-side HTML in `.erb`/`.hbs`/`.blade.php`
    or a Django/Jinja template;
  - an attribute that decides semantics or interaction: `role`, `aria-*`, `alt`,
    `label`, `tabIndex`, `autoFocus`, `.focus()`, or a keyboard/pointer handler
    added to an element (`onClick`, `onKeyDown`) as part of new markup;
  - a stylesheet hunk that decides focus, contrast or visibility (`outline`,
    `:focus`, `color`, `background`, `display: none`).

  **A touched `.tsx` is not a UI change.** A component file whose diff only moves
  handler bodies, wires analytics, adds hooks, types or imports leaves the markup
  as it was, and an a11y finder sent at it burns an agent to report nothing; the
  front is unavailable and the report doesn't mention it. A `.js` that builds a
  dialog does activate it. When the grep is ambiguous, read the hunks before
  offering the front, not after.

- design source, only when the UI grep above passed: any one of `design-context/`
  at the repo root, a token source the project reads (a `tokens.json`, CSS custom
  properties, a Tailwind theme config), or the branch's `.bb/<slug>/design.md`
  (or `design/`). One resolving makes `design` available; the resolution order and
  what each rung is worth are `front-design.md`'s.
- `gh pr view --json number,url`: is there an open PR.
- failing checks: `gh pr checks <n>` when a PR exists, otherwise
  `gh run list --branch <branch> --limit 1`: the branch's last run is evidence
  enough for `ci` without a PR.

A front whose probe comes back empty is **not offered** and not reported as a
failure. Only `threads` needs an open PR; `ci` falls back to the branch's last
run. `gh` unauthenticated makes both unavailable. Say so once, with
`gh auth login` as the remedy, and offer the rest. No `CODE_REVIEW_GUIDE.md` makes
`rules` unavailable. One line, with `/bb:review-setup` as the remedy. UI in the diff
but no design source makes `design` unavailable. One line, naming what would create a
source (a token file the build reads, or a `design-context/` from `/bb:brisar`).

## Depth: two tiers by default, a third only when asked

| Diff                             | Correctness angles                                | Quality | Rules      | Contract | A11y    | Design  | Verify                         | Sweep   | Report cap |
| -------------------------------- | ------------------------------------------------- | ------- | ---------- | -------- | ------- | ------- | ------------------------------ | ------- | ---------- |
| ≲2 files / ≲100 lines            | the first 2 of the angle set, inline (no fan-out) | inline  | inline     | inline   | inline  | inline  | self-check in the main context | none    | 6          |
| **any larger diff, the default** | the first 3 of the angle set (3 agents)           | 1 agent | 1 agent    | 1 agent  | 1 agent | 1 agent | 1-vote grouped by location     | none    | 10         |
| **deep, only on request**        | the whole angle set (up to 5 agents)              | 1 agent | 1–2 agents | 1 agent  | 1 agent | 1 agent | 1-vote grouped by location     | 1 agent | 15         |

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
   has to guess), changed files, one paragraph of what changed, the repo's
   `CODE_REVIEW_GUIDE.md` when there is one, the criteria path its front points at
   (`review-checklist.md`, `quality-checklist.md` or `design-checklist.md`, siblings
   of this file), and the spec when there is one, plus ONE angle/lens set and its
   candidate cap. The `design` finder's scope block also carries the resolved design
   sources (`front-design.md`, §1), so the finder cites instead of re-resolving.
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
