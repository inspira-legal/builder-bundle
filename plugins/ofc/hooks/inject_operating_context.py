#!/usr/bin/env python3
"""SessionStart hook: re-establish the toolkit's operating frame at session start
and after a context compaction — exactly when the model has lost the thread.
Emits operating-context.md as `additionalContext`.

Deliberately light and principle-level (not a procedure): it loads on EVERY
session in every repo where the plugin is enabled, so it nudges the way of
working, it does not force a mode. Edit operating-context.md to change the frame.

On an unattended run (OFC_UNATTENDED truthy) it appends unattended-context.md —
the no-questions / draft-PR / capped-retries addendum. That addendum is UX and
loop discipline only; never-merge is enforced server-side by capability scoping,
not by this frame.
"""

from __future__ import annotations

import json
import os
import sys

# Truthy values for OFC_UNATTENDED (case-insensitive). Anything else — including
# unset, "0", "false", "" — is supervised.
UNATTENDED_TRUTHY = {"1", "true", "yes"}


def is_unattended() -> bool:
    return os.environ.get("OFC_UNATTENDED", "").strip().lower() in UNATTENDED_TRUTHY


def read_frame(here: str, filename: str) -> str:
    try:
        return open(os.path.join(here, filename), encoding="utf-8").read().strip()
    except OSError:
        return ""  # missing file -> stay silent, never block the session


def main() -> int:
    here = os.path.dirname(os.path.abspath(__file__))
    ctx = read_frame(here, "operating-context.md")
    if is_unattended():
        addendum = read_frame(here, "unattended-context.md")
        if addendum:
            ctx = f"{ctx}\n\n{addendum}".strip()
    if not ctx:
        return 0
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": ctx,
                }
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
