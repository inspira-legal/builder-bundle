// Tiny synth: kick on every beat, hat on offbeats, written as 16-bit mono WAV on the same timeline as the picture.
import { writeFileSync } from "node:fs";
export function synthBeat(file, seconds, bpm = 120, ticks = [], sr = 44100) {
  const n = Math.floor(seconds * sr),
    buf = new Float32Array(n),
    step = 60 / bpm;
  for (let b = 0; b * step < seconds; b++) {
    const s0 = Math.floor(b * step * sr);
    for (let i = 0; i < sr * 0.25 && s0 + i < n; i++) {
      // kick: falling sine
      const t = i / sr;
      buf[s0 + i] +=
        Math.sin(2 * Math.PI * (120 * Math.exp(-t * 18) + 40) * t) * Math.exp(-t * 9) * 0.8;
    }
    const h0 = s0 + Math.floor((step * sr) / 2);
    for (let i = 0; i < sr * 0.05 && h0 + i < n; i++)
      buf[h0 + i] += (Math.random() * 2 - 1) * Math.exp((-i / sr) * 90) * 0.15;
  }
  for (const tk of ticks) {
    // UI click: short bright blip
    const s0 = Math.floor(tk * sr);
    for (let i = 0; i < sr * 0.04 && s0 + i < n; i++) {
      const t = i / sr;
      buf[s0 + i] += Math.sin(2 * Math.PI * 2400 * t) * Math.exp(-t * 160) * 0.3;
    }
  }
  const out = Buffer.alloc(44 + n * 2);
  out.write("RIFF", 0);
  out.writeUInt32LE(36 + n * 2, 4);
  out.write("WAVEfmt ", 8);
  out.writeUInt32LE(16, 16);
  out.writeUInt16LE(1, 20);
  out.writeUInt16LE(1, 22);
  out.writeUInt32LE(sr, 24);
  out.writeUInt32LE(sr * 2, 28);
  out.writeUInt16LE(2, 32);
  out.writeUInt16LE(16, 34);
  out.write("data", 36);
  out.writeUInt32LE(n * 2, 40);
  for (let i = 0; i < n; i++)
    out.writeInt16LE(Math.round(Math.max(-1, Math.min(1, buf[i])) * 32767), 44 + i * 2);
  writeFileSync(file, out);
}
