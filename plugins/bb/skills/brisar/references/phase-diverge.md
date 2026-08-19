# Diverge phase: directions in equal standing

Loaded after the Brief phase, when the builder chooses to diverge. This phase turns the mapped
solution space into **distinct directions** the builder can judge, then converges on one,
keeping the runner-up and the discarded traceable.

**Distinct directions, not iterated versions.** Two layouts of the same idea are one direction
drawn twice. A direction is a **different bet about why the person does not act today**, if
the bet is wrong, the screen can be beautiful and still fail.

## The rule this phase exists to enforce

> A recommendation is allowed. **An asymmetric description is not.**

Describing one direction in depth and the others in a paragraph decides for the builder while
pretending to offer a choice. The person who asked is the one who judges, and they cannot judge
what was not written. Equal treatment is not fairness for its own sake; it is the precondition
for the choice being real.

This is enforced, not suggested: **the gate refuses to advance** when the directions are
unevenly specified (Step 4).

## Step 0: Read the space

From `.brisar/session.yaml` and the brief:

- **`gate.design_brief`** → the brief. The findings, the reconciliation, the open tension. This
  is the material; the directions are combinations of it.
- **`gate.discover_brief`** → the hypothesis, the appetite and the cuts. **The appetite bounds
  every direction**. A gorgeous six-week direction inside a two-week appetite is a direction
  that does not exist. And no direction may solve for something that was cut, unless the brief's
  reconciliation already flagged the cut as wrong and the builder reopened it.
- **`research.mode`** → pocket or full. It sets the count (Step 2), never the depth per
  direction.
- **the profile** → who is choosing. It changes nothing about the directions themselves
  and two things about the presentation: the vocabulary (Phase 0's banned list binds for
  `technical_vocabulary` false), and whether the recommendation is optional (Step 3).

## Step 1: separate the base from what varies

Before writing any direction, write **what is common to all of them**. This block is not a
variable of exploration. It is the ground the directions stand on.

It holds: the shell/layout inherited from an existing pattern, the constraints every version
must respect, the elements that appear regardless, the states every direction must represent,
and the non-negotiables from the contract.

**Why this comes first:** without it every direction re-describes the same shell, the differences
drown in repetition, and the builder cannot see what they are actually choosing between. With
it, each direction is only its own bet, which is what makes them comparable.

The base also makes an honest place for **declared exceptions**: when one direction breaks
something the base establishes, it says so and says why. An unstated exception reads as an
oversight.

## Step 2: generate the directions

**Minimum 2. No maximum imposed**: propose 4 if the space genuinely holds 4. Pocket mode
usually means 2; it does **not** mean one direction plus decoration.

Each direction is **dynamic to the problem**, never a fixed label set. Derive them from the
readings of the problem the research surfaced ("there is no path forward", "there is no way to see
what exists", "the institutional validation is missing"), not from a template of names.

### The five mandatory parts: every direction, all five

1. **The bet**: which reading of the problem it assumes, in one or two sentences. State the
   mechanism: _what does this direction believe is blocking the person, and what does it do about
   it?_ Two directions with the same bet are one direction.
2. **Composition**: the structure, concrete enough to start drawing: what anchors the frame, what
   supports it, what is demoted or dropped. Say which blocks from the inventory it uses **and
   which it deliberately leaves out**. How much is on screen at once is itself a design
   variable, not a checklist to fill.
3. **The copy it plans**: actual strings, not intentions. "A persuasive headline" is not copy;
   the sentence is. Include the primary action's label. Copy is where a direction's tone becomes
   falsifiable, and it is the part most often skipped, which is exactly why it is mandatory.
4. **A rationale anchored in the research**: which findings support this direction, cited: the
   reference and what it does, the source with its year, the real token value. A direction whose
   rationale cites nothing is a preference wearing research clothes.
5. **Risk and cost**: how it fails, and an honest read of what it costs against the appetite.
   Include the failure mode the research already exposed when there is one. A reference that
   shows the pattern degrading is worth more than a hypothetical.

### Two things that make the set genuinely comparable

- **Comparable length and grain.** Not identical word counts, comparable specificity. If one
  direction has copy for every block and another has copy for none, the set is not a choice.
- **Name the one that is the floor.** Usually the most conventional direction is the comparison
  baseline: if none of the others beat it clearly, their extra cost is not justified. Saying which
  one plays that role makes the comparison honest.

### What does not go to divergence

An explicit list, with the reason for each. A direction ruled out **with a reason** is worth more
than a direction never mentioned. It shows the space was mapped, not just sampled, and it stops
the same idea from resurfacing three rounds later. Reasons that qualify: no market repertoire, a
dependency the system cannot promise, a cost the appetite cannot absorb, a claim the product
cannot honor.

## Step 3: present them

Print the base block, then the directions, then a comparison table:

| #   | Direction | Reading of the problem | External dependency | Cost |
| --- | --------- | ---------------------- | ------------------- | ---- |

Then, in chat, the same discipline the brief phase requires: **what each direction is betting,
and roughly what it will look like**. Enough for someone who has not read the document to have
a view. Apply the legibility rules from `references/brief.md`: expand internal pointers on first
use, gloss design concepts in 5–10 words, and remember the audience is not only designers.

A recommendation may be stated: clearly, as a recommendation, with the reason. It goes **after**
all directions are described, never instead of describing them.

**When `reads_code` is false the recommendation is mandatory.** Equal treatment is what makes
the choice real, and for someone without design repertoire it also makes the choice hard: N paths
at identical depth, no criterion to weigh them by. Withholding the recommendation there is not
neutrality. It hands over the hardest judgement in the flow to the person least equipped to make
it, and the usual outcome is picking the first one. This does not bend the equal-treatment rule:
that rule forbids **asymmetric description**, not a stated recommendation. Describe all of them at
the same grain, then say which one you would pick, why, and what would have to be true for the
runner-up to win.

## Step 4: equal-treatment check (blocking)

Before the gate, check your own output. For each direction, all five parts present and specified
at comparable grain.

If any direction is missing a part, or is visibly thinner than the others: **do not gate. Fill
it in first.** Do not offer the choice and do not ask the builder whether it matters, the whole
point of the phase is that the choice is real, and an incomplete direction is a vote against
itself.

The one legitimate exception: a direction whose part is genuinely **not applicable** (a
composition with no primary action has no primary-action label). Say `not applicable` with the
reason. That is information. Silence is not.

## Step 5: converge

Convergence picks **one** direction and keeps the rest traceable:

- **The chosen one**: and why, against the bet, not against taste.
- **The runner-up**: and **when it would be better**. This is the useful part: it names the
  condition under which the choice was wrong.
- **The discarded ones**: why not now. "Not now" and "never" are different; say which.
- **The pivot condition**: the signal that would make you switch. Without it, a wrong direction
  gets defended instead of changed.

Record all four in the brief (the living-contract rule) and in session.yaml. The discarded
directions stay in the document, deleting them destroys the record of what was considered.

If the builder does not answer, proceed with an **explicit default**, say that you did, and
record it as a default rather than a decision.

## Step 6: persistence and gate

```yaml
diverge:
  status: completed | in-progress
  count: <n>
  base_declared: true
  directions:
    - id: <short-name>
      bet: <one line>
      is_baseline: bool
      cost: low | fits-appetite | over-appetite
      status: chosen | runner-up | discarded
      discard_reason: <only when discarded>
  pivot_condition: <one line>
  excluded: [<idea>: <reason>]
  next_action: ready-for-medium
```

### Gate

```json
{
  "questions": [
    {
      "question": "<N> paths put together at the same level of detail, and the chosen one is <name>. How do we go on?",
      "header": "Next",
      "options": [
        {
          "label": "Build the chosen path (Recommended)",
          "description": "I ask where you want to see it standing up and go on to the build."
        },
        {
          "label": "Switch the chosen path",
          "description": "You pick another one, they are all described at the same level for exactly this. I record the switch in the brief."
        },
        {
          "label": "Look for more paths",
          "description": "Only worth it if there is a genuinely new idea. Otherwise it is the same thing redrawn. I say what I would look for before you decide."
        },
        {
          "label": "Stop here",
          "description": "The paths and the choice stay saved in the brief. Pick it up later with /bb:brisar."
        }
      ],
      "multiSelect": false
    }
  ]
}
```

## Expected behaviors

1. **Equal treatment is the deliverable.** A set where one direction is written and the others are
   sketched has not done this phase's job, however good the written one is.
2. **A direction is a bet, not a layout.** If two share the bet, merge them and find a real third.
3. **Copy is mandatory.** It is the fastest way to discover a direction does not work, and the
   easiest thing to skip.
4. **Cite the research.** Every rationale points at a finding. Uncited direction, unexamined
   preference.
5. **Cost is honest or the choice is fake.** A direction that does not fit the appetite is
   labelled, not smuggled.
6. **Keep the discarded.** With reasons, in the brief. The record of what was considered is part
   of the value.
7. **Recommend, then stop.** State the recommendation and leave the decision. Do not build the
   presentation so only one option survives contact.

One sharp caution: **more directions is not more divergence.** Four directions with the same
underlying bet, differing in arrangement, are worse than two that genuinely disagree, they cost
four times the writing and give the builder no real choice. Divergence is measured in distinct
readings of the problem, never in variant count.

## Cooperation contract

| Artifact                                    | Produced by                                        | Consumed by                                               |
| ------------------------------------------- | -------------------------------------------------- | --------------------------------------------------------- |
| `.bb/<slug>/brief-design.md`                | Brief (updated here with directions + convergence) | Develop, Deliver, the implementing dev                    |
| `.brisar/session.yaml` (`diverge:` section) | Diverge                                            | medium question, Develop, Deliver, re-entry               |
| Chosen direction + base block               | Diverge                                            | Develop (what to build), Deliver (what to review against) |
| Appetite and cuts                           | `/bb:discover` (upstream)                          | Diverge (Step 0, bounds every direction)                  |
