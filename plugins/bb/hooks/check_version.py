#!/usr/bin/env python3
"""Keep the installed bb current, without asking and without waiting.

Two entry points live here. `report()` runs in process from the SessionStart hook:
it reads the stamp, returns the line the session context carries when the last run
installed something, and says whether today's check is still owed. The `__main__`
path is the detached worker that does the network half and writes the stamp back.

The stamp is the only channel between the two, and it lives under
`CLAUDE_PLUGIN_DATA` because the install path carries the version and is replaced
on every update.

Every failure here is silent: the hook's contract is exit 0 and no output, and a
resolution that comes back empty means nothing runs.
"""

from __future__ import annotations

import json
import os
from datetime import date
from typing import NamedTuple

CLAUDE_DIR = os.path.join(os.path.expanduser("~"), ".claude")
PLUGIN_NAME = "bb"
STAMP_NAME = "update-stamp.json"

# What the worker records in the stamp's `outcome`. `report()` speaks for
# `installed` alone; the rest are read by whoever is diagnosing a quiet install.
OUTCOME_INSTALLED = "installed"
OUTCOME_CURRENT = "current"
OUTCOME_SKIPPED = "skipped"
OUTCOME_FAILED = "failed"


class Target(NamedTuple):
    """The running install, as the worker needs to address it."""

    marketplace: str  # the name `claude plugin update bb@MARKETPLACE` takes
    clone: str  # the marketplace's git clone, from `installLocation`
    scope: str  # `user` or `project`
    project_path: str | None  # where a project scoped update has to run
    version: str  # the version this session loaded
    root: str  # the install path the scope was matched on


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


def version_of(root: str | None) -> str | None:
    parts = _segments(root) if root else None
    return parts[1] if parts else None


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
    same as a missing one: no line, and the day is still owed."""
    return read_json(path) if path else {}


def write_stamp(path: str | None, **fields: str) -> bool:
    """The stamp, replaced whole with `date` plus whatever the caller records.
    Returns whether it landed, so the worker can stop when it cannot claim."""
    if not path:
        return False
    stamp = {"date": today()}
    stamp.update({key: value for key, value in fields.items() if value})
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(stamp, f, indent=2)
            f.write("\n")
    except OSError:
        return False
    return True


def today() -> str:
    return date.today().isoformat()


def due(stamp: dict) -> bool:
    """Whether today's check is still owed. A stamp with no date is a first run."""
    return stamp.get("date") != today()


def claim_today(path: str | None) -> bool:
    """Write today into the stamp before anything is spawned, keeping the fields
    the last run left. A second session starting the same moment reads the
    claimed date and spawns nothing."""
    stamp = read_stamp(path)
    if not due(stamp):
        return False
    fields = {
        key: str(stamp.get(key) or "")
        for key in ("outcome", "from", "to", "reason")
        if stamp.get(key)
    }
    return write_stamp(path, **fields)


def resolve() -> Target | None:
    """The running install: the marketplace name from the install path, the clone
    from `known_marketplaces.json`, and the scope from the `installed_plugins.json`
    entry whose `installPath` is this same path. Anything unresolved is None, and
    the caller does nothing."""
    root = plugin_root()
    parts = _segments(root) if root else None
    if not root or not parts:
        return None
    marketplace, version = parts

    known = read_json(os.path.join(CLAUDE_DIR, "plugins", "known_marketplaces.json"))
    entry = known.get(marketplace)
    clone = entry.get("installLocation") if isinstance(entry, dict) else None
    if not clone or not os.path.isdir(os.path.join(clone, ".git")):
        return None

    installed = read_json(os.path.join(CLAUDE_DIR, "plugins", "installed_plugins.json"))
    plugins = installed.get("plugins")
    key = f"{PLUGIN_NAME}@{marketplace}"
    records = plugins.get(key) if isinstance(plugins, dict) else None
    for record in records if isinstance(records, list) else []:
        if not isinstance(record, dict):
            continue
        if not _same_path(str(record.get("installPath") or ""), root):
            continue
        scope = str(record.get("scope") or "")
        if not scope:
            return None
        return Target(
            marketplace=marketplace,
            clone=clone,
            scope=scope,
            project_path=record.get("projectPath") or None,
            version=str(record.get("version") or version),
            root=root,
        )
    return None


def report() -> str | None:
    """The line for the session context, or None when there is nothing to say.

    Only an install speaks. A first run, a day that installed nothing, and a run
    that failed all return None, which is the silence the feature promises.
    """
    stamp = read_stamp(stamp_path())
    if stamp.get("outcome") != OUTCOME_INSTALLED:
        return None
    to = str(stamp.get("to") or "")
    if not to:
        return None
    came_from = str(stamp.get("from") or "")
    origin = f" from {came_from}" if came_from else ""
    if version_of(plugin_root()) == to:
        return (
            f"- **bb updated itself to {to}**{origin}, and this session is running it. "
            f"The CHANGELOG entry for {to} is what changed."
        )
    return (
        f"- **bb {to} is installed**{origin}, and this session is still running "
        f"{version_of(plugin_root()) or 'the version it loaded'}. The new one loads on "
        "the next start."
    )
