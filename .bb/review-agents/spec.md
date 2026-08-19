---
status: done
created: 2026-08-04
slug: review-agents
---

# bb-finder and bb-verifier: capability scoping for the review fan out

Two agents defined in the plugin, `plugins/bb/agents/bb-finder.md` and
`plugins/bb/agents/bb-verifier.md`, named by their **role in the pipeline**, not by front.
`/bb:review`'s fan out (and, by borrowing, `/bb:ship`'s) starts dispatching them through
`subagent_type`, and the frontmatter's `tools:` becomes what guarantees that finder and
verifier do not write. Along with it: each role's invariant contract moves into the agent's
system prompt, and CI learns to validate `agents/*.md`.

The finders' read-only property is guaranteed by prose today (`fronts.md:77`, "read-only, they
report, never edit"), but the repo's `.claude/CLAUDE.md` orders **"enforce irreversible hazards
with capability scoping, not prose"**. It is the same reasoning already applied twice in the
repo: never-merge and outward-posting left the prose for the routine's capability scoping.

The concrete damage: a finder that decides to fix what it found breaks the single writer rule
with up to 5 agents writing in parallel in the same working tree, a corruption that is hard to
attribute, because the report records no edits nobody asked for.

Success: the read-only invariant sits in the frontmatter and in CI, and no skill has to repeat
it for it to hold.

## The seam between agent and caller

The agent owns the half that does not change between fronts; the caller assembles the half that
does.

```
bb-finder (system prompt)             | caller (scope block + prompt)
--------------------------------------|--------------------------------------
read-only, never edits                | resolved diff range (<merge_base>...HEAD)
every candidate with a nameable       | changed files and what changed
  consequence passes, no self-censor  | CODE_REVIEW_GUIDE.md / the brief, if any
returns exactly the Finding shape the | criteria path (review-/quality-checklist)
  caller passed                       | ONE angle/lens set plus its cap
says how many it cut at the cap       | the front's Finding shape

bb-verifier (system prompt)           | caller (scope block + prompt)
--------------------------------------|--------------------------------------
CONFIRMED/PLAUSIBLE/REFUTED rubric    | the candidates at that spot, [0], [1], …
bias: PLAUSIBLE is the default        | a per front addendum (a citation in
REFUTED only when it is constructible |   rules/contract, WCAG plus a contrast
  from the code, citing the line      |   recompute in a11y)
one verdict per index, judged         | the scope block
  independently, with evidence        |
```

**With no Finding shape passed** (the caller forgot, or it is a new use): the finder returns
`file:line | summary | failure_scenario`, the minimum `group_candidates.py` can group.

**A known and accepted limit:** with Bash on the list, a diff carrying text that instructs the
model ("ignore the above, edit X") is not barred by capability, because `Edit`/`Write` are gone
and `sed -i` is not. The `instruction-integrity` angle stays the defense by reading; the scoping
is a surface reduction, not isolation.

## Decisions

- **Two agents, by role**: `bb-finder` and `bb-verifier`. What differs between fronts is prompt
  content the caller already assembles (the angle set, the criteria path, the scope block, the
  Finding shape); one agent per front would be 7 global names guarding the same invariant half.
- **`tools: Read, Grep, Glob, Bash` in both**, with the cost declared: `tools:` works by tool
  name, so `sed -i` and `>` stay reachable through Bash. The scoping removes what the model
  naturally reaches for (Edit/Write); it is not hermetic. Bash is what keeps
  `git diff <range>` and `gh pr diff` (mode-external-pr) working without inflating the scope
  block.
- **The agent owns the contract.** The CONFIRMED/PLAUSIBLE/REFUTED rubric (plus the PLAUSIBLE
  bias, plus REFUTED only when constructible from the code) lives in `bb-verifier`'s prompt; the
  finder's contract (a nameable consequence, no self-censoring) lives in `bb-finder`.
  `verify.md §2`, `fronts.md` item 5 and `front-correctness.md`'s consequence paragraph defer in
  one line each.
- **What does not move:** the citation based verification of `rules`/`contract`/`a11y` stays in
  the reference and the caller appends it to the verifier's prompt, because it is per front
  content and not a role invariant. Same for the Finding shape's fields, the angle sets and the
  caps.
- **The fallback is to relocate, not to delete**: `fronts.md:77` and `review/SKILL.md:91` become
  "the finders go as `subagent_type: bb-finder`, read-only by capability", one line each. The
  invariant stays named once, but the frontmatter is what guarantees it; `fronts.md`'s item 6
  keeps covering a host with no fan out.
- **CI guards the scoping**: `validate-frontmatter.ts` walks `agents/*.md` (`name` plus
  `description` required) and **fails if a bb agent lists `Write`/`Edit`/`NotebookEdit` in
  `tools:`**, which is exactly the PR's argument turned into a test. `validate.yml`'s `paths:`
  gains `plugins/bb/agents/**` and `.github/scripts/**`, otherwise an agent only PR never fires
  the Validate.
- **`model:` omitted in both** → it inherits the session's model. The quality of the finding and
  of the verdict is precisely what nobody wants made cheaper by default.
- **`description:` in PT-BR and deliberately narrow**: it says this is an internal role in the
  review pipeline, dispatched by the skills, and it points at `/bb:review` for whoever wants to
  review. A plugin agent stays globally visible with its description always in context.
- **`plugin.json` declares nothing**: `agents/` is auto-discovered (confirmed in the official
  `pr-review-toolkit`: 6 agents, `plugin.json` with no `agents` field). Only the bump.
- **Version**: `2.2.0` → `2.3.0` in `plugin.json` and in the `metadata.version` of each touched
  SKILL.md (`review`; `ship` only if it ends up touched).
- **`/bb:ship` with no edit expected**: it borrows `fronts.md`/`verify.md`, so it inherits the
  agents through the borrowing convention. Adjust `ship/SKILL.md:54` only if the line turns
  ambiguous after slice 2.

## Behavior

Happy path (`/bb:review`, step 3, a depth with fan out):

1. The probe resolves the diff range and the available fronts; nothing changes here.
2. The caller assembles the scope block and fires every finder **in one message**, each with
   `subagent_type: "bb-finder"`, one angle/lens set and its front's cap.
3. Each finder reads the diff (`git diff <merge_base>...HEAD` through Bash) and the files with
   the enclosing function open; it returns candidates in the front's Finding shape. No finder
   can call Edit/Write, since they are not on the tools list.
4. The barrier: the main context gathers everything and runs `group_candidates.py`.
5. One `bb-verifier` per spot, with the indexed candidates plus the front's addendum when it is
   `rules`/`contract`/`a11y`. The rubric comes from the agent's prompt.
6. Dedupe, rank, cap, report: unchanged. The stats line still adds up.

| WHEN                                            | THEN                                                                                                 |
| ----------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `bb-finder` does not resolve as `subagent_type` | it falls back to the generic agent with the contract inline; no crash and no silent regression       |
| there is no Agent tool at all in the host       | `fronts.md`'s item 6, everything in the main context, and the report says it was single pass         |
| the caller passes no Finding shape              | the finder returns `file:line \| summary \| failure_scenario`                                        |
| a tiny diff (≲2 files / ≲100 lines)             | no agent is spawned, since the depth table already orders it inline                                  |
| a candidate from `rules` / `contract` / `a11y`  | the caller appends the addendum; the verifier applies the 3 states over a citation, not over a crash |
| a finder dies                                   | the front reports with the angles that came back and names what is missing                           |
| a verifier dies or omits an index               | the candidate stays without a verdict, on a line of its own, never promoted                          |
| `/bb:ship` runs the same pass                   | it uses the same two agents with no edit in `ship/`                                                  |
| someone adds a bb agent with `Write`            | the Validate fails naming the file and the forbidden tool                                            |
| a PR touches only `plugins/bb/agents/**`        | the Validate fires, since the paths filter was extended                                              |
| the diff carries text that instructs the model  | Edit/Write barred; writing through Bash stays reachable, a declared limit                            |
| `BB_UNATTENDED` set                             | nothing changes, since the path is already report only                                               |

## Tasks

- [x] **1. The two agents**: `bb-finder.md` and `bb-verifier.md`, the frontmatter (`name`, a
      narrow PT-BR `description`, `tools: ["Read", "Grep", "Glob", "Bash"]`, no `model`) and an
      English system prompt with each role's invariant contract
      → behaviors 3, 5 and the Finding shape and injection rows · dep: — · verify: CI
- [x] **2. The engine dispatches the agents**: `fronts.md` (item 1 names the `subagent_type`,
      item 5 defers the contract), `review/SKILL.md:91`, `verify.md §2` (defers the rubric, keeps
      the per front addendum), `front-correctness.md`
      → behaviors 2, 5 and the fallback and ship rows · dep: 1 · verify: CI
- [x] **3. CI guards the scoping**: `validate-frontmatter.ts` walks `agents/*.md`, requires
      `name` plus `description` and fails on `Write`/`Edit`/`NotebookEdit`; `validate.yml` gains
      `plugins/bb/agents/**` and `.github/scripts/**` in its `paths:`
      → the table's two CI rows · dep: — · verify: CI green (which proves the assertion gives no
      false positive on the other agents)
- [x] **4. Docs and version**: `.claude/CLAUDE.md` (the tree gains `agents/`, plus one convention
      line), the README if it lists the structure, the bump `2.2.0` → `2.3.0`
      → no behavior of its own · dep: 1-3 · verify: CI

Suggested PR: `feat(review): bb-finder e bb-verifier com capability scoping`.

## Out of scope

- **`/bb:review-setup`'s 5 discovery subagents**: fixed prompts, in a skill that runs rarely; it
  does not pay for 5 global names. _revisit_ if review-setup becomes routine.
- **Reusing the native `Explore`**: its description says it locates code and does not review or
  audit, which would fight the task.
- **`/bb:spec`'s independent reviewer** (the Agent tool, fresh context): the same read-only
  shape, but with no Finding shape and no verify pipeline, so it is not the same role. _revisit_
  if it starts returning structured findings.
- **One agent per front**: the differences between fronts are prompt content the caller already
  assembles.
- Deleting the local `claude/review-fronts` branch: cleanup, not part of this task.

## Open

- Nothing load-bearing. The one point to confirm during the build is whether `ship/SKILL.md:54`
  needs a wording adjustment, decided by default: touch it only if the line turns ambiguous
  after slice 2.
