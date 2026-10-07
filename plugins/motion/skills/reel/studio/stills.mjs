// node stills.mjs scenes/<name> t1 t2 ... [--w 1920 --h 1080] -> out/<name>-at-<t>.png (quick critique without a full render)
// Runs from any folder: paths resolve against the studio.
import { chromium } from "playwright";
import { mkdirSync } from "node:fs";
import { resolve, basename } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

process.chdir(fileURLToPath(new URL(".", import.meta.url)));
const args = process.argv.slice(2);
const opt = (k, d) => (args.includes(`--${k}`) ? +args.splice(args.indexOf(`--${k}`), 2)[1] : d);
const w = opt("w", 1920),
  h = opt("h", 1080);
const [dir, ...ts] = args;
mkdirSync("out", { recursive: true });
const b = await chromium.launch(),
  p = await b.newPage({ viewport: { width: w, height: h } });
p.on("pageerror", (e) => console.error("pageerror", e.message));
await p.goto(pathToFileURL(resolve(dir, "index.html")).href);
await p.evaluate(() => window.READY);
for (const t of ts) {
  await p.evaluate((t) => window.seek(t), +t);
  await p.screenshot({ path: `out/${basename(resolve(dir))}-at-${t}.png` });
}
await b.close();
