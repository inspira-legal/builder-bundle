---
name: brisar
description: Trilha de design ponta a ponta — do "tenho uma ideia" ao protótipo revisado. Calibra o perfil do builder (executive/senior/junior/content), detecta produto pelo cwd, e roteia pro artefato certo — scaffold Vite com o DS Brisa, embed em codebase existente, protótipo hosted (sem código local) ou handoff Framer. Depois da direção visual, segue internamente pras fases Develop (constrói telas hi-fi a partir do design-context) e Deliver (design review + acessibilidade + handoff doc). Aplica maturity gate (sugere /bb:discover ou /bb:spec) quando o sinal é production/will-scale. Use quando o builder disser "quero começar", "novo projeto", "criar tela em <marca>", "monta protótipo", "constrói a superfície", "revisa o protótipo", "handoff de design", "tenho uma ideia de interface". NÃO use pra enquadrar problema de produto (use /bb:discover) nem pra spec formal de execução (use /bb:spec).
license: MIT
metadata:
  author: Inspira
  version: 2.0.0
---

# Brisar

The design trilha in one skill — **briefing + dispatcher + builder**. Get ANY
builder (executive, senior, junior, content) from "I have an idea / I need to
work on X" to the right artifact (prototype, embed into codebase, scaffold, or
Framer handoff) in the fewest possible turns — calibrating depth and vocabulary
by profile — and then carry the work through two internal stages:

- **Develop** — build high-fidelity surfaces against the design-context
  contracts (`references/phase-develop.md`).
- **Deliver** — design review, accessibility audit, and handoff doc
  (`references/phase-deliver.md`).

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
   preflight, not asked.
5. **Lightning intake max 3 questions.** If you find yourself preparing a
   fourth, stop — it's turning into a form. (Executive gets up to 5-6, but in
   operational language.)
6. **Maturity gate is an invitation, not a block.** An override costs one flag
   in session.yaml; blocking costs trust.
7. **Scaffold ≠ planning.** This skill WRITES real files. If Bash fails,
   surface the error — don't fake success.
8. **Deliver visual direction before Develop.** The Develop phase needs
   `design/<surface>.md`; without it the builder is back to guessing the screen.
9. **Suggest, never auto-invoke.** Other skills (/bb:discover, /bb:spec,
   /bb:challenge, /bb:review) are always suggested via handoff gate.
   Internal phase transitions (→ Develop, → Deliver) also go through a gate —
   the builder crosses them on purpose.
10. **Never block due to missing tooling.** git missing → manual instructions.
    MCP missing → markdown handoff. There's always a fallback.

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
appetite and cuts inform fidelity/scope, and resume at Phase 3 (scaffold) —
intake is already filled.

If any other partial session exists: offer to resume. If the session has
`profile.persona_id`: skip Phase 0 (calibration).

### 0.2 — Detect Brisa DS

Heuristic in order (stop at the first one that works):

1. Variable `BRISAR_DS_PATH`.
2. `.brisar/config.yaml` field `ds_path`.
3. Bundled: `references/ds/` **in this skill's own directory** — ships with the
   plugin; contains `brand/DESIGN.md` + sub-brands + tokens + voice references.

If nothing works, record `ds_path: not-found` and continue in brand free-text
mode.

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

| Phase                                                                      | When to load                                                                                       | File                                                                     |
| -------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| Pre-flight tooling                                                         | Step 0.4                                                                                           | `references/preflight-tooling.md`                                        |
| Product registry                                                           | Step 0.5 + Phase 1                                                                                 | `references/product-registry.yaml`                                       |
| **Phase 0 — Profile calibration**                                          | After Step 0, BEFORE Phase 1. Skip if session already has profile.                                 | `references/phase-0-calibration.md`                                      |
| Phase 1 — Lightning intake                                                 | After Phase 0. Depth adapts to persona_id.                                                         | `references/phase-1-intake.md`                                           |
| Phase 2 — Maturity gate                                                    | After Phase 1, EXCEPT: persona = executive/content, OR `brand.workflow == framer-harpa`            | `references/phase-2-gate.md`                                             |
| Phase 3 — Scaffold (real files)                                            | After Phase 2. Variant by persona: senior/junior = normal scaffold; executive = `prototype-hosted` | `references/phase-3-scaffold.md`                                         |
| Phase 4 — Design direction                                                 | After Phase 3                                                                                      | `references/phase-4-design-direction.md`                                 |
| **Phase Framer-handoff** (replaces Phase 2+3+4 on the Framer/content path) | When `brand.workflow == framer-harpa` OR `persona_id == content`                                   | `references/phase-framer-handoff.md`                                     |
| Phase 5 — Terminal report                                                  | Always, last phase of the direction stage.                                                         | `references/phase-5-handoff.md`                                          |
| **Develop** — hi-fi surface construction                                   | Builder asks to build, a shortcut routes here, or the Phase 5 gate chose it                        | `references/phase-develop.md` (+ `references/develop-modes.md` per mode) |
| **Deliver** — review, accessibility, handoff                               | Builder asks to review/hand off, a shortcut routes here, or the Develop gate chose it              | `references/phase-deliver.md` (+ `references/deliver-modes.md` per mode) |
| Schemas (`.brisar/session.yaml`, `.brisar/config.yaml`)                    | When you need to read/write state                                                                  | `references/persistence.md`                                              |

---

## Cooperation contract — who produces, who consumes

| Artifact                                                                  | Produced by                                                            | Consumed by                                                   |
| ------------------------------------------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------------------- |
| `.brisar/session.yaml`                                                    | direction phases (0-5), Develop, Deliver — each writes its own section | all phases (each reads the whole YAML in its Step 0), re-runs |
| `.brisar/config.yaml`                                                     | Phase 3                                                                | Develop (tokens.md/components.md path), future invocations    |
| `<slug>/design-context/tokens.md` + `components.md`                       | Phase 3                                                                | Develop (Step 0)                                              |
| `<slug>/design/<surface>.md`                                              | Phase 4                                                                | builder, Develop                                              |
| `<slug>/...` (vite, package.json, src/)                                   | Phase 3                                                                | builder (`pnpm install && pnpm dev`), Develop                 |
| `<slug>/HANDOFF-DEV.md`                                                   | Phase 3 (persona = executive)                                          | dev who picks up the prototype later                          |
| `.brisar/tarsila/notes.md`                                                | Develop (optional decisions log)                                       | Deliver, builder                                              |
| `.brisar/clarisse/*.md` (design-review, accessibility-checklist, handoff) | Deliver                                                                | builder, implementing dev                                     |
| `.bb/tasks/<slug>/spec.md`                                                | /bb:discover, /bb:spec (outside this skill)                            | Step 0.1 (bootstrap return), Phase 3                          |
| `harpa-handoff-<slug>-<date>.md` (in cwd)                                 | Framer/content path                                                    | builder inside `harpa-lpbuilder/`                             |

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

When the maturity gate fires and the builder accepts framing the problem first, brisar
writes `.brisar/session.yaml` with:

- `status: bootstrapped-to-discover`
- `intent`, `brand`, `artifact` already filled from the lightning intake
- `gate.resolution: bootstrap-to-discover`

…then suggests running `/bb:discover <ideia>` and stops (never auto-invokes).
/bb:discover keeps its own state in `.bb/tasks/<slug>/spec.md`. When the
builder returns and runs `/bb:brisar` again, Step 0.1 detects the bootstrap
status, locates the discover brief, records it under `gate.discover_brief`, and
jumps straight to Phase 3 (scaffold) with the framing carried over.

### Critical path rule

`.brisar/config.yaml` is where the design-context path is registered. Phase 3
decides the path (default: `<slug>/design-context/`); Develop reads it from the
config — no hardcoded string on either side.

---

## Full flow

```
Step 0: Pre-flight (silent)
  0.1 → detect existing session (incl. bootstrap return → Phase 3)
  0.2 → detect Brisa DS (bundled at references/ds/)
  0.3 → build brand registry (from the DS)
  0.4 → tooling preflight (git, gh, MCPs)
  0.5 → detect product by cwd (product-registry.yaml)

Phase 0 — Profile calibration (1 question)
  → executive | builder-senior | builder-junior | content

Phase 1 — Lightning intake (max 3 questions, depth by persona)
  → shortcut router may jump straight to Develop, Deliver, or /bb:discover
  → content: skips straight to Phase Framer

Phase 2 — Maturity gate (senior/junior only)
  → production/will-scale → suggest /bb:discover or /bb:spec (bootstrap protocol)

Phase 3 — Scaffold OR prototype-hosted
  → senior + detected product = embed (clone via gh)
  → senior/junior + greenfield = local Vite scaffold
  → executive = prototype-hosted (folder + HANDOFF-DEV.md, no local npm install)

Phase 4 — Design direction
  → <slug>/design/<surface>.md per surface (max 5)

Phase Framer (replaces Phase 2-4 on the Framer/content path)
  → harpa-handoff-<slug>-<date>.md, with or without MCP unframer

Phase 5 — Terminal report + gate
  → report what was created, per persona
  → gate: continue to Develop / run /bb:discover / stop here

Develop (entered via gate, shortcut, or direct ask)
  → build hi-fi surfaces against design-context contracts
  → gate: continue to Deliver / add surface / stop here

Deliver (entered via gate, shortcut, or direct ask)
  → design review + accessibility + handoff doc
  → gate: /bb:review (auditoria de acessibilidade) / /bb:spec / encerrar
```

One sharp caution: **never overwrite an existing `.brisar/` session without
asking** — archive it (`.brisar/session.archived-<ISO>.yaml`) before restarting.
