# The five challenge modes

Load only the section for the mode chosen in Step 2. Every mode runs against the
**steelmanned** thesis, and every challenge it produces must be specific,
concrete, and pointed toward improvement.

## Question the premises: Socratic

Map the implicit premises of the thesis (what must be true for it to work).
Formulate questions that put each central premise in question. Climb the "why"
chain until you find unverified premises. Prioritize the 3–5 with the highest
impact if they are false.

## Test the evidence: Falsification

Define the falsification criterion: what would need to be true to prove the
thesis wrong? Evaluate the quality of the evidence (direct observation, data,
anecdote, or assumption?). Identify gaps between the conclusion and what the
evidence actually supports.

## Build the counter-argument: Dialectic

Formulate the strongest possible antithesis, not the most obvious one.
Identify points of irresolvable tension between thesis and antithesis. Propose
a synthesis that acknowledges what each side gets right.

## Project the failure: Pre-mortem

Assume it is 6 months in the future and the thesis has failed. Narrate 3–5
plausible failure stories: concrete, not generic. For each one, trace the chain
of second-order consequences. Order by probability.

## Attack adversarially: Red Team

Adopt the perspective of whoever wants this to fail (competitor, internal
critic, market, regulator). Identify the most likely attack vectors. For each
vector: what would the specific action be, and what is the resulting damage?

## Worked examples

### "Challenge my strategy of migrating to microservices in Q3"

**Steelman:** "You believe that decomposing into independent services will clear
the deploy bottleneck, let the 4 teams ship on cycles of their own and improve
failure isolation, especially after last quarter's 3 incidents caused by
coupling. Is that a fair reading?"

**Mode:** Pre-mortem.
**Challenge 1:** Six months in, 2 of the 8 services are extracted but the
monolith still depends on them through synchronous calls. The bottleneck got
worse, because every change touches both.
**Challenge 2:** The orders and inventory services are eventually consistent, but
the logic assumes immediate consistency. A flash sale creates 200 oversold orders
in 4 minutes.

### "Question my premises about launching feature X this month"

**Steelman:** reformulate the strongest argument for launching now; confirm.
**Mode:** Falsification, _"What would have to be true to prove that launching now
is a mistake? Which data backs the timing, and what is a premise?"_
