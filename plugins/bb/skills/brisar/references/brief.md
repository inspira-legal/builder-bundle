# Brief phase: the journey's document

Entered straight from the Research phase (no gate between them; the research is the input,
the brief is the artifact). This phase opens `.bb/<slug>/design.md`, consolidating the
fronts into it, reconciling them against the upstream problem framing, presenting them in a
way a non-designer can act on, and **keeping the document alive** for the rest of the trilha.

**`design.md` is the only document brisar writes.** Every later phase writes its own section
of this same file: Diverge the directions, Develop what got built, Deliver the review and the
accessibility audit. One skill, one document, the way `/bb:discover` has `discovery.md` and
`/bb:spec` has `spec.md` (plugin-level `references/spec-state.md`). The brief is the first
diamond's half of it, and everything downstream reads it.

## Location

Beside the task contract, as its sibling:

```
.bb/<slug>/discovery.md  ← the framing (/bb:discover)
.bb/<slug>/spec.md       ← the execution contract (/bb:spec)
.bb/<slug>/design.md     ← the journey, opened here and written by every later phase
.bb/<slug>/prototype/    ← the clickable artifact (Develop)
```

**Resolve `.bb/` the way the contract says**: the nearest ancestor of the cwd that already has
one, and only create it in the cwd when no ancestor does (plugin-level
`references/spec-state.md`). Never resolve it as a bare relative path: after Phase 3 the session
runs from **inside** the prototype folder, so a relative `.bb/` would mint a second root one
level down, and the journey would land in a different tree than its sibling `spec.md`, which is
exactly what the folder contract exists to prevent.

```bash
BB=$(d=$PWD; while [ "$d" != / ] && [ ! -d "$d/.bb" ]; do d=$(dirname "$d"); done; [ -d "$d/.bb" ] && echo "$d/.bb" || echo "$PWD/.bb")
```

**If that path is a symlink into a canonical store**, read through it and **write to the
canonical target**. The Edit tool refuses to write through a symlink on purpose, that refusal
is what stops a copy from being born inside the repo. Record the real path in the brief's own
frontmatter (`canonical:`) so the instruction travels inside the artifact and nobody has to
remember it. **Leave the in-repo path in place as the symlink**: the resumption glob and every
reader below name `.bb/<slug>/design.md`, and they have to keep finding it.

If there is no task contract yet (pocket mode, no spec), write to `$BB/<slug>/design.md`
anyway and create the dir. The journey can precede the spec, and usually does: Deliver's gate
is what invokes `/bb:spec`.

## Authority: say this once and never blur it

> **Where `design.md` and the spec disagree, the spec wins. `design.md` is the record;
> the spec is the contract.**

The journey _changes_ the spec. That is its job, and it does it by **invoking `/bb:spec`** at
Deliver's gate, not by contradicting the contract in place and not by writing a delta section
for someone to apply by hand. A record that quietly disagrees with the contract creates two
sources of truth, which is the failure this rule exists to prevent.

The correction runs one way only. `/bb:spec` never edits `design.md`; that would give this
document two writers, which is the disease the one-document rule cures. When the spec reverses
a decision recorded here, **the next round of this skill** writes the reversal as a reversal
(revokes D4, per the spec). Precedence is what makes that affordable: a stale record never
misleads whoever builds, because whoever builds reads the contract.

## The living-contract rule: not optional, not on request

**Every round updates the brief.** A direction chosen, a constraint discovered while drawing, a
decision revoked, a copy claim that failed review. It goes in, at the moment it happens,
without being asked and without asking.

Concretely, keeping it alive means three things:

1. **Append the round, don't overwrite the history.** When exploration produces a v2, the brief
   gains a section for what changed and what stayed out **on purpose**. The reader needs to see
   the path, not just the destination.
2. **Record reversals as reversals.** When a later decision revokes an earlier one, say so
   explicitly, _"revokes the July 28 decision"_. A brief that silently rewrites its own past
   cannot be trusted as a record, and someone will ask why the screen contradicts it.
3. **Mark what is still in review.** Copy pending a brand pass, a claim pending confirmation, a
   permission question pending a legal answer. Unmarked, they read as settled.

At the end of the trilha Deliver's gate **invokes `/bb:spec`**, which reads this document and
writes the contract out of it. That call is the Deliver phase's business, but the material comes
from here, which is exactly why the record has to be complete.

## The frontmatter: the journey's state, and the only place it lives

`design.md` opens with a frontmatter block. This is what tells a later session where the
journey stopped and what it produced, so there is no state file beside it to keep in sync.

```yaml
---
status: in-progress | bootstrapped-to-discover | completed
phase: research | brief | diverge | medium | develop | deliver | done
round: 1
slug: <slug>
created: <ISO>
canonical: <real path, only when .bb is a symlink into a store>
medium: code | claude-design | paper | figma | pencil # the medium question
surfaces: # from Diverge on; the locator Deliver reviews against
  - name: <surface>
    artifact: <path under prototype/, or file + page + artboard on a canvas>
    states_built: [default, empty, loading, error]
    states_not_built: [<state>] # declared, never silent
    variants: [<variant>]
    deviations: [<what departed from the direction, and why>]
wcag_aa_status: pass | fail | partial | not-assessed # Deliver
blockers: [<what has to be fixed before merge>] # Deliver
---
```

The fields below `canonical:` accrete as the phases run, and they are why one document
replaces the six files this skill used to scatter: the surfaces list is the locator Deliver
needs, `states_not_built` is the declaration a prototype owes, and `wcag_aa_status` plus
`blockers` are the audit summarizing itself.

`status: bootstrapped-to-discover` is the one Phase 2 writes when the maturity gate sends the
builder to `/bb:discover` first: the journey is open and waiting outside brisar.

`phase` is the phase that is **open**, not the last one finished, so a session that
reads it knows what to do rather than what was done. Every phase updates it when it
hands off, and `round` increments with each exploration round.

A brief with no frontmatter reads as `phase: brief`, `round: 1`, `status: in-progress`.
It is a brief written before this block existed, and it is not an error.

## Step 1: assemble the document

Sections, in order. **Bold = mandatory in every mode**, including pocket.

| Section                                      | What it holds                                                     | Pocket            |
| -------------------------------------------- | ----------------------------------------------------------------- | ----------------- |
| **Executive summary**                        | The N things the research changed, ranked by how much they matter | 3-5 bullets       |
| **Reconciliation with the framing**          | confirms · contradicts · does not reach (Step 2)                  | yes, short        |
| **Findings by front**                        | The research, organized by decision, not by tool                  | floor fronts only |
| **The directions**                           | Filled by the Diverge phase; leave the heading                    | yes               |
| **The tension the research did not resolve** | Step 3                                                            | yes               |
| **Left out, and why**                        | A front skipped, a front degraded, a direction discarded          | yes, short        |
| **Decision log for this brief**              | Dated table, grows over the rounds                                | starts empty      |
| Exploration rounds                           | One block per round after the first (living-contract rule)        | as they happen    |

Two rules about the findings section:

- **Organize by the decision at stake, never by the tool that found it.** "Where the price
  goes, and at what cost" is a section; "Mobbin results" is a dump.
- **Every constraint carries its number and its source.** A value read from disk gets the path;
  a study gets author and year; an unverifiable claim gets `[unverified]`.

## Step 2: reconciliation against the upstream framing (mandatory)

The step that stops a beautiful screen from answering the wrong question. Compare the research
against `.bb/<slug>/discovery.md`'s `## Problem` / `## Hypothesis` / `## Fit` /
`## Cuts` and write **three blocks**. All three, even when one is short.

- **Confirms**: where the research supports the hypothesis, **and with what**: the reference,
  the source, the real value. "Confirmed" without evidence is just agreement.
- **Contradicts**: where the research disproves the framing, a cut, or a constraint the briefing
  asserted. Goes with the argument, not as a complaint. **A wrong cut is a legitimate
  finding**. The whole point of researching after framing is that framing can be wrong, and
  the person who wrote it wants to know.
- **Does not reach**: what the hypothesis claims that the research could **neither** support
  **nor** knock down. This is the honest block, and it is usually the most useful one: it tells
  the builder what the first round of real data is allowed to prove.

**Drift runs in every direction, so look in every direction.** Three questions, not one:

1. Does the research still serve the problem, or did it wander into an adjacent one?
2. Is the framing still true, or did the research overtake it?
3. Is there a conflict **between** parts of the contract that only shows up now that the
   research is on the table. A success metric that one of the variants cannot emit, a
   constraint that contradicts another?

That third question is the one nobody asks, and it is where the expensive findings live.

If there is no spec, say so in one line and continue. The reconciliation degrades,
it does not block. Same non-blocking stance the Deliver phase already takes.

### Legibility bites hardest here

This section naturally pulls cross-references (`## Cuts`, "restriction 2", "D7") and turns into
alphabet soup. **Every item states what the framing said, in your own words, before judging
it.** Not:

> ❌ contradicts cut 2

But:

> ✅ The briefing cut the social proof, claiming the marketing curation had not happened yet.
> **It happened**, it is public on the site, with 19 law-firm logos and a named testimonial
> with a job title. The slot can be designed for strong content, not thin content.

The second is longer and it is the only one that reads on its own.

## Step 3: the unresolved tension (mandatory)

Close with a question the research left open, or a tension it surfaced and could not settle.

**If you cannot find one, the research was probably shallow**: go back and look at what you
took for granted. A brief where everything fits is usually a brief that stopped asking.

Good tension: a conflict between two things the contract wants that cannot both be true; a
dependency the design needs and the system cannot promise; a measurement the design cannot
emit. Not a tension: a to-do, an unfinished task, or a decision that just needs someone to
pick.

## Step 4: present it (the reading is part of the delivery)

**Never hand over the document and stop.** The brief is long by design; the reading is what
makes it usable. Assume the reader has not read it, because they have not.

In chat, in this order:

1. **The main findings**: what changed, and what it means for the screen. Not a section
   index.
2. **The main references and what each one teaches**: a name is not a reference; say what
   it does and why we care.
3. **The directions mapped**: each with its rationale and **roughly what it will look like**.
   Enough that the reader can form an opinion without opening the file.
4. **The open tension**: plainly, as a question needing a decision.

Not ornate, not long-winded, but enough that someone can read it, understand it, and not need
the full document to have a view. That is the bar.

**Present the delta once the reader has already read it.** "Assume nothing has been read" is true
for a stakeholder seeing it for the first time and false for the builder on their fourth round with
the same document, re-reading a brief they helped write is the most common way this step becomes
noise. So the discriminator is **the reader, not the round number**: for someone who has followed
the rounds, give what changed, what it revoked, and what is still open, then stop. When the round
is being presented to someone new. A stakeholder, a dev picking up the handoff. The full reading
comes back, because for them it is round 1. If you cannot tell which case you are in, ask; it is
one short question and it decides the whole shape of the message.

### Three tests that keep the reading tight

Legibility (below) has a mechanical self-check and concision does not, so concision loses by
default, glossing, expanding pointers and citing evidence all push the text up. These three
tests are the counterweight, and they cut length **without** cutting content:

1. **Each block earns its place by enabling a decision or an opinion.** A sentence that changes
   nothing the reader will decide comes out, however true it is.
2. **The finding travels with its consequence, not with its path.** "The scale stops at 32px, so a
   large headline leaves the system", not the story of how it was discovered. The reader wants the
   constraint, not the search.
3. **Evidence lives in the document; the chat carries the conclusion.** The citation rules above
   (path and value, author and year, `[unverified]`) govern the artifact. In chat, name the
   source once and point at the document. A chat block that reproduces the evidence has become
   the document, and then nobody reads either.

Self-check, symmetric to the legibility one: scan your own reading for a sentence that changes no
decision. Cut it. Density is content; length is not.

### When concision and legibility disagree, legibility wins

The two rules pull in opposite directions and the tie has to be called, or the text oscillates.
**Legibility wins, and it wins for a reason:** a sentence the reader cannot decode costs them the
whole point, while a sentence that is ten words longer costs them ten words. So the gloss stays and
the pointer stays expanded, every time.

Concision does not lose its teeth, though. It just aims somewhere else. **Cut whole items, not the
words inside them.** The finding that changes no decision comes out entirely; the finding that
survives keeps its gloss, its number and its source. That is the resolution: concision decides
**what** is in the reading, legibility decides **how** each surviving thing is written. Shortening
by stripping glosses is the one move that fails both rules at once. It produces a text that is
still long and now needs a decoder.

### Three hard legibility rules: they apply to the document too, not just the chat

The audience is **not only designers**. A document that needs decoding is a document that was
not read.

Read `technical_vocabulary` before writing. When it is false, the banned vocabulary below binds
here. And it binds on **the skill's own words**, not only on design concepts: "divergence",
"reconciliation", "the research floor" are our method's names, and a builder without design
repertoire has no reason to know them. Name the phase by its result: "I put together paths for you
to choose from", instead of "diverge into directions".

#### The banned vocabulary, when `technical_vocabulary` is false

This is the list, and it is the one every phase that prints user-facing text reads:

| Banned                                                      | Say instead                    |
| ----------------------------------------------------------- | ------------------------------ |
| `scaffold`, `embed`, `repo`, `branch`, `slug`, `npm`, `MCP` | folder, project, install, page |
| `divergence`, `diverge`                                     | the paths I put together       |
| `reconciliation`                                            | what the research changed      |
| the research floor, `pocket`, `full`                        | the minimum research           |

Each hit gets replaced by what it means for the reader, never annotated.

1. **An internal pointer carries its meaning on first use.** Never a bare `D7`, `P6`,
   "restriction 2", "axis 2", always `D7 (the decision that the value block carries the
persuasion)`. The test: _a reader who has not opened the spec understands the
   sentence._
2. **A design concept gets a 5-10 word gloss on first use.** "reactance (the defense a person
   raises when they feel they are being sold to)", "endowment effect (the same thing is worth
   more once it is yours)". One short gloss, then use the term freely.
3. **Dense is not the same as illegible.** A long, meticulous brief is a good brief, density is
   how much content is there. Illegibility is the reader needing a decoder. Cut the decoder,
   keep the content.

Self-check before presenting, two passes, both target **zero**:

1. **Bare pointers**: `D\d+`, `P\d+`, "restriction N", "axis N" with no gloss at first occurrence.
2. **Banned vocabulary, when `technical_vocabulary` is false**: scan for every row of the table
   above. The list binds on every phase that prints, not only on the intake. A phase that honours
   it in the questions and breaks it in the findings has not honoured it.

Both passes are mechanical on purpose. A rule with a check gets followed and a rule with an
adjective gets drifted, which is exactly how the vocabulary contract went unenforced through four
phases.

## Step 5: persistence and gate

Write the document. Its frontmatter is the persistence: set `phase: diverge` (the phase
now open), `status`, and `round`. There is no second file, in this phase or any later one.

The reconciliation counts and the open tension are **sections of the document**, not
fields to copy somewhere: a contradicted point needs the sentence explaining it, which
is exactly what a count loses. Develop and Deliver read this document by its path,
`.bb/<slug>/design.md`, and write their own sections into it; the spec is its sibling in the
same folder. **The two coexist; the record never replaces the contract.**

### What goes in `## Left out, and why`

The declared-never-silent rule, written down. One line each, and the reason is the point:

- a research front not run, and what made it not worth its cost
- a front run degraded, and which conclusions got weaker because of it
- a direction discarded during divergence, and what killed it
- an idea that never reached divergence at all

A front skipped without a reason reads as a front nobody thought of.

### Gate

If the reconciliation produced any `contradicts`, **lead with it**. A contradicted framing is
a decision the builder owns, and it is cheaper to settle now than after the screens exist.

```json
{
  "questions": [
    {
      "question": "Brief closed and saved at <path>. <N> point(s) of the research contradict the framing. How do we go on?",
      "header": "Next",
      "options": [
        {
          "label": "Put together paths for you to choose from (Recommended)",
          "description": "I put together 2 or 3 different paths for this screen, all described at the same level of detail, and you choose. Each one bets on a different reason for the person not to act today."
        },
        {
          "label": "Resolve the contradiction first",
          "description": "I stop here for you to decide the points where the research disagrees with the framing. If the contract changes, the spec changes before the screens."
        },
        {
          "label": "Stop here",
          "description": "The brief stays saved and alive. Pick it up later with /bb:brisar. It detects the brief and offers the divergence."
        }
      ],
      "multiSelect": false
    }
  ]
}
```

When nothing was contradicted, drop the second option and simplify the question.

## Expected behaviors

1. **The brief is a contract, so it gets maintained like one.** Update every round, without
   being asked. A brief that stops at v1 while the design reaches v8 is worse than no brief:
   people trust it and it is wrong.
2. **Record reversals out loud.** "Revokes the July 28 decision" is a sentence that saves an
   argument later.
3. **Evidence or a mark, never a confident guess.** Path and value for anything read from disk;
   author and year for anything from literature; `[unverified]` for anything you cannot
   trace. This is what makes the document quotable.
4. **A wrong cut is a finding, not insubordination.** Report it with the argument and let the
   owner decide. Never design on top of a cut without saying so.
5. **Present, don't deliver-and-vanish.** The reading is part of the job. Assume nothing has
   been read.
6. **Write for the non-designer.** Gloss the concept, expand the pointer, drop the jargon that
   is not carrying weight.
7. **End on a real tension.** If there isn't one, look harder before declaring the brief done.

One sharp caution: **the brief does not choose the direction.** It maps the space and may carry
a recommendation, but the moment it describes one option in depth and the others in a sentence,
it has decided for the builder while pretending to offer a choice. Equal treatment is the
Diverge phase's rule (`references/phase-diverge.md`) and it starts here, with the brief not
pre-loading the answer.

## Cooperation contract

| Artifact                                                                    | Produced by                               | Consumed by                                     |
| --------------------------------------------------------------------------- | ----------------------------------------- | ----------------------------------------------- |
| The findings by front, in the current round                                 | Research                                  | Brief (Step 1, the material)                    |
| `.bb/<slug>/discovery.md` (`## Problem`/`## Hypothesis`/`## Fit`/`## Cuts`) | `/bb:discover`                            | Brief (Step 2, reconciliation)                  |
| `.bb/<slug>/spec.md`                                                        | `/bb:spec`                                | Brief (Step 2, reconciliation)                  |
| `.bb/<slug>/design.md`                                                      | **Brief** (and every later phase)         | Diverge, Develop, Deliver, `/bb:spec`           |
