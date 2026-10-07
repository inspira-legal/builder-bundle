// node play.mjs <name>: opens out/<name>.mp4 in the system's default player.
// Without a desktop (a server, WSL) the opener fails; then it prints the path, which the skill hands over instead.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

const file = resolve(`out/${process.argv[2]}.mp4`);
if (!existsSync(file)) {
  console.error(`not found: ${file}`);
  process.exit(1);
}
const opener =
  { darwin: "open", win32: "explorer.exe", linux: "xdg-open" }[process.platform] ?? "xdg-open";
const r = spawnSync(opener, [file], { stdio: "ignore" });
// explorer.exe exits 1 even when it opened the file, so its status says nothing.
const opened = !r.error && (r.status === 0 || process.platform === "win32");
console.log(opened ? `opened ${file}` : `VIDEO ${file}`);
