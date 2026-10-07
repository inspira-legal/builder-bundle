// Prepares the workspace (~/Motion) the reel skill renders in, on macOS, Linux and Windows.
// Idempotent: it does real work only when the plugin version differs from the workspace's
// stamp, so it runs on every call and costs nothing once ready. Prints READY <path> on success.
// Node only, no shell: the same command runs from bash and from PowerShell.
import { spawnSync } from "node:child_process";
import { cpSync, existsSync, mkdirSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

if (+process.versions.node.split(".")[0] < 18) {
  console.log(
    "NODE_MISSING: Node 18+ is required; install Node LTS from https://nodejs.org and try again.",
  );
  process.exit(1);
}

const skillDir = fileURLToPath(new URL("..", import.meta.url));
const home = process.env.MOTION_HOME ?? join(homedir(), "Motion");
const stamp = join(home, ".studio-version");
const { version } = JSON.parse(
  readFileSync(join(skillDir, "../../.claude-plugin/plugin.json"), "utf8"),
);

if (existsSync(stamp) && readFileSync(stamp, "utf8").trim() === version) {
  console.log(`READY ${home}`);
  process.exit(0);
}
const firstRun = !existsSync(stamp);

const run = (cmd, args, opts = {}) => {
  // Windows refuses to spawn npm.cmd without a shell (CVE-2024-27980); the args are fixed, so the shell is safe here.
  const r = spawnSync(cmd, args, {
    cwd: home,
    stdio: "inherit",
    shell: process.platform === "win32" && cmd === "npm",
    ...opts,
  });
  return r.status === 0;
};
const fail = (msg) => {
  console.log(`FAILED: ${msg}`);
  process.exit(1);
};

console.log(`→ Preparing the studio at ${home} (first time takes a few minutes)`);
mkdirSync(home, { recursive: true });
// ponytail: merges into the workspace; the engine and the bundled reference scenes are refreshed, the person's own scenes and out/ stay.
cpSync(join(skillDir, "studio"), home, { recursive: true });

if (!run("npm", ["install", "--no-fund", "--no-audit", "--loglevel=error"]))
  fail("npm install (network or proxy?)");
// Headless shell only: the render never opens a window, and the full Chromium is several times bigger.
if (
  !run(process.execPath, ["node_modules/playwright/cli.js", "install", "chromium", "--only-shell"])
)
  fail("Chromium download (network or proxy?)");

if (firstRun) {
  console.log("→ Smoke test");
  const r = spawnSync(process.execPath, ["render.mjs", "scenes/demo", "--fps", "2"], {
    cwd: home,
    encoding: "utf8",
  });
  const out = `${r.stdout}${r.stderr}`;
  if (r.status !== 0 && /missing dependencies|install-deps|shared libraries/i.test(out)) {
    console.log(
      "DEPS_MISSING: Chromium needs system libraries. Run once: sudo npx playwright install-deps chromium",
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
