---
name: spec
description: Align on the idea before building. Develops a draft, iterates the gray areas with you through the question tool, maps the expected behavior (happy path plus edges), runs an adversarial completeness pass and closes at a 3 way gate, implement / delegate / stop. Reads the framing from /bb:discover when it is there. Use when the user says "write the spec", "spec this out", "let's plan", "shape this", "what should we build", "let's discuss before building", or starts a non trivial feature. Don't use it for small mechanical changes (just do those) or to find bugs (use /bb:review).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 2.4.0
---

# Spec

Reach a **shared understanding of the idea before any code**. What matters is the alignment; the spec is where it lands: a document written to be read, not a form to fill. You and the model converge on what you're building, then build fast against it.

> The point was never a template; it was building context and discussing before building. The spec keeps that: the converged conversation, written down for whoever builds from it. (When someone downstream needs a shareable product/UX spec document, that's the export mode; see `references/export-spec.md`.)

## Auto-size by complexity

- **Tiny** (≤3 files, one obvious change): skip the spec; just build it.
- **Medium** (a clear feature): the loop (gray areas + reuse scan + the load-bearing technical forks + the behavior map: happy path + edges), then the gate.
- **Large / fuzzy** (new domain, real ambiguity): the full loop (reuse, the components and how data moves between them, the technical forks, the behavior map, break it into tasks), then the gate.

Always required: reach alignment, **close the load-bearing technical decisions, map the behavior**, and stop at a validated spec. Size is a running estimate, not locked at the start. If a "Tiny/Medium" task keeps surfacing gray areas mid-flow, re-size up and spec it properly.

## Read upstream intent first

If the spec for this slug already carries `## Problem` / `## Hypothesis` / `## Fit` / `## Cuts` (seeded by `/bb:discover`, or under the older names on a spec written before the rename), **read them before drafting**: they're the intent this work serves. The problem and success signal anchor the `why`, the appetite bounds the scope, and `## Fit` / `## Cuts` already settle what's in and what was deliberately dropped, so don't re-litigate a cut the user made upstream, and don't ask gray-area questions discover already answered. Echo the framing in one line so the user sees it carried through, then develop the design on top of it. No upstream sections is fine; spec from the one-liner as usual.

## The loop

You bring the idea; Claude develops it, then loops with you through the **`AskUserQuestion` tool** until the picture is consistent and you sign off. Never interrogate from a blank page, and never decide silently; drive it through real questions.

1. **Develop the draft (draft-first).** Read the one-liner, look at the codebase, and write a short draft spec with your best-guess decisions filled in: what/why, scope edges, reuse, the decisions you can already make. For Large work, also sketch the _how_ (next section) before breaking it into tasks. Bring something concrete to react to.

2. **Highest-stakes fork first, ask before you anchor.** On the single decision most expensive to undo, ask the user how _they'd_ call it _before_ you reveal your own pick (an open `AskUserQuestion`). Anchoring is strongest on the choice that matters most. Don't pre-frame that one. One fork only; everything else stays draft-first.

3. **Surface the gray areas as questions.** Everything else that genuinely could go more than one way → ask via `AskUserQuestion`, batched (the tool takes up to 4 at once), each as concrete options with your lean. Decide the obvious yourself; don't ask about what the codebase or goal already settles.

4. **Loop.** Fold each answer into the draft, re-surface anything new it opens, ask again. Keep going until a round surfaces no new gray areas.

5. **Adversarial completeness pass (when the gray areas run dry).** Don't _review_ the spec: try to **break** it; the same model that wrote the map approves it on a re-read. Two moves, looping anything they surface back to step 3:
   - **Run the generators** (`references/completeness-generators.md`) to manufacture questions along the axes omission hides in: input dimensions, external outputs' empty/limit/shape-change cases, state & lifecycle, failure & recovery, concurrency, trust boundary, data lifecycle, observability. Output is questions, not filled sections.
   - **Render the trace**: lay out behavior → task → test as a coverage table, not a mental check; every mapped behavior traces to a task and every task to a behavior. An unlinked row IS the omission, made visible rather than asserted. This is the table the gate shows; "I checked traceability" becomes proof the user can see.

   What you're hunting: (a) **unresolved load-bearing decisions** (a technical fork building can't proceed without, still blank or "TBD"); (b) **unmapped or unanswered behavior** (a happy-path step glossed over, an edge with no decided outcome); (c) **material contradictions**. Load-bearing gaps, behavior holes, and real conflicts only. Don't manufacture nitpicks, or the loop never closes.

6. **Check the spec: the lint, then the independent reviewer. Every spec that got written, every time.** This is a step of its own because it's the one an author skips: you cannot see your own omissions, and the pass that would catch them is the pass that feels redundant.

   First the lint (dead section names, malformed tables, a missing required section), so the gate spends its attention on completeness instead:

   ```bash
   python3 scripts/lint_spec.py .bb/<slug>/spec.md
   ```

   Then dispatch the `bb-spec-reviewer` agent (Agent tool) with the spec's path and **nothing else**: not a summary of the conversation, not which sections are new, not what to look for. Its mandate is its own system prompt, so don't re-compose it here; naming what to look for narrows it to what this context can already see, which is the half the review exists to cover. A reviewer with no memory of the conversation that produced the spec reads it the way the builder will, and the builder is now one fresh agent per task.

   It returns findings, each weighed `load-bearing` or `minor` with a one-line reason. Fold them all back into step 3's loop. The weight is the reviewer's, since it read the spec; the round is yours, since only you know what the fold changed:
   - **Round one is mandatory**, whatever the spec's size and however clean it looks.
   - **Round two runs when round one returned at least one `load-bearing` finding**, whatever section the fold touched, because a fold that closes a load-bearing gap is itself unreviewed text.
   - **Two rounds is the ceiling.** Anything still `load-bearing` after round two goes into `## Open`, where step 7's gate blocks on it exactly like an open decision.

   Without an Agent tool in this context, say so at the gate rather than showing a verdict that never ran.

7. **The exit gate: blocks on open load-bearing decisions.** Don't gate blind: first **show the artifact the user is signing off on**, a tight recap of the happy path, the full edge→outcome table, the **coverage table** (behavior → task → test) with `⚠️` on any unmapped row plus a one-line counter (`N behaviors, M mapped, K open`), and the **review's status** in one line, always: the reviewer's verdict (clean, or what it flagged and how it was resolved), or that it did not run and why, so "is this complete?" is answerable at a glance instead of forcing them to reopen the file. Then list what's **still open** (unresolved load-bearing decisions + parked questions). Then ask one `AskUserQuestion` (a handoff gate, with the format in the plugin-level `references/handoff-gate.md`):
   - **If any load-bearing decision is still open, or a `load-bearing` finding survived round two into `## Open`:** do NOT offer a clean "build". The only options are **resolve it now** or **defer explicitly** ("decide at build time", recorded as such in the spec). Never a silent "build anyway".
   - **If nothing load-bearing is open:** finalize `.bb/<slug>/spec.md` (with its frontmatter block; see "Capture the alignment"), then offer three paths: **Implement** (invoke `/bb:implement` now: build every task and stop ready to ship, where it offers `/bb:ship`), **Delegate** (invoke `/bb:delegate <slug>` now: build every task _and_ land it, the full `implement → ship` run), or **Stop here** (leave the spec; the user picks up later). Choosing to adjust instead is always available. That loops back into the question tool; an Implement or Delegate pick is the affirmative start, not a silent roll-through.

Size the ask to the stakes: cheap-to-reverse decisions lead with your pick (the user vetoes if wrong); expensive-to-undo ones lay the options out and let them choose. Full playbook in `references/draft-first.md`.

## Decide the technical forks (required for Medium+)

Before the gate, the load-bearing technical decisions must be **made or explicitly deferred**, not left implicit. Surface each that genuinely could go more than one way as a tool question (draft-first: your lean + the alternatives). Skip only what the codebase or goal already settles. Each fork closes as one bullet in `## Decisions`. When a fork is a **stack choice** (framework, package manager, tooling), consult the manifesto first (plugin-level `references/consult-manifesto.md`). The answer may already be settled company-wide.

- **Reuse**: what existing code, patterns, or modules this builds on. Name them (the cheapest guard against reinventing).
- **Data model / shape**: the entities, fields, and relationships, or the shape of the data flowing through.
- **Contracts & interfaces**: the function/API/CLI signatures and the boundaries between the pieces.
- **Where the logic lives**: which component/layer owns what, and how the pieces talk (a few bullets or mermaid lines for Large work, not a document).
- **Error & edge handling**: for each edge in the behavior map (below), decide _how_ it's handled (failure & rollback, validation, retries). Map the case in the behavior; decide the handling here.
- **Integration points**: the existing systems, dependencies, and external services it touches.

These are the decisions that cost the most _after_ you've built against them (expensive to undo), so they get closed here, before breaking it into tasks. A fork left open is what the gate blocks on. Architecture that needs more room than a bullet (a seam, a data flow, a diagram) is described in the spec's free top half, under the name it has in this problem (`references/spec-format.md`).

## Map the behavior (required for Medium+)

The behaviors are what guarantee the built thing matches the idea. An unmapped behavior is an unverified assumption about the final result; the completeness of this map is the fidelity between idea and outcome.

- **Happy path**: walk the main flow step by step and concretely: input → what happens → observable output. Every step the flow really takes gets a line.
- **Edge cases**: every meaningful deviation, each with its **expected outcome**, phrased `WHEN <case> THEN <observable outcome>` so each row reads directly as a test: empty / zero / huge input, invalid input, first-run vs repeat, concurrent use, failure & rollback, denied permission/auth, partial or interrupted runs, migrating existing data. Map the _outcome_, not just that the case exists.

Walking each behavior surfaces decisions you haven't made; those go back into the loop as gray areas, and each edge's outcome drives its handling in the technical forks. **A behavior with no decided outcome is an open item the gate blocks on.** Litmus for whether an edge's outcome is load-bearing (not just a minor case): **does its outcome contradict the `why`?** If choosing the wrong outcome would make the built thing betray its own reason for existing, it's load-bearing, and the gate blocks on it like any other fork. This map doubles as the acceptance criteria: each behavior is something `/bb:ship` and `/bb:review` check against, and each happy-path segment is a vertical task. Record it in a `## Behavior` section for Large work (happy path + an edge→outcome table); inline for Medium.

## Capture the alignment (lightweight, on disk)

Write a single `.bb/<slug>/spec.md`, the converged draft itself, written as something a person will read: an opening that says what this is and why now, then whatever sections describe this particular problem, then the fixed sections the other skills consume. The format (the two halves, the fixed sections and their readers, the table rule, the task shape) lives in `references/spec-format.md`; follow it. There's no separate write-up step; the draft you iterated _is_ the spec, and it survives a context reset so a fresh session reloads it.

**The prose describes what to build.** How the conversation got there (what you first assumed, what a later read corrected, which message settled it) goes in the commit body instead. A landed spec that gets rewritten gains the new decision in the file and the reason in the commit.

The on-disk contract (location, frontmatter schema, status lifecycle) is the plugin-level `references/spec-state.md`; follow it. In short: specs go to `.bb/<slug>/spec.md`. If a spec already exists for a _different_ idea under the same slug, suffix it (`-2`) or ask; never silently overwrite another spec.

On finalize, open the spec with the frontmatter block (`status: pending`, `created: <today>`, `slug: <slug>`). If `/bb:discover` wrote the file first without the block, backfill it on finalize. Leave the lifecycle after this to delegate; spec only seeds `pending`.

**Large** work carries `## Behavior` and `## Tasks` as their own sections: the acceptance contract and the vertical tasks the build side consumes. **Medium** work keeps both inline in the decisions.

## Export mode: a shareable product/UX spec

When the audience is beyond this session (a designer picking it up in Figma, a dev team without the spec's context, stakeholders), export the converged spec as a product spec document. Format, auto-sizing (spec/content/tasks), the hypothesis-OKR-metric trio rule, and UI copy voice rules live in `references/export-spec.md`; load it only when exporting. The spec in `.bb/` stays the source of truth; the export is a rendering of it.

## Don't fabricate

Before asserting how something works: check the codebase, then its docs, then the web; if you still don't know, **say so**. A wrong assumption here cascades into the build, and a draft full of confident guesses is worse than one that flags what it's unsure of. Uncertainty flagged beats confidence invented.

## Hand off: the gate decides whether to roll on

spec always ends at a validated `.bb/<slug>/spec.md`; the spec is the durable asset either way. What changes is what happens next, and the gate's 3-way pick (above) decides it. The step from speccing to building is a checkpoint the user crosses on purpose, not a stop.

- **Implement:** invoke `/bb:implement` now. It loads this spec as the intent, builds every task, and stops ready to ship, where it offers `/bb:ship`. The "build it, I'll decide on shipping after" path.
- **Delegate:** invoke `/bb:delegate <slug>` now. It loads this spec as the intent, builds every task, _and_ lands it (the full `/bb:implement` → `/bb:ship` run). The "I'm happy, run the whole thing" path.
- **Stop here:** leave the spec and say the next step plainly: "Spec saved at `.bb/<slug>/spec.md`. To build it later: `/bb:implement` (builds, then offers ship), or `/bb:delegate <slug>` to build and land in one run."

**Safety valve:** if building later reveals the idea was underspecified (surprises pile up), STOP and re-spec. That's the signal alignment was incomplete, not a license to improvise.

## Bundled resources

### references/spec-format.md

The spec's format: the free top half and the fixed sections, what each fixed section is read by, the describes-vs-recounts rule, tables, dead section names, and the task shape with its dependencies. Paired with `scripts/lint_spec.py`, which enforces the mechanical half.

### references/draft-first.md

The draft-first playbook: what a draft spec must cover, and how to surface the genuine forks as tool questions with a recommended pick instead of a wall of open prompts.

### references/completeness-generators.md

The question factory for the adversarial pass: omission-axes (inputs, external outputs, state, failure, concurrency, trust, data lifecycle, observability) turned into prompts that manufacture questions, not sections to fill.

### references/export-spec.md

The shareable product/UX spec format (spec/content/tasks documents, the hypothesis-OKR-metric trio rule, UI copy voice), loaded only in export mode.
