// node render.mjs scenes/demo [--fps 60] [--w 1920] [--h 1080] [--frames-only]
// Deterministic: headless browser calls seek(t) per frame, ffmpeg encodes. Audio: synthesized from window.BPM, or scene's audio.wav.
import { chromium } from "playwright";
import ffmpeg from "ffmpeg-static"; // bundled binary: no Homebrew needed
import { spawn } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import { resolve, basename } from "node:path";
import { synthBeat } from "./lib/audio.mjs";

const [dir, ...rest] = process.argv.slice(2);
if (!dir) {
  console.error("usage: node render.mjs scenes/<name> [--fps N --w N --h N]");
  process.exit(1);
}
const opt = (k, d) => (rest.includes(`--${k}`) ? +rest[rest.indexOf(`--${k}`) + 1] : d);
const fps = opt("fps", 60),
  w = opt("w", 1920),
  h = opt("h", 1080);
const name = basename(resolve(dir));
mkdirSync("out", { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: w, height: h } });
await page.goto("file://" + resolve(dir, "index.html"));
await page.evaluate(() => window.READY); // scene may expose a promise (fonts, images)
const { duration, bpm, ticks } = await page.evaluate(() => ({
  duration: window.DURATION,
  bpm: window.BPM,
  ticks: window.TICKS || [],
}));
const total = Math.round(duration * fps);

let audio = resolve(dir, "audio.wav");
if (!existsSync(audio)) {
  audio = bpm ? `out/${name}.wav` : null;
  if (audio) synthBeat(audio, duration, bpm, ticks);
}

const ff = spawn(
  ffmpeg,
  [
    "-y",
    "-loglevel",
    "error",
    "-f",
    "image2pipe",
    "-framerate",
    String(fps),
    "-i",
    "-",
    ...(audio ? ["-i", audio] : []),
    "-c:v",
    "libx264",
    "-pix_fmt",
    "yuv420p",
    "-crf",
    "16",
    ...(audio ? ["-c:a", "aac", "-shortest"] : []),
    `out/${name}.mp4`,
  ],
  { stdio: ["pipe", "inherit", "inherit"] },
);

for (let i = 0; i < total; i++) {
  await page.evaluate((t) => window.seek(t), i / fps);
  if (!ff.stdin.write(await page.screenshot({ type: "png" })))
    await new Promise((r) => ff.stdin.once("drain", r));
  if (i % fps === 0)
    await page.screenshot({ path: `out/${name}-still-${String(i / fps).padStart(2, "0")}.png` }); // stills for the critique loop
}
ff.stdin.end();
await new Promise((r) => ff.on("close", r));
await browser.close();
console.log(`out/${name}.mp4 (${total} frames @ ${fps}fps)`);
