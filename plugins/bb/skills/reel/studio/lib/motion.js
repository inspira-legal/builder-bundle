// Closed-form springs: pure functions of t, so seek(t) works for any frame without simulating earlier ones.
(function (g) {
  const PRESETS = {
    snappy: { w: 22, z: 0.75 }, // buttons, toggles, leading edges
    default: { w: 12, z: 0.8 }, // cards, containers, camera
    heavy: { w: 7, z: 0.9 }, // big type, 3D objects, logo lockups
    playful: { w: 14, z: 0.45 }, // mascots, stickers (visible overshoot)
  };

  // 0 -> 1 step response at time t (seconds since the change)
  function spring(t, preset = "default") {
    if (t <= 0) return 0;
    const { w, z } = typeof preset === "string" ? PRESETS[preset] : preset;
    if (z >= 1) return 1 - Math.exp(-w * t) * (1 + w * t);
    const wd = w * Math.sqrt(1 - z * z);
    return 1 - Math.exp(-z * w * t) * (Math.cos(wd * t) + ((z * w) / wd) * Math.sin(wd * t));
  }

  // Value with several targets over time: one spring per change, each from its own start time.
  // track(t, 0, [[0.5, 100], [1.2, 40]], 'snappy')
  function track(t, initial, changes, preset = "default") {
    let v = initial,
      prev = initial;
    for (const [t0, target] of changes) {
      v += (target - prev) * spring(t - t0, preset);
      prev = target;
    }
    return v;
  }

  const lerp = (a, b, k) => a + (b - a) * k;
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  // Beat grid: time in seconds of beat n at a given BPM
  const beat = (n, bpm = 120) => (n * 60) / bpm;

  g.motion = { spring, track, lerp, clamp, beat, PRESETS };
})(globalThis);
