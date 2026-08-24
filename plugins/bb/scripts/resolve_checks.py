#!/usr/bin/env python3
"""
Resolve the project's checks through the authority chain, without running any of
them: CLAUDE.md and docs, then CI workflow files, then package.json / justfile /
Makefile / pyproject.toml. Consumed by /bb:implement (its step 4, and the `checks`
it hands to workflows/build-tasks.js) and by /bb:ship (its Step 2).

The chain used to be prose in three places, so a change to it had to land three
times. This script is the resolution; the callers run what it returns.

A top authority can also forbid running checks locally. That comes back as
`runnable: false` with the line that says so, so a caller neither tries the command
nor reads the refusal as a tree that was already red.

Usage:
  python3 resolve_checks.py
  python3 resolve_checks.py --repo /path/to/repo
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

# What makes a line or a script name a check rather than a dev server or a release.
CHECK_WORDS = re.compile(
    r"test|lint|format|fmt|typecheck|type-check|tsc|validate|check|build|"
    r"mypy|ruff|pytest|eslint|prettier|oxfmt|clippy|vitest|jest",
    re.IGNORECASE,
)

# A backticked span or a CI `run:` line is only a command when it starts with one of
# these. It is what keeps `gh pr checks --watch` out of a check list: the authority
# tiers are read as text, and a repo's docs mention plenty of commands that are not
# the project's checks.
RUNNERS = {
    "npm", "pnpm", "yarn", "bun", "bunx", "npx", "deno",
    "just", "make", "task", "rake", "bundle",
    "python", "python3", "uv", "poetry", "pdm", "hatch", "tox", "nox",
    "pytest", "mypy", "ruff", "black", "isort", "flake8",
    "cargo", "go", "dotnet", "mvn", "gradle", "swift", "mix",
    "tsc", "eslint", "prettier", "oxfmt", "oxlint", "biome",
    "composer", "php", "bazel", "pre-commit",
}

# The verbs that turn a mention of the checks into a prohibition on running them.
FORBID = re.compile(
    r"nunca\s+rode|n[aã]o\s+rode|nunca\s+execute|n[aã]o\s+execute|"
    r"never\s+run|do\s+not\s+run|don'?t\s+run|no\s+local\s+(?:checks|tests|builds)",
    re.IGNORECASE,
)

MAX_COMMANDS = 12


def run_ok(cmd: list[str], cwd: str | None = None) -> str | None:
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def looks_like_command(text: str) -> bool:
    text = text.strip()
    if not text or "\n" in text or len(text) > 120:
        return False
    return text.split()[0] in RUNNERS


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out = []
    for item in items:
        key = " ".join(item.split())
        if key and key not in seen:
            seen.add(key)
            out.append(key)
    return out


def policy_sources(root: Path) -> list[Path]:
    """Ordered highest authority first: the repo speaks before the machine does."""
    home = Path.home()
    return [
        root / "CLAUDE.md",
        root / ".claude" / "CLAUDE.md",
        root / "AGENTS.md",
        root / "docs" / "CONTRIBUTING.md",
        root / "CONTRIBUTING.md",
        home / ".claude" / "CLAUDE.md",
    ]


def read_authority_tier(root: Path) -> tuple[list[str], dict | None, list[str]]:
    """Return (commands, policy, notes) from the CLAUDE.md / docs tier."""
    commands: list[str] = []
    notes: list[str] = []
    policy = None

    for path in policy_sources(root):
        if not path.is_file():
            continue
        for raw in read_text(path).splitlines():
            line = raw.strip()
            if not line or not CHECK_WORDS.search(line):
                continue
            spans = re.findall(r"`([^`]+)`", line)
            commands.extend(s for s in spans if looks_like_command(s))
            if FORBID.search(line):
                notes.append(line)
                if policy is None:
                    policy = {
                        "decision": "ci-only",
                        "source": str(path),
                        "evidence": line[:400],
                    }

    return dedupe(commands), policy, notes


def read_ci_tier(root: Path) -> list[str]:
    workflows = root / ".github" / "workflows"
    if not workflows.is_dir():
        return []

    commands: list[str] = []
    for path in sorted(workflows.glob("*.y*ml")):
        lines = read_text(path).splitlines()
        i = 0
        while i < len(lines):
            match = re.match(r"^(\s*)-?\s*run:\s*(.*)$", lines[i])
            if not match:
                i += 1
                continue
            indent, inline = match.group(1), match.group(2).strip()
            if inline in ("|", ">", "|-", ">-"):
                # Block scalar: every more-indented line that follows is one command.
                i += 1
                while i < len(lines):
                    body = lines[i]
                    if body.strip() and not body.startswith(indent + " "):
                        break
                    if looks_like_command(body):
                        commands.append(body.strip())
                    i += 1
                continue
            if looks_like_command(inline):
                commands.append(inline)
            i += 1

    return dedupe(c for c in commands if CHECK_WORDS.search(c))


def package_manager(root: Path) -> str:
    for lockfile, manager in (
        ("pnpm-lock.yaml", "pnpm"),
        ("bun.lock", "bun"),
        ("bun.lockb", "bun"),
        ("yarn.lock", "yarn"),
        ("package-lock.json", "npm"),
    ):
        if (root / lockfile).is_file():
            return manager
    return "npm"


def read_manifest_tier(root: Path) -> list[str]:
    commands: list[str] = []

    package = root / "package.json"
    if package.is_file():
        try:
            scripts = json.loads(read_text(package)).get("scripts") or {}
        except (ValueError, AttributeError):
            scripts = {}
        manager = package_manager(root)
        for name in scripts:
            if CHECK_WORDS.search(name):
                commands.append(f"{manager} run {name}")

    for filename, runner in (("justfile", "just"), ("Justfile", "just"), ("Makefile", "make")):
        path = root / filename
        if not path.is_file():
            continue
        for line in read_text(path).splitlines():
            match = re.match(r"^([A-Za-z][\w-]*)\s*:(?!=)", line)
            if match and CHECK_WORDS.search(match.group(1)):
                commands.append(f"{runner} {match.group(1)}")

    pyproject = root / "pyproject.toml"
    if pyproject.is_file():
        # Section headers instead of a TOML parse: what is being read is which tool the
        # project configured, and that is the header itself.
        text = read_text(pyproject)
        for header, command in (
            ("[tool.ruff", "ruff check ."),
            ("[tool.mypy", "mypy ."),
            ("[tool.pytest", "pytest"),
            ("[tool.black", "black --check ."),
        ):
            if header in text:
                commands.append(command)

    return dedupe(commands)


def parse_args(argv: list[str]) -> str:
    repo = "."
    args = argv[:]
    while args:
        if args[0] == "--repo" and len(args) > 1:
            repo = args[1]
            args = args[2:]
        else:
            args = args[1:]
    return repo


def main() -> None:
    repo = parse_args(sys.argv[1:])
    git_root = run_ok(["git", "rev-parse", "--show-toplevel"], cwd=repo)
    root = Path(git_root) if git_root else Path(repo).resolve()

    authority, policy, notes = read_authority_tier(root)
    ci = read_ci_tier(root)
    manifest = read_manifest_tier(root)

    if authority:
        commands, source = authority, "CLAUDE.md / docs"
    elif ci:
        commands, source = ci, ".github/workflows"
    elif manifest:
        commands, source = manifest, "package.json / justfile / Makefile / pyproject.toml"
    else:
        commands, source = [], None

    result = {
        "git_root": str(root),
        "commands": commands[:MAX_COMMANDS],
        "source": source,
        "runnable": policy is None,
        "policy": policy,
        "notes": notes[:5],
        "candidates": {
            "authority": authority,
            "ci": ci,
            "manifest": manifest,
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
