#!/usr/bin/env python3
"""
Create (or reuse) an isolated git worktree on a throwaway branch so an
autonomous run can edit and commit WITHOUT touching the user's live checkout or
a protected branch. Emits JSON to stdout.

Fail-closed: if the destination working tree is dirty, if the run is on a
protected branch, or if a worktree can't be created, it emits dirty_blocked /
blocked and exits non-zero so the caller aborts rather than falling back to the
live tree.

Usage:
  python enter_worktree.py --label implement
  python enter_worktree.py --label implement --base main --repo /path/to/repo
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

PROTECTED = {"main", "master", "release", "develop", "production"}


def run(cmd: list[str], cwd: str | None = None) -> tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def git(args: list[str], cwd: str) -> str | None:
    code, out, _ = run(["git", *args], cwd=cwd)
    return out if code == 0 else None


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Create/reuse an isolated git worktree on a throwaway branch (fail-closed).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--repo", default=".", help="Path inside the target repo.")
    p.add_argument("--label", required=True, help="Short label for the throwaway branch/worktree.")
    p.add_argument("--base", default=None, help="Base branch (defaults to the repo default branch).")
    p.add_argument("--seq", default="1", help="Disambiguator appended to the branch name.")
    return p.parse_args()


def emit(obj: dict, code: int) -> int:
    print(json.dumps(obj, indent=2))
    return code


def main() -> int:
    args = parse_args()
    root = git(["rev-parse", "--show-toplevel"], cwd=args.repo)
    if not root:
        return emit({"error": "not inside a git repository", "blocked": True}, 1)

    current = git(["branch", "--show-current"], cwd=root) or ""
    if current in PROTECTED:
        # Refuse to run an autonomous job from a protected branch's worktree.
        return emit(
            {"blocked": True, "reason": f"on protected branch '{current}'", "worktree_path": None},
            1,
        )

    status = git(["status", "--porcelain"], cwd=root)
    if status:
        return emit(
            {"dirty_blocked": True, "reason": "destination tree has uncommitted changes", "worktree_path": None},
            1,
        )

    base = args.base or git(["symbolic-ref", "--short", "refs/remotes/origin/HEAD"], cwd=root)
    if base and "/" in base:
        base = base.split("/", 1)[1]
    base = base or "main"
    base_sha = git(["rev-parse", base], cwd=root) or git(["rev-parse", "HEAD"], cwd=root)

    branch = f"auto/{args.label}-{args.seq}"
    wt_path = f"../.worktrees/{args.label}-{args.seq}"

    # Reuse if the worktree already exists; else create it.
    existing = git(["worktree", "list", "--porcelain"], cwd=root) or ""
    if branch in existing or wt_path.lstrip("./") in existing:
        return emit(
            {"worktree_path": wt_path, "branch": branch, "base": base, "base_sha": base_sha, "created": False},
            0,
        )

    code, _, err = run(["git", "worktree", "add", "-b", branch, wt_path, base], cwd=root)
    if code != 0:
        return emit({"blocked": True, "reason": f"git worktree add failed: {err}", "worktree_path": None}, 1)

    return emit(
        {"worktree_path": wt_path, "branch": branch, "base": base, "base_sha": base_sha, "created": True},
        0,
    )


if __name__ == "__main__":
    raise SystemExit(main())
