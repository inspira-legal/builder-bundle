# Phase 5: handoff + gate

After Phase 4 writes the visual direction of each surface into `.bb/<slug>/design.md`, the journey-map part of brisar is done. This phase prints the handoff summary, shaped by the profile, and ends with the **handoff gate**. A single `AskUserQuestion` offering the natural next steps. The gate suggests, never auto-invokes (per `plugins/bb/references/handoff-gate.md`).

**Read the medium before writing the summary.** Everything below that names the `prototype/`
folder assumes medium `code`. On a canvas or
`claude-design` medium Phase 3 was skipped (`medium.scaffold: skipped`) and none of those exist:
report `design.md` and the canvas artifact instead. Telling the builder to open a folder that
was never created is the kind of error that reads as the tool being confused about its own state.

## Output shape (default: `technical_instructions` true)

Plain text. Structure:

```
✓ /bb:brisar finished the scaffold. Prototype at .bb/<slug>/prototype/

Structure created:
  .bb/<slug>/
  ├── design.md                                      ← the journey, one surface per section
  └── prototype/
      ├── package.json, vite.config.ts, tsconfig.json
      └── src/{main.tsx, App.tsx, index.css, tokens-brand.css}

To run it:

  cd <slug>
  pnpm install
  pnpm dev
```

With a single surface, that last block is one line, `.bb/<slug>/design.md`.

Then the gate:

```json
{
  "questions": [
    {
      "question": "Scaffold ready. Next step?",
      "header": "Next",
      "options": [
        {
          "label": "Build the surfaces now (Develop phase)",
          "description": "I continue in this session: I read the chosen direction and each surface in .bb/<slug>/design.md, plus the DS from the plugin, and build screen by screen"
        },
        {
          "label": "Run /bb:discover first",
          "description": "Deepen the framing (problem, fit, hypothesis, appetite) before designing"
        },
        {
          "label": "Stop here",
          "description": "The project stays ready; run /bb:brisar again in this folder whenever you want to build"
        }
      ],
      "multiSelect": false
    }
  ]
}
```

- **Develop:** load `references/phase-develop.md` and continue in this same session. Set the brief's `phase: develop`.
- **/bb:discover:** suggest the command (`/bb:discover <the idea in 1 sentence>`) and STOP, never invoke it.
- **Stop:** print one line saying the re-entry works (`/bb:brisar` in this folder resumes) and end.

## Conditional variants

### If `uses_terminal` is false (path prototype-hosted)

**Replaces the whole default terminal**: nobody runs `pnpm dev` here and the Develop phase doesn't apply (design goes straight to HTML in Phase 4).

```
✓ /bb:brisar finished. HTML prototype created at .bb/<slug>/prototype/

What's here:
  .bb/<slug>/
  ├── design.md               ← the written direction for each screen
  └── prototype/
      ├── index.html          ← open this file in the browser (double-click)
      ├── <surface-1>.html    ← one page per screen
      ├── <surface-2>.html
      ├── styles.css          ← the visuals of the <brand> brand
      └── README.md           ← how to show it to the team

How to open it:
  1. Go to the .bb/<slug>/prototype/ folder in Finder
  2. Double-click index.html
  3. It opens in the browser. The links on the page take you to each screen.

You don't need to install anything. It works offline.

How to show it to the team:
  - Share the zipped folder (each person opens the index.html)
  - Or ask the eng team to host it (Vercel/Netlify). It becomes a link

To turn it into a real product:
  Pass the folder to the technical team. They rewrite it
  in the real stack (Vite + React + Tailwind v4 with the brand tokens).
  `../design.md` carries the direction, and `/bb:spec` turns it into the contract.
```

If the builder marked `intent.scale_signal == will-scale`, add at the end:

```
⚠ You marked that this prototype WILL become a product. Before the technical
team picks it up, consider running /bb:discover, it leaves the problem, the
hypothesis and the metric clear, and saves rework later.
```

No Develop gate here. End with a simple report. Mention `/bb:discover` as the optional next step (as above) and stop.

### If `technical_instructions` is false (explicit narration)

Same default terminal, but with narration before the gate:

```
✓ /bb:brisar finished the scaffold. I'll walk you through the next steps:

1. Open a terminal in this folder. Command:
       cd <slug>

2. Install the dependencies (this takes 1-2 minutes):
       pnpm install
   If you don't have pnpm: install it with `npm install -g pnpm` first.

3. Run the development server:
       pnpm dev
   A link like http://localhost:5173 shows up, open it in the browser.

If anything goes wrong at any step, tell me. I help you debug it.
```

Then the same gate as the default variant (Develop / /bb:discover / stop). In the Develop option description, add that each step will be narrated.

### If path Framer (`brand.workflow == framer-harpa`)

**Replaces the whole default terminal**: the builder doesn't have a `<slug>/` to cd into. The path is to open Claude Code inside `harpa-lpbuilder/`. See `phase-framer-handoff.md` for the terminal it prints. No Develop gate. The Develop phase is not used on the Framer path.

### If Phase 2 fired and the builder chose override

Add before the gate:

```
⚠ Heads up: you marked "<scale_signal>" but skipped the maturity gate.
The override is recorded in the brief's decision log with the reason "<override_reason>".
If at some point you feel the grounding is missing, run /bb:discover,
that is where it gets resolved.
```

### If brand: deferred

Add:

```
⚠ Brand: not decided yet. I used the Inspira tokens as a fallback.
When you decide, run /bb:brisar again.
```

### If brand.source ∈ {custom-from-inspira, custom-from-lexflow, from-scratch, external-tokens}

Add:

```
⚠ Custom brand (<source>): the initial tokens are inherited from <base>.
The token delta in design.md carries the identity as it evolves.
When it stabilizes, consider promoting it to a DESIGN.md of its own at <DS_PATH>/brand/<name>/.
```

### If DS not-found

Add:

```
⚠ The design system was not found in this environment. The scaffold's tokens are
Tailwind defaults with placeholders. Point BRISAR_DS_PATH at it. The bundle also
carries a copy at references/ds/ inside the skill itself.
```

### If DS gaps were detected in Phase 4

Add:

```
🌱 DS gaps detected in the surfaces:
  - <surface>: <missing component>
  - ...

These are recorded in the brief, under what was left out.
Review or promote them whenever you want. They are candidates for new DS components.
```

## Critical behavior

- **Do not execute `cd`, `pnpm install`, or the dev server.** The user runs them. Auto-execution violates the builder's expectation and creates side effects without confirmation.
- **Surface errors explicitly.** If any file from Phase 3/4 failed to be written, mention it instead of simulating success.
- **Always include the path on the first line** (`./<slug>/` is relative. Good; `<slug>` alone is ambiguous). The builder may be following logs; ambiguity here costs time.

## When to run /bb:brisar again in the same project

If the builder returns to the same slug and runs /bb:brisar:

- Step 0 finds `.bb/<slug>/design.md` with `status: completed` in its frontmatter.
- Asks:
  ```
  A Brisa project already exists here (<slug>, brand <brand>, <N> surfaces). What do you want?
  - Build/iterate the surfaces (Develop phase)
  - Review/handoff what exists (Deliver phase)
  - Add a new surface (goes to Phase 4)
  - Switch brand (rewrites the tokens, keeps src/)
  - Reframe it (I suggest /bb:discover)
  - Start over from zero (appends a new round to the brief, keeping the old one)
  ```
- Routes accordingly. "Reframe it" suggests `/bb:discover` and stops; "Start over" appends a round, it never replaces what the brief already holds.

This is the re-entry contract. Not used on the first invocation, but keeps the skill useful in subsequent sessions.
