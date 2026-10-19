---
name: animate-tour
description: Build the first-steps animation of an Inspira feature, the stepped tour of its "Bem-vindo à" modal, in the pattern of the Análise em Tabela, Gestão de Projetos and Acompanhamento Processual tours, delivered as the app's FeatureTourDialog code or as GIFs of the animated area (one per step plus the full tour). It plans the steps from the feature's screenshots, its code or a walk through it in the browser. Use when the user asks for "animação de primeiros passos", "tour da feature", "modal de onboarding animado", "GIF mostrando como a feature funciona", "GIF para o e-mail de lançamento", "GIF para a central de ajuda", mentions StepArt or TourDialog, or invokes /bb:animate-tour. Don't use it for a free-form motion video or a launch film in MP4 (use /bb:reel).
license: MIT
allowed-tools: Bash(node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" prepare), PowerShell(node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" prepare), Bash(node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" prepare --force), PowerShell(node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" prepare --force), Bash(node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" new *), PowerShell(node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" new *), Bash(node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" record *), PowerShell(node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" record *), Read(~/Motion/**), Edit(~/Motion/scenes/**/*.html), Write(~/Motion/scenes/**/*.html)
metadata:
  author: Dênis Augusto Luft
---

# animate-tour

Inspira's first-steps modals tell a feature in 3 to 5 steps, each with an animated miniature of
the interface. This skill makes that animation **always in the same pattern**, as code or as GIF.

The whole pattern (narrative, stage, palette, motion vocabulary) is in `references/pattern.md`.
Read it before drawing any step. It is the contract: the skill takes no color, curve or rhythm
from outside it. The person asking is often not technical: talk in their language, and show the
step plan and the stills, not the code.

## 1. Pick the mode

Ask where the animation will be used, when the request does not say:

- **Inside the app** (a dev building the feature): **code mode**. It needs the
  `frontend-projects` repository. Follow `references/code-mode.md`.
- **Outside the app** (email, presentation, help center, social): **GIF mode**. It needs no code.
  Follow `references/gif-mode.md`. Ask which quality they want, `light` (email, slides) or `high`
  (help center), unless the request already names it or its use. Make both only when the person
  answers that they do not know, never as a way to skip the question.

A dev may want both: the code first, then the GIF of the same art.

## 2. Gather the material

Ask for what did not come with the request:

- **How you see the feature.** Offer three sources, and take whichever the person picks:
  - **Screenshots** of each stage of the feature, in the order a person uses it.
  - **The code**, in code mode: the feature's pages and components in `frontend-projects`.
  - **You walk it in a browser**, on `https://app.dev.inspira.legal/` unless the person names
    another address. Follow `references/walkthrough.md`.
- **One line about the feature**: what it solves and which action starts it ("criar projeto",
  "adicionar processo").
- In code mode, **the page** where the tour opens and **the action** the last button triggers.

Without screenshots or a walk, the feature has to exist in the app and the person has to
describe each screen. Draw only the screens you saw or had described, and say what is missing. Step 1 is the
exception: it is a piece of the pattern (`pattern.md`, section 1).

A screenshot that is unreadable, blurred, empty or caught mid-transition is no basis for a step.
Leave it out, and say which one you discarded and what it seemed to show, so the person can send
another when that screen matters.

## 3. Plan the steps before drawing

From the screenshots, the code or the walk, write the step plan and **get it approved through `AskUserQuestion`
before producing anything**. Put the plan in the question itself, one line per step:

| Step | Title    | Body (1 or 2 sentences) | Miniature                      | Movement                               |
| ---- | -------- | ----------------------- | ------------------------------ | -------------------------------------- |
| 1    | Comece … | …                       | dashed card and the "…" button | `stepIn`, cursor and `glowPulse` on it |
| 2    | …        | …                       | the crop of screen X: …        | `pop` staggered by .15s, …             |

The plan follows `pattern.md`, section 1: 3 to 5 steps, one idea each, step 1 "create" and the
last one "the result", the miniature as the smallest crop of the real screen with its real
labels, fictional data in place of anything the screenshots show (say what you replaced), and a
single looping point of attention per step.

In GIF mode the title and the body do not go into the image, since the animated area is the art
alone, but they stay in the plan: they are the caption communication writes around the GIF.
Write them in the brand's voice. When the `inspira-brand-messaging` skill is available, follow
it. When it is not, take the tone from the existing tours (`references/examples/`): a short
sentence, the verb in the imperative, the benefit before the mechanism.

## 4. Produce

- **Code:** `references/code-mode.md`. The mold is the repo's current `ProjectsTourDialog`, and
  the examples are in `references/examples/`.
- **GIF:** `references/gif-mode.md`. It runs on `/bb:reel`'s studio, starts from
  `assets/scene-template.html` (or `assets/example-tabular.html`, a whole tour already ported) and
  records with `scripts/tour.mjs`.

## 5. Check against the pattern

Before delivering, go through this list:

- [ ] The stage is 404 × 212 with the `sky-2 → neutral-1` gradient, and the content is centered
      in 220 to 320px (up to 360px on a dense screen, `pattern.md`, section 2).
- [ ] Only the colors of the aliases and tokens in `pattern.md`, section 3. Only design system
      icons.
- [ ] Entrances use `pop` or `stepIn`, staggered by .15s, the largest `animation-delay` at about
      .9s, and every one ends visible.
- [ ] The standard cursor SVG sits on the target, the target has `glowPulse`, one loop per step.
- [ ] No text under 11px. No real data.
- [ ] Code: the last button's label fits the footer (`pattern.md`, section 6).
- [ ] Code: lint, ts:check, spell:check and the spec pass, and you saw the tour running in the
      app.
- [ ] GIF: Poppins loaded, `light` stays under its ceiling, and you read **every** settled `.png`
      and found no missing element.

## 6. Close the delivery

End the delivery message by asking, in plain text, whether the result is what the person wanted
or what they would change. It is an open question with no options, because a change to a tour is
said in the person's own words ("the cursor covers the button", "step 3 is too fast"). When they
ask for a change, make it, check it again (record the GIF again, or rerun the checks in code
mode), show the new stills or the changed step, and ask again. Repeat until the person says it is
good.

GIF mode has no natural next step: once the person approves, stop.

Code mode, once the person approves, ends with the handoff gate
(`<plugin-root>/references/handoff-gate.md`): one `AskUserQuestion` naming the tour that was built
and asking how to follow.

| Option               | What it does now                                                                      |
| -------------------- | ------------------------------------------------------------------------------------- |
| Review (Recommended) | Invokes `/bb:review` over the branch, with the accessibility and design fronts in it. |
| Ship                 | Invokes `/bb:ship`, which settles the destination and ships the branch.               |
| Stop here            | The tour stays on the branch; pick it back up with `/bb:review` or `/bb:ship`.        |

## Keep the skill current

`references/pattern.md` and `references/examples/` are a dated copy of the app. When a new tour
lands in the app, or an existing one changes a keyframe, a color or a measure, update both, plus
the "DO NOT EDIT" blocks of `assets/scene-template.html`.

`assets/icons` is a copy of `packages/ui/src/assets/icons` in `frontend-projects`, taken at
`7d472a7f9` (`origin/main` on 2026-10-15) and still identical at `caaac6800`. The package version
(`@inspira-legal/ui` 1.0.0) does not move when an icon changes, so the commit is the pin. Every
`.svg` there is the list of icons a scene may use, so a missing icon fails the record. To see
whether the design system moved since the copy, and to copy it again, run from the
`frontend-projects` checkout:

```bash
git diff --stat 7d472a7f9 origin/main -- packages/ui/src/assets/icons
cp packages/ui/src/assets/icons/*.svg PATH_TO_BB/plugins/bb/skills/animate-tour/assets/icons/
```

Then write the new commit in place of `7d472a7f9` above.
