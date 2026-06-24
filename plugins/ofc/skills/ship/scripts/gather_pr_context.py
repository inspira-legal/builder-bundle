#!/usr/bin/env python3
"""
Gather all context needed to open a PR: branch info, base branch,
commit history, diff stats, uncommitted changes, and PR template.

Requires:
  - `gh auth login` already set up
  - inside a git repository

Usage:
  python gather_pr_context.py
  python gather_pr_context.py --repo /path/to/repo
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: str | None = None) -> tuple[int, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout.strip()


def run_ok(cmd: list[str], cwd: str | None = None) -> str | None:
    code, out = run(cmd, cwd=cwd)
    return out if code == 0 else None


def find_git_root(start: str) -> str | None:
    out = run_ok(["git", "rev-parse", "--show-toplevel"], cwd=start)
    return out


def get_branch(cwd: str) -> str | None:
    return run_ok(["git", "branch", "--show-current"], cwd=cwd)


def get_upstream(cwd: str) -> str | None:
    return run_ok(
        ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
        cwd=cwd,
    )


def get_base_branch(cwd: str) -> str | None:
    return run_ok(
        ["gh", "repo", "view", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"],
        cwd=cwd,
    )


def get_commit_log(base: str, cwd: str) -> str | None:
    return run_ok(["git", "log", "--oneline", f"{base}..HEAD"], cwd=cwd)


def get_diff_stat(base: str, cwd: str) -> str | None:
    return run_ok(["git", "diff", f"{base}...HEAD", "--stat"], cwd=cwd)


def get_status(cwd: str) -> str | None:
    return run_ok(["git", "status", "--short"], cwd=cwd)


def find_pr_template(cwd: str) -> str | None:
    candidates = [
        ".github/pull_request_template.md",
        ".github/PULL_REQUEST_TEMPLATE.md",
        "pull_request_template.md",
        "PULL_REQUEST_TEMPLATE.md",
    ]
    for candidate in candidates:
        path = Path(cwd) / candidate
        if path.is_file():
            return path.read_text()

    # Check template directory
    template_dir = Path(cwd) / ".github" / "PULL_REQUEST_TEMPLATE"
    if template_dir.is_dir():
        templates = sorted(template_dir.glob("*.md"))
        if templates:
            return templates[0].read_text()

    return None


def main() -> None:
    repo_path = "."
    if len(sys.argv) > 2 and sys.argv[1] == "--repo":
        repo_path = sys.argv[2]

    git_root = find_git_root(repo_path)
    if not git_root:
        print(json.dumps({"error": "Not inside a git repository"}))
        sys.exit(1)

    cwd = git_root
    branch = get_branch(cwd)
    upstream = get_upstream(cwd)
    base = get_base_branch(cwd)
    status = get_status(cwd)

    result: dict = {
        "git_root": cwd,
        "branch": branch,
        "upstream": upstream,
        "base_branch": base,
        "uncommitted_changes": status or "",
    }

    if base:
        result["commit_log"] = get_commit_log(base, cwd) or ""
        result["diff_stat"] = get_diff_stat(base, cwd) or ""
    else:
        result["commit_log"] = ""
        result["diff_stat"] = ""
        result["warning"] = "Could not detect base branch"

    template = find_pr_template(cwd)
    if template:
        result["pr_template"] = template

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
