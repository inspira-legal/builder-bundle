---
name: reel
description: Build a motion-design video (product launch film, feature walkthrough, showreel, UI morph loop, kinetic type) as code, render it to MP4 with sound, and critique its own frames until good. Use when the user asks for a motion or animated video, launch video, reel, "faz um vídeo", "vídeo de lançamento", "vídeo da feature", or invokes /motion:reel, e.g. "/motion:reel lançamento do Drive, 20s, vertical".
license: MIT
allowed-tools: Bash(node "${CLAUDE_SKILL_DIR}/scripts/bootstrap.mjs"), PowerShell(node "${CLAUDE_SKILL_DIR}/scripts/bootstrap.mjs"), Bash(node render.mjs *), PowerShell(node render.mjs *), Bash(node stills.mjs *), PowerShell(node stills.mjs *), Bash(node new-scene.mjs *), PowerShell(node new-scene.mjs *), Bash(node ffmpeg.mjs *), PowerShell(node ffmpeg.mjs *), Bash(node play.mjs *), PowerShell(node play.mjs *)
metadata:
  author: Enzo Figueiredo
  version: 0.1.0
---

# reel

Videos are programs. You write a scene with a pure `seek(t)`; `~/Motion/render.mjs` renders frames and the MP4. The person asking is often not technical: talk in their language, skip jargon, show the video and the stills, not the code.

## 0. Prepare the studio (every run)

Run `node "${CLAUDE_SKILL_DIR}/scripts/bootstrap.mjs"` exactly as written (the same command works in bash and in PowerShell). It is instant once the studio is ready, and installs it on the first run (a few minutes: say so before running it).

- `READY <path>`: `cd` there once and run every command below from it. Below, `~/Motion` means that path (on Windows it sits under the user folder, e.g. `C:\Users\<name>\Motion`); write commands with relative paths, never with `~`.
- `NODE_MISSING`, or `node` not found at all: stop and walk the person through installing Node LTS from nodejs.org (the installer for their system; on Windows on ARM, the x64 one, since ffmpeg has no ARM build there), then ask them to reopen Claude Code and repeat the request.
- `DEPS_MISSING` (Linux): Chromium lacks system libraries. Ask the person to run, once, `! sudo npx playwright install-deps chromium` in this prompt (the `!` runs it here; it asks for their password), then run the bootstrap again.
- Any other failure: show the last lines of the error in plain words; a network or proxy block on the Chromium or ffmpeg download is the usual cause.

Then read `~/Motion/CLAUDE.md`: its rules apply to everything below.

## 1. Parse the request

Extract, ask only if missing and it changes the result: **subject** (URL / product / "showreel"), **length** (default 15s), **format** (16:9 default; 9:16, 1:1 on request), **reference** (frame, video, image folder), **audio** (music, voice via key in `.env`). Scene name = kebab-case slug.

## 2. Reference before design

Inspira house style: before designing a product or feature film, read `~/Motion/scenes/drive-launch-v2/index.html` (launch) and `~/Motion/scenes/acervo-permissoes-v3/index.html` (feature walkthrough). Reuse their palette tokens, Poppins type, UI rig (app window, sidebar, cards, cursor) and pacing; copy the closer one as the starting point.
Without a reference the default is centered text on a gradient with everything fading in: avoid it.

- Frame: look at it; take palette, type, grain, pacing. Not the subject.
- Video: extract frames with the bundled ffmpeg (`node ffmpeg.mjs -i in.mp4 -vf fps=2 out/ref-%03d.png`), describe pacing shot by shot, then design.
- Folder of images: write `scenes/<name>/style_guide.md` from it first.
- None given: name a concrete look (e.g. "swiss editorial", "PC-98 pixel", "paper cutout") and say which. Let the technique follow the look; don't pick a library unless asked.

## 3. Brand / product

Fetch the product URL and gather real logo, screenshots and copy (use actual product assets, never invented ones). Keep one scene folder per brand so the renderer, audio and export are reused for follow-ups.

## 4. Write the spec, not the vibe

Before code, write `scenes/<name>/spec.md`:

- **Film in one line**: logline; every decision is checked against it.
- **Beat sheet**: timestamps on the beat grid (`motion.beat(n, bpm)`); hook in first 2s; a visual payoff every 3-5s; last frame == first when it should loop.
- **State list**: for UI films, one element that morphs size/radius/color between named states (button, loader, player, slider, chart, palette), a cursor driving each change. One shape, never cut.
- **Text on screen**: when huge, when subtitle-sized; leave composition room.
- **Gotchas**: layout is a function of (w, h); real data, not lorem.

## 5. Build

- Start the scene with `node new-scene.mjs <name> <base-scene>` (base: the closer house-style scene, or `demo`); it copies the folder with its fonts. Then change the files with Edit/Write, not with shell or Python scripts: those ask the person for approval.
- `scenes/<name>/index.html`, one file, zero deps, keeping the contract of `scenes/demo`: `window.DURATION`, `window.BPM`, `window.seek(t)`, `<script src="../../lib/motion.js">`.
- `seek(t)` pure: no timers, Date.now, Math.random (use a seeded hash of index).
- All motion via `motion.spring` / `motion.track` (presets: snappy UI, default cards/camera, heavy big type/logos, playful mascots). Tiny overshoot on UI, none on type. Multi-target values use `track()`.
- Cuts and hits on beats. Sound from `lib/audio.mjs` (synth on the same timeline) or the user's `audio.wav`. Voice: read the key from `~/Motion/.env` by name, never print it, and never ask the person to paste a key into the chat.
- Long films: gates plan -> rig -> stills -> animatic -> full pass -> polish -> audio -> render. Write `STORYBOARD.md`; for parallel work brief subagents through an `ANIMATION_GUIDE.md`.

## 6. Render and critique (mandatory)

1. `node render.mjs scenes/<name> --fps 60 [--w --h]`. Run it in the foreground with a 600000ms timeout, never in the background: a background render dies when the session ends.
2. Read the stills in `out/<name>-still-NN.png` (Read tool shows images).
3. Score 1-10: composition, type, motion feel, originality vs the reference. Check every on-screen word for spelling and accents (ANÁLISE, not ANALISE). List the 3 worst problems.
4. Fix, re-render. Repeat until every score is 8+. Iteration is the method; say how many rounds it took.

Test cheap first (`--fps 30`, short), final at 60.

## 7. Deliver

Run `node play.mjs <name>` so the video plays (when it prints `VIDEO <path>` there is no desktop to open it: give the path), then report the file path, the poster still and the rounds of critique. Other formats: re-render with `--w/--h` (9:16 = 1080x1920, 1:1 = 1080x1080); reframe type and UI per format, never crop.
