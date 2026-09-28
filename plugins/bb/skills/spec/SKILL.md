---
name: spec
description: Align on the idea before building. Develops a draft, iterates the gray areas of what gets built with you through the question tool, maps the expected behavior (happy path plus edges), orders the work in phases and closes at a gate that asks what now (build, review the spec, or stop) and what runs after the build (review the branch, ship, both or neither). Reads the framing from /bb:discover and the journey from /bb:brisar when they are there. Use when the user says "write the spec", "spec this out", "let's plan", "shape this", "what should we build", "let's discuss before building", or starts a non trivial feature. Don't use it for small mechanical changes (just do those) or to find bugs (use /bb:review).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 3.1.0
---

# Spec

Reach a **shared understanding of the idea before any code**. What matters is the alignment; the spec is where it lands: a document written to be read, not a form to fill. You and the model converge on what you're building, then build fast against it.

> The point was never a template; it was building context and discussing before building. The spec keeps that: the converged conversation, written down for whoever builds from it. (When someone downstream needs a shareable product/UX spec document, that's the export mode; see `references/export-spec.md`.)

**A spec is a plan.** It says what gets built, the business rules, the expected behavior and the order the work runs in. The technical details are the builder's: the task agent settles them at build time, with the code open. A technical risk you see goes in `## Attention points`, named and with no solution. `references/spec-format.md` carries the whole format.

## Auto-size by complexity

- **Tiny** (≤3 files, one obvious change): skip the spec; just build it.
- **Medium** (a clear feature): the loop (gray areas of what gets built + the behavior map: happy path + edges + the phases), then the gate.
- **Large / fuzzy** (new domain, real ambiguity): the same loop, with the pieces and how they fit described in the spec's free top half before the work is broken into tasks, then the gate.

Always required: reach alignment, **map the behavior, run the lint before every gate**, and stop at a validated spec. Size is a running estimate, not locked at the start. If a "Tiny/Medium" task keeps surfacing gray areas mid-flow, re-size up and spec it properly.

## Read the upstream records first

Two siblings in `.bb/<slug>/` can already hold work this spec serves, and neither is written
here (plugin-level `references/spec-state.md`):

- **`discovery.md`**, from `/bb:discover`: `## Problem` / `## Hypothesis` / `## Fit` / `## Cuts`.
  The problem and success signal anchor the `why`, the appetite bounds the scope, and `## Fit` /
  `## Cuts` already settle what's in and what was deliberately dropped.
- **`design.md`**, from `/bb:brisar`: the journey. The chosen direction, the surfaces and the
  states each one built, and what the design review and the accessibility audit found.

**Read them before drafting, and cite them instead of copying them.** A section quoted into
the spec is a second copy that goes stale the next time its own skill runs; a path is a
pointer that stays true. The one exception is `## Metric`: the lint reads the baseline and
the target inline, so those two values are materialized, each carrying the record's own
source with the record named beside it (`references/draft-first.md` has the seeding
rule). So don't re-litigate a cut the user made upstream, and don't ask
gray-area questions discover already answered. Echo the framing in one line, naming which
records exist, so the user sees it carried through, then develop the design on top of it.

Where a record and this spec disagree, **the spec wins**: it is the contract, they are the
records. The correction belongs to the record's own writer on its next round, so leave both
files alone. Either record missing is fine, and one arriving later is the normal case: brisar's
Deliver invokes this skill from its own gate. Spec from the one-liner as usual.

## The loop

You bring the idea; Claude develops it, then loops with you through the **`AskUserQuestion` tool** until the picture is consistent and you sign off. Never interrogate from a blank page, and never decide silently; drive it through real questions.

1. **Develop the draft (draft-first).** Read the one-liner, look at the codebase, and write a short draft spec with your best guesses filled in: what/why, the business rules, the scope edges, the behavior you expect. `## Metric` arrives filled too, seeded per the rule in `references/draft-first.md` (the discovery record's values with the record named in the provenance, a marked guess, or the honest skip); the shape is in `references/spec-format.md`. For Large work, also describe the pieces in the top half before breaking it into tasks. Bring something concrete to react to.

2. **Highest-stakes question first, ask before you anchor.** On the single call most expensive to get wrong about what gets built, ask the user how _they'd_ call it _before_ you reveal your own pick (an open `AskUserQuestion`). Anchoring is strongest on the choice that matters most. Don't pre-frame that one. One question only; everything else stays draft-first.

3. **Surface the gray areas as questions.** Everything else about what gets built and how it behaves that genuinely could go more than one way → ask via `AskUserQuestion`, batched (the tool takes up to 4 at once), each as concrete options with your lean. Decide the obvious yourself; don't ask about what the codebase or goal already settles. A technical detail is the builder's and is not asked. The exception is a technical choice only the user can make, like a stack the company settled or a contract another team depends on: ask it, and when it is a **stack choice** (framework, package manager, tooling), consult the manifesto first (plugin-level `references/consult-manifesto.md`).

4. **Loop.** Fold each answer into the draft, re-surface anything new it opens, ask again. Keep going until a round surfaces no new gray areas.

5. **Order the work.** Break the build into tasks and group them in `###` phases by what depends on what (`references/spec-format.md`): a foundation runs alone, the tasks that only need it and change different parts of the code share the next phase, and a closing task that needs all of them is the last phase. Write the technical risks you saw into `## Attention points`, each one the risk and where it lives, with no solution.

6. **Run the lint.** It catches dead section names, malformed tables and a missing required section. It runs before every gate, the first one and each one that reopens:

   ```bash
   python3 scripts/lint_spec.py .bb/<slug>/spec.md
   ```

   Fix its errors before the gate. Its warnings reach the gate as they are: a missing `## Attention points` is silenced by `Nothing.`, a missing `## Metric` by its one `skipped: <reason>` line, and a size warning is the user's call to split.

   When the project has `EVENTS.md` at its root, run the checker beside the lint, over
   the same spec:

   ```bash
   python3 <plugin-root>/scripts/check_events.py --spec .bb/<slug>/spec.md
   ```

   Fix what it finds the way you fix the lint's errors: a missing prefix or a missing
   dictionary field is already a task by then, per `references/draft-first.md`, and an
   `E`-code line still standing at the gate is an open item there. Without an
   `EVENTS.md`, there is nothing to check; say so in one line, that the project has no
   event convention yet and where the format lives
   (`<plugin-root>/references/events-convention.md`), and move on unchanged.

7. **The exit gate.** Described in its own section below.

Size the ask to the stakes: cheap-to-reverse decisions lead with your pick (the user vetoes if wrong); expensive-to-undo ones lay the options out and let them choose. Full playbook in `references/draft-first.md`.

## Map the behavior (required for Medium+)

The behaviors are what guarantee the built thing matches the idea. An unmapped behavior is an unverified assumption about the final result; the completeness of this map is the fidelity between idea and outcome.

- **Happy path**: walk the main flow step by step and concretely: input → what happens → observable output. Every step the flow really takes gets a line.
- **Edge cases**: every deviation that changes the outcome for the user, each with its **expected outcome**, phrased `WHEN <case> THEN <observable outcome>` so each row reads directly as a test: empty / zero / huge input, invalid input, first-run vs repeat, concurrent use, failure & rollback, denied permission/auth, partial or interrupted runs, migrating existing data. Map the _outcome_, not just that the case exists.

Walking each behavior surfaces calls you haven't made; those go back into the loop as gray areas. **A behavior with no decided outcome is an open item the gate blocks on.** Litmus for whether an edge's outcome is load-bearing (not just a minor case): **does its outcome contradict the `why`?** If choosing the wrong outcome would make the built thing betray its own reason for existing, it's load-bearing, and the gate blocks on it. This map doubles as the acceptance criteria: each behavior is something `/bb:ship` and `/bb:review` check against, and each happy-path segment is a vertical task. Record it in a `## Behavior` section for Large work (happy path + an edge→outcome table, which `/bb:review`'s `contract` front reads row by row); inline for Medium.

## The exit gate

The gate is where the spec proposes the build. Don't gate blind: first **show what the user is signing off on**, in the order a person reads to understand what gets built:

- **What it does and why**: two or three lines, the spec's opening said again.
- **The phases, in run order**: each `###` heading with its tasks under it, one line per task saying what it changes, and a mark on the phases whose tasks run together. A spec with no `###` heading lists its tasks flat, in document order, and says they run one at a time.
- **The load-bearing edges**: only the `WHEN … THEN …` rows whose wrong outcome would contradict the `why` (the litmus in "Map the behavior"), then a pointer to `## Behavior` for the rest.
- **The measure**: the `## Metric` section as written, the metric block or its skip line, so the measure gets signed off with the plan.
- **The verdict line** (in "Review the spec" below).
- **What is still open**: the items in `## Open`, each `Baseline:` or `Target:` value without real provenance, and each `E`-code line the checker printed in step 6. A `W`-code line from the lint or the checker shows beside the list without joining it: seen, never blocking.

The gate holds `## Metric` where the lint cannot: a value without real provenance is an open item, a value's own `skipped:` is not, and on a Medium spec the event trace is judged by hand. A checker `E`-code line is resolved by fixing the row or by writing the exception as its own task. A line whose path is the project's `EVENTS.md` has no row in this spec to fix, whatever its code, so it is resolved in that file and deferred as an external blocker until then. The shapes that arrive that way, and the remedy for each, are `references/draft-first.md`'s gate bullets.

### When something load-bearing is open

Everything on the open list counts here: a load-bearing decision, a metric value without real provenance, and a checker `E`-code line. Do NOT offer `Build`. Ask one `AskUserQuestion` whose options are **resolve it now**, **defer it explicitly** ("decide at build time", recorded as such in the spec) and **Stop here**. Never a silent "build anyway". What the user settles goes into the spec, the lint runs again, and the gate reopens.

### When nothing load-bearing is open

Finalize `.bb/<slug>/spec.md` (with its frontmatter block; see "Capture the alignment"), then ask **two questions in one `AskUserQuestion` call** (the format in the plugin-level `references/handoff-gate.md`):

- **What now**, single choice:
  - **Build (Recommended)**: invoke `/bb:implement <slug>` now, at the scope the second question sets.
  - **Review the spec**: run one `bb-spec-reviewer` over the spec (below), then reopen this gate. Offered only while the spec carries text no review has read.
  - **Stop here**: leave the spec; the user picks it up later.
- **After the build**, `multiSelect`, two boxes the user ticks or leaves: **Review the branch** (`/bb:review` over the branch before anything ships) and **Ship** (`/bb:ship` settles the destination and ships it). Both empty is a build only.

The second answer counts only with `Build`. With `Review the spec` or `Stop here` it is ignored, and the next gate asks it again.

**The two answers together are implement's scope**, so implement asks nothing:

| after the build     | `/bb:implement` scope  |
| ------------------- | ---------------------- |
| nothing ticked      | build only             |
| `Review the branch` | build and review       |
| `Ship`              | build and ship         |
| both                | build, review and ship |

The user can answer with an adjustment instead (the tool's free-text option). A change to the spec made at the gate is new text: fold it in, run the lint, and reopen the gate with `Review the spec` offered again. A `Build` pick is the affirmative start, not a silent roll-through.

## Review the spec (the user's pick at the gate)

The review is an option, never a required step: a spec that no review read builds the same way when the user picks `Build`. The author cannot see their own omissions, and a reader with no memory of the conversation can, which is what the option is for.

**One reviewer, one pass.** Dispatch one `bb:bb-spec-reviewer` (read only by its own `tools:`) with `subagent_type: bb:bb-spec-reviewer`. The agent owns the contract and the finding shape; the prompt gives it the spec's full text, the spec's path and the repo root, because it may open the files the spec names. It reads the whole spec once. What it returns is resolved as it arrives, and it does not read the spec again in this round: every re-read of a fold finds new claims in the fold's own text, so a review that re-reads its corrections never closes. What a correction gets wrong reaches the build, where `bb-reuse-check`, the CI and `/bb:review` look.

**Each finding gets one outcome**:

- **Fixed**: the correction goes into the spec now. A risk the spec does not name goes into `## Attention points` the way the author would write it: the risk and where it lives, with no solution. An edge with no row gets its row, when the outcome is clear.
- **Rejected**, on a ground you state.
- **In `## Open`**, for what only the user can decide: an edge whose outcome nobody decided, a business rule missing or contradicting another. The gate already blocks on `## Open`, so the question reaches the user there.

Keep a running note of each finding and its outcome; it becomes the verdict line. None of it goes into the spec, and no finding is quietly dropped. Then run the lint and reopen the gate. What the review's own findings changed is not new text, so the gate reopens without `Review the spec`.

**Which text the review read.** The verdict stays out of the spec's frontmatter (plugin-level `references/spec-state.md`), so the record is this session's: the spec as it stood after the findings were folded in. A spec that differs from that record, and a spec this session never reviewed, carry text no review has read, and the gate offers the option. A gate in a later session has no record of an earlier review, so it offers the option.

**The verdict line**, in the words of the user's language: `not reviewed` before any review ran, `clean` when the review found nothing, otherwise its counts (`5 fixed, 1 rejected, 1 in ## Open`, leaving out a count of zero), or `did not run`. Under it, one line per rejected finding with the ground it was rejected on; the fixed ones are already in the spec, and the `## Open` ones are listed at the gate.

**The reviewer dying.** Without an Agent tool in this context, the review did not run: say so in the verdict line rather than showing a verdict that never ran. A reviewer that dies is dispatched once more over the same text; a second death reaches the gate as `did not run`. Either way no review read the text, so the gate keeps offering the option.

## Capture the alignment (lightweight, on disk)

Write a single `.bb/<slug>/spec.md`, the converged draft itself, written as something a person will read: an opening that says what this is and why now, then whatever sections describe this particular problem, then the fixed sections the other skills consume. The format (the two halves, the fixed sections and their readers, the table rule, attention points, the task line and its phases) lives in `references/spec-format.md`; follow it. There's no separate write-up step; the draft you iterated _is_ the spec, and it survives a context reset so a fresh session reloads it.

**The prose describes what to build.** How the conversation got there (what you first assumed, what a later read corrected, which message settled it) goes in the commit body instead. A landed spec that gets rewritten gains the new decision in the file and the reason in the commit.

The on-disk contract (location, frontmatter schema, status lifecycle) is the plugin-level `references/spec-state.md`; follow it. In short: specs go to `.bb/<slug>/spec.md`. If a spec already exists for a _different_ idea under the same slug, suffix it (`-2`) or ask; never silently overwrite another spec.

On finalize, open the spec with the frontmatter block (`status: pending`, `created: <today>`, `slug: <slug>`). This skill is the file's only writer, so the block is there from the first write. A spec landed before that rule can be missing it; backfill it on finalize. Leave the lifecycle after this to implement; spec only seeds `pending`.

The review's verdict is not part of the block: it belongs to this session, and it reaches the user at the gate, which is where a person can still act on it.

**Large** work carries `## Behavior`, `## Attention points` and `## Tasks` as their own sections: the acceptance contract, the risks the builder handles and the phased tasks the build side consumes. **Medium** work can keep the behavior and the tasks inline in the decisions. `## Metric` is its own section at every size, between `## Behavior` and `## Attention points`: the measure with provenance and the events table, or one explicit `skipped: <reason>` line (shape in `references/spec-format.md`).

## Export mode: a shareable product/UX spec

When the audience is beyond this session (a designer picking it up in Figma, a dev team without the spec's context, stakeholders), export the converged spec as a product spec document. Format, auto-sizing (spec/content/tasks), the hypothesis-OKR-metric trio rule, and UI copy voice rules live in `references/export-spec.md`; load it only when exporting. The spec in `.bb/` stays the source of truth; the export is a rendering of it.

## Don't fabricate

Before asserting how something works: check the codebase, then its docs, then the web; if you still don't know, **say so**. A wrong assumption here cascades into the build, and a draft full of confident guesses is worse than one that flags what it's unsure of. Uncertainty flagged beats confidence invented.

## Hand off: the gate decides whether to roll on

spec always ends at a validated `.bb/<slug>/spec.md`; the spec is the durable asset either way. What changes is what happens next, and the gate's two answers decide it. The step from speccing to building is a checkpoint the user crosses on purpose, not a stop. Every build path is the same skill, `/bb:implement <slug>`, at the scope the second answer sets:

- **Build, nothing ticked:** it loads this spec as the intent, builds every task, and stops ready to ship, where it offers `/bb:ship`.
- **Build, with `Review the branch`:** the tasks, then `/bb:review` over the branch, with the findings applied before that same offer.
- **Build, with `Ship`:** the tasks, then `/bb:ship` settles the destination and ships it.
- **Build, with both:** the review runs on the branch before the ship, so the fixes land in the same branch the tasks produced and the PR opens from code that was already read.
- **Stop here:** leave the spec and say the next step plainly: "Spec saved at `.bb/<slug>/spec.md`. To build it later: `/bb:implement <slug>`, which asks what runs after the build."

**Safety valve:** if building later reveals that a business rule or a behavior is missing, or contradicts another, the build stops and hands back here to re-spec. That's the signal alignment was incomplete. A technical gap is not: the task agent settles it and records the choice.

## Bundled resources

### references/spec-format.md

The spec's format: the free top half and the fixed sections, what each fixed section is read by, the describes-vs-recounts rule, the Metric section with its events table, tables, attention points, dead section names, and the task line with the `###` phases it runs in. Paired with `scripts/lint_spec.py`, which enforces the mechanical half.

### references/draft-first.md

The draft-first playbook: what a draft spec must cover, and how to surface the gray areas of what gets built as tool questions with a recommended pick instead of a wall of open prompts.

### references/export-spec.md

The shareable product/UX spec format (spec/content/tasks documents, the hypothesis-OKR-metric trio rule, UI copy voice), loaded only in export mode.
