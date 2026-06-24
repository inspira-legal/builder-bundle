#!/usr/bin/env python3
"""
Parse a research-watch queue file into a structured JSON list, so a scheduled
ofc:digest-research run reloads its spec deterministically (zero tokens) on each
fire instead of free-associating new topics.

Queue file format (one entry per line; blank lines and # comments ignored):

    # competitors
    what did vercel ship this week? | sources: changelog, blog
    new issues/releases on owner/repo
    track: claude code routines changes

A trailing "| ..." segment is captured verbatim as an untrusted note (display
only). Emits {schema_version, count, entries:[{id, question, untrusted_note}]}.

Usage:
  python build_queue.py --queue .research/watch/main/WATCH.md
"""

from __future__ import annotations

import argparse
import json
import sys

SCHEMA_VERSION = 1


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Parse a research-watch queue file into JSON.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--queue", required=True, help="Path to the queue/WATCH.md file.")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    try:
        lines = open(args.queue, encoding="utf-8").read().splitlines()
    except OSError as e:
        print(json.dumps({"error": f"could not read queue: {e}", "entries": [], "count": 0}))
        return 1

    entries = []
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        question, _, note = line.partition("|")
        entries.append(
            {
                "id": len(entries) + 1,
                "question": question.strip(),
                "untrusted_note": note.strip()[:500],
            }
        )

    print(json.dumps({"schema_version": SCHEMA_VERSION, "count": len(entries), "entries": entries}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
