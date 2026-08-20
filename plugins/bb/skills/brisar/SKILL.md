---
name: brisar
description: End to end design trilha. The whole double diamond, from the raw idea to a reviewed delivery, for designers and non designers alike. Research before pixels, consolidated into a design brief that stays a live contract, diverges into directions and asks where to explore (code, Claude design, Figma, Paper or Pencil); then it builds, critiques, and closes with accessibility, handoff and the delta back to the spec. Scales the effort and states what it skipped. Use when the builder says "let's start", "new project", "design a screen in <brand>", "build a prototype", "research before drawing", "show me directions", "build the surface", "review the prototype", "design handoff", "I have an interface idea". Don't use it to frame a product problem (that is /bb:discover) or to write a formal execution spec (that is /bb:spec).
license: MIT
metadata:
  author: Inspira
  version: 2.7.0
---

# Brisar

The design trilha in one skill. **The whole double diamond**, for designers and
non-designers alike. Get ANY builder (executive, senior, junior, content) from "I
have an idea / I need to work on X" to a reviewed artifact, calibrating depth and
vocabulary by profile.

**First diamond, understand the space before drawing in it:**

- **Research**: market bench, the design system read from source, and what the
  product actually has to show (`references/phase-research.md`).
- **Brief**: the research consolidated into a written contract, reconciled
  against the problem framing (`references/brief.md`).
- **Diverge**: distinct directions, all described at the same depth, then
  converge (`references/phase-diverge.md`).

**Then the medium**, because the brief serves any of them and only the build
changes: code, Claude design, Figma, Paper or Pencil (`references/phase-medium.md`).

**Second diamond, build it and hold it to account:**

- **Develop**: build high-fidelity surfaces against the contracts
  (`references/phase-develop.md`).
- **Deliver**: design review, accessibility audit, handoff doc, and the delta
  back into the spec (`references/phase-deliver.md`).

Each stage is entered explicitly (the builder asks, a shortcut routes there, or
the previous stage's gate suggests it). The skill never rolls from one stage to
the next silently.

## Execution principles

1. **Every question via `AskUserQuestion`**: rationale in the plugin-root
   `references/handoff-gate.md`.
2. **The profile is already in the session.** `~/.claude/BUILDER-BUNDLE.md`
   carries it, written from `~/.claude/bb.config.json`; brisar never asks who is
   building. With no profile, run `/bb:profile` once and continue with the answers.
3. **Adapt depth and vocabulary to the profile.** Each phase reads the flag it
   needs: `reads_code` sets how many questions and in what language,
   `technical_vocabulary` decides whether `scaffold`, `embed` and `MCP` appear
   at all, `uses_terminal` decides whether a path needs a command, and
   `technical_instructions` decides how a command is written. The contract is the
   plugin-level `references/bb-config.md`.
4. **Detect > ask.** Step 0 cross-references cwd with the product registry; a
   match settles brand and hosting without asking. Tooling gaps are detected in
   preflight, not asked. **Exception: the medium is always asked**, assuming it
   scaffolds a repo for someone who wanted a canvas, or opens a canvas for
   someone shipping today.
5. **Lightning intake max 3 questions.** If you find yourself preparing a
   fourth, stop, it's turning into a form. (With `reads_code` false it goes up
   to 5-6, but in everyday language.)
6. **Maturity gate is an invitation, not a block.** An override costs one line
   in the brief's decision log; blocking costs trust.
7. **Scaffold ≠ planning.** This skill WRITES real files. If Bash fails,
   surface the error. Don't fake success.
8. **The research floor never scales down, and what is skipped is said.**
   Every mode runs market bench + the DS read from source + "does this need a
   new component?". Everything else is judged and **declared** in one line.
   Silent scope reduction reads as thoroughness and is the opposite.
9. **Directions get equal treatment.** A recommendation is fine; describing one
   direction in depth and the others in a sentence decides for the builder while
   pretending to offer a choice.
10. **The brief is a living contract.** Every round updates it, without being
    asked. It ends as a delta back into the spec. Where brief and spec disagree,
    **the spec wins**: the brief is the research record, the spec is the contract.
11. **Suggest, never auto-invoke.** Other skills (/bb:discover, /bb:spec,
    /bb:challenge, /bb:review) are always suggested via handoff gate.
    Internal phase transitions also go through a gate. The builder crosses them
    on purpose. The one exception inside this skill: Research flows straight into
    Brief, because the research is the brief's input and does not stand alone.
12. **The review may disagree with the contract.** With the argument, as a
    `divergence`, never as a blocker and never as a silent rewrite. Disagreeing
    is the job; deciding belongs to the owner.
13. **Never block due to missing tooling.** git missing → manual instructions.
    MCP missing → markdown handoff, or a medium that needs no MCP. There's always
    a fallback.
14. **Write for the non-designer.** Expand an internal pointer on first use, gloss
    a design concept in 5–10 words. Dense is fine; needing a decoder is not.
15. **Deliver visual direction before Develop.** The Develop phase needs the
    surface's direction file; without it the builder is back to guessing the
    screen.

---

## Step 0: pre-flight (silent)

Before any question, five checks, without printing anything to the user.
Nothing is written yet: the answers are held in context until Phase 1 confirms
the slug, and the first write is the brief itself.

### 0.1: is there a journey already in this project?

The brief is what carries a journey, so finding one is the whole resume:

```bash
BB=$(d=$PWD; while [ "$d" != / ] && [ ! -d "$d/.bb" ]; do d=$(dirname "$d"); done; echo "$d/.bb")
ls "$BB"/*/brief-design.md "$BB"/tasks/*/brief-design.md 2>/dev/null
```

The walk-up matters: a re-entry from inside the project folder would miss a brief that lives in
the `.bb/` one level up, and "never re-run the research over an existing brief" would fail
silently, the worst way for that rule to fail. If more than one brief matches, ask which one.

A brief on disk means the journey already ran, possibly in a much earlier session, possibly by
someone else. **Do not re-run it and do not rewrite it.** Read its frontmatter, `phase` and
`status`, and resume from there:

| Frontmatter                                | Resume at                                   |
| ------------------------------------------ | ------------------------------------------- |
| `status: bootstrapped-to-discover`         | Research, with the spec next to it (below)  |
| `status: completed`                        | ask: Develop, a new surface, or a new round |
| `phase: research`, findings, no directions | Diverge                                     |
| `phase: diverge`, none marked `chosen`     | Diverge, at convergence                     |
| a chosen direction, nothing built          | the medium question                         |
| a chosen direction and surfaces built      | Deliver                                     |

On `status: bootstrapped-to-discover`, the maturity gate fired earlier and the builder went to
/bb:discover. The spec it wrote is the file next to the brief in the same task folder (the
spec-state contract, plugin-level `references/spec-state.md`: `.bb/<slug>/spec.md` carrying
`## Problem` / `## Fit`, or the older names on a previous spec). Let the appetite and the cuts
inform fidelity and scope, and resume at the **Research phase**: the intake is already in the
brief, and the framing is exactly what the research has to test.

Say in one line what you found and where you are resuming, then continue. Re-running research
over a brief that already exists is the most expensive mistake available here, and it destroys
the record of rounds the brief was keeping.

A `.brisar/` folder from an older run may still be sitting in the project. Read it once for
whatever context it holds, and leave it where it is. Nothing is written back to it. If its
`session.yaml` carries a `profile.persona_id` and there is no `~/.claude/bb.config.json`,
that is an answer the person already gave: derive the four flags from it (the table in the
plugin-level `references/bb-config.md`) and offer `/bb:profile` to write them down.

### 0.2: detect Brisa DS

Heuristic in order (stop at the first one that works):

1. Variable `BRISAR_DS_PATH`.
2. The project it is running in: a `design-context/` at the root, or the DS the detected product declares (`ds_source`).
3. Bundled: `references/ds/` **in this skill's own directory**. Ships with the
   plugin; contains `brand/DESIGN.md` + sub-brands + voice references.

If nothing works, record `ds_path: not-found` and continue in brand free-text
mode.

This resolves the **brand**: voice, principles, sub-brand identity. It is not the
production token source, and its bundled `brand/tokens/tokens.json` must not be
used as one; the research phase locates the real one from the repo, or remotely
via `gh` (`references/phase-research.md`, Front B).

### 0.3: build the brand registry

If DS found, glob `brand/DESIGN.md` (base) + `brand/*/DESIGN.md` (sub-brands).
Read the first line of each (`# {Brand}. Style Reference`) for the canonical
name. Always add `No brand / custom` and `I do not know yet` as final options.

### 0.4: tooling preflight

Detects what's installed: git, gh + auth, MCPs (unframer, figma, etc). Details
in `references/preflight-tooling.md`. The result is held in context, the
questions it removes are simply not asked.

**Critical principle:** preflight informs the path, never blocks. If git is
missing and `uses_terminal` is true, warn and offer to resolve. If MCP unframer
is missing on the Framer path, fall back to the markdown handoff.

### 0.5: detect product by cwd

Reads `references/product-registry.yaml` and evaluates each product's
`detection[]` against the cwd. First match wins (registry order is priority).

When detected:

- Skip the brand question in Phase 1 (already known by `product.brand`)
- Skip the hosting question (already known: `mode_default: embed`)
- Load `repo_url`, `ds_source`, `requires_mcp` for the later flow
- Hold it in context; the brief records the product it landed on

If no match: record `product.detected: unknown` and continue. Phase 1 asks
brand normally.

**Important:** detection is by marker in the filesystem (file/dir/contains),
never by folder name.

---

## Navigation map (lazy load)

Each phase lives in a separate file under `references/`. **Don't load all files
in Step 0**, open only what the current phase needs.

| Phase                                                              | When to load                                                                                                                                                                                                                         | File                                                                     |
| ------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------ |
| Pre-flight tooling                                                 | Step 0.4                                                                                                                                                                                                                             | `references/preflight-tooling.md`                                        |
| Product registry                                                   | Step 0.5 + Phase 1                                                                                                                                                                                                                   | `references/product-registry.yaml`                                       |
| Phase 1, Lightning intake                                          | First phase. Depth adapts to `reads_code`.                                                                                                                                                                                           | `references/phase-1-intake.md`                                           |
| Phase 2, Maturity gate                                             | After Phase 1, EXCEPT when `brand.workflow == framer-harpa`                                                                                                                                                                          | `references/phase-2-gate.md`                                             |
| **Research, the first diamond**                                    | After Phase 2, before anything is drawn. Skip only for a trivial mechanical change.                                                                                                                                                  | `references/phase-research.md`                                           |
| **Brief, the design contract**                                     | Straight after Research (no gate between them) and again on **every later round** that changes a decision                                                                                                                            | `references/brief.md`                                                    |
| **Diverge, directions in equal standing**                          | After the Brief gate, when the builder chooses to diverge                                                                                                                                                                            | `references/phase-diverge.md`                                            |
| **Medium, where to explore**                                       | After Diverge, before Phase 3. Also when Develop is reached by shortcut with no `medium` recorded.                                                                                                                                   | `references/phase-medium.md`                                             |
| Phase 3, Scaffold (real files)                                     | After the medium question, and **only** when `medium.chosen == code`. `uses_terminal` picks the variant: true = normal scaffold; false = `prototype-hosted`                                                                          | `references/phase-3-scaffold.md`                                         |
| Phase 4, Design direction                                          | After Phase 3. **Skip only the per-surface prose** when a design brief already carries the chosen direction, but Step 4 (recording `surfaces[]` in the direction's own frontmatter) always runs, because four readers join that list | `references/phase-4-design-direction.md`                                 |
| **Phase Framer-handoff** (replaces Phase 2+3+4 on the Framer path) | When `brand.workflow == framer-harpa`                                                                                                                                                                                                | `references/phase-framer-handoff.md`                                     |
| Phase 5, Terminal report                                           | Always, last phase of the direction stage.                                                                                                                                                                                           | `references/phase-5-handoff.md`                                          |
| **Develop**, hi-fi surface construction                            | Builder asks to build, a shortcut routes here, or the Phase 5 gate chose it                                                                                                                                                          | `references/phase-develop.md` (+ `references/develop-modes.md` per mode) |
| **Deliver**, review, accessibility, handoff                        | Builder asks to review/hand off, a shortcut routes here, or the Develop gate chose it                                                                                                                                                | `references/phase-deliver.md` (+ `references/deliver-modes.md` per mode) |
| The brief's frontmatter, the journey's only state                  | When you need to know or record where the journey stopped                                                                                                                                                                            | `references/brief.md`                                                    |

---

## Cooperation contract: who produces, who consumes

| Artifact                                                                  | Produced by                                                                | Consumed by                                                                                                                 |
| ------------------------------------------------------------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **`.bb/<slug>/brief-design.md`**                                          | **Brief**, and updated by every later round, including Deliver             | every phase (each reads it in its Step 0), Diverge, Develop, Deliver, the implementing dev, later rounds                    |
| `<slug>/design-context/tokens.md` + `components.md`                       | Phase 3 (medium `code` only)                                               | Develop (Step 0). On canvas mediums the DS values come from the Research instead                                            |
| `.bb/<slug>/design.md` (or `design/<surface>.md`)                         | Phase 4                                                                    | builder, Develop, complements the design brief (brief = chosen direction; this = per-surface hierarchy, states, components) |
| `<slug>/...` (vite, package.json, src/)                                   | Phase 3                                                                    | builder (`pnpm install && pnpm dev`), Develop                                                                               |
| `<slug>/HANDOFF-DEV.md`                                                   | Phase 3 (when `uses_terminal` is false)                                    | dev who picks up the prototype later                                                                                        |
| `.bb/<slug>/develop-notes.md`                                             | Develop (optional decisions log)                                           | Deliver, builder                                                                                                            |
| `.bb/<slug>/design-review.md`, `accessibility-checklist.md`, `handoff.md` | Deliver                                                                    | builder, implementing dev                                                                                                   |
| `.bb/<slug>/spec.md`                                                      | /bb:discover, /bb:spec (outside this skill); **delta proposed by Deliver** | Step 0.1 (bootstrap return), Research, Brief, Diverge, Develop, Deliver                                                     |
| `harpa-handoff-<slug>-<date>.md` (in cwd)                                 | Framer/content path                                                        | builder inside `harpa-lpbuilder/`                                                                                           |

Each phase reads the whole brief in Step 0 and writes **only its own
sections** at the end, cross-awareness without coupling. The brief's
frontmatter (`status`, `phase`, `round`) is the journey's state; there is no
second file holding a copy of it (`references/brief.md`).

### Framer path (Site Institucional)

When the builder chooses "Site institucional (Framer)" on Question 2, or the
brand carries `brand.workflow == framer-harpa`, brisar forks: **does not scaffold**, **does
not create the `<slug>/` folder**, **does not generate design-context/**.
Instead, it generates `harpa-handoff-<slug>-<date>.md` in the cwd with intent +
visual direction in Framer idiom + instructions to open Claude Code inside
`harpa-lpbuilder/`.

**Variant when MCP unframer is missing:** generate the markdown handoff anyway,
without MCP. The dev/designer takes it to Framer manually. The Develop phase
is not used on this path. Details in `references/phase-framer-handoff.md`.

### Bootstrap protocol (brisar → /bb:discover → brisar)

When the maturity gate fires and the builder accepts framing the problem first, brisar
opens `.bb/<slug>/brief-design.md` with `status: bootstrapped-to-discover` and
`phase: research` in the frontmatter, the intake's answers (intent, brand, artifact) in
prose, and the gate's resolution in the decision log.

…then suggests running `/bb:discover <ideia>` and stops (never auto-invokes).
/bb:discover keeps its own state in `.bb/<slug>/spec.md`. When the
builder returns and runs `/bb:brisar` again, Step 0.1 reads that frontmatter, finds the
spec next to the brief, and resumes at the **Research phase** with the framing carried
over.

### The spec and the design brief: they coexist, neither replaces the other

Two documents in the same task folder, two different questions, and later phases read
both:

| File                                                                   | Answers                                              | Written by                 |
| ---------------------------------------------------------------------- | ---------------------------------------------------- | -------------------------- |
| `.bb/<slug>/spec.md` (`## Problem`/`## Hypothesis`/`## Fit`/`## Cuts`) | Is it worth building, for whom, and what did we cut? | `/bb:discover`, `/bb:spec` |
| `.bb/<slug>/brief-design.md`                                           | How should this surface be, and why?                 | the Brief phase here       |

**Never substitute one for the other.** Reviewing against the research alone loses the
problem; reviewing against the hypothesis alone loses everything the research learned.
The Brief phase reconciles the two when it closes, and Deliver reconciles them again
against the built thing, the artifact that did not exist the first time.

### Critical path rule

The paths are derived, not persisted. `design-context/` sits at the root of the
scaffolded folder Phase 3 created; the visual direction is `.bb/<slug>/design.md` (or
`design/<surface>.md`), next to the spec in the task folder (plugin-level
`references/spec-state.md`). Develop and Deliver derive both from the slug, no
hardcoded string on either side.

**On canvas mediums there is no design-context**, by design
(`medium.scaffold: skipped`). The DS values come from the Research phase, which read
the same source one step earlier. Its absence on those paths is the normal state, not
a failure to report.

---

## Full flow

```
Step 0: Pre-flight (silent)
  0.1 → detect existing session (incl. bootstrap return → Research)
  0.2 → detect Brisa DS (bundled at references/ds/)
  0.3 → build brand registry (from the DS)
  0.4 → tooling preflight (git, gh, MCPs, incl. paper/figma/pencil/mobbin, both scopes)
  0.5 → detect product by cwd (product-registry.yaml)

Phase 1: Lightning intake (max 3 questions, depth by reads_code)
  → shortcut router may jump straight to Develop, Deliver, or /bb:discover
  → brand.workflow == framer-harpa: skips straight to Phase Framer

Phase 2: Maturity gate (senior/junior only)
  → production/will-scale → suggest /bb:discover or /bb:spec (bootstrap protocol)

╭─ FIRST DIAMOND ─────────────────────────────────────────────────────────────╮
│ Research: research before the pixel                                         │
│   → declare the mode (pocket|full): what runs, what was skipped, why,       │
│     and what any degraded front invalidates                                 │
│   → floor, always: bench · DS read from source · new component?             │
│     no Mobbin → galleries/prints (login wall) · no repo → gh remote read    │
│   → discretionary: biases w/ provenance · heuristics · mental models ·      │
│     what the product has to show                                            │
│   → fan-out in parallel subagents; only the distillate returns              │
│   → NO GATE, flows straight into Brief                                      │
│                                                                             │
│ Brief: the design contract                                                  │
│   → .bb/<slug>/brief-design.md, the journey in its own frontmatter          │
│   → reconcile vs the framing: confirms · contradicts · does not reach       │
│   → close on an unresolved tension (none found = research was shallow)      │
│   → present it in chat: findings · references · directions · tension        │
│     (round ≥2 = the delta only; each block must enable a decision)          │
│   → gate: build the paths / resolve the contradiction / stop here           │
│                                                                             │
│ Diverge: directions on equal footing                                        │
│   → declare the base common to all directions first                         │
│   → ≥2 directions, each with all 5 parts (bet·composition·copy·             │
│     rationale·risk); equal-treatment check BLOCKS the gate                  │
│   → converge: chosen + runner-up + discarded + pivot condition              │
│   → recommendation MANDATORY when reads_code is false                       │
│   → gate: build / switch path / search further / stop here                  │
╰─────────────────────────────────────────────────────────────────────────────╯

Medium: where to explore (1 question, offers only what's detected)
  → code | claude design | paper | figma | pencil
  → canvas mediums set scaffold: skipped

Phase 3: Scaffold OR prototype-hosted     [medium == code only]
  → senior + detected product = embed (clone via gh)
  → senior/junior + greenfield = local Vite scaffold
  → executive = prototype-hosted (folder + HANDOFF-DEV.md, no local npm install)

Phase 4: Design direction        [prose skipped when the brief has it]
  → .bb/<slug>/design.md, or design/<surface>.md per surface (max 5)

Phase Framer (replaces Phase 2-4 on the Framer/content path)
  → harpa-handoff-<slug>-<date>.md, with or without MCP unframer

Phase 5: Terminal report + gate
  → report what was created, written for the profile
  → gate: continue to Develop / run /bb:discover / stop here

╭─ SECOND DIAMOND ────────────────────────────────────────────────────────────╮
│ Develop (entered via gate, shortcut, or direct ask)                         │
│   → build in the chosen medium, against the direction + tokens              │
│   → record a precise locator per surface × variant, plus deviations         │
│   → gate: continue to Deliver / add surface / stop here                     │
│                                                                             │
│ Deliver (entered via gate, shortcut, or direct ask)                         │
│   → open the artifact via the reader for its medium                         │
│   → review surface × VARIANT through 7 lenses: fidelity · hypothesis ·      │
│     hierarchy · DS+states · COPY word-by-word · CONTRAST computed ·         │
│     TRIANGULATION (problem × research × built)                              │
│   → severity: blocker · significant · DIVERGENCE · minor                    │
│   → accessibility + handoff doc + DELTA back into the spec                  │
│   → gate: settle the divergences / build in code / /bb:review (a11y)        │
│     / /bb:spec / stop here                                                  │
╰─────────────────────────────────────────────────────────────────────────────╯
```

Two sharp cautions:

**Never overwrite an existing brief without asking**: a restart appends a new round
to `.bb/<slug>/brief-design.md`, it does not replace what is there.

**Changing medium does not reopen the first diamond.** Explore on a canvas, then build
in code, is the normal path. The research, brief and chosen direction are already
settled. Say so out loud when it happens, so nobody expects a fresh interview.
