# Research phase — the first diamond of design

Loaded after Phase 2 (maturity gate) and before the medium question. This is where the
solution space gets mapped **before** anything is drawn. It ends in the Brief phase
(`references/brief.md`), which is the written contract the rest of the trilha reads.

**This phase does not draw, does not scaffold, does not decide the direction.** It gathers
what a senior designer would gather before touching a canvas, and it gathers it from the
real sources — the market, the production design system, and the product itself.

Two rules that define the phase:

1. **The floor never scales down** (see Step 1). Every mode runs it.
2. **What is skipped is said out loud.** Silent cuts read as "we covered everything" when we
   didn't.

## Why it exists

Without this phase brisar goes from "I have an idea" to "here is a surface" with nothing in
between but the builder's own repertoire. The screen may be beautiful and answer the wrong
question — and there is no artifact to argue with later.

The evidence that this is the load-bearing phase: it is the one that finds the things nobody
asked for. Reading the token source from disk reveals that the type scale stops at 32px and
there is no shadow token at all, which kills a whole class of commercial layout before it is
drawn. Reading the repo reveals screenshots and page shells that already exist, so the
"new" thing was half-built. Reading the market reveals that a pattern the builder assumed
was standard appears in **zero** of 18 references. None of that comes from asking the
builder.

## Cross-awareness with the session

Before any question, read `.brisar/session.yaml` in full:

- **`gate.discover_brief`** (`.bb/tasks/<slug>/spec.md` with `## problem` / `## hypothesis` /
  `## fit` / `## cuts`) — this is the **upstream contract**. The research answers _how should
  this be?_; the discover brief answered _is it worth building, and what did we cut?_ Load it:
  the hypothesis tells you what the research must test, and the cuts tell you what **not** to
  research a solution for.
  - **A cut is a constraint, not a taboo.** If the research finds a cut was wrong, that is a
    legitimate finding and it goes in the brief's reconciliation section — with the argument.
    Never silently design on top of a cut.
- **`preflight.product`** — settles where the design system lives (`ds_source`).
- **`intent.raw_prompt`** — the builder's own words. Often carries the constraint that matters
  most, phrased casually.
- If a project spec exists (a full behavior contract, not just the discover sections), read it
  too: variants, states and conditional blocks are the shape the research has to serve.

Write your output to the `research:` section of session.yaml and set
`current_phase: research`.

## Step 0 — Calibrate depth, and say it in one line

Judge the depth from what you already have; **do not ask**. Signals, in order of weight:

| Signal                                                             | Pushes toward       |
| ------------------------------------------------------------------ | ------------------- |
| No spec, no discover brief, one surface, adjustment-shaped request | `pocket`            |
| Builder said "rápido", "simples", "só uma tela"                    | `pocket`            |
| Discover brief with small appetite                                 | `pocket`            |
| New surface with no precedent in the product                       | `full`              |
| Contract with multiple variants/states, or a metric attached       | `full`              |
| Commercial/persuasive surface, or a novel interaction              | `full`              |
| Builder said "com profundidade", "pesquisa a fundo"                | `full`              |
| The hardest composition has no market repertoire                   | `full`, and say why |

Then print **one line**, before running anything:

> **Pesquisa — modo `pocket`.** Vou rodar o piso: referências no Mobbin, o design system lido
> da fonte, e a resposta sobre componente novo. **Pulei** vieses comportamentais — o padrão
> aqui é conhecido e o ganho não paga a rodada. Se quiser, peço e rodo.

The line has three parts and all three are mandatory: **the mode · what runs · what was
skipped and why**. "Nothing was skipped" is a valid third part in `full` mode.

## Step 1 — The floor (runs in every mode, no exceptions)

Three fronts. They are the floor because each one has been the source of a finding that
changed the design, and none of them can be replaced by the builder's memory.

### Front A — Market bench (Mobbin)

Use `search_screens` **and** `search_flows` — the flow around the screen matters as much as
the screen. Search the pattern and its neighbours, not the feature name.

What comes back is **not a gallery**. For every relevant reference:

- **which decision it takes**, and at what cost;
- what it does well and what to avoid;
- group **by recurring decision, never by app** — "P2: quantified usage recap" beats
  "Dovetail, beehiiv".

Two mandatory blocks:

- **"Does not apply to us, and why."** Naming the mismatch is as valuable as the match — it
  stops a pattern from being copied because it looked adjacent.
- **Negative findings.** If a technique is **absent** across the whole corpus, say so with
  the count: _"none of the 18 screens uses urgency — zero countdowns"_. Absence is evidence
  against treating something as the default, and it is invisible unless you look for it.

Return links + the decision each one makes. Never screenshots.

### Front B — The design system, read from source

**Read the token source from disk, in full.** Not from memory, not from a brand package, not
from the copy bundled with this plugin (`references/ds/` is frozen and is **never**
authoritative for production code).

Locate it in this order — stop at the first that works:

1. `preflight.product.ds_source`, when a product was detected.
2. Detect from the cwd/repo: a tailwind theme (`**/tailwind/theme.css`, `index.css`), a
   `tokens.json`, a design-system package under `packages/`. Also read the repo's own token
   rules if it has them (e.g. a `.claude/rules/*tokens*.md`) — **the repo's rules win over
   any general convention.**
3. `references/ds/` bundled here, flagged explicitly as a frozen fallback.

_Known gap:_ the beta `product-registry.yaml` has no Inspira product entries, so detection
usually does not fire and step 2 is the real path. Don't rely on the registry.

Then answer the question that matters — **how far can we diverge without leaving the
system?** — in four parts:

- **Where the system tightens.** Real values, not impressions: largest type size, heaviest
  weight, whether a shadow token exists at all, largest radius, ramps that repeat the same
  hex at different names, blur, dark-theme support. This is where a commercial or
  high-emphasis surface breaks.
- **Where it already permits divergence.** Gradients, ramps with genuinely distinct steps,
  animation tokens, and any component prop that already sanctions an expressive register —
  plus any precedent already shipped that proves it.
- **Component inventory, with the caveats.** Not just names — **what each one actually is**.
  A card component that is really a `<button>` with `role=option`, a feature card whose
  `href` is required (so it is a navigation card and semantically wrong on a page where
  nothing navigates), a component whose name suggests pricing but is an execution plan. These
  traps cost real rework and only surface by reading the source.
- **Traps.** Breakpoints that do not match the framework defaults, framework defaults reset to
  `initial`, utilities that only exist locally. Anyone writing from muscle memory gets these
  wrong.

**And one search that is not about tokens: does this page type already exist?** Grep the repo
for the shell you are about to design — a full-screen page without the app chrome, an
unauthenticated layout, an empty state of this shape. Finding that the pattern is already
written and shipped turns "build a new shell" into "reuse the one in production".

If the surface is going to production code, also state what would have to be **added** to the
system, and what escaping the scale costs — that is a decision to document, never to hide.

### Front C — Does this need a new component?

An explicit answer, always, even when it is "no". Three outcomes:

- **No** — the DS covers it; name the components.
- **Derivable** — an existing component with a variant or a wrapper; say which and what
  changes.
- **Yes, new** — name it, say why nothing existing fits, and flag it as a DS gap so it can
  become a design-system issue instead of a local one-off.

## Step 2 — Discretionary fronts (decide, then declare)

Run these when they earn their cost. The decision is yours; **the declaration is mandatory**
(Step 0's third part).

### Behavioral biases and triggers

Only when the surface has to persuade, reassure, or move someone past a decision.

Two hard requirements, and they are what separates this from a listicle:

- **Bring the source.** Primary source when one exists — author, year, publication, the actual
  finding with its numbers. When you cannot trace a claim, mark it `[não verificado]` and say
  so plainly. Numbers that circulate without a traceable origin (the famous "loss aversion is
  2× stronger", "free trials convert 2–5× better") **do not go into a product document** as
  fact. Include the honest contestation when the literature disputes the effect — it does not
  change the screen decision, it changes how confidently you explain it.
- **Translate each bias into a screen decision, not a label.** "Loss aversion" is not an
  insight. "Show what the person already produced in the tool instead of what they would gain"
  is. And say where each trigger **risks** reading as manipulative or desperate for this
  specific audience — the wrong tone destroys credibility faster than it converts.

### Heuristics that actually bite

Not a recital. Only the ones that bear on this pattern, each with the concrete implication for
this screen. Three that bite beat ten that are quoted.

### Mental models of the audience

How does this person already expect this to work, based on the tools they use daily? Where
should the surface follow the convention, and where can it diverge **on purpose**? Divergence
without intent is just unfamiliarity.

### What the product actually has to show

Run this whenever the surface has to prove value, show state, or reference real content. It is
the cheapest front and it repeatedly returns the most actionable material:

- **Assets already in the repo** — screenshots, illustrations, patterns. A product screenshot
  sitting in `assets/` is a value proof that costs one import, zero queries and zero data
  sensitivity.
- **Data that actually exists** — which field, from which query, and **whether authorization
  is verified for the state the user is in**. An aggregate the backend cannot serve to an
  expired user is not available, however present it looks in the schema. Say what is
  _blocked_ and what is _unverified_ — they are different risks.
- **Live copy** — the strings the product already uses for this concept, read from i18n or the
  components. When two surfaces disagree about the same thing, that is a finding: the screen
  usually has to become the source and the other artifact gets realigned.
- **Locales** — every language the surface must exist in. Tightly fitted layouts break when a
  translation runs longer; a slot whose text comes from an external dashboard may have no
  translation dimension at all.

## Step 3 — Fan-out execution

**Fire every selected front in ONE message, as parallel Agent tool calls.** Research never
runs in the main context — subagents protect it. Each returns only the distilled result, never
raw dumps.

Every subagent returns the same structure:

```
## Achados
- [finding, with the decision or constraint it implies]

## Evidência
- [links, file paths, real values, sources with year]

## Não rendeu
- [what was searched and came back empty — including negative findings worth keeping]
```

Rules for the fan-out:

- **One front per subagent.** They are blind to each other on purpose; convergence between
  independent fronts is a signal, and it is only meaningful if they did not share context.
- **Pass the constraints down.** Every subagent gets the hypothesis, the cuts, and the
  audience. A front that does not know what was cut will research a solution for it.
- **`Não rendeu` is not filler.** An empty front stated plainly beats a padded one, and an
  absence across a corpus is a finding (Front A).
- If a front fails on tooling (MCP absent, source unreadable), degrade and say which one —
  never block, never fake it.

## Step 4 — Persistence and handoff to the Brief

Write to `.brisar/session.yaml`:

```yaml
research:
  status: completed | partial | blocked
  mode: pocket | full
  ran: [bench, ds, new-component, biases, heuristics, mental-models, product-inventory]
  skipped:
    - front: biases
      reason: <one line — why it did not earn its cost>
  ds_source:
    path: <path actually read>
    authority: source | frozen-fallback
  degraded: [<front>: <reason>] # tooling gaps
  next_action: ready-for-brief
```

Then **go straight into `references/brief.md`** — the research does not stand on its own and
does not get its own gate. The brief is the artifact; this phase is its input. There is one
gate, at the end of the brief, and that is where the builder gets to steer.

## Persona — expected behaviors

1. **The floor is the floor.** Pocket mode shrinks the discretionary fronts, never the three
   in Step 1. A short brief with real market and real tokens beats a long one built on memory.
2. **Read the source, cite the value.** "The scale stops at 32px" with the file path beats
   "the type scale is limited". Every constraint that will shape the design gets a number and
   a location.
3. **Say what you skipped.** Step 0's third part is not optional. Silent scope reduction is the
   one failure mode that looks like thoroughness.
4. **Absence is a finding.** Report the technique that appears nowhere, the query that returned
   nothing, the source you could not trace. It is evidence, and it is invisible if unstated.
5. **Mark uncertainty instead of smoothing it.** `[não verificado]` costs nothing and protects
   every downstream decision. A confident sentence with no source is a liability in a document
   people will quote back.
6. **Never research a solution for something that was cut** — but do report when the cut looks
   wrong, with the argument. That belongs in the brief's reconciliation, not in a new design.
7. **Distill, don't dump.** The main context receives conclusions and evidence, not transcripts.

One sharp caution: **this phase must not become the design.** The moment a front starts
proposing a layout, it has left its job — the direction space is the Diverge phase's business
(`references/phase-diverge.md`), and it needs the research to be neutral to work. Research
that arrives pre-committed to one answer produces a divergence with one real option and three
decorative ones.

## Cooperation contract

| Artifact                                                                     | Produced by                                     | Consumed by                                                   |
| ---------------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------- |
| `.bb/tasks/<slug>/spec.md` (`## problem`/`## hypothesis`/`## fit`/`## cuts`) | `/bb:discover`, `/bb:spec` (outside this skill) | Research (Step 0 — upstream contract), Brief (reconciliation) |
| `.brisar/session.yaml` (`research:` section)                                 | Research                                        | Brief, Diverge, Deliver (what was skipped, and why)           |
| Distilled findings per front                                                 | Research subagents                              | Brief (`references/brief.md`)                                 |
| Token source on disk + the repo's own token rules                            | the product repo                                | Research (Front B — read, never written)                      |
