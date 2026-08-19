# Phase 0: calibration (1 question)

Before the lightning intake (Phase 1), brisar needs to understand WHO is building. A 1-question calibration determines:

1. **Depth of questions in Phase 1.** Executive → more questions in operational language. Senior dev → fewer questions, technical vocabulary OK.
2. **Default output path.** Executive → prototype + written handoff to dev. Senior dev → embed into real codebase. Junior → embed with step-by-step narration. Content → Framer.
3. **Conversation language.** Executive never receives "scaffold", "embed", "MCP" vocabulary. Senior receives it directly.

## When to run

Right after the Step 0 pre-flight (session, DS, tooling, detected product), before Phase 1.

**Skip if** session.yaml already has `profile.persona_id` filled (re-runs inherit the profile until the builder asks for a change).

## The question

Print a short intro before:

> **/bb:brisar**: before we start, help me calibrate so I can serve you better.

Then `AskUserQuestion`:

```json
{
  "questions": [
    {
      "question": "How will you work on this project?",
      "header": "Profile",
      "options": [
        {
          "label": "No technical background, I want a prototype",
          "description": "I don't know git or npm. I want something clickable to validate with stakeholders. Another team picks up the code later."
        },
        {
          "label": "I can work in code, take me straight there",
          "description": "I have git, a configured environment, I know the stack. I want the least friction possible."
        },
        {
          "label": "I get the basics, but I'll need instructions",
          "description": "I have git plus an environment, but keep explaining each step to me."
        },
        {
          "label": "I'll work on content or a site (Framer)",
          "description": "Institutional site, copy, design; no code. Whether I have git or not doesn't matter."
        }
      ],
      "multiSelect": false
    }
  ]
}
```

## Mapping

| Answer                         | persona_id       | needs_instructions | can_clone_repo         | Default path                                           |
| ------------------------------ | ---------------- | ------------------ | ---------------------- | ------------------------------------------------------ |
| No technical background        | `executive`      | true               | false                  | `prototype-hosted`                                     |
| I can work in code             | `builder-senior` | false              | true                   | `embed` if product detected, else `scaffold`           |
| I get the basics, I'll need    | `builder-junior` | true               | true                   | `embed` with narration, else `scaffold` with narration |
| I'll work on content or a site | `content`        | true               | false (doesn't matter) | `framer-handoff`                                       |

## Persistence

Writes to `.brisar/session.yaml`:

```yaml
profile:
  persona_id: executive | builder-senior | builder-junior | content
  needs_instructions: bool
  can_clone_repo: bool
  calibrated_at: <ISO>
```

## Implications for the rest of the flow

### `executive`

- **Phase 1 turns into 5-6 questions in operational language.** Doesn't ask "hosting" / "fidelity" / "Shaping appetite". Asks:
  - "Who is going to use this thing? (in-house lawyer, client, manager...)"
  - "What problem does it solve? (1 sentence)"
  - "When does it need to be ready?"
  - "Do you have a sense of the visuals (Inspira / Lexflow / other / not sure)?"
  - "Do you need the technical team to carry it on afterwards? (yes/no)"
- **Phase 2 (gate) skipped.** Executive doesn't decide on shaping; brisar can SUGGEST /bb:discover as a next step, but doesn't block.
- **Phase 3 does NOT scaffold locally with `pnpm install`.** Goes to `prototype-hosted` (generates folder + HANDOFF-DEV.md, makes it explicit that dev picks up later).
- **Terminal handoff** always includes instruction to pass the prototype + handoff markdown to someone in engineering.
- **Banned vocabulary in messages:** scaffold, embed, npm, MCP, repo, branch, slug. Use: "folder", "project", "install", "environment", "project name".
  - **This binds on every phase that prints, not only the intake.** The first diamond adds its own
    method names to the list: `divergence`/`diverge`, `reconciliation`, the research floor,
    `pocket`/`full`, and they get replaced by what they mean ("the paths I put together", "the
    minimum research"), never annotated. `references/brief.md` carries the mechanical self-check.

### `builder-senior`

- **Phase 1 reduces to 2 questions:** intent + (product OR brand, depending on whether Step 0.5 detected the product).
- **Skips hosting/appetite calibration** when product is detected (it's already known: embed into existing codebase).
- **Direct embed** if product known by the registry. If greenfield, minimal scaffold.
- **Maturity gate runs normally.** Senior can do a conscious override.
- **Vocabulary:** technical ok. No narration of each `cd <folder>`.

### `builder-junior`

- **Standard Phase 1 (3 questions).**
- **Each handoff becomes narrated instruction.** Instead of "run `pnpm install && pnpm dev`", prints:
  > 1. Open the terminal in this folder: `cd <slug>`
  > 2. Install the dependencies (this takes 1-2min): `pnpm install`
  > 3. Wait for it to finish. It prints "done" at the end.
  > 4. Start the dev server: `pnpm dev`
  > 5. Open http://localhost:5173 in the browser.
- **Maturity gate runs normally.**
- **Vocabulary:** technical OK but always explains the term on first occurrence.

### `content`

- **Forces Framer path.** Regardless of detected product, if calibration = content, goes to `references/phase-framer-handoff.md`.
- **Step 0.4 should have already detected** whether the unframer MCP is present. If missing: falls into `fallback_path: framer-handoff-no-mcp`, which generates markdown in cwd that the dev/designer picks up (and mention the builder can add the MCP to their Claude config for the canvas path next time).
- **Visual direction is GIVEN, not asked.** Content persona does not formulate design; brisar proposes based on product/brand.
- **Vocabulary:** marketing/design, not dev. Use: "page", "section", "block", "publish". Avoid: "deploy", "merge", "branch".

## Cross-validation with preflight

After the answer, brisar cross-references with what `preflight-tooling.md` detected silently:

| Answer           | Detected tooling     | What brisar does                                                                                                       |
| ---------------- | -------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| `builder-senior` | git missing          | "You said you can work in code but git isn't installed here. Want me to install it, or do you prefer another path?"    |
| `builder-senior` | gh without auth      | "Inspira's repos are private; you need `gh auth login`. Shall we do it together?"                                      |
| `content`        | unframer MCP missing | Notes it silently; the Framer phase uses the markdown fallback and tells the builder how to add the MCP for next time. |
| `executive`      | (any state)          | Doesn't check anything git/MCP; path doesn't require it.                                                               |

## Fallback

If builder doesn't respond clearly OR free response is ambiguous:

1. Temporary default to `builder-junior` (more robust path for uncertainty).
2. Asks ONCE again, simpler:
   > "To calibrate: are you going to work in the code directly, or only on content or a prototype?"
3. If still uncertain: persists as `builder-junior` and continues. Builder can ask to recalibrate at any time.

One sharp caution: **never guess the persona from the initial prompt**. An executive may write "I need a platform for X" exactly like a senior. Always run the calibration (ONE question; a second one turns it into a form).
