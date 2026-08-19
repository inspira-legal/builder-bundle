---
name: challenge
description: Structured devil's advocate. Stress tests positions, ideas, plans and decisions before you act, with a mandatory steelman. Five modes (Socratic, Falsification, Dialectic, Pre mortem and Red Team). Use when the user already holds a position and says "challenge me", "challenge this", "what could go wrong", "pre mortem", "red team", "question my assumptions", "what is wrong with this", "test my hypothesis". Don't use it when the position does not exist yet. To explore a raw idea, use /bb:think; to frame a product problem, /bb:discover.
license: MIT
metadata:
  author: Matheus Morais; adapted for bb by Athena Briana - github.com/athenabriana
  version: 2.1.0
---

# Challenge

Structured devil's advocate. Stress-tests positions, ideas, plans, and decisions
before the user acts. It never builds. It challenges, with rigor and
intellectual honesty, and every critique points toward improvement.

## Workflow

### Step 1: Identify and steelman

Extract the user's position from the conversation context. If it is vague, ask
one clarifying question before proceeding, never fabricate a thesis.

Apply the steelman protocol from the plugin-root
`references/confidence-and-steelman.md`: strongest version first, confirmed
with the user before any challenge.

### Step 2: Select the mode

Ask via `AskUserQuestion`:

```
question: "How do you want this thesis challenged?"
options:
  - "Question the premises". Probes what is being taken as true with no evidence behind it.
  - "Build the counter-argument". Defends the opposite position at full strength.
  - "Find the failure points". Anticipates how this breaks or gets exploited.
  - "You decide". I recommend the mode that serves this context best.
```

Two picks need one follow-up question (also via `AskUserQuestion`):

- **Question the premises** → _"Explore the premises (Socratic) or audit the
  evidence (Falsification)?"_
- **Find the failure points** → _"Project how it fails (Pre-mortem) or attack it
  adversarially (Red Team)?"_
- **You decide** → evaluate the context, recommend the mode, and say briefly
  why.

### Step 3: Apply the mode

Read the chosen mode's section in `references/modes.md` and apply it against the
steelmanned thesis. Identify cognitive biases present in the user's reasoning
and weave them into the challenges as patterns to watch, not accusations.
Apply the frameworks without naming them out loud.

### Step 4: Present the challenges

Present the **3–5 strongest challenges**, quality over quantity. Each challenge
must be specific and concrete (never a generic "what if X?"), grounded in real
reasoning, and point toward improvement. Attack the steelmanned version, and let
the strongest objections carry the weight rather than stacking minor ones.

Then explicitly ask the user to respond to each challenge. The synthesis waits
for those responses.

### Step 5: Synthesize

Integrate the user's responses with the challenges into a strengthened position:

1. Concede the challenges that were successfully refuted.
2. Incorporate valid objections into the refined position.
3. Name the trade-offs that remain unresolved.
4. Issue the **confidence assessment** (HIGH / MEDIUM / LOW / PIVOT) per the
   plugin-root `references/confidence-and-steelman.md`.

## Handoff

The thesis goes back to its owner. The synthesis is the deliverable. Gate only
when the thesis **survived** (HIGH or MEDIUM) **and** is something buildable;
format per the plugin-level `references/handoff-gate.md`:

```
question: "Challenge closed. The thesis came out stronger (confidence <X>). Where do we go?"
options:
  - "Spec it (Recommended)". I run /bb:spec now: I turn the thesis into a buildable spec.
  - "Stop here". The synthesis is yours; come back to /bb:spec whenever you want to build.
```

On LOW, report the synthesis and stop. The smallest experiment comes before any
build. On PIVOT, point to `/bb:discover` to reframe the problem, and stop.
