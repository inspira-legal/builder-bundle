# Persistence — schemas for .brisar/

Two files live in `.brisar/` in the scaffolded project: `session.yaml` (state of the /bb:brisar session and its Develop/Deliver phases) and `config.yaml` (persistent config that the Develop phase and re-runs of brisar read).

## .brisar/session.yaml — full schema

Single source shared by the whole brisar journey: intake, gate, scaffold, design direction, Develop, Deliver.

**Cross-awareness principle:** each phase reads the whole YAML in Step 0 and writes **only its section** at the end. Phases never fire silently — who decides the next step is the builder, at the gates.

Optional fields appear as `null` when not filled in.

```yaml
version: 2
brisar_version: "2.0.0"
status: in-progress | completed | bootstrapped-to-discover
current_phase: brisar-intake | develop | deliver | done

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
  discover_brief: <path or null>   # filled on the bootstrap return (Step 0.1) — points at .bb/tasks/<slug>/spec.md

# Shaping lives OUTSIDE this file: /bb:discover writes .bb/tasks/<slug>/spec.md
# (problem, fit, hypothesis, appetite, cuts). gate.discover_brief points at it.

# ============================================================
# Develop phase (high-fidelity surface construction)
# ============================================================
tarsila:
  status: null | in-progress | completed | blocked
  build_target: react+tailwind | prototype-html | storybook
  surfaces:
    - name: <surface_name>
      file: <path>
      status: built | iterated | blocked
      custom_components: [<name>]
      missing_tokens: [<token>]
      states_covered: [default, loading, empty, error]
      last_updated: <ISO>
  notes_path: ".brisar/tarsila/notes.md" | null
  next_action: ready-for-review | needs-tokens | re-prototype

# ============================================================
# Deliver phase (design review + accessibility + handoff)
# ============================================================
clarisse:
  status: null | in-progress | completed | blocked
  ran_modes: [design-review | accessibility | handoff]
  artifacts:
    design_review: ".brisar/clarisse/design-review.md" | null
    accessibility: ".brisar/clarisse/accessibility-checklist.md" | null
    handoff: ".brisar/clarisse/handoff.md" | null
  design_review:
    blockers: <N>
    significants: <N>
    fit_with_hypothesis: aligned | partial | misaligned | unknown
  accessibility:
    wcag_aa_status: pass | fail | partial | not-assessed
    mode: inline | delegated
    blockers: [<id>]
  handoff:
    completeness: high | med | low
    ci_code_review_present: bool
    surfaces_documented: <N>
  next_action: ready-to-merge | fix-blockers | re-prototype | run-/bb:review-a11y

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

The `tarsila:` and `clarisse:` section keys are kept for continuity with pre-2.0 sessions — they are the state of the **Develop** and **Deliver** phases respectively. Artifact directories stay `.brisar/tarsila/` and `.brisar/clarisse/`.

### Compatibility with pre-2.0 sessions (brisa-ds bundle)

Old sessions may carry `nise:`/`esperanca:` sections, a `shaping:` block, and statuses like `bootstrapped-from-brisar` or `deferred-to-*`. When brisar detects one, perform a soft migration:

- `nise.status: completed` (or a filled `shaping:` block) means shaping was done — treat the session as having its framing settled; if a `.bb/tasks/<slug>/spec.md` exists, point `gate.discover_brief` at it.
- `bootstrapped-from-brisar` → `bootstrapped-to-discover` (the builder now runs `/bb:discover` instead of /nise).
- `deferred-to-*` statuses → `in-progress` (the deferral targets no longer exist as separate skills; the gates re-offer the right next step).
- Leave the old `nise:`/`esperanca:` sections in place (read-only reference); write only the v2 keys.
- Bump `brisar_version: "2.0.0"`.

### Status states — who can set

| Status                     | Set by                           | Meaning                                                                                                                                                                             |
| -------------------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `in-progress`              | any phase                        | Session started, not finished. Step 0.1 offers to resume.                                                                                                                           |
| `bootstrapped-to-discover` | Phase 2 (gate accepted)          | Partial intake written; waiting for the builder to run `/bb:discover` and come back. Step 0.1 detects it, locates the brief, records `gate.discover_brief`, and resumes at Phase 3. |
| `completed`                | last phase run (usually Deliver) | Journey finished. Re-runs enter the re-entry contract.                                                                                                                              |

### Where session.yaml lives

Always at `<slug>/.brisar/session.yaml` (after the scaffold) or at `.brisar/session.yaml` in the directory where brisar was invoked (before the scaffold — during intake). The move from "before-scaffold" to "inside the slug" happens in Phase 3 — it copies, doesn't move (the original stays as reference until the next session).

In practice: Phase 3 writes `<slug>/.brisar/session.yaml` with the post-scaffold state. Partial sessions (intake / gate-bootstrap) stay in the cwd until the builder confirms the slug.

## .brisar/config.yaml — schema

This is the file the Develop phase reads to find tokens.md/components.md. More stable than session.yaml — does not change every turn.

```yaml
version: 1
brisar_version: "2.0.0"
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
# Where the context files live — the "agreed path" of the contract with Develop.
design_context_path: "<slug>/design-context/"

# Surface tracking (updated by Phase 4 and re-runs)
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
4. For a specific surface: also reads design/<surface>.md.
5. Step 0 declares: "Active context: external" (because it found tokens.md/components.md).
```

## Re-entry and idempotency

When /bb:brisar is called again in the same project:

1. Detects `.brisar/session.yaml` with `status: completed`.
2. Reads `.brisar/config.yaml` for slug, brand, design_context_path, surfaces.
3. Offers the re-entry options (see phase-5-handoff.md "When to run /bb:brisar again"):
   - Build/iterate surfaces (Develop phase)
   - Review/handoff (Deliver phase)
   - Add surface (Phase 4 only)
   - Change brand (Phase 3 partial — only design-context/ and tokens-brand.css)
   - Re-shape (suggests /bb:discover)
   - Restart (archives session, restarts)

The rule: NEVER overwrite without asking. Always archive (`.brisar/session.archived-<ISO timestamp>.yaml`) before restarting.
