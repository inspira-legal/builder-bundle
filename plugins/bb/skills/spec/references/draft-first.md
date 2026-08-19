# Draft-first: propose, then react to alignment

The move: don't ask the user to fill a blank. Read the one-liner, glance at the
codebase, and **write a draft spec with your decisions already made.** Hand them
something concrete to react to, people correct a proposal far faster, and more
accurately, than they answer open questions cold.

## What the draft must cover

The spec's form belongs to `spec-format.md`: the free top half, then the fixed sections.
The draft's job is to arrive with those already filled from your best read of the goal
and the codebase, so the user reacts to a proposal instead of completing a blank. Mark
anything you're guessing so it reads as a guess rather than a fact.

Two things a first draft earns the most from. First, **reuse**: name the existing code,
patterns or modules this builds on, the cheapest guard against reinventing something that
exists. Second, the **smallest version still worth shipping**, which is what turns a scope
edge into a line you can actually hold.

## Surfacing the forks (the only thing you ask about)

A decision earns a question only when it **genuinely could go more than one way**
and the goal or codebase doesn't already settle it. Everything else: decide it,
note it, move on. That filter is what keeps this from becoming an interrogation.

Ask the forks through the **`AskUserQuestion` tool**: concrete options the user picks, not open prose. For each real fork:

- Present **concrete options**: "card layout" vs "table", not "Option A / B".
- State **your lean and why**, so the user can approve it in one word.
- Make it a clean either/or; offer "your call" when you truly have no preference.
- **Size the ask to the stakes:** cheap-to-reverse → lead with your pick and let
  them veto; expensive-to-undo → lay the options out and let them choose.

## How to drive it

- On the **single highest-stakes fork**, ask how the user would decide _before_
  revealing your pick. Anchoring is strongest on the decision that matters most,
  so don't pre-frame that one. Everything else stays draft-first.
- One **small batch** of forks at a time via `AskUserQuestion` (up to 4 per
  call), never a wall.
- After each round, **fold the answers into the draft and show only what
  changed**: the diff, not the whole document again.
- **When the gray areas run dry, run the adversarial completeness pass**: the
  skill's step 5 (generators + the behavior→task→test trace), not a casual
  re-read. It hunts open load-bearing decisions, unmapped behavior, and material
  contradictions, and loops anything it surfaces back into the questions.
- **Then the check, step 6**: the lint, then an independent reviewer in fresh
  context. Medium and up, every time, before the gate ever opens.
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
  build (or build and ship), and an explicit build pick is the user affirmatively
  starting execution, not the spec silently rolling into it. Never start building
  off the back of a re-read; only off that explicit pick.
- Keep **deferred decisions visible**: anything handed back to you ("your call")
  gets noted, so it's not silently assumed.
- When a good idea surfaces that's **out of scope**, don't drop it and don't build
  it; park it in the spec's out-of-scope bucket as a plain bullet (never a
  checkbox, which the task selector would mistake for work).
- If a fork can't be settled without facts, go check (codebase → docs → web) and
  come back with the options, rather than guessing.
