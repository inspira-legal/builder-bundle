#!/usr/bin/env python3
"""
Render a maintenance digest from scan_repo.py output, with built-in
de-duplication so a recurring run never re-pings Slack or re-posts an identical
PR comment.

Reads the scan JSON (from --scan FILE or stdin) and an optional prior-state file
(--state FILE: a map of {pr_number: content_hash} from the last run). Emits ONE
JSON object to stdout:

  {
    "slack_markdown": "...",            # grouped digest, lowercase house style
    "changed": [142, 138],              # PR numbers whose state changed since last run
    "unchanged_count": 7,
    "new_state": {"142": "ab12…", …},   # persist this for the next run
    "comments": [                       # one sticky body per Dependabot PR (edit in place)
      {"number": 142, "marker": "<!-- bb:maintain-repo:pr-142 -->", "body": "…"}
    ]
  }

The content hash deliberately EXCLUDES the raw async mergeable/UNKNOWN fields and
keys on the settled signals (verdict, ci state, head sha, priority) so that
async-mergeability flapping cannot generate phantom "changed" rows. Merge is
never invoked — every output ends on "you merge".

Usage:
  python scan_repo.py --repo owner/name | python render_digest.py --state state.json
  python render_digest.py --scan scan.json --state state.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from typing import Any

MARKER = "<!-- bb:maintain-repo:pr-{n} -->"

SAFE = "yes"
NO = "no"
HUMAN = "needs-human"


def content_hash(pr: dict[str, Any]) -> str:
    verdict = pr.get("verdict") or {}
    key = {
        "merge_safe": verdict.get("merge_safe"),
        "ci": (pr.get("ci") or {}).get("state"),
        "head_sha": pr.get("head_sha"),
        "priority": pr.get("priority_label"),
        "semver": (pr.get("semver") or {}).get("class"),
    }
    blob = json.dumps(key, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def pr_line(pr: dict[str, Any]) -> str:
    n = pr.get("number")
    url = pr.get("url") or ""
    sv = pr.get("semver") or {}
    pkg = sv.get("package") or pr.get("untrusted_title", "")[:60]
    delta = f"{sv.get('from')}→{sv.get('to')}" if sv.get("from") else ""
    verdict = pr.get("verdict") or {}
    why = "; ".join((verdict.get("reasons") or [])[:2])
    notes = "; ".join((verdict.get("risk_notes") or [])[:1])
    prio = pr.get("priority_label", "")
    tail = " — ".join(x for x in [why, notes] if x)
    return f"• <{url}|#{n}> *{pkg}* {delta} · {prio}{(' — ' + tail) if tail else ''}"


def render_slack(scan: dict[str, Any], changed: set[int]) -> str:
    prs = scan.get("prs") or []
    repo = scan.get("repo", "")
    safe = [p for p in prs if (p.get("verdict") or {}).get("merge_safe") == SAFE]
    human = [p for p in prs if (p.get("verdict") or {}).get("merge_safe") == HUMAN]
    blocked = [p for p in prs if (p.get("verdict") or {}).get("merge_safe") == NO]

    lines: list[str] = []
    lines.append(f"*{repo}* — maintenance digest ({len(changed)} changed since last run)")
    if scan.get("dependabot_alert_count"):
        lines.append(f"_{scan['dependabot_alert_count']} open dependabot security alert(s)_")

    def section(title: str, items: list[dict[str, Any]]) -> None:
        shown = [p for p in items if p.get("number") in changed] if changed else items
        if not shown:
            return
        lines.append("")
        lines.append(f"*{title}*")
        for p in shown:
            lines.append(pr_line(p))

    section("prioritize & safe to merge (you merge)", safe)
    section("needs you", human)
    section("blocked", blocked)

    if not changed and prs:
        lines.append("")
        lines.append("_no state changes since the last run._")
    lines.append("")
    lines.append("_mergeable verdicts are decision-support. you merge — nothing here merges for you._")
    return "\n".join(lines)


def render_comment(pr: dict[str, Any]) -> str:
    n = pr.get("number")
    verdict = pr.get("verdict") or {}
    ms = verdict.get("merge_safe")
    sv = pr.get("semver") or {}
    badge = {SAFE: "safe to merge", HUMAN: "needs you", NO: "blocked"}.get(ms, ms)
    rows = [
        MARKER.format(n=n),
        "### maintenance triage",
        f"- **verdict:** {badge}",
        f"- **change:** `{sv.get('package') or '?'}` {sv.get('from')} → {sv.get('to')} ({sv.get('class')})",
        f"- **ci:** {(pr.get('ci') or {}).get('state')}",
        f"- **merge state:** {pr.get('merge_state') or 'unknown'}",
    ]
    reasons = verdict.get("reasons") or []
    if reasons:
        rows.append(f"- **why:** {', '.join(reasons)}")
    notes = verdict.get("risk_notes") or []
    if notes:
        rows.append(f"- **notes:** {'; '.join(notes)}")
    rows.append("")
    rows.append("_decision-support only — merge is a human action. ci-green reflects only what this PR's own workflows ran; major / maintainer-change updates still need a local sandboxed test._")
    return "\n".join(rows)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Render a de-duplicated maintenance digest (Slack + sticky PR comments).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--scan", default="-", help="Path to scan_repo.py JSON, or '-' for stdin.")
    p.add_argument("--state", default=None, help="Prior-state JSON {pr_number: hash} for dedupe.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    raw = sys.stdin.read() if args.scan == "-" else open(args.scan, encoding="utf-8").read()
    scan = json.loads(raw)

    if scan.get("schema_version") != 1:
        print(json.dumps({"error": f"unrecognized scan schema_version {scan.get('schema_version')}"}))
        return 1

    prior: dict[str, str] = {}
    if args.state:
        try:
            prior = json.loads(open(args.state, encoding="utf-8").read())
        except (OSError, json.JSONDecodeError):
            prior = {}

    new_state: dict[str, str] = {}
    changed: set[int] = set()
    comments: list[dict[str, Any]] = []

    for pr in scan.get("prs") or []:
        n = pr.get("number")
        if n is None:
            continue
        h = content_hash(pr)
        new_state[str(n)] = h
        if prior.get(str(n)) != h:
            changed.add(n)
        if pr.get("is_dependabot"):
            comments.append({"number": n, "marker": MARKER.format(n=n), "body": render_comment(pr)})

    out = {
        "slack_markdown": render_slack(scan, changed),
        "changed": sorted(changed),
        "unchanged_count": len(new_state) - len(changed),
        "new_state": new_state,
        "comments": comments,
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
