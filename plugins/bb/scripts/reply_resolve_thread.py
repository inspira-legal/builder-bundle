#!/usr/bin/env python3
"""
Reply to a PR review thread and/or resolve it via `gh api graphql`.

Thread IDs come from fetch_comments.py output (review_threads[].id).

Usage:
  python reply_resolve_thread.py --thread-id <id> --body "Fixed in abc1234"
  python reply_resolve_thread.py --thread-id <id> --body "..." --no-resolve
  python reply_resolve_thread.py --thread-id <id>            # resolve only
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

REPLY_MUTATION = """\
mutation($threadId: ID!, $body: String!) {
  addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $threadId, body: $body}) {
    comment { id url }
  }
}
"""

RESOLVE_MUTATION = """\
mutation($threadId: ID!) {
  resolveReviewThread(input: {threadId: $threadId}) {
    thread { id isResolved }
  }
}
"""


def _run(cmd: list[str], stdin: str | None = None) -> str:
    p = subprocess.run(cmd, input=stdin, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"Command failed: {' '.join(cmd)}\n{p.stderr}")
    return p.stdout


def _graphql(query: str, variables: dict[str, str]) -> dict[str, Any]:
    cmd = ["gh", "api", "graphql", "-F", "query=@-"]
    for key, value in variables.items():
        cmd += ["-F", f"{key}={value}"]
    payload = json.loads(_run(cmd, stdin=query))
    if payload.get("errors"):
        sys.exit(f"GitHub GraphQL errors:\n{json.dumps(payload['errors'], indent=2)}")
    return payload["data"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--thread-id", required=True, help="Review thread node ID (review_threads[].id from fetch_comments.py)")
    ap.add_argument("--body", help="Reply body (markdown). Omit to resolve without replying.")
    ap.add_argument("--no-resolve", action="store_true", help="Reply only; leave the thread unresolved")
    args = ap.parse_args()

    if not args.body and args.no_resolve:
        sys.exit("Nothing to do: no --body and --no-resolve given")

    result: dict[str, Any] = {}
    if args.body:
        result["reply"] = _graphql(REPLY_MUTATION, {"threadId": args.thread_id, "body": args.body})
    if not args.no_resolve:
        result["resolve"] = _graphql(RESOLVE_MUTATION, {"threadId": args.thread_id})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
