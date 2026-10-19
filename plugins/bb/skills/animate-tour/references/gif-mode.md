# GIF mode: the animation outside the app

GIF mode is for a person who needs the animation in an email, a presentation or the help
center, with no access to the code. It produces the **animated area** only (the 404 × 212 stage,
without the modal around it): one GIF per step, the full GIF, and a settled `.png` per step.

The work runs on `/bb:reel`'s studio in `~/Motion`: its Chromium plays the scene frame by frame
and its ffmpeg encodes. Every command below goes through this skill's wrapper,
`node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" VERB …`, the only form pre-approved. Run it exactly as
written, from any folder, with no `cd`.

The sections follow the work:

1. Prepare the studio
2. Start the scene
3. Write the steps
4. Record
5. Check before delivering
6. Deliver

## 1. Prepare the studio

Run `node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" prepare` in the foreground with a 600000 ms
timeout. It runs `/bb:reel`'s bootstrap, so it is instant once the studio is ready, and the first
run installs it (a few minutes and about 270 MB: say so before running it).

- `READY PATH`: that path is the studio, written `STUDIO` below (usually `~/Motion`).
- The command timed out: run it again. It resumes.
- `NODE_MISSING`, or `node` not found: stop and walk the person through installing Node LTS (20
  or newer) from nodejs.org, then ask them to reopen Claude Code and repeat the request.
- `WINDOWS_ARM`: walk the person through installing the x64 build of Node from nodejs.org, which
  runs on ARM, then repeat.
- `DEPS_MISSING` (Linux): ask the person to run, once, the exact command the line prints,
  prefixed with `!` in this prompt, then run `prepare` again.
- A record that fails with "Executable doesn't exist": the browser cache was cleaned. Run
  `node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" prepare --force` and record again.

## 2. Start the scene

Run `node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" new SLUG`, with a short kebab-case slug ending in
`-tour` (`case-tracking-tour`); the script refuses any other name, because the studio's `CLAUDE.md`
points its tour exception at `scenes/*-tour/`. It writes `STUDIO/scenes/SLUG/index.html` from
`assets/scene-template.html`, with the Poppins fonts and `icons.js` beside it. Add
`--from example-tabular` to start from the Análise em Tabela tour, ported whole, which is also
the model for translating a `StepArt.tsx` into a scene.

Change the scene with Read, Edit and Write only, never with shell, sed or Python. The skill
pre-approves those file tools under `STUDIO/scenes` and the `tour.mjs` verbs, and a shell edit is
not. The pre-approval holds for the turn in which the skill opens: after the person's next message
(a change asked at SKILL.md, step 6), Claude Code may ask again for each record and each edit.
When that happens, tell the person once that the option that stops asking for that command
keeps the rest of the loop quiet. The studio's `CLAUDE.md`
holds the rules of `/bb:reel` films, and a tour scene follows `pattern.md` instead.

## 3. Write the steps

1. Change the `<title>` and write one `<template data-step="N" data-title="..." data-duration="4">`
   per step, in order.
2. Build the art with the template's classes (`pattern.md`, section 3, maps them to the code) and
   `style="..."` for measures. Colors come from the `--color-*` variables only.
3. Icons: an empty `i` element with `data-icon="NAME"` and `class="ic ic-sm"` (or `ic-xs`). The
   names are the files in `assets/icons` without the `.svg` (`paper`, `plus`, `grid`,
   `folder-kanban`, `calendar`, `check`, `download`, `comment`, `court`, `judge` and so on). An
   unknown name fails the record and names the icon.
4. Entrances: the `pop` class (or `step-in` on a whole block) and `style="animation-delay:.15s"`
   for the stagger. The point of attention: the `glow` class on the target, and the cursor SVG
   (`class="cursor"`) inside a `span` with `class="rel"` that wraps the target. The template's
   comment says where to anchor the cursor for each target size.
5. Two movements on one element: each movement class declares the whole `animation`, so the last
   one wins. `pop glow` and `step-in glow` are already combined in the template and work. For
   any other pair (`pop` with a keyframe of your own, say), put the entrance on a parent element
   and the loop on its child, or the element stays at `opacity:0` for good.
6. A movement the template lacks (`taskMove`, say): copy its keyframe from `pattern.md`,
   section 4, into the block "This feature's own keyframes", with the `tour-` prefix.

### How long each step lasts

`data-duration` sets the seconds a step stays on screen:

- **4s** is the default: about 1.2s of entrances and 2.8s holding with the cursor tapping, long
  enough to read the miniature.
- A step with a long movement (`taskMove`, 3.6s) takes **a multiple** of the cycle, so the loop
  never cuts in the middle (3.6s or 7.2s).
- Past 6s a step gets heavy. Split it into two steps instead.

A step's GIF goes back to the start when it loops, so its entrances play again. That is
intended: each loop presents the idea again, the way reopening the step does in the app.

## 4. Record

```bash
node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" record SLUG --quality light
node "${CLAUDE_SKILL_DIR}/scripts/tour.mjs" record SLUG --quality high
```

| Quality | For                               | Size           | fps | Ceiling                  |
| ------- | --------------------------------- | -------------- | --- | ------------------------ |
| `light` | Email, presentation, Slack        | 404 × 212      | 20  | flags any GIF above 2 MB |
| `high`  | Help center, product page, retina | 808 × 424 (2x) | 25  | none                     |

The fps always divides 100, because a GIF stores the delay between frames in hundredths of a
second: 30 fps would play 10% faster than it was recorded. The output lands in `STUDIO/out/SLUG/QUALITY/`.
A full record replaces that folder only once every file is ready, so a failed record leaves the
previous delivery whole:

```
SLUG-step-1.gif … SLUG-step-N.gif
SLUG-full.gif
SLUG-step-1.png … SLUG-step-N.png      the settled frame of each step
```

To iterate on one step, add `--steps 2` (or `--steps 2 3`). It replaces only those steps' GIF and
`.png`, keeps the others, and leaves `SLUG-full.gif` as it was: the record prints a `NOTE` when the
full GIF predates the change. Before delivering, record once without `--steps` so the full GIF
carries every change.

Every GIF opens on its settled frame, not on the empty stage, because an email client that does
not animate (Outlook desktop) shows the first frame only.

## 5. Check before delivering

Read **every** settled `.png`, one per step. Compare them with the screenshots you received and
with `references/examples/case-tracking-frames.png`, three frames of the Acompanhamento
Processual launch GIF. That image is a reference of **style**, not of content: where it differs
from the screenshots, the screenshots win.

- The content is centered, with room on both sides, and nothing is cut at the stage's edges.
- The text reads at 404px: 11px is the floor.
- Every element that should show does show. A missing element is nearly always the two
  movements conflict of section 3, item 5.
- No data from the screenshots went through unreplaced (`pattern.md`, section 1).
- The record printed no `WARN` about Poppins.
- In `light`, no GIF is flagged `OVER 2 MB`. If one is, shorten `data-duration` or cut a step.

## 6. Deliver

Deliver the quality the person asked for. Give the output folder and one line per file (the
full GIF, each step's GIF, and the `.png` as a cover or a still alternative), with the step plan:
each step's title and body are the caption that goes around the GIF. List what was replaced (the
screenshots' data, colors outside the palette) and what was left out (discarded screenshots).
Close with the plain text question of SKILL.md, step 6: is the result what the person wanted, or
what would they change.
