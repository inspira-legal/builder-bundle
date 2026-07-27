#!/usr/bin/env python3
"""Emit the concrete Cloud Routine setup for one shaped brief: a self-contained
routine prompt (slug / repo / base branch filled in) plus the provisioning
checklist that makes never-merge hold server-side. Boilerplate generation kept
deterministic and out of the model's hands — see references/routines.md for the
why behind each line.

Usage:
  python scaffold_routine.py --slug <slug> [--base main] [--repo owner/name]
  python scaffold_routine.py --self-test
"""

from __future__ import annotations

import argparse
import sys

PROMPT = """\
Set BB_UNATTENDED=1. Run /bb:delegate {slug} against the brief for `{slug}` \
(`.bb/tasks/{slug}/spec.md`) in {repo}: it builds every unchecked task in the brief, keeping the local gate green \
(cap retries at 3 on known-flake signatures only), commits per slice to a \
`claude/{slug}` branch, then chains into /bb:ship — open a DRAFT PR against \
`{base}` and watch it to resolution (green CI + handled review-bot threads), \
bounded by the run budget. Do not merge, do not push to a protected branch. If a \
task or the gate blocks unrecoverably, flip the brief's status to blocked, write \
the blocker into the PR description, and exit."""

CHECKLIST = """\
Do this once per repo:
  [ ] Commit `.bb/tasks/{slug}/spec.md` (brief + `## tasks`) and the `bb`
      plugin to {repo} — the fresh clone sees only what's in git.
  [ ] Capability-scope the routine's token: no merge permission, "Allow
      unrestricted branch pushes" OFF, no merge-capable connector attached.
  [ ] Enable branch protection on `{base}` (require a PR, block direct and force
      pushes) — the server-side backstop.
  [ ] Network: the Trusted preset (registries + GitHub) is enough.

Trigger: schedule, daily, an overnight slot; off-the-hour minute. One brief per
routine. With every task already checked the run is a no-op."""


def render(slug: str, base: str, repo: str | None) -> str:
    repo_ref = f"`{repo}`" if repo else "this repo"
    prompt = PROMPT.format(slug=slug, base=base, repo=repo_ref)
    checklist = CHECKLIST.format(slug=slug, base=base, repo=repo or "the target repo")
    return f"=== Routine prompt ===\n{prompt}\n\n=== Setup checklist ===\n{checklist}"


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Scaffold a Cloud Routine for one shaped brief.")
    p.add_argument("--slug", help="The brief slug (.bb/tasks/<slug>/spec.md).")
    p.add_argument("--base", default="main", help="Protected base branch the draft PR targets.")
    p.add_argument("--repo", help="owner/name, if you want it named in the prompt.")
    p.add_argument("--self-test", action="store_true", help="Run built-in checks and exit.")
    return p.parse_args(argv)


def self_test() -> int:
    # Distinctive base ("trunk") so base substitution is tested apart from the
    # `main` defaults; assert on the section banners so a glued header regresses.
    out = render("skill-flow-tightening", "trunk", "inspira-legal/builder-bundle")
    assert "=== Routine prompt ===" in out
    assert "=== Setup checklist ===" in out
    assert "BB_UNATTENDED=1" in out
    assert "/bb:delegate skill-flow-tightening" in out
    assert "claude/skill-flow-tightening" in out
    assert "inspira-legal/builder-bundle" in out
    assert "DRAFT PR against `trunk`" in out
    assert "branch protection on `trunk`" in out
    bare = render("x", "release", None)
    assert "this repo" in bare and "DRAFT PR against `release`" in bare
    print("scaffold_routine self-test: PASS")
    return 0


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    if args.self_test:
        return self_test()
    if not args.slug:
        print("error: --slug is required", file=sys.stderr)
        return 2
    print(render(args.slug, args.base, args.repo))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
