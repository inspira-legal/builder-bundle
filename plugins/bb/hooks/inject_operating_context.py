#!/usr/bin/env python3
"""SessionStart hook: re-establish the toolkit's operating frame at session start
and after a context compaction, exactly when the model has lost the thread.
Emits operating-context.md as `additionalContext`, plus the person's profile.

Deliberately light and principle-level (not a procedure): it loads on EVERY
session in every repo where the plugin is enabled, so it nudges the way of
working, it does not force a mode. Edit operating-context.md to change the frame,
and PROFILE_LINES below to change what a profile flag means.

The profile lives at ~/.claude/bb.profile.json, written by /bb:profile; the
contract is references/bb-profile.md. A missing, unreadable or malformed file
means no profile, never an error: this hook must never block a session.
"""

from __future__ import annotations

import json
import os

PROFILE_PATH = os.path.join(os.path.expanduser("~"), ".claude", "bb.profile.json")

# What each answer means, in the words the frame carries. The flags themselves
# are never injected: `reads_code: false` says nothing on its own.
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
    "step_by_step": (
        "Describe the technical parts one step at a time: where each step runs, how "
        "long it takes, and what it prints when it works.",
        "Keep the technical parts compact. One line per command is enough.",
    ),
    "technical_vocabulary": (
        "Technical vocabulary reads fine: scaffold, branch, embed, MCP.",
        "Write in plain language. Replace scaffold, branch, embed and MCP with what "
        "they do, rather than using the term and glossing it.",
    ),
}

INVITATION = (
    "- **No profile calibrated yet.** How much to spell out is a guess right now. "
    "When a bb skill runs, offer `/bb:profile`: it asks four questions once, and every "
    "session after this one is calibrated."
)

HEADING = "\n## Who is on the other side\n\n"


def read_frame(here: str, filename: str) -> str:
    try:
        return open(os.path.join(here, filename), encoding="utf-8").read().strip()
    except OSError:
        return ""  # missing file -> stay silent, never block the session


def read_profile() -> dict | None:
    """The profile, or None. Malformed reads the same as missing, on purpose."""
    try:
        with open(PROFILE_PATH, encoding="utf-8") as f:
            profile = json.load(f).get("profile")
    except (OSError, ValueError, AttributeError):
        return None
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


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ctx = read_frame(here, "operating-context.md")
    if not ctx:
        return 0
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": ctx + "\n" + profile_block(read_profile()),
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
