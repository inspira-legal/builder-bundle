import assert from "node:assert";
import { mkdtempSync, readFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { synthSfx } from "./audio.mjs";

const dir = mkdtempSync(join(tmpdir(), "sfx-test-"));
const f = join(dir, "sfx.wav");
try {
  const events = [
    { t: 0.5, kind: "click" },
    { t: 1, kind: "type", dur: 0.4 },
    { t: 2, kind: "pop" },
  ];
  synthSfx(f, 3, events);
  const b = readFileSync(f);
  assert.equal(b.length, 44 + 3 * 44100 * 2, "WAV holds seconds * sr samples");
  const peak = (t0, t1) => {
    let m = 0;
    for (let i = Math.floor(t0 * 44100); i < Math.floor(t1 * 44100); i++)
      m = Math.max(m, Math.abs(b.readInt16LE(44 + i * 2)));
    return m;
  };
  for (const e of events) assert(peak(e.t, e.t + 0.1) > 500, `${e.kind} is audible at ${e.t}s`);
  assert.equal(peak(2.5, 3), 0, "silent between events");
  synthSfx(f, 3, events);
  assert(readFileSync(f).equals(b), "deterministic");
  assert.throws(() => synthSfx(f, 1, [{ t: 0, kind: "typing" }]), /unknown SFX kind/);
  synthSfx(f, 1, [{ t: 0, kind: "type", dur: Infinity }]); // must end: dur is bounded by the film
} finally {
  rmSync(dir, { recursive: true, force: true });
}
