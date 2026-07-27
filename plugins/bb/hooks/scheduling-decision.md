# Scheduling & trigger decision table

Pick the mechanism by **durability** and **what wakes it**. The most common
mistake is scheduling an AFK overnight job as a session `/loop` and waking to
nothing — `/loop` is not durable.

| Mechanism                  | Wakes on                                         | Runs where                 | Min interval | Survives laptop closed?       | Durable state                                  | Notes                                                                                                                                                   |
| -------------------------- | ------------------------------------------------ | -------------------------- | ------------ | ----------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **bare/fixed `/loop`**     | a self-paced interval, in-session                | your machine, open session | 1 min        | **No**                        | session only                                   | auto-expires 7 days; fires only while running **and idle**; no catch-up for missed fires; a fresh conversation clears it. The "I'm at my desk" watcher. |
| **Desktop scheduled task** | a cron time                                      | your machine               | 1 min        | **No** (dies on sleep/reboot) | local files                                    | needs local files/tools; runs on next launch if closed when due. On Windows, sleep kills it.                                                            |
| **Cloud Routine**          | a cron time OR a GitHub event OR an API `/fire`  | Anthropic infra            | 1 hr         | **Yes**                       | a `claude/` branch commit or a connector write | fresh clone, **no local files**, **no approval prompts mid-run**, per-account daily run cap. The only true AFK option.                                  |
| **Channels**               | a pushed webhook (CI, CodeRabbit, error tracker) | an open local session      | event-driven | No                            | session                                        | pushes an event into a live session where your files/debugging context are loaded; sender allowlist is the gate.                                        |
| **`/goal`**                | turn-after-turn until a condition holds          | current session            | n/a          | No                            | session                                        | "keep going until CI is green and threads resolved" — a linear never-ending loop, not a scheduler.                                                      |
| **Monitor tool**           | each line of a background command's output       | current session            | n/a          | No                            | session                                        | event-driven in-session watching; replaces a foreground `--watch`. "Silence is not success" — alert on every terminal state.                            |

## How to pick

- **Needs to run while my laptop is closed** → Cloud Routine. Accept: no local
  files (commit state or use a connector), no mid-run approval prompts (so
  withhold irreversible capability — run the routine with a token that has no
  merge/branch-push permission and no merge-capable connector).
- **React the instant a PR/CI/bot event happens, AFK** → Cloud Routine with a
  `pull_request` (or API `/fire`) trigger. Beats polling on latency and cost.
- **React the instant an event happens, but I'm at my desk with context loaded**
  → Channels (push the webhook into the live session).
- **Watch a live PR/build while I work** → bare `/loop` or the Monitor tool.
- **Drive one task to a finish line in this session** → `/goal`.
- **Needs my local checkout / uncommitted files** → Desktop scheduled task (and
  accept the machine-must-stay-awake tradeoff).
