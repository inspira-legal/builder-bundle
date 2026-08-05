# Brief phase — the design contract

Entered straight from the Research phase (no gate between them — the research is the input,
the brief is the artifact). This phase consolidates the fronts into one document, reconciles
it against the upstream problem framing, presents it in a way a non-designer can act on, and
**keeps it alive** for the rest of the trilha.

The brief is the contract of the first diamond. Everything downstream reads it: the Diverge
phase builds directions from it, Develop builds against it, Deliver reviews against it.

## Location

Beside the task contract, as its sibling:

```
.bb/tasks/<slug>/spec.md          ← the execution contract (/bb:spec)
.bb/tasks/<slug>/brief-design.md  ← this file's output
```

**Resolve `.bb/` the way the contract says** — the nearest ancestor of the cwd that already has
one, and only create it in the cwd when no ancestor does (plugin-level
`references/task-state.md`). Never resolve it as a bare relative path: after Phase 3 the session
runs from **inside** the project folder, so a relative `.bb/` would mint a second root one level
down, and the brief would land in a different tree than its sibling `design.md` — which is exactly
what the folder contract exists to prevent.

```bash
BB=$(d=$PWD; while [ "$d" != / ] && [ ! -d "$d/.bb" ]; do d=$(dirname "$d"); done; [ -d "$d/.bb" ] && echo "$d/.bb" || echo "$PWD/.bb")
```

**If that path is a symlink into a canonical store**, read through it and **write to the
canonical target**. The Edit tool refuses to write through a symlink on purpose — that refusal
is what stops a copy from being born inside the repo. Record the real path in the brief's own
frontmatter (`canonical:`) so the instruction travels inside the artifact and nobody has to
remember it. **Leave the in-repo path in place as the symlink**: the resumption glob and every
reader below name `.bb/tasks/<slug>/brief-design.md`, and they have to keep finding it.

If there is no task contract yet (pocket mode, no spec), write to
`$BB/tasks/<slug>/brief-design.md` anyway and create the dir — the brief can precede the spec.

## Authority — say this once and never blur it

> **Where the brief and the spec disagree, the spec wins. The brief is the research record;
> the spec is the contract.**

The brief _changes_ the spec — that is its job, and it does it through the delta at handoff,
not by contradicting it in place. A brief that quietly disagrees with the contract creates two
sources of truth, which is the failure this rule exists to prevent.

## The living-contract rule — not optional, not on request

**Every round updates the brief.** A direction chosen, a constraint discovered while drawing, a
decision revoked, a copy claim that failed review — it goes in, at the moment it happens,
without being asked and without asking.

Concretely, keeping it alive means three things:

1. **Append the round, don't overwrite the history.** When exploration produces a v2, the brief
   gains a section for what changed and what stayed out **on purpose**. The reader needs to see
   the path, not just the destination.
2. **Record reversals as reversals.** When a later decision revokes an earlier one, say so
   explicitly — _"revoga a decisão de 28/07"_. A brief that silently rewrites its own past
   cannot be trusted as a record, and someone will ask why the screen contradicts it.
3. **Mark what is still in review.** Copy pending a brand pass, a claim pending confirmation, a
   permission question pending a legal answer. Unmarked, they read as settled.

At the end of the trilha the brief feeds the **delta back into the spec** — the contract catches
up with what the design learned. That handoff is the Deliver phase's business, but the material
comes from here, which is exactly why the record has to be complete.

## Step 1 — Assemble the document

Sections, in order. **Bold = mandatory in every mode**, including pocket.

| Section                                   | What it holds                                                     | Pocket            |
| ----------------------------------------- | ----------------------------------------------------------------- | ----------------- |
| **Sumário executivo**                     | The N things the research changed, ranked by how much they matter | 3–5 bullets       |
| **Reconciliação com o enquadramento**     | confirma · contradiz · não alcança (Step 2)                       | yes, short        |
| **Achados por frente**                    | The research, organized by decision — not by tool                 | floor fronts only |
| **As direções**                           | Filled by the Diverge phase; leave the heading                    | yes               |
| **A tensão que a pesquisa não resolveu**  | Step 3                                                            | yes               |
| **Registro de decisões sobre este brief** | Dated table, grows over the rounds                                | starts empty      |
| Rodadas de exploração                     | One block per round after the first (living-contract rule)        | as they happen    |

Two rules about the findings section:

- **Organize by the decision at stake, never by the tool that found it.** "Where the price
  goes, and at what cost" is a section; "Mobbin results" is a dump.
- **Every constraint carries its number and its source.** A value read from disk gets the path;
  a study gets author and year; an unverifiable claim gets `[não verificado]`.

## Step 2 — Reconciliation against the upstream framing (mandatory)

The step that stops a beautiful screen from answering the wrong question. Compare the research
against the discover brief's `## problem` / `## hypothesis` / `## fit` / `## cuts` and write
**three blocks**. All three, even when one is short.

- **Confirma** — where the research supports the hypothesis, **and with what**: the reference,
  the source, the real value. "Confirmed" without evidence is just agreement.
- **Contradiz** — where the research disproves the framing, a cut, or a constraint the briefing
  asserted. Goes with the argument, not as a complaint. **A wrong cut is a legitimate
  finding** — the whole point of researching after framing is that framing can be wrong, and
  the person who wrote it wants to know.
- **Não alcança** — what the hypothesis claims that the research could **neither** support
  **nor** knock down. This is the honest block, and it is usually the most useful one: it tells
  the builder what the first round of real data is allowed to prove.

**Drift runs in every direction, so look in every direction.** Three questions, not one:

1. Does the research still serve the problem, or did it wander into an adjacent one?
2. Is the framing still true, or did the research overtake it?
3. Is there a conflict **between** parts of the contract that only shows up now that the
   research is on the table — a success metric that one of the variants cannot emit, a
   constraint that contradicts another?

That third question is the one nobody asks, and it is where the expensive findings live.

If there is no discover brief, say so in one line and continue — the reconciliation degrades,
it does not block. Same non-blocking stance the Deliver phase already takes.

### Legibility bites hardest here

This section naturally pulls cross-references (`## cuts`, "restriction 2", "D7") and turns into
alphabet soup. **Every item states what the framing said, in your own words, before judging
it.** Not:

> ❌ contradiz o corte 2

But:

> ✅ O briefing cortou a prova social alegando que a curadoria de marketing ainda não tinha
> acontecido. **Aconteceu** — está pública no site, com 19 logos de banca e um depoimento
> nomeado com cargo. O slot pode ser desenhado pra conteúdo forte, não magro.

The second is longer and it is the only one that reads on its own.

## Step 3 — The unresolved tension (mandatory)

Close with a question the research left open, or a tension it surfaced and could not settle.

**If you cannot find one, the research was probably shallow** — go back and look at what you
took for granted. A brief where everything fits is usually a brief that stopped asking.

Good tension: a conflict between two things the contract wants that cannot both be true; a
dependency the design needs and the system cannot promise; a measurement the design cannot
emit. Not a tension: a to-do, an unfinished task, or a decision that just needs someone to
pick.

## Step 4 — Present it (the reading is part of the delivery)

**Never hand over the document and stop.** The brief is long by design; the reading is what
makes it usable. Assume the reader has not read it — because they have not.

In chat, in this order:

1. **Os principais achados** — what changed, and what it means for the screen. Not a section
   index.
2. **As principais referências e o que cada uma ensina** — a name is not a reference; say what
   it does and why we care.
3. **As direções mapeadas** — each with its rationale and **roughly what it will look like**.
   Enough that the reader can form an opinion without opening the file.
4. **A tensão aberta** — plainly, as a question needing a decision.

Not ornate, not long-winded — but enough that someone can read it, understand it, and not need
the full document to have a view. That is the bar.

**Present the delta once the reader has already read it.** "Assume nothing has been read" is true
for a stakeholder seeing it for the first time and false for the builder on their fourth round with
the same document — re-reading a brief they helped write is the most common way this step becomes
noise. So the discriminator is **the reader, not the round number**: for someone who has followed
the rounds, give what changed, what it revoked, and what is still open, then stop. When the round
is being presented to someone new — a stakeholder, a dev picking up the handoff — the full reading
comes back, because for them it is round 1. If you cannot tell which case you are in, ask; it is
one short question and it decides the whole shape of the message.

### Three tests that keep the reading tight

Legibility (below) has a mechanical self-check and concision does not, so concision loses by
default — glossing, expanding pointers and citing evidence all push the text up. These three
tests are the counterweight, and they cut length **without** cutting content:

1. **Each block earns its place by enabling a decision or an opinion.** A sentence that changes
   nothing the reader will decide comes out, however true it is.
2. **The finding travels with its consequence, not with its path.** "A escala para em 32px, então
   manchete grande sai do sistema" — not the story of how it was discovered. The reader wants the
   constraint, not the search.
3. **Evidence lives in the document; the chat carries the conclusion.** The citation rules above
   (path and value, author and year, `[não verificado]`) govern the artifact. In chat, name the
   source once and point at the document — a chat block that reproduces the evidence has become
   the document, and then nobody reads either.

Self-check, symmetric to the legibility one: scan your own reading for a sentence that changes no
decision. Cut it. Density is content; length is not.

### When concision and legibility disagree, legibility wins

The two rules pull in opposite directions and the tie has to be called, or the text oscillates.
**Legibility wins, and it wins for a reason:** a sentence the reader cannot decode costs them the
whole point, while a sentence that is ten words longer costs them ten words. So the gloss stays and
the pointer stays expanded, every time.

Concision does not lose its teeth, though — it just aims somewhere else. **Cut whole items, not the
words inside them.** The finding that changes no decision comes out entirely; the finding that
survives keeps its gloss, its number and its source. That is the resolution: concision decides
**what** is in the reading, legibility decides **how** each surviving thing is written. Shortening
by stripping glosses is the one move that fails both rules at once — it produces a text that is
still long and now needs a decoder.

### Three hard legibility rules — they apply to the document too, not just the chat

The audience is **not only designers**. A document that needs decoding is a document that was
not read.

Read `profile.persona_id` before writing: for `executive` and `content`, Phase 0's banned
vocabulary binds here (`phase-0-calibration.md`). And it binds on **the skill's own words**, not
only on design concepts — "divergência", "reconciliação", "piso da pesquisa" are our method's
names, and a builder without design repertoire has no reason to know them. Name the phase by its
result: "monto caminhos pra você escolher", not "divergir em direções".

1. **An internal pointer carries its meaning on first use.** Never a bare `D7`, `P6`,
   "restriction 2", "axis 2" — always `D7 (a decisão de que o bloco de valor carrega a
persuasão)`. The ruler: _a reader who has opened neither the spec nor the discover brief
   understands the sentence._
2. **A design concept gets a 5–10 word gloss on first use.** "reactância (a defesa que a pessoa
   levanta quando sente que estão vendendo pra ela)", "efeito de dotação (a mesma coisa vale
   mais depois que já é sua)". One short gloss, then use the term freely.
3. **Dense is not the same as illegible.** A long, meticulous brief is a good brief — density is
   how much content is there. Illegibility is the reader needing a decoder. Cut the decoder,
   keep the content.

Self-check before presenting, two passes, both target **zero**:

1. **Bare pointers** — `D\d+`, `P\d+`, "restrição N", "eixo N" with no gloss at first occurrence.
2. **Banned vocabulary, when `persona_id` is `executive` or `content`** — scan for `scaffold`,
   `embed`, `npm`, `MCP`, `repo`, `branch`, `slug`, plus the method's own names (`divergência`,
   `divergir`, `reconciliação`, `piso`, `pocket`, `full`). Each hit gets replaced by what it means
   for the reader, not annotated: "o projeto do produto", "os caminhos que montei", "a pesquisa
   mínima". The list from Phase 0 was written for the intake and it binds on every phase that
   prints — a phase that honours it in the questions and breaks it in the findings has not honoured
   it.

Both passes are mechanical on purpose. A rule with a check gets followed and a rule with an
adjective gets drifted, which is exactly how the vocabulary contract went unenforced through four
phases.

## Step 5 — Persistence and gate

Write the document, then `.brisar/session.yaml`:

```yaml
brief:
  status: completed | in-progress
  path: <canonical path to brief-design.md>
  round: 1 # increments on every update
  reconciliation:
    upstream: <path to the discover brief, or null>
    confirms: <n>
    contradicts: <n> # >0 means the framing needs a decision
    unreachable: <n>
  open_tension: <one line>
  next_action: ready-for-diverge
```

Also record the path under `gate.design_brief` — that is the slot Develop and Deliver read,
the same way `gate.discover_brief` carries the upstream framing. **The two coexist; the design
brief never replaces the discover brief.**

### Gate

If the reconciliation produced any `contradicts`, **lead with it** — a contradicted framing is
a decision the builder owns, and it is cheaper to settle now than after the screens exist.

```json
{
  "questions": [
    {
      "question": "Brief fechado e salvo em <path>. <N> ponto(s) da pesquisa contradizem o enquadramento. Como seguimos?",
      "header": "Próximo",
      "options": [
        {
          "label": "Montar caminhos pra você escolher (Recomendado)",
          "description": "Monto 2 ou 3 caminhos diferentes pra essa tela, todos descritos no mesmo nível de detalhe, e você escolhe. Cada um aposta num motivo diferente pra pessoa não agir hoje."
        },
        {
          "label": "Resolver a contradição primeiro",
          "description": "Paro aqui pra você decidir os pontos onde a pesquisa discorda do enquadramento. Se mudar o contrato, o spec muda antes das telas."
        },
        {
          "label": "Encerrar aqui",
          "description": "Brief fica salvo e vivo. Retome depois com /bb:brisar — ele detecta o brief e oferece a divergência."
        }
      ],
      "multiSelect": false
    }
  ]
}
```

When nothing was contradicted, drop the second option and simplify the question.

## Persona — expected behaviors

1. **The brief is a contract, so it gets maintained like one.** Update every round, without
   being asked. A brief that stops at v1 while the design reaches v8 is worse than no brief:
   people trust it and it is wrong.
2. **Record reversals out loud.** "Revoga a decisão de 28/07" is a sentence that saves an
   argument later.
3. **Evidence or a mark, never a confident guess.** Path and value for anything read from disk;
   author and year for anything from literature; `[não verificado]` for anything you cannot
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
Diverge phase's rule (`references/phase-diverge.md`) and it starts here — with the brief not
pre-loading the answer.

## Cooperation contract

| Artifact                                                                     | Produced by                               | Consumed by                                     |
| ---------------------------------------------------------------------------- | ----------------------------------------- | ----------------------------------------------- |
| `.brisar/session.yaml` (`research:` section)                                 | Research                                  | Brief (Step 1 — the material)                   |
| `.bb/tasks/<slug>/spec.md` (`## problem`/`## hypothesis`/`## fit`/`## cuts`) | `/bb:discover`, `/bb:spec`                | Brief (Step 2 — reconciliation)                 |
| `.bb/tasks/<slug>/brief-design.md`                                           | **Brief** (and updated every later round) | Diverge, Develop, Deliver, the implementing dev |
| `.brisar/session.yaml` (`brief:` + `gate.design_brief`)                      | Brief                                     | Diverge, Develop, Deliver, re-entry             |
| Delta back into `spec.md`                                                    | Deliver (material from here)              | `/bb:implement`, `/bb:spec`                     |
