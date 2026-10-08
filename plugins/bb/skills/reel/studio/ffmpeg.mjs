// node ffmpeg.mjs frames <video> [fps]: extracts frames of a reference video into out/ref-NNN.png.
// The one ffmpeg use the skill has, on purpose: a pre-approved command that took any ffmpeg
// argument could overwrite (-y) or fetch (-i <url>) anything, if text on a page steered the model.
import ffmpeg from "ffmpeg-static";
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import { resolve } from "node:path";
import { fileURLToPath } from "node:url";

const [cmd, video, fps = "2"] = process.argv.slice(2);
const input = video && resolve(video); // resolved before the chdir, so a path relative to where the person is works
if (cmd !== "frames" || !input || !existsSync(input) || !/^\d+(\.\d+)?$/.test(fps)) {
  console.error("usage: node ffmpeg.mjs frames <local-video-file> [fps]");
  process.exit(1);
}
process.chdir(fileURLToPath(new URL(".", import.meta.url)));
mkdirSync("out", { recursive: true });
const r = spawnSync(
  ffmpeg,
  ["-loglevel", "error", "-y", "-i", input, "-vf", `fps=${fps}`, "out/ref-%03d.png"],
  { stdio: "inherit" },
);
if (r.status === 0) console.log("out/ref-NNN.png");
process.exit(r.status ?? 1);
