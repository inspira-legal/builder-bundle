---
name: spec
description: Align on the idea before building. Develops a draft, iterates the gray areas with you through the question tool, maps the expected behavior (happy path plus edges), runs an adversarial completeness pass and closes at a gate that also settles how far the build goes (build, build and ship, build review and ship, or stop). Reads the framing from /bb:discover and the journey from /bb:brisar when they are there. Use when the user says "write the spec", "spec this out", "let's plan", "shape this", "what should we build", "let's discuss before building", or starts a non trivial feature. Don't use it for small mechanical changes (just do those) or to find bugs (use /bb:review).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 2.8.0
---

# Spec

Reach a **shared understanding of the idea before any code**. What matters is the alignment; the spec is where it lands: a document written to be read, not a form to fill. You and the model converge on what you're building, then build fast against it.

> The point was never a template; it was building context and discussing before building. The spec keeps that: the converged conversation, written down for whoever builds from it. (When someone downstream needs a shareable product/UX spec document, that's the export mode; see `references/export-spec.md`.)

## Auto-size by complexity

- **Tiny** (≤3 files, one obvious change): skip the spec; just build it.
- **Medium** (a clear feature): the loop (gray areas + reuse scan + the load-bearing technical forks + the behavior map: happy path + edges), then the gate.
- **Large / fuzzy** (new domain, real ambiguity): the full loop (reuse, the components and how data moves between them, the technical forks, the behavior map, break it into tasks), then the gate.

Always required: reach alignment, **close the load-bearing technical decisions, map the behavior, run the check at step 6**, and stop at a validated spec. Size is a running estimate, not locked at the start. If a "Tiny/Medium" task keeps surfacing gray areas mid-flow, re-size up and spec it properly.

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
pointer that stays true. So don't re-litigate a cut the user made upstream, and don't ask
gray-area questions discover already answered. Echo the framing in one line, naming which
records exist, so the user sees it carried through, then develop the design on top of it.

Where a record and this spec disagree, **the spec wins**: it is the contract, they are the
records. The correction belongs to the record's own writer on its next round, so leave both
files alone. Either record missing is fine, and one arriving later is the normal case: brisar's
Deliver invokes this skill from its own gate. Spec from the one-liner as usual.

## The loop

You bring the idea; Claude develops it, then loops with you through the **`AskUserQuestion` tool** until the picture is consistent and you sign off. Never interrogate from a blank page, and never decide silently; drive it through real questions.

1. **Develop the draft (draft-first).** Read the one-liner, look at the codebase, and write a short draft spec with your best-guess decisions filled in: what/why, scope edges, reuse, the decisions you can already make. For Large work, also sketch the _how_ (next section) before breaking it into tasks. Bring something concrete to react to.

2. **Highest-stakes fork first, ask before you anchor.** On the single decision most expensive to undo, ask the user how _they'd_ call it _before_ you reveal your own pick (an open `AskUserQuestion`). Anchoring is strongest on the choice that matters most. Don't pre-frame that one. One fork only; everything else stays draft-first.

3. **Surface the gray areas as questions.** Everything else that genuinely could go more than one way → ask via `AskUserQuestion`, batched (the tool takes up to 4 at once), each as concrete options with your lean. Decide the obvious yourself; don't ask about what the codebase or goal already settles.

4. **Loop.** Fold each answer into the draft, re-surface anything new it opens, ask again. Keep going until a round surfaces no new gray areas.

5. **Adversarial completeness pass (when the gray areas run dry).** Don't _review_ the spec: try to **break** it; the same model that wrote the map approves it on a re-read. Two moves, looping anything they surface back to step 3:
   - **Run the generators** (`references/completeness-generators.md`) to manufacture questions along the axes omission hides in: input dimensions, external outputs' empty/limit/shape-change cases, state & lifecycle, failure & recovery, concurrency, trust boundary, data lifecycle, observability. Output is questions, not filled sections.
   - **Render the trace**: lay out behavior → task → test as a coverage table, not a mental check; every mapped behavior traces to a task and every task to a behavior. An unlinked row IS the omission, made visible rather than asserted. The gate shows the table's counter and its unlinked rows; "I checked traceability" becomes proof the user can see.

   What you're hunting: (a) **unresolved load-bearing decisions** (a technical fork building can't proceed without, still blank or "TBD"); (b) **unmapped or unanswered behavior** (a happy-path step glossed over, an edge with no decided outcome); (c) **material contradictions**. Load-bearing gaps, behavior holes, and real conflicts only. Don't manufacture nitpicks, or the loop never closes.

6. **Check the spec: the lint, then two independent lenses, three passes at most before the gate.** This is a step of its own because it's the one an author skips: you cannot see your own omissions, and the pass that would catch them is the pass that feels redundant.

   **Unconditional.** Every change reaches a lens before the build: the first draft, every fold, resolving an item from `## Open`, an answer that arrived after the gate, a revised decision on a landed spec. The size is no exemption, and whichever build option the gate is about to offer, a lens reads the change first. The one exception is the notes a routed pass writes into the spec (pass 3, or a pass at the gate): they land after the last lens read it, and the verdict line names them as read by no lens.

   First the lint (dead section names, malformed tables, a missing required section), so the gate spends its attention on completeness instead:

   ```bash
   python3 scripts/lint_spec.py .bb/<slug>/spec.md
   ```

   **The pass counter.** `scripts/review_pass.py` keeps the pass count and the last text the grounding lens read on disk, one entry per spec, so a context compaction loses neither. Pass the session's scratchpad directory as `--state`, so the count belongs to this session: a later session that reopens the spec starts at pass 1, with a full read. On a host with no scratchpad, leave the flag out and the script uses its own fixed directory, where a slug's state older than 12 hours starts again at pass 1.

   ```bash
   python3 scripts/review_pass.py next .bb/<slug>/spec.md --state <scratchpad>
   python3 scripts/review_pass.py read .bb/<slug>/spec.md --state <scratchpad>
   python3 scripts/review_pass.py reset .bb/<slug>/spec.md --state <scratchpad>
   ```

   Call `next` before every pass. It prints `run`, `pass`, `diff`, and `tally`. With `run: false` the spec is the text the grounding lens last read, so no pass runs and the run goes to the gate. With `run: true`, `pass` is the number of the pass about to run and `diff` is the change since that text, `null` when the grounding lens has read none. Call `read` once the grounding lens returns a verdict, clean or not. A grounding lens that died never gets a `read`, so the next `next` runs even over an unchanged spec and diffs against the last text it did read.

   `tally` is the path of a file beside the state, for what the gate reads back and no pass writes into the spec: each lens's counts over the run (resolved, rejected, routed to each place, a pass it did not run on) and the leftover list. Rewrite it after every pass, and build the verdict line and the leftover list from it at step 7, so a compaction between a pass and the gate loses neither. Call `reset` once the gate's pick moves on, a build or **Stop here**: it removes the state and the tally, so a later reopening of the spec in this session starts at pass 1 with a full read.

   **The lenses.** Both are `bb:bb-spec-reviewer` (read only by its own `tools:`), dispatched with `subagent_type: bb:bb-spec-reviewer` **in one message** so they run together. The agent owns the contract, the finding shape, and the delta pass's scope, so the prompt says which lens this one is, which kind of pass it is, and what it reads:
   - **Coherence** gets the spec's full text on every pass. It opens no files, so it is the cheap lens, and a contradiction between a changed section and an unchanged one is exactly what a diff would hide from it.
   - **Grounding** gets the spec's path and the repo root on every pass. When `diff` is `null` it is a **full pass** and also gets the spec's full text: pass 1, or a later pass after it died on every pass so far. Otherwise it is a **delta pass** and gets `diff` in place of the full text, and the prompt asks for nothing past that. The agent's contract sets what a delta pass checks, and a prompt cannot widen it.

   Running the grounding lens only when the coherence one came back empty would skip the expensive check exactly on the spec already showing signs of being sloppy.

   **Passes 1 and 2 fold.** Fold what they return back into step 3, with one exception: a **grounding finding that invalidates a `## Decisions` bullet, that names a file a task does not have, or that points at a thing the repo already does and the spec is about to rebuild, becomes an item in `## Open`**, which the gate already blocks on. Those three are what the grounding lens finds that the draft cannot absorb on its own. A finding rejected on a stated ground counts as dealt with; what none of them can be is quietly dropped. Then call `next` again: a pass whose findings were all rejected left the spec unchanged, so `next` reports `run: false` and the gate opens.

   **Pass 3 routes, it does not fold.** Nothing in the prose is rewritten after pass 3, and the gate opens next, with no fourth pass before it. A finding rejected on a stated ground still counts as dealt with. Each other finding goes to one place:
   - **`## Open`**, which the gate blocks on, for a load-bearing gap: a grounding finding of the three kinds above, and a coherence finding of a missing decision, a behavior with no decided outcome, an unmapped row (a happy path step with no task, a task with no behavior), or a contradiction.
   - **The task it names**, for any other grounding finding: a nested plain bullet under that task, indented two spaces so a formatter keeps it a list item, opening with `**Left for the build**:`. The task agent reads the whole spec before it builds, so the note reaches it, and a plain bullet is not a checkbox, so `scan_specs.py` does not count it as a task.
   - **The gate's leftover list**, for a grounding finding that names no task and a coherence finding of surplus (a repeated fact, prose that recounts the conversation). It does not block.

   **A change at the gate runs one delta pass.** Each change the user makes at the gate, resolving an `## Open` item or anything else, runs one pass like pass 2 and 3: `next`, both lenses, `read`, then its findings routed the way pass 3's are, and the gate again. Call `next` only after such a change: a gate where the user changes nothing runs no pass, and its pick goes on. The first delta pass at the gate also reads the notes pass 3 wrote, since they are part of the diff.

   **A lens dying.** Without an Agent tool in this context, the review did not run: say so at the gate rather than showing a verdict that never ran. When the grounding lens dies, skip `read` and carry on: the next pass hands it every change since the text it did read, or the whole spec if it has read none. On pass 3 there is no next pass, and the gate names it as not run on pass 3. When the coherence lens dies, dispatch it alone once more over the same text, with no `next` call and no pass counted; a second death reaches the gate as a lens that did not run on that pass. In both cases the survivor's findings fold or route as that pass does, and the gate names the lens that is missing, because a verdict shown without that caveat claims a pass the spec never got.

   **When `review_pass.py` fails** (exit 1, with a `review_pass:` line on stderr), stop calling it for this run. The remaining passes run full for both lenses, a pass runs when the spec changed since the last one, the run keeps the count in its own context, and the same three passes and the same routing hold. The verdict line names the failure.

7. **The exit gate: blocks on open load-bearing decisions.** Don't gate blind: first **show what the user is signing off on**, in the order a person reads to understand what gets built, so neither the what nor the order stays locked in the file:
   - **What it does and why**: two or three lines, the spec's opening said again.
   - **The tasks, in run order**: under their `###` phase headings (`references/spec-format.md`), one line per task saying what it changes, plus its `dep:` when something blocks it. This is the step by step. A spec with no phases lists its tasks flat, in document order.
   - **The load-bearing edges**: only the `WHEN … THEN …` rows whose wrong outcome would contradict the `why` (the litmus in "Map the behavior"), then a pointer to `## Behavior` for the rest.
   - **Coverage as a counter**: the line `N behaviors, M mapped, K open`, plus each unmapped row marked `⚠️` when there is one. The whole trace lives in the tasks' `→ behaviors` fields, so the gate shows only what is missing from it.
   - **The verdict line** (below).

   Then list what's **still open** (unresolved load-bearing decisions + parked questions), and after it the **leftover list** from step 6, marked as not blocking: the user decides there whether any of it becomes a change, and a change runs one delta pass before the gate shows again. Then ask one `AskUserQuestion` (a handoff gate, with the format in the plugin-level `references/handoff-gate.md`):
   - **If any load-bearing decision is still open:** do NOT offer a clean "build". The only options are **resolve it now** or **defer explicitly** ("decide at build time", recorded as such in the spec). Never a silent "build anyway".
   - **If nothing load-bearing is open:** finalize `.bb/<slug>/spec.md` (with its frontmatter block; see "Capture the alignment"), then offer four paths, three of which invoke `/bb:implement <slug>` now and differ only in **how far the run goes**: **Build** (every task, then it offers the ship), **Build and ship** (the tasks, then `/bb:ship`), **Build, review and ship** (the tasks, `/bb:review` over the branch, then `/bb:ship`), or **Stop here** (leave the spec; the user picks up later). **The pick is implement's scope answer**, so implement doesn't ask it again. Choosing to adjust instead is always available. That loops back into the question tool; a build pick is the affirmative start, not a silent roll-through.

   **The verdict line** has one part per lens, then the pass count, in the words of the user's language. A lens's part counts the whole run, not only its last pass, and is built from these pieces, leaving out a count of zero:

   | the lens over the run                | its part of the line                                  |
   | ------------------------------------ | ----------------------------------------------------- |
   | its last pass came back clean        | `clean`, plus `delta` for a grounding delta pass      |
   | it had findings before its last pass | `3 resolved, 1 rejected` before `clean`               |
   | its last pass rejected every finding | `1 rejected, clean`: the spec did not change          |
   | its last pass routed findings        | `did not close: 1 in ## Open, 4 in tasks, 2 leftover` |
   | it died on a pass                    | `did not run on pass 2`                               |

   After the parts, the line says `closed in 2 passes`; once a pass has run at the gate, `4 passes, 1 at the gate`; and `notes no lens read` while notes a routed pass wrote are still unread. When `review_pass.py` failed, the line opens with `review_pass.py failed: full passes`. A whole line reads `coherence: clean · grounding: 3 resolved, did not close: 1 in ## Open, 4 in tasks · 3 passes, notes no lens read`.

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

On finalize, open the spec with the frontmatter block (`status: pending`, `created: <today>`, `slug: <slug>`). This skill is the file's only writer, so the block is there from the first write. A spec landed before that rule can be missing it; backfill it on finalize. Leave the lifecycle after this to implement; spec only seeds `pending`.

Step 6's verdict is not part of the block: it belongs to this run, and it reaches the user at the gate, which is where a person can still act on it.

**Large** work carries `## Behavior` and `## Tasks` as their own sections: the acceptance contract and the vertical tasks the build side consumes. **Medium** work keeps both inline in the decisions.

## Export mode: a shareable product/UX spec

When the audience is beyond this session (a designer picking it up in Figma, a dev team without the spec's context, stakeholders), export the converged spec as a product spec document. Format, auto-sizing (spec/content/tasks), the hypothesis-OKR-metric trio rule, and UI copy voice rules live in `references/export-spec.md`; load it only when exporting. The spec in `.bb/` stays the source of truth; the export is a rendering of it.

## Don't fabricate

Before asserting how something works: check the codebase, then its docs, then the web; if you still don't know, **say so**. A wrong assumption here cascades into the build, and a draft full of confident guesses is worse than one that flags what it's unsure of. Uncertainty flagged beats confidence invented.

## Hand off: the gate decides whether to roll on

spec always ends at a validated `.bb/<slug>/spec.md`; the spec is the durable asset either way. What changes is what happens next, and the gate's 4-way pick (above) decides it. The step from speccing to building is a checkpoint the user crosses on purpose, not a stop. Every build path is the same skill, `/bb:implement <slug>`, at the scope the pick sets:

- **Build:** it loads this spec as the intent, builds every task, and stops ready to ship, where it offers `/bb:ship`. The "build it, I'll decide on shipping after" path.
- **Build and ship:** the tasks, then `/bb:ship` settles the destination and ships it. The "I'm happy, run the whole thing" path.
- **Build, review and ship:** the same, with `/bb:review` over the branch first, so the fixes land in the same commits the tasks produced and the PR opens from code that was already read.
- **Stop here:** leave the spec and say the next step plainly: "Spec saved at `.bb/<slug>/spec.md`. To build it later: `/bb:implement <slug>`, which asks how far to go."

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
