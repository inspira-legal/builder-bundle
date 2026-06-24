# Unattended setup — ofc:digest-research as a daily Cloud Routine

A read-only morning brief that runs without your laptop. Same Cloud Routine
constraints as elsewhere: fresh clone, **no local files**, **no approval prompts
mid-run**, durable output only via a `claude/` branch commit or a connector.
Create via `/schedule` or claude.ai/code/routines — not a session `/loop`.

## 1. The queue lives in the repo

A Cloud Routine can't read a local `.research/` file. Commit the watch queue
(e.g. `research/WATCH.md`, one question per line; `#` comments and `| note`
allowed) so the fresh clone can read it with `build_queue.py`.

## 2. Delivery — pick ONE durable channel

- **Slack (recommended):** add the **Slack connector** at
  claude.ai/customize/connectors (the session `slack_*` MCP tools are NOT
  available in a routine). The routine posts the digest + delta. For
  "delta vs yesterday", read the channel's recent history rather than a local
  file.
- **Committed digest branch:** the routine writes `digests/YYYY-MM-DD.md` on a
  `claude/ofc:digest-research` branch and opens/updates a draft PR. Durable,
  diffable, accumulates in git — and the prior file is then available to diff
  against next run.

## 3. Enforce read-only (it is not the default)

A routine runs autonomously and can use any included connector's writes without
asking. So:

- Attach ONLY the delivery connector (Slack) — no GitHub-write/merge connector.
- Keep network on the **Trusted** preset (registries + the sources you research).
- Read-only is enforced by capability: with no write/merge connector attached, a
  stray write/merge command has nothing to call. That's the control, not a hook.

## 4. Schedule & cost

- Trigger: schedule, daily, an off-the-hour weekday-morning slot (1-hour minimum
  is easily met).
- Fan-out: keep `/ofc:research-topic` at **2–3 sub-agents** for the scheduled
  variant (multi-agent ≈ 15× tokens). No fan-out-in-a-loop before measuring.
- Routines draw down subscription usage and have a per-account daily run cap.
  Read actual usage at claude.ai after week one, then decide daily vs
  weekday-only.
