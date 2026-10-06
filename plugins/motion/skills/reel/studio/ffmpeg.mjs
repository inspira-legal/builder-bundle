// npm run ffmpeg -- <args>: runs the bundled ffmpeg, so commands carry no shell substitution for the user to approve.
import ffmpeg from "ffmpeg-static";
import { spawnSync } from "node:child_process";

process.exit(spawnSync(ffmpeg, process.argv.slice(2), { stdio: "inherit" }).status ?? 1);
