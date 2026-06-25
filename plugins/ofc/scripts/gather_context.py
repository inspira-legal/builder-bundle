#!/usr/bin/env python3
"""
Gather branch context relative to its base: branch/upstream, base + merge-base,
commit log, diff stat, changed files, full diff, uncommitted changes, and (for PR
creation) the repo's PR template. Superset consumed by both /ofc:ship (PR creation)
and /ofc:gather-branch-context (branch summary).

Requires:
  - inside a git repository
  - `gh auth login` for base-branch detection and PR template (falls back to "main")

Usage:
  python gather_context.py
  python gather_context.py --repo /path/to/repo
  python gather_context.py --base develop
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

MAX_DIFF_CHARS = 100000


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


def resolve_merge_base(base: str, cwd: str) -> tuple[str | None, str | None]:
    """Return (merge_base_sha, ref_used). Prefer origin/<base>, fall back to local <base>."""
    run_ok(["git", "fetch", "origin", base], cwd=cwd)  # best-effort; offline is fine
    for ref in (f"origin/{base}", base):
        mb = run_ok(["git", "merge-base", ref, "HEAD"], cwd=cwd)
        if mb:
            return mb, ref
    return None, None


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

    template_dir = Path(cwd) / ".github" / "PULL_REQUEST_TEMPLATE"
    if template_dir.is_dir():
        templates = sorted(template_dir.glob("*.md"))
        if templates:
            return templates[0].read_text()

    return None


def parse_args(argv: list[str]) -> tuple[str, str | None]:
    repo_path = "."
    base_override = None
    args = argv[:]
    while args:
        if args[0] == "--repo" and len(args) > 1:
            repo_path = args[1]
            args = args[2:]
        elif args[0] == "--base" and len(args) > 1:
            base_override = args[1]
            args = args[2:]
        else:
            args = args[1:]
    return repo_path, base_override


def main() -> None:
    repo_path, base_override = parse_args(sys.argv[1:])

    git_root = find_git_root(repo_path)
    if not git_root:
        print(json.dumps({"error": "Not inside a git repository"}))
        sys.exit(1)

    cwd = git_root
    base = base_override or get_base_branch(cwd) or "main"
    merge_base, _ = resolve_merge_base(base, cwd)

    result: dict = {
        "git_root": cwd,
        "branch": run_ok(["git", "branch", "--show-current"], cwd=cwd),
        "upstream": run_ok(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd=cwd
        ),
        "base_branch": base,
        "merge_base": merge_base,
        "uncommitted_changes": run_ok(["git", "status", "--short"], cwd=cwd) or "",
    }

    if merge_base:
        result["commit_log"] = run_ok(["git", "log", "--oneline", f"{merge_base}..HEAD"], cwd=cwd) or ""
        result["commit_count"] = len(result["commit_log"].splitlines()) if result["commit_log"] else 0
        result["diff_stat"] = run_ok(["git", "diff", f"{merge_base}...HEAD", "--stat"], cwd=cwd) or ""
        result["files_changed"] = run_ok(["git", "diff", f"{merge_base}...HEAD", "--name-status"], cwd=cwd) or ""
        result["full_diff"] = run_ok(["git", "diff", f"{merge_base}...HEAD"], cwd=cwd) or ""
        if len(result["full_diff"]) > MAX_DIFF_CHARS:
            result["full_diff"] = result["full_diff"][:MAX_DIFF_CHARS] + "\n\n... (diff truncated, too large)"
            result["diff_truncated"] = True
    else:
        result["warning"] = f"Could not find merge base between {base} and HEAD"
        result["commit_log"] = ""
        result["commit_count"] = 0
        result["diff_stat"] = ""
        result["files_changed"] = ""
        result["full_diff"] = ""

    template = find_pr_template(cwd)
    if template:
        result["pr_template"] = template

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
