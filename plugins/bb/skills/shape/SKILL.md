---
name: shape
description: Align on the idea before building — Claude develops a draft, loops with you through the question tool on the gray areas (the load-bearing technical decisions AND a meticulous behavior map — happy path + edge cases with expected outcomes), runs an adversarial completeness pass (generators + an independent reviewer subagent + behavior↔task traceability), and gates on a three-way implement / delegate / stop pick, blocking while any load-bearing decision or behavior is still open. Auto-sizes by complexity. Reads upstream `## problem` / `## hypothesis` / `## fit` from /ofc:frame-problem and /ofc:assess-fit when present, building the design on the framed intent. Use when the user says "shape this", "let's plan", "think this through", "what should we build", "discuss before building", or starts a non-trivial feature or project. Do NOT use for tiny mechanical changes (just do them), for code-quality cleanups (use /ofc:tidy), or to find bugs (use /ofc:ship).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 1.14.0
---

# Shape

Reach a **shared understanding of the idea before any code**. The asset that matters is the alignment, not a document — you and the model converge on the _shape_ of what you're building, then build fast against it.

> Replaces the old spec-driven flow. The point was never the spec; it was building context and discussing before building. This keeps that and drops the ceremony.

## Auto-size by complexity

- **Tiny** (≤3 files, one obvious change): skip shaping — just build it.
- **Medium** (a clear feature): the loop — gray areas + reuse scan + the load-bearing technical forks + the behavior map (happy path + edges), then the gate.
- **Large / fuzzy** (new domain, real ambiguity): the full loop — reuse + components + data-flow design, the technical forks, the behavior map, slice into pieces, then the gate.

Always required: reach alignment, **close the load-bearing technical decisions, map the behavior**, and stop at a validated brief. Size is a running estimate, not locked at the start — if a "Tiny/Medium" task keeps surfacing gray areas mid-flow, re-size up and shape it properly.

## Read upstream intent first

If `.ofc/tasks/<slug>/shape.md` already carries `## problem` / `## hypothesis` (from `/ofc:frame-problem`) or `## fit` / `## cuts` (from `/ofc:assess-fit`), **read them before drafting** — they're the intent this work serves. The problem and success signal anchor the `why`, the appetite bounds the scope, and `## fit` / `## cuts` already settle what's in and what was deliberately dropped — so don't re-litigate a cut the user made upstream, and don't ask gray-area questions the trio already answered. Echo the framing in one line so the user sees it carried through, then develop the design on top of it. No upstream sections is fine — shape from the one-liner as usual.

## The loop

You bring the idea; Claude develops it, then loops with you through the **`AskUserQuestion` tool** until the picture is consistent and you sign off. Never interrogate from a blank page, and never decide silently — drive it through real questions.

1. **Develop the draft (draft-first).** Read the one-liner, look at the codebase, and write a short draft brief with your best-guess decisions filled in — what/why, scope edges, reuse, the decisions you can already make. For Large work, also sketch the _how_ (next section) before slicing. Bring something concrete to react to.

2. **Highest-stakes fork first — ask before you anchor.** On the single decision most expensive to undo, ask the user how _they'd_ call it _before_ you reveal your own pick (an open `AskUserQuestion`). Anchoring is strongest on the choice that matters most — don't pre-frame that one. One fork only; everything else stays draft-first.

3. **Surface the gray areas as questions.** Everything else that genuinely could go more than one way → ask via `AskUserQuestion`, batched (the tool takes up to 4 at once), each as concrete options with your lean. Decide the obvious yourself; don't ask about what the codebase or goal already settles.

4. **Loop.** Fold each answer into the draft, re-surface anything new it opens, ask again. Keep going until a round surfaces no new gray areas.

5. **Adversarial completeness pass (when the gray areas run dry).** Don't _review_ the brief — try to **break** it; the same model that wrote the map rubber-stamps it on a re-read. Three moves, looping anything they surface back to step 3:
   - **Run the generators** (`references/completeness-generators.md`) to manufacture questions along the axes omission hides in — input dimensions, external outputs' empty/limit/shape-change cases, state & lifecycle, failure & recovery, concurrency, trust boundary, data lifecycle, observability. Output is questions, not filled sections.
   - **Spawn an independent reviewer** (Agent tool, fresh context) given ONLY the brief and the mandate _"you did not write this — find what's missing, unmapped, or self-contradicting."_ The author can't see its own omissions; a reviewer with no memory of the conversation that produced the brief can. **Run it for every Medium-and-up brief** — one fan-out is cheap against a hole the gate then certifies as closed. Carry its verdict to the gate (the gate shows it).
   - **Render the trace** — lay out behavior → slice → test as a coverage table, not a mental check: every mapped behavior traces to a slice and every slice to a behavior. An unlinked row IS the omission — made visible rather than asserted. This is the table the gate shows; "I checked traceability" becomes proof the user can see.

   What you're hunting: (a) **unresolved load-bearing decisions** (a technical fork building can't proceed without, still blank or "TBD"); (b) **unmapped or unanswered behavior** (a happy-path step glossed over, an edge with no decided outcome); (c) **material contradictions**. Load-bearing gaps, behavior holes, and real conflicts only — don't manufacture nitpicks, or the loop never closes.

6. **The exit gate — blocks on open load-bearing decisions.** Don't gate blind: first **show the artifact the user is signing off on** — a tight recap of the happy path, the full edge→outcome table, the **coverage table** (behavior → slice → test) with `⚠️` on any unmapped row plus a one-line counter (`N behaviors, M mapped, K open`), and (Medium+) the **independent reviewer's verdict** in one line (clean, or what it flagged and how it was resolved) — so "is this complete?" is answerable at a glance instead of forcing them to reopen the file. Rendering the coverage and the verdict is what turns the completeness pass from a claim into something the user can verify. Then list what's **still open** (unresolved load-bearing decisions + parked questions). Then ask one `AskUserQuestion`:
   - **If any load-bearing decision is still open:** do NOT offer a clean "build". The only options are **resolve it now** or **defer explicitly** ("decide at build time" — recorded as such in the brief). Never a silent "build anyway".
   - **If nothing load-bearing is open:** finalize `.ofc/tasks/<slug>/shape.md` (with its frontmatter block — see "Capture the alignment"), then offer three paths — **Implement** (invoke `/ofc:implement` now: build every slice and stop ready to ship, where it offers `/ofc:ship`), **Delegate** (invoke `/ofc:delegate <slug>` now: build every slice _and_ land it, the full `implement → ship` run), or **Stop here** (leave the brief; the user picks up later). Choosing to adjust instead is always available — that loops back into the question tool; an Implement or Delegate pick is the affirmative start, not a silent roll-through.

Size the ask to the stakes: cheap-to-reverse decisions lead with your pick (the user vetoes if wrong); expensive-to-undo ones lay the options out and let them choose. Full playbook in `references/draft-first.md`.

## Decide the technical forks (required for Medium+)

Before the gate, the load-bearing technical decisions must be **made or explicitly deferred** — not left implicit. This is the substance the old Design phase carried; surface each that genuinely could go more than one way as a tool question (draft-first: your lean + the alternatives). Skip only what the codebase or goal already settles. Don't write a design document — close the decisions.

- **Reuse** — what existing code, patterns, or modules this builds on. Name them (the cheapest guard against reinventing).
- **Data model / shape** — the entities, fields, and relationships, or the shape of the data flowing through.
- **Contracts & interfaces** — the function/API/CLI signatures and the boundaries between the pieces.
- **Where the logic lives** — which component/layer owns what, and how the pieces talk (a few bullets or mermaid lines for Large work, not a document).
- **Error & edge handling** — for each edge in the behavior map (below), decide _how_ it's handled (failure & rollback, validation, retries). Map the case in the behavior; decide the handling here.
- **Integration points** — what it touches: existing systems, dependencies, external services.

These are the decisions that bite _after_ you've built against them — expensive to undo — so they get closed here, before slicing. A fork left open is what the gate blocks on. For Large work, record the closed decisions in the brief's `## design` section; for Medium, inline in the decisions.

## Map the behavior (required for Medium+)

The behaviors are what guarantee the built thing matches the idea — so map them **meticulously, not as a sketch**. An unmapped behavior is an unverified assumption about the final result; the completeness of this map is the fidelity between idea and outcome.

- **Happy path** — walk the main flow step by step and concretely: input → what happens → observable output. Don't abbreviate; the steps you skip are the gaps that surface in review.
- **Edge cases** — every meaningful deviation, each with its **expected outcome**, phrased `WHEN <case> THEN <observable outcome>` so each row reads directly as a test: empty / zero / huge input, invalid input, first-run vs repeat, concurrent use, failure & rollback, denied permission/auth, partial or interrupted runs, migrating existing data. Map the _outcome_, not just that the case exists.

Walking each behavior surfaces decisions you haven't made — those go back into the loop as gray areas, and each edge's outcome drives its handling in the technical forks. **A behavior with no decided outcome is an open item the gate blocks on.** Litmus for whether an edge's outcome is load-bearing (not just a minor case): **does its outcome contradict the `why`?** If choosing the wrong outcome would make the built thing betray its own reason for existing — a privacy app that leaks, a grounded-answer tool that hallucinates when retrieval is empty — it's load-bearing, and the gate blocks on it like any other fork. The "error & edge handling" bullet is generic; this test is what promotes a specific edge to load-bearing. This map doubles as the acceptance criteria: each behavior is something `/ofc:ship` and the local gate check against, and each happy-path segment is a vertical slice. Record it in a `## behavior` section for Large work (happy path + an edge→outcome table); inline for Medium.

## Capture the alignment (lightweight, on disk)

Write a single `.ofc/tasks/<slug>/shape.md` — the converged draft itself: **what** we're building, **why**, the **decisions** made (including what to reuse), what's **out of scope** (including ideas parked for later, each marked _revisit_), and what's **still open**. Keep out-of-scope and open items as plain bullets — never checkboxes, so the task selector never mistakes them for work. Everything lives in one file so editing it later carries the full context; there's no separate write-up step, the draft you iterated _is_ the brief. This is durable context (survives a context reset; a fresh session or the overnight loop reloads it), **not** a contract to satisfy line-by-line.

`<slug>` is a short kebab name for the idea. If `.ofc/tasks/<slug>/shape.md` already exists for a _different_ idea, suffix it (`-2`) or ask — never silently overwrite another brief.

On finalize, open the brief with the **frontmatter block** that `/ofc:delegate` and a Cloud Routine select and track on (schema in `.claude/CLAUDE.md`):

```yaml
---
status: pending
created: <today, YYYY-MM-DD>
slug: <slug>
---
```

Always `status: pending` (no slice built yet); `created` is today; `slug` matches the dir. If an upstream skill (`/ofc:frame-problem`, `/ofc:assess-fit`) wrote the file first without the block, backfill it on finalize. Leave the lifecycle after this to delegate — shape only seeds `pending`.

For **Large** work, capture the closed technical decisions in a `## design` section — components and their boundaries, the data model, key data flows, and the decisions that bite — so the architecture is reviewable as one block and the build side (`/ofc:implement`, then `/ofc:ship`) reads it as the intent. **Medium** work keeps these inline in the decisions above; no `## design` block (that would be ceremony for a small feature).

For Large work, also capture the **behavior map** in a `## behavior` section — the happy path step by step plus an edge→outcome table whose rows are phrased `WHEN … THEN …` (each row a test). It's the acceptance contract the build and review check against (Medium keeps it inline).

Also for Large work, add a `## tasks` section to the same file — **vertical slices** (each a thin end-to-end cut that delivers something visible) as a GitHub-style checklist (`- [ ]`) the build side consumes. **Each slice cites the behavior(s) it delivers, and every mapped behavior has at least one slice** — that two-way trace is what makes an omission show up as an unlinked item rather than a silent gap, and it's what the gate renders as the coverage table.

## Don't fabricate

Before asserting how something works: check the codebase, then its docs, then the web; if you still don't know, **say so**. A wrong assumption here cascades into the build — and a draft full of confident guesses is worse than one that flags what it's unsure of. Uncertainty flagged beats confidence invented.

## Hand off — the gate decides whether to roll on

shape always ends at a validated `.ofc/tasks/<slug>/shape.md`; the brief is the durable asset either way. What changes is what happens next, and the gate's 3-way pick (above) decides it — the seam between shaping and building is a checkpoint the user crosses on purpose, not a wall.

- **Implement:** invoke `/ofc:implement` now — it loads this brief as the intent, builds every slice, and stops ready to ship, where it offers `/ofc:ship`. The "build it, I'll decide on shipping after" path.
- **Delegate:** invoke `/ofc:delegate <slug>` now — it loads this brief as the intent, builds every slice, _and_ lands it (the full `/ofc:implement` → `/ofc:ship` run, the same verb the overnight routine uses). The "I'm happy, run the whole thing" path.
- **Stop here:** leave the brief and say the next step plainly — "Brief saved at `.ofc/tasks/<slug>/shape.md`. To build it later: `/ofc:implement` (build, then offers ship), or `/ofc:delegate <slug>` to build + ship in one go." For an unattended overnight run, point to the routine guide (`references/routines.md` at the plugin root): commit the brief, then schedule `/ofc:delegate <slug>` under `OFC_UNATTENDED`.

**Safety valve:** if building later reveals the idea was underspecified (surprises pile up), STOP and re-shape — that's the signal alignment was incomplete, not a license to improvise.

## Bundled Resources

### references/draft-first.md

The draft-first playbook — what a draft brief must cover, and how to surface the genuine forks as tool questions with a recommended pick instead of a wall of open prompts.

### references/completeness-generators.md

The question factory for the adversarial pass — omission-axes (inputs, external outputs, state, failure, concurrency, trust, data lifecycle, observability) turned into prompts that manufacture questions, not sections to fill.
