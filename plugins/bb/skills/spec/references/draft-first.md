# Draft-first: propose, then react to alignment

The move: don't ask the user to fill a blank. Read the one-liner, glance at the
codebase, and **write a draft spec with your best guesses already made.** Hand them
something concrete to react to, people correct a proposal far faster, and more
accurately, than they answer open questions cold.

## What the draft must cover

The spec's form belongs to `spec-format.md`: the free top half, then the fixed sections.
The draft's job is to arrive with those already filled from your best read of the goal
and the codebase, so the user reacts to a proposal instead of completing a blank. Mark
anything you're guessing so it reads as a guess rather than a fact.

The draft is a plan: what gets built, the business rules, the behavior you expect and the
order the work runs in. Two things a first draft earns the most from. First, the
**business rules**: what the thing must do and must never do, in the words of the
product, which is what the build cannot re-derive on its own. Second, the **smallest
version still worth shipping**, which is what turns a scope edge into a line you can
actually hold.

Reading the codebase is still where the draft starts, because it shows you what the work
touches. What you see there goes into the spec as a risk, never as a design: a technical
risk becomes a bullet in `## Attention points`, the risk and where it lives, and the
builder decides how to handle it with the code open.

## Surfacing the gray areas (the only thing you ask about)

A call earns a question only when it **genuinely could go more than one way**
and the goal or codebase doesn't already settle it. Everything else: decide it,
note it, move on. That filter is what keeps this from becoming an interrogation.

The questions are about **what gets built and how it behaves**: a business rule, a scope
edge, the outcome of an edge case. A technical detail is the builder's and does not reach
the user. The one exception is a technical choice only the user can make, like a stack the
company settled or a contract another team depends on.

Ask them through the **`AskUserQuestion` tool**: concrete options the user picks, not open prose. For each real gray area:

- Present **concrete options**: "card layout" vs "table", not "Option A / B".
- State **your lean and why**, so the user can approve it in one word.
- Make it a clean either/or; offer "your call" when you truly have no preference.
- **Size the ask to the stakes:** cheap-to-reverse → lead with your pick and let
  them veto; expensive-to-undo → lay the options out and let them choose.

## How to drive it

- On the **single highest-stakes question**, ask how the user would decide _before_
  revealing your pick. Anchoring is strongest on the call that matters most,
  so don't pre-frame that one. Everything else stays draft-first.
- One **small batch** of questions at a time via `AskUserQuestion` (up to 4 per
  call), never a wall.
- After each round, **fold the answers into the draft and show only what
  changed**: the diff, not the whole document again.
- **When the gray areas run dry, order the work and open the gate.** Group the tasks in
  `###` phases, write the attention points, run the lint, and show the gate. The review
  is one of the gate's options: the user picks it or builds without it.
- **The gate blocks on open load-bearing decisions.** Never offer a clean "build"
  while one is unresolved. The user must resolve it or defer it explicitly
  ("decide at build time", recorded in the spec). No silent "build anyway".
- **Reflect back:** "So we're building X, for Y, and NOT doing Z, right?"
- **Alignment is active, not silent.** It's confirmed when the user restates the
  idea in their own words or explicitly approves the written spec, never by the
  mere absence of objections. No reaction usually means they checked out, not that
  they agree; prompt for the explicit nod.
- **The validated spec is the checkpoint.** When the user approves (or sends last
  edits), that `.bb/<slug>/spec.md` is the artifact. The gate then offers to
  build, with what runs after the build ticked in the same call, and an explicit
  build pick is the user affirmatively starting execution, not the spec silently
  rolling into it. Never start building off the back of a re-read; only off that
  explicit pick.
- Keep **deferred decisions visible**: anything handed back to you ("your call")
  gets noted, so it's not silently assumed.
- When a good idea surfaces that's **out of scope**, don't drop it and don't build
  it; park it in the spec's out-of-scope bucket as a plain bullet (never a
  checkbox, which the task selector would mistake for work).
- If a question can't be settled without facts, go check (codebase → docs → web) and
  come back with the options, rather than guessing.
