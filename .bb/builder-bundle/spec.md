---
status: done
created: 2026-07-23
slug: builder-bundle
---

# Builder Bundle: the builder skills unified into a single plugin

Turn this repo (formerly `ofc-skills`, already renamed on GitHub to
`inspira-legal/builder-bundle`) into the **Builder Bundle**: the unified skill set for
Inspira builders, approved in the 2026-07-23 meeting. It consolidates 28 skills (ofc 15 +
the brisar bundle + loose copies from the `inspira-skills` store + inspira-code-review)
into **16 skills** organized in 6 trilhas, invoked as `/bb:<skill>`.

Today there are 4 places with overlapping skills (ofc, brisar, the store,
inspira-code-review), with duplication, broken things (codenavi) and outdated ones.
Whoever is learning does not know what to use. A single opinionated plugin, with one skill
per verb and modes for the variations, gives location ("where am I in the journey?") and
makes any future extension happen _inside_ the bundle instead of becoming one more plugin.

Success: the team installs one plugin and knows which verb to use at each point of the
journey.

## The 6 trilhas

- **Pensar**: `discover`, `challenge`, `think`, `legal-lens`
- **Desenhar**: `spec`
- **Construir**: `implement`, `ship`, `delegate`, `gather-branch-context`
- **Revisar**: `review`, `maintain-repo`, `review-setup`
- **Design**: `brisar`, `ui-accessibility`
- **Pesquisar/Doc**: `code-deep-research`, `write-readme`

## How the bundle is organized

- **Layout**: `plugins/bb/{skills/<16>/,references/,scripts/,hooks/}`. Shared references at
  the plugin level (handoff-gate.md, the quality/review checklists, the review engine);
  per-skill references inside each `skills/<name>/references/` (brisar's phases, discover's
  modes, export-spec).
- **The journey's flow** (what the gates chain): a pain or an idea → `discover` (with
  challenge, think and legal-lens as support) → _it is code_ → `spec` → `implement` →
  `ship` → `review` of the PR; _it is design_ → `brisar` → back to `spec`. `think` only
  offers a gate once it has converged; `challenge` hands back to the thesis's owner.
- **The state contract**: `.bb/tasks/<slug>/spec.md` with `status/created/slug`
  frontmatter. Documented in a single place (a shared reference) and used by **spec,
  implement and delegate** (the Cloud Routine goes through delegate, so it inherits).
- **The manifesto**: one shared reference ("consult-manifesto") included by the canonical
  list (implement, ship, review, review-setup). It fetches
  `gh api repos/inspira-legal/manifesto/...`, applies the
  Obrigatório/Padrão/Alternativa/Proibido levels, and falls back with a warning.

## Decisions

- **The invocation prefix is `bb`** (`/bb:spec`, `/bb:brisar`). The plugin name in
  `plugin.json` is `bb`; the dir `plugins/ofc` becomes `plugins/bb`; the marketplace stays
  `inspira-legal`; the version is **2.0.0**. `marketplace.json` starts listing **only
  `bb`**, and the `ofc` entry is removed (an intentional major break; whoever has ofc
  installed migrates through the CHANGELOG note, with no double transition entry).
- **State on disk: `.bb/tasks/<slug>/spec.md`**, one path, no legacy fallback. Old briefs
  are migrated by hand (documented in the CHANGELOG).
- **Hybrid language**: instruction bodies in English (the ofc standard, the base of the
  method); descriptions, triggers and every text the user sees (gate questions, reports) in
  PT-BR.
- **The manifesto at runtime**: `implement`, `ship`, `review` and `review-setup` (the
  canonical list; `delegate` inherits through implement→ship) consult
  `inspira-legal/manifesto` through `gh api` when they need to decide the stack. A graceful
  fallback: without access, follow the current repo's patterns and **say** the manifesto
  was not consulted.
- **6 fusions** (the general conflict rule: ofc's method wins, and the content of the other
  sources becomes a reference):
  1. `discover` ← frame-problem + assess-fit (ofc) + nise + esperanca (brisar). The whole
     first diamond. The output contract: it writes the upstream sections
     (`## problem`/`## hypothesis`/`## fit`/`## cuts`) into `.bb/tasks/<slug>/spec.md`,
     which `spec` reads as the intent.
  2. `think` ← think (store) + answer-yourself (ofc). A named exception to the general
     rule: the base of the method is the store's think (a reasoning partner), and
     answer-yourself comes in as the "take" mode (a direct verdict when a judgment is
     asked for).
  3. `review` ← review-changes + tidy + tidy-pr (ofc) + pr-review (store) + fix-ci (store,
     `skills/github-management/fix-ci`). 3 sources: the diff + the PR's threads + CI; it
     reads `CODE_REVIEW_GUIDE.md`; **interactive mode**: it reports, asks what to apply,
     applies the chosen fixes, replies to and resolves threads, and re-reports.
  4. `spec` ← shape (ofc) + spec (store). shape's method (the behavior map, the adversarial
     reviewer, the 3-way gate); spec's name; the original spec's export format becomes
     `references/export-spec.md`.
  5. `brisar` ← brisar + tarsila + clarisse (the Develop/Deliver phases internal, through
     references; nise and esperanca went to discover). It keeps the brand's
     `references/ds/`.
  6. `review-setup` ← code-review-setup + code-review-update (inspira-code-review). The
     output is only the `CODE_REVIEW_GUIDE.md` guide, and it **no longer** generates a
     custom per-repo skill.
- **2 renames**: desafio → `challenge`; shape → `spec`.
- **Progressive disclosure is mandatory in a fused skill**: a lean SKILL.md that routes;
  the material of each phase/mode in `references/`, loaded only when the phase runs.
- **The handoff gate**: every skill with a natural next step ends with an
  `AskUserQuestion` offering the next one; "stop here" is always an option; it **suggests,
  never auto-invokes** (the single exception: `delegate`, and the implement→ship auto-chain
  when ship was already authorized). One format, in `references/handoff-gate.md`. Without a
  gate: legal-lens, maintain-repo, review-setup, write-readme, code-deep-research,
  gather-branch-context, ui-accessibility.
- **A review engine shared** between `ship` and `review` in `references/` + `scripts/` (2
  passes, a severity scale, CI/threads). The roles are distinct (automatic ship lands,
  interactive review reports), and the engine is single to avoid drift. The existing
  scripts (`fetch_comments.py`, `reply_resolve_thread.py`, `gather_context.py`) are reused.
- **Reuse**: the ofc skills that come through almost intact, implement, ship, delegate,
  gather-branch-context, legal-lens, maintain-repo, code-deep-research and write-readme
  (the adjustments: the `.bb/` paths, the shape→spec references, the manifesto, the gates,
  the bb identity). ofc's hooks (the SessionStart operating context and the rest) are kept
  with updated texts.
- **Import sources**: the local `inspira-skills` repo at
  `C:\Users\PC\development\inspira-skills` (`skills/brisar/*`, skills/desafio, skills/think,
  skills/spec, skills/pr-review, skills/ui-accessibility, `skills/inspira-code-review/*`,
  skills/github-management/fix-ci).
- **Validation only through CI/PR** (`gh pr checks --watch`), never running checks locally.
  The existing lefthook/bun setup is kept.
- **The migration is documented**: the README + CHANGELOG carry the ofc→bb note (uninstall
  `ofc@inspira-legal`, install `bb@inspira-legal`; GitHub redirects the repo's old name).

## Behavior

1. The team runs `claude plugin marketplace add inspira-legal/builder-bundle` and
   `claude plugin install bb@inspira-legal` → it installs, and `/bb:` lists the 16 skills.
2. `/bb:discover` runs the first diamond (frame + fit, with the nise/esperanca material per
   phase) → the gate offers spec / brisar / challenge / stop here.
3. `/bb:spec <idea>` runs the method, writes `.bb/tasks/<slug>/spec.md`, and its 3-way gate
   offers implement/delegate/stop.
4. `/bb:implement` reads the brief, builds slice by slice, and offers ship.
5. `/bb:ship` runs the quality pass (the shared engine), greens the gate, lands, and
   watches CI and the threads; it never merges.
6. `/bb:review <PR|branch>` joins the diff + the threads + CI + `CODE_REVIEW_GUIDE.md`,
   reports, and asks what to apply.
7. `/bb:brisar` routes the Develop (tarsila) / Deliver (clarisse) phases, loading that
   phase's reference; on delivery, the gate offers ui-accessibility / spec.
8. `implement`/`ship`/`review`/`review-setup` consult the manifesto at runtime for stack
   decisions.

| WHEN                                            | THEN                                                                           |
| ----------------------------------------------- | ------------------------------------------------------------------------------ |
| there are only briefs on the old path           | `/bb:delegate` finds nothing; the manual migration is in the CHANGELOG         |
| the manifesto is unreachable (offline, no `gh`) | it follows the current repo's patterns and says it did not consult             |
| the user answers "stop here" at a gate          | nothing is auto-invoked                                                        |
| `/bb:review` runs on a branch with no PR        | it works with the diff source only, and reports that                           |
| `CODE_REVIEW_GUIDE.md` does not exist           | review runs generic and suggests `/bb:review-setup`; if it exists, it updates  |
| the repo has the old setup's custom skill       | it keeps working in isolation; the migration note recommends removing it       |
| delegate runs under `BB_UNATTENDED`             | it never merges (capability scoping) and the implement→ship auto-chain applies |
| the user tries `/ofc:<skill>` after migrating   | it does not exist; README/CHANGELOG carry the full mapping (15 ofc → bb)       |
| a fused skill runs one phase                    | only that phase's reference is loaded                                          |
| bb is installed without uninstalling ofc        | the two coexist, but the hooks inject the context twice                        |
| whoever has ofc runs `claude plugin update`     | it fails, because the marketplace lists only `bb`; expected in 2.0.0           |

## Tasks

- [x] **1. Scaffold**: `plugins/ofc`→`plugins/bb`, plugin.json (name bb, 2.0.0, PT-BR
      description), marketplace.json with `bb` only, the root README, the hooks with
      updated texts, the `BB_UNATTENDED` env var → behavior 1 · dep: — · verify: CI
- [x] **2. Shared conventions**: `references/handoff-gate.md`, the `.bb/` state contract,
      consult-manifesto, the progressive disclosure guideline
      → behaviors 2, 7 · dep: 1 · verify: CI
- [x] **3. The Desenhar trilha**: `spec` (shape renamed + `references/export-spec.md` +
      writing into `.bb/`) → behavior 3 · dep: 2 · verify: CI
- [x] **4. The Construir trilha**: `implement`, `delegate`, `ship`,
      `gather-branch-context`, with the paths/identity/manifesto/gates
      → behaviors 4, 5, 8 · dep: 2 · verify: CI
- [x] **5. The Revisar trilha**: `review` (fused, 3 sources, interactive), `review-setup`
      (fused, guide only), `maintain-repo`; the shared engine extracted
      → behaviors 5, 6 · dep: 2 · verify: CI
- [x] **6. The Pensar trilha**: `discover` (4 sources fused), `challenge`, `think`
      (answer-yourself fused), `legal-lens` → behavior 2 · dep: 2 · verify: CI
- [x] **7. The Design trilha**: `brisar` (tarsila/clarisse as phases, keeping
      `references/ds/`), `ui-accessibility` → behavior 7 · dep: 2 · verify: CI
- [x] **8. Pesquisar/Doc + the final docs**: `code-deep-research`, `write-readme`; the
      CHANGELOG + the ofc→bb migration note with the 28→16 mapping
      → behavior 1 · dep: 3-7 · verify: CI
- [x] **9. A single PR**: branch → PR → green CI; the content of the fusions validated
      against `analise-skills-ofc-brisar.md` and `mapa-casos-de-uso-skills.md`
      → behaviors 1-8 · dep: 8 · verify: green CI

## Out of scope

- Unpublishing or deprecating the copies in the `inspira-skills` store (spec, think,
  desafio, pr-review, ui-accessibility, the brisar bundle, inspira-code-review,
  tlc-spec-driven, codenavi), _revisit_: a separate PR in the inspira-skills repo once bb
  is published.
- A task manager / a shared backlog / session log→git, _revisit_ (v2).
- The OKF organizational memory (elephant), _revisit_ (a sibling plugin).
- The Mobbin MCP as a brisar mode, _revisit_ (Matheus is exploring it).
- The design system / the monorepo, a separate forum of Léo's.
- Org-level distribution (an admin installs for everyone), to be decided later; v1 goes
  through the marketplace.

## Open

- The "BB" acronym and branding in the README (Léo wants to explore it), which does not
  block, because the plugin's name is already `bb`.
- Org-level distribution, to be decided outside this work.
