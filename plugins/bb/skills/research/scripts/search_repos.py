#!/usr/bin/env python3
"""
Search GitHub for repositories matching multiple queries and/or topics,
deduplicate, filter by stars, and return a ranked list.

Requires:
  - `gh auth login` already set up

Usage:
  python search_repos.py "react state management" "redux alternatives"
  python search_repos.py --topic state-management --topic react
  python search_repos.py --limit 20 --language typescript --min-stars 500 "query"
"""

from __future__ import annotations

import json
import subprocess
import sys


DEFAULT_LIMIT = 15
PER_QUERY_LIMIT = 10
DEFAULT_MIN_STARS = 100

FIELDS = "fullName,description,stargazersCount,updatedAt,language,url"


def run_ok(cmd: list[str]) -> str | None:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else None


def search_repos(query: str, min_stars: int, language: str | None = None) -> list[dict]:
    cmd = [
        "gh", "search", "repos", query,
        "--json", FIELDS,
        "--limit", str(PER_QUERY_LIMIT),
        "--stars", f">={min_stars}",
    ]
    if language:
        cmd += ["--language", language]

    out = run_ok(cmd)
    if not out:
        return []

    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []


def search_by_topic(topic: str, min_stars: int, language: str | None = None) -> list[dict]:
    cmd = [
        "gh", "search", "repos",
        "--topic", topic,
        "--json", FIELDS,
        "--limit", str(PER_QUERY_LIMIT),
        "--stars", f">={min_stars}",
    ]
    if language:
        cmd += ["--language", language]

    out = run_ok(cmd)
    if not out:
        return []

    try:
        return json.loads(out)
    except json.JSONDecodeError:
        return []


def dedupe(all_repos: list[dict], limit: int) -> list[dict]:
    seen: dict[str, dict] = {}
    for repo in all_repos:
        name = repo.get("fullName", "")
        if name and name not in seen:
            seen[name] = repo

    return list(seen.values())[:limit]


def main() -> None:
    queries: list[str] = []
    topics: list[str] = []
    language: str | None = None
    limit = DEFAULT_LIMIT
    min_stars = DEFAULT_MIN_STARS

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--limit" and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        elif args[i] == "--language" and i + 1 < len(args):
            language = args[i + 1]
            i += 2
        elif args[i] == "--min-stars" and i + 1 < len(args):
            min_stars = int(args[i + 1])
            i += 2
        elif args[i] == "--topic" and i + 1 < len(args):
            topics.append(args[i + 1])
            i += 2
        else:
            queries.append(args[i])
            i += 1

    if not queries and not topics:
        print(json.dumps({"error": "No search queries or topics provided"}))
        sys.exit(1)

    all_repos: list[dict] = []
    for query in queries:
        all_repos.extend(search_repos(query, min_stars, language))
    for topic in topics:
        all_repos.extend(search_by_topic(topic, min_stars, language))

    results = dedupe(all_repos, limit)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
