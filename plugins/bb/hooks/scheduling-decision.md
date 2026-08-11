# Scheduling & trigger decision table

Pick the mechanism by **durability** and **what wakes it**. The most common
mistake is scheduling an overnight job as a session `/loop` and waking to
nothing — `/loop` is not durable.

| Mechanism                  | Wakes on                                         | Runs where                 | Min interval | Durable state | Notes                                                                                                                                                   |
| -------------------------- | ------------------------------------------------ | -------------------------- | ------------ | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **bare/fixed `/loop`**     | a self-paced interval, in-session                | your machine, open session | 1 min        | session only  | auto-expires 7 days; fires only while running **and idle**; no catch-up for missed fires; a fresh conversation clears it. The "I'm at my desk" watcher. |
| **Desktop scheduled task** | a cron time                                      | your machine               | 1 min        | local files   | needs local files/tools; runs on next launch if closed when due. On Windows, sleep kills it.                                                            |
| **Channels**               | a pushed webhook (CI, CodeRabbit, error tracker) | an open local session      | event-driven | session       | pushes an event into a live session where your files/debugging context are loaded; sender allowlist is the gate.                                        |
| **`/goal`**                | turn-after-turn until a condition holds          | current session            | n/a          | session       | "keep going until CI is green and threads resolved" — a linear never-ending loop, not a scheduler.                                                      |
| **Monitor tool**           | each line of a background command's output       | current session            | n/a          | session       | event-driven in-session watching; replaces a foreground `--watch`. "Silence is not success" — alert on every terminal state.                            |

## How to pick

- **React the instant an event happens, with my desk context loaded** → Channels
  (push the webhook into the live session).
- **Watch a live PR/build while I work** → bare `/loop` or the Monitor tool.
- **Drive one task to a finish line in this session** → `/goal`.
- **Needs my local checkout / uncommitted files** → Desktop scheduled task (and
  accept the machine-must-stay-awake tradeoff).
