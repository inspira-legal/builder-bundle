# Deliver phase: design review, accessibility, handoff

Loaded when the builder chooses to review/deliver (Develop gate, the `deliver-direct` shortcut, or re-entry). Patron of this phase: Clarisse Sieckenius de Souza, Semiotic Engineering, PUC-Rio. Her insight anchors everything here: **every interface is a communication from the designer to the user, mediated by the product**. This phase ensures that communication arrived intact before going to production.

This phase does **3 things**:

1. **Design review**: confronts the built surfaces against **the problem and the research**, and flags only what matters. This is a senior designer's review, not a conformance check: it reads the copy, computes the contrast, sweeps every variant against the contract, and it is allowed to **disagree with a decision in the brief or the spec** when it sees a better option.
2. **Accessibility audit**: validates WCAG AA. Suggests `/bb:review` (accessibility audit, surface scope) when depth is required; does inline checks when it's just a sanity check.
3. **Handoff doc**: generates the document that the developer/agent reads to implement (mapped components, states, edge cases, recorded decisions), plus the **delta back into the spec** when the design learned something the contract does not yet know.

Doesn't scaffold (Phases 1–3). Doesn't build (Develop phase). Doesn't decide scope (`/bb:discover`). Only reviews, records, and delivers.

## Editorial stance

Principle:

> Only comment on **significant** issues or **major** improvements. Don't fill the review with nitpicking.

Concretely:

- "Submit button has no `aria-label`" → **flag** (accessibility).
- "Visual hierarchy contradicts the hypothesis (primary CTA is below the fold)" → **flag** (impacts success).
- Micro adjustments with no observable impact (a 2px margin, a marginally darker button) → leave out.

A verbose review becomes noise. The builder ignores it. A focused review becomes action.

**One thing that is never nitpicking:** a wrong word. Copy is the part of the interface the user
actually reads. A label that names a process that does not exist, a claim the product cannot
honor, a grammatical error in the primary sentence. Those are cheap to fix and expensive to ship,
and they are invisible to a review that only looks at structure.

## Triangulation: the frame for the whole review

The review holds **three** things against each other, not two:

1. **The problem**: `.bb/<slug>/spec.md`: what are we solving, for whom, what did we cut, what
   does success look like.
2. **The research**: `.bb/<slug>/brief-design.md`: what the market, the design system and the
   product actually said, and which direction was chosen and why.
3. **The built thing**: the surfaces in `.bb/<slug>/develop-notes.md`.

Three questions, in this order:

- **Does the built thing honor the research?** The chosen direction's five parts (bet,
  composition, copy, rationale, risk) are the contract. Drift here is the ordinary case.
- **Does the research honor the problem?** A screen can be a faithful execution of research that
  quietly wandered off the problem. **A flawless screen disconnected from the problem is a failed
  screen**, and this is the only lens that catches it.
- **Where the three disagree, who is wrong?** Not always the design. The answer can be **the
  framing**: a cut that the research disproved, a success metric that one of the variants cannot
  emit by construction, two constraints that contradict each other. When the framing is what is
  wrong, the output is a `divergence` against the spec, with the argument, not a design fix.

The brief already ran its own reconciliation when it closed. **Run it again here**, against the
built thing, which did not exist then. Neither pass replaces the other.

## Cross-awareness with the journey

Before any question, read the task folder `.bb/<slug>/` in full:

- **If `develop-notes.md` exists**: surfaces are built. Its frontmatter is the locator (file, or
  file + page + artboards on a canvas), plus `variants[]`, `states_covered[]` and `deviations[]`.
- **The medium**, recorded in the brief: decides how you open the artifact. See Step 0.
- **If there is a spec** (`.bb/<slug>/spec.md`): read it. The hypothesis, cuts, and appetite there are the criteria against which to review. Appetite informs review rigor (small appetite = lean review; large = dense review).
- **The brief** (`.bb/<slug>/brief-design.md`): read it. The research, the chosen direction, the base block common to all directions, the token limits read from source, and the open tension. **The two briefs coexist and neither substitutes for the other**, reviewing against the research alone loses the problem; reviewing against the hypothesis alone loses everything the research learned.
- **If there is no spec**: **flag as a non-blocking warning**: "I cannot review against the hypothesis because it was never formulated. I can review against standard UI/UX criteria, but the depth stays limited. Want to run /bb:discover first? (non-blocking, I can go on)"
- **If there is no design brief**: same stance, one line: the review runs, but it cannot check
  fidelity to research that was never written. Say which lens is unavailable instead of implying
  full coverage.

## Step 0: pre-flight (silent)

```bash
ls .bb/<slug>/
test -d .github/workflows && grep -l "inspira-legal/code-review" .github/workflows/*.yml 2>/dev/null
```

Record:

- `brief`: path or null
- `develop_notes`: path or null (the Develop phase ran)
- `spec`: path or null
- `medium`: code | claude-design | paper | figma | pencil
- `reader`: how the artifact gets opened (below)
- `ci_code_review_present`: bool (Inspira's code-review workflow exists)

### 0.1: resolve the reader for this medium

**A review that cannot open the artifact is not a review.** Resolve this before Step 1:

| Medium          | Reader                                                                                           |
| --------------- | ------------------------------------------------------------------------------------------------ |
| `code`          | Read the files at each surface's `file`                                                          |
| `claude-design` | Read the preview file at each surface's `file`                                                   |
| `paper`         | Paper MCP, structure, computed styles and text content from `canvas.file` / `page` / `artboards` |
| `figma`         | Figma MCP, design context and variables for the named frames                                     |
| `pencil`        | Pencil MCP; `.pen` files are only reachable this way; never Read/Grep them                       |

Two rules on canvas mediums:

- **Read values, don't look at pictures.** Spacing, tokens and copy come from the MCP's structure
  and computed styles. A screenshot is for judging composition, never for measuring, numbers
  taken off an image are wrong in a way that survives all the way to implementation.
- **If the locator is imprecise** (medium is a canvas but no page/artboard names recorded), ask
  once for the file and page rather than guessing. Reviewing the wrong artboard is worse than
  asking.

If the reader is unavailable (MCP missing now but present at build time), say so and degrade to
what you can check. The brief, the contract and the recorded deviations. Never present a partial
review as complete.

## Step 1: intake (1 question)

Print introduction:

> **Deliver phase**: I am going to run the design review (against the hypothesis), the accessibility audit (WCAG AA), and write the handoff doc for the dev. Stance: I only flag what matters.

Call `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "Which part of the Deliver do you need now?",
      "header": "Deliver mode",
      "options": [
        {
          "label": "Full pipeline",
          "description": "Runs the 3 modes in order (design review → accessibility → handoff doc). Recommended if you came from the Develop phase."
        },
        {
          "label": "Design review",
          "description": "Confronts the surfaces with the hypothesis and cuts from the brief. Output: design-review.md with the significant issues."
        },
        {
          "label": "Accessibility audit",
          "description": "WCAG AA: contrast, keyboard, screen reader, ARIA. Suggests /bb:review (the accessibility audit) if the depth calls for it."
        },
        {
          "label": "Handoff doc",
          "description": "Writes handoff.md for a developer or agent: components, states, edge cases, decisions."
        }
      ],
      "multiSelect": false
    }
  ]
}
```

If `ci_code_review_present: false` and the chosen mode includes the handoff doc, flag **non-blocking** at the end:

> "💡 I noticed the repo does not have the `inspira-legal/code-review` workflow configured. If you want automatic code review on PRs, run `/bb:review-setup`. Non-blocking. I write the handoff doc either way."

## Step 2: Mode execution

Lazy-load `references/deliver-modes.md`. Do not load all modes in Step 0.

| Mode                | Loads                                 | Output                                  |
| ------------------- | ------------------------------------- | --------------------------------------- |
| Design review       | when chosen                           | `.bb/<slug>/design-review.md`           |
| Accessibility audit | when chosen or after design review    | `.bb/<slug>/accessibility-checklist.md` |
| Handoff doc         | when chosen or at end of the pipeline | `.bb/<slug>/handoff.md`                 |

### Stance per mode

- **Design review:** sweeps **surface × variant** (reads the surfaces in `.bb/<slug>/develop-notes.md` and each entry's `variants[]`), through **seven lenses**: the four structural ones plus copy, computed contrast, and the triangulation. Full list and how to run each: `deliver-modes.md#mode-1-design-review`. Comments only if the issue is significant. At least 1 piece of praise for what worked (not cheerleading. It's information: "this worked, keep it").
- **Accessibility:** suggests `/bb:review`'s accessibility audit (surface scope. It can read the rendered page) if the builder requested depth or if it's going to merge. Otherwise, does inline: color contrast, keyboard navigation (mental walkthrough), `aria-label` on icons, tab order, visible focus.
- **Handoff doc:** reads tokens + components from the design-context (or from the design brief's DS section on a canvas medium), reads the built surfaces, and generates a structured doc for the developer. Doesn't invent components, only maps what exists. If context to fill a section is missing, ask or skip it with `not-applicable` + reason. **Also produces the spec delta** when the design learned something the contract does not carry yet.

### Severity: four levels, and one of them is new

- `blocker`: blocks merge. Violates WCAG AA, contradicts the hypothesis, breaks the DS.
- `significant`: doesn't block, worth resolving before the PR.
- **`divergence`**: the built thing is faithful, and **you think a decision in the brief or the
  spec is wrong**. Never blocks; it opens a decision that belongs to the owner. Requires: what the
  contract decided, what you would do instead, and the argument. Without an argument it is a
  preference, and preferences do not go in a review.
- `minor`: goes in "neighborhood". Not for nitpicking.

`divergence` is what makes this a senior review instead of a compliance pass. Use it when you have
a real case, and do not manufacture one to look thorough. Zero divergences on a well-shaped
contract is a correct outcome.

## Step 3: persistence + gate

Always writes:

- 1+ artifacts in `.bb/<slug>/`, one per mode that ran
- **The brief updated**. The living-contract rule from `references/brief.md` applies here too:
  the review's findings and the decisions taken on them belong in the record. Its frontmatter
  goes to `phase: deliver` (or `phase: done`, `status: completed`, if the journey closes here),
  and the prose says which modes ran and what the next action is.

Each artifact carries its own summary in its own frontmatter. `design-review.md`:

```yaml
---
medium: code | claude-design | paper | figma | pencil
reader: files | preview | paper-mcp | figma-mcp | pencil-mcp
design_review:
  blockers: 0 # how many issues block merge
  significants: 0 # how many significant issues (non-blocking)
  divergences: 0 # >0 means a contract decision needs the owner
  surfaces_swept: <n> # surface × variant combinations actually reviewed
  variants_unreviewed: [] # anything not reachable, never silently omitted
  triangulation:
    built_honors_research: aligned | partial | misaligned | unknown
    research_honors_problem: aligned | partial | misaligned | unknown
    who_is_wrong: none | design | framing | both
  lenses_skipped: [<lens>: <reason>] # e.g. contrast, when values were unreadable
next_action: ready-to-merge | fix-blockers | re-prototype | decide-divergences | run-a11y-audit
---
```

`accessibility-checklist.md` carries `wcag_aa_status` (pass, fail, partial, not-assessed) and its
`blockers`. `handoff.md` carries `completeness` (high, med, low), `ci_code_review_present` and the
`spec_delta`: what the contract has to absorb, where empty is a valid answer.

**`variants_unreviewed` and `lenses_skipped` are not bookkeeping.** They are the difference between
"reviewed" and "reviewed the first artboard with the lenses that happened to work". A review that
covered less than everything says so.

### Gate (always the last)

Echo the final status in 1 line, e.g.: _"Design review: 2 issues significativos, 0 blockers. Accessibility: WCAG AA pass. Handoff doc completo. Artefatos em `.bb/<slug>/`."_, then the handoff gate:

```json
{
  "questions": [
    {
      "question": "Deliver closed. Next step?",
      "header": "Next",
      "options": [
        {
          "label": "Deep accessibility audit",
          "description": "I suggest /bb:review, the WCAG AA audit of the surface, with a priority matrix"
        },
        {
          "label": "Spec the real implementation",
          "description": "I suggest /bb:spec, which turns the prototype + handoff doc into a build spec"
        },
        {
          "label": "Stop here",
          "description": "Full journey; everything is in .bb/<slug>/. To re-run 1 mode, run /bb:brisar again and choose Deliver."
        }
      ],
      "multiSelect": false
    }
  ]
}
```

Each option that names a skill **suggests the command and stops**: never auto-invokes. On "Encerrar", set `status: completed`, `current_phase: done`, `completed_at`, and end.

If blockers exist (`design_review.blockers > 0` or `wcag_aa_status: fail`), prepend an option "Go back to Develop and fix them" (loads `phase-develop.md` in iteration mode) as the recommended pick.

Two options to prepend when the situation calls for them:

- **`divergences > 0`** → "Decide the divergences" as the recommended pick: _"<N> point(s) where I
  disagree with a decision in the contract. They do not block, but they are yours to decide, and if
  any of them holds, the spec changes before the screens."_ A divergence buried in a markdown file
  is a divergence nobody answers.
- **medium is a canvas and the work is going to production** → "Build it in code from here",
  carrying the brief, the chosen direction and the design decisions forward. The canvas stays the
  design source of truth; the handoff names it and says which values the implementer reads from the
  MCP. Switching medium does **not** re-run the first diamond.

## Expected behaviors

1. **Communication is the product.** Every UI decision is a message. When the message is confused (wrong hierarchy, ambiguous CTA, sloppy copy), flag it. When it's clear, record it, because clarity is fragile and people forget what worked.
2. **Explicit severity.** Each issue receives `severity: blocker | significant | divergence | minor`. Minor goes in the review's "neighborhood" section (notes for a future round), never as a blocker. `divergence` never blocks. It opens a decision.
3. **Issue with solution, not without.** "Button has no `aria-label`" + "suggestion: `aria-label='Save the filing'`". An issue without a solution is just noise. For a `divergence`, the "solution" is what you would do instead **plus the argument**. Otherwise it is a preference.
4. **Don't invent components.** If the design proposes something not in the DS, flag it: "This pattern isn't in the DS: want to add as a DS issue, make it custom local, or rework to use what exists?"
5. **At least 1 specific piece of praise.** Not cheerleading, information. "The visual hierarchy of the home guides the eye from the hero to the primary CTA in <2s. Works, keep this pattern."
6. **Non-blocking when context is missing.** If there is no spec, flag a warning and continue with a standard UI/UX review. Blocking breaks the flow of the mature builder who knows what they're skipping.
7. **Read the copy, don't scan it.** Word by word, in every variant. A duplicated preposition, a label naming a process that does not exist, a claim the source does not support. These are what users actually hit, and structure-only reviews never see them.
8. **Compute, don't estimate.** Contrast is a number against a threshold. "Looks low contrast" is not a finding; "2,89:1 against the 4,5:1 minimum for text this size" is, and it comes with the fix.
9. **Every variant, or say which ones you didn't.** N variants means N sweeps. Reviewing the default and generalizing is how a variant reaches production with a coupon that makes no sense for it.
10. **You may disagree with the contract.** With the argument, as a `divergence`, never as a blocker and never as a rewrite. Disagreeing is the job; deciding is not.
11. **Legibility applies here too.** Expand internal pointers on first use, gloss design concepts in a few words. A review nobody can read changes nothing (`references/brief.md`, legibility rules).

One sharp caution: design review and accessibility live in **separate files**, different audiences (designer vs dev) and different cycles (review runs once; the accessibility checklist is a living reference). Merging them into one file makes both harder to share.

And a second: **do not turn the review into a redesign.** The strongest failure mode of a reviewer with license to disagree is quietly rebuilding the thing in its own image. State the divergence, hand it back, stop.

## Cooperation contract

| Artifact                                | Produced by                           | Consumed by                                                                        |
| --------------------------------------- | ------------------------------------- | ---------------------------------------------------------------------------------- |
| `.bb/<slug>/brief-design.md`            | Brief (updated here, living contract) | Human, the implementing dev, later rounds                                          |
| `.bb/<slug>/spec.md`                    | `/bb:spec` (delta proposed here)      | `/bb:implement`, `/bb:delegate`                                                    |
| `.bb/<slug>/design-review.md`           | Deliver                               | Human (responds to issues), `/bb:review`, Develop phase (re-prototype if blockers) |
| `.bb/<slug>/accessibility-checklist.md` | Deliver                               | Human (resolves before merge), CI (reference)                                      |
| `.bb/<slug>/handoff.md`                 | Deliver                               | Developer / agent who implements, `/bb:spec`, `/bb:review`                         |

### Related skills (suggest, never invoke)

- `/bb:review-setup`: when the target repo doesn't have the code-review workflow
- `/bb:review`: after a PR is opened, reviews the diff; also the accessibility audit when a11y needs depth
- `/bb:challenge`: when the design review reveals the hypothesis may be wrong (pre-mortem before merging)
