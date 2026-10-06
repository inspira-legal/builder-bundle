# Motion studio

Videos here are programs, not files. You write a scene; `render.mjs` turns it into frames and MP4.

## Pipeline

- Scene = `scenes/<name>/index.html` exposing `window.DURATION`, optional `window.BPM`, and `window.seek(t)` (paints the exact frame at time t, seconds).
- Render: `npm run render -- scenes/<name> [--fps 60 --w 1920 --h 1080]` -> `out/<name>.mp4` + one still per second `out/<name>-still-NN.png`.
- Default stack: one HTML file, canvas/SVG, zero dependencies. Use Remotion/HyperFrames only if asked.

## Rules

- seek(t) is pure: no setTimeout, requestAnimationFrame, Date.now, Math.random. Same t -> same pixels.
- Motion = closed-form springs from `lib/motion.js` (`spring`, `track`). No easing curves. Presets: snappy (UI), default (cards/camera), heavy (big type/logos), playful (mascots). Tiny overshoot on UI, none on type.
- A value with several targets uses `track()` (one spring per change), never restart a spring.
- Cuts and hits land on the beat grid (`motion.beat(n, bpm)`). Sound: `lib/audio.mjs` synthesizes on the same timeline; a scene's own `audio.wav` overrides it.
- Layout from a function of (w, h), not fixed pixels, so 9:16, 1:1 and 16:9 all render. Reframe type and UI per format, don't crop.
- No centered-text-on-gradient with everything fading in. Ask for or use a reference (frame, video, image folder) before designing; extract its palette, type and pacing.
- Keys go in `.env` (never in prompts or code).

## Critique loop (mandatory before calling a video done)

1. Render, read the stills. 2. Score each 1-10 (composition, type, motion feel, originality). 3. Write the 3 worst problems. 4. Fix and re-render. Repeat until every score is 8+.
   Gates for long films: plan -> rig -> stills -> animatic -> full pass -> polish -> audio -> render.

## Effort

medium for small fixes/re-renders, xhigh for new films, max when the first 3 seconds must carry a launch.
