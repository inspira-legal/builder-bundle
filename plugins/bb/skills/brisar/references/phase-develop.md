# Develop phase: build the prototype

Loaded when the builder chooses to build surfaces (Phase 5 gate, the `develop-direct` shortcut, or re-entry). You build a **clickable prototype** of the journey: its screens navigating between each other, each screen's states, the DS tokens applied. Mock data, no integrations, no error handling, no tests. That is not a degradation, it is what a prototype is for; the product code is `/bb:implement`'s job, written from the spec.

The discipline here is **fidelity to contracts**:

- Read the design system from the plugin: `${CLAUDE_PLUGIN_ROOT}/skills/brisar/references/ds/`, or `BRISAR_DS_PATH` when the builder set it.
- Read the surface's direction, `## Surfaces` in `.bb/<slug>/design.md`, written in Phase 4.
- Build React + Tailwind (or plain static HTML if `prototype-hosted`) into `.bb/<slug>/prototype/`, applying tokens faithfully.
- When something is not in the DS, **ask** before inventing.

## Cross-awareness with the journey

Before any question, read `.bb/<slug>/design.md` in full, and with it:

- **The spec next to it** (`.bb/<slug>/spec.md`), when there is one. Read it. Cuts recorded there are respected: DO NOT prototype features that were cut. Flag at the start: "I am skipping [feature_x] because it was cut in the discover." The hypothesis informs layout decisions (when the builder asks "how should I arrange the CTA?", recall it). The appetite scales fidelity: small/medium appetite = lean fidelity (structure + tokens; no microinteraction polish); large appetite = polish included.
- **The brief itself** is the **richer contract**: it carries the research, the chosen direction with its five parts (bet, composition, copy, rationale, risk), the base block common to all directions, and the token constraints read from source. The copy in the direction is the copy you build. Not a starting point to improve on. The spec and the design brief **coexist**: the spec says what problem and what was cut; the design brief says how this surface should be.
- **Read the medium** recorded by the medium question: it decides the artifact and the tooling (table at the top of `references/develop-modes.md`). On a canvas or `claude-design` medium there is no `prototype/` folder; the artifact is the canvas, named in the surfaces list. That is the normal path, not a failure.
- **Save your output** in `.bb/<slug>/design.md` under `## Built` (Step 3 below), update the
  surfaces list in its frontmatter, and set `phase: develop`.

## Step 0: pre-flight (silent)

Checks, without printing anything. **Which ones apply depends on `medium.chosen`**. Read it first.

### 0.0: medium

The medium is in the brief, recorded by the medium question.

- medium `code` → run 0.1–0.3 below.
- medium `claude-design`, `paper`, `figma` or `pencil` → **skip 0.1**. There is no `prototype/`
  folder on those paths by design, the scaffold is skipped. Instead confirm the MCP for that
  medium is reachable. The DS still comes from the plugin (0.2), the same as on `code`.
  Only if `design.md` is also missing do you fall into fallback mode.
- No medium in the brief → the builder arrived by shortcut, without the medium question. Do not
  guess: run the medium question (`references/phase-medium.md`) first. It is one turn and it
  decides everything downstream.

### 0.1: the prototype folder (medium `code` only)

```bash
test -d "$BB/<slug>/prototype"
```

If it does not exist: the builder reached Develop without Phase 3. Offer to run the scaffold, which is one turn, rather than improvising a folder here.

### 0.2: the design system

It ships with the plugin, so there is nothing per-project to find:

```bash
DS_PATH="${BRISAR_DS_PATH:-${CLAUDE_PLUGIN_ROOT}/skills/brisar/references/ds}"
test -d "$DS_PATH/brand"
```

If `BRISAR_DS_PATH` is set but unreadable, fall back to the plugin's own `references/ds/` and say so once, then continue. Only if neither resolves do you degrade to visual construction without DS (structure first, tokens later).

### 0.3: visual direction per surface

The surfaces are listed in `design.md`'s own frontmatter, each with its `artifact`. The task folder is the one for this slug, under the nearest `.bb/` up the tree:

```bash
BB=$(d=$PWD; while [ "$d" != / ] && [ ! -d "$d/.bb" ]; do d=$(dirname "$d"); done; echo "$d/.bb")
ls "$BB/<slug>/design.md" "$BB/tasks/<slug>/design.md" 2>/dev/null
```

If `## Surfaces` is empty: Phase 4 needs to run first (offer it) or the builder describes the screen directly in chat.

**Exception. A chosen direction outranks this check.** When `design.md` already carries one,
you have the visual direction in a richer form. Do not send the builder back to Phase 4 to
produce a thinner version of what the document already says.

## Step 1: intake (1-2 questions)

Print the introduction:

> **Develop phase**: I am going to build a clickable prototype of the screen, with the DS tokens applied. Mode: full surface, single component, or iteration on something that exists.

Call `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "What kind of build do you need?",
      "header": "Develop mode",
      "options": [
        {
          "label": "Full surface",
          "description": "Build 1 or more surfaces end to end (reads each one's direction in .bb/<slug>/design.md). Recommended if you came from the scaffold."
        },
        {
          "label": "Single component",
          "description": "Build 1 new component or DS variant (button, card, dialog, and so on). The output goes to the prototype's components/."
        },
        {
          "label": "Iterate on what exists",
          "description": "Change a screen or component that already exists. Reads the current file and proposes diffs."
        }
      ],
      "multiSelect": false
    }
  ]
}
```

If "Full surface" and `surfaces[]` has more than one entry, ask the second question:

```json
{
  "questions": [
    {
      "question": "Which surface, or surfaces?",
      "header": "Surface",
      "options": [
        { "label": "<surface_1>", "description": "The direction recorded for <surface_1>" },
        { "label": "<surface_2>", "description": "..." }
      ],
      "multiSelect": true
    }
  ]
}
```

If only 1 surface exists: skip the question, assume default.

## Step 2: build

Lazy-load `references/develop-modes.md`. Do not load everything in Step 0.

Each mode has a template + checklist:

| Mode                   | Template/checklist              | Main output                                                                             |
| ---------------------- | ------------------------------- | --------------------------------------------------------------------------------------- |
| Full surface           | `develop-modes.md#full-surface` | `.bb/<slug>/prototype/src/<surface>.tsx` (or `<surface>.html` if prototype-hosted)      |
| Single component       | `develop-modes.md#component`    | `.bb/<slug>/prototype/src/components/<Name>.tsx`                                        |
| Iterate on what exists | `develop-modes.md#iteration`    | Diff applied to the existing file                                                       |

Cross-cutting rules:

- **Tokens first.** Apply tokens before writing any hardcoded color/spacing.
- **DS components before custom.** If a Button exists in the DS, use it. Custom only if justifiable.
- **Loading/Empty/Error states always.** Even on small appetite. A state you did not build is declared in `states_not_built`, never faked.
- **Do not invent brand.** If the DS does not have an `accent-warning` color, do not invent it, ask the builder or mark TODO.
- **Mock the data, skip the wiring.** No API calls, no auth, no persistence. When the builder asks for the real thing, name the path: `/bb:spec`, then `/bb:implement`.

## Step 3: persistence + gate

Always write:

- The artifact itself, in the chosen medium (project files, preview, or canvas nodes)
- `.bb/<slug>/design.md`, section `## Built`: the build decisions, with the surfaces list in the
  document's own frontmatter
  in prose under it (custom components, missing tokens, doubts)

The surfaces list in `design.md`'s frontmatter:

```yaml
---
status: completed | in-progress | blocked
medium: code | claude-design | paper | figma | pencil
surfaces:
  - name: <surface_name>
    # Locator. Deliver reads the artifact from this. Precise or Deliver cannot review it.
    file: <path> # medium code / claude-design
    canvas: # medium paper / figma / pencil
      file: <file name or id>
      page: <page name>
      artboards: [<artboard/frame names, one per state or variant>]
    variants: [<variant name>] # when the surface has more than one, per the contract
    states: [default, loading, empty, error]
    status: built | iterated | blocked
    custom_components: [<name>] # components created outside the DS
    missing_tokens: [<token>] # tokens that were missing in the DS
    deviations: # conscious departures from the brief or the DS, Deliver checks these
      - what: <one line>
        why: <one line>
build_target: react+tailwind | prototype-html | canvas | preview-html
next_action: ready-for-review | needs-tokens | re-prototype
---
```

**Why the locator is strict:** the Deliver phase opens what you wrote. On a canvas medium it needs
file, page and artboard names to read structure and computed values through the MCP, "designed in
Paper" is not a locator. On any medium, a surface with variants that lists only one is a surface
whose other variants will not be reviewed.

**Record deviations rather than absorbing them.** A departure you justified in your head is
invisible to the review; one written here gets checked against the brief instead of being
rediscovered as a bug.

### Gate (always the last)

Echo what was built (1 line: _"Built <surface> at <path>. Loading/Empty/Error included."_) + reminder about missing tokens/components (if any). Then the handoff gate:

```json
{
  "questions": [
    {
      "question": "Surface built. Next step?",
      "header": "Next",
      "options": [
        {
          "label": "Review it and prepare the handoff (Deliver phase)",
          "description": "Design review + accessibility, then /bb:spec, before building for real"
        },
        {
          "label": "Build another surface",
          "description": "I go back to the Develop intake with the next surface"
        },
        {
          "label": "Stop here",
          "description": "The state is saved; run /bb:brisar again to continue"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

- **Deliver:** load `references/phase-deliver.md` and continue. Set the brief's `phase: deliver`.
- **Another surface:** loop back to Step 1 with the remaining surfaces.
- **Stop:** persist and end.

## Expected behaviors

1. **Fidelity > creativity.** The contract (tokens + components + the surface's direction file) is the truth. When something conflicts or is missing, ask. Do not improvise.
2. **States always.** Default, loading, empty, error. Even on small appetite, only skip with an explicit `cut_reason`.
3. **Decision recorded.** If you invented a custom component, write it under `## Built` in `.bb/<slug>/design.md` with the reason. Do not disappear without a record.
4. **At most 2 questions per turn.** More than that becomes a form. Ask + build + echo.
5. **Cuts respected.** If the spec cut X, do not prototype X. If the builder asks for X anyway, flag first: _"I noticed [X] was cut in the discover. Go on anyway, or reopen the cut?"_
6. **No nitpicking of tokens.** If tokens.md says `--color-primary: #0070F3`, use exactly that. Do not "tweak 1%" to look better.

One sharp caution: **never edit `tokens.md` or `components.md`**. The DS source of truth is governed by the scaffold phases (or an explicit DS-update round), and the Develop phase is a consumer. Writing to it from here creates a race between surfaces.

## Cooperation contract

| Artifact                                   | Produced by | Consumed by            |
| ------------------------------------------ | ----------- | ---------------------- |
| `${CLAUDE_PLUGIN_ROOT}/.../references/ds/` | the plugin  | Develop (Step 0, read) |
| `.bb/<slug>/design.md` (or `design/*.md`)  | Phase 4     | Develop (Step 2)       |
| `<project>/src/<surface>.tsx` (or .html)   | Develop     | Deliver, dev           |
| `.bb/<slug>/design.md`, `## Built`         | Develop     | Deliver, human builder |
