// node render.mjs scenes/demo [--fps 60] [--w 1920] [--h 1080]
// Deterministic: headless browser calls seek(t) per frame, ffmpeg encodes. Audio: synthesized from window.BPM, or scene's audio.wav.
// Runs from any folder: paths resolve against the studio, so the skill can call it by absolute path.
import { chromium } from "playwright";
import ffmpeg from "ffmpeg-static"; // bundled binary: no Homebrew needed
import { spawn } from "node:child_process";
import { existsSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { resolve, basename } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { synthBeat } from "./lib/audio.mjs";

process.chdir(fileURLToPath(new URL(".", import.meta.url)));
const die = (msg) => {
  console.error(`render failed: ${msg}`);
  process.exit(1);
};

const [dir, ...rest] = process.argv.slice(2);
if (!dir) die("usage: node render.mjs scenes/<name> [--fps N --w N --h N]");
const opt = (k, d) => (rest.includes(`--${k}`) ? +rest[rest.indexOf(`--${k}`) + 1] : d);
const fps = opt("fps", 60),
  w = opt("w", 1920),
  h = opt("h", 1080);
// yuv420p needs even dimensions; ffmpeg would fail late and leave the previous mp4 in place.
if (!(fps > 0) || !(w > 0 && w % 2 === 0) || !(h > 0 && h % 2 === 0))
  die(`--fps must be positive and --w/--h positive even numbers (got ${fps}, ${w}x${h})`);
const name = basename(resolve(dir));
const mp4 = `out/${name}.mp4`;
mkdirSync("out", { recursive: true });

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: w, height: h } });
await page.goto(pathToFileURL(resolve(dir, "index.html")).href);
await page.evaluate(() => window.READY); // scene may expose a promise (fonts, images)
const { duration, bpm, ticks } = await page.evaluate(() => ({
  duration: window.DURATION,
  bpm: window.BPM,
  ticks: window.TICKS || [],
}));
const total = Math.round(duration * fps);
if (!Number.isFinite(total) || total <= 0) {
  await browser.close();
  die(`window.DURATION must be a positive number of seconds (got ${duration})`);
}

let audio = resolve(dir, "audio.wav");
if (!existsSync(audio)) {
  audio = bpm ? `out/${name}.wav` : null;
  if (audio) synthBeat(audio, duration, bpm, ticks);
}

// A stale mp4 must never pass for the new one: drop it before encoding.
rmSync(mp4, { force: true });
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
    mp4,
  ],
  { stdio: ["pipe", "inherit", "inherit"] },
);
const closed = new Promise((r) => ff.on("close", r));
let pipeError = null;
ff.stdin.on("error", (e) => (pipeError = e)); // ffmpeg died mid-render: stop feeding it

for (let i = 0; i < total && !pipeError; i++) {
  await page.evaluate((t) => window.seek(t), i / fps);
  const png = await page.screenshot({ type: "png" });
  if (i % fps === 0)
    writeFileSync(`out/${name}-still-${String(i / fps).padStart(2, "0")}.png`, png); // stills for the critique loop
  // Racing `closed` keeps a dead ffmpeg from leaving us waiting for a drain that never comes.
  if (!ff.stdin.write(png))
    await Promise.race([new Promise((r) => ff.stdin.once("drain", r)), closed]);
}
ff.stdin.end();
const code = await closed;
await browser.close();
if (code !== 0 || pipeError) {
  rmSync(mp4, { force: true });
  die(`ffmpeg exited with code ${code}${pipeError ? ` (${pipeError.message})` : ""}`);
}
console.log(`${mp4} (${total} frames @ ${fps}fps)`);
