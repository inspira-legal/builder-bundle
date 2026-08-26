#!/usr/bin/env python3
"""
Resolve the project's checks through the authority chain, without running any of
them: CLAUDE.md and docs, then CI workflow files, then package.json / justfile /
Makefile / pyproject.toml. Consumed by /bb:implement (its step 4, and the `checks`
it hands to workflows/build-tasks.js) and by /bb:ship (its Step 2).

This docstring is where the chain is stated, and this script is the resolution; the
callers cite it and run what it returns, so a change to the chain lands once.

Only the repo's own documents define the repo's checks. The machine-level
`~/.claude/CLAUDE.md` is read for one thing: it can forbid running anything locally.
Its commands belong to whatever project its author had in mind, so they never enter
the list.

A prohibition comes back as `runnable: false` with `policy.evidence`, the line that
says so, and `policy.scope`, which of the two said it. A caller then neither tries
the command nor reads the refusal as a tree that was already red, and can name the
right source when it explains why nothing ran.

What this script cannot resolve it reports instead of dropping. `unresolved` carries
the commands it saw in the tier that answered and could not turn into something
runnable, each with its reason. Deciding that a dev server is not a check is this
script's call and stays silent; failing to recognize a stack's runner is not, and an
empty `commands` that hides it reads as "this project has no checks". A non-empty
`unresolved` is the caller's cue to read `where` itself rather than trust the list.

Usage:
  python3 resolve_checks.py
  python3 resolve_checks.py --repo /path/to/repo
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

# What makes a line or a script name a check rather than a dev server or a release.
CHECK_WORDS = re.compile(
    r"test|lint|format|fmt|typecheck|type-check|tsc|validate|check|build|"
    r"mypy|ruff|pytest|eslint|prettier|oxfmt|clippy|vitest|jest",
    re.IGNORECASE,
)

# What a prohibition can be about. Wider than CHECK_WORDS because a line forbidding
# the checks names them the way prose does ("never run the suite locally"), and
# "suite" is not a word any check list is built from.
CHECK_SUBJECTS = re.compile(
    CHECK_WORDS.pattern + r"|su[ií]te|suite|e2e|coverage|spec[s]?\b",
    re.IGNORECASE,
)

# A backticked span or a CI `run:` line is only a command when it starts with one of
# these. It is what keeps `gh pr checks --watch` out of a check list: the authority
# tiers are read as text, and a repo's docs mention plenty of commands that are not
# the project's checks. A `./`-prefixed head counts too, which is how the repo-local
# wrappers (`./gradlew`, `./mvnw`, `./scripts/check.sh`) get in without being listed.
RUNNERS = {
    "npm", "pnpm", "yarn", "bun", "bunx", "npx", "deno", "node", "tsx", "vitest", "jest",
    "just", "make", "task", "rake", "bundle", "cmake", "ctest", "meson", "ninja",
    "python", "python3", "uv", "poetry", "pdm", "hatch", "tox", "nox",
    "pytest", "mypy", "ruff", "black", "isort", "flake8", "pyright",
    "cargo", "go", "dotnet", "mvn", "gradle", "gradlew", "swift", "mix", "zig",
    "tsc", "eslint", "prettier", "oxfmt", "oxlint", "biome",
    "composer", "php", "phpunit", "bazel", "pre-commit", "rspec", "sbt", "lein", "stack",
    "bash", "sh", "zsh", "docker", "docker-compose", "podman", "mise", "nix", "devbox",
    "dart", "flutter", "elixir", "ruby", "cabal", "clang-format", "shellcheck",
}

# Shell scaffolding and everyday tools, which is a different thing from a runner this
# script was never taught. This list only guards the `unresolved` report, never the
# answer, so a name missing from it costs one noisy line a reader dismisses, while a
# name missing from RUNNERS costs a check nobody runs. That asymmetry is why one list
# is allowed to be incomplete and the other is not.
NOT_RUNNERS = {
    "echo", "printf", "cd", "export", "set", "shopt", "unset", "eval", "exec", "source",
    "if", "then", "else", "elif", "fi", "for", "while", "until", "do", "done", "case",
    "esac", "exit", "return", "trap", "read", "shift", "true", "false", "wait",
    "cat", "cp", "mv", "rm", "mkdir", "rmdir", "touch", "ln", "ls", "find", "chmod",
    "sed", "awk", "grep", "cut", "sort", "uniq", "tee", "head", "tail", "tr", "xargs",
    "jq", "yq", "env", "which", "sleep", "date", "git", "gh", "curl", "wget", "tar",
    "unzip", "sudo", "apt", "apt-get", "brew", "choco", "winget", "gpg", "ssh",
}

# A backticked span or a CI line that reads like a command whose head this script does
# not know: a plausible executable, more than one token, and a check word after the
# head. It is the `pants test ::` of a stack RUNNERS never learned, and reporting it is
# the difference between an answer and a silence.
CANDIDATE_SHAPE = re.compile(r"^[\w./@:+-]+(?:\s+\S+)+$")

# The verbs that turn a mention of the checks into a prohibition on running them.
FORBID = re.compile(
    r"nunca\s+rode|n[aã]o\s+rode|nunca\s+execute|n[aã]o\s+execute|"
    r"never\s+run|do\s+not\s+run|don'?t\s+run|no\s+local\s+(?:checks|tests|builds)",
    re.IGNORECASE,
)

# A watcher never terminates, and a caller told to run every command once waits on it
# forever. Matched against the whole command, flags included, because `--watch` is
# where the hang lives.
DENY_ANYWHERE = re.compile(r"\bwatch\b|\bserve\b|--ui\b", re.IGNORECASE)

# What a check is not, matched against the command with its flags stripped: a dev
# server, a publish, a deploy. Flags are stripped first so `cargo test --release`
# stays a check while `pnpm run build:release` does not.
DENY_NAMED = re.compile(
    r"\bdev\b|\bstart\b|\bpublish\b|\brelease\b|\bdeploy\b|\bpreview\b|\bbump\b",
    re.IGNORECASE,
)

# A formatter in write mode rewrites the tree instead of reporting on it. Its
# `--check` sibling is the check; this one is an edit, and running it to establish a
# baseline dirties every file it touches.
WRITE_MODE = re.compile(r"--write\b|--fix\b|--fix-only\b|--in-place\b", re.IGNORECASE)

# A CI line lifted out of its step loses the shell that defined these, so it cannot
# run on its own: an array built two lines above, a command substitution, a GitHub
# expression the runner would have interpolated.
UNRESOLVED = re.compile(r"\$\{|\$\(|`")

# Only a workflow that gates a change is a source of this project's checks. A release
# or a publish workflow runs on a tag and its commands are not checks.
CI_GATE_TRIGGERS = ("pull_request", "push", "merge_group", "pull_request_target")

MAX_COMMANDS = 12
MAX_UNRESOLVED = 5

# Why a candidate did not become a command, when the reason is the script's own limit
# rather than a decision it was entitled to make.
UNRESOLVED_REASONS = ("unrecognized-runner", "shell-dependent")


def run_ok(cmd: list[str], cwd: str | None = None) -> str | None:
    # The encoding is named because `text=True` decodes in the locale codec, which is
    # cp1252 on Windows: one accented character in the repo's own path would raise here.
    p = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
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
    head = text.split()[0]
    return head in RUNNERS or head.startswith("./")


def read_package_scripts(root: Path) -> dict:
    package = root / "package.json"
    if not package.is_file():
        return {}
    try:
        return json.loads(read_text(package)).get("scripts") or {}
    except (ValueError, AttributeError):
        return {}


def script_body(text: str, scripts: dict) -> str | None:
    """The package.json body behind a `<manager> run <name>`, when there is one.

    A command naming a script says nothing about what the script does. `bun run fmt`
    reads as a check and rewrites the tree; the body is where that shows, and the
    body is available in every tier once package.json has been read.
    """
    parts = [token for token in text.split() if not token.startswith("-")]
    if len(parts) < 2 or parts[0] not in ("npm", "pnpm", "yarn", "bun", "deno"):
        return None
    name = parts[2] if len(parts) > 2 and parts[1] == "run" else parts[1]
    body = scripts.get(name)
    return body if isinstance(body, str) else None


def unknown_runner_shape(text: str) -> bool:
    """Whether text reads like a check command whose runner this script cannot name."""
    text = text.strip()
    if "\n" in text or not 3 < len(text) <= 120:
        return False
    if not CANDIDATE_SHAPE.match(text):
        return False
    head, *rest = text.split()
    if head in RUNNERS or head in NOT_RUNNERS or head.startswith("./"):
        return False
    return bool(CHECK_WORDS.search(" ".join(rest)))


def classify_command(text: str, scripts: dict | None = None) -> tuple[bool, str | None]:
    """(is one of this project's checks, why it was dropped when it is not).

    A reason comes back only for the drops a reader has to see. Ruling out a dev
    server, a watcher or a formatter in write mode is a decision this script is
    entitled to make, so it returns no reason: reporting those would bury the two
    cases where the script did not decide but failed, which are the ones that turn an
    empty list into a wrong answer.

    The check word is looked for with the flags stripped, so `pnpm publish
    --no-git-checks` is not admitted by the word sitting inside its own flag.
    """
    if WRITE_MODE.search(text) or DENY_ANYWHERE.search(text):
        return False, None
    named = " ".join(token for token in text.split() if not token.startswith("-"))
    if DENY_NAMED.search(named):
        return False, None
    if UNRESOLVED.search(text):
        # The shell step that defined an array, a substitution or a CI expression is
        # not travelling with the line, so this one cannot run as written. It still
        # names a check often enough to be worth reading.
        return False, "shell-dependent" if CHECK_WORDS.search(named) else None
    if not looks_like_command(text):
        return False, "unrecognized-runner" if unknown_runner_shape(text) else None
    body = script_body(text, scripts) if scripts else None
    if body and (WRITE_MODE.search(body) or DENY_ANYWHERE.search(body)):
        return False, None
    return bool(CHECK_WORDS.search(named)), None


def dedupe_unresolved(items: list[dict]) -> list[dict]:
    seen: set[str] = set()
    out = []
    for item in items:
        if item["command"] not in seen:
            seen.add(item["command"])
            out.append(item)
    return out


def dedupe(items: list[str]) -> list[str]:
    seen: set[str] = set()
    out = []
    for item in items:
        key = " ".join(item.split())
        if key and key not in seen:
            seen.add(key)
            out.append(key)
    return out


def policy_sources(root: Path) -> list[tuple[Path, str]]:
    """Ordered highest authority first, each with the scope it governs.

    The repo's own documents define this project's checks. The machine-level
    CLAUDE.md governs the machine: it can forbid running anything locally, and that
    prohibition is real, but its commands belong to whatever project its author had
    in mind and are never this one's checks.
    """
    home = Path.home()
    return [
        (root / "CLAUDE.md", "repo"),
        (root / ".claude" / "CLAUDE.md", "repo"),
        (root / "AGENTS.md", "repo"),
        (root / "docs" / "CONTRIBUTING.md", "repo"),
        (root / "CONTRIBUTING.md", "repo"),
        (home / ".claude" / "CLAUDE.md", "machine"),
    ]


def read_authority_tier(
    root: Path, scripts: dict
) -> tuple[list[str], dict | None, list[str], list[dict]]:
    """Return (commands, policy, notes, unresolved) from the CLAUDE.md / docs tier.

    The first repo document that yields a command is the one that answers: the tiers
    are exclusive, so a passing mention in CONTRIBUTING.md does not get appended to
    the suite CLAUDE.md already stated. `unresolved` follows the same rule one level
    down, carrying what the answering document could not resolve, and everything the
    tier saw when no document in it answered at all.
    """
    commands: list[str] = []
    notes: list[str] = []
    unresolved: list[dict] = []
    unanswered: list[dict] = []
    policy = None

    for path, scope in policy_sources(root):
        if not path.is_file():
            continue
        found: list[str] = []
        dropped: list[dict] = []
        for raw in read_text(path).splitlines():
            line = raw.strip()
            if not line:
                continue
            if scope == "repo" and CHECK_WORDS.search(line):
                for span in re.findall(r"`([^`]+)`", line):
                    is_check, reason = classify_command(span, scripts)
                    if is_check:
                        found.append(span)
                    elif reason:
                        dropped.append(
                            {"command": span.strip(), "reason": reason, "where": str(path)}
                        )
            # The prohibition is read on every line, not only on one a check list
            # could have been built from: "never run the suite locally" names the
            # checks in words no command carries.
            if FORBID.search(line) and CHECK_SUBJECTS.search(line):
                notes.append(f"{path}: {line[:200]}")
                if policy is None:
                    policy = {
                        "decision": "ci-only",
                        "source": str(path),
                        "scope": scope,
                        "evidence": line[:400],
                    }
        if found and not commands:
            commands, unresolved = found, dropped
        elif not found:
            unanswered.extend(dropped)

    return dedupe(commands), policy, notes, dedupe_unresolved(unresolved or unanswered)


def ci_gate_trigger(text: str) -> str | None:
    """The trigger that makes a workflow a gate on a change, or None.

    A `push` filtered down to `tags:` is a release trigger, not a gate: what runs
    under it publishes, and a publish is not one of this project's checks.
    """
    lines = text.splitlines()
    # `on` is a YAML 1.1 boolean, so workflows write it quoted about as often as bare.
    start = next(
        (i for i, line in enumerate(lines) if re.match(r"""^["']?on["']?\s*:""", line)), None
    )
    if start is None:
        return None

    inline = lines[start].split(":", 1)[1].strip()
    if inline:
        names = re.findall(r"[\w-]+", inline)
        return next((n for n in names if n in CI_GATE_TRIGGERS), None)

    block: list[str] = []
    for line in lines[start + 1 :]:
        if line.strip() and not line.startswith((" ", "\t")):
            break
        block.append(line)
    body = "\n".join(block)

    for trigger in CI_GATE_TRIGGERS:
        match = re.search(rf"^(\s*)-?\s*{trigger}\s*:?\s*$", body, re.MULTILINE)
        if not match:
            continue
        if trigger != "push":
            return trigger
        indent = match.group(1)
        filters: list[str] = []
        for line in body[match.end() :].splitlines():
            if line.strip() and not line.startswith(indent + " "):
                break
            filters.append(line)
        filter_text = "\n".join(filters)
        if "tags" in filter_text and "branches" not in filter_text:
            continue
        return trigger
    return None


def run_lines(text: str) -> list[str]:
    """Every line a workflow's `run:` steps would execute, block scalars unrolled.

    Nothing is judged here. What a line turns out to be is `classify_command`'s to
    say, which is what keeps the recognizing and the reporting in one place.
    """
    lines = text.splitlines()
    out: list[str] = []
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
                if body.strip():
                    out.append(body.strip())
                i += 1
            continue
        if inline:
            out.append(inline)
        i += 1
    return out


def read_ci_tier(root: Path, scripts: dict) -> tuple[list[str], list[str], list[dict]]:
    """Return (commands, workflow names read, unresolved) from the workflow tier."""
    workflows = root / ".github" / "workflows"
    if not workflows.is_dir():
        return [], [], []

    commands: list[str] = []
    unresolved: list[dict] = []
    read: list[str] = []
    for path in sorted(workflows.glob("*.y*ml")):
        text = read_text(path)
        if not ci_gate_trigger(text):
            continue
        read.append(path.name)
        for candidate in run_lines(text):
            is_check, reason = classify_command(candidate, scripts)
            if is_check:
                commands.append(candidate)
            elif reason:
                unresolved.append({"command": candidate, "reason": reason, "where": path.name})

    return dedupe(commands), read, dedupe_unresolved(unresolved)


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


def read_manifest_tier(root: Path, scripts: dict) -> list[str]:
    commands: list[str] = []

    if scripts:
        manager = package_manager(root)
        for name, body in scripts.items():
            if not CHECK_WORDS.search(name) or DENY_NAMED.search(name):
                continue
            # The body decides, not the name: a `fmt` running `oxfmt --write .` is an
            # edit, and the `fmt:check` sitting next to it is the check.
            if isinstance(body, str) and (WRITE_MODE.search(body) or DENY_ANYWHERE.search(body)):
                continue
            commands.append(f"{manager} run {name}")

    for filename, runner in (("justfile", "just"), ("Justfile", "just"), ("Makefile", "make")):
        path = root / filename
        if not path.is_file():
            continue
        for line in read_text(path).splitlines():
            match = re.match(r"^([A-Za-z][\w-]*)\s*:(?!=)", line)
            if not match:
                continue
            target = match.group(1)
            if CHECK_WORDS.search(target) and not DENY_NAMED.search(target):
                commands.append(f"{runner} {target}")

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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Resolve this project's checks through the authority chain, as JSON."
    )
    parser.add_argument("--repo", default=".", help="Path inside the target repository.")
    return parser.parse_args()


def main() -> None:
    repo = parse_args().repo
    git_root = run_ok(["git", "rev-parse", "--show-toplevel"], cwd=repo)
    root = Path(git_root) if git_root else Path(repo).resolve()

    scripts = read_package_scripts(root)
    authority, policy, notes, authority_unresolved = read_authority_tier(root, scripts)
    ci, ci_workflows, ci_unresolved = read_ci_tier(root, scripts)
    manifest = read_manifest_tier(root, scripts)

    # The tier that answers is the tier whose unresolved commands matter: a runner this
    # script cannot name in CONTRIBUTING.md is noise once CLAUDE.md has stated the
    # suite. With no tier answering, every one of them is a lead worth reading, which
    # is the case that would otherwise report "no checks" to a repo that has them. The
    # manifest tier reads structured data instead of prose, so it has nothing to fail at.
    if authority:
        commands, source, unresolved = authority, "CLAUDE.md / docs", authority_unresolved
    elif ci:
        commands, source, unresolved = ci, ".github/workflows", ci_unresolved
    elif manifest:
        commands = manifest
        source = "package.json / justfile / Makefile / pyproject.toml"
        unresolved = []
    else:
        commands, source = [], None
        unresolved = dedupe_unresolved(authority_unresolved + ci_unresolved)

    result = {
        "git_root": str(root),
        "commands": commands[:MAX_COMMANDS],
        # `source: null` is the one answer that means no tier resolved anything. A
        # tier that answers always answers with at least one command, so a caller
        # reading an empty list still has to read `source` to know which happened.
        "source": source,
        "truncated": len(commands) > MAX_COMMANDS,
        "resolved_count": len(commands),
        "runnable": policy is None,
        "policy": policy,
        "notes": notes[:5],
        # What the script saw and could not resolve, so an empty `commands` is never
        # read as "no checks" when it means "no runner I recognize". Non-empty is the
        # caller's cue to open `where` and decide, instead of trusting the list.
        "unresolved": unresolved[:MAX_UNRESOLVED],
        "candidates": {
            "authority": authority,
            "ci": ci,
            "ci_workflows": ci_workflows,
            "manifest": manifest,
        },
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
