// node tour.mjs <prepare|new|record> [args…]: the GIF mode of /bb:animate-tour, on the reel studio.
//
//   prepare                         runs /bb:reel's bootstrap: installs or confirms ~/Motion, prints READY <path>
//   new <slug> [--from <asset>]     starts ~/Motion/scenes/<slug> from assets/<asset>.html (default scene-template)
//   record <slug> [--quality light|high] [--steps N …]
//                                   writes ~/Motion/out/<slug>/<quality>/: one GIF per step, the full GIF,
//                                   and a settled PNG per step
//
// The studio's engine does the work: its Playwright drives the scene's seek(t) frame by frame and its
// ffmpeg encodes. Nothing here installs a second browser. The skill pre-approves this file by its own
// path, and the slug rule keeps every path inside ~/Motion.
import { spawnSync } from "node:child_process";
import {
  copyFileSync,
  existsSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  renameSync,
  rmSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { createRequire } from "node:module";
import { homedir, tmpdir } from "node:os";
import { basename, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const SKILL = fileURLToPath(new URL("..", import.meta.url));
const HOME = process.env.MOTION_HOME ?? join(homedir(), "Motion");
// A tour scene's name ends in -tour: the studio's CLAUDE.md points its exception at scenes/*-tour/,
// so a tour scene never gets read as a /bb:reel film. The same rule keeps `../` out of every path.
const SLUG = /^[a-z0-9][a-z0-9-]*-tour$/;
const ASSET = /^[a-z0-9][a-z0-9-]*$/;
const WIDTH = 404;
const HEIGHT = 212;

// GIF stores the delay in hundredths of a second, so fps divides 100 or the GIF plays fast.
// Ordered (bayer) dithering keeps the gradient smooth and, unlike error diffusion, stays still
// from frame to frame instead of shimmering.
const QUALITIES = {
  light: { scale: 1, fps: 20, dither: "bayer:bayer_scale=5", capMb: 2 },
  high: { scale: 2, fps: 25, dither: "bayer:bayer_scale=3", capMb: null },
};

const die = (msg, code = 1) => {
  console.error(msg);
  process.exit(code);
};
// Inside a recording, a failure throws instead, so the browser closes and the frames are removed.
const fail = (msg) => {
  throw new Error(msg);
};
const flag = (args, name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : fallback;
};

function prepare(args) {
  const bootstrap = join(SKILL, "..", "reel", "scripts", "bootstrap.mjs");
  if (!existsSync(bootstrap))
    die("BOOTSTRAP_MISSING: /bb:reel's bootstrap is not beside this skill.");
  const r = spawnSync(process.execPath, [bootstrap, ...args.filter((a) => a === "--force")], {
    stdio: "inherit",
  });
  process.exit(r.status ?? 1);
}

function writeIcons(sceneDir) {
  const dir = join(SKILL, "assets", "icons");
  const icons = {};
  for (const file of readdirSync(dir).filter((f) => f.endsWith(".svg"))) {
    // Only the root <svg> loses its 24px size, so the .ic-* class sets it: a <rect> inside
    // keeps its own width and height, or it draws nothing.
    // Ids take the icon's name as a prefix: several icons ship `id="a"` on their clip mask, and two
    // of them inline in one step would otherwise both point at the first mask in the page.
    const name = file.slice(0, -4);
    icons[name] = readFileSync(join(dir, file), "utf8")
      .replace(/<\?xml[^>]*>\s*/, "")
      .replace(/<svg\b[^>]*>/, (tag) => tag.replace(/\s(width|height)="[^"]*"/g, ""))
      .replace(/\bid="([^"]+)"/g, `id="${name}-$1"`)
      .replace(/url\(#([^)]+)\)/g, `url(#${name}-$1)`)
      .replace(/href="#([^"]+)"/g, `href="#${name}-$1"`)
      .trim();
  }
  writeFileSync(join(sceneDir, "icons.js"), `window.ICONS = ${JSON.stringify(icons)};\n`);
}

function newScene(args) {
  const [slug] = args;
  const from = flag(args, "from", "scene-template");
  if (!SLUG.test(slug ?? "") || !ASSET.test(from ?? ""))
    die("usage: tour.mjs new <kebab-case-slug-ending-in-tour> [--from <asset>]");
  const source = join(SKILL, "assets", `${from}.html`);
  if (!existsSync(source)) die(`asset not found: assets/${from}.html`);
  const dir = join(HOME, "scenes", slug);
  if (existsSync(dir)) die(`${dir} already exists: edit it instead`);
  mkdirSync(join(dir, "fonts"), { recursive: true });
  copyFileSync(source, join(dir, "index.html"));
  for (const font of readdirSync(join(SKILL, "assets", "fonts")))
    copyFileSync(join(SKILL, "assets", "fonts", font), join(dir, "fonts", font));
  writeIcons(dir);
  console.log(`SCENE ${join(dir, "index.html")}`);
}

function encode(ffmpeg, frames, fps, dither, gif) {
  // The frames are copied in play order, so the GIF can start on any frame of the loop.
  const tmp = mkdtempSync(join(tmpdir(), "animate-tour-"));
  try {
    frames.forEach((f, n) => copyFileSync(f, join(tmp, `${String(n).padStart(5, "0")}.png`)));
    const r = spawnSync(
      ffmpeg,
      [
        "-loglevel",
        "error",
        "-y",
        "-framerate",
        String(fps),
        "-i",
        join(tmp, "%05d.png"),
        "-filter_complex",
        `[0:v]split[a][b];[a]palettegen=stats_mode=full[p];[b][p]paletteuse=dither=${dither}`,
        "-loop",
        "0",
        gif,
      ],
      { stdio: "inherit" },
    );
    if (r.status !== 0) fail(`ffmpeg failed on ${gif}`);
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}

async function record(args) {
  const [slug] = args;
  const quality = flag(args, "quality", "light");
  const q = QUALITIES[quality];
  if (!SLUG.test(slug ?? "") || !q)
    die("usage: tour.mjs record <slug-ending-in-tour> [--quality light|high] [--steps N …]");
  const dir = join(HOME, "scenes", slug);
  if (!existsSync(join(dir, "index.html"))) die(`scene not found: ${dir}/index.html`);
  if (!existsSync(join(HOME, "node_modules", "playwright")))
    die("STUDIO_MISSING: run `tour.mjs prepare` first.");

  // The studio's own packages, so the browser and ffmpeg are the ones /bb:reel installed.
  const require = createRequire(join(HOME, "package.json"));
  const { chromium } = require("playwright");
  const ffmpeg = require("ffmpeg-static");
  writeIcons(dir); // keeps the scene's icons in step with the skill after an update

  // Everything is written to a staging folder beside the output, and lands only when the whole
  // record succeeded: a failure leaves the previous delivery whole, and a stale GIF still never
  // passes for the new one. The staging folder sits under out/ so the final move is a rename.
  const out = join(HOME, "out", slug, quality);
  mkdirSync(join(HOME, "out", slug), { recursive: true });
  const stage = mkdtempSync(join(HOME, "out", slug, `.${quality}-`));
  const work = mkdtempSync(join(tmpdir(), "animate-tour-frames-"));
  const partial = args.includes("--steps");

  const browser = await chromium.launch();
  const report = [];
  try {
    const page = await browser.newPage({
      viewport: { width: WIDTH, height: HEIGHT },
      deviceScaleFactor: q.scale,
    });
    const errors = [];
    page.on("pageerror", (e) => errors.push(e.message));
    await page.goto(pathToFileURL(join(dir, "index.html")).href);
    await page.evaluate(() => window.READY);
    if (errors.length) fail(`scene error: ${errors[0]}`);
    if (!(await page.evaluate(() => document.fonts.check("500 12px Poppins"))))
      console.warn("WARN: Poppins did not load; the GIF falls back to another font.");

    const durations = await page.evaluate(() => window.STEPS);
    const picked = partial
      ? [
          ...new Set(
            args
              .slice(args.indexOf("--steps") + 1)
              .filter((a) => /^\d+$/.test(a))
              .map((n) => Number(n) - 1)
              .filter((i) => i >= 0 && i < durations.length),
          ),
        ]
      : durations.map((_, i) => i);
    if (!picked.length) fail(`--steps must name steps between 1 and ${durations.length}`);

    const clip = { x: 0, y: 0, width: WIDTH, height: HEIGHT };
    const all = [];
    let firstStart = 0;
    for (const i of picked) {
      const n = Math.round(durations[i] * q.fps);
      const frames = [];
      for (let f = 0; f < n; f++) {
        await page.evaluate(([s, t]) => window.seekStep(s, t), [i, f / q.fps]);
        const file = join(work, `s${i}-${String(f).padStart(5, "0")}.png`);
        writeFileSync(file, await page.screenshot({ clip }));
        frames.push(file);
      }
      const missing = await page.evaluate(() => [...new Set(window.MISSING_ICONS)]);
      if (missing.length) fail(`icons not in the design system: ${missing.join(", ")}`);

      // The settled frame: every entrance done. It is the step's still, and the GIF opens on it,
      // because an email client that does not animate (Outlook desktop) shows the first frame only.
      const settled = Math.min(await page.evaluate((s) => window.settledAt(s), i), durations[i]);
      await page.evaluate(([s, t]) => window.seekStep(s, t), [i, settled]);
      const still = join(stage, `${slug}-step-${i + 1}.png`);
      writeFileSync(still, await page.screenshot({ clip }));
      const start = Math.min(n - 1, Math.ceil(settled * q.fps));
      if (all.length === 0) firstStart = start;

      const gif = join(stage, `${slug}-step-${i + 1}.gif`);
      encode(ffmpeg, [...frames.slice(start), ...frames.slice(0, start)], q.fps, q.dither, gif);
      report.push(still, gif);
      all.push(...frames);
    }
    // The full GIF is the whole tour, so only a record of every step writes it.
    if (!partial && picked.length > 1) {
      const gif = join(stage, `${slug}-full.gif`);
      encode(ffmpeg, [...all.slice(firstStart), ...all.slice(0, firstStart)], q.fps, q.dither, gif);
      report.push(gif);
    }

    if (partial) {
      // Iterating on one step replaces that step's files and keeps the rest of the delivery.
      mkdirSync(out, { recursive: true });
      for (const file of readdirSync(stage)) renameSync(join(stage, file), join(out, file));
    } else {
      rmSync(out, { recursive: true, force: true });
      renameSync(stage, out);
    }
  } finally {
    await browser.close();
    rmSync(work, { recursive: true, force: true });
    rmSync(stage, { recursive: true, force: true });
  }

  console.log(`OUT ${out} (${WIDTH * q.scale}x${HEIGHT * q.scale}, ${q.fps} fps)`);
  for (const staged of report) {
    const file = join(out, basename(staged));
    const mb = statSync(file).size / 1e6;
    const over = q.capMb && file.endsWith(".gif") && mb > q.capMb ? `  OVER ${q.capMb} MB` : "";
    console.log(`  ${basename(file)}  ${mb.toFixed(2)} MB${over}`);
  }
  if (partial && existsSync(join(out, `${slug}-full.gif`)))
    console.log(
      `NOTE ${slug}-full.gif predates this record: record without --steps to rebuild it.`,
    );
}

const [verb, ...args] = process.argv.slice(2);
if (verb === "prepare") prepare(args);
else if (verb === "new") newScene(args);
else if (verb === "record") await record(args).catch((e) => die(`record failed: ${e.message}`));
else die("usage: tour.mjs <prepare|new|record> [args…]", 2);
