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
"""

from __future__ import annotations

import io
import json
import os

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


def inject(frame: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": frame + "\n" + profile_block(None),
                }
            }
        )
    )


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    config = read_config()
    if not config:
        # Nobody calibrated anything, so nothing is written into anyone's files.
        # The frame still opens the session, and the invitation says where it
        # will live once it is asked for.
        frame = read_frame(here)
        if frame:
            inject(frame)
        return 0
    # Only an explicit false opts out. An absent or unparsable value reads as
    # yes, the same direction as a missing profile flag: more context, never less.
    if config.get("custom_instructions", True) is False:
        remove()
        return 0
    frame = read_frame(here)
    if not frame:
        return 0
    text = render(read_version(here), frame, read_profile(config))
    if read_raw(INSTRUCTIONS_PATH) != text:
        write(INSTRUCTIONS_PATH, text)
    memory = read_raw(MEMORY_PATH)
    updated = with_block(memory)
    if updated is not None and updated != memory:
        write(MEMORY_PATH, updated, newline="")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:  # a broken hook must never take a session down with it
        raise SystemExit(0)
