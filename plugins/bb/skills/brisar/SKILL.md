---
name: brisar
description: Trilha de design ponta a ponta — duplo diamante inteiro, do "tenho uma ideia" à entrega revisada, pra designer e não-designer. Pesquisa antes do pixel (referências de mercado, o design system lido da fonte, o que o produto já tem), consolida num design brief que é contrato vivo, diverge em direções tratadas em pé de igualdade, e pergunta onde explorar — código, Claude design, Figma ou Paper, oferecendo só o que está instalado. Depois constrói (Develop) e critica (Deliver — review que lê copy, calcula contraste, varre cada variante e pode discordar do contrato com argumento) + acessibilidade + handoff + delta pro spec. Calibra o perfil do builder, detecta produto pelo cwd, escala o esforço (pocket/full) e declara o que pulou. Aplica maturity gate (sugere /bb:discover ou /bb:spec) quando o sinal é production/will-scale. Use quando o builder disser "quero começar", "novo projeto", "criar tela em <marca>", "monta protótipo", "pesquisa antes de desenhar", "quero ver direções", "constrói a superfície", "revisa o protótipo", "handoff de design", "tenho uma ideia de interface". NÃO use pra enquadrar problema de produto (use /bb:discover) nem pra spec formal de execução (use /bb:spec).
license: MIT
metadata:
  author: Inspira
  version: 2.4.0
---

# Brisar

The design trilha in one skill — **the whole double diamond**, for designers and
non-designers alike. Get ANY builder (executive, senior, junior, content) from "I
have an idea / I need to work on X" to a reviewed artifact, calibrating depth and
vocabulary by profile.

**First diamond — understand the space before drawing in it:**

- **Research** — market bench, the design system read from source, and what the
  product actually has to show (`references/phase-research.md`).
- **Brief** — the research consolidated into a written contract, reconciled
  against the problem framing (`references/brief.md`).
- **Diverge** — distinct directions, all described at the same depth, then
  converge (`references/phase-diverge.md`).

**Then the medium**, because the brief serves any of them and only the build
changes: code, Claude design, Figma or Paper (`references/phase-medium.md`).

**Second diamond — build it and hold it to account:**

- **Develop** — build high-fidelity surfaces against the contracts
  (`references/phase-develop.md`).
- **Deliver** — design review, accessibility audit, handoff doc, and the delta
  back into the spec (`references/phase-deliver.md`).

Each stage is entered explicitly (the builder asks, a shortcut routes there, or
the previous stage's gate suggests it) — the skill never rolls from one stage to
the next silently. All user-facing text — questions, option labels, echoes,
error messages — is **PT-BR**; instruction bodies are English.

## Execution principles

1. **Every question via `AskUserQuestion`** — rationale in the plugin-root
   `references/handoff-gate.md`.
2. **Profile calibration BEFORE any content question.** Phase 0 is 1 question
   with 4 clear options. Skip only if session.yaml already has `profile`.
3. **Adapt depth and vocabulary to the profile.** Executive receives 5-6
   questions in operational language, without "scaffold/embed/MCP". Senior
   receives 2 technical questions. Junior receives 3 questions + narration of
   each step. Content goes straight to the Framer path with visual direction
   given (not asked). Persona is a path difference, not a capability ranking.
4. **Detect > ask.** Step 0 cross-references cwd with the product registry; a
   match settles brand and hosting without asking. Tooling gaps are detected in
   preflight, not asked. **Exception: the medium is always asked** — assuming it
   scaffolds a repo for someone who wanted a canvas, or opens a canvas for
   someone shipping today.
5. **Lightning intake max 3 questions.** If you find yourself preparing a
   fourth, stop — it's turning into a form. (Executive gets up to 5-6, but in
   operational language.)
6. **Maturity gate is an invitation, not a block.** An override costs one flag
   in session.yaml; blocking costs trust.
7. **Scaffold ≠ planning.** This skill WRITES real files. If Bash fails,
   surface the error — don't fake success.
8. **The research floor never scales down, and what is skipped is said.**
   Every mode runs market bench + the DS read from source + "does this need a
   new component?". Everything else is judged and **declared** in one line.
   Silent scope reduction reads as thoroughness and is the opposite.
9. **Directions get equal treatment.** A recommendation is fine; describing one
   direction in depth and the others in a sentence decides for the builder while
   pretending to offer a choice.
10. **The brief is a living contract.** Every round updates it, without being
    asked. It ends as a delta back into the spec. Where brief and spec disagree,
    **the spec wins** — the brief is the research record, the spec is the contract.
11. **Suggest, never auto-invoke.** Other skills (/bb:discover, /bb:spec,
    /bb:challenge, /bb:review) are always suggested via handoff gate.
    Internal phase transitions also go through a gate — the builder crosses them
    on purpose. The one exception inside this skill: Research flows straight into
    Brief, because the research is the brief's input and does not stand alone.
12. **The review may disagree with the contract.** With the argument, as a
    `divergência`, never as a blocker and never as a silent rewrite. Disagreeing
    is the job; deciding belongs to the owner.
13. **Never block due to missing tooling.** git missing → manual instructions.
    MCP missing → markdown handoff, or a medium that needs no MCP. There's always
    a fallback.
14. **Write for the non-designer.** Expand an internal pointer on first use, gloss
    a design concept in 5–10 words. Dense is fine; needing a decoder is not.
15. **Deliver visual direction before Develop.** The Develop phase needs
    `design/<surface>.md`; without it the builder is back to pure shaping.

---

## Step 0 — Pre-flight (silent)

Before any question, five checks — without printing anything to the user.
Everything recorded in `.brisar/session.yaml`.

### 0.1 — Is there a Brisa session in this project?

```bash
test -f .brisar/session.yaml && cat .brisar/session.yaml
test -f .brisar/config.yaml && cat .brisar/config.yaml
```

If a complete session exists (`status: completed`) and config: the project was
already scaffolded. Ask the user whether they want to (a) go straight to the
Develop phase with the context loaded, (b) regenerate the visual direction for
a new surface, or (c) start from scratch archiving the old session.

If `status: bootstrapped-to-discover`: the maturity gate fired earlier and the
builder went to /bb:discover. Look for the resulting brief (the task-state
contract, plugin-level `references/task-state.md`: `.bb/tasks/<slug>/spec.md`
carrying `## problem` / `## fit`); confirm with the builder which brief it is if
more than one matches. Record its path under `gate.discover_brief`, let the
appetite and cuts inform fidelity/scope, and resume at the **Research phase** —
intake is already filled, and the framing is exactly what the research has to
test.

**Also look for an existing design brief**, whether or not a session exists:

```bash
ls .bb/tasks/*/brief-design.md 2>/dev/null
```

A design brief on disk means the first diamond already ran — possibly in a much
earlier session, possibly by someone else. **Do not re-run it and do not rewrite
it.** Read it, record the path under `gate.design_brief`, and resume where it
left off:

| What the brief has                    | Resume at               |
| ------------------------------------- | ----------------------- |
| Research and findings, no directions  | Diverge                 |
| Directions, none marked `chosen`      | Diverge, at convergence |
| A chosen direction, nothing built     | the medium question     |
| A chosen direction and surfaces built | Deliver                 |

Say in one line what you found and where you are resuming, then continue. Re-running
research over a brief that already exists is the most expensive mistake available
here — and it destroys the record of rounds the brief was keeping.

If any other partial session exists: offer to resume. If the session has
`profile.persona_id`: skip Phase 0 (calibration).

### 0.2 — Detect Brisa DS

Heuristic in order (stop at the first one that works):

1. Variable `BRISAR_DS_PATH`.
2. `.brisar/config.yaml` field `ds_path`.
3. Bundled: `references/ds/` **in this skill's own directory** — ships with the
   plugin; contains `brand/DESIGN.md` + sub-brands + voice references.

If nothing works, record `ds_path: not-found` and continue in brand free-text
mode.

This resolves the **brand** — voice, principles, sub-brand identity. It is not the
production token source, and its bundled `brand/tokens/tokens.json` must not be
used as one; the research phase locates the real one from the repo, or remotely
via `gh` (`references/phase-research.md`, Front B).

### 0.3 — Build the brand registry

If DS found, glob `brand/DESIGN.md` (base) + `brand/*/DESIGN.md` (sub-brands).
Read the first line of each (`# {Brand} — Style Reference`) for the canonical
name. Always add `Sem marca / custom` and `Ainda não sei` as final options.

### 0.4 — Tooling preflight

Detects what's installed: git, gh + auth, MCPs (unframer, figma, etc). Details
in `references/preflight-tooling.md`. Result goes to `session.yaml` under
`preflight.tooling/mcps`.

**Critical principle:** preflight informs the path, never blocks. If git is
missing AND persona = senior later, warn and offer to resolve. If MCP unframer
is missing AND persona = content, fall back to the markdown handoff.

### 0.5 — Detect product by cwd

Reads `references/product-registry.yaml` and evaluates each product's
`detection[]` against the cwd. First match wins (registry order is priority).

When detected:

- Skip the brand question in Phase 1 (already known by `product.brand`)
- Skip the hosting question (already known: `mode_default: embed`)
- Load `repo_url`, `ds_source`, `requires_mcp` for the later flow
- Persist in `session.yaml` under `preflight.product`

If no match: record `product.detected: unknown` and continue. Phase 1 asks
brand normally.

**Important:** detection is by marker in the filesystem (file/dir/contains),
never by folder name.

---

## Navigation map (lazy load)

Each phase lives in a separate file under `references/`. **Don't load all files
in Step 0** — open only what the current phase needs.

| Phase                                                                      | When to load                                                                                                                                                | File                                                                     |
| -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Pre-flight tooling                                                         | Step 0.4                                                                                                                                                    | `references/preflight-tooling.md`                                        |
| Product registry                                                           | Step 0.5 + Phase 1                                                                                                                                          | `references/product-registry.yaml`                                       |
| **Phase 0 — Profile calibration**                                          | After Step 0, BEFORE Phase 1. Skip if session already has profile.                                                                                          | `references/phase-0-calibration.md`                                      |
| Phase 1 — Lightning intake                                                 | After Phase 0. Depth adapts to persona_id.                                                                                                                  | `references/phase-1-intake.md`                                           |
| Phase 2 — Maturity gate                                                    | After Phase 1, EXCEPT: persona = executive/content, OR `brand.workflow == framer-harpa`                                                                     | `references/phase-2-gate.md`                                             |
| **Research — the first diamond**                                           | After Phase 2, before anything is drawn. Skip only for a trivial mechanical change.                                                                         | `references/phase-research.md`                                           |
| **Brief — the design contract**                                            | Straight after Research (no gate between them) and again on **every later round** that changes a decision                                                   | `references/brief.md`                                                    |
| **Diverge — directions in equal standing**                                 | After the Brief gate, when the builder chooses to diverge                                                                                                   | `references/phase-diverge.md`                                            |
| **Medium — where to explore**                                              | After Diverge, before Phase 3. Also when Develop is reached by shortcut with no `medium` recorded.                                                          | `references/phase-medium.md`                                             |
| Phase 3 — Scaffold (real files)                                            | After the medium question, and **only** when `medium.chosen == código`. Variant by persona: senior/junior = normal scaffold; executive = `prototype-hosted` | `references/phase-3-scaffold.md`                                         |
| Phase 4 — Design direction                                                 | After Phase 3. **Skip when a design brief already carries the chosen direction** — it is the richer form of the same thing                                  | `references/phase-4-design-direction.md`                                 |
| **Phase Framer-handoff** (replaces Phase 2+3+4 on the Framer/content path) | When `brand.workflow == framer-harpa` OR `persona_id == content`                                                                                            | `references/phase-framer-handoff.md`                                     |
| Phase 5 — Terminal report                                                  | Always, last phase of the direction stage.                                                                                                                  | `references/phase-5-handoff.md`                                          |
| **Develop** — hi-fi surface construction                                   | Builder asks to build, a shortcut routes here, or the Phase 5 gate chose it                                                                                 | `references/phase-develop.md` (+ `references/develop-modes.md` per mode) |
| **Deliver** — review, accessibility, handoff                               | Builder asks to review/hand off, a shortcut routes here, or the Develop gate chose it                                                                       | `references/phase-deliver.md` (+ `references/deliver-modes.md` per mode) |
| Schemas (`.brisar/session.yaml`, `.brisar/config.yaml`)                    | When you need to read/write state                                                                                                                           | `references/persistence.md`                                              |

---

## Cooperation contract — who produces, who consumes

| Artifact                                                                  | Produced by                                                                | Consumed by                                                                      |
| ------------------------------------------------------------------------- | -------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| `.brisar/session.yaml`                                                    | every phase — each writes its own section                                  | all phases (each reads the whole YAML in its Step 0), re-runs                    |
| **`.bb/tasks/<slug>/brief-design.md`**                                    | **Brief** — and updated by every later round, including Deliver            | Diverge, Develop, Deliver, the implementing dev, later rounds                    |
| `.brisar/config.yaml`                                                     | Phase 3 (medium `código` only)                                             | Develop (tokens.md/components.md path), future invocations                       |
| `<slug>/design-context/tokens.md` + `components.md`                       | Phase 3 (medium `código` only)                                             | Develop (Step 0). On canvas mediums the DS values come from the Research instead |
| `<slug>/design/<surface>.md`                                              | Phase 4                                                                    | builder, Develop — superseded by the design brief when one exists                |
| `<slug>/...` (vite, package.json, src/)                                   | Phase 3                                                                    | builder (`pnpm install && pnpm dev`), Develop                                    |
| `<slug>/HANDOFF-DEV.md`                                                   | Phase 3 (persona = executive)                                              | dev who picks up the prototype later                                             |
| `.brisar/tarsila/notes.md`                                                | Develop (optional decisions log)                                           | Deliver, builder                                                                 |
| `.brisar/clarisse/*.md` (design-review, accessibility-checklist, handoff) | Deliver                                                                    | builder, implementing dev                                                        |
| `.bb/tasks/<slug>/spec.md`                                                | /bb:discover, /bb:spec (outside this skill); **delta proposed by Deliver** | Step 0.1 (bootstrap return), Research, Brief, Diverge, Develop, Deliver          |
| `harpa-handoff-<slug>-<date>.md` (in cwd)                                 | Framer/content path                                                        | builder inside `harpa-lpbuilder/`                                                |

Each phase reads the whole session.yaml in Step 0 and writes **only its
section** at the end — cross-awareness without coupling.

### Framer path (Site Institucional / content persona)

When the builder chooses "Site institucional (Framer)" on Question 2 OR
`persona_id == content` in Phase 0, brisar forks: **does not scaffold**, **does
not create the `<slug>/` folder**, **does not generate design-context/**.
Instead, it generates `harpa-handoff-<slug>-<date>.md` in the cwd with intent +
visual direction in Framer idiom + instructions to open Claude Code inside
`harpa-lpbuilder/`.

**Variant when MCP unframer is missing:** generate the markdown handoff anyway,
without MCP — the dev/designer takes it to Framer manually. The Develop phase
is not used on this path. Details in `references/phase-framer-handoff.md`.

### Bootstrap protocol (brisar → /bb:discover → brisar)

When the maturity gate fires and the builder accepts shaping first, brisar
writes `.brisar/session.yaml` with:

- `status: bootstrapped-to-discover`
- `intent`, `brand`, `artifact` already filled from the lightning intake
- `gate.resolution: bootstrap-to-discover`

…then suggests running `/bb:discover <ideia>` and stops (never auto-invokes).
/bb:discover keeps its own state in `.bb/tasks/<slug>/spec.md`. When the
builder returns and runs `/bb:brisar` again, Step 0.1 detects the bootstrap
status, locates the discover brief, records it under `gate.discover_brief`, and
resumes at the **Research phase** with the framing carried over.

### The two briefs — they coexist, neither replaces the other

Two slots in `session.yaml`, two different questions, and later phases read both:

| Slot                  | File                                                                         | Answers                                              | Written by                 |
| --------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------- | -------------------------- |
| `gate.discover_brief` | `.bb/tasks/<slug>/spec.md` (`## problem`/`## hypothesis`/`## fit`/`## cuts`) | Is it worth building, for whom, and what did we cut? | `/bb:discover`, `/bb:spec` |
| `gate.design_brief`   | `.bb/tasks/<slug>/brief-design.md`                                           | How should this surface be, and why?                 | the Brief phase here       |

**Never substitute one for the other.** Reviewing against the research alone loses the
problem; reviewing against the hypothesis alone loses everything the research learned.
The Brief phase reconciles the two when it closes, and Deliver reconciles them again
against the built thing — the artifact that did not exist the first time.

### Critical path rule

`.brisar/config.yaml` is where the design-context path is registered. Phase 3
decides the path (default: `<slug>/design-context/`); Develop reads it from the
config — no hardcoded string on either side.

**On canvas mediums there is no config and no design-context**, by design
(`medium.scaffold: skipped`). The DS values come from the Research phase, which read
the same source one step earlier. Absent config on those paths is the normal state, not
a failure to report.

---

## Full flow

```
Step 0: Pre-flight (silent)
  0.1 → detect existing session (incl. bootstrap return → Research)
  0.2 → detect Brisa DS (bundled at references/ds/)
  0.3 → build brand registry (from the DS)
  0.4 → tooling preflight (git, gh, MCPs — incl. paper/figma/pencil/mobbin, both scopes)
  0.5 → detect product by cwd (product-registry.yaml)

Phase 0 — Profile calibration (1 question)
  → executive | builder-senior | builder-junior | content

Phase 1 — Lightning intake (max 3 questions, depth by persona)
  → shortcut router may jump straight to Develop, Deliver, or /bb:discover
  → content: skips straight to Phase Framer

Phase 2 — Maturity gate (senior/junior only)
  → production/will-scale → suggest /bb:discover or /bb:spec (bootstrap protocol)

╭─ FIRST DIAMOND ─────────────────────────────────────────────────────────────╮
│ Research — pesquisa antes do pixel                                          │
│   → declare the mode (pocket|full): what runs, what was skipped, why,       │
│     and what any degraded front invalidates                                 │
│   → floor, always: bench · DS read from source · new component?             │
│     no Mobbin → galleries/prints (login wall) · no repo → gh remote read    │
│   → discretionary: biases w/ provenance · heuristics · mental models ·      │
│     what the product has to show                                            │
│   → fan-out in parallel subagents; only the distillate returns              │
│   → NO GATE — flows straight into Brief                                     │
│                                                                             │
│ Brief — o contrato de design                                                │
│   → .bb/tasks/<slug>/brief-design.md, recorded at gate.design_brief         │
│   → reconcile vs the framing: confirma · contradiz · não alcança            │
│   → close on an unresolved tension (none found = research was shallow)      │
│   → present it in chat: findings · references · directions · tension        │
│     (round ≥2 = the delta only; each block must enable a decision)          │
│   → gate: montar caminhos / resolver a contradição / encerrar               │
│                                                                             │
│ Diverge — direções em pé de igualdade                                       │
│   → declare the base common to all directions first                         │
│   → ≥2 directions, each with all 5 parts (aposta·composição·copy·           │
│     racional·risco); equal-treatment check BLOCKS the gate                  │
│   → converge: chosen + runner-up + discarded + pivot condition              │
│   → recommendation MANDATORY for executive/content personas                 │
│   → gate: construir / trocar caminho / buscar mais / encerrar               │
╰─────────────────────────────────────────────────────────────────────────────╯

Medium — onde explorar (1 question, offers only what's detected)
  → código | claude design | paper | figma | pencil
  → canvas mediums set scaffold: skipped

Phase 3 — Scaffold OR prototype-hosted     [medium == código only]
  → senior + detected product = embed (clone via gh)
  → senior/junior + greenfield = local Vite scaffold
  → executive = prototype-hosted (folder + HANDOFF-DEV.md, no local npm install)

Phase 4 — Design direction                 [skipped when the brief carries it]
  → <slug>/design/<surface>.md per surface (max 5)

Phase Framer (replaces Phase 2-4 on the Framer/content path)
  → harpa-handoff-<slug>-<date>.md, with or without MCP unframer

Phase 5 — Terminal report + gate
  → report what was created, per persona
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
│   → severity: blocker · significant · DIVERGÊNCIA · minor                   │
│   → accessibility + handoff doc + DELTA back into the spec                  │
│   → gate: decidir divergências / construir em código / /bb:review (a11y)    │
│     / /bb:spec / encerrar                                                   │
╰─────────────────────────────────────────────────────────────────────────────╯
```

Two sharp cautions:

**Never overwrite an existing `.brisar/` session without asking** — archive it
(`.brisar/session.archived-<ISO>.yaml`) before restarting.

**Changing medium does not reopen the first diamond.** Explore on a canvas, then build
in code, is the normal path — the research, brief and chosen direction are already
settled. Say so out loud when it happens, so nobody expects a fresh interview.
