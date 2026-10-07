// node stills.mjs scenes/<name> t1 t2 ... -> out/<name>-at-<t>.png (quick critique without a full render)
import { chromium } from "playwright";
import { resolve, basename } from "node:path";
import { pathToFileURL } from "node:url";
const [dir, ...ts] = process.argv.slice(2);
const b = await chromium.launch(),
  p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
p.on("pageerror", (e) => console.error("pageerror", e.message));
await p.goto(pathToFileURL(resolve(dir, "index.html")).href);
await p.evaluate(() => window.READY);
for (const t of ts) {
  await p.evaluate((t) => window.seek(t), +t);
  await p.screenshot({ path: `out/${basename(resolve(dir))}-at-${t}.png` });
}
await b.close();
