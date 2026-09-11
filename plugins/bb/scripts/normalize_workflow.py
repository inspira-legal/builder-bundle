#!/usr/bin/env python3
"""
Write a CR-free copy of a workflow script and print where it landed.

Every installed copy of `plugins/bb/workflows/build-tasks.js` carries CR, the version
cache and the marketplace clone alike, and the permission layer refuses a `scriptPath`
whose bytes hold a control character. The installer does not honor `.gitattributes`, so
the repo cannot fix this at the source; the fix is to normalize at the point of use and
dispatch the copy. Read by `<plugin-root>/references/build-tasks-workflow.md`, which is
what any dispatcher of a workflow reads.

The source is read as bytes and every `\\r` is dropped, unconditionally: a source that
is already LF comes out byte-identical, and a conditional strip is a branch that only
runs on the machines where it is wrong.

Stdout is the copy's path, one line, nothing else, so the caller can hand it straight to
`scriptPath`. Anything to say about a failure goes to stderr with a non-zero exit, which
is the one signal the fallback chain reads: a missing or unreadable source and an out dir
that cannot be written both mean the run builds in context.

Usage:
  python3 normalize_workflow.py <source>
  python3 normalize_workflow.py <source> --out /path/to/dir
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

# Where the copy goes when the caller has nowhere of its own to offer. Under the system
# temp so the script needs nothing published to it; the skill passes its session
# scratchpad through `--out` when it has one.
DEFAULT_OUT_NAME = "bb-workflows"


def default_out_dir() -> Path:
    return Path(tempfile.gettempdir()) / DEFAULT_OUT_NAME


def normalize(source: Path, out_dir: Path) -> Path:
    """Copy `source` into `out_dir` without its CR bytes, and return the copy's path."""
    raw = source.read_bytes()
    out_dir.mkdir(parents=True, exist_ok=True)
    copy = out_dir / source.name
    copy.write_bytes(raw.replace(b"\r", b""))
    return copy


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Write a CR-free copy of a workflow script and print its path."
    )
    parser.add_argument("source", help="The workflow script to normalize.")
    parser.add_argument(
        "--out",
        default=None,
        help="Directory to write the copy into (default: a directory under the system temp).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source = Path(args.source)
    out_dir = Path(args.out) if args.out else default_out_dir()

    # One handler for both failures, because `OSError` names the path it choked on: the
    # exit code is what the chain reads, and the message is what says which path it was.
    try:
        copy = normalize(source, out_dir)
    except OSError as err:
        print(f"normalize_workflow: {err}", file=sys.stderr)
        raise SystemExit(1) from err

    print(copy)


if __name__ == "__main__":
    main()
