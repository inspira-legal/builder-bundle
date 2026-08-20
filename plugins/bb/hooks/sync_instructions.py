#!/usr/bin/env python3
"""Keep ~/.claude/BUILDER-BUNDLE.md holding bb's custom instructions, and keep
~/.claude/CLAUDE.md importing it. Run by /bb:profile right after it writes the
config, and by the SessionStart hook so an updated plugin refreshes the file
instead of leaving the previous version's frame in place.

The instructions are a file the person can open, read, edit and delete, which is
why they live in ~/.claude instead of being injected into every session.

Nothing is written before there is a config: the file and the CLAUDE.md import
both arrive on the first /bb:profile, never on install. Until then the hook
carries the frame in the session itself, the way it always did, and says once
that /bb:profile exists.

`custom_instructions: false` is the opt out, and it is a removal: the managed
block leaves CLAUDE.md and BUILDER-BUNDLE.md leaves the disk. The contract is
references/bb-config.md. Every failure exits 0 and silently: a hook must never
block a session.

The same hook carries bb's own update: check_version.report() adds a line when the
last worker installed something, and a new worker is spawned when today's check is
still owed. Nothing waits on it, and it is outside the opt out, which only ever
governed the instructions file.
"""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys

CLAUDE_DIR = os.path.join(os.path.expanduser("~"), ".claude")
CONFIG_PATH = os.path.join(CLAUDE_DIR, "bb.config.json")
INSTRUCTIONS_PATH = os.path.join(CLAUDE_DIR, "BUILDER-BUNDLE.md")
MEMORY_PATH = os.path.join(CLAUDE_DIR, "CLAUDE.md")

# The import is fenced by markers so it can be found again, replaced in place and
# removed whole. Everything between them belongs to this script; everything
# outside is the person's and is never rewritten.
BLOCK_START = "<!-- bb:start -->"
BLOCK_END = "<!-- bb:end -->"
IMPORT_LINE = "@BUILDER-BUNDLE.md"

# What each answer means, in the words the instructions carry. The flags
# themselves are never written: `reads_code: false` says nothing on its own.
PROFILE_LINES: dict[str, tuple[str, str]] = {
    "reads_code": (
        "They read and edit the code. Argue a decision on its merits, show the diff, "
        "name the file and the function.",
        "They do not read the code. Describe what changes in terms of what the thing "
        "does, never by naming a function or pasting a diff.",
    ),
    "uses_terminal": (
        "They run commands and git themselves. A command is enough on its own.",
        "They do not work in a terminal. Prefer a path that needs no command, and when "
        "one is unavoidable, say where it goes and what it does first.",
    ),
    "technical_instructions": (
        "Keep the technical parts compact. One line per command is enough.",
        "Describe the technical parts one step at a time: where each step runs, how "
        "long it takes, and what it prints when it works.",
    ),
    "technical_vocabulary": (
        "Technical vocabulary reads fine: scaffold, branch, embed, MCP.",
        "Write in plain language. Replace scaffold, branch, embed and MCP with what "
        "they do, rather than using the term and glossing it.",
    ),
}

INVITATION = (
    "- **No profile calibrated yet.** How much to spell out is a guess right now. "
    "When a bb skill runs, offer `/bb:profile`: it asks four questions once, writes "
    "the answers into `~/.claude/BUILDER-BUNDLE.md`, and every session after that "
    "reads them from there."
)

HEADING = "\n## Who is on the other side\n\n"

# The update line sits under its own heading, so it is never read as one more
# bullet of the profile block it follows.
UPDATE_HEADING = "\n\n## bb's own version\n\n"

WORKER = "check_version.py"

# Windows has no fork: a child stays attached to the parent's console unless it is
# told to detach, and a console it owns alone would flash a window on every start.
DETACHED_PROCESS = 0x00000008
CREATE_NO_WINDOW = 0x08000000


def read_raw(path: str) -> str | None:
    """The file with its own line endings intact, or None. `newline=""` is what
    keeps a CRLF file CRLF when only one block of it is being replaced."""
    try:
        with io.open(path, encoding="utf-8", newline="") as f:
            return f.read()
    except OSError:
        return None


def newline_of(text: str) -> str:
    crlf = text.count("\r\n")
    return "\r\n" if crlf > text.count("\n") - crlf else "\n"


def block_bounds(lines: list[str]) -> tuple[int, int] | None:
    """Where the first whole block starts and ends. A start with no end after it
    is not a block: nothing is removed on the strength of half a pair. An end
    pairs with the *nearest* start above it, so a leftover start earlier in the
    file cannot swallow the lines between the two."""
    start = None
    for i, line in enumerate(lines):
        marker = line.strip()
        if marker == BLOCK_START:
            start = i
        elif marker == BLOCK_END and start is not None:
            return start, i
    return None


def without_blocks(lines: list[str]) -> tuple[list[str], bool]:
    """The lines with every whole block gone, and whether there was one."""
    found = False
    while True:
        bounds = block_bounds(lines)
        if bounds is None:
            return lines, found
        start, end = bounds
        lines = lines[:start] + lines[end + 1 :]
        found = True


def strip_block(text: str) -> str | None:
    """The text without the managed block, or None when there is no whole block.

    Splitting and joining on "\n" leaves each line's own ending inside the line,
    so a CRLF file, or a file carrying both, comes back byte for byte outside the
    block.
    """
    lines, found = without_blocks(text.split("\n"))
    if not found:
        return None
    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines) + ("\n" if lines else "")


def with_block(text: str | None) -> str | None:
    """The file with exactly one block at the end, or None when it is not ours to
    touch. A start marker left without an end is a half written block, and the
    person's lines sit under it: appending a block there would put them inside the
    pair, and the next run would take them out with it. Nothing is written into a
    file in that state."""
    if text is not None:
        remainder, _ = without_blocks(text.split("\n"))
        if any(line.strip() == BLOCK_START for line in remainder):
            return None
    nl = newline_of(text) if text else "\n"
    block = nl.join([BLOCK_START, IMPORT_LINE, BLOCK_END])
    # An empty strip result is a file that held nothing but the block, which is
    # not the same as no block at all: `or` here would append a second one on
    # every session.
    stripped = None if text is None else strip_block(text)
    body = "" if text is None else (text if stripped is None else stripped)
    body = body.rstrip("\r\n")
    return (body + nl + nl if body else "") + block + nl


def read_frame(here: str) -> str:
    try:
        with open(os.path.join(here, "operating-context.md"), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""  # missing file -> stay silent, never block the session


def read_version(here: str) -> str:
    try:
        path = os.path.join(here, os.pardir, ".claude-plugin", "plugin.json")
        with open(path, encoding="utf-8") as f:
            return str(json.load(f).get("version") or "") or "an unknown version"
    except (OSError, ValueError):
        return "an unknown version"


def read_config() -> dict:
    """The config, or an empty dict. Malformed reads the same as missing, on purpose."""
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            config = json.load(f)
    except (OSError, ValueError):
        return {}
    return config if isinstance(config, dict) else {}


def read_profile(config: dict) -> dict | None:
    profile = config.get("profile")
    return profile if isinstance(profile, dict) else None


def profile_block(profile: dict | None) -> str:
    if profile is None:
        return HEADING + INVITATION
    # A missing flag is False: an older config stays valid, and the safe default
    # is more explanation, not less.
    lines = [
        "- " + PROFILE_LINES[flag][0 if profile.get(flag) else 1]
        for flag in PROFILE_LINES
    ]
    return HEADING + "\n".join(lines)


def render(version: str, frame: str, profile: dict | None) -> str:
    header = (
        f"<!-- Written by bb {version}, through /bb:profile. An edit here is replaced "
        "the next time it runs. To stop it, run /bb:profile and choose not to use bb's "
        "custom instructions: this file and the import in CLAUDE.md both go away. -->"
    )
    return header + "\n\n" + frame + "\n" + profile_block(profile) + "\n"


def write(path: str, text: str, newline: str = "\n") -> None:
    os.makedirs(CLAUDE_DIR, exist_ok=True)
    with io.open(path, "w", encoding="utf-8", newline=newline) as f:
        f.write(text)


def remove() -> None:
    """The opt out, and it leaves nothing behind."""
    memory = read_raw(MEMORY_PATH)
    if memory is not None:
        without = strip_block(memory)
        if without is not None:
            write(MEMORY_PATH, without, newline="")
    try:
        os.remove(INSTRUCTIONS_PATH)
    except OSError:
        pass


def emit(context: str) -> None:
    """The one payload this hook prints. Every path that has something to say
    joins it here, because a second print would be a second JSON document on a
    stream the runner parses as one."""
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": context,
                }
            }
        )
    )


def load_check_version(here: str):
    """The sibling module. A hook can be started from anywhere, so its directory
    goes on the path rather than being assumed to be there."""
    if here not in sys.path:
        sys.path.insert(0, here)
    import check_version

    return check_version


def spawn_worker(here: str) -> None:
    """The detached worker, with all three of its streams on the null device.

    The hook's stdout is the JSON payload above, and a child holding that handle
    would write into the middle of it. The child outlives this process: nothing
    here waits, and its effect lands on the next session either way.
    """
    argv = [sys.executable, os.path.join(here, WORKER)]
    extra: dict = {}
    if os.name == "nt":
        extra["creationflags"] = DETACHED_PROCESS | CREATE_NO_WINDOW
    else:
        extra["start_new_session"] = True
    # The child's cwd is its own business: it takes the directory for the CLI
    # calls from the install's `projectPath`. Starting it in ~/.claude keeps a
    # detached process from holding a handle on whatever directory this session
    # opened in.
    cwd = CLAUDE_DIR if os.path.isdir(CLAUDE_DIR) else None
    with open(os.devnull, "r+b") as null:
        subprocess.Popen(
            argv,
            stdin=null,
            stdout=null,
            stderr=null,
            cwd=cwd,
            close_fds=True,
            **extra,
        )


def update_note(here: str) -> str:
    """The line the last worker earned, and today's spawn when the day is owed.

    Wrapped whole: bb's own update is worth no part of the session, so anything
    that goes wrong in here leaves the instructions half of the hook untouched.
    """
    try:
        check_version = load_check_version(here)
        line = check_version.report()
        path = check_version.stamp_path()
        if check_version.claim_today(path):
            # The date is claimed before the spawn, so a second session starting
            # this same moment reads today and spawns nothing.
            spawn_worker(here)
        return (UPDATE_HEADING + line) if line else ""
    except Exception:
        return ""


def sync(here: str, config: dict) -> None:
    """The instructions file and the CLAUDE.md import, brought up to date. This
    path says nothing in the session: the instructions reach it through the
    import."""
    frame = read_frame(here)
    if not frame:
        return
    text = render(read_version(here), frame, read_profile(config))
    if read_raw(INSTRUCTIONS_PATH) != text:
        write(INSTRUCTIONS_PATH, text)
    memory = read_raw(MEMORY_PATH)
    updated = with_block(memory)
    if updated is not None and updated != memory:
        write(MEMORY_PATH, updated, newline="")


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    update = update_note(here)
    frame = ""
    config = read_config()
    if not config:
        # Nobody calibrated anything, so nothing is written into anyone's files.
        # The frame still opens the session, and the invitation says where it
        # will live once it is asked for.
        carried = read_frame(here)
        if carried:
            frame = carried + "\n" + profile_block(None)
    elif config.get("custom_instructions", True) is False:
        # Only an explicit false opts out. An absent or unparsable value reads as
        # yes, the same direction as a missing profile flag: more context, never
        # less. The opt out is the instructions file alone; the update line is
        # not a thing anyone asked to stop.
        remove()
    else:
        sync(here, config)
    context = frame + update if frame else update.lstrip("\n")
    if context:
        emit(context)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:  # a broken hook must never take a session down with it
        raise SystemExit(0)
