import assert from "node:assert";
import "../lib/motion.js";
const { spring, track } = globalThis.motion;
assert.equal(spring(0), 0);
assert(Math.abs(spring(5, "snappy") - 1) < 1e-6, "settles at 1");
assert(
  Math.max(...Array.from({ length: 200 }, (_, i) => spring(i / 100, "playful"))) > 1,
  "playful overshoots",
);
assert.equal(track(0, 10, [[1, 50]]), 10);
assert(
  Math.abs(
    track(9, 10, [
      [1, 50],
      [2, 20],
    ]) - 20,
  ) < 1e-6,
  "ends at last target",
);
console.log("motion ok");
