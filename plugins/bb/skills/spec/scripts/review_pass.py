#!/usr/bin/env python3
"""Keep the spec review's pass count and the last text the grounding lens read.

Both live on disk, not in the run's memory, so a context compaction loses neither. The
state holds one entry per slug (the spec's parent directory name), so two specs reviewed
in one session keep separate counts.

`next` runs before a pass. It prints one JSON object:
  run   whether a pass runs: true when the grounding lens has read no text yet, or when
        the spec differs from the text it read
  pass  the pass number; it only advances when `run` is true, so with `run: false` it is
        the last pass counted
  diff  the unified diff from the text the grounding lens last read to the spec now,
        `null` when it has read none

`read` runs after the grounding lens returns a verdict, and saves the spec's current text
as the text it read. A lens that died never calls it, so the next `next` diffs against
the last text it did read and hands it every change it missed.

`--state` is the session's scratchpad, so the count belongs to the run. Without it the
state goes to a fixed directory under the system temp, where a slug's state older than 12
hours counts as a finished run and starts again at pass 1: there the reset depends on the
clock, not on the run remembering where it began.

Any failure goes to stderr with exit 1; the caller then runs full passes.

Usage:
  python3 review_pass.py next .bb/<slug>/spec.md [--state <dir>]
  python3 review_pass.py read .bb/<slug>/spec.md [--state <dir>]
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import sys
import tempfile
import time
from pathlib import Path

FIXED_DIR_NAME = "bb-review-pass"
STALE_AFTER = 12 * 60 * 60


def fixed_state_dir() -> Path:
    return Path(tempfile.gettempdir()) / FIXED_DIR_NAME


def state_file(state_dir: Path, spec: Path) -> Path:
    return state_dir / f"{spec.resolve().parent.name}.json"


def load(path: Path, expires: bool) -> dict:
    """Return the slug's state, or a fresh one when there is none or it expired."""
    fresh = {"pass": 0, "text": None, "updated": time.time()}
    if not path.exists():
        return fresh
    state = json.loads(path.read_text(encoding="utf-8"))
    if expires and time.time() - state.get("updated", 0) > STALE_AFTER:
        return fresh
    return state


def save(path: Path, state: dict) -> None:
    # Write then rename, so a run killed mid write leaves the old state, not half a file.
    path.parent.mkdir(parents=True, exist_ok=True)
    state["updated"] = time.time()
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, path)


def unified(old: str, new: str, name: str) -> str:
    lines = difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=f"a/{name}",
        tofile=f"b/{name}",
        n=3,
    )
    # A last line with no newline would run into the next hunk header.
    return "".join(line if line.endswith("\n") else line + "\n" for line in lines)


def cmd_next(spec: Path, path: Path, expires: bool) -> dict:
    state = load(path, expires)
    text = spec.read_text(encoding="utf-8")
    last = state["text"]
    run = last is None or text != last
    if run:
        state["pass"] += 1
        save(path, state)
    diff = None if last is None else unified(last, text, spec.name)
    return {"run": run, "pass": state["pass"], "diff": diff}


def cmd_read(spec: Path, path: Path, expires: bool) -> dict:
    state = load(path, expires)
    state["text"] = spec.read_text(encoding="utf-8")
    save(path, state)
    return {"pass": state["pass"]}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Pass count and last grounding-read text for the spec review."
    )
    parser.add_argument("command", choices=("next", "read"))
    parser.add_argument("spec", help="The spec, .bb/<slug>/spec.md.")
    parser.add_argument(
        "--state",
        default=None,
        help="The session's scratchpad (default: a fixed directory under the system temp, "
        "where state older than 12 hours starts a new run).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    spec = Path(args.spec)
    expires = args.state is None
    state_dir = fixed_state_dir() if expires else Path(args.state) / FIXED_DIR_NAME
    path = state_file(state_dir, spec)
    command = cmd_next if args.command == "next" else cmd_read
    try:
        result = command(spec, path, expires)
    except (OSError, ValueError, KeyError, TypeError) as err:
        print(f"review_pass: {err}", file=sys.stderr)
        raise SystemExit(1) from err
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
