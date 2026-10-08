// Runs one studio script: `node studio.mjs <render|stills|new-scene|ffmpeg|play> [args…]`.
// The skill pre-approves this file by its own path, so the permission rule cannot match a
// look-alike path; the verb list is what keeps it from running anything else.
import { spawnSync } from "node:child_process";
import { homedir } from "node:os";
import { join } from "node:path";

const VERBS = ["render", "stills", "new-scene", "ffmpeg", "play"];
const [verb, ...args] = process.argv.slice(2);
if (!VERBS.includes(verb)) {
  console.error(`usage: studio.mjs <${VERBS.join("|")}> [args…]`);
  process.exit(2);
}
const home = process.env.MOTION_HOME ?? join(homedir(), "Motion");
const r = spawnSync(process.execPath, [join(home, `${verb}.mjs`), ...args], { stdio: "inherit" });
process.exit(r.status ?? 1);
