# Unattended addendum (BB_UNATTENDED)

This run is **unattended** — no human is watching, and a prompt that waits for an
answer hangs the run forever. The frame below is added on top of the operating
frame for this run only.

- **Never `AskUserQuestion`.** Any skill that would ask a question instead picks
  the documented lean (the recommended option it would have led with), records
  the choice in its output/commit/PR, and proceeds. A surfaced decision becomes a
  logged decision, not a blocking prompt.
- **The lean covers this run's own work** — which fix to take, which documented
  destination to use. Output lands where the run already writes: its own draft PR,
  its threads, its report. Outward posting is out of reach by provisioning (App
  scoped to this repo, no outward connector — see the routine setup docs), so a
  skipped question has nowhere else to go.
- **`ship` opens a draft PR and resolves it.** Destination is fixed — a **draft**
  PR on a `claude/` branch, no destination question. Then watch it **to
  resolution**: green CI and handled review-bot comments/threads (reply, fix,
  push to the `claude/` branch, resolve). The watch is bounded by the **run
  budget**, not a human stop — it ends when the PR is resolved or the budget is
  spent, under two caps: the CI fix cap (3 cycles, known-flake only) and a
  comment-round cap (a thread a bot re-opens after a pushed fix+reply twice halts,
  noted on the draft). A persistently-red check or an unsatisfiable bot leaves the
  draft with the blocker written in and reports — it does not loop.
- **`implement` caps its gate retries** at 3 on known-flake signatures only; an
  unrecoverable failure opens the draft PR with the blocker in its description and
  exits, rather than improvising past the brief.
- **Never-merge holds regardless of this frame.** Merge and protected-branch push
  stay out of reach because the routine's token is capability-scoped (no
  merge/branch-push permission) and branch protection backs it server-side. This
  addendum governs interaction and PR shape only — it is **not** the safety
  boundary, so never treat it as one and never attempt a merge or a protected push
  on the strength of being unattended.
