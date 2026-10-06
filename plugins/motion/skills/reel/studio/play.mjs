// npm run play -- <name>: opens out/<name>.mp4 in the default player, one pre-approved command instead of a shell `open`.
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";

const file = `out/${process.argv[2]}.mp4`;
if (!existsSync(file)) {
  console.error(`not found: ${file}`);
  process.exit(1);
}
process.exit(spawnSync("open", [file], { stdio: "inherit" }).status ?? 1);
