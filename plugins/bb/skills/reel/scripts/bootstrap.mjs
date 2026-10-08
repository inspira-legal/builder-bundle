// Prepares the workspace (~/Motion) the reel skill renders in, on macOS, Linux and Windows.
// Idempotent: it does real work only when the bundled studio differs from what the workspace
// last received, so it runs on every call and costs nothing once ready. Prints READY <path>.
// Node only, no shell: the same command runs from bash and from PowerShell.
// `--force` reinstalls even when the workspace looks ready (a cleaned cache, a broken install).
import { spawnSync } from "node:child_process";
import { createHash } from "node:crypto";
import {
  cpSync,
  existsSync,
  mkdirSync,
  readdirSync,
  readFileSync,
  statSync,
  writeFileSync,
} from "node:fs";
import { homedir } from "node:os";
import { join, relative } from "node:path";
import { fileURLToPath } from "node:url";

// Playwright 1.63, pinned in the lock, requires Node 20.
if (+process.versions.node.split(".")[0] < 20) {
  console.log(
    "NODE_MISSING: Node 20+ is required; install Node LTS from https://nodejs.org and try again.",
  );
  process.exit(1);
}
// ffmpeg-static ships no Windows ARM binary, so the install would fail looking like a network error.
if (process.platform === "win32" && process.arch === "arm64") {
  console.log(
    "WINDOWS_ARM: install the x64 build of Node LTS from https://nodejs.org (it runs on Windows ARM) and try again.",
  );
  process.exit(1);
}

const studio = fileURLToPath(new URL("../studio", import.meta.url));
const home = process.env.MOTION_HOME ?? join(homedir(), "Motion");
const stamp = join(home, ".studio-version");
const force = process.argv.includes("--force");

// The stamp is a hash of the bundled studio, not a version number: any change to the studio
// reaches people on the next call, with no version to remember to bump.
const files = (dir) =>
  readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? files(join(dir, e.name)) : [join(dir, e.name)],
  );
const hash = createHash("sha256");
for (const f of files(studio).sort()) hash.update(relative(studio, f)).update(readFileSync(f));
const version = hash.digest("hex").slice(0, 16);

const ready = () => existsSync(stamp) && readFileSync(stamp, "utf8").trim() === version;
if (!force && ready() && existsSync(join(home, "node_modules/playwright"))) {
  console.log(`READY ${home}`);
  process.exit(0);
}
const firstRun = !existsSync(stamp);

const run = (cmd, args) => {
  // Windows refuses to spawn npm.cmd without a shell (CVE-2024-27980); the args are fixed, so the shell is safe here.
  const r = spawnSync(cmd, args, {
    cwd: home,
    stdio: "inherit",
    shell: process.platform === "win32" && cmd === "npm",
  });
  return r.status === 0;
};
const fail = (msg) => {
  console.log(`FAILED: ${msg}`);
  process.exit(1);
};

console.log(`→ Preparing the studio at ${home} (first time takes a few minutes)`);
mkdirSync(join(home, "scenes"), { recursive: true });
// The engine is refreshed on every update; the person's scenes and out/ are never touched, and the
// bundled example scenes are seeded only when missing, so an edited example survives an update.
cpSync(studio, home, {
  recursive: true,
  filter: (src) => relative(studio, src).split(/[\\/]/)[0] !== "scenes",
});
for (const scene of readdirSync(join(studio, "scenes"))) {
  if (!existsSync(join(home, "scenes", scene)))
    cpSync(join(studio, "scenes", scene), join(home, "scenes", scene), { recursive: true });
}

if (!run("npm", ["install", "--no-fund", "--no-audit", "--loglevel=error"]))
  fail("npm install (network or proxy?)");
// Headless shell only: the render never opens a window, and the full Chromium is several times bigger.
if (
  !run(process.execPath, ["node_modules/playwright/cli.js", "install", "chromium", "--only-shell"])
)
  fail("Chromium download (network or proxy?)");

if (firstRun || force) {
  console.log("→ Smoke test");
  const r = spawnSync(process.execPath, ["render.mjs", "scenes/demo", "--fps", "2"], {
    cwd: home,
    encoding: "utf8",
  });
  const out = `${r.stdout}${r.stderr}`;
  if (r.status !== 0 && /missing dependencies|install-deps|shared libraries/i.test(out)) {
    // sudo resets PATH, which hides a Node from nvm/fnm/volta; running from the studio uses its pinned Playwright.
    console.log(
      `DEPS_MISSING: Chromium needs system libraries (Debian/Ubuntu). Run once: cd "${home}" && sudo env "PATH=$PATH" npx playwright install-deps chromium`,
    );
    process.exit(1);
  }
  const mp4 = join(home, "out/demo.mp4");
  if (r.status !== 0 || !existsSync(mp4) || statSync(mp4).size === 0)
    fail(`smoke test render\n${out.slice(-1500)}`);
}

// Written last: a run that failed halfway retries on the next call.
writeFileSync(stamp, version);
console.log(`READY ${home}`);
