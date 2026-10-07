// node play.mjs <name>: opens out/<name>.mp4 in the system's default player.
// Without a desktop (a server, WSL) the opener fails; then it prints the path, which the skill hands over instead.
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

process.chdir(fileURLToPath(new URL(".", import.meta.url)));
const file = resolve(`out/${process.argv[2]}.mp4`);
if (!existsSync(file)) {
  console.error(`not found: ${file}`);
  process.exit(1);
}
const opener =
  { darwin: "open", win32: "explorer.exe", linux: "xdg-open" }[process.platform] ?? "xdg-open";
// Detached and unref'd: some xdg-open setups never exit, and waiting on them would hang the step.
const child = spawn(opener, [file], { stdio: "ignore", detached: true });
child.on("error", () => console.log(`VIDEO ${file}`));
child.on("spawn", () => {
  child.unref();
  console.log(`opened ${file}`);
});
