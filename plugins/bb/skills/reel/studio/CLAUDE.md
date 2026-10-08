# Motion studio

Videos here are programs, not files. You write a scene; `render.mjs` turns it into frames and MP4. This file holds the scene rules; the reel skill points here instead of repeating them.

## Pipeline

- Scene = `scenes/<name>/index.html` exposing `window.DURATION` (seconds), optional `window.BPM`, and `window.seek(t)` (paints the exact frame at time t, seconds). Copy the contract from `scenes/demo`; `<script src="../../lib/motion.js">`.
- Start a scene: `node new-scene.mjs <name> <base-scene>` (base: the closer house-style scene, or `demo`).
- Preview frames: `node stills.mjs scenes/<name> t1 t2 … [--w --h]` → `out/<name>-at-<t>.png`.
- Render: `node render.mjs scenes/<name> [--fps 60 --w 1920 --h 1080 --subframes N]` → `out/<name>.mp4` + one still per second `out/<name>-still-NN.png`. It exits with an error, and leaves no mp4, when the render fails.
- Motion blur: `--subframes 8` averages 8 seeks per frame (180° shutter), so fast moves smear instead of stepping. It costs N× the render time; 8 is the floor (4 leaves double outlines). One blur grammar per film: never subframes on a stepped film, never stacked on fake smear copies. The stills stay sharp.
- Reference video: `node ffmpeg.mjs frames <video> [fps]` → `out/ref-NNN.png`.
- Every script runs from any folder: paths resolve against the studio.
- Default stack: one HTML file, canvas/SVG, zero dependencies. Fonts ship with the scene (`scenes/<name>/assets/*.woff2`, Poppins in the house scenes); a monospaced face is installed at `../../node_modules/@fontsource/jetbrains-mono/files/`.

## Rules

- `seek(t)` is pure: no setTimeout, requestAnimationFrame, Date.now, Math.random (use a seeded hash of an index). Same t → same pixels.
- Motion = closed-form springs from `lib/motion.js` (`spring`, `track`). No easing curves. Presets: snappy (UI), default (cards/camera), heavy (big type/logos), playful (mascots). Tiny overshoot on UI, none on type.
- A value with several targets uses `track()` (one spring per change), never restart a spring.
- Cuts and hits land on the beat grid (`motion.beat(n, bpm)`). Sound: `lib/audio.mjs` synthesizes on the same timeline; a scene's own `audio.wav` overrides it.
- Layout from a function of (w, h), not fixed pixels, so 9:16, 1:1 and 16:9 all render. Reframe type and UI per format, don't crop.
- No centered-text-on-gradient with everything fading in. Ask for or use a reference (frame, video, image folder) before designing; extract its palette, type and pacing.
- Real data and real product assets, never lorem or invented logos.

## Critique loop (mandatory before calling a video done)

1. Render, read the stills. 2. Score each 1–10 (composition, type, motion feel, originality). Check every on-screen word for spelling and accents. 3. Write the 3 worst problems. 4. Fix and re-render. Repeat until every score is 8+.
   Test cheap first (`--fps 30`), final at 60. Gates for long films: plan → rig → stills → animatic → full pass → polish → audio → render.
