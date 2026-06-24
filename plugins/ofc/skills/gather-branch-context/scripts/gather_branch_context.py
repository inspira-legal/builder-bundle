#!/usr/bin/env python3
"""
Gather branch context relative to main/base: commit log, full diff,
file change summary, and uncommitted changes.

Usage:
  python gather_branch_context.py
  python gather_branch_context.py --repo /path/to/repo
  python gather_branch_context.py --base develop
"""

from __future__ import annotations

import json
import subprocess
import sys


def run_ok(cmd: list[str], cwd: str | None = None) -> str | None:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else None


def find_git_root(start: str) -> str | None:
    return run_ok(["git", "rev-parse", "--show-toplevel"], cwd=start)


def get_base_branch(cwd: str) -> str | None:
    return run_ok(
        ["gh", "repo", "view", "--json", "defaultBranchRef", "--jq", ".defaultBranchRef.name"],
        cwd=cwd,
    )


def main() -> None:
    repo_path = "."
    base_override = None

    args = sys.argv[1:]
    while args:
        if args[0] == "--repo" and len(args) > 1:
            repo_path = args[1]
            args = args[2:]
        elif args[0] == "--base" and len(args) > 1:
            base_override = args[1]
            args = args[2:]
        else:
            args = args[1:]

    git_root = find_git_root(repo_path)
    if not git_root:
        print(json.dumps({"error": "Not inside a git repository"}))
        sys.exit(1)

    cwd = git_root
    branch = run_ok(["git", "branch", "--show-current"], cwd=cwd)
    base = base_override or get_base_branch(cwd) or "main"

    # Ensure we have the base branch locally for diffing
    run_ok(["git", "fetch", "origin", base], cwd=cwd)

    # Merge base — the exact commit where branch diverged
    merge_base = run_ok(["git", "merge-base", f"origin/{base}", "HEAD"], cwd=cwd)

    result: dict = {
        "git_root": cwd,
        "branch": branch,
        "base_branch": base,
        "merge_base": merge_base,
        "uncommitted_changes": run_ok(["git", "status", "--short"], cwd=cwd) or "",
    }

    if merge_base:
        result["commit_log"] = run_ok(
            ["git", "log", "--oneline", f"{merge_base}..HEAD"], cwd=cwd
        ) or ""
        result["commit_count"] = len(result["commit_log"].splitlines()) if result["commit_log"] else 0
        result["diff_stat"] = run_ok(
            ["git", "diff", f"{merge_base}...HEAD", "--stat"], cwd=cwd
        ) or ""
        result["files_changed"] = run_ok(
            ["git", "diff", f"{merge_base}...HEAD", "--name-status"], cwd=cwd
        ) or ""
        result["full_diff"] = run_ok(
            ["git", "diff", f"{merge_base}...HEAD"], cwd=cwd
        ) or ""

        # Truncate full diff if massive (keep under 100k chars)
        if len(result["full_diff"]) > 100000:
            result["full_diff"] = result["full_diff"][:100000] + "\n\n... (diff truncated, too large)"
            result["diff_truncated"] = True
    else:
        result["error"] = f"Could not find merge base between origin/{base} and HEAD"
        result["commit_log"] = ""
        result["diff_stat"] = ""
        result["files_changed"] = ""
        result["full_diff"] = ""

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
