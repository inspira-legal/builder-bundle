#!/usr/bin/env python3
"""Keep the installed bb current, without asking, without waiting, and without
saying anything.

The SessionStart hook calls `claim_today()` in process, which is one file read on
the common path, and spawns the `__main__` path here when the day is still owed.
That path is the detached worker: it guards the marketplace clone, runs the two
commands a person would run, and records what it did.

The stamp holds the claimed day and the last outcome. It lives under
`CLAUDE_PLUGIN_DATA` because the install path carries the version and is replaced
on every update. Nothing reads the outcome back into a session: it is there for
whoever is diagnosing a quiet install.

Every failure here is silent: the hook's contract is exit 0 and no output, and a
resolution that comes back empty means nothing runs.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import date
from typing import NamedTuple

CLAUDE_DIR = os.path.join(os.path.expanduser("~"), ".claude")
PLUGIN_NAME = "bb"
STAMP_NAME = "update-stamp.json"
CLAIM_PREFIX = "update-claim-"

# What the worker records in the stamp's `outcome`, for whoever is diagnosing a
# quiet install. Nothing in a session reads them back. `ran` is deliberately not
# `installed`: the worker calls the CLI without comparing versions first, so what
# it knows is that both commands exited 0, not whether either had work to do.
OUTCOME_RAN = "ran"
OUTCOME_SKIPPED = "skipped"
OUTCOME_FAILED = "failed"

# How long the worker gives the network and the CLI. The worker is detached, so a
# command that hangs would otherwise sit there until the machine sleeps.
GIT_TIMEOUT = 60
CLI_TIMEOUT = 300


class Target(NamedTuple):
    """The running install, as the worker needs to address it."""

    marketplace: str  # the name `claude plugin update bb@MARKETPLACE` takes
    clone: str  # the marketplace's git clone, from `installLocation`
    scope: str  # `user` or `project`
    project_path: str | None  # where a project scoped update has to run


def plugin_root() -> str | None:
    """`.../plugins/cache/MARKETPLACE/bb/VERSION`.

    `CLAUDE_PLUGIN_ROOT` first, because it is what the platform states. The
    module's own path answers the same question when the variable does not reach
    the process, which is the case for a hook whose command interpolated it.
    """
    root = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if not root:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return root or None


def _same_path(left: str, right: str) -> bool:
    def key(path: str) -> str:
        return os.path.normcase(os.path.normpath(path)).rstrip("\\/")

    return key(left) == key(right)


def _segments(root: str) -> tuple[str, str] | None:
    """The marketplace name and the version the install path carries."""
    head, version = os.path.split(os.path.normpath(root))
    head, plugin = os.path.split(head)
    marketplace = os.path.basename(head)
    if plugin != PLUGIN_NAME or not marketplace or not version:
        return None
    return marketplace, version


def marketplace_of(root: str | None) -> str | None:
    parts = _segments(root) if root else None
    return parts[0] if parts else None


def read_json(path: str) -> dict:
    """The file as a dict. Missing and malformed both read as empty, on purpose:
    nothing here is worth an exception on a session start."""
    try:
        with open(path, encoding="utf-8") as f:
            loaded = json.load(f)
    except (OSError, ValueError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def stamp_path() -> str | None:
    """Where the stamp sits. `CLAUDE_PLUGIN_DATA` names the plugin's own data
    directory; without it the path is rebuilt from the marketplace name, which is
    how the platform names that directory anyway."""
    data = os.environ.get("CLAUDE_PLUGIN_DATA")
    if not data:
        marketplace = marketplace_of(plugin_root())
        if not marketplace:
            return None
        data = os.path.join(
            CLAUDE_DIR, "plugins", "data", f"{PLUGIN_NAME}-{marketplace}"
        )
    return os.path.join(data, STAMP_NAME)


def read_stamp(path: str | None) -> dict:
    """The stamp, or an empty dict for a first run. A malformed file reads the
    same as a missing one: the day is still owed."""
    return read_json(path) if path else {}


def write_stamp(path: str | None, **fields: str) -> bool:
    """The stamp, replaced whole with today's date plus whatever the caller
    records. Returns whether it landed, which is how the hook tells a claim that
    took the day from one that did not."""
    if not path:
        return False
    stamp = {"date": today()}
    stamp.update({key: value for key, value in fields.items() if value})
    # Through a temp file in the same directory. A worker killed mid write would
    # otherwise leave truncated JSON, which reads as a first run and gives the
    # day away again.
    temp = f"{path}.tmp"
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(temp, "w", encoding="utf-8") as f:
            json.dump(stamp, f, indent=2)
            f.write("\n")
        os.replace(temp, path)
    except OSError:
        return False
    return True


def _carried(stamp: dict) -> dict:
    """The fields a claim keeps, so a day that installs nothing still carries the
    reason the day before it stopped."""
    return {
        key: str(stamp.get(key) or "")
        for key in ("outcome", "reason")
        if stamp.get(key)
    }


def today() -> str:
    return date.today().isoformat()


def due(stamp: dict) -> bool:
    """Whether today's check is still owed. A stamp with no date is a first run."""
    return stamp.get("date") != today()


def _claim_marker(path: str) -> bool:
    """The exclusive create that decides who owns today. It is the only part of
    the claim two sessions cannot both win: starting at the same moment they
    read the same stale stamp, so whoever writes it second still writes it. A
    filesystem that cannot mark at all lets the claim through, because a feature
    that stops updating is worse than one that spawns twice in a rare race."""
    folder = os.path.dirname(path)
    marker = f"{CLAIM_PREFIX}{today()}"
    try:
        os.makedirs(folder, exist_ok=True)
        os.close(os.open(os.path.join(folder, marker), os.O_CREAT | os.O_EXCL))
    except FileExistsError:
        return False
    except OSError:
        return True
    try:
        for name in os.listdir(folder):
            if name.startswith(CLAIM_PREFIX) and name != marker:
                os.remove(os.path.join(folder, name))
    except OSError:
        pass
    return True


def claim_today(path: str | None) -> bool:
    """Claim today before anything is spawned, keeping the fields the last run
    left. A second session starting the same moment loses the claim and spawns
    nothing."""
    stamp = read_stamp(path)
    if not due(stamp):
        return False
    if not path or not _claim_marker(path):
        return False
    return write_stamp(path, **_carried(stamp))


def resolve() -> Target | None:
    """The running install: the marketplace name from the install path, the clone
    from `known_marketplaces.json`, and the scope from the `installed_plugins.json`
    entry whose `installPath` is this same path. Anything unresolved is None, and
    the caller does nothing."""
    root = plugin_root()
    parts = _segments(root) if root else None
    if not root or not parts:
        return None
    marketplace = parts[0]

    known = read_json(os.path.join(CLAUDE_DIR, "plugins", "known_marketplaces.json"))
    entry = known.get(marketplace)
    clone = entry.get("installLocation") if isinstance(entry, dict) else None
    if not clone or not os.path.isdir(os.path.join(clone, ".git")):
        return None

    installed = read_json(os.path.join(CLAUDE_DIR, "plugins", "installed_plugins.json"))
    plugins = installed.get("plugins")
    key = f"{PLUGIN_NAME}@{marketplace}"
    records = plugins.get(key) if isinstance(plugins, dict) else None
    matches = [
        record
        for record in (records if isinstance(records, list) else [])
        if isinstance(record, dict)
        and _same_path(str(record.get("installPath") or ""), root)
        and record.get("scope")
    ]
    if not matches:
        return None
    # Two scopes can share one cached install path, so the file can hold more
    # than one match, and its order is not an order of preference. The `user`
    # install is the one a session opened anywhere loads, so it goes first.
    matches.sort(key=lambda record: str(record.get("scope")) != "user")
    record = matches[0]
    return Target(
        marketplace=marketplace,
        clone=clone,
        scope=str(record.get("scope")),
        project_path=record.get("projectPath") or None,
    )


def _record(outcome: str, reason: str = "") -> None:
    """What this run did, into the stamp."""
    write_stamp(stamp_path(), outcome=outcome, reason=reason)


def _run(argv: list[str], timeout: int, cwd: str | None = None) -> str | None:
    """The command's stdout, or None when it failed, timed out, or never started.

    The worker has no stream to report on, so every way a command can go wrong
    comes back as the same None and the caller writes the reason it knows.
    """
    command: str | list[str] = argv
    if os.name == "nt" and os.path.splitext(argv[0])[1].lower() in (".cmd", ".bat"):
        # CreateProcess runs an executable. A `claude` installed as a .cmd shim,
        # which is what npm writes on Windows, needs the interpreter in front.
        #
        # cmd.exe reparses the line it is handed, and the marketplace name and
        # the shim's own path both come out of files this hook does not own. So
        # every argument goes in quoted, which is what keeps an `&` or a `|` from
        # reading as a separator, and a `%`, the one metacharacter a quote does
        # not tame, stops the run instead of reaching the parser. `/s` makes cmd
        # strip the outer pair and take the rest of the line as it stands.
        if any("%" in arg or (chr(34) in arg) for arg in argv):
            return None
        comspec = os.environ.get("COMSPEC") or "cmd.exe"
        quoted = " ".join(f'"{arg}"' for arg in argv)
        command = f'"{comspec}" /d /s /c "{quoted}"'
    try:
        done = subprocess.run(
            command,
            capture_output=True,
            timeout=timeout,
            cwd=cwd,
            # Explicit, because the platform default is a legacy code page on
            # most Windows installs: a byte git prints that the code page has no
            # character for raises, and that raise reads as a failed command.
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, ValueError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def _run_or_fail(
    argv: list[str], timeout: int, reason: str, cwd: str | None = None
) -> str | None:
    """The command's stdout, or None with the reason already in the stamp. Every
    command the worker runs stops the run the same way, so the recording lives
    here and the caller carries only the reason it knows."""
    out = _run(argv, timeout, cwd)
    if out is None:
        _record(OUTCOME_FAILED, reason=reason)
    return out


def _default_branch(git: str, clone: str) -> str | None:
    """The branch the remote's HEAD points at, asked of the remote itself so a
    clone whose `origin/HEAD` was never written still answers."""
    argv = [git, "-C", clone, "ls-remote", "--symref", "origin", "HEAD"]
    out = _run(argv, GIT_TIMEOUT)
    prefix = "refs/heads/"
    for line in (out or "").splitlines():
        if not line.startswith("ref: "):
            continue
        ref = line[len("ref: ") :].split()[0]
        if ref.startswith(prefix):
            return ref[len(prefix) :] or None
    return None


def main() -> int:
    """The detached worker: guard, install, record.

    Nothing is compared first. `claude plugin update` is forward only and the day
    is already claimed, so a run with nothing to install costs one CLI call that
    nobody waits on, and reading the remote version would buy only a name for a
    line this feature does not print.

    Every path ends in one stamp write and exit 0.
    """
    target = resolve()
    if not target:
        _record(
            OUTCOME_SKIPPED,
            reason="the marketplace clone or the scope did not resolve",
        )
        return 0

    git = shutil.which("git")
    claude = shutil.which("claude")
    if not git or not claude:
        missing = "git" if not git else "claude"
        _record(OUTCOME_SKIPPED, reason=f"{missing} is not on this PATH")
        return 0

    branch = _default_branch(git, target.clone)
    if not branch:
        _record(OUTCOME_FAILED, reason="the remote default branch did not answer")
        return 0

    # The guard: `claude plugin update` installs the clone's working tree, so a
    # clone that doubles as someone's checkout is left exactly as it is.
    head = [git, "-C", target.clone, "rev-parse", "--abbrev-ref", "HEAD"]
    checked_out = _run_or_fail(
        head, GIT_TIMEOUT, "the clone's checked out branch did not answer"
    )
    if checked_out is None:
        return 0
    checked_out = checked_out.strip()
    if checked_out != branch:
        _record(OUTCOME_SKIPPED, reason=f"the clone is on {checked_out}, not {branch}")
        return 0
    dirt = _run_or_fail(
        [git, "-C", target.clone, "status", "--porcelain"],
        GIT_TIMEOUT,
        "the clone's status did not answer",
    )
    if dirt is None:
        return 0
    if dirt.strip():
        _record(OUTCOME_SKIPPED, reason=f"the clone's tree is dirty on {branch}")
        return 0

    # A project scoped install is addressed from its own directory, the way the
    # person would run the command there. Without that directory the command
    # would run from wherever the worker started, and a project scope addressed
    # from somewhere else installs nothing, so it says so and stops.
    cwd = target.project_path or None
    if cwd and not os.path.isdir(cwd):
        cwd = None
    if target.scope == "project" and not cwd:
        _record(OUTCOME_SKIPPED, reason="the project directory did not resolve")
        return 0
    refresh = [claude, "plugin", "marketplace", "update", target.marketplace]
    reason = f"claude plugin marketplace update {target.marketplace} failed"
    if _run_or_fail(refresh, CLI_TIMEOUT, reason, cwd) is None:
        return 0
    plugin = f"{PLUGIN_NAME}@{target.marketplace}"
    install = [claude, "plugin", "update", plugin, "-s", target.scope, "-y"]
    reason = f"claude plugin update {plugin} failed"
    if _run_or_fail(install, CLI_TIMEOUT, reason, cwd) is None:
        return 0

    _record(OUTCOME_RAN, reason=f"{plugin} on {branch}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        # A traceback has nowhere to go from a detached child whose streams are
        # the null device, and the claimed date makes tomorrow the retry.
        raise SystemExit(0)
