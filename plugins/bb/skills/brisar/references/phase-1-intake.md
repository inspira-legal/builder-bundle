# Phase 1: lightning intake (depth adapts to persona_id)

The previous version asked 6-10 questions just to reach "now I'll frame it." This phase cuts that, but the number and language of the questions vary by the `profile.persona_id` captured in Phase 0. When the trade-off of skipping the framing isn't worth it (serious artifact, persona = senior/junior), Phase 2 (maturity gate) pulls /bb:discover into the flow.

## Step 0a: shortcut router (pre-persona)

Before branching by persona, brisar checks whether the builder mentioned **specific intent for a later stage of the trilha**. When there's a clear signal, it shortens the pipeline: jumps to the right phase (or suggests /bb:discover) instead of running the full intake + scaffold.

It reads `intent.raw_prompt` (what the builder typed) + `preflight.product.detected` + the presence of `.brisar/session.yaml` in the cwd.

### Shortcut matrix

| Signal in raw_prompt                                                                                                                       | Cwd                                                 | Shortcut          | Target                   | What brisar does                                                                                                                         |
| ------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------- | ----------------- | ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------- |
| "one screen", "design only", "quick prototype", "design X", "build screen Y"                                                               | already-scaffolded repo (has `.brisar/config.yaml`) | `develop-direct`  | Develop phase (internal) | Skips intake. Writes `intent.shortcut: develop-direct` to session.yaml. After confirmation, jumps to `references/phase-develop.md`.      |
| "review this design", "I need docs for the dev", "before merging", "close the deliver", "prepare the PR"                                   | repo with surfaces in `src/` or `<surface>.html`    | `deliver-direct`  | Deliver phase (internal) | Skips intake. Writes `intent.shortcut: deliver-direct`. After confirmation, jumps to `references/phase-deliver.md`.                      |
| "shape it", "mature the problem", "is it worth it", "validate the market", "is there demand", "I need to cut scope", "prioritize features" | any                                                 | `discover-direct` | `/bb:discover`           | Skips intake. Writes `intent.shortcut: discover-direct`. Suggests `/bb:discover` (it runs its own intake) and STOPS, never auto-invokes. |
| "I want to start", "new project", "scaffold it", "screen X in brand Y" (default)                                                           | any                                                 | none              | (follows normal flow)    | Persona branch below.                                                                                                                    |

### When the shortcut fires

1. Print a short confirmation, example for `develop-direct`:

   > **/bb:brisar**: I detected you want to build straight away. I'll skip the intake and go into the Develop phase. Confirm?

2. `AskUserQuestion` requesting confirmation:

   ```json
   {
     "questions": [
       {
         "question": "Shortcut detected: <target>. Skip the intake?",
         "header": "Shortcut",
         "options": [
           {
             "label": "Yes, skip to <target>",
             "description": "The target phase or skill runs its own intake. It pulls context directly."
           },
           {
             "label": "No, full flow",
             "description": "Runs the normal intake (calibration + 3 questions + scaffold)."
           }
         ],
         "multiSelect": false
       }
     ]
   }
   ```

3. If "Yes" → writes `intent.shortcut` and a minimal session.yaml. For `develop-direct`/`deliver-direct`, load the target phase file and continue there. For `discover-direct`, suggest `/bb:discover <idea>` and STOP.
4. If "No" → continues normally to Step 0b (persona branch).

### Why confirmation is mandatory

A heuristic-detected shortcut may be wrong. Asking for confirmation costs 1 turn and avoids skipping context the builder wanted to build (for example: "I need docs for the dev" might be part of a larger intake, not necessarily a jump to Deliver).

### When NOT to fire the shortcut (even with a signal)

- No `.brisar/config.yaml` in cwd AND signal is `develop-direct`: scaffold is a prerequisite for the Develop phase. Falls into the normal flow; the Phase 5 gate offers Develop at the end.
- Persona `executive` or `content` detected in Phase 0: skip shortcuts. These paths have operational/brand-first intake that doesn't combine well with short-circuit.

---

## Step 0b: branch by persona

Read `.brisar/session.yaml` field `profile.persona_id`. Route:

| `persona_id`     | Goes to                                                                             | How many questions                                         |
| ---------------- | ----------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| `builder-senior` | [Senior variant](#senior-variant-2-questions)                                       | 2 (intent + brand, with brand skipped if product detected) |
| `builder-junior` | [Standard flow](#question-1-what-are-you-building) below + narration                | 3                                                          |
| `executive`      | [Executive variant](#executive-variant-operational-language)                        | 5-6 in operational language                                |
| `content`        | **Does NOT enter Phase 1.** Jumps straight to `references/phase-framer-handoff.md`. | 0 (intake-Framer-variant)                                  |

If `persona_id` is missing: assumes `builder-junior` (Phase 0 fallback) and follows the standard flow.

If `preflight.product.detected != unknown`: brand, hosting, and (sometimes) artifact are already derived from the product, skip those questions regardless of persona. Use [Shortcuts with product detected](#shortcuts-with-product-detected).

---

## Senior variant (2 questions)

Senior dev, technical vocabulary OK, no narration of every `cd`. Path optimized for minimum friction.

Print a short intro:

> **/bb:brisar**: senior profile detected. 2 questions and I drop you in the editor.

### Senior question #1: intent

```json
{
  "questions": [
    {
      "question": "What are you building? One sentence.",
      "header": "Intent",
      "options": [
        {
          "label": "Free response",
          "description": "For example: 'semantic search screen in LexFlow' or 'new Chat component in the DS'"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

Derives slug + surface inference, same as the standard flow.

### Senior question #2: brand/product (CONDITIONAL)

- If `preflight.product.detected != unknown`: SKIP. Brand + hosting are already known.
- Otherwise: use the standard Question 2 (brand registry).

Question 3 (artifact/hosting/appetite) **does not run for senior** when product is detected. The product's `mode_default` defines this. Senior in greenfield (product = `greenfield-vite`) gets the standard question 3.

Short echo + proceed to Phase 2 (gate runs as usual).

---

## Junior variant (standard flow + narration)

Junior uses the 3 questions below (Question 1, 2, 3), exactly like senior in greenfield, but with **explicit narration** in each echo. Each echo needs to explain:

- What's going to happen in the next step
- How long it takes
- What file/command to look at

Example of junior echo (vs senior):

| Senior                                    | Junior                                                                                                                      |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| "Slug: `lexflow-search`. Going to brand." | "Derived slug: `lexflow-search`. I'll use it as the folder name. Next: the brand question, so I know which tokens to copy." |

When in Phase 5 (handoff), junior receives narrated instructions for each command (see `phase-5-handoff.md`).

---

## Executive variant (operational language)

Executive doesn't have technical vocabulary. **NEVER use**: scaffold, embed, MCP, repo, branch, slug, hosting, fidelity, Shaping appetite, surface. **Use**: folder, project, install, environment, page, area.

Print a short intro:

> **/bb:brisar**: I'll help you get from "idea" to "a clickable prototype you can show the team". I'll ask 5 quick questions in everyday language.

### Exec question #1: what

```json
{
  "questions": [
    {
      "question": "What do you want to build? In one sentence, the way you'd explain it to a colleague.",
      "header": "Idea",
      "options": [
        {
          "label": "Free response",
          "description": "For example: 'a platform for the department's financial management', 'a tool to track the legal team's contracts'"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

### Exec question #2: who uses it

```json
{
  "questions": [
    {
      "question": "Who is going to use this tool?",
      "header": "Users",
      "options": [
        {
          "label": "Internal team (operations, finance, HR, etc)",
          "description": "An internal tool, no external client"
        },
        {
          "label": "Inspira's in-house lawyers",
          "description": "A tool for the firm's own lawyers"
        },
        {
          "label": "An Inspira client",
          "description": "An outward-facing tool, for the end client"
        },
        {
          "label": "Mixed / not sure yet",
          "description": "More than one audience, or still being defined"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

### Exec question #3: what problem it solves

```json
{
  "questions": [
    {
      "question": "What problem does this tool solve today?",
      "header": "Problem",
      "options": [
        {
          "label": "Free response",
          "description": "In one sentence. For example: 'people lose time hunting for a contract in a folder', 'there's no visibility of the budget per area'"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

### Exec question #4: visual

```json
{
  "questions": [
    {
      "question": "How do you want it to look?",
      "header": "Visual",
      "options": [
        {
          "label": "Inspira's look (blue/black, light)",
          "description": "The parent brand. Inspira's default look"
        },
        {
          "label": "LexFlow's look (dark, dev-tool)",
          "description": "A dark visual, like a programmer's tool"
        },
        {
          "label": "Another internal brand (Stillare, etc)",
          "description": "It has its own identity, tell me which"
        },
        {
          "label": "Not sure / decide for me",
          "description": "I use Inspira as the base. You adjust it later"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

### Exec question #5: when

```json
{
  "questions": [
    {
      "question": "When do you want something ready to show?",
      "header": "Deadline",
      "options": [
        {
          "label": "This week",
          "description": "Urgent. A simple prototype will have to do"
        },
        { "label": "In ~2 weeks", "description": "A reasonable amount of time to explore" },
        { "label": "No set deadline", "description": "I want to do it properly" }
      ],
      "multiSelect": false
    }
  ]
}
```

### Exec question #6: next step (CONDITIONAL, only if answer to #1 implies a serious product)

```json
{
  "questions": [
    {
      "question": "After the prototype: is someone in engineering going to turn it into a real product?",
      "header": "Continuation",
      "options": [
        {
          "label": "Yes, I'll hand it to the technical team",
          "description": "The prototype is to validate; someone builds it afterwards"
        },
        {
          "label": "No, I only need it to show or validate",
          "description": "It can stay a demo"
        },
        { "label": "Not sure yet", "description": "Depends on the feedback I get" }
      ],
      "multiSelect": false
    }
  ]
}
```

### How to read (executive)

Map to the session.yaml schema:

- Question #1 → `intent.raw_prompt` + derived `slug`
- Question #2 → `intent.audience` (new field: `internal-team | internal-lawyers | client | mixed`)
- Question #3 → `intent.problem_statement`
- Question #4 → `brand.name` (or `deferred` if "not sure")
- Question #5 → `shaping.appetite` mapped: "this week" → `1 week`, "~2 weeks" → `2 weeks`, "no set deadline" → `undefined`
- Question #6 → `intent.scale_signal`: "yes, engineering picks it up" → `will-scale`, "no, only a demo" → `exploration`, "not sure" → `exploration`

**Always force:**

- `artifact.fidelity: prototype-hosted` (HTML variant, not local Vite)
- `artifact.hosting: prototype-hosted`
- `intent.persona: executive`

Short echo in operational language. E.g.: _"Got it, project: 'financial management platform'. For an internal team. For this week. I'll put together a clickable HTML prototype you can open in the browser and show the team. It generates a `<slug>/` folder with the files ready plus a `HANDOFF-DEV.md` the technical team uses to carry on."_

**Phase 2 (gate) does NOT run for executive.** Goes straight to Phase 3 prototype-hosted variant.

---

## Shortcuts with product detected

When `preflight.product.detected` is a known product (inspira-saas, portal-cliente, stillare, lexflow, ds-inspira), several fields are already derivable. Skip the corresponding questions:

| Field                  | Source                                    |
| ---------------------- | ----------------------------------------- |
| `brand.name`           | `product.brand`                           |
| `brand.design_md_path` | derived from `product.ds_source`          |
| `artifact.hosting`     | `embedded` (always, for detected product) |
| `mode`                 | `product.mode_default` (usually `embed`)  |

What still needs to be asked:

- **Question #1 (intent)**: always, without this there's nothing to build
- **Appetite/scale_signal**: only for senior/junior (executive on detected product is rare; if it happens, force `will-scale` and continue)

Echo when product is detected: _"I detected you're in [Stillare/LexFlow/etc]. I skipped brand and hosting, I already know them. Next: [intent question]."_

---

## Question 1: what are you building?

Print a short intro:

> **/bb:brisar**: design trilha. I'll ask 3 quick questions and in a few minutes you have a scaffolded project and a visual direction to start designing. Use "Other" for free text at any point.

Then `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "What are you building? Describe it in one sentence, I'll use it to name the project folder.",
      "header": "Project",
      "options": [
        {
          "label": "Free response",
          "description": "In one sentence, for example: 'semantic search screen for Lexflow' or 'new institutional landing page'"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

### How to read

The answer serves two purposes:

1. **Project slug**: derive in sanitized kebab-case (lowercase, ASCII, no stopwords). E.g.: "semantic search screen for Lexflow" → `lexflow-semantic-search`. E.g.: "new institutional landing page" → `institutional-landing`. Cap at 50 characters.
2. **Surface inference (provisional)**: suggest main surfaces. E.g.: "search" → `[search, results, empty]`. "landing" → `[hero, benefits, cta]`. Will be confirmed/adjusted in Phase 4.

If the phrase is vague ("an app", "something new"), ask ONCE for specificity: _"Can you be more concrete? For example: 'a filter panel for lawyers', 'a brief editor', 'an onboarding screen'."_ If still vague, accept with `intent.confidence: low` and continue.

Short echo: _"Got it, slug: `<slug>`. Going to brand."_

## Question 2: brand

Use the registry built in Step 0.3. Construct the options dynamically:

**Always inject `Institutional site (Framer)` as a fixed option, before "No brand / custom"**: it's a different surface (Framer + harpa-lpbuilder), not a registry brand. It's a forked path, not a brand.

```json
{
  "questions": [
    {
      "question": "Which brand?",
      "header": "Brand",
      "options": [
        {
          "label": "Inspira",
          "description": "Base brand, light theme, Cornflower Blue + Rich Black"
        },
        { "label": "Lexflow", "description": "Dev-tool sub-brand: dark theme, GitHub Primer" },
        {
          "label": "Institutional site (Framer)",
          "description": "Not Vite, uses Framer + harpa-lpbuilder. I'll redirect you to that flow."
        },
        {
          "label": "No brand / custom",
          "description": "I'll create an identity of my own, white-label or a new brand"
        },
        { "label": "I do not know yet", "description": "Decide later, record it as pending" }
      ],
      "multiSelect": false
    }
  ]
}
```

### How to read

- **Institutional site (Framer)**: register `brand.name: site-institucional`, `brand.workflow: framer-harpa`, `brand.design_md_path: null`. **SKIP the entire Question 3 (the artifact/hosting/appetite question in the original format) and use the [Question 3 Framer-variant](#question-3-framer-variant-only-when-brandworkflow--framer-harpa) below.** The flow continues differently from here. Phase 2 (gate) is skipped and Phase 3 becomes `references/phase-framer-handoff.md` instead of the normal scaffold.
- **Known brand (Inspira, Lexflow, etc.)**: register `brand.name`, `brand.source: registry`, `brand.design_md_path: <path>`. Echo: _"Brand [X], I'll copy the tokens from `<path>` in the scaffold."_
- **No brand / custom**: do a follow-up:
  ```json
  {
    "questions": [
      {
        "question": "How should the identity start?",
        "header": "Custom",
        "options": [
          { "label": "Start from Inspira", "description": "Clone Inspira's tokens, I adjust later" },
          { "label": "Start from Lexflow", "description": "Clone Lexflow's tokens, I adjust later" },
          { "label": "Start from zero", "description": "Tailwind primitives only, no brand layer" },
          {
            "label": "I have external tokens",
            "description": "I'll put them in design-context by hand"
          }
        ],
        "multiSelect": false
      }
    ]
  }
  ```
  Register `brand.source: custom-from-inspira | custom-from-lexflow | from-scratch | external-tokens`. For custom-from-X, copy the tokens of the base brand but register `brand.name: custom`, `brand.design_md_path: null`.
- **Don't know yet**: register `brand: deferred`. Use Inspira as fallback in the scaffold but warn: _"I'll use Inspira as the base; once you decide, edit `<slug>/design-context/tokens.md` or run `/bb:brisar` again."_
- **Empty brand registry (DS not-found)**: fall back to free-text mode. Ask which brand, register `brand.source: free-text`, use Tailwind primitives in the scaffold.

Short echo.

## Question 3 Framer-variant (only when `brand.workflow == framer-harpa`)

When the builder chose "Institutional site (Framer)", the fidelity/hosting questions from the Vite path don't make sense (Framer is hi-fi by definition; hosting is always the existing Framer project). Replace with:

```json
{
  "questions": [
    {
      "question": "What are you building on the site? (a new page, a section in an existing page, or an edit to content already live)",
      "header": "Framer scope",
      "options": [
        {
          "label": "New page",
          "description": "Create a brand-new page in Harpa. It gets a new route"
        },
        {
          "label": "Section in an existing page",
          "description": "Add or redesign a block in a page that already exists"
        },
        {
          "label": "Edit to content already live",
          "description": "Change copy, images, or fine-tune without a structural change"
        },
        {
          "label": "I don't know the scope yet",
          "description": "I'll explore, start by sketching"
        }
      ],
      "multiSelect": false
    },
    {
      "question": "Appetite + priority",
      "header": "Appetite",
      "options": [
        { "label": "Today: urgent", "description": "It has to go live this week" },
        { "label": "This week: normal", "description": "The standard marketing iteration" },
        {
          "label": "2 weeks, a campaign",
          "description": "A feature launch, an announcement, or a milestone"
        },
        { "label": "No deadline: exploration", "description": "A redesign study, an experiment" }
      ],
      "multiSelect": false
    }
  ]
}
```

### How to read (Framer-variant)

Capture:

- `framer.scope` ∈ `{new-page, section-in-existing, edit-existing, exploration}`
- `shaping.appetite` (mapped to "1 day" / "1 week" / "2 weeks" / "undefined")
- `artifact.fidelity: framer-canvas` (constant for this path)
- `artifact.hosting: framer-harpa` (constant)
- `intent.scale_signal: commitment` (constant. Institutional site is always production)

**Important:** `intent.scale_signal: commitment` AND the normal Phase 2 gate does not fire here. Framer + harpa-lpbuilder is already the production path, there's no scaffold to gate. Jump directly to `references/phase-framer-handoff.md`.

Short echo: _"Institutional site / Framer, scope: [X], appetite: [Y]. I'll put together the handoff for the HARPA flow."_

---

## Question 3: artifact + hosting + appetite + scale (standard variant, NON-Framer)

> Use only when `brand.workflow != framer-harpa` (Inspira, Lexflow, custom, deferred. Anything that will become a Vite scaffold).

Combined question (a single `AskUserQuestion` with 2 questions, both structured):

```json
{
  "questions": [
    {
      "question": "What do you want at the end + where is it going to live?",
      "header": "Artifact",
      "options": [
        {
          "label": "Low-fi prototype (standalone)",
          "description": "Clickable wireframe, new repo"
        },
        {
          "label": "Mid-fi prototype (standalone)",
          "description": "Visuals applied, mocked, new repo"
        },
        {
          "label": "Hi-fi prototype (standalone)",
          "description": "Final visuals, mock data, new repo"
        },
        {
          "label": "Hi-fi prototype (embedded)",
          "description": "Final visuals inside an existing app"
        },
        {
          "label": "Product live (standalone)",
          "description": "Real deploy, new repo, real data"
        },
        {
          "label": "Product live (embedded)",
          "description": "Real deploy, existing app, real data"
        },
        { "label": "Storybook only", "description": "An isolated component for review" }
      ],
      "multiSelect": false
    },
    {
      "question": "Appetite + scale intent",
      "header": "Appetite",
      "options": [
        { "label": "1 day: exploration", "description": "A lightning sprint, disposable" },
        { "label": "1 week: exploration", "description": "Small and focused, still exploration" },
        { "label": "2 weeks: exploration", "description": "Medium sized, still testing" },
        {
          "label": "2 weeks, it will scale",
          "description": "Medium sized, but the prototype becomes a product"
        },
        {
          "label": "6 weeks, commitment",
          "description": "The classic Shaping cycle, committed to the result"
        },
        { "label": "No set deadline: it will scale", "description": "Open-ended, but serious" }
      ],
      "multiSelect": false
    }
  ]
}
```

### How to read

Capture:

- `artifact.fidelity` ∈ `{low-fi, mid-fi, hi-fi, production, storybook-only}` (mapped from the 7 labels)
- `artifact.hosting` ∈ `{standalone, embedded, storybook-only}` (mapped)
- `shaping.appetite` (string)
- `intent.scale_signal` ∈ `{exploration, will-scale, commitment}`, derived from the second question

The combination `artifact.fidelity` + `intent.scale_signal` feeds Phase 2 (maturity gate). Don't cross-check here, just capture and continue.

Brief echo with the 3 pieces of data together: _"Got it, hi-fi standalone prototype, 1 week of exploration. Going to the gate."_

## State to persist

At the end of Phase 1, write a partial `.brisar/session.yaml`:

```yaml
version: 1
status: in-progress
created_at: <ISO>
current_phase: phase-2

intent:
  type: new
  confidence: high
  scale_signal: exploration # exploration | will-scale | commitment
  raw_prompt: "<what the builder typed in P1>"
  slug: "<derived slug>"

brand:
  name: Lexflow
  source: registry
  design_md_path: brand/lexflow/DESIGN.md

artifact:
  fidelity: hi-fi
  hosting: embedded

shaping:
  appetite: "1 week"

surfaces_provisional:
  - search
  - results
  - empty
```

`surfaces_provisional` is a list inferred from the prompt, not confirmed. Phase 4 will refine it. Useful for the gate to decide context.
