# Persistence: schemas for .brisar/

Two files live in `.brisar/` in the scaffolded project: `session.yaml` (state of the /bb:brisar session and its Develop/Deliver phases) and `config.yaml` (persistent config that the Develop phase and re-runs of brisar read).

## .brisar/session.yaml: full schema

Single source shared by the whole brisar journey: intake, gate, scaffold, design direction, Develop, Deliver.

**Cross-awareness principle:** each phase reads the whole YAML in Step 0 and writes **only its section** at the end. Phases never fire silently. Who decides the next step is the builder, at the gates.

Optional fields appear as `null` when not filled in.

```yaml
version: 2
brisar_version: "2.1.0"
status: in-progress | completed | bootstrapped-to-discover
current_phase: brisar-intake | research | brief | diverge | medium | develop | deliver | done

created_at: <ISO>
completed_at: <ISO or null>

# ============================================================
# Lightning intake (entry point)
# ============================================================
intent:
  type: new | revising | exploratory
  confidence: low | med | high
  scale_signal: exploration | will-scale | commitment
  raw_prompt: "<what the builder typed in Phase 1>"
  slug: "<derived and confirmed slug>"
  shortcut: null | develop-direct | deliver-direct | discover-direct  # shortcut detected by the router

brand:
  name: Inspira | Lexflow | <another brand from the registry> | custom | deferred
  source: registry | custom-from-inspira | custom-from-lexflow | from-scratch | external-tokens | free-text | deferred
  design_md_path: "<path relative to the DS, or null>"

artifact:
  fidelity: low-fi | mid-fi | hi-fi | production | storybook-only | prototype-hosted | framer-canvas
  hosting: standalone | embedded | prototype-hosted | storybook-only | framer-harpa

profile:
  persona_id: builder-senior | builder-junior | executive | content

gate:
  fired: bool
  resolution: bootstrap-to-discover | override | not-applicable
  override_reason: <string or null>
  discover_brief: <path or null>   # filled on the bootstrap return (Step 0.1). Points at .bb/<slug>/spec.md
  design_brief: <path or null>     # filled by the Brief phase. Points at .bb/<slug>/brief-design.md

# Two briefs, two questions, and they COEXIST: neither replaces the other:
#   discover_brief → is it worth building, for whom, what did we cut?  (/bb:discover, /bb:spec)
#   design_brief   → how should this surface be, and why?              (the Brief phase here)
# Shaping lives OUTSIDE this file. Both paths point into .bb/<slug>/.

# ============================================================
# Research phase (the first diamond: before any pixel)
# ============================================================
research:
  status: null | in-progress | completed | partial | blocked
  mode: pocket | full
  ran: [bench, ds, new-component, biases, heuristics, mental-models, product-inventory]
  skipped:
    - front: <name>
      reason: <one line. Why it did not earn its cost>   # declared, never silent
  ds_source:
    path: <path actually read, or the gh coordinates>
    authority: source | remote | brand-only   # brand-only = the bundled brand package, NOT a token source
    found_via: cwd | disk-search | remote | registry | builder-told-us
    record_suggestion: <path worth adding to product-registry/.brisar config, or null>
  bench:
    via: mobbin | galleries | builder-screenshots | product-precedent | browser | web-search
    surface_access: public | behind-login   # decides which rungs of the bench ladder exist
    corpus_size: <n or null>                # null when the corpus was not systematically sampled
  degraded:
    - front: <name>
      reason: <one line. What was missing>
      invalidates: <one line, which conclusions got weaker>   # mandatory; naming the tool is not enough
  next_action: ready-for-brief

# ============================================================
# Brief phase (the design contract: updated EVERY later round)
# ============================================================
brief:
  status: null | in-progress | completed
  path: <canonical path to brief-design.md>
  round: <int>                     # increments on every update
  reconciliation:
    upstream: <path to the spec, or null>
    confirms: <n>
    contradicts: <n>               # >0 means the framing needs a decision
    unreachable: <n>
  open_tension: <one line>
  next_action: ready-for-diverge

# ============================================================
# Diverge phase (directions in equal standing)
# ============================================================
diverge:
  status: null | in-progress | completed
  count: <n>                       # >= 2
  base_declared: bool              # the block common to all directions
  directions:
    - id: <short-name>
      bet: <one line>
      is_baseline: bool            # the conventional direction, used as the comparison floor
      cost: low | fits-appetite | over-appetite
      status: chosen | runner-up | discarded
      discard_reason: <only when discarded>
  pivot_condition: <one line>
  excluded: [<idea>: <reason>]     # never went to divergence, and why
  next_action: ready-for-medium

# ============================================================
# Medium (where the exploration happens: asked, never assumed)
# ============================================================
medium:
  chosen: code | claude-design | paper | figma | pencil
  offered: [<options presented>]
  unavailable: [<medium>: <missing mcp>]   # named to the builder, not hidden
  reason: <one line. Why this one fits>
  history: [<medium per round, in order>]  # canvas-then-code is normal, not a conflict
  scaffold: required | skipped              # canvas mediums skip Phase 3
  deliver_reader: files | preview | paper-mcp | figma-mcp | pencil-mcp

# ============================================================
# Develop phase (high-fidelity surface construction)
# ============================================================
tarsila:
  status: null | in-progress | completed | blocked
  medium: code | claude-design | paper | figma | pencil
  build_target: react+tailwind | prototype-html | storybook | canvas | preview-html
  surfaces:
    - name: <surface_name>
      # Locator, Deliver opens the artifact from this. Imprecise here = unreviewable.
      file: <path>                 # medium code / claude-design
      canvas:                      # medium paper / figma / pencil
        file: <file name or id>
        page: <page name>
        artboards: [<names, one per state or variant>]
      variants: [<variant name>]   # the review unit is surface × variant
      status: built | iterated | blocked
      custom_components: [<name>]
      missing_tokens: [<token>]
      states_covered: [default, loading, empty, error]
      deviations:                  # conscious departures, judged by Deliver, not rediscovered
        - what: <one line>
          why: <one line>
      last_updated: <ISO>
  notes_path: ".brisar/tarsila/notes.md" | null
  next_action: ready-for-review | needs-tokens | re-prototype

# ============================================================
# Deliver phase (design review + accessibility + handoff)
# ============================================================
clarisse:
  status: null | in-progress | completed | blocked
  ran_modes: [design-review | accessibility | handoff]
  medium: code | claude-design | paper | figma | pencil
  reader: files | preview | paper-mcp | figma-mcp | pencil-mcp
  artifacts:
    design_review: ".brisar/clarisse/design-review.md" | null
    accessibility: ".brisar/clarisse/accessibility-checklist.md" | null
    handoff: ".brisar/clarisse/handoff.md" | null
  design_review:
    blockers: <N>
    significants: <N>
    divergences: <N>               # >0 means a contract decision needs the owner
    minors: <N>
    surfaces_swept: <N>            # surface × variant combinations actually reviewed
    variants_unreviewed: [<name>]  # unreachable ones, never silently omitted
    lenses_skipped: [<lens>: <reason>]   # e.g. contrast, when values were unreadable
    fit_with_hypothesis: aligned | partial | misaligned | unknown
    triangulation:
      built_honors_research: aligned | partial | misaligned | unknown
      research_honors_problem: aligned | partial | misaligned | unknown
      who_is_wrong: none | design | framing | both
  accessibility:
    wcag_aa_status: pass | fail | partial | not-assessed
    mode: inline | delegated
    blockers: [<id>]
  handoff:
    completeness: high | med | low
    ci_code_review_present: bool
    surfaces_documented: <N>
    spec_delta: [<what the contract has to absorb>]   # empty is a valid answer
  next_action: ready-to-merge | fix-blockers | decide-divergences | re-prototype | run-a11y-audit

# variants_unreviewed and lenses_skipped are not bookkeeping: they are the difference
# between "reviewed" and "reviewed the first artboard with the lenses that happened to work".

# ============================================================
# Surfaces tracking (Phase 4)
# ============================================================
surfaces_provisional: [<list inferred in Phase 1>]
surfaces_confirmed: [<final list in Phase 4>]

# === Feedback seeds (filled by Phase 4 / Develop) ===
ds_feedback_seeds: [<list of gaps>]

# === Audit (only filled if intent.type == revising) ===
audit:
  existing_repo: <string or null>
  framing: <string or null>

# === Deployment (filled by Deliver if fidelity == production) ===
deployment:
  github_authed: bool | null
  github_strategy: direct | local-then-promote | not-applicable
```

The `tarsila:` and `clarisse:` section keys are kept for continuity with pre-2.0 sessions. They are the state of the **Develop** and **Deliver** phases respectively. Artifact directories stay `.brisar/tarsila/` and `.brisar/clarisse/`.

### Compatibility with pre-2.0 sessions (brisa-ds bundle)

Old sessions may carry `nise:`/`esperanca:` sections, a `shaping:` block, and statuses like `bootstrapped-from-brisar` or `deferred-to-*`. When brisar detects one, perform a soft migration:

- `nise.status: completed` (or a filled `shaping:` block) means shaping was done. Treat the session as having its framing settled; if a `.bb/<slug>/spec.md` exists, point `gate.discover_brief` at it.
- `bootstrapped-from-brisar` → `bootstrapped-to-discover` (the builder now runs `/bb:discover` instead of /nise).
- `deferred-to-*` statuses → `in-progress` (the deferral targets no longer exist as separate skills; the gates re-offer the right next step).
- Leave the old `nise:`/`esperanca:` sections in place (read-only reference); write only the v2 keys.
- Bump `brisar_version: "2.1.0"`.

### Sessions written before 2.13.0

The medium token used to be recorded in Portuguese. A `session.yaml` or `config.yaml` carrying
`código` in `medium.chosen`, `medium.history`, `tarsila.medium` or `clarisse.medium` reads as
`code`; write `code` back on the next save. Same for a `divergência`/`reconciliação` key: read it
as `divergence`/`reconciliation`.

### Status states: who can set

| Status                     | Set by                           | Meaning                                                                                                                                                                                                                                         |
| -------------------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `in-progress`              | any phase                        | Session started, not finished. Step 0.1 offers to resume.                                                                                                                                                                                       |
| `bootstrapped-to-discover` | Phase 2 (gate accepted)          | Partial intake written; waiting for the builder to run `/bb:discover` and come back. Step 0.1 detects it, locates the spec, records `gate.discover_brief`, and resumes at the **Research phase**; the framing is what the research has to test. |
| `completed`                | last phase run (usually Deliver) | Journey finished. Re-runs enter the re-entry contract.                                                                                                                                                                                          |

**A design brief on disk is itself a resume signal**, session or no session. Step 0.1 globs
`.bb/*/brief-design.md` **and** `.bb/tasks/*/brief-design.md`, the layout the folder had
before; the same slug under both paths is one brief, the `.bb/<slug>/` copy is the one
read, and every round writes back to the file it read. A resumed round that grew a
second brief in the other folder lost its own history. When one exists the first diamond already ran, and brisar picks up
from how far it got (findings only → Diverge · directions with none chosen → convergence · a chosen
direction, nothing built → the medium question · surfaces built → Deliver). **Never re-run research
over an existing brief**. It is the most expensive mistake available here, and it destroys the
round history the brief was keeping.

### Where session.yaml lives

Always at `<slug>/.brisar/session.yaml` (after the scaffold) or at `.brisar/session.yaml` in the directory where brisar was invoked (before the scaffold, during intake). The move from "before-scaffold" to "inside the slug" happens in Phase 3. It copies, doesn't move (the original stays as reference until the next session).

In practice: Phase 3 writes `<slug>/.brisar/session.yaml` with the post-scaffold state. Partial sessions (intake / gate-bootstrap) stay in the cwd until the builder confirms the slug.

## .brisar/config.yaml: schema

This is the file the Develop phase reads to find tokens.md/components.md. More stable than session.yaml. Does not change every turn.

```yaml
version: 1
brisar_version: "2.1.0"
slug: "<slug>"
created_at: <ISO>

# Where the canonical DS lives (required to resolve design_md_path)
ds_path: "<absolute path or null if not-found>"

# Chosen brand
brand:
  name: "<canonical name>"
  source: "<source>"
  design_md_path: "<absolute path, or null>"

# === THIS IS THE CRITICAL FIELD FOR THE DEVELOP PHASE ===
# Where the context files live: the "agreed path" of the contract with Develop.
design_context_path: "<slug>/design-context/"

# The task folder: .bb/<slug>/, where Phase 4 writes the visual direction
# next to the spec (plugin-level references/spec-state.md). Absolute, like ds_path.
design_path: "<absolute path>"

# Surface tracking (updated by Phase 4 and re-runs). `file` is relative to
# design_path: `design.md` for a single surface, `design/<name>.md` for several.
surfaces:
  - name: busca
    file: design/busca.md
    state: drafted | in-progress | implemented
    last_updated: <ISO>
```

### How the Develop phase consumes

```
1. Develop reads .brisar/config.yaml (searches in cwd and ancestors).
2. Reads <design_context_path>/tokens.md
3. Reads <design_context_path>/components.md
4. For a specific surface: also reads <design_path>/<surfaces[].file>.
5. Step 0 declares: "Active context: external" (because it found tokens.md/components.md).
```

Readers take `file` from the config and join it to `design_path`, the single/multi
shape is decided once, in Phase 4, and never re-derived downstream.

## Re-entry and idempotency

When /bb:brisar is called again in the same project:

1. Detects `.brisar/session.yaml` with `status: completed`.
2. Reads `.brisar/config.yaml` for slug, brand, design_context_path, design_path, surfaces.
3. Offers the re-entry options (see phase-5-handoff.md "When to run /bb:brisar again"):
   - Build/iterate surfaces (Develop phase)
   - Review/handoff (Deliver phase)
   - Add surface (Phase 4 only)
   - Change brand (Phase 3 partial, only design-context/ and tokens-brand.css)
   - Re-enquadrar (suggests /bb:discover)
   - Restart (archives session, restarts)

The rule: NEVER overwrite without asking. Always archive (`.brisar/session.archived-<ISO timestamp>.yaml`) before restarting.
