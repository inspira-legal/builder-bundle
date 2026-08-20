# Research phase: the first diamond of design

Loaded after Phase 2 (maturity gate) and before the medium question. This is where the
solution space gets mapped **before** anything is drawn. It ends in the Brief phase
(`references/brief.md`), which is the written contract the rest of the trilha reads.

**This phase does not draw, does not scaffold, does not decide the direction.** It gathers
what a senior designer would gather before touching a canvas, and it gathers it from the
real sources: the market, the production design system, and the product itself.

Two rules that define the phase:

1. **The floor never scales down** (see Step 1). Every mode runs it.
2. **What is skipped is said out loud.** Silent cuts read as "we covered everything" when we
   didn't.

## Why it exists

Without this phase brisar goes from "I have an idea" to "here is a surface" with nothing in
between but the builder's own repertoire. The screen may be beautiful and answer the wrong
question, and there is no artifact to argue with later.

The evidence that this is the load-bearing phase: it is the one that finds the things nobody
asked for. Reading the token source from disk reveals that the type scale stops at 32px and
there is no shadow token at all, which kills a whole class of commercial layout before it is
drawn. Reading the repo reveals screenshots and page shells that already exist, so the
"new" thing was half-built. Reading the market reveals that a pattern the builder assumed
was standard appears in **zero** of 18 references. None of that comes from asking the
builder.

## Cross-awareness with the journey

Before any question, read `.bb/<slug>/design.md` in full, and with it:

- **`.bb/<slug>/spec.md`** (`## Problem` / `## Hypothesis` / `## Fit` / `## Cuts`). This is
  the **upstream contract**. The research answers _how should this be?_; the spec answered
  _is it worth building, and what did we cut?_ Load it:
  the hypothesis tells you what the research must test, and the cuts tell you what **not** to
  research a solution for.
  - **A cut is a constraint, not a taboo.** If the research finds a cut was wrong, that is a
    legitimate finding and it goes in the brief's reconciliation section, with the argument.
    Never silently design on top of a cut.
- **`preflight.product`**: settles where the design system lives (`ds_source`).
- **the profile**: who is reading. It does not change **what** the floor researches; it
  changes the vocabulary of everything printed. When `technical_vocabulary` is false, the banned
  vocabulary in `references/brief.md` binds here too: the mode line and the findings are
  user-facing text. Say "the product project is not on this computer", not "the repo is not in
  the cwd".
- **`intent.raw_prompt`**: the builder's own words. Often carries the constraint that matters
  most, phrased casually.
- If a project spec exists (a full behavior contract, not just the discover sections), read it
  too: variants, states and conditional blocks are the shape the research has to serve.

Write your output into the brief, per Step 4 below, and set its frontmatter
`phase: research`.

## Step 0: calibrate depth, and say it in one line

Judge the depth from what you already have; **do not ask**. Signals, in order of weight:

| Signal                                                       | Pushes toward       |
| ------------------------------------------------------------ | ------------------- |
| No spec, one surface, adjustment-shaped request              | `pocket`            |
| Builder said "quick", "simple", "just one screen"            | `pocket`            |
| Spec with small appetite                                     | `pocket`            |
| New surface with no precedent in the product                 | `full`              |
| Contract with multiple variants/states, or a metric attached | `full`              |
| Commercial/persuasive surface, or a novel interaction        | `full`              |
| Builder said "in depth", "research it thoroughly"            | `full`              |
| The hardest composition has no market repertoire             | `full`, and say why |

Then print **one line**, before running anything:

> **Research, `pocket` mode.** I am running the floor: references on Mobbin, the design system
> read from source, and the answer about a new component. **I skipped** behavioral biases, the
> pattern here is known and the gain does not pay for the round. Ask and I run it.

The line has three parts and all three are mandatory: **the mode · what runs · what was
skipped and why**. "Nothing was skipped" is a valid third part in `full` mode.

**A fourth part appears whenever a floor front ran degraded: what the degradation invalidates.**
Naming the missing tool is not enough. The reader needs to know which conclusions got weaker.
"I ran Front B without the repo" tells them nothing; "I did not read the tokens from source, so
the values are second hand and the component inventory does not exist" tells them what not to
trust:

> **Research, `full` mode.** I ran the floor and the biases. **Degraded:** the product repo is
> not here and `gh` is not authenticated, so the design system was read from the brand package:
> the values are second hand, the component inventory does not exist, and **I did not check
> whether this page is already in production**. Nothing was skipped.

## Step 1: the floor (runs in every mode, no exceptions)

Three fronts. They are the floor because each one has been the source of a finding that
changed the design, and none of them can be replaced by the builder's memory.

### Front A: market bench (Mobbin)

Use `search_screens` **and** `search_flows`. The flow around the screen matters as much as
the screen. Search the pattern and its neighbours, not the feature name.

What comes back is **not a gallery**. For every relevant reference:

- **which decision it takes**, and at what cost;
- what it does well and what to avoid;
- group **by recurring decision, never by app**, "P2: quantified usage recap" beats
  "Dovetail, beehiiv".

Two mandatory blocks:

- **"Does not apply to us, and why."** Naming the mismatch is as valuable as the match, it
  stops a pattern from being copied because it looked adjacent.
- **Negative findings.** If a technique is **absent** across the whole corpus, say so with
  the count: _"none of the 18 screens uses urgency. Zero countdowns"_. Absence is evidence
  against treating something as the default, and it is invisible unless you look for it.

Return links + the decision each one makes. Never screenshots.

#### Without Mobbin (`preflight.mcps.mobbin: false`)

The front still runs. It is the floor. What changes is where the corpus comes from, and the
first thing to settle is **whether the surface you are designing is public or behind a login**,
because that decides which rungs exist at all.

**Behind a login, which is most of a product.** An in-app paywall, a trial-expiry screen, an
upgrade modal, an empty state, onboarding after signup: none of these are reachable. They need an
account, and **brisar does not create accounts or sign in**, so a competitor's live app is not a
source here, however tempting. Do not plan around getting in. Available rungs, in order:

1. **Public galleries, searched by site.** `site:land-book.com`, `site:saaslandingpage.com`,
   `site:refero.design`, `site:pageflows.com`, `site:nicelydone.club`, and Mobbin's own public
   pages. This is the primary rung off Mobbin and it is what separates the fallback from a
   generic search: these return **screens**, not articles about patterns. Some of them index
   recorded product flows rather than single frames, which is the closest substitute for a
   logged-in surface, check what each one actually holds instead of assuming coverage.
2. **Ask for what the builder already has.** If they mentioned a reference, or work in this
   market, the screenshot in their hand beats a blind search. One question, highest signal per
   token, and it is the rung most often skipped out of politeness.
3. **The product's own precedent.** Adjacent surfaces already shipped are a corpus of one that
   you can actually read, and it is the corpus the design has to be consistent with anyway.
   Weak for novelty, strong for convention.
4. **Generic web search**: last resort. Returns named patterns without visual evidence; treat
   what comes back as a hypothesis to verify, never as a bench.

**Public: a landing, a pricing page, a marketing site.** Here the browser earns its place:
`preview_start` with a url, or a Chrome MCP when present. It is the current state and the whole
page is walkable, which beats a cropped screenshot. Two cautions: it reads the **marketing**
surface and says nothing about how the platform behaves once you are inside, and a consent banner
gets the most privacy-preserving answer, not a click-through to see the page faster.

**Say which rungs were available, not just which one you used.** "I ran the bench on public
galleries because the screen is behind a login and there is no way in" is a finding about the
corpus, and it is what lets the reader weigh everything built on top of it.

The two obligations that give Front A its value survive the degradation: group **by recurring
decision, never by app**, and keep the **"does not apply to us, and why"** block.

**One obligation changes, and it matters.** A negative finding needs a corpus that was sampled
systematically, "none of the 18 screens uses urgency" only carries weight if the 18 were not
handed to you by a ranking algorithm. Off Mobbin, a negative finding is reported **with the size
and the origin of the corpus** ("in the 6 landings I opened, none uses a countdown") or it
is not reported at all. Absence measured on a biased corpus is not evidence, and a brief that
asserts it will be quoted back.

### Front B: the design system, read from source

**Read the token source from disk, in full.** Not from memory, not from a brand package, not
from the copy bundled with this plugin (`references/ds/` is frozen and is **never**
authoritative for production code).

Locate it in this order, stop at the first that works:

1. `preflight.product.ds_source`, when a product was detected.
2. Detect from the cwd/repo: a tailwind theme (`**/tailwind/theme.css`, `index.css`), a
   `tokens.json`, a design-system package under `packages/`. Also read the repo's own token
   rules if it has them (e.g. a `.claude/rules/*tokens*.md`). **The repo's rules win over
   any general convention.**
3. **The repo elsewhere on this machine**: see below. Cheapest rung after the cwd, and the one
   most often skipped: "not in the cwd" is not "not on the disk".
4. **The repo remotely, without cloning**: see below. The rung for: the repo really is absent
   and `gh` is authenticated.
5. `references/ds/brand/` bundled here. **A brand package, not a token source.** See the
   caution below before using it.

_Known gap:_ the beta `product-registry.yaml` has no Inspira product entries, so detection
usually does not fire and step 2 is the real path. Don't rely on the registry.

#### Rung 3: the repo is on this machine, just not here

Before concluding the repo is absent, **look for it on disk**. A builder who has ever cloned the
product still has it, and brisar is frequently invoked from somewhere else. A sibling folder, a
docs repo, a fresh directory. Detecting only the cwd turns "I am standing somewhere else" into "the
source does not exist", which then degrades three fronts for no reason.

```bash
# macOS: spotlight, sub-second even across a home directory
mdfind -name "theme.css" -onlyin ~ 2>/dev/null | grep -v node_modules
# portable fallback
find ~ -maxdepth 6 -name "tokens.json" -not -path "*/node_modules/*" 2>/dev/null
```

Search for the artifact, not the repo name. The folder can be named anything. Good targets: the
token file, `tokens.json`, the repo's own rules file, the i18n directory. **Exclude
`node_modules`**: a dependency's own `theme.css` will match and it is not the design system.

This rung is worth more than the remote one, and it is worth saying why: it reads **real source**,
so it recovers the component inventory and the "how many places use this" answer that the remote
rung cannot give. When it hits, Front B is not degraded at all.

Two cautions. Confirm the hit is the **right** checkout before reading it. A stale worktree, a
vendored copy or another branch's copy will answer confidently and wrongly, so state which path
you read. And more than one plausible hit is a question for the builder, not a coin flip.

#### Rung 4: read the repo remotely (`gh`)

When rungs 1–3 found nothing and `preflight.tooling.gh_authed` is true, read the files straight
from GitHub. Seconds, no disk, no clone. **Two calls, in this order:**

```bash
# 1. the whole file listing, in ONE call: this is the map
gh api "repos/<owner>/<repo>/git/trees/HEAD?recursive=1" --jq '.tree[].path' > /tmp/tree.txt
grep -iE 'tailwind|tokens|theme\.css|i18n|locales' /tmp/tree.txt

# 2. read the files the listing pointed at
gh api "repos/<owner>/<repo>/contents/<path>" -H "Accept: application/vnd.github.raw"
```

**Use the tree, not code search.** `gh search code` sits on a **10-requests-per-minute** budget
(`gh api rate_limit --jq .resources.code_search`). A fan-out of research subagents exhausts it in
one round, and the 403 comes back as empty output, indistinguishable from "found nothing". Its
`path:` qualifier also does not take globs, so a query that looks reasonable returns zero and reads
as absence. The tree endpoint is on the ordinary 5,000/hour budget, returns every path in one call,
and is greppable locally.

What this rung gets you and what it does not:

- **Token values and live i18n copy**: fully. This is the half that works.
- **Whether a path exists**: and here the tree is genuinely conclusive: when the response says
  `truncated: false`, the listing is complete, so a path that is absent from it **is** absent.
  Check that field before claiming either way.
- **The component inventory with its traps**: no. Knowing a card component is really a `<button
role=option>` means reading component source, and that is a sweep, not two file reads. This is
  the half that stays open, and it is the expensive half.
- **"How many places use this"**: no. There is no grep here.

So: report what you read with its path, and report the inventory as **missing** rather than
inferring it from token names.

#### When `gh` is not available: the rung that actually gets used

`gh_authed: false` is not an edge case: `gh` may be missing, unauthenticated, or authenticated on
an account without access to a private product. So this path needs to be as designed as the happy
one. In order, and **each of these is a real answer, not a shrug**:

1. **Rung 3 first, always.** Most `gh_authed: false` cases are solved on disk, because someone who
   works on the product has it cloned. Do not offer authentication before looking.
2. **Offer `gh auth login`**: one command, and it upgrades every later run, not just this one.
   Never run it silently: it is an authentication step and it belongs to the builder.
3. **Ask the builder to point at it.** "Where is the product project on this machine?" or "paste me
   the tokens file" is one question with a complete answer. Cheapest of all, and the rung most
   often skipped out of a reflex to seem self-sufficient. A builder who works on the product knows
   this path from memory.
4. **Ask what the repo's own rules say.** Many repos carry a token rules file
   (`.claude/rules/*tokens*.md`, `CONTRIBUTING`, a DS README) that names the canonical path and the
   local conventions. Getting **that** file is often better than getting the tokens, because it is
   authored guidance rather than raw values, and **it stays right when the paths move**.
5. **Only then rung 5**: the brand package, for voice and visual intent, with the token gap
   declared in the mode line.

Cloning the repo shallowly is the rung that would give real grep without an existing checkout.
brisar does **not** clone on its own: dropping a private company repo onto someone's machine is the
builder's call. Mention it as an option and move on.

**Where the paths should live, and it is not in this file.** Hardcoding a product's token path
into the plugin makes the plugin wrong the day the repo is refactored, and it puts internal layout
in a place that does not own it. Two better homes, in order: the **repo's own rules file** (the
product repo states where its tokens are. It is the only thing that can keep that true), and
`references/product-registry.yaml` (the `ds_source` field exists precisely for this) or
`BRISAR_DS_PATH` for a machine-specific override. When you spend real effort
locating a source, **say so and suggest recording it** in one of those. The next run should not
repeat the search.

#### Caution about rung 5

`references/ds/brand/` is the **brand** package: voice, principles, colour meanings, logo usage.
Its `tokens/tokens.json` is a brand artifact and is **not** the production token vocabulary; the
production source is the design-system package in the product repo. Designing against it produces
class names the codebase does not have, which surfaces at implementation time and costs a rewrite.

So on rung 5: use it for **voice and visual intent**, never for token values. When rung 5 is all
you have, the honest report is _"I did not read the design system from source"_, with the consequence spelled
out in the mode line (Step 0's fourth part), not a token table presented as if it were read.

Then answer the question that matters. **How far can we diverge without leaving the
system?**, in four parts:

- **Where the system tightens.** Real values, not impressions: largest type size, heaviest
  weight, whether a shadow token exists at all, largest radius, ramps that repeat the same
  hex at different names, blur, dark-theme support. This is where a commercial or
  high-emphasis surface breaks.
- **Where it already permits divergence.** Gradients, ramps with genuinely distinct steps,
  animation tokens, and any component prop that already sanctions an expressive register,
  plus any precedent already shipped that proves it.
- **Component inventory, with the caveats.** Not just names. **What each one actually is**.
  A card component that is really a `<button>` with `role=option`, a feature card whose
  `href` is required (so it is a navigation card and semantically wrong on a page where
  nothing navigates), a component whose name suggests pricing but is an execution plan. These
  traps cost real rework and only surface by reading the source.
- **Traps.** Breakpoints that do not match the framework defaults, framework defaults reset to
  `initial`, utilities that only exist locally. Anyone writing from muscle memory gets these
  wrong.

**And one search that is not about tokens: does this page type already exist?** Grep the repo
for the shell you are about to design. A full-screen page without the app chrome, an
unauthenticated layout, an empty state of this shape. Finding that the pattern is already
written and shipped turns "build a new shell" into "reuse the one in production".

Without the repo on disk, run it through rung 4's file listing. Path names carry a lot here (a
`pages/TrialExpired/` directory answers the question by itself), and an untruncated tree makes the
negative answer trustworthy too. What the listing cannot tell you is what the shell actually
does, so read the file before concluding it is reusable.

If the surface is going to production code, also state what would have to be **added** to the
system, and what escaping the scale costs. That is a decision to document, never to hide.

### Front C: does this need a new component?

An explicit answer, always, even when it is "no". Three outcomes:

- **No**: the DS covers it; name the components.
- **Derivable**: an existing component with a variant or a wrapper; say which and what
  changes.
- **Yes, new**: name it, say why nothing existing fits, and flag it as a DS gap so it can
  become a design-system issue instead of a local one-off.

## Step 2: discretionary fronts (decide, then declare)

Run these when they earn their cost. The decision is yours; **the declaration is mandatory**
(Step 0's third part).

### Behavioral biases and triggers

Only when the surface has to persuade, reassure, or move someone past a decision.

Two hard requirements, and they are what separates this from a listicle:

- **Bring the source.** Primary source when one exists: author, year, publication, the actual
  finding with its numbers. When you cannot trace a claim, mark it `[unverified]` and say
  so plainly. Numbers that circulate without a traceable origin (the famous "loss aversion is
  2× stronger", "free trials convert 2–5× better") **do not go into a product document** as
  fact. Include the honest contestation when the literature disputes the effect. It does not
  change the screen decision, it changes how confidently you explain it.
- **Translate each bias into a screen decision, not a label.** "Loss aversion" is not an
  insight. "Show what the person already produced in the tool instead of what they would gain"
  is. And say where each trigger **risks** reading as manipulative or desperate for this
  specific audience. The wrong tone destroys credibility faster than it converts.

### Heuristics that change the screen

Not a recital. Only the ones that bear on this pattern, each with the concrete implication for
this screen. Three that change the design beat ten that are quoted.

### Mental models of the audience

How does this person already expect this to work, based on the tools they use daily? Where
should the surface follow the convention, and where can it diverge **on purpose**? Divergence
without intent is just unfamiliarity.

### What the product actually has to show

Run this whenever the surface has to prove value, show state, or reference real content. It is
the cheapest front and it repeatedly returns the most actionable material:

- **Assets already in the repo**: screenshots, illustrations, patterns. A product screenshot
  sitting in `assets/` is a value proof that costs one import, zero queries and zero data
  sensitivity.
- **Data that actually exists**: which field, from which query, and **whether authorization
  is verified for the state the user is in**. An aggregate the backend cannot serve to an
  expired user is not available, however present it looks in the schema. Say what is
  _blocked_ and what is _unverified_. They are different risks.
- **Live copy**: the strings the product already uses for this concept, read from i18n or the
  components. When two surfaces disagree about the same thing, that is a finding: the screen
  usually has to become the source and the other artifact gets realigned.
- **Locales**: every language the surface must exist in. Tightly fitted layouts break when a
  translation runs longer; a slot whose text comes from an external dashboard may have no
  translation dimension at all.

**This is the front the missing repo hits hardest**: all four items above are reads from disk.
Rung 3 (the repo found elsewhere on disk) recovers all of it, which is why it comes first. Rung 4
recovers the live copy and, partially, the assets; **what data actually exists and whether
authorization serves it cannot be answered remotely**, and guessing it is how a design ends up
promising a number the backend will not return. When the repo is absent, this front reports what
it recovered and marks the data question `[unverified]` instead of assuming availability.

## Step 3: fan-out execution

**Fire every selected front in ONE message, as parallel Agent tool calls.** Research never
runs in the main context, subagents protect it. Each returns only the distilled result, never
raw dumps.

Every subagent returns the same structure:

```
## Findings
- [finding, with the decision or constraint it implies]

## Evidence
- [links, file paths, real values, sources with year]

## Came back empty
- [what was searched and came back empty, including negative findings worth keeping]
```

Rules for the fan-out:

- **One front per subagent.** They are blind to each other on purpose; convergence between
  independent fronts is a signal, and it is only meaningful if they did not share context.
- **Pass the constraints down.** Every subagent gets the hypothesis, the cuts, and the
  audience. A front that does not know what was cut will research a solution for it.
- **`Came back empty` is not filler.** An empty front stated plainly beats a padded one, and an
  absence across a corpus is a finding (Front A).
- If a front fails on tooling (MCP absent, source unreadable), degrade and say which one.
  Never block, never fake it.

## Step 4: write it into the brief, then hand off

There is no state file to fill. What the research produced goes into
`.bb/<slug>/design.md`, in the sections that already exist for it
(`references/brief.md`):

| What the research holds                                 | Where it lands in the brief                    |
| ------------------------------------------------------- | ---------------------------------------------- |
| the findings of each front that ran                     | findings by front, one block per front         |
| the mode line (`pocket` or `full`) and which fronts ran | the round's opening line                       |
| a front skipped, and why                                | `## Left out`, one row with the reason         |
| a front degraded, and which conclusions weaken          | `## Left out`, with what it invalidates        |
| the DS source actually read, its path and its authority | findings, Front B, with the path and the value |
| the bench's route and corpus size                       | findings, Front A                              |
| a path worth recording for next time                    | the suggestion, said out loud to the builder   |

Set the frontmatter `phase: brief`.

Then **go straight into `references/brief.md`**. The research does not stand on its own and
does not get its own gate. The brief is the artifact; this phase is its input. There is one
gate, at the end of the brief, and that is where the builder gets to steer.

## Expected behaviors

1. **The floor is the floor.** Pocket mode shrinks the discretionary fronts, never the three
   in Step 1. A short brief with real market and real tokens beats a long one built on memory.
2. **Read the source, cite the value.** "The scale stops at 32px" with the file path beats
   "the type scale is limited". Every constraint that will shape the design gets a number and
   a location.
3. **Say what you skipped.** Step 0's third part is not optional. Silent scope reduction is the
   one failure mode that looks like thoroughness.
4. **Absence is a finding.** Report the technique that appears nowhere, the query that returned
   nothing, the source you could not trace. It is evidence, and it is invisible if unstated.
5. **Mark uncertainty instead of smoothing it.** `[unverified]` costs nothing and protects
   every downstream decision. A confident sentence with no source is a liability in a document
   people will quote back.
6. **Never research a solution for something that was cut**: but do report when the cut looks
   wrong, with the argument. That belongs in the brief's reconciliation, not in a new design.
7. **Distill, don't dump.** The main context receives conclusions and evidence, not transcripts.

One sharp caution: **this phase must not become the design.** The moment a front starts
proposing a layout, it has left its job. The direction space is the Diverge phase's business
(`references/phase-diverge.md`), and it needs the research to be neutral to work. Research
that arrives pre-committed to one answer produces a divergence with one real option and three
decorative ones.

## Cooperation contract

| Artifact                                                               | Produced by                                     | Consumed by                                                  |
| ---------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| `.bb/<slug>/spec.md` (`## Problem`/`## Hypothesis`/`## Fit`/`## Cuts`) | `/bb:discover`, `/bb:spec` (outside this skill) | Research (Step 0, upstream contract), Brief (reconciliation) |
| `.bb/<slug>/design.md` (findings by front, `## Left out`)              | Research                                        | Brief, Diverge, Deliver (what was skipped, and why)          |
| Distilled findings per front                                           | Research subagents                              | Brief (`references/brief.md`)                                |
| Token source on disk + the repo's own token rules                      | the product repo                                | Research (Front B; read, never written)                      |
