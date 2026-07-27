---
name: spec
description: Alinhar a ideia antes de construir — desenvolve um draft, itera as zonas cinzentas com você via question tool (decisões técnicas load-bearing E um mapa de comportamento meticuloso — happy path + edges com outcome esperado), roda um passe adversarial de completude (geradores + revisor independente + rastreabilidade comportamento↔slice) e fecha num gate de 3 vias implement / delegate / parar. Auto-dimensiona por complexidade. Lê as seções upstream `## problem` / `## hypothesis` / `## fit` do /bb:discover quando presentes. Use quando o usuário disser "faz o spec", "especifica isso", "vamos planejar", "shape this", "o que a gente deveria construir", "discutir antes de construir", ou começar uma feature não-trivial. NÃO use pra mudanças mecânicas pequenas (só faça), nem pra achar bugs (use /bb:review).
license: MIT
metadata:
  author: Athena Briana - github.com/athenabriana
  version: 2.0.0
---

# Spec

Reach a **shared understanding of the idea before any code**. The asset that matters is the alignment, not a document — you and the model converge on the _shape_ of what you're building, then build fast against it.

> The point was never the spec document; it was building context and discussing before building. This keeps that and drops the ceremony. (When someone downstream needs a shareable product/UX spec document, that's the export mode — see `references/export-spec.md`.)

## Auto-size by complexity

- **Tiny** (≤3 files, one obvious change): skip shaping — just build it.
- **Medium** (a clear feature): the loop — gray areas + reuse scan + the load-bearing technical forks + the behavior map (happy path + edges), then the gate.
- **Large / fuzzy** (new domain, real ambiguity): the full loop — reuse + components + data-flow design, the technical forks, the behavior map, slice into pieces, then the gate.

Always required: reach alignment, **close the load-bearing technical decisions, map the behavior**, and stop at a validated brief. Size is a running estimate, not locked at the start — if a "Tiny/Medium" task keeps surfacing gray areas mid-flow, re-size up and shape it properly.

## Read upstream intent first

If the brief for this slug already carries `## problem` / `## hypothesis` / `## fit` / `## cuts` (seeded by `/bb:discover`), **read them before drafting** — they're the intent this work serves. The problem and success signal anchor the `why`, the appetite bounds the scope, and `## fit` / `## cuts` already settle what's in and what was deliberately dropped — so don't re-litigate a cut the user made upstream, and don't ask gray-area questions discover already answered. Echo the framing in one line so the user sees it carried through, then develop the design on top of it. No upstream sections is fine — spec from the one-liner as usual.

## The loop

You bring the idea; Claude develops it, then loops with you through the **`AskUserQuestion` tool** until the picture is consistent and you sign off. Never interrogate from a blank page, and never decide silently — drive it through real questions. All question text the user sees is PT-BR.

1. **Develop the draft (draft-first).** Read the one-liner, look at the codebase, and write a short draft brief with your best-guess decisions filled in — what/why, scope edges, reuse, the decisions you can already make. For Large work, also sketch the _how_ (next section) before slicing. Bring something concrete to react to.

2. **Highest-stakes fork first — ask before you anchor.** On the single decision most expensive to undo, ask the user how _they'd_ call it _before_ you reveal your own pick (an open `AskUserQuestion`). Anchoring is strongest on the choice that matters most — don't pre-frame that one. One fork only; everything else stays draft-first.

3. **Surface the gray areas as questions.** Everything else that genuinely could go more than one way → ask via `AskUserQuestion`, batched (the tool takes up to 4 at once), each as concrete options with your lean. Decide the obvious yourself; don't ask about what the codebase or goal already settles.

4. **Loop.** Fold each answer into the draft, re-surface anything new it opens, ask again. Keep going until a round surfaces no new gray areas.

5. **Adversarial completeness pass (when the gray areas run dry).** Don't _review_ the brief — try to **break** it; the same model that wrote the map rubber-stamps it on a re-read. Three moves, looping anything they surface back to step 3:
   - **Run the generators** (`references/completeness-generators.md`) to manufacture questions along the axes omission hides in — input dimensions, external outputs' empty/limit/shape-change cases, state & lifecycle, failure & recovery, concurrency, trust boundary, data lifecycle, observability. Output is questions, not filled sections.
   - **Spawn an independent reviewer** (Agent tool, fresh context) given ONLY the brief and the mandate _"you did not write this — find what's missing, unmapped, or self-contradicting."_ The author can't see its own omissions; a reviewer with no memory of the conversation that produced the brief can. **Run it for every Medium-and-up brief** — one fan-out is cheap against a hole the gate then certifies as closed. Carry its verdict to the gate (the gate shows it).
   - **Render the trace** — lay out behavior → slice → test as a coverage table, not a mental check: every mapped behavior traces to a slice and every slice to a behavior. An unlinked row IS the omission — made visible rather than asserted. This is the table the gate shows; "I checked traceability" becomes proof the user can see.

   What you're hunting: (a) **unresolved load-bearing decisions** (a technical fork building can't proceed without, still blank or "TBD"); (b) **unmapped or unanswered behavior** (a happy-path step glossed over, an edge with no decided outcome); (c) **material contradictions**. Load-bearing gaps, behavior holes, and real conflicts only — don't manufacture nitpicks, or the loop never closes.

6. **The exit gate — blocks on open load-bearing decisions.** Don't gate blind: first **show the artifact the user is signing off on** — a tight recap of the happy path, the full edge→outcome table, the **coverage table** (behavior → slice → test) with `⚠️` on any unmapped row plus a one-line counter (`N behaviors, M mapped, K open`), and (Medium+) the **independent reviewer's verdict** in one line (clean, or what it flagged and how it was resolved) — so "is this complete?" is answerable at a glance instead of forcing them to reopen the file. Then list what's **still open** (unresolved load-bearing decisions + parked questions). Then ask one `AskUserQuestion` (a handoff gate — format in the plugin-level `references/handoff-gate.md`):
   - **If any load-bearing decision is still open:** do NOT offer a clean "build". The only options are **resolve it now** or **defer explicitly** ("decide at build time" — recorded as such in the brief). Never a silent "build anyway".
   - **If nothing load-bearing is open:** finalize `.bb/tasks/<slug>/spec.md` (with its frontmatter block — see "Capture the alignment"), then offer three paths — **Implementar** (invoke `/bb:implement` now: build every slice and stop ready to ship, where it offers `/bb:ship`), **Delegar** (invoke `/bb:delegate <slug>` now: build every slice _and_ land it, the full `implement → ship` run), or **Encerrar aqui** (leave the brief; the user picks up later). Choosing to adjust instead is always available — that loops back into the question tool; an Implementar or Delegar pick is the affirmative start, not a silent roll-through.

Size the ask to the stakes: cheap-to-reverse decisions lead with your pick (the user vetoes if wrong); expensive-to-undo ones lay the options out and let them choose. Full playbook in `references/draft-first.md`.

## Decide the technical forks (required for Medium+)

Before the gate, the load-bearing technical decisions must be **made or explicitly deferred** — not left implicit. Surface each that genuinely could go more than one way as a tool question (draft-first: your lean + the alternatives). Skip only what the codebase or goal already settles. Don't write a design document — close the decisions. When a fork is a **stack choice** (framework, package manager, tooling), consult the manifesto first (plugin-level `references/consult-manifesto.md`) — the answer may already be settled company-wide.

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

Walking each behavior surfaces decisions you haven't made — those go back into the loop as gray areas, and each edge's outcome drives its handling in the technical forks. **A behavior with no decided outcome is an open item the gate blocks on.** Litmus for whether an edge's outcome is load-bearing (not just a minor case): **does its outcome contradict the `why`?** If choosing the wrong outcome would make the built thing betray its own reason for existing, it's load-bearing, and the gate blocks on it like any other fork. This map doubles as the acceptance criteria: each behavior is something `/bb:ship` and `/bb:review` check against, and each happy-path segment is a vertical slice. Record it in a `## behavior` section for Large work (happy path + an edge→outcome table); inline for Medium.

## Capture the alignment (lightweight, on disk)

Write a single `.bb/tasks/<slug>/spec.md` — the converged draft itself: **what** we're building, **why**, the **decisions** made (including what to reuse), what's **out of scope** (including ideas parked for later, each marked _revisit_), and what's **still open**. Keep out-of-scope and open items as plain bullets — never checkboxes, so the task selector never mistakes them for work. Everything lives in one file so editing it later carries the full context; there's no separate write-up step, the draft you iterated _is_ the brief. This is durable context (survives a context reset; a fresh session or an unattended run reloads it), **not** a contract to satisfy line-by-line.

The on-disk contract — location, frontmatter schema, status lifecycle — is the plugin-level `references/task-state.md`; follow it. In short: briefs go to `.bb/tasks/<slug>/spec.md`. If a brief already exists for a _different_ idea under the same slug, suffix it (`-2`) or ask — never silently overwrite another brief.

On finalize, open the brief with the frontmatter block (`status: pending`, `created: <today>`, `slug: <slug>`). If `/bb:discover` wrote the file first without the block, backfill it on finalize. Leave the lifecycle after this to delegate — spec only seeds `pending`.

For **Large** work, capture the closed technical decisions in a `## design` section — components and their boundaries, the data model, key data flows, and the decisions that bite — so the architecture is reviewable as one block and the build side reads it as the intent. **Medium** work keeps these inline in the decisions above; no `## design` block (that would be ceremony for a small feature).

For Large work, also capture the **behavior map** in a `## behavior` section — the happy path step by step plus an edge→outcome table whose rows are phrased `WHEN … THEN …` (each row a test). It's the acceptance contract the build and review check against (Medium keeps it inline).

Also for Large work, add a `## tasks` section to the same file — **vertical slices** (each a thin end-to-end cut that delivers something visible) as a GitHub-style checklist (`- [ ]`) the build side consumes. **Each slice cites the behavior(s) it delivers, and every mapped behavior has at least one slice** — that two-way trace is what makes an omission show up as an unlinked item rather than a silent gap, and it's what the gate renders as the coverage table.

## Export mode — a shareable product/UX spec

When the audience is beyond this session — a designer picking it up in Figma, a dev team without the brief's context, stakeholders — export the converged brief as a product spec document. Format, auto-sizing (spec/content/tasks), the hypothesis-OKR-metric trio rule, and UI copy voice rules live in `references/export-spec.md`; load it only when exporting. The brief in `.bb/tasks/` stays the source of truth; the export is a rendering of it.

## Don't fabricate

Before asserting how something works: check the codebase, then its docs, then the web; if you still don't know, **say so**. A wrong assumption here cascades into the build — and a draft full of confident guesses is worse than one that flags what it's unsure of. Uncertainty flagged beats confidence invented.

## Hand off — the gate decides whether to roll on

spec always ends at a validated `.bb/tasks/<slug>/spec.md`; the brief is the durable asset either way. What changes is what happens next, and the gate's 3-way pick (above) decides it — the seam between shaping and building is a checkpoint the user crosses on purpose, not a wall.

- **Implementar:** invoke `/bb:implement` now — it loads this brief as the intent, builds every slice, and stops ready to ship, where it offers `/bb:ship`. The "build it, I'll decide on shipping after" path.
- **Delegar:** invoke `/bb:delegate <slug>` now — it loads this brief as the intent, builds every slice, _and_ lands it (the full `/bb:implement` → `/bb:ship` run, the same verb the overnight routine uses). The "I'm happy, run the whole thing" path.
- **Encerrar aqui:** leave the brief and say the next step plainly — "Brief salvo em `.bb/tasks/<slug>/spec.md`. Pra construir depois: `/bb:implement` (constrói, depois oferece ship), ou `/bb:delegate <slug>` pra construir + landar de uma vez." For an unattended overnight run, point to the routine guide (`references/routines.md` at the plugin root): commit the brief, then schedule `/bb:delegate <slug>` under `BB_UNATTENDED`.

**Safety valve:** if building later reveals the idea was underspecified (surprises pile up), STOP and re-spec — that's the signal alignment was incomplete, not a license to improvise.

## Bundled Resources

### references/draft-first.md

The draft-first playbook — what a draft brief must cover, and how to surface the genuine forks as tool questions with a recommended pick instead of a wall of open prompts.

### references/completeness-generators.md

The question factory for the adversarial pass — omission-axes (inputs, external outputs, state, failure, concurrency, trust, data lifecycle, observability) turned into prompts that manufacture questions, not sections to fill.

### references/export-spec.md

The shareable product/UX spec format (spec/content/tasks documents, the hypothesis-OKR-metric trio rule, UI copy voice) — loaded only in export mode.
