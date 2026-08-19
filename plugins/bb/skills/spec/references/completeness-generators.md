# Completeness generators

Run these during the adversarial pass to **manufacture questions** along the axes
omission hides in. They are a question factory, **not sections to fill**. Run
the generator, turn any unanswered case into a gray area, then discard the rest.
Apply only the axes the work actually touches; don't pad.

The goal isn't to answer every prompt for every feature; it's that the axes you
would have skipped become _explicit questions_ instead of silent omissions.

- **Input dimensions**: for each input, empty / zero / one / many / huge;
  malformed or wrong-type; missing or optional; untrusted / hostile. What's the
  outcome of each?
- **External outputs**: for everything the design reads or calls (a model, an
  index, the network, the filesystem, a DB, a subprocess): its **empty case**
  (zero results / no data), its **limit case** (exceeds a window / quota / size /
  rate), its **shape-change case** (format / dimension / schema / version drifts).
- **State & lifecycle**: first run vs repeat; create / update / delete /
  re-create; stale or cached state; what persists across runs and what must reset.
- **Failure & recovery**: each external call fails or times out; partial
  completion; crash mid-operation; idempotent on retry?; what's the rollback.
- **Concurrency**: two of these run at once; shared resource; race on the same
  record/file; ordering assumptions that may not hold.
- **Trust & security boundary**: where untrusted data enters and what it could do
  if hostile (injection, path traversal, overflow); who is authorized; whether
  anything sensitive gets logged or surfaced.
- **Data lifecycle**: migrating data already in the old shape; backward
  compatibility; retention and deletion.
- **Observability**: when it breaks in production, how do you find out; what's
  logged or surfaced; is failure silent.

For each case a generator raises, the test for whether it's load-bearing is the
same litmus from the behavior map: **does the wrong outcome contradict the
`why`?** If yes, the gate blocks on it.
